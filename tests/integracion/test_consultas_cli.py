"""Las cinco consultas de la CLI contra los datos de la demo, con respuestas simuladas."""

from datetime import date

import pytest
from rich.console import Console

from wikitunes.catalogo import Catalogo
from wikitunes.ui import consultas
from wikitunes.ui.preguntas import resolver

pytestmark = pytest.mark.integracion


class PreguntasFalsas:
    """Responde con textos fijos, resueltos igual que en el autocompletado real."""

    def __init__(self, *respuestas: str, fecha: date | None = None) -> None:
        self.respuestas = list(respuestas)
        self.fecha = fecha

    def elegir(self, _pregunta, elegibles):
        elegido = resolver(self.respuestas.pop(0), elegibles)
        assert elegido is not None
        return elegido.valor

    def pedir_fecha(self, _pregunta, predeterminada=""):
        return self.fecha


@pytest.fixture
def catalogo(conexion_bd):
    cat = Catalogo(conexion_bd)
    if not cat.artistas():
        pytest.skip("No están cargados los datos de la demo (docker compose up -d --wait).")
    return cat


@pytest.fixture
def consola():
    return Console(width=120, record=True, color_system=None)


def test_integrantes_en_fecha_con_el_arte_primero(consola, catalogo):
    preguntas = PreguntasFalsas("king crimson", fecha=date(1974, 6, 1))
    consultas.integrantes_en_fecha(consola, catalogo, preguntas)
    salida = consola.export_text()
    arte = catalogo.arte_de_artista(101).texto.splitlines()[0].strip()
    assert salida.index(arte) < salida.index("Integrantes de King Crimson el 1 de junio de 1974")
    assert "John Wetton" in salida and "1972–1974" in salida


def test_integrantes_en_una_fecha_sin_banda(consola, catalogo):
    consultas.integrantes_en_fecha(
        consola, catalogo, PreguntasFalsas("King Crimson", fecha=date(1990, 1, 1))
    )
    assert "Sin resultados" in consola.export_text()


def test_historial_de_the_beatles(consola, catalogo):
    consultas.historial_de_integrantes(consola, catalogo, PreguntasFalsas("the beatles"))
    salida = consola.export_text()
    assert "▀█▀ █ █ █▀▀" in salida  # el «THE» del arte de The Beatles
    assert "Pete Best" in salida and "1960–1962" in salida


def test_tracklist_con_encabezado_generado(consola, catalogo):
    consultas.tracklist_de_album(consola, catalogo, PreguntasFalsas("Abbey Road"))
    salida = consola.export_text()
    assert "Come Together" in salida
    assert "LP · 17 pistas · duración total 47:25" in salida


def test_arbol_de_rock(consola, catalogo):
    consultas.arbol_de_genero(consola, catalogo, PreguntasFalsas("rock"))
    salida = consola.export_text()
    assert "Heavy metal" in salida and "Rock sinfónico" in salida


def test_canciones_de_ringo(consola, catalogo):
    consultas.canciones_de_persona(consola, catalogo, PreguntasFalsas("ringo starr"))
    salida = consola.export_text()
    assert "Octopus’s Garden" in salida and "Photograph" in salida
