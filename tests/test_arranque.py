"""Pruebas de la animación de arranque (renderizada a texto, sin terminal)."""

from rich.cells import cell_len
from rich.console import Console

from wikitunes.ui.arranque import (
    SEGUNDOS_POR_FOTOGRAMA,
    fotogramas,
    portada,
    renderizable,
    reproducir_animacion,
)


def consola_de_prueba() -> Console:
    return Console(record=True, width=100, force_terminal=True, color_system=None)


def test_dura_entre_2_y_3_segundos():
    assert 2.0 <= len(fotogramas()) * SEGUNDOS_POR_FOTOGRAMA <= 3.0


def test_todos_los_fotogramas_caben_en_80_columnas():
    for cuadro in fotogramas():
        assert max(cell_len(linea) for linea in cuadro.splitlines()) <= 80


def test_el_conejito_tiene_audifonos_y_hay_notas():
    cuadros = fotogramas()
    assert "(\\_/)" in cuadros[-1] and "███" in cuadros[-1]
    assert any(nota in cuadro for cuadro in cuadros for nota in "♪♫♬")


def test_el_conejito_mueve_la_cabeza():
    caras = {linea for cuadro in fotogramas() for linea in cuadro.splitlines() if "(=" in linea}
    assert len(caras) >= 3  # distintas posiciones y expresiones


def test_aparicion_progresiva():
    cuadros = fotogramas()
    assert len(cuadros[0].splitlines()) < len(cuadros[3].splitlines())


def test_termina_en_la_portada_con_el_titulo():
    assert fotogramas()[-1] == portada()
    assert "catálogo musical" in portada()


def test_reproducir_sin_pulsar_teclas():
    consola = consola_de_prueba()
    esperas = []
    saltada = reproducir_animacion(consola, pulsada=lambda s: esperas.append(s) or False)
    assert not saltada
    assert len(esperas) == len(fotogramas())
    assert "catálogo musical" in consola.export_text()


def test_saltar_con_una_tecla():
    consola = consola_de_prueba()
    esperas = []
    saltada = reproducir_animacion(consola, pulsada=lambda s: esperas.append(s) or True)
    assert saltada
    assert len(esperas) == 1
    # Aunque se salte, queda la portada.
    assert "catálogo musical" in consola.export_text()


def test_renderizable_conserva_el_texto():
    assert renderizable(portada()).plain == portada()
