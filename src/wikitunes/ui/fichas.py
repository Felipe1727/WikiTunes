"""Render de las fichas de artista, persona, canción y género (sin interacción)."""

from rich.console import Group, RenderableType
from rich.table import Table
from rich.text import Text

from wikitunes.modelos import FichaArtista, FichaCancion, FichaGenero, FichaPersona
from wikitunes.ui.consultas import _tabla, render_arbol_genero, render_integrantes
from wikitunes.ui.textos import ROLES, TIPOS_ALBUM, TIPOS_ARTISTA, fecha_larga, traducir


def _datos(filas: list[tuple[str, str]]) -> Table:
    """Tabla de dos columnas «dato: valor», sin bordes."""
    tabla = Table.grid(padding=(0, 2))
    tabla.add_column(style="bold bright_magenta", justify="right")
    tabla.add_column()
    for etiqueta, valor in filas:
        tabla.add_row(etiqueta, valor)
    return tabla


def _lugar(ciudad: str | None, pais: str | None) -> str:
    return ", ".join(parte for parte in (ciudad, pais) if parte) or "—"


def render_ficha_artista(ficha: FichaArtista) -> RenderableType:
    if ficha.anio_formacion or ficha.anio_disolucion:
        activo = f"{ficha.anio_formacion or '?'}–{ficha.anio_disolucion or ''}"
    else:
        activo = "—"
    datos = _datos(
        [
            ("Tipo", traducir(ficha.tipo, TIPOS_ARTISTA)),
            ("Años", activo),
            ("Origen", _lugar(ficha.ciudad, ficha.pais)),
            ("Géneros", ", ".join(ficha.generos) or "—"),
        ]
    )
    partes: list[RenderableType] = [datos, Text()]
    if ficha.discografia:
        discos = _tabla("Discografía")
        discos.add_column("Año", justify="right")
        discos.add_column("Título", style="bold")
        discos.add_column("Tipo")
        for album in ficha.discografia:
            anio = str(album.fecha_lanzamiento.year) if album.fecha_lanzamiento else "—"
            discos.add_row(anio, album.titulo, traducir(album.tipo, TIPOS_ALBUM))
        partes += [discos, Text()]
    partes.append(
        render_integrantes(
            ficha.integrantes, "Integrantes", f"{ficha.nombre} no tiene integrantes registrados."
        )
    )
    return Group(*partes)


def render_ficha_persona(ficha: FichaPersona) -> RenderableType:
    nacimiento = fecha_larga(ficha.fecha_nacimiento) if ficha.fecha_nacimiento else "—"
    filas = [
        ("Nombre legal", ficha.nombre_legal),
        ("Nacimiento", f"{nacimiento} · {_lugar(ficha.ciudad, ficha.pais)}"),
    ]
    if ficha.fecha_fallecimiento:
        filas.append(("Fallecimiento", fecha_larga(ficha.fecha_fallecimiento)))
    partes: list[RenderableType] = [_datos(filas), Text()]
    if ficha.membresias:
        tabla = _tabla("Artistas de los que fue integrante")
        tabla.add_column("Artista", style="bold")
        tabla.add_column("Rol")
        tabla.add_column("Periodo", justify="center")
        for m in ficha.membresias:
            tabla.add_row(m.artista, m.rol or "—", m.periodo)
        partes.append(tabla)
    else:
        partes.append(Text("No fue integrante de ningún artista del catálogo.", style="italic"))
    return Group(*partes)


def render_ficha_cancion(ficha: FichaCancion) -> RenderableType:
    interpretes = ", ".join(
        i.artista + (" (feat.)" if i.rol == "Featuring" else "") for i in ficha.interpretes
    )
    datos = _datos(
        [
            ("Intérpretes", interpretes or "—"),
            ("Duración", ficha.duracion_texto),
            ("Géneros", ", ".join(ficha.generos) or "—"),
        ]
    )
    partes: list[RenderableType] = [datos, Text()]
    if ficha.creditos:
        creditos = _tabla("Créditos")
        creditos.add_column("Persona", style="bold")
        creditos.add_column("Rol")
        for c in ficha.creditos:
            creditos.add_row(c.persona, traducir(c.rol, ROLES))
        partes += [creditos, Text()]
    albumes = _tabla("Aparece en")
    albumes.add_column("Año", justify="right")
    albumes.add_column("Álbum", style="bold")
    albumes.add_column("Tipo")
    albumes.add_column("Pista", justify="right")
    for a in ficha.albumes:
        anio = str(a.fecha_lanzamiento.year) if a.fecha_lanzamiento else "—"
        pista = f"{a.disco}-{a.pista}" if a.disco > 1 else str(a.pista)
        albumes.add_row(anio, a.titulo, traducir(a.tipo, TIPOS_ALBUM), pista)
    partes.append(albumes)
    return Group(*partes)


def render_ficha_genero(ficha: FichaGenero) -> RenderableType:
    partes: list[RenderableType] = [render_arbol_genero(ficha.arbol), Text()]
    if ficha.artistas:
        artistas = _tabla("Artistas")
        artistas.add_column("Artista", style="bold")
        for a in ficha.artistas:
            artistas.add_row(a.nombre)
        partes += [artistas, Text()]
    if ficha.albumes:
        albumes = _tabla("Álbumes")
        albumes.add_column("Año", justify="right")
        albumes.add_column("Título", style="bold")
        albumes.add_column("Tipo")
        for a in ficha.albumes:
            anio = str(a.fecha_lanzamiento.year) if a.fecha_lanzamiento else "—"
            albumes.add_row(anio, a.titulo, traducir(a.tipo, TIPOS_ALBUM))
        partes.append(albumes)
    if not ficha.artistas and not ficha.albumes:
        partes.append(
            Text("Ningún artista ni álbum está clasificado en este género.", style="italic")
        )
    return Group(*partes)
