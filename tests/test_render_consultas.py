"""Pruebas del render de las consultas (sin base de datos)."""

from datetime import date, timedelta

from rich.console import Console

from wikitunes.modelos import Integrante, NodoGenero, Participacion, Pista, ResumenAlbum, Tracklist
from wikitunes.ui.consultas import (
    elegibles_albumes,
    elegibles_canciones,
    render_arbol_genero,
    render_canciones_de_persona,
    render_integrantes,
    render_tracklist,
)


def texto(renderizable) -> str:
    consola = Console(width=120, record=True, color_system=None)
    consola.print(renderizable)
    return consola.export_text()


def test_canciones_de_persona():
    salida = texto(
        render_canciones_de_persona(
            "Persona (ficticio)",
            [
                Participacion(1, "Canción A", "Banda (ficticio)", "Principal"),
                Participacion(2, "Canción B", "(crédito individual)", "Compositor"),
            ],
        )
    )
    assert "Canción A" in salida and "Intérprete principal" in salida
    assert "2 canciones" in salida


def test_canciones_de_persona_sin_resultados():
    assert "Sin resultados" in texto(render_canciones_de_persona("Nadie", []))


def test_arbol_de_genero():
    nodos = [
        NodoGenero(1, "Rock", 0, "Rock"),
        NodoGenero(2, "Hard rock", 1, "Rock > Hard rock"),
        NodoGenero(3, "Heavy metal", 2, "Rock > Hard rock > Heavy metal"),
        NodoGenero(4, "Pop rock", 1, "Rock > Pop rock"),
    ]
    salida = texto(render_arbol_genero(nodos))
    lineas = salida.splitlines()
    assert lineas[0].strip() == "Rock"
    # Heavy metal queda más indentado que Hard rock (es su hijo).
    hard = next(linea for linea in lineas if "Hard rock" in linea)
    heavy = next(linea for linea in lineas if "Heavy metal" in linea)
    assert heavy.index("Heavy") > hard.index("Hard")
    assert "3 subgéneros en 2 niveles" in salida


def test_tracklist_con_duracion_total_y_tipo_traducido():
    tracklist = Tracklist(
        album_id=1,
        titulo="Álbum (ficticio)",
        tipo="Compilation",
        cantidad_pistas=2,
        duracion_total=timedelta(seconds=4749),
        pistas=[
            Pista(1, 1, 10, "Uno", "Banda, feat. Invitado", "3:11"),
            Pista(1, 2, 11, "Dos", "Banda", "2:00"),
        ],
    )
    salida = texto(render_tracklist(tracklist))
    assert "feat. Invitado" in salida
    assert "Compilación · 2 pistas · duración total 1:19:09" in salida
    assert "Disco" not in salida  # un solo disco


def test_tracklist_con_dos_discos_muestra_la_columna():
    tracklist = Tracklist(
        1,
        "EP (ficticio)",
        "EP",
        2,
        timedelta(seconds=60),
        [
            Pista(1, 1, 1, "A", "X", "0:30"),
            Pista(2, 1, 2, "B", "X", "0:30"),
        ],
    )
    assert "Disco" in texto(render_tracklist(tracklist))


def test_integrantes_con_periodo_en_anios():
    salida = texto(
        render_integrantes(
            [Integrante(1, "Persona (ficticio)", "Bajo", date(1972, 7, 1), date(1974, 12, 31))],
            "Integrantes",
            "vacío",
        )
    )
    assert "1972–1974" in salida and "Bajo" in salida


def test_integrantes_vacio():
    assert "no tenía integrantes" in texto(
        render_integrantes([], "t", "Banda no tenía integrantes.")
    )


def test_elegibles_de_albumes_muestran_anio_y_tipo():
    elegibles = elegibles_albumes([ResumenAlbum(1, "Red", "LP", date(1974, 9, 27))])
    assert elegibles[0].texto == "Red (1974) · LP"


def test_canciones_con_el_mismo_titulo_se_distinguen_por_numero():
    elegibles = elegibles_canciones({7: "Get Back", 3: "Get Back", 5: "Red"})
    assert [e.texto for e in elegibles] == ["Get Back #3", "Get Back #7", "Red"]
    assert elegibles[0].valor.id == 3
