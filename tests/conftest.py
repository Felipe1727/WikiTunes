"""Configuración compartida de las pruebas.

Las pruebas marcadas con `integracion` usan los fixtures `conexion_bd` (usuario de solo lectura)
o `conexion_bd_root`. Si la base no responde, se saltan con un aviso, salvo que
`WIKITUNES_EXIGIR_BD=1`, en cuyo caso fallan.
"""

import os
from collections.abc import Iterator
from pathlib import Path

import mysql.connector
import pytest

from wikitunes.configuracion import ConfiguracionBD

RAIZ_REPOSITORIO = Path(__file__).resolve().parent.parent


def base_exigida() -> bool:
    return os.getenv("WIKITUNES_EXIGIR_BD") == "1"


def _conectar_o_saltar(*, como_root: bool) -> mysql.connector.MySQLConnection:
    parametros = ConfiguracionBD.desde_entorno().parametros_conector(como_root=como_root)
    try:
        return mysql.connector.connect(**parametros)
    except mysql.connector.Error as error:
        mensaje = (
            "No hay conexión con la base de datos "
            f"({error}). Levántala con `docker compose up -d --wait`."
        )
        if base_exigida():
            pytest.fail(mensaje, pytrace=False)
        pytest.skip(mensaje)


@pytest.fixture(scope="session")
def conexion_bd() -> Iterator[mysql.connector.MySQLConnection]:
    """Conexión de solo lectura a la base `musica`, compartida por toda la sesión."""
    conexion = _conectar_o_saltar(como_root=False)
    try:
        yield conexion
    finally:
        conexion.close()


@pytest.fixture(scope="session")
def conexion_bd_root() -> Iterator[mysql.connector.MySQLConnection]:
    """Conexión como `root` a la base `musica`, compartida por toda la sesión."""
    conexion = _conectar_o_saltar(como_root=True)
    try:
        yield conexion
    finally:
        conexion.close()
