"""Pruebas de textos, autocompletado y encabezados de la interfaz."""

from datetime import date

import pytest
from rich.console import Console

from wikitunes.modelos import Arte
from wikitunes.ui.encabezados import encabezado_artista, titulo_generado
from wikitunes.ui.preguntas import CompletadorNormalizado, Elegible, interpretar_fecha, resolver
from wikitunes.ui.textos import ROLES, TIPOS_ALBUM, fecha_larga, normalizar, traducir


def test_traducciones_del_esquema():
    assert traducir("Compilation", TIPOS_ALBUM) == "Compilación"
    assert traducir("Single", TIPOS_ALBUM) == "Sencillo"
    assert traducir("Featuring", ROLES) == "Invitado (feat.)"
    assert traducir("Musico de sesion", ROLES) == "Músico de sesión"
    assert traducir("Algo nuevo", ROLES) == "Algo nuevo"
    assert traducir(None, ROLES) == "—"


def test_fecha_larga():
    assert fecha_larga(date(1974, 6, 1)) == "1 de junio de 1974"


def test_normalizar_ignora_mayusculas_tildes_y_comillas():
    assert normalizar("Maxwell’s") == normalizar("maxwell's")
    assert normalizar("Rock Psicodélico") == "rock psicodelico"


def test_autocompletado_encuentra_por_subcadena_normalizada():
    completador = CompletadorNormalizado(["Paul McCartney", "Maxwell’s Silver Hammer", "Música"])
    assert completador.coincidencias("mccart") == ["Paul McCartney"]
    assert completador.coincidencias("maxwell's") == ["Maxwell’s Silver Hammer"]
    assert completador.coincidencias("musica") == ["Música"]


def test_resolver():
    elegibles = [Elegible("Get Back", 1), Elegible("Get Back (LP)", 2), Elegible("Red", 3)]
    assert resolver("get back", elegibles).valor == 1  # exacta antes que parcial
    assert resolver("red", elegibles).valor == 3
    assert resolver("back (l", elegibles).valor == 2  # parcial única
    assert resolver("e", elegibles) is None  # ambigua
    assert resolver("nada", elegibles) is None


@pytest.mark.parametrize(
    ("escrito", "esperado"),
    [
        ("1974-06-01", date(1974, 6, 1)),
        (" 1969-10-10 ", date(1969, 10, 10)),
        ("1974-13-01", None),
        ("ayer", None),
    ],
)
def test_interpretar_fecha(escrito, esperado):
    assert interpretar_fecha(escrito) == esperado


ARTE = Arte("█▀▀ LOGO\n█▄▄ LOGO", "bold red")


def test_encabezado_con_el_arte_si_cabe():
    texto = encabezado_artista(ARTE, "Banda", 80)
    assert texto.plain == ARTE.texto
    assert str(texto.style) == "bold red"


def test_encabezado_con_pyfiglet_si_el_arte_no_cabe():
    texto = encabezado_artista(ARTE, "Banda", 5)
    assert texto.plain == "Banda"  # ni siquiera pyfiglet cabe en 5 columnas


def test_encabezado_sin_arte_usa_el_nombre():
    texto = encabezado_artista(None, "Wings", 80)
    assert "\n" in texto.plain  # figura de varias líneas


def test_titulo_generado_cabe_en_el_ancho():
    for ancho in (100, 60, 40):
        texto = titulo_generado("In the Court of the Crimson King", ancho)
        consola = Console(width=200, record=True)
        consola.print(texto)
        assert max(len(linea) for linea in consola.export_text().splitlines()) <= max(
            ancho, len(texto.plain)
        )
