"""Pruebas unitarias del cargador (no necesitan base de datos)."""

from pathlib import Path

import pytest

from wikitunes.cargador import (
    ORDEN_TABLAS,
    ErrorDeCarga,
    TablaCsv,
    leer_arte,
    leer_csv,
    leer_directorio,
    validar_columnas,
)

DATOS_EJEMPLO = Path(__file__).parent / "datos_ejemplo"


def escribir(ruta: Path, contenido: str) -> Path:
    ruta.write_text(contenido, encoding="utf-8", newline="")
    return ruta


def test_celdas_vacias_son_none(tmp_path):
    tabla = leer_csv(escribir(tmp_path / "t.csv", "a,b,c\n1,,x\n"))
    assert tabla.filas[0].valores == {"a": "1", "b": None, "c": "x"}


def test_comas_comillas_y_saltos_de_linea(tmp_path):
    tabla = leer_csv(
        escribir(tmp_path / "t.csv", 'id,texto\n1,"uno, dos ""tres""\ncuatro"\n2,simple\n')
    )
    assert tabla.filas[0].valores["texto"] == 'uno, dos "tres"\ncuatro'
    # La línea es la última línea física del registro.
    assert [fila.linea for fila in tabla.filas] == [3, 4]


def test_cantidad_de_celdas_distinta(tmp_path):
    with pytest.raises(ErrorDeCarga, match=r"t\.csv, línea 2"):
        leer_csv(escribir(tmp_path / "t.csv", "a,b\n1,2,3\n"))


def test_csv_sin_encabezado(tmp_path):
    with pytest.raises(ErrorDeCarga, match="vacío"):
        leer_csv(escribir(tmp_path / "t.csv", ""))


def test_columna_desconocida():
    tabla = TablaCsv(ruta=Path("pais.csv"), columnas=["pais_id", "inventada"])
    with pytest.raises(ErrorDeCarga, match="pais.csv.*inventada"):
        validar_columnas(tabla, "pais", {"pais_id", "nombre", "codigo_iso2"})


def test_arte_con_barras_y_unicode_sin_salto_final():
    arte = leer_arte(DATOS_EJEMPLO / "arte", "ficticio.txt")
    assert arte == ' ╔═╗ \\ barra \\n literal "comillas"\n  ▀▀▀ espacios finales   '


def test_arte_fuera_del_directorio(tmp_path):
    (tmp_path / "arte").mkdir()
    escribir(tmp_path / "secreto.txt", "no")
    with pytest.raises(ErrorDeCarga, match="fuera de arte/"):
        leer_arte(tmp_path / "arte", "../secreto.txt")


def test_arte_inexistente(tmp_path):
    (tmp_path / "arte").mkdir()
    with pytest.raises(ErrorDeCarga, match="no existe"):
        leer_arte(tmp_path / "arte", "falta.txt")


def test_leer_directorio_respeta_el_orden_de_carga():
    tablas = leer_directorio(DATOS_EJEMPLO)
    assert list(tablas) == [tabla for tabla in ORDEN_TABLAS if tabla in tablas]
    assert tablas["arte_artista"].columnas == ["artista_id", "arte", "estilo"]


def test_directorio_vacio(tmp_path):
    assert leer_directorio(tmp_path) == {}
