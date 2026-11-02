"""Encabezados de las consultas: el arte ASCII del artista o un título generado con pyfiglet."""

import pyfiglet
from rich.cells import cell_len
from rich.console import Console, RenderableType
from rich.text import Text

from wikitunes.modelos import Arte

FUENTES_TITULO = ("standard", "small", "mini")


def _ancho(texto: str) -> int:
    return max((cell_len(linea) for linea in texto.splitlines()), default=0)


def titulo_generado(texto: str, ancho_disponible: int, estilo: str = "bold bright_magenta") -> Text:
    """El texto en la fuente de pyfiglet más grande que quepa; si ninguna cabe, texto simple."""
    for fuente in FUENTES_TITULO:
        figura = pyfiglet.figlet_format(texto, font=fuente, width=10_000).rstrip()
        if _ancho(figura) <= ancho_disponible:
            return Text(figura, style=estilo)
    return Text(texto, style=estilo)


def encabezado_artista(arte: Arte | None, nombre: str, ancho_disponible: int) -> RenderableType:
    """El arte guardado del artista, con su estilo; si no hay o no cabe, el nombre con pyfiglet."""
    if arte is not None and _ancho(arte.texto) <= ancho_disponible:
        return Text(arte.texto, style=arte.estilo or "bold")
    return titulo_generado(nombre, ancho_disponible, (arte.estilo if arte else None) or "bold")


def mostrar_encabezado(consola: Console, encabezado: RenderableType) -> None:
    consola.print()
    consola.print(encabezado)
    consola.print()
