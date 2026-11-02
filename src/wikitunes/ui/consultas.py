"""Las cinco consultas del menú principal.

Cada consulta tiene una función de render, que convierte los datos en tablas o árboles de Rich
(sin interacción, fácil de probar), y una acción, que pregunta, consulta y muestra.
"""

from collections import Counter
from datetime import date

from rich import box
from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from wikitunes.catalogo import Catalogo
from wikitunes.modelos import (
    Integrante,
    NodoGenero,
    Participacion,
    Referencia,
    ResumenAlbum,
    Tracklist,
)
from wikitunes.ui.encabezados import encabezado_artista, mostrar_encabezado, titulo_generado
from wikitunes.ui.preguntas import Elegible, Preguntas
from wikitunes.ui.textos import ROLES, TIPOS_ALBUM, fecha_larga, traducir

ESTILO_TABLA = "bright_magenta"


def sin_resultados(mensaje: str) -> Panel:
    return Panel(
        Text(mensaje, style="italic"), title="Sin resultados", border_style="yellow", expand=False
    )


def _tabla(titulo: str | None = None) -> Table:
    return Table(
        title=titulo,
        box=box.ROUNDED,
        header_style=f"bold {ESTILO_TABLA}",
        border_style=ESTILO_TABLA,
        title_style="bold",
        expand=False,
    )


# --- Elegibles -----------------------------------------------------------------------------


def elegibles_de(referencias: list[Referencia]) -> list[Elegible[Referencia]]:
    return [Elegible(r.nombre, r) for r in referencias]


def texto_album(album: ResumenAlbum) -> str:
    anio = f" ({album.fecha_lanzamiento.year})" if album.fecha_lanzamiento else ""
    return f"{album.titulo}{anio} · {traducir(album.tipo, TIPOS_ALBUM)}"


def elegibles_albumes(albumes: list[ResumenAlbum]) -> list[Elegible[ResumenAlbum]]:
    textos = Counter(texto_album(a) for a in albumes)
    return [
        Elegible(texto_album(a) + (f" #{a.id}" if textos[texto_album(a)] > 1 else ""), a)
        for a in albumes
    ]


# --- Render --------------------------------------------------------------------------------


def render_canciones_de_persona(
    persona: str, participaciones: list[Participacion]
) -> RenderableType:
    if not participaciones:
        return sin_resultados(f"No hay canciones registradas para {persona}.")
    tabla = _tabla()
    tabla.add_column("Canción", style="bold")
    tabla.add_column("Vía")
    tabla.add_column("Rol")
    for p in sorted(
        participaciones, key=lambda p: (p.via == "(crédito individual)", p.via, p.cancion)
    ):
        tabla.add_row(p.cancion, p.via, traducir(p.rol, ROLES))
    canciones = len({p.cancion_id or p.cancion for p in participaciones})
    vias = sorted({p.via for p in participaciones})
    resumen = Text(f"{canciones} canciones · vías: {', '.join(vias)}", style="dim")
    return Group(tabla, resumen)


def render_arbol_genero(nodos: list[NodoGenero]) -> RenderableType:
    if not nodos:
        return sin_resultados("Ese género no existe en el catálogo.")
    raiz = Tree(Text(nodos[0].nombre, style=f"bold {ESTILO_TABLA}"), guide_style=ESTILO_TABLA)
    ramas = {nodos[0].ruta: raiz}
    for nodo in nodos[1:]:
        padre = nodo.ruta.rsplit(" > ", 1)[0]
        ramas[nodo.ruta] = ramas[padre].add(
            Text(nodo.nombre, style="bold" if nodo.nivel == 1 else "")
        )
    total = len(nodos) - 1
    return Group(
        raiz, Text(f"{total} subgéneros en {max(n.nivel for n in nodos)} niveles", style="dim")
    )


def render_tracklist(tracklist: Tracklist) -> RenderableType:
    if not tracklist.pistas:
        return sin_resultados(f"{tracklist.titulo} no tiene pistas registradas.")
    varios_discos = len({p.disco for p in tracklist.pistas}) > 1
    tabla = _tabla()
    if varios_discos:
        tabla.add_column("Disco", justify="right")
    tabla.add_column("#", justify="right")
    tabla.add_column("Canción", style="bold")
    tabla.add_column("Intérpretes")
    tabla.add_column("Duración", justify="right")
    for pista in tracklist.pistas:
        fila = [str(pista.numero), pista.cancion, pista.interpretes or "—", pista.duracion or "—"]
        tabla.add_row(*([str(pista.disco)] if varios_discos else []), *fila)
    resumen = Text(
        f"{traducir(tracklist.tipo, TIPOS_ALBUM)} · {tracklist.cantidad_pistas} pistas · "
        f"duración total {tracklist.duracion_total_texto}",
        style="dim",
    )
    return Group(tabla, resumen)


def render_integrantes(integrantes: list[Integrante], titulo: str, vacio: str) -> RenderableType:
    if not integrantes:
        return sin_resultados(vacio)
    tabla = _tabla(titulo)
    tabla.add_column("Integrante", style="bold")
    tabla.add_column("Rol")
    tabla.add_column("Periodo", justify="center")
    for i in integrantes:
        tabla.add_row(i.persona, i.rol or "—", i.periodo)
    return tabla


# --- Acciones ------------------------------------------------------------------------------


def _ancho(consola: Console) -> int:
    return consola.width


def canciones_de_persona(
    consola: Console, catalogo: Catalogo, preguntas: Preguntas
) -> Referencia | None:
    persona = preguntas.elegir("¿De qué persona?", elegibles_de(catalogo.personas()))
    if persona is None:
        return None
    mostrar_encabezado(consola, titulo_generado(persona.nombre, _ancho(consola)))
    consola.print(
        render_canciones_de_persona(persona.nombre, catalogo.canciones_de_persona(persona))
    )
    return persona


def arbol_de_genero(
    consola: Console, catalogo: Catalogo, preguntas: Preguntas
) -> Referencia | None:
    genero = preguntas.elegir("¿Qué género?", elegibles_de(catalogo.generos()))
    if genero is None:
        return None
    mostrar_encabezado(consola, titulo_generado(genero.nombre, _ancho(consola)))
    consola.print(render_arbol_genero(catalogo.subgeneros(genero.nombre)))
    return genero


def tracklist_de_album(
    consola: Console, catalogo: Catalogo, preguntas: Preguntas
) -> ResumenAlbum | None:
    album = preguntas.elegir("¿Qué álbum?", elegibles_albumes(catalogo.albumes()))
    if album is None:
        return None
    mostrar_tracklist(consola, catalogo, album.id)
    return album


def mostrar_tracklist(consola: Console, catalogo: Catalogo, album_id: int) -> Tracklist | None:
    tracklist = catalogo.tracklist(album_id)
    if tracklist is None:
        consola.print(sin_resultados("Ese álbum no existe en el catálogo."))
        return None
    mostrar_encabezado(consola, titulo_generado(tracklist.titulo, _ancho(consola)))
    consola.print(render_tracklist(tracklist))
    return tracklist


def _encabezado_de(consola: Console, catalogo: Catalogo, artista: Referencia) -> None:
    arte = catalogo.arte_de_artista(artista.id)
    mostrar_encabezado(consola, encabezado_artista(arte, artista.nombre, _ancho(consola)))


def integrantes_en_fecha(
    consola: Console, catalogo: Catalogo, preguntas: Preguntas, fecha: date | None = None
) -> Referencia | None:
    artista = preguntas.elegir("¿De qué artista?", elegibles_de(catalogo.artistas()))
    if artista is None:
        return None
    fecha = fecha or preguntas.pedir_fecha("¿En qué fecha?")
    if fecha is None:
        return None
    _encabezado_de(consola, catalogo, artista)
    consola.print(
        render_integrantes(
            catalogo.integrantes_en_fecha(artista.nombre, fecha),
            f"Integrantes de {artista.nombre} el {fecha_larga(fecha)}",
            f"{artista.nombre} no tenía integrantes el {fecha_larga(fecha)}.",
        )
    )
    return artista


def historial_de_integrantes(
    consola: Console, catalogo: Catalogo, preguntas: Preguntas
) -> Referencia | None:
    artista = preguntas.elegir("¿De qué artista?", elegibles_de(catalogo.artistas()))
    if artista is None:
        return None
    _encabezado_de(consola, catalogo, artista)
    consola.print(
        render_integrantes(
            catalogo.historial_integrantes(artista.nombre),
            f"Historial de integrantes de {artista.nombre}",
            f"{artista.nombre} no tiene integrantes registrados.",
        )
    )
    return artista
