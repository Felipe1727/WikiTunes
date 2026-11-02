"""Pruebas de la vista `v_participacion_persona` y de los procedimientos corregidos.

Todo el escenario es FICTICIO (los nombres llevan "(ficticio)") y vive dentro de una transacción
de `root` que termina en ROLLBACK: la base no queda modificada.

Escenario:
    Banda (ficticio), acreditada como Principal en c1, c2 y c3.
    Álbumes: LP 2003-05-01 [c1], LP 2010-05-01 [c2], compilación 2015-01-01 [c1, c2].
    c3 no está en ningún álbum (no tiene fecha de salida).

    Ana   integrante 2000-01-01 .. 2005-12-31
    Beto  integrante 2006-01-01 .. (activo)
    Ciro  no integrante; Productor de c1
    Dora  integrante 2000-01-01 .. 2005-12-31; Compositora de c2
    Eva   integrante 2000-01-01 .. 2001-12-31 y otra vez 2008-01-01 .. (activo)
"""

from collections.abc import Iterator
from dataclasses import dataclass

import mysql.connector
import pytest

pytestmark = pytest.mark.integracion

BANDA = "Banda (ficticio)"
VIA_INDIVIDUAL = "(crédito individual)"


@dataclass
class Escenario:
    cursor: object
    personas: dict[str, int]


def _insertar(cursor, sql: str, parametros: tuple) -> int:
    cursor.execute(sql, parametros)
    return cursor.lastrowid


@pytest.fixture
def escenario(conexion_bd_root) -> Iterator[Escenario]:
    conexion_bd_root.rollback()
    conexion_bd_root.start_transaction()
    cursor = conexion_bd_root.cursor()
    try:
        banda = _insertar(
            cursor, "INSERT INTO artista (nombre, tipo) VALUES (%s, 'Banda')", (BANDA,)
        )
        personas = {}
        for corto, legal in [
            ("Ana", "Ana María Legal (ficticio)"),
            ("Beto", "Beto Legal (ficticio)"),
            ("Ciro", "Ciro Legal (ficticio)"),
            ("Dora", "Dora Legal (ficticio)"),
            ("Eva", "Eva Legal (ficticio)"),
        ]:
            personas[corto] = _insertar(
                cursor,
                "INSERT INTO persona (nombre_legal, nombre_conocido) VALUES (%s, %s)",
                (legal, f"{corto} (ficticio)"),
            )
        for corto, inicio, fin in [
            ("Ana", "2000-01-01", "2005-12-31"),
            ("Beto", "2006-01-01", None),
            ("Dora", "2000-01-01", "2005-12-31"),
            ("Eva", "2000-01-01", "2001-12-31"),
            ("Eva", "2008-01-01", None),
        ]:
            cursor.execute(
                "INSERT INTO membresia (persona_id, artista_id, rol, fecha_inicio, fecha_fin) "
                "VALUES (%s, %s, 'Voz', %s, %s)",
                (personas[corto], banda, inicio, fin),
            )
        canciones = {
            nombre: _insertar(
                cursor,
                "INSERT INTO cancion (titulo, duracion_seg) VALUES (%s, 180)",
                (f"{nombre} (ficticio)",),
            )
            for nombre in ("c1", "c2", "c3")
        }
        for cancion_id in canciones.values():
            cursor.execute(
                "INSERT INTO credito_artista (cancion_id, artista_id, rol) "
                "VALUES (%s, %s, 'Principal')",
                (cancion_id, banda),
            )
        for titulo, tipo, fecha, contenido in [
            ("LP 2003 (ficticio)", "LP", "2003-05-01", ["c1"]),
            ("LP 2010 (ficticio)", "LP", "2010-05-01", ["c2"]),
            ("Compilación 2015 (ficticio)", "Compilation", "2015-01-01", ["c1", "c2"]),
        ]:
            album = _insertar(
                cursor,
                "INSERT INTO album (titulo, tipo, fecha_lanzamiento) VALUES (%s, %s, %s)",
                (titulo, tipo, fecha),
            )
            for pista, nombre in enumerate(contenido, start=1):
                cursor.execute(
                    "INSERT INTO album_cancion (album_id, cancion_id, numero_pista) "
                    "VALUES (%s, %s, %s)",
                    (album, canciones[nombre], pista),
                )
        cursor.execute(
            "INSERT INTO credito_persona (cancion_id, persona_id, rol) "
            "VALUES (%s, %s, 'Productor')",
            (canciones["c1"], personas["Ciro"]),
        )
        cursor.execute(
            "INSERT INTO credito_persona (cancion_id, persona_id, rol) "
            "VALUES (%s, %s, 'Compositor')",
            (canciones["c2"], personas["Dora"]),
        )
        yield Escenario(cursor=cursor, personas=personas)
    finally:
        cursor.close()
        conexion_bd_root.rollback()


def canciones_de(escenario: Escenario, nombre: str) -> set[tuple[str, str, str]]:
    """(canción, vía, rol) que devuelve sp_canciones_de_persona para ese nombre."""
    escenario.cursor.execute("CALL sp_canciones_de_persona(%s)", (nombre,))
    filas = []
    for _sentencia, resultado in escenario.cursor.fetchsets():
        filas.extend(resultado)
    return {(cancion.removesuffix(" (ficticio)"), via, rol) for _p, cancion, via, rol in filas}


def historial(escenario: Escenario, artista: str) -> list[tuple]:
    escenario.cursor.execute("CALL sp_historial_integrantes(%s)", (artista,))
    filas = []
    for _sentencia, resultado in escenario.cursor.fetchsets():
        filas.extend(resultado)
    return filas


# --- Participación vía artista ---------------------------------------------------------------


def test_integrante_en_la_fecha_de_salida(escenario):
    assert canciones_de(escenario, "Ana (ficticio)") == {("c1", BANDA, "Principal")}


def test_antiguo_integrante_sin_credito_no_figura(escenario):
    # Beto entró en 2006: no estaba cuando salió c1 (2003) aunque sí en la compilación de 2015.
    assert canciones_de(escenario, "Beto (ficticio)") == {("c2", BANDA, "Principal")}


def test_antiguo_integrante_con_credito_propio(escenario):
    assert canciones_de(escenario, "Dora (ficticio)") == {
        ("c1", BANDA, "Principal"),
        ("c2", BANDA, "Principal"),
        ("c2", VIA_INDIVIDUAL, "Compositor"),
    }


def test_cancion_sin_fecha_de_salida_no_cuenta_por_membresia(escenario):
    for nombre in ("Ana", "Beto", "Dora", "Eva"):
        canciones = {
            cancion for cancion, _via, _rol in canciones_de(escenario, f"{nombre} (ficticio)")
        }
        assert "c3" not in canciones


def test_la_compilacion_no_cambia_la_fecha_de_salida(escenario):
    # Eva no era integrante en 2003 (c1) pero sí en 2010 (c2) y en 2015 (compilación).
    assert canciones_de(escenario, "Eva (ficticio)") == {("c2", BANDA, "Principal")}


def test_productor_externo_solo_como_credito_individual(escenario):
    assert canciones_de(escenario, "Ciro (ficticio)") == {("c1", VIA_INDIVIDUAL, "Productor")}


# --- Búsqueda exacta por nombre --------------------------------------------------------------


def test_busqueda_por_nombre_legal_exacto(escenario):
    assert canciones_de(escenario, "Ana María Legal (ficticio)") == {("c1", BANDA, "Principal")}


def test_busqueda_parcial_no_devuelve_filas(escenario):
    assert canciones_de(escenario, "Ana") == set()
    assert canciones_de(escenario, "ficticio") == set()


def test_el_plan_considera_los_indices_de_persona(escenario):
    escenario.cursor.execute(
        "EXPLAIN SELECT persona_id FROM persona WHERE nombre_conocido = %s OR nombre_legal = %s",
        ("Ana (ficticio)", "Ana (ficticio)"),
    )
    columnas = [d[0] for d in escenario.cursor.description]
    fila = dict(zip(columnas, escenario.cursor.fetchone(), strict=True))
    posibles = set((fila["possible_keys"] or "").split(","))
    assert {"idx_persona_nombre_conocido", "idx_persona_nombre_legal"} <= posibles


def test_existen_los_indices_de_nombre(conexion_bd):
    cursor = conexion_bd.cursor()
    cursor.execute(
        "SELECT table_name, index_name, non_unique FROM information_schema.statistics "
        "WHERE table_schema = DATABASE() AND index_name IN "
        "('uq_artista_nombre', 'idx_persona_nombre_conocido', 'idx_persona_nombre_legal')"
    )
    indices = {(tabla, indice): no_unico for tabla, indice, no_unico in cursor.fetchall()}
    cursor.close()
    assert indices == {
        ("artista", "uq_artista_nombre"): 0,
        ("persona", "idx_persona_nombre_conocido"): 1,
        ("persona", "idx_persona_nombre_legal"): 1,
    }


# --- Integrantes de un artista ---------------------------------------------------------------


def test_nombre_de_artista_unico(escenario):
    with pytest.raises(mysql.connector.Error) as error:
        escenario.cursor.execute(
            "INSERT INTO artista (nombre, tipo) VALUES (%s, 'Banda')", (BANDA,)
        )
    assert error.value.errno == 1062


def test_historial_completo_ordenado(escenario):
    filas = historial(escenario, BANDA)
    resumen = [
        (persona, str(inicio), None if fin is None else str(fin))
        for _id, _artista, persona, _rol, inicio, fin in filas
    ]
    assert resumen == [
        ("Ana (ficticio)", "2000-01-01", "2005-12-31"),
        ("Dora (ficticio)", "2000-01-01", "2005-12-31"),
        ("Eva (ficticio)", "2000-01-01", "2001-12-31"),
        ("Beto (ficticio)", "2006-01-01", None),
        ("Eva (ficticio)", "2008-01-01", None),
    ]


def test_historial_incluye_el_id_de_la_persona(escenario):
    ids = {fila[0] for fila in historial(escenario, BANDA)}
    esperados = {escenario.personas[n] for n in ("Ana", "Beto", "Dora", "Eva")}
    assert ids == esperados


def test_historial_de_artista_inexistente(escenario):
    assert historial(escenario, "No existe (ficticio)") == []
