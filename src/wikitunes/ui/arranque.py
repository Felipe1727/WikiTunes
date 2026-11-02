"""Animación de arranque: un conejito con audífonos que escucha música.

Los fotogramas son texto puro (`fotogramas()`), así se pueden probar sin terminal. La animación
dura entre 2 y 3 segundos, se puede saltar con cualquier tecla y termina en la portada.
"""

import os
import sys
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager

import pyfiglet
from rich.console import Console, Group
from rich.live import Live
from rich.text import Text

SEGUNDOS_POR_FOTOGRAMA = 0.15

# Conejito con audífonos: la diadema pasa sobre las orejas y los auriculares tapan los costados.
OREJAS = "        (\\_/)"
DIADEMA = "      ╭─┴───┴─╮"
CARAS = {
    "abre": "    ███(='.'=)███",
    "disfruta": "    ███(=^.^=)███",
    "cierra": "    ███(=-.-=)███",
}
PATAS = '(")_(")'

# Notas que aparecen alrededor de la cabeza, en posiciones que cambian con el ritmo.
NOTAS = [
    ("♪", 2, 0),
    ("♫", 17, 1),
    ("♬", 0, 2),
    ("♪", 19, 0),
    ("♫", 3, 1),
    ("♬", 18, 2),
]


def _con_notas(lineas: list[str], cantidad: int, desfase: int) -> list[str]:
    """Agrega `cantidad` notas a las tres líneas superiores, rotando según `desfase`."""
    filas = [list(linea.ljust(22)) for linea in lineas]
    for indice in range(cantidad):
        nota, columna, fila = NOTAS[(indice + desfase) % len(NOTAS)]
        filas[fila][columna] = nota
    return ["".join(f).rstrip() for f in filas]


def _conejo(cara: str, inclinacion: int) -> list[str]:
    """El conejito completo; `inclinacion` mueve la cabeza (-1 izquierda, 1 derecha)."""
    margen = " " * (1 + inclinacion)
    return [
        "",
        margen + OREJAS,
        margen + DIADEMA,
        margen + CARAS[cara],
        " " * 8 + PATAS,
    ]


def _titulo() -> list[str]:
    lineas = pyfiglet.figlet_format("WikiTunes", font="small").rstrip("\n").splitlines()
    return [linea.rstrip() for linea in lineas] + [
        "   catálogo musical · The Beatles · King Crimson"
    ]


def fotogramas() -> list[str]:
    """Todos los fotogramas de la animación, como texto (el último es la portada)."""
    cuadros: list[str] = []
    completo = _conejo("abre", 0)
    # 1) Aparición progresiva, de arriba abajo.
    for visibles in range(2, len(completo) + 1):
        cuadros.append("\n".join(completo[:visibles]))
    # 2) El conejito cabecea al ritmo y aparecen las notas.
    ritmo = [(-1, "cierra"), (0, "disfruta"), (1, "cierra"), (0, "disfruta")] * 3
    for paso, (inclinacion, cara) in enumerate(ritmo):
        lineas = _conejo(cara, inclinacion)
        cuadros.append("\n".join(_con_notas(lineas, min(paso + 1, 3), paso)))
    # 3) Portada: el conejito quieto, feliz, con el título.
    cuadros.append(portada())
    return cuadros


def portada() -> str:
    """El último fotograma: conejito, notas y título."""
    return "\n".join(_con_notas(_conejo("disfruta", 0), 3, 0) + [""] + _titulo())


def renderizable(fotograma: str) -> Text:
    """El fotograma con color: conejito rosado, audífonos morados, notas celestes."""
    texto = Text(fotograma, style="bold bright_white")
    texto.highlight_regex(r"[♪♫♬]", "bold bright_cyan")
    texto.highlight_regex(r"[█╭╮─┴]+", "magenta")
    texto.highlight_regex(r"\(\\_/\)|\(=.\.=\)|\(\"\)_\(\"\)", "bold pink1")
    return texto


class LectorDeTeclas:
    """Detecta si se pulsó una tecla (sin bloquear) mientras dura la animación."""

    def __init__(self) -> None:
        self._activo = False

    @contextmanager
    def escuchando(self) -> Iterator["LectorDeTeclas"]:
        if not sys.stdin.isatty():
            yield self
            return
        if os.name == "nt":
            self._activo = True
            try:
                yield self
            finally:
                self._activo = False
            return
        import termios
        import tty

        descriptor = sys.stdin.fileno()
        anterior = termios.tcgetattr(descriptor)
        try:
            tty.setcbreak(descriptor)
            self._activo = True
            yield self
        finally:
            self._activo = False
            termios.tcsetattr(descriptor, termios.TCSADRAIN, anterior)

    def pulsada(self, espera: float) -> bool:
        """Espera hasta `espera` segundos y devuelve si se pulsó una tecla (y la consume)."""
        if not self._activo:
            time.sleep(espera)
            return False
        if os.name == "nt":
            import msvcrt

            limite = time.monotonic() + espera
            while time.monotonic() < limite:
                if msvcrt.kbhit():
                    msvcrt.getwch()
                    return True
                time.sleep(0.01)
            return False
        import select

        listos, _, _ = select.select([sys.stdin], [], [], espera)
        if listos:
            os.read(sys.stdin.fileno(), 1024)
            return True
        return False


def reproducir_animacion(
    consola: Console,
    pulsada: Callable[[float], bool] | None = None,
    segundos_por_fotograma: float = SEGUNDOS_POR_FOTOGRAMA,
) -> bool:
    """Reproduce la animación y deja la portada en pantalla. Devuelve si se saltó con una tecla.

    `pulsada(espera)` espera entre fotogramas y dice si se pulsó una tecla; por defecto se lee el
    teclado real.
    """
    cuadros = fotogramas()
    lector = LectorDeTeclas()
    with lector.escuchando():
        esperar = pulsada or lector.pulsada
        saltada = False
        with Live(renderizable(cuadros[0]), console=consola, auto_refresh=False) as vivo:
            for cuadro in cuadros:
                vivo.update(renderizable(cuadro), refresh=True)
                if esperar(segundos_por_fotograma):
                    saltada = True
                    break
            vivo.update(renderizable(cuadros[-1]), refresh=True)
    return saltada


def mostrar_portada(consola: Console) -> None:
    """La portada sin animación."""
    consola.print(Group(renderizable(portada())))
