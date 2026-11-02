"""Menú principal: «¿Qué quieres consultar?»."""

from dataclasses import dataclass

import questionary
from questionary import Style

ESTILO_PREGUNTAS = Style(
    [
        ("qmark", "fg:#ff87d7 bold"),
        ("question", "bold"),
        ("pointer", "fg:#ff87d7 bold"),
        ("highlighted", "fg:#ff87d7 bold"),
        ("selected", "fg:#87d7ff"),
        ("answer", "fg:#87d7ff bold"),
        ("instruction", "fg:#808080 italic"),
    ]
)

PREGUNTA_PRINCIPAL = "¿Qué quieres consultar?"


@dataclass(frozen=True)
class Opcion:
    clave: str
    titulo: str


OPCIONES_PRINCIPALES = [
    Opcion("canciones_persona", "Canciones de una persona"),
    Opcion("arbol_generos", "Árbol de un género"),
    Opcion("tracklist", "Tracklist de un álbum"),
    Opcion("integrantes_fecha", "Integrantes de un artista en una fecha"),
    Opcion("historial", "Historial de integrantes de un artista"),
    Opcion("ficha_artista", "Ficha de un artista"),
    Opcion("ficha_persona", "Ficha de una persona"),
    Opcion("ficha_cancion", "Ficha de una canción"),
    Opcion("salir", "Salir"),
]


def elegir(pregunta: str, opciones: list[Opcion]) -> str | None:
    """Muestra un menú y devuelve la clave elegida (`None` si se cancela con Ctrl+C)."""
    return questionary.select(
        pregunta,
        choices=[questionary.Choice(o.titulo, value=o.clave) for o in opciones],
        style=ESTILO_PREGUNTAS,
        instruction="(flechas y Enter)",
        qmark="♪",
    ).ask()


def menu_principal() -> str | None:
    return elegir(PREGUNTA_PRINCIPAL, OPCIONES_PRINCIPALES)
