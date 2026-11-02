"""Acciones del menú principal: piden lo necesario y arrancan la navegación."""

from wikitunes.ui.consultas import elegibles_albumes, elegibles_canciones, elegibles_de
from wikitunes.ui.navegacion import (
    Contexto,
    Navegador,
    Pantalla,
    PantallaAlbum,
    PantallaArbolGenero,
    PantallaArtista,
    PantallaCancion,
    PantallaCancionesPersona,
    PantallaHistorial,
    PantallaIntegrantes,
    PantallaPersona,
)


def _navegar(ctx: Contexto, pantalla: Pantalla | None) -> None:
    if pantalla is not None:
        Navegador(ctx).navegar(pantalla)


def canciones_de_persona(ctx: Contexto) -> None:
    persona = ctx.preguntas.elegir("¿De qué persona?", elegibles_de(ctx.catalogo.personas()))
    _navegar(ctx, persona and PantallaCancionesPersona(persona))


def arbol_de_genero(ctx: Contexto) -> None:
    genero = ctx.preguntas.elegir("¿Qué género?", elegibles_de(ctx.catalogo.generos()))
    _navegar(ctx, genero and PantallaArbolGenero(genero.nombre))


def tracklist_de_album(ctx: Contexto) -> None:
    album = ctx.preguntas.elegir("¿Qué álbum?", elegibles_albumes(ctx.catalogo.albumes()))
    _navegar(ctx, album and PantallaAlbum(album.id, album.titulo))


def integrantes_en_fecha(ctx: Contexto) -> None:
    artista = ctx.preguntas.elegir("¿De qué artista?", elegibles_de(ctx.catalogo.artistas()))
    if artista is None:
        return
    fecha = ctx.preguntas.pedir_fecha("¿En qué fecha?")
    _navegar(ctx, fecha and PantallaIntegrantes(artista, fecha))


def historial_de_integrantes(ctx: Contexto) -> None:
    artista = ctx.preguntas.elegir("¿De qué artista?", elegibles_de(ctx.catalogo.artistas()))
    _navegar(ctx, artista and PantallaHistorial(artista))


def ficha_de_artista(ctx: Contexto) -> None:
    artista = ctx.preguntas.elegir("¿Qué artista?", elegibles_de(ctx.catalogo.artistas()))
    _navegar(ctx, artista and PantallaArtista(artista.id, artista.nombre))


def ficha_de_persona(ctx: Contexto) -> None:
    persona = ctx.preguntas.elegir("¿Qué persona?", elegibles_de(ctx.catalogo.personas()))
    _navegar(ctx, persona and PantallaPersona(persona.id, persona.nombre))


def ficha_de_cancion(ctx: Contexto) -> None:
    canciones = {c.id: c.nombre for c in ctx.catalogo.canciones()}
    cancion = ctx.preguntas.elegir("¿Qué canción?", elegibles_canciones(canciones))
    _navegar(ctx, cancion and PantallaCancion(cancion.id, cancion.nombre))


ACCIONES = {
    "canciones_persona": canciones_de_persona,
    "arbol_generos": arbol_de_genero,
    "tracklist": tracklist_de_album,
    "integrantes_fecha": integrantes_en_fecha,
    "historial": historial_de_integrantes,
    "ficha_artista": ficha_de_artista,
    "ficha_persona": ficha_de_persona,
    "ficha_cancion": ficha_de_cancion,
}
