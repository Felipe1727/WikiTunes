"""Pruebas de los errores de conexión (sin base de datos)."""

import socket

import pytest

from wikitunes.conexion import ErrorDeConexion, conectar
from wikitunes.configuracion import ConfiguracionBD


def puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_base_caida_da_un_error_en_espanol():
    configuracion = ConfiguracionBD(
        host="127.0.0.1",
        puerto=puerto_libre(),
        nombre="musica",
        usuario="wikitunes",
        clave="wikitunes",
        clave_root="x",
    )
    with pytest.raises(ErrorDeConexion) as error:
        conectar(configuracion)
    mensaje = str(error.value)
    assert "No se pudo conectar a la base de datos" in mensaje
    assert "docker compose up -d --wait" in mensaje


def test_puerto_invalido(monkeypatch):
    monkeypatch.setenv("WIKITUNES_BD_PUERTO", "no-es-numero")
    with pytest.raises(ValueError, match="WIKITUNES_BD_PUERTO"):
        ConfiguracionBD.desde_entorno()
