"""Pruebas del punto de entrada `wikitunes` (sin terminal ni base de datos)."""

import pytest
from rich.console import Console

from wikitunes import cli
from wikitunes.conexion import ErrorDeBaseDeDatos, ErrorDeConexion


class ConexionFalsa:
    def close(self) -> None:
        pass


@pytest.fixture
def consola():
    return Console(record=True, width=100, color_system=None)


@pytest.fixture
def sin_animacion(monkeypatch):
    def prohibida(*_args, **_kwargs):
        raise AssertionError("no debía animarse")

    monkeypatch.setattr(cli, "reproducir_animacion", prohibida)


@pytest.mark.parametrize(
    ("sin_animacion", "es_tty", "entorno", "esperado"),
    [
        (False, True, {}, True),
        (True, True, {}, False),
        (False, False, {}, False),
        (False, True, {"NO_COLOR": "1"}, False),
    ],
)
def test_debe_animarse(sin_animacion, es_tty, entorno, esperado):
    assert cli.debe_animarse(sin_animacion, es_tty, entorno) is esperado


def test_base_caida_muestra_un_aviso_sin_traceback(monkeypatch, consola, sin_animacion):
    def falla():
        raise ErrorDeConexion("No se pudo conectar. Prueba con `docker compose up -d --wait`.")

    monkeypatch.setattr(cli, "conectar", falla)
    assert cli.principal(["--sin-animacion"], consola) == 1
    salida = consola.export_text()
    assert "docker compose up -d" in salida
    assert "Traceback" not in salida


def test_menu_y_salir(monkeypatch, consola, sin_animacion):
    monkeypatch.setattr(cli, "conectar", ConexionFalsa)
    monkeypatch.setattr(cli.menu, "menu_principal", lambda: "salir")
    assert cli.principal(["--sin-animacion"], consola) == 0
    salida = consola.export_text()
    assert "catálogo musical" in salida  # portada
    assert "¡Hasta pronto!" in salida


def test_ctrl_c_sale_sin_traceback(monkeypatch, consola, sin_animacion):
    def interrumpir():
        raise KeyboardInterrupt

    monkeypatch.setattr(cli, "conectar", ConexionFalsa)
    monkeypatch.setattr(cli.menu, "menu_principal", interrumpir)
    assert cli.principal(["--sin-animacion"], consola) == 130
    assert "¡Hasta pronto!" in consola.export_text()


def test_cancelar_el_menu_sale(monkeypatch, consola, sin_animacion):
    monkeypatch.setattr(cli, "conectar", ConexionFalsa)
    monkeypatch.setattr(cli.menu, "menu_principal", lambda: None)
    assert cli.principal(["--sin-animacion"], consola) == 0


def test_error_en_una_consulta_vuelve_al_menu(monkeypatch, consola, sin_animacion):
    respuestas = iter(["tracklist", "salir"])

    def fallar(_consola, _catalogo):
        raise ErrorDeBaseDeDatos("Error de la base de datos: algo salió mal.")

    monkeypatch.setattr(cli, "conectar", ConexionFalsa)
    monkeypatch.setattr(cli.menu, "menu_principal", lambda: next(respuestas))
    monkeypatch.setattr(cli, "acciones", lambda: {"tracklist": fallar})
    assert cli.principal(["--sin-animacion"], consola) == 0
    assert "algo salió mal" in consola.export_text()


def test_el_menu_principal_tiene_la_pregunta_y_las_consultas():
    from wikitunes.ui import menu

    assert menu.PREGUNTA_PRINCIPAL == "¿Qué quieres consultar?"
    claves = [o.clave for o in menu.OPCIONES_PRINCIPALES]
    assert claves[-1] == "salir" and len(claves) == 9
