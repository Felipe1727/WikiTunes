"""Pruebas unitarias del script de MusicBrainz con un JSON FICTICIO mínimo (sin red)."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

RUTA_SCRIPT = Path(__file__).parent.parent / "obtencion_datos" / "scripts" / "musicbrainz.py"


@pytest.fixture(scope="module")
def musicbrainz():
    especificacion = importlib.util.spec_from_file_location("musicbrainz", RUTA_SCRIPT)
    modulo = importlib.util.module_from_spec(especificacion)
    sys.modules["musicbrainz"] = modulo
    especificacion.loader.exec_module(modulo)
    return modulo


JSON_FICTICIO = {
    "id": "00000000-0000-0000-0000-000000000001",
    "title": "Álbum ficticio",
    "date": "1969-09-26",
    "country": "GB",
    "label-info": [{"label": {"name": "Sello ficticio"}}],
    "release-group": {"primary-type": "Album", "secondary-types": ["Compilation"]},
    "artist-credit": [
        {"name": "Banda ficticia", "joinphrase": " with "},
        {"name": "Invitado ficticio"},
    ],
    "media": [
        {
            "position": 1,
            "tracks": [
                {"position": 1, "title": 'Uno "A"', "length": 185600, "recording": {"id": "r1"}},
                {
                    "position": 2,
                    "title": "Dos",
                    "length": None,
                    "recording": {"id": "r2", "length": 1499},
                },
            ],
        },
        {
            "position": 2,
            "tracks": [{"position": 1, "title": "Tres", "recording": {"id": "r3"}}],
        },
    ],
}


@pytest.mark.parametrize(
    ("milisegundos", "segundos"),
    [(185600, 186), (185499, 185), (185500, 186), (None, None)],
)
def test_ms_a_segundos(musicbrainz, milisegundos, segundos):
    assert musicbrainz.ms_a_segundos(milisegundos) == segundos


def test_extraer_lanzamiento(musicbrainz):
    lanzamiento = musicbrainz.extraer_lanzamiento(JSON_FICTICIO)
    assert lanzamiento.titulo == "Álbum ficticio"
    assert lanzamiento.credito_artista == "Banda ficticia with Invitado ficticio"
    assert lanzamiento.sellos == ("Sello ficticio",)
    assert lanzamiento.tipo == "Album"
    assert lanzamiento.tipos_secundarios == ("Compilation",)
    assert [(p.disco, p.numero, p.titulo, p.duracion_seg) for p in lanzamiento.pistas] == [
        (1, 1, 'Uno "A"', 186),
        (1, 2, "Dos", 1),
        (2, 1, "Tres", None),
    ]


def test_usa_crudo_sin_red(musicbrainz, tmp_path, monkeypatch):
    (tmp_path / "abc.json").write_text(json.dumps(JSON_FICTICIO), encoding="utf-8")

    def sin_red(*_args, **_kwargs):
        raise AssertionError("no debe conectarse a la red")

    monkeypatch.setattr(musicbrainz.urllib.request, "urlopen", sin_red)
    assert musicbrainz.obtener_json("abc", directorio=tmp_path) == JSON_FICTICIO


def test_borrador_csv(musicbrainz):
    borrador = musicbrainz.formatear_borrador(musicbrainz.extraer_lanzamiento(JSON_FICTICIO))
    assert '  1,1,"Uno ""A""",186,r1' in borrador
    assert "Tipo: Album + Compilation" in borrador
    assert "Pistas: 3  Duración total: 187 s" in borrador
