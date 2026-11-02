"""Pruebas de la tabla `arte_artista`.

Usan la conexión `root` dentro de una transacción que siempre termina en ROLLBACK, así que la
base no queda modificada. El artista que se inserta es FICTICIO y solo existe durante la prueba.
"""

from collections.abc import Iterator

import mysql.connector
import pytest

pytestmark = pytest.mark.integracion

ARTE_DE_PRUEBA = (
    "  ╔══════╗  \"comillas\" y 'simples'\n"
    " █▀▀ \\ barra \\n literal \\\\ doble\n"
    "\t← no hay tabuladores en el arte real, pero la base debe conservarlos\n"
    "   espacios al final   \n"
    "▄▄▄ fin"
)


@pytest.fixture
def cursor_en_transaccion(conexion_bd_root) -> Iterator:
    """Cursor de root con un artista ficticio insertado; deshace todo al terminar."""
    conexion_bd_root.rollback()
    conexion_bd_root.start_transaction()
    cursor = conexion_bd_root.cursor()
    cursor.execute(
        "INSERT INTO artista (nombre, tipo) VALUES (%s, 'Banda')",
        ("Artista ficticio de prueba",),
    )
    cursor.artista_ficticio_id = cursor.lastrowid
    try:
        yield cursor
    finally:
        cursor.close()
        conexion_bd_root.rollback()


def test_el_arte_se_recupera_identico(cursor_en_transaccion):
    cursor = cursor_en_transaccion
    artista_id = cursor.artista_ficticio_id
    cursor.execute(
        "INSERT INTO arte_artista (artista_id, arte, estilo) VALUES (%s, %s, %s)",
        (artista_id, ARTE_DE_PRUEBA, "bold red"),
    )
    cursor.execute("SELECT arte, estilo FROM arte_artista WHERE artista_id = %s", (artista_id,))
    arte, estilo = cursor.fetchone()
    assert arte == ARTE_DE_PRUEBA
    assert estilo == "bold red"


def test_el_estilo_es_opcional(cursor_en_transaccion):
    cursor = cursor_en_transaccion
    artista_id = cursor.artista_ficticio_id
    cursor.execute(
        "INSERT INTO arte_artista (artista_id, arte) VALUES (%s, %s)", (artista_id, "arte")
    )
    cursor.execute("SELECT estilo FROM arte_artista WHERE artista_id = %s", (artista_id,))
    assert cursor.fetchone()[0] is None


def test_un_solo_arte_por_artista(cursor_en_transaccion):
    cursor = cursor_en_transaccion
    artista_id = cursor.artista_ficticio_id
    cursor.execute(
        "INSERT INTO arte_artista (artista_id, arte) VALUES (%s, %s)", (artista_id, "uno")
    )
    with pytest.raises(mysql.connector.Error) as error:
        cursor.execute(
            "INSERT INTO arte_artista (artista_id, arte) VALUES (%s, %s)", (artista_id, "dos")
        )
    # 1062: entrada duplicada para la clave primaria.
    assert error.value.errno == 1062


def test_el_artista_debe_existir(cursor_en_transaccion):
    cursor = cursor_en_transaccion
    with pytest.raises(mysql.connector.Error) as error:
        cursor.execute(
            "INSERT INTO arte_artista (artista_id, arte) VALUES (%s, %s)", (-1, "huérfano")
        )
    # 1452: falla la restricción de llave foránea.
    assert error.value.errno == 1452


def test_borrar_el_artista_borra_su_arte(cursor_en_transaccion):
    cursor = cursor_en_transaccion
    artista_id = cursor.artista_ficticio_id
    cursor.execute(
        "INSERT INTO arte_artista (artista_id, arte) VALUES (%s, %s)", (artista_id, "arte")
    )
    cursor.execute("DELETE FROM artista WHERE artista_id = %s", (artista_id,))
    cursor.execute("SELECT COUNT(*) FROM arte_artista WHERE artista_id = %s", (artista_id,))
    assert cursor.fetchone()[0] == 0
