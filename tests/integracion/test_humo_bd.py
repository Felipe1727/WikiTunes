"""Prueba de humo: la base levantada con Docker Compose tiene todos sus objetos."""

import mysql.connector
import pytest

pytestmark = pytest.mark.integracion

TABLAS_ESPERADAS = {
    "pais",
    "ciudad",
    "genero",
    "sello",
    "persona",
    "artista",
    "membresia",
    "artista_genero",
    "album",
    "album_artista",
    "album_genero",
    "cancion",
    "cancion_genero",
    "album_cancion",
    "credito_artista",
    "credito_persona",
}

PROCEDIMIENTOS_ESPERADOS = {
    "sp_canciones_de_persona",
    "sp_subgeneros",
    "sp_tracklist",
    "sp_integrantes_en_fecha",
}


def consultar_valor(conexion, sql: str, parametros: tuple = ()) -> object:
    cursor = conexion.cursor()
    try:
        cursor.execute(sql, parametros)
        return cursor.fetchone()[0]
    finally:
        cursor.close()


def test_existen_las_16_tablas_del_esquema(conexion_bd):
    cursor = conexion_bd.cursor()
    cursor.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = DATABASE() AND table_type = 'BASE TABLE'"
    )
    nombres = {fila[0] for fila in cursor.fetchall()}
    cursor.close()
    assert TABLAS_ESPERADAS <= nombres


def test_existen_los_4_triggers(conexion_bd_root):
    # El usuario de solo lectura no ve los triggers en information_schema; se usa root.
    cantidad = consultar_valor(
        conexion_bd_root,
        "SELECT COUNT(*) FROM information_schema.triggers WHERE trigger_schema = 'musica'",
    )
    assert cantidad == 4


def test_existe_la_vista_de_participacion(conexion_bd):
    cantidad = consultar_valor(
        conexion_bd,
        "SELECT COUNT(*) FROM information_schema.views "
        "WHERE table_schema = DATABASE() AND table_name = 'v_participacion_persona'",
    )
    assert cantidad == 1


def test_existen_los_procedimientos(conexion_bd):
    cursor = conexion_bd.cursor()
    cursor.execute(
        "SELECT routine_name FROM information_schema.routines "
        "WHERE routine_schema = DATABASE() AND routine_type = 'PROCEDURE'"
    )
    nombres = {fila[0] for fila in cursor.fetchall()}
    cursor.close()
    assert PROCEDIMIENTOS_ESPERADOS <= nombres


def test_el_usuario_puede_leer_y_ejecutar(conexion_bd):
    assert consultar_valor(conexion_bd, "SELECT COUNT(*) FROM persona") >= 0
    cursor = conexion_bd.cursor()
    cursor.execute("CALL sp_subgeneros(%s)", ("Rock",))
    # Consumir todos los conjuntos de resultados que devuelve el CALL.
    list(cursor.fetchsets())
    cursor.close()


def test_el_usuario_no_puede_escribir(conexion_bd):
    cursor = conexion_bd.cursor()
    with pytest.raises(mysql.connector.Error) as error:
        cursor.execute("INSERT INTO pais (nombre, codigo_iso2) VALUES ('Prueba', 'ZZ')")
    cursor.close()
    conexion_bd.rollback()
    # 1142: comando denegado al usuario para la tabla.
    assert error.value.errno == 1142
