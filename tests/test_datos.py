"""Pruebas de los datos de la demo leyendo los CSV y `obtencion_datos/crudo/` (sin base de datos).

Son genéricas: se aplican a todos los datos de `datos/`, sean de The Beatles o de King Crimson.
"""

import csv
import json
import re
from collections import defaultdict
from datetime import date
from functools import cache
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos"
OBTENCION = RAIZ / "obtencion_datos"
PATRON_MBID = re.compile(r"musicbrainz\.org/release/([0-9a-f-]{36})")


@cache
def tabla(nombre: str) -> tuple[dict[str, str], ...]:
    ruta = DATOS / f"{nombre}.csv"
    if not ruta.is_file():
        return ()
    with ruta.open(encoding="utf-8", newline="") as archivo:
        return tuple(csv.DictReader(archivo))


@cache
def fuentes() -> tuple[dict[str, str], ...]:
    with (OBTENCION / "fuentes.csv").open(encoding="utf-8", newline="") as archivo:
        return tuple(csv.DictReader(archivo))


def mbid_de_album(album_id: str) -> str | None:
    for fila in fuentes():
        if fila["tabla"] == "album" and fila["id"] == album_id:
            coincidencia = PATRON_MBID.search(fila["url"])
            if coincidencia:
                return coincidencia.group(1)
    return None


@cache
def pistas_crudo(mbid: str) -> tuple[dict, list[tuple[int, int, str, int]]]:
    datos = json.loads((OBTENCION / "crudo" / f"{mbid}.json").read_text(encoding="utf-8"))
    pistas = []
    for medio in datos["media"]:
        for pista in medio["tracks"]:
            largo = pista.get("length") or (pista.get("recording") or {}).get("length")
            pistas.append(
                (medio["position"], pista["position"], pista["title"], (largo + 500) // 1000)
            )
    return datos, pistas


def albumes() -> list[dict[str, str]]:
    return list(tabla("album"))


hay_datos = pytest.mark.skipif(
    not tabla("album"), reason="Todavía no hay datos de la demo en datos/."
)


@hay_datos
@pytest.mark.parametrize("album", albumes(), ids=lambda a: a["titulo"])
def test_album_igual_a_su_edicion_de_referencia(album):
    mbid = mbid_de_album(album["album_id"])
    assert mbid, f"el álbum {album['titulo']} no tiene MBID en fuentes.csv"
    datos, pistas = pistas_crudo(mbid)
    assert album["titulo"] == datos["title"]
    assert album["fecha_lanzamiento"] == datos["date"]

    canciones = {c["cancion_id"]: c for c in tabla("cancion")}
    filas = sorted(
        (int(f["numero_disco"]), int(f["numero_pista"]), f["cancion_id"])
        for f in tabla("album_cancion")
        if f["album_id"] == album["album_id"]
    )
    assert [(d, n) for d, n, _ in filas] == [(d, n) for d, n, _, _ in pistas]
    for (disco, numero, cancion_id), (_, _, titulo, _) in zip(filas, pistas, strict=True):
        assert canciones[cancion_id]["titulo"] == titulo, f"pista {disco}.{numero}"


@hay_datos
def test_duracion_de_cada_cancion_es_la_de_su_primer_lanzamiento():
    fechas = {a["album_id"]: date.fromisoformat(a["fecha_lanzamiento"]) for a in albumes()}
    apariciones = defaultdict(list)
    for fila in tabla("album_cancion"):
        apariciones[fila["cancion_id"]].append(fila)
    for cancion in tabla("cancion"):
        primera = min(apariciones[cancion["cancion_id"]], key=lambda f: fechas[f["album_id"]])
        _, pistas = pistas_crudo(mbid_de_album(primera["album_id"]))
        duracion = next(
            d
            for disco, numero, _, d in pistas
            if (disco, numero) == (int(primera["numero_disco"]), int(primera["numero_pista"]))
        )
        assert int(cancion["duracion_seg"]) == duracion, cancion["titulo"]


@hay_datos
def test_toda_cancion_esta_en_algun_album():
    en_albumes = {f["cancion_id"] for f in tabla("album_cancion")}
    assert {c["cancion_id"] for c in tabla("cancion")} == en_albumes


@hay_datos
@pytest.mark.parametrize(
    ("nombre_tabla", "clave"),
    [
        ("persona", "persona_id"),
        ("artista", "artista_id"),
        ("membresia", "membresia_id"),
        ("album", "album_id"),
        ("cancion", "cancion_id"),
        ("sello", "sello_id"),
        ("genero", "genero_id"),
    ],
)
def test_cada_fila_tiene_fuente(nombre_tabla, clave):
    con_fuente = {f["id"] for f in fuentes() if f["tabla"] == nombre_tabla and f["url"]}
    sin_fuente = [f[clave] for f in tabla(nombre_tabla) if f[clave] not in con_fuente]
    assert not sin_fuente, f"{nombre_tabla} sin fuente: {sin_fuente}"


def test_fuentes_tiene_el_encabezado_esperado():
    with (OBTENCION / "fuentes.csv").open(encoding="utf-8", newline="") as archivo:
        assert next(csv.reader(archivo)) == ["tabla", "id", "url", "campos", "nota"]


@hay_datos
def test_cada_cancion_tiene_interprete_principal():
    con_principal = {c["cancion_id"] for c in tabla("credito_artista") if c["rol"] == "Principal"}
    sin = [c["titulo"] for c in tabla("cancion") if c["cancion_id"] not in con_principal]
    assert not sin


@hay_datos
def test_cada_cancion_tiene_compositor_o_arreglista_si_es_tradicional():
    roles = defaultdict(set)
    for credito in tabla("credito_persona"):
        roles[credito["cancion_id"]].add(credito["rol"])
    sin = [
        c["titulo"]
        for c in tabla("cancion")
        if not ({"Compositor", "Arreglista"} & roles[c["cancion_id"]])
    ]
    assert not sin


@hay_datos
def test_no_hay_membresias_solapadas():
    periodos = defaultdict(list)
    for m in tabla("membresia"):
        inicio = date.fromisoformat(m["fecha_inicio"]) if m["fecha_inicio"] else date.min
        fin = date.fromisoformat(m["fecha_fin"]) if m["fecha_fin"] else date.max
        assert inicio <= fin, m
        periodos[(m["persona_id"], m["artista_id"])].append((inicio, fin))
    for clave, lista in periodos.items():
        lista.sort()
        for (_, fin_anterior), (inicio, _) in zip(lista, lista[1:], strict=False):
            assert inicio > fin_anterior, f"membresías solapadas: {clave}"


@hay_datos
def test_tipos_de_lanzamiento_exigidos_y_featuring():
    tipos = {a["tipo"] for a in albumes()}
    assert {"LP", "Single", "EP", "Compilation"} <= tipos
    assert any(c["rol"] == "Featuring" for c in tabla("credito_artista"))


@hay_datos
def test_padres_de_genero_y_sello_antes_que_los_hijos():
    for nombre_tabla, clave, padre in [
        ("genero", "genero_id", "genero_padre_id"),
        ("sello", "sello_id", "sello_padre_id"),
    ]:
        vistos = set()
        for fila in tabla(nombre_tabla):
            if fila[padre]:
                assert fila[padre] in vistos, f"{nombre_tabla} {fila[clave]}"
            vistos.add(fila[clave])
