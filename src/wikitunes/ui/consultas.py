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
from wikitunes.ui.preguntas import Elegible
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


def elegibles_canciones(canciones: dict[int, str]) -> list[Elegible[Referencia]]:
    """Canciones por título; si dos se llaman igual (p. ej. versiones de single y de LP), se
    agrega su número para distinguirlas."""
    repetidos = Counter(canciones.values())
    return [
        Elegible(
            titulo + (f" #{cancion_id}" if repetidos[titulo] > 1 else ""),
            Referencia(cancion_id, titulo),
        )
        for cancion_id, titulo in sorted(canciones.items(), key=lambda c: (c[1], c[0]))
    ]


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


# --- Mostrar (encabezado + resultado) ------------------------------------------------------


def mostrar_tracklist(consola: Console, catalogo: Catalogo, album_id: int) -> Tracklist | None:
    tracklist = catalogo.tracklist(album_id)
    if tracklist is None:
        consola.print(sin_resultados("Ese álbum no existe en el catálogo."))
        return None
    mostrar_encabezado(consola, titulo_generado(tracklist.titulo, consola.width))
    consola.print(render_tracklist(tracklist))
    return tracklist


def _encabezado_de(consola: Console, catalogo: Catalogo, artista: Referencia) -> None:
    arte = catalogo.arte_de_artista(artista.id)
    mostrar_encabezado(consola, encabezado_artista(arte, artista.nombre, consola.width))


def mostrar_integrantes_en_fecha(
    consola: Console, catalogo: Catalogo, artista: Referencia, fecha: date
) -> list[Integrante]:
    """Primero el arte del artista; después los integrantes de esa fecha."""
    _encabezado_de(consola, catalogo, artista)
    integrantes = catalogo.integrantes_en_fecha(artista.nombre, fecha)
    consola.print(
        render_integrantes(
            integrantes,
            f"Integrantes de {artista.nombre} el {fecha_larga(fecha)}",
            f"{artista.nombre} no tenía integrantes el {fecha_larga(fecha)}.",
        )
    )
    return integrantes


def mostrar_historial(
    consola: Console, catalogo: Catalogo, artista: Referencia
) -> list[Integrante]:
    """Primero el arte del artista; después todos sus periodos de membresía."""
    _encabezado_de(consola, catalogo, artista)
    integrantes = catalogo.historial_integrantes(artista.nombre)
    consola.print(
        render_integrantes(
            integrantes,
            f"Historial de integrantes de {artista.nombre}",
            f"{artista.nombre} no tiene integrantes registrados.",
        )
    )
    return integrantes
