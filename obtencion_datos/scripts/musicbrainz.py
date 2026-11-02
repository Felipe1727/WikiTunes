"""Descarga lanzamientos de MusicBrainz y muestra un borrador de su tracklist.

Uso:
    uv run python obtencion_datos/scripts/musicbrainz.py <mbid> [<mbid> ...] [--refrescar]

Cada respuesta se guarda en `obtencion_datos/crudo/<mbid>.json` y se reutiliza en ejecuciones
posteriores, así los datos se pueden reproducir sin red. Solo usa la biblioteca estándar.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

DIRECTORIO_CRUDO = Path(__file__).resolve().parent.parent / "crudo"
URL_API = "https://musicbrainz.org/ws/2/release/{mbid}?inc={inc}&fmt=json"
INCLUSIONES = "recordings+artist-credits+labels+release-groups"
USER_AGENT = "WikiTunes/0.1 (https://github.com/Felipe1727/WikiTunes)"
SEGUNDOS_ENTRE_PETICIONES = 1.0

_ultima_peticion = 0.0


@dataclass(frozen=True)
class Pista:
    disco: int
    numero: int
    titulo: str
    duracion_seg: int | None
    mbid_grabacion: str


@dataclass(frozen=True)
class Lanzamiento:
    mbid: str
    titulo: str
    fecha: str | None
    pais: str | None
    sellos: tuple[str, ...]
    tipo: str | None
    tipos_secundarios: tuple[str, ...]
    credito_artista: str
    pistas: tuple[Pista, ...]


def ms_a_segundos(milisegundos: int | None) -> int | None:
    """Convierte milisegundos a segundos, redondeando al más cercano (0,5 hacia arriba)."""
    if milisegundos is None:
        return None
    return int((milisegundos + 500) // 1000)


def credito_como_texto(creditos: list[dict]) -> str:
    """Une un `artist-credit` de MusicBrainz tal como aparece en el lanzamiento."""
    return "".join(credito["name"] + credito.get("joinphrase", "") for credito in creditos)


def extraer_lanzamiento(datos: dict) -> Lanzamiento:
    """Transforma la respuesta JSON de MusicBrainz en un `Lanzamiento` (función pura)."""
    grupo = datos.get("release-group") or {}
    pistas = []
    for medio in datos.get("media", []):
        for pista in medio.get("tracks", []):
            duracion = pista.get("length")
            if duracion is None:
                duracion = (pista.get("recording") or {}).get("length")
            pistas.append(
                Pista(
                    disco=medio.get("position", 1),
                    numero=pista["position"],
                    titulo=pista["title"],
                    duracion_seg=ms_a_segundos(duracion),
                    mbid_grabacion=(pista.get("recording") or {}).get("id", ""),
                )
            )
    sellos = tuple(
        info["label"]["name"] for info in datos.get("label-info", []) if info.get("label")
    )
    return Lanzamiento(
        mbid=datos["id"],
        titulo=datos["title"],
        fecha=datos.get("date"),
        pais=datos.get("country"),
        sellos=sellos,
        tipo=grupo.get("primary-type"),
        tipos_secundarios=tuple(grupo.get("secondary-types", [])),
        credito_artista=credito_como_texto(datos.get("artist-credit", [])),
        pistas=tuple(pistas),
    )


def _esperar_turno() -> None:
    global _ultima_peticion
    espera = SEGUNDOS_ENTRE_PETICIONES - (time.monotonic() - _ultima_peticion)
    if espera > 0:
        time.sleep(espera)
    _ultima_peticion = time.monotonic()


def obtener_json(
    mbid: str, *, refrescar: bool = False, directorio: Path = DIRECTORIO_CRUDO
) -> dict:
    """Devuelve el JSON del lanzamiento, desde `crudo/` o descargándolo (y guardándolo)."""
    ruta = directorio / f"{mbid}.json"
    if ruta.is_file() and not refrescar:
        return json.loads(ruta.read_text(encoding="utf-8"))
    _esperar_turno()
    peticion = urllib.request.Request(
        URL_API.format(mbid=mbid, inc=INCLUSIONES),
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urllib.request.urlopen(peticion, timeout=30) as respuesta:
        datos = json.load(respuesta)
    directorio.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return datos


def formatear_borrador(lanzamiento: Lanzamiento) -> str:
    lineas = [
        f"{lanzamiento.titulo} — {lanzamiento.credito_artista}",
        f"  MBID: {lanzamiento.mbid}",
        f"  Fecha: {lanzamiento.fecha or '?'}  País: {lanzamiento.pais or '?'}",
        f"  Sello: {', '.join(lanzamiento.sellos) or '?'}",
        "  Tipo: "
        + (" + ".join(filter(None, [lanzamiento.tipo, *lanzamiento.tipos_secundarios])) or "?"),
        "  disco,pista,titulo,duracion_seg,mbid_grabacion",
    ]
    total = 0
    for pista in lanzamiento.pistas:
        total += pista.duracion_seg or 0
        titulo = '"' + pista.titulo.replace('"', '""') + '"'
        duracion = "" if pista.duracion_seg is None else str(pista.duracion_seg)
        lineas.append(f"  {pista.disco},{pista.numero},{titulo},{duracion},{pista.mbid_grabacion}")
    lineas.append(f"  Pistas: {len(lanzamiento.pistas)}  Duración total: {total} s")
    return "\n".join(lineas)


def principal(argumentos: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(
        description="Descarga lanzamientos de MusicBrainz y muestra un borrador del tracklist."
    )
    analizador.add_argument("mbids", nargs="+", help="MBID de cada lanzamiento (release)")
    analizador.add_argument(
        "--refrescar", action="store_true", help="volver a descargar aunque exista en crudo/"
    )
    opciones = analizador.parse_args(argumentos)
    codigo = 0
    for mbid in opciones.mbids:
        try:
            datos = obtener_json(mbid, refrescar=opciones.refrescar)
        except (urllib.error.URLError, TimeoutError) as error:
            print(f"No se pudo obtener {mbid} de MusicBrainz: {error}", file=sys.stderr)
            codigo = 1
            continue
        print(formatear_borrador(extraer_lanzamiento(datos)))
        print()
    return codigo


if __name__ == "__main__":
    sys.exit(principal())
