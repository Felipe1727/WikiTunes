"""Preguntas al usuario: elegir con autocompletado y pedir fechas.

`Preguntas` agrupa todas las interacciones para poder reemplazarlas en las pruebas.
"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date

import questionary
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document

from wikitunes.ui.menu import ESTILO_PREGUNTAS, Opcion, elegir
from wikitunes.ui.textos import normalizar


@dataclass(frozen=True)
class Elegible[T]:
    """Un elemento elegible: el texto que se muestra y el valor que representa."""

    texto: str
    valor: T


class CompletadorNormalizado(Completer):
    """Sugiere las opciones que contienen lo escrito, sin distinguir mayúsculas, tildes ni
    comillas tipográficas (así «maxwells» encuentra «Maxwell’s Silver Hammer»)."""

    def __init__(self, opciones: Sequence[str]) -> None:
        self.opciones = list(opciones)
        self._normalizadas = [normalizar(o) for o in self.opciones]

    def coincidencias(self, escrito: str) -> list[str]:
        buscado = normalizar(escrito)
        return [o for o, n in zip(self.opciones, self._normalizadas, strict=True) if buscado in n]

    def get_completions(self, document: Document, complete_event) -> Iterable[Completion]:
        for opcion in self.coincidencias(document.text_before_cursor):
            yield Completion(opcion, start_position=-len(document.text_before_cursor))


def resolver[T](escrito: str, elegibles: Sequence[Elegible[T]]) -> Elegible[T] | None:
    """El elegible que corresponde a lo escrito: coincidencia exacta (normalizada) o única."""
    buscado = normalizar(escrito)
    exactos = [e for e in elegibles if normalizar(e.texto) == buscado]
    if exactos:
        return exactos[0]
    parciales = [e for e in elegibles if buscado and buscado in normalizar(e.texto)]
    return parciales[0] if len(parciales) == 1 else None


def interpretar_fecha(escrito: str) -> date | None:
    """`AAAA-MM-DD` → fecha; `None` si el formato o la fecha no son válidos."""
    try:
        return date.fromisoformat(escrito.strip())
    except ValueError:
        return None


class Preguntas:
    """Interacciones con el usuario a través de questionary."""

    def elegir_opcion(self, pregunta: str, opciones: list[Opcion]) -> str | None:
        return elegir(pregunta, opciones)

    def elegir[T](self, pregunta: str, elegibles: Sequence[Elegible[T]]) -> T | None:
        """Pide un elemento con autocompletado. `None` si se cancela."""
        textos = [e.texto for e in elegibles]

        def validar(escrito: str) -> bool | str:
            if resolver(escrito, elegibles) is not None:
                return True
            return "Elige una opción de la lista (Tab muestra las sugerencias)."

        respuesta = questionary.autocomplete(
            pregunta,
            choices=textos,
            completer=CompletadorNormalizado(textos),
            validate=validar,
            style=ESTILO_PREGUNTAS,
            qmark="♪",
        ).ask()
        if respuesta is None:
            return None
        elegido = resolver(respuesta, elegibles)
        return elegido.valor if elegido else None

    def pedir_fecha(self, pregunta: str, predeterminada: str = "") -> date | None:
        def validar(escrito: str) -> bool | str:
            if interpretar_fecha(escrito) is None:
                return "Escribe una fecha válida con el formato AAAA-MM-DD (p. ej. 1974-06-01)."
            return True

        respuesta = questionary.text(
            pregunta,
            default=predeterminada,
            validate=validar,
            style=ESTILO_PREGUNTAS,
            qmark="♪",
            instruction="(AAAA-MM-DD)",
        ).ask()
        return interpretar_fecha(respuesta) if respuesta is not None else None
