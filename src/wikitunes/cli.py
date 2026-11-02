"""Punto de entrada de la línea de comandos: `wikitunes`."""

import argparse
import os
import sys
from collections.abc import Callable, Mapping, Sequence

from rich.console import Console
from rich.panel import Panel

from wikitunes import __version__
from wikitunes.catalogo import Catalogo
from wikitunes.conexion import ErrorDeBaseDeDatos, ErrorDeConexion, conectar
from wikitunes.ui import menu
from wikitunes.ui.arranque import mostrar_portada, reproducir_animacion

Accion = Callable[[Console, Catalogo], None]


def crear_analizador() -> argparse.ArgumentParser:
    analizador = argparse.ArgumentParser(
        prog="wikitunes",
        description="Explora un catálogo musical: artistas, personas, álbumes y canciones.",
    )
    analizador.add_argument(
        "--sin-animacion", action="store_true", help="no mostrar la animación de arranque"
    )
    analizador.add_argument("--version", action="version", version=f"wikitunes {__version__}")
    return analizador


def debe_animarse(sin_animacion: bool, es_tty: bool, entorno: Mapping[str, str]) -> bool:
    """La animación solo corre en una terminal interactiva, con color y si no se desactivó."""
    return not sin_animacion and es_tty and "NO_COLOR" not in entorno


def mostrar_error(consola: Console, mensaje: str) -> None:
    consola.print(Panel(mensaje, title="No se pudo completar", border_style="red", expand=False))


def accion_pendiente(consola: Console, _catalogo: Catalogo) -> None:
    consola.print("[italic]Esta consulta todavía no está disponible.[/italic]")


def acciones() -> dict[str, Accion]:
    """Acción de cada opción del menú principal."""
    return {opcion.clave: accion_pendiente for opcion in menu.OPCIONES_PRINCIPALES}


def bucle_principal(consola: Console, catalogo: Catalogo) -> int:
    disponibles = acciones()
    while True:
        consola.print()
        eleccion = menu.menu_principal()
        if eleccion in (None, "salir"):
            consola.print("[bold bright_magenta]¡Hasta pronto![/] ♪")
            return 0
        try:
            disponibles[eleccion](consola, catalogo)
        except ErrorDeConexion as error:
            mostrar_error(consola, str(error))
            return 1
        except ErrorDeBaseDeDatos as error:
            mostrar_error(consola, str(error))


def principal(argumentos: Sequence[str] | None = None, consola: Console | None = None) -> int:
    opciones = crear_analizador().parse_args(argumentos)
    consola = consola or Console()
    try:
        if debe_animarse(opciones.sin_animacion, sys.stdout.isatty(), os.environ):
            reproducir_animacion(consola)
        else:
            mostrar_portada(consola)
        try:
            conexion = conectar()
        except ErrorDeConexion as error:
            mostrar_error(consola, str(error))
            return 1
        try:
            return bucle_principal(consola, Catalogo(conexion))
        finally:
            conexion.close()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C, o la entrada se cerró (Ctrl+D o sin terminal interactiva).
        consola.print("\n[bold bright_magenta]¡Hasta pronto![/] ♪")
        return 130


def ejecutar() -> None:
    sys.exit(principal())
