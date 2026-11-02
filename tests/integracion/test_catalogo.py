"""Pruebas de `Catalogo` contra los datos de la demo."""

from datetime import date, timedelta

import pytest

from wikitunes.catalogo import Catalogo
from wikitunes.conexion import ErrorDeBaseDeDatos, conectar
from wikitunes.modelos import Referencia

pytestmark = pytest.mark.integracion


@pytest.fixture(scope="module")
def catalogo(conexion_bd):
    cat = Catalogo(conexion_bd)
    if not cat.artistas():
        pytest.skip("No están cargados los datos de la demo (docker compose up -d --wait).")
    return cat


def buscar(referencias, nombre):
    return next(r for r in referencias if r.nombre == nombre)


def test_conectar_con_la_configuracion_por_defecto():
    try:
        conexion = conectar()
    except ErrorDeBaseDeDatos:
        pytest.skip("Base no disponible.")
    conexion.close()


def test_listados_para_autocompletar(catalogo):
    assert "Paul McCartney" in {p.nombre for p in catalogo.personas()}
    assert "King Crimson" in {a.nombre for a in catalogo.artistas()}
    assert "Abbey Road" in {a.titulo for a in catalogo.albumes()}
    assert "Rock progresivo" in {g.nombre for g in catalogo.generos()}
    assert "Starless" in {c.nombre for c in catalogo.canciones()}


def test_canciones_de_persona_con_ids(catalogo):
    mccartney = buscar(catalogo.personas(), "Paul McCartney")
    participaciones = catalogo.canciones_de_persona(mccartney)
    assert {p.via for p in participaciones} >= {"The Beatles", "Wings", "Paul McCartney"}
    assert all(p.cancion_id is not None for p in participaciones)
    # Las dos versiones de «Get Back» (single y LP) tienen ids distintos.
    get_back = {p.cancion_id for p in participaciones if p.cancion == "Get Back"}
    assert len(get_back) == 2


def test_persona_sin_canciones(catalogo):
    assert catalogo.canciones_de_persona(buscar(catalogo.personas(), "Pete Best")) == []


def test_subgeneros(catalogo):
    arbol = catalogo.subgeneros("Rock")
    assert arbol[0].nombre == "Rock" and arbol[0].nivel == 0
    assert {n.nivel for n in arbol} == {0, 1, 2}
    assert catalogo.subgeneros("No existe") == []


def test_tracklist_con_sus_dos_resultados(catalogo):
    abbey_road = next(a for a in catalogo.albumes() if a.titulo == "Abbey Road")
    tracklist = catalogo.tracklist(abbey_road.id)
    assert tracklist.cantidad_pistas == 17 == len(tracklist.pistas)
    assert isinstance(tracklist.duracion_total, timedelta)
    # Suma de las 17 duraciones de MusicBrainz (crudo/).
    assert tracklist.duracion_total_texto == "47:25"
    assert tracklist.pistas[0].cancion == "Come Together"
    assert all(p.cancion_id is not None for p in tracklist.pistas)
    assert catalogo.tracklist(999999) is None


def test_integrantes_en_fecha_con_ids(catalogo):
    integrantes = catalogo.integrantes_en_fecha("King Crimson", date(1974, 6, 1))
    assert {i.persona for i in integrantes} == {
        "Robert Fripp",
        "John Wetton",
        "Bill Bruford",
        "David Cross",
    }
    assert all(i.persona_id is not None for i in integrantes)


def test_historial(catalogo):
    historial = catalogo.historial_integrantes("The Beatles")
    best = next(i for i in historial if i.persona == "Pete Best")
    assert best.periodo == "1960–1962"


def test_ficha_artista(catalogo):
    kc = buscar(catalogo.artistas(), "King Crimson")
    ficha = catalogo.ficha_artista(kc.id)
    assert ficha.arte is not None and ficha.arte.estilo == "bold red"
    assert ficha.ciudad == "Londres" and ficha.pais == "Reino Unido"
    assert [a.titulo for a in ficha.discografia] == [
        "In the Court of the Crimson King",
        "Red",
        "Discipline",
        "VROOOM",
    ]
    assert len(ficha.integrantes) == 37
    assert catalogo.ficha_artista(999999) is None


def test_ficha_persona_con_sus_bandas(catalogo):
    mccartney = buscar(catalogo.personas(), "Paul McCartney")
    ficha = catalogo.ficha_persona(mccartney.id)
    assert ficha.nombre_legal == "James Paul McCartney"
    assert ficha.ciudad == "Liverpool"
    assert {m.artista for m in ficha.membresias} == {"The Beatles", "Paul McCartney", "Wings"}


def test_ficha_cancion_con_sus_albumes(catalogo):
    something = buscar(catalogo.canciones(), "Something")
    ficha = catalogo.ficha_cancion(something.id)
    assert [a.titulo for a in ficha.albumes] == ["Abbey Road", "1"]
    assert {(c.persona, c.rol) for c in ficha.creditos} >= {
        ("George Harrison", "Compositor"),
        ("George Martin", "Productor"),
    }
    assert ficha.duracion_texto == "3:03"
    assert ficha.interpretes[0].artista == "The Beatles"


def test_ficha_genero_incluye_subgeneros(catalogo):
    ficha = catalogo.ficha_genero("Rock progresivo")
    assert {n.nombre for n in ficha.arbol} == {
        "Rock progresivo",
        "Rock sinfónico",
        "Metal progresivo",
    }
    assert "King Crimson" in {a.nombre for a in ficha.artistas}
    assert "Red" in {a.titulo for a in ficha.albumes}
    assert catalogo.ficha_genero("No existe") is None


def test_referencia_inexistente_no_falla(catalogo):
    assert catalogo.canciones_de_persona(Referencia(999999, "Nadie (ficticio)")) == []
