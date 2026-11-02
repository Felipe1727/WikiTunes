"""Pruebas de integración del cargador con datos FICTICIOS (`tests/datos_ejemplo/`).

`cargar(..., confirmar=False)` no hace COMMIT y cada prueba termina con ROLLBACK: los datos reales
de la demo no se pierden.
"""

import shutil
from pathlib import Path

import pytest

from wikitunes.cargador import ORDEN_TABLAS, ErrorDeCarga, cargar

pytestmark = pytest.mark.integracion

DATOS_EJEMPLO = Path(__file__).parent.parent / "datos_ejemplo"


@pytest.fixture
def root(conexion_bd_root):
    conexion_bd_root.rollback()
    try:
        yield conexion_bd_root
    finally:
        conexion_bd_root.rollback()


def contar_filas(conexion) -> dict[str, int]:
    cursor = conexion.cursor()
    cantidades = {}
    for tabla in ORDEN_TABLAS:
        cursor.execute(f"SELECT COUNT(*) FROM `{tabla}`")
        cantidades[tabla] = cursor.fetchone()[0]
    cursor.close()
    return cantidades


def test_carga_los_datos_de_ejemplo(root):
    cantidades = cargar(root, DATOS_EJEMPLO, confirmar=False)
    assert cantidades["genero"] == 3
    cursor = root.cursor()
    cursor.execute("SELECT nombre_legal, nombre_conocido, fecha_fallecimiento FROM persona")
    assert cursor.fetchall() == [
        ('Persona "Apodo" Ficticia', "Persona\nde dos líneas (ficticio)", None)
    ]
    cursor.execute("SELECT nombre FROM pais")
    assert cursor.fetchall() == [("País ficticio, con coma",)]
    cursor.execute("SELECT arte, estilo FROM arte_artista WHERE artista_id = 9001")
    arte, estilo = cursor.fetchone()
    assert arte == ' ╔═╗ \\ barra \\n literal "comillas"\n  ▀▀▀ espacios finales   '
    assert estilo == "bold red"
    cursor.execute("SELECT genero_padre_id FROM genero WHERE genero_id = 9003")
    assert cursor.fetchone() == (9002,)
    cursor.close()


def test_la_recarga_no_duplica(root):
    cargar(root, DATOS_EJEMPLO, confirmar=False)
    primera = contar_filas(root)
    cargar(root, DATOS_EJEMPLO, confirmar=False)
    assert contar_filas(root) == primera


def test_directorio_vacio_deja_la_base_vacia(root, tmp_path):
    assert cargar(root, tmp_path, confirmar=False) == {}
    assert set(contar_filas(root).values()) == {0}


def test_error_indica_archivo_y_linea_y_no_deja_cambios(root, tmp_path):
    antes = contar_filas(root)
    shutil.copytree(DATOS_EJEMPLO, tmp_path, dirs_exist_ok=True)
    with (tmp_path / "membresia.csv").open("a", encoding="utf-8") as archivo:
        archivo.write("9002,9999,9001,Bajo,1971-01-01,\n")  # persona 9999 no existe
    with pytest.raises(ErrorDeCarga, match=r"membresia\.csv, línea 3"):
        cargar(root, tmp_path, confirmar=False)
    assert contar_filas(root) == antes


def test_columna_desconocida_en_la_base(root, tmp_path):
    (tmp_path / "pais.csv").write_text("pais_id,inventada\n1,x\n", encoding="utf-8")
    with pytest.raises(ErrorDeCarga, match="columna desconocida.*inventada"):
        cargar(root, tmp_path, confirmar=False)
