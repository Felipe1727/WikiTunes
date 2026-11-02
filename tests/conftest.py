"""Configuración compartida de las pruebas.

Las pruebas marcadas con `integracion` usan el fixture `conexion_bd`. Si la base no responde,
se saltan con un aviso, salvo que `WIKITUNES_EXIGIR_BD=1`, en cuyo caso fallan.
"""

import os
from collections.abc import Iterator
from pathlib import Path

import mysql.connector
import pytest
from dotenv import load_dotenv

RAIZ_REPOSITORIO = Path(__file__).resolve().parent.parent

# El .env es opcional; las variables ya definidas en el entorno tienen prioridad.
load_dotenv(RAIZ_REPOSITORIO / ".env", override=False)


def parametros_conexion() -> dict[str, object]:
    """Parámetros del usuario de solo lectura, con los valores por defecto de desarrollo."""
    return {
        "host": os.getenv("WIKITUNES_BD_HOST", "127.0.0.1"),
        "port": int(os.getenv("WIKITUNES_BD_PUERTO", "3306")),
        "user": os.getenv("WIKITUNES_BD_USUARIO", "wikitunes"),
        "password": os.getenv("WIKITUNES_BD_CLAVE", "wikitunes"),
        "database": os.getenv("WIKITUNES_BD_NOMBRE", "musica"),
        "connection_timeout": 5,
    }


def base_exigida() -> bool:
    return os.getenv("WIKITUNES_EXIGIR_BD") == "1"


def parametros_conexion_root() -> dict[str, object]:
    """Parámetros de `root`, para comprobaciones que el usuario de solo lectura no puede hacer."""
    parametros = parametros_conexion()
    parametros["user"] = "root"
    parametros["password"] = os.getenv("WIKITUNES_BD_CLAVE_ROOT", "raiz_wikitunes")
    return parametros


def _conectar_o_saltar(parametros: dict[str, object]) -> mysql.connector.MySQLConnection:
    try:
        return mysql.connector.connect(**parametros)
    except mysql.connector.Error as error:
        mensaje = (
            "No hay conexión con la base de datos "
            f"({error}). Levántala con `docker compose up -d --wait`."
        )
        if base_exigida():
            pytest.fail(mensaje, pytrace=False)
        pytest.skip(mensaje)


@pytest.fixture(scope="session")
def conexion_bd() -> Iterator[mysql.connector.MySQLConnection]:
    """Conexión de solo lectura a la base `musica`, compartida por toda la sesión."""
    conexion = _conectar_o_saltar(parametros_conexion())
    try:
        yield conexion
    finally:
        conexion.close()


@pytest.fixture(scope="session")
def conexion_bd_root() -> Iterator[mysql.connector.MySQLConnection]:
    """Conexión como `root` a la base `musica`, compartida por toda la sesión."""
    conexion = _conectar_o_saltar(parametros_conexion_root())
    try:
        yield conexion
    finally:
        conexion.close()
