"""Conexión a MySQL y ejecución de consultas y procedimientos almacenados.

Los errores del conector se traducen a excepciones propias con mensajes en español, listos para
mostrar al usuario.
"""

from collections.abc import Sequence
from typing import Any

import mysql.connector

from wikitunes.configuracion import ConfiguracionBD

Fila = dict[str, Any]


class ErrorDeBaseDeDatos(Exception):
    """Error al consultar la base de datos, con un mensaje en español."""


class ErrorDeConexion(ErrorDeBaseDeDatos):
    """No se pudo conectar (o se perdió la conexión) con la base de datos."""


# Errores del conector que significan "no hay base de datos disponible".
ERRORES_DE_CONEXION = {
    1045,  # acceso denegado (usuario o clave)
    1049,  # base de datos desconocida
    2003,  # no se puede conectar al servidor
    2005,  # host desconocido
    2006,  # el servidor se fue
    2013,  # se perdió la conexión durante la consulta
    2055,  # se perdió la conexión
}


def _mensaje_sin_conexion(configuracion: ConfiguracionBD, error: mysql.connector.Error) -> str:
    return (
        f"No se pudo conectar a la base de datos en {configuracion.host}:{configuracion.puerto} "
        f"({error.msg}). ¿Está levantada? Prueba con `docker compose up -d --wait`."
    )


def conectar(configuracion: ConfiguracionBD | None = None) -> mysql.connector.MySQLConnection:
    """Abre una conexión con el usuario de solo lectura de la aplicación."""
    configuracion = configuracion or ConfiguracionBD.desde_entorno()
    try:
        conexion = mysql.connector.connect(**configuracion.parametros_conector())
    except mysql.connector.Error as error:
        raise ErrorDeConexion(_mensaje_sin_conexion(configuracion, error)) from error
    conexion.autocommit = True
    return conexion


def _traducir(error: mysql.connector.Error) -> ErrorDeBaseDeDatos:
    if error.errno in ERRORES_DE_CONEXION:
        return ErrorDeConexion(
            "Se perdió la conexión con la base de datos. "
            "Comprueba que esté levantada (`docker compose up -d --wait`) y vuelve a intentarlo."
        )
    return ErrorDeBaseDeDatos(f"Error de la base de datos: {error.msg} (código {error.errno}).")


def consultar(conexion, sql: str, parametros: Sequence[Any] = ()) -> list[Fila]:
    """Ejecuta un SELECT y devuelve las filas como diccionarios."""
    try:
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute(sql, tuple(parametros))
            return list(cursor.fetchall())
        finally:
            cursor.close()
    except mysql.connector.Error as error:
        raise _traducir(error) from error


def llamar_procedimiento(conexion, nombre: str, *argumentos: Any) -> list[list[Fila]]:
    """Llama a un procedimiento y devuelve cada conjunto de resultados como lista de diccionarios.

    Se usa `CALL` + `nextset()` porque `cursor.stored_results()` está obsoleto en el conector.
    """
    marcadores = ", ".join(["%s"] * len(argumentos))
    try:
        cursor = conexion.cursor()
        try:
            cursor.execute(f"CALL {nombre}({marcadores})", argumentos)
            conjuntos: list[list[Fila]] = []
            while True:
                if cursor.description:
                    columnas = [descripcion[0] for descripcion in cursor.description]
                    conjuntos.append(
                        [dict(zip(columnas, fila, strict=True)) for fila in cursor.fetchall()]
                    )
                if not cursor.nextset():
                    break
            return conjuntos
        finally:
            cursor.close()
    except mysql.connector.Error as error:
        raise _traducir(error) from error
