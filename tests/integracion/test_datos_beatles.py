"""Hechos verificables de los datos de The Beatles (vista y procedimientos)."""

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


def consultar(conexion, sql: str, parametros: tuple = ()) -> list[tuple]:
    cursor = conexion.cursor()
    cursor.execute(sql, parametros)
    filas = cursor.fetchall()
    cursor.close()
    return filas


@pytest.fixture(scope="module")
def bd(conexion_bd):
    if not consultar(conexion_bd, "SELECT 1 FROM artista WHERE nombre = 'The Beatles'"):
        pytest.skip("No están cargados los datos de The Beatles (docker compose up -d --wait).")
    return conexion_bd


def test_integrantes_en_1961_incluyen_a_best_y_sutcliffe(bd):
    nombres = {
        fila[1] for fila in llamar(bd, "sp_integrantes_en_fecha", "The Beatles", "1961-06-01")
    }
    assert {"Pete Best", "Stuart Sutcliffe"} <= nombres


def test_integrantes_en_1963_son_los_cuatro(bd):
    nombres = {
        fila[1] for fila in llamar(bd, "sp_integrantes_en_fecha", "The Beatles", "1963-01-01")
    }
    assert nombres == {"John Lennon", "Paul McCartney", "George Harrison", "Ringo Starr"}


def test_lennon_participa_en_abbey_road_y_no_en_i_me_mine(bd):
    filas = llamar(bd, "sp_canciones_de_persona", "John Lennon")
    via_beatles = {cancion for _p, cancion, via, _r in filas if via == "The Beatles"}
    abbey_road = {
        titulo
        for (titulo,) in consultar(
            bd,
            "SELECT c.titulo FROM album a JOIN album_cancion ac ON ac.album_id = a.album_id "
            "JOIN cancion c ON c.cancion_id = ac.cancion_id WHERE a.titulo = 'Abbey Road'",
        )
    }
    assert len(abbey_road) == 17
    assert abbey_road <= via_beatles
    assert "I Me Mine" not in {cancion for _p, cancion, _v, _r in filas}


def test_pete_best_no_tiene_canciones(bd):
    assert llamar(bd, "sp_canciones_de_persona", "Pete Best") == []


def test_mccartney_por_tres_vias(bd):
    vias = {via for _p, _c, via, _r in llamar(bd, "sp_canciones_de_persona", "Paul McCartney")}
    assert {"The Beatles", "Wings", "Paul McCartney"} <= vias


def test_canciones_reutilizadas_en_1_son_la_misma_fila(bd):
    filas = consultar(
        bd,
        "SELECT c.titulo, COUNT(DISTINCT ac.album_id) FROM cancion c "
        "JOIN album_cancion ac ON ac.cancion_id = c.cancion_id "
        "WHERE c.titulo IN ('Something', 'Come Together', 'The Long and Winding Road', 'Get Back') "
        "GROUP BY c.cancion_id, c.titulo",
    )
    apariciones = {}
    for titulo, cantidad in filas:
        apariciones.setdefault(titulo, []).append(cantidad)
    assert apariciones["Something"] == [2]
    assert apariciones["Come Together"] == [2]
    assert apariciones["The Long and Winding Road"] == [2]
    # Single (y 1) por un lado, versión del LP Let It Be por otro.
    assert sorted(apariciones["Get Back"]) == [1, 2]


def test_featuring_de_billy_preston_en_el_tracklist(bd):
    pistas = llamar(bd, "sp_tracklist", 2)
    assert pistas[0][3] == "The Beatles, feat. Billy Preston"


def test_arbol_de_rock_tiene_tres_niveles(bd):
    niveles = {fila[2] for fila in llamar(bd, "sp_subgeneros", "Rock")}
    assert niveles == {0, 1, 2}
