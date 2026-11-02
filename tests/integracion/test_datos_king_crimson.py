"""Hechos verificables de los datos de King Crimson (vista y procedimientos)."""

import pytest

pytestmark = pytest.mark.integracion


def llamar(conexion, procedimiento: str, *argumentos) -> list[tuple]:
    cursor = conexion.cursor()
    marcadores = ", ".join(["%s"] * len(argumentos))
    cursor.execute(f"CALL {procedimiento}({marcadores})", argumentos)
    filas = []
    for _sentencia, resultado in cursor.fetchsets():
        filas.extend(resultado)
    cursor.close()
    return filas


@pytest.fixture(scope="module")
def bd(conexion_bd):
    cursor = conexion_bd.cursor()
    cursor.execute("SELECT 1 FROM artista WHERE nombre = 'King Crimson'")
    cargado = cursor.fetchall()
    cursor.close()
    if not cargado:
        pytest.skip("No están cargados los datos de King Crimson (docker compose up -d --wait).")
    return conexion_bd


def integrantes(bd, fecha: str) -> set[str]:
    return {fila[1] for fila in llamar(bd, "sp_integrantes_en_fecha", "King Crimson", fecha)}


FORMACIONES = {
    "1969-06-01": {"Robert Fripp", "Michael Giles", "Greg Lake", "Ian McDonald", "Peter Sinfield"},
    "1974-06-01": {"Robert Fripp", "John Wetton", "Bill Bruford", "David Cross"},
    "1981-06-01": {"Robert Fripp", "Adrian Belew", "Tony Levin", "Bill Bruford"},
    "1995-06-01": {
        "Robert Fripp",
        "Adrian Belew",
        "Tony Levin",
        "Bill Bruford",
        "Trey Gunn",
        "Pat Mastelotto",
    },
}


@pytest.mark.parametrize(("fecha", "esperados"), FORMACIONES.items())
def test_formacion_en_cada_epoca(bd, fecha, esperados):
    assert integrantes(bd, fecha) == esperados


def test_las_cuatro_formaciones_son_distintas(bd):
    formaciones = [frozenset(integrantes(bd, fecha)) for fecha in FORMACIONES]
    assert len(set(formaciones)) == 4


def test_banda_inactiva_entre_1985_y_1993(bd):
    assert integrantes(bd, "1990-01-01") == set()


def test_historial_con_los_cuatro_periodos_de_fripp(bd):
    filas = llamar(bd, "sp_historial_integrantes", "King Crimson")
    periodos_fripp = [(str(f[4]), str(f[5])) for f in filas if f[2] == "Robert Fripp"]
    assert periodos_fripp == [
        ("1968-11-30", "1974-12-31"),
        ("1981-04-01", "1984-07-31"),
        ("1994-04-01", "2008-08-31"),
        ("2013-09-25", "2021-12-31"),
    ]
    assert len({f[0] for f in filas}) == 23


def test_fripp_solo_en_king_crimson(bd):
    cursor = bd.cursor()
    cursor.execute(
        "SELECT DISTINCT a.nombre FROM membresia m "
        "JOIN persona p ON p.persona_id = m.persona_id "
        "JOIN artista a ON a.artista_id = m.artista_id "
        "WHERE p.nombre_conocido = 'Robert Fripp'"
    )
    assert cursor.fetchall() == [("King Crimson",)]
    cursor.close()


def test_belew_no_figura_en_el_king_crimson_de_1969(bd):
    canciones = {fila[1] for fila in llamar(bd, "sp_canciones_de_persona", "Adrian Belew")}
    assert "21st Century Schizoid Man (including Mirrors)" not in canciones
    assert "Elephant Talk" in canciones
