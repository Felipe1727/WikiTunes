"""Pruebas del arte ASCII de los artistas (`datos/arte/`), sin base de datos."""

import csv
import importlib.util
import sys
from pathlib import Path

import pytest
from rich.cells import cell_len, get_character_cell_size
from rich.style import Style

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos"
DIRECTORIO_ARTE = DATOS / "arte"
ANCHO_MAXIMO = 80


def leer(nombre: str) -> list[dict[str, str]]:
    with (DATOS / nombre).open(encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


ARTES = leer("arte_artista.csv")


def test_cada_artista_tiene_arte():
    artistas = {fila["artista_id"] for fila in leer("artista.csv")}
    con_arte = {fila["artista_id"] for fila in ARTES}
    assert artistas == con_arte


@pytest.mark.parametrize("fila", ARTES, ids=lambda f: f["archivo"])
def test_formato_del_archivo(fila):
    contenido = (DIRECTORIO_ARTE / fila["archivo"]).read_bytes()
    assert b"\r" not in contenido, "finales de línea CRLF"
    assert b"\t" not in contenido, "tabuladores"
    texto = contenido.decode("utf-8")
    assert texto.endswith("\n") and texto.strip(), "archivo vacío o sin salto final"
    for numero, linea in enumerate(texto.splitlines(), start=1):
        assert cell_len(linea) <= ANCHO_MAXIMO, f"línea {numero} con {cell_len(linea)} columnas"
        anchos_raros = {c for c in linea if get_character_cell_size(c) != 1}
        assert not anchos_raros, (
            f"línea {numero}: caracteres que no ocupan una columna {anchos_raros}"
        )


@pytest.mark.parametrize("fila", ARTES, ids=lambda f: f["archivo"])
def test_estilo_valido_de_rich(fila):
    assert fila["estilo"], "falta el estilo"
    Style.parse(fila["estilo"])


def test_el_generador_reproduce_los_archivos():
    ruta = RAIZ / "obtencion_datos" / "scripts" / "generar_arte.py"
    especificacion = importlib.util.spec_from_file_location("generar_arte", ruta)
    modulo = importlib.util.module_from_spec(especificacion)
    sys.modules["generar_arte"] = modulo
    especificacion.loader.exec_module(modulo)
    for nombre, generar in modulo.ARTES.items():
        esperado = "\n".join(linea.rstrip() for linea in generar()) + "\n"
        assert (DIRECTORIO_ARTE / f"{nombre}.txt").read_text(encoding="utf-8") == esperado, nombre
    assert {f"{nombre}.txt" for nombre in modulo.ARTES} == {f["archivo"] for f in ARTES}
