"""Consultas, fichas y navegación contra los datos de la demo, con un guion de respuestas."""

from datetime import date

import pytest
from rich.console import Console

from wikitunes.catalogo import Catalogo
from wikitunes.ui import acciones
from wikitunes.ui.navegacion import Contexto
from wikitunes.ui.preguntas import resolver

pytestmark = pytest.mark.integracion


class Guion:
    """Responde según una lista de pasos: ("elegir", texto), ("opcion", texto) o ("fecha", d).

    Cuando se acaban los pasos, «¿Y ahora?» vuelve al menú principal.
    """

    def __init__(self, *pasos) -> None:
        self.pasos = list(pasos)
        self.menus: list[list[str]] = []  # opciones de cada «¿Y ahora?»

    def _siguiente(self, tipo: str):
        paso_tipo, valor = self.pasos.pop(0)
        assert paso_tipo == tipo, f"se esperaba {paso_tipo}, se pidió {tipo}"
        return valor

    def elegir(self, _pregunta, elegibles):
        texto = self._siguiente("elegir")
        elegido = resolver(texto, elegibles)
        assert elegido is not None, f"{texto!r} no está entre {[e.texto for e in elegibles][:10]}"
        return elegido.valor

    def elegir_opcion(self, _pregunta, opciones):
        self.menus.append([o.titulo for o in opciones])
        if not self.pasos:
            return "menu"
        texto = self._siguiente("opcion")
        coincidencias = [o for o in opciones if texto in o.titulo]
        assert coincidencias, f"{texto!r} no está entre {[o.titulo for o in opciones]}"
        return coincidencias[0].clave

    def pedir_fecha(self, _pregunta, predeterminada=""):
        return self._siguiente("fecha")


@pytest.fixture
def catalogo(conexion_bd):
    cat = Catalogo(conexion_bd)
    if not cat.artistas():
        pytest.skip("No están cargados los datos de la demo (docker compose up -d --wait).")
    return cat


def ejecutar(catalogo, accion, guion: Guion) -> str:
    consola = Console(width=120, record=True, color_system=None)
    accion(Contexto(consola, catalogo, guion))
    assert not guion.pasos, f"pasos sin usar: {guion.pasos}"
    return consola.export_text()


# --- Las cinco consultas ---------------------------------------------------------------------


def test_integrantes_en_fecha_con_el_arte_primero(catalogo):
    salida = ejecutar(
        catalogo,
        acciones.integrantes_en_fecha,
        Guion(("elegir", "king crimson"), ("fecha", date(1974, 6, 1))),
    )
    arte = catalogo.arte_de_artista(101).texto.splitlines()[0].strip()
    assert salida.index(arte) < salida.index("Integrantes de King Crimson el 1 de junio de 1974")
    assert "John Wetton" in salida and "1972–1974" in salida


def test_integrantes_en_una_fecha_sin_banda(catalogo):
    salida = ejecutar(
        catalogo,
        acciones.integrantes_en_fecha,
        Guion(("elegir", "King Crimson"), ("fecha", date(1990, 1, 1))),
    )
    assert "Sin resultados" in salida


def test_historial_de_the_beatles(catalogo):
    salida = ejecutar(catalogo, acciones.historial_de_integrantes, Guion(("elegir", "the beatles")))
    assert "▀█▀ █ █ █▀▀" in salida  # el «THE» del arte de The Beatles
    assert "Pete Best" in salida and "1960–1962" in salida


def test_tracklist_con_resumen(catalogo):
    salida = ejecutar(catalogo, acciones.tracklist_de_album, Guion(("elegir", "Abbey Road")))
    assert "Come Together" in salida
    assert "LP · 17 pistas · duración total 47:25" in salida


def test_arbol_de_rock(catalogo):
    salida = ejecutar(catalogo, acciones.arbol_de_genero, Guion(("elegir", "rock")))
    assert "Heavy metal" in salida and "Rock sinfónico" in salida


def test_canciones_de_ringo(catalogo):
    salida = ejecutar(catalogo, acciones.canciones_de_persona, Guion(("elegir", "ringo starr")))
    assert "Octopus’s Garden" in salida and "Photograph" in salida


# --- Fichas ------------------------------------------------------------------------------------


def test_ficha_de_artista(catalogo):
    salida = ejecutar(catalogo, acciones.ficha_de_artista, Guion(("elegir", "King Crimson")))
    assert "Discografía" in salida and "VROOOM" in salida
    assert "Londres, Reino Unido" in salida
    assert "Rock progresivo" in salida


def test_ficha_de_persona(catalogo):
    salida = ejecutar(catalogo, acciones.ficha_de_persona, Guion(("elegir", "George Harrison")))
    assert "25 de febrero de 1943" in salida and "Liverpool" in salida
    assert "Traveling Wilburys" in salida and "1988–1991" in salida


def test_ficha_de_cancion(catalogo):
    salida = ejecutar(catalogo, acciones.ficha_de_cancion, Guion(("elegir", "Something")))
    assert "George Harrison" in salida and "Productor" in salida
    assert "Abbey Road" in salida and "Compilación" in salida


# --- Navegación --------------------------------------------------------------------------------


def test_cancion_a_su_album(catalogo):
    guion = Guion(("elegir", "Starless"), ("opcion", "Álbum: Red"))
    salida = ejecutar(catalogo, acciones.ficha_de_cancion, guion)
    assert "LP · 5 pistas" in salida
    assert "Menú › Starless › Red" in salida


def test_integrante_a_su_ficha_y_a_otra_banda(catalogo):
    guion = Guion(
        ("elegir", "The Beatles"),
        ("fecha", date(1963, 1, 1)),
        ("opcion", "Persona: Paul McCartney"),
        ("opcion", "Artista: Wings"),
    )
    salida = ejecutar(catalogo, acciones.integrantes_en_fecha, guion)
    assert "James Paul McCartney" in salida
    assert "Band on the Run" in salida  # discografía de Wings
    assert "Paul McCartney › Wings" in salida


def test_genero_a_artista(catalogo):
    guion = Guion(
        ("elegir", "Rock progresivo"),
        ("opcion", "Ver artistas y álbumes"),
        ("elegir", "Rock progresivo"),
        ("opcion", "Ir a un artista"),
        ("elegir", "King Crimson"),
    )
    salida = ejecutar(catalogo, acciones.arbol_de_genero, guion)
    assert "Discografía" in salida and "In the Court of the Crimson King" in salida


def test_tracklist_a_cancion_a_otro_album(catalogo):
    guion = Guion(
        ("elegir", "Abbey Road"),
        ("opcion", "Ir a una canción"),
        ("elegir", "2. Something"),
        ("opcion", "Álbum: 1 (2000)"),
    )
    salida = ejecutar(catalogo, acciones.tracklist_de_album, guion)
    assert "Compilación · 27 pistas" in salida
    assert "Menú › Abbey Road › Something › 1" in salida


def test_volver_y_menu_principal(catalogo):
    guion = Guion(("elegir", "Pete Best"), ("opcion", "Artista: The Beatles"), ("opcion", "Volver"))
    ejecutar(catalogo, acciones.ficha_de_persona, guion)
    # 1.º «¿Y ahora?»: sin «Volver»; 2.º: con «Volver a Pete Best»; 3.º: otra vez en la persona.
    assert not any("Volver" in o for o in guion.menus[0])
    assert "Volver a Pete Best" in guion.menus[1]
    assert guion.menus[2] == guion.menus[0]
    assert all(m[-1] == "Menú principal" for m in guion.menus)


def test_cancelar_un_salto_no_vuelve_a_mostrar_la_pantalla(catalogo):
    class GuionConCancelacion(Guion):
        def elegir(self, pregunta, elegibles):
            if pregunta == "¿Qué integrante?":
                return None
            return super().elegir(pregunta, elegibles)

    guion = GuionConCancelacion(("elegir", "King Crimson"), ("opcion", "Ir a un integrante"))
    salida = ejecutar(catalogo, acciones.historial_de_integrantes, guion)
    assert salida.count("Historial de integrantes de King Crimson") == 1
    assert len(guion.menus) == 2
