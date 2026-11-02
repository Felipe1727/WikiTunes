"""Navegación entre resultados: pantallas, saltos y el menú «¿Y ahora?».

Cada pantalla se muestra y devuelve sus saltos (a qué otras pantallas se puede ir). `navegar`
mantiene una pila para poder volver y una línea de migas con el camino recorrido.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date

from rich.console import Console
from rich.text import Text

from wikitunes.catalogo import Catalogo
from wikitunes.modelos import Referencia
from wikitunes.ui import consultas, fichas
from wikitunes.ui.encabezados import encabezado_artista, mostrar_encabezado, titulo_generado
from wikitunes.ui.menu import Opcion
from wikitunes.ui.preguntas import Elegible, Preguntas
from wikitunes.ui.textos import fecha_larga

PREGUNTA_SIGUIENTE = "¿Y ahora?"
VOLVER = "volver"
MENU_PRINCIPAL = "menu"


@dataclass
class Contexto:
    consola: Console
    catalogo: Catalogo
    preguntas: Preguntas


@dataclass(frozen=True)
class Salto:
    """Una opción del menú «¿Y ahora?». `destino` devuelve la pantalla (o `None` si se cancela)."""

    texto: str
    destino: Callable[[Contexto], "Pantalla | None"]


def directo(texto: str, pantalla: "Pantalla") -> Salto:
    return Salto(texto, lambda _ctx: pantalla)


def eligiendo(texto: str, pregunta: str, elegibles: list[Elegible], crear) -> Salto:
    """Un salto que primero pide elegir un elemento (con autocompletado) entre `elegibles`."""

    def destino(ctx: Contexto):
        elegido = ctx.preguntas.elegir(pregunta, elegibles)
        return crear(elegido) if elegido is not None else None

    return Salto(texto, destino)


@dataclass(frozen=True)
class Pantalla:
    """Una pantalla navegable. Las subclases implementan `titulo` y `mostrar`."""

    @property
    def titulo(self) -> str:
        raise NotImplementedError

    def mostrar(self, ctx: Contexto) -> list[Salto]:
        raise NotImplementedError


def _sin_datos(ctx: Contexto, mensaje: str) -> list[Salto]:
    ctx.consola.print(consultas.sin_resultados(mensaje))
    return []


def _encabezado_pyfiglet(ctx: Contexto, texto: str) -> None:
    mostrar_encabezado(ctx.consola, titulo_generado(texto, ctx.consola.width))


@dataclass(frozen=True)
class PantallaArtista(Pantalla):
    artista_id: int
    nombre: str = ""

    @property
    def titulo(self) -> str:
        return self.nombre or "Artista"

    def mostrar(self, ctx: Contexto) -> list[Salto]:
        ficha = ctx.catalogo.ficha_artista(self.artista_id)
        if ficha is None:
            return _sin_datos(ctx, "Ese artista no existe en el catálogo.")
        mostrar_encabezado(
            ctx.consola, encabezado_artista(ficha.arte, ficha.nombre, ctx.consola.width)
        )
        ctx.consola.print(fichas.render_ficha_artista(ficha))
        artista = Referencia(ficha.id, ficha.nombre)
        saltos = [
            directo(f"Álbum: {a.titulo}", PantallaAlbum(a.id, a.titulo)) for a in ficha.discografia
        ]
        integrantes = {i.persona_id: i.persona for i in ficha.integrantes if i.persona_id}
        if len(integrantes) == 1:
            ((persona_id, nombre),) = integrantes.items()
            saltos.append(directo(f"Persona: {nombre}", PantallaPersona(persona_id, nombre)))
        elif integrantes:
            saltos.append(
                eligiendo(
                    "Ir a un integrante…",
                    "¿Qué integrante?",
                    [Elegible(n, Referencia(i, n)) for i, n in integrantes.items()],
                    lambda r: PantallaPersona(r.id, r.nombre),
                )
            )
            saltos.append(
                Salto(
                    "Integrantes en una fecha…",
                    lambda c: _pedir_integrantes(c, artista),
                )
            )
        return saltos


def _pedir_integrantes(ctx: Contexto, artista: Referencia) -> "PantallaIntegrantes | None":
    fecha = ctx.preguntas.pedir_fecha("¿En qué fecha?")
    return PantallaIntegrantes(artista, fecha) if fecha else None


@dataclass(frozen=True)
class PantallaPersona(Pantalla):
    persona_id: int
    nombre: str = ""

    @property
    def titulo(self) -> str:
        return self.nombre or "Persona"

    def mostrar(self, ctx: Contexto) -> list[Salto]:
        ficha = ctx.catalogo.ficha_persona(self.persona_id)
        if ficha is None:
            return _sin_datos(ctx, "Esa persona no existe en el catálogo.")
        _encabezado_pyfiglet(ctx, ficha.nombre)
        ctx.consola.print(fichas.render_ficha_persona(ficha))
        saltos = [
            directo("Sus canciones", PantallaCancionesPersona(Referencia(ficha.id, ficha.nombre)))
        ]
        vistos = set()
        for m in ficha.membresias:
            if m.artista_id not in vistos:
                vistos.add(m.artista_id)
                saltos.append(
                    directo(f"Artista: {m.artista}", PantallaArtista(m.artista_id, m.artista))
                )
        return saltos


@dataclass(frozen=True)
class PantallaCancion(Pantalla):
    cancion_id: int
    nombre: str = ""

    @property
    def titulo(self) -> str:
        return self.nombre or "Canción"

    def mostrar(self, ctx: Contexto) -> list[Salto]:
        ficha = ctx.catalogo.ficha_cancion(self.cancion_id)
        if ficha is None:
            return _sin_datos(ctx, "Esa canción no existe en el catálogo.")
        _encabezado_pyfiglet(ctx, ficha.titulo)
        ctx.consola.print(fichas.render_ficha_cancion(ficha))
        saltos = []
        for a in ficha.albumes:
            anio = f" ({a.fecha_lanzamiento.year})" if a.fecha_lanzamiento else ""
            saltos.append(directo(f"Álbum: {a.titulo}{anio}", PantallaAlbum(a.album_id, a.titulo)))
        for i in ficha.interpretes:
            saltos.append(
                directo(f"Artista: {i.artista}", PantallaArtista(i.artista_id, i.artista))
            )
        personas = {c.persona_id: c.persona for c in ficha.creditos}
        for persona_id, nombre in personas.items():
            saltos.append(directo(f"Persona: {nombre}", PantallaPersona(persona_id, nombre)))
        return saltos


@dataclass(frozen=True)
class PantallaAlbum(Pantalla):
    """El tracklist de un álbum."""

    album_id: int
    nombre: str = ""

    @property
    def titulo(self) -> str:
        return self.nombre or "Álbum"

    def mostrar(self, ctx: Contexto) -> list[Salto]:
        tracklist = consultas.mostrar_tracklist(ctx.consola, ctx.catalogo, self.album_id)
        if tracklist is None:
            return []
        saltos = [
            eligiendo(
                "Ir a una canción…",
                "¿Qué canción?",
                [
                    Elegible(f"{p.numero}. {p.cancion}", Referencia(p.cancion_id, p.cancion))
                    for p in tracklist.pistas
                    if p.cancion_id
                ],
                lambda r: PantallaCancion(r.id, r.nombre),
            )
        ]
        for artista in ctx.catalogo.artistas_de_album(self.album_id):
            saltos.append(
                directo(f"Artista: {artista.nombre}", PantallaArtista(artista.id, artista.nombre))
            )
        return saltos


@dataclass(frozen=True)
class PantallaGenero(Pantalla):
    """Ficha de un género: su árbol y los artistas y álbumes del género o sus subgéneros."""

    nombre: str

    @property
    def titulo(self) -> str:
        return self.nombre

    def mostrar(self, ctx: Contexto) -> list[Salto]:
        ficha = ctx.catalogo.ficha_genero(self.nombre)
        if ficha is None:
            return _sin_datos(ctx, "Ese género no existe en el catálogo.")
        _encabezado_pyfiglet(ctx, ficha.nombre)
        ctx.consola.print(fichas.render_ficha_genero(ficha))
        saltos = []
        if len(ficha.arbol) > 1:
            saltos.append(
                eligiendo(
                    "Ir a un subgénero…",
                    "¿Qué subgénero?",
                    [Elegible(n.nombre, n.nombre) for n in ficha.arbol[1:]],
                    PantallaGenero,
                )
            )
        if ficha.artistas:
            saltos.append(
                eligiendo(
                    "Ir a un artista…",
                    "¿Qué artista?",
                    consultas.elegibles_de(ficha.artistas),
                    lambda r: PantallaArtista(r.id, r.nombre),
                )
            )
        if ficha.albumes:
            saltos.append(
                eligiendo(
                    "Ir a un álbum…",
                    "¿Qué álbum?",
                    consultas.elegibles_albumes(ficha.albumes),
                    lambda a: PantallaAlbum(a.id, a.titulo),
                )
            )
        return saltos


@dataclass(frozen=True)
class PantallaArbolGenero(Pantalla):
    """El árbol de un género (`sp_subgeneros`)."""

    nombre: str

    @property
    def titulo(self) -> str:
        return f"Árbol de {self.nombre}"

    def mostrar(self, ctx: Contexto) -> list[Salto]:
        _encabezado_pyfiglet(ctx, self.nombre)
        nodos = ctx.catalogo.subgeneros(self.nombre)
        ctx.consola.print(consultas.render_arbol_genero(nodos))
        if not nodos:
            return []
        return [
            eligiendo(
                "Ver artistas y álbumes de un género del árbol…",
                "¿Qué género?",
                [Elegible(n.nombre, n.nombre) for n in nodos],
                PantallaGenero,
            )
        ]


@dataclass(frozen=True)
class PantallaCancionesPersona(Pantalla):
    persona: Referencia

    @property
    def titulo(self) -> str:
        return f"Canciones de {self.persona.nombre}"

    def mostrar(self, ctx: Contexto) -> list[Salto]:
        _encabezado_pyfiglet(ctx, self.persona.nombre)
        participaciones = ctx.catalogo.canciones_de_persona(self.persona)
        ctx.consola.print(
            consultas.render_canciones_de_persona(self.persona.nombre, participaciones)
        )
        saltos = [
            directo(
                f"Ficha de {self.persona.nombre}",
                PantallaPersona(self.persona.id, self.persona.nombre),
            )
        ]
        canciones = {p.cancion_id: p.cancion for p in participaciones if p.cancion_id}
        if canciones:
            saltos.append(
                eligiendo(
                    "Ir a una canción…",
                    "¿Qué canción?",
                    consultas.elegibles_canciones(canciones),
                    lambda r: PantallaCancion(r.id, r.nombre),
                )
            )
        return saltos


def _saltos_integrantes(ctx: Contexto, artista: Referencia, integrantes) -> list[Salto]:
    saltos = [directo(f"Ficha de {artista.nombre}", PantallaArtista(artista.id, artista.nombre))]
    personas = {i.persona_id: i.persona for i in integrantes if i.persona_id}
    if 0 < len(personas) <= 8:
        saltos += [directo(f"Persona: {n}", PantallaPersona(i, n)) for i, n in personas.items()]
    elif personas:
        saltos.append(
            eligiendo(
                "Ir a un integrante…",
                "¿Qué integrante?",
                [Elegible(n, Referencia(i, n)) for i, n in personas.items()],
                lambda r: PantallaPersona(r.id, r.nombre),
            )
        )
    return saltos


@dataclass(frozen=True)
class PantallaIntegrantes(Pantalla):
    artista: Referencia
    fecha: date

    @property
    def titulo(self) -> str:
        return f"{self.artista.nombre} el {fecha_larga(self.fecha)}"

    def mostrar(self, ctx: Contexto) -> list[Salto]:
        integrantes = consultas.mostrar_integrantes_en_fecha(
            ctx.consola, ctx.catalogo, self.artista, self.fecha
        )
        saltos = [Salto("Cambiar la fecha…", lambda c: _pedir_integrantes(c, self.artista))]
        return saltos + _saltos_integrantes(ctx, self.artista, integrantes)


@dataclass(frozen=True)
class PantallaHistorial(Pantalla):
    artista: Referencia

    @property
    def titulo(self) -> str:
        return f"Historial de {self.artista.nombre}"

    def mostrar(self, ctx: Contexto) -> list[Salto]:
        integrantes = consultas.mostrar_historial(ctx.consola, ctx.catalogo, self.artista)
        return _saltos_integrantes(ctx, self.artista, integrantes)


@dataclass
class Navegador:
    """Recorre pantallas con una pila: «¿Y ahora?» ofrece saltos, «Volver» y «Menú principal»."""

    ctx: Contexto
    pila: list[Pantalla] = field(default_factory=list)

    def migas(self) -> Text:
        return Text("Menú › " + " › ".join(p.titulo for p in self.pila), style="dim italic")

    def navegar(self, inicial: Pantalla) -> None:
        self.pila = [inicial]
        mostrar = True
        saltos: list[Salto] = []
        while self.pila:
            if mostrar:
                self.ctx.consola.print()
                self.ctx.consola.print(self.migas())
                saltos = self.pila[-1].mostrar(self.ctx)
            opciones = [Opcion(str(i), s.texto) for i, s in enumerate(saltos)]
            if len(self.pila) > 1:
                opciones.append(Opcion(VOLVER, f"Volver a {self.pila[-2].titulo}"))
            opciones.append(Opcion(MENU_PRINCIPAL, "Menú principal"))
            self.ctx.consola.print()
            eleccion = self.ctx.preguntas.elegir_opcion(PREGUNTA_SIGUIENTE, opciones)
            if eleccion in (None, MENU_PRINCIPAL):
                return
            if eleccion == VOLVER:
                self.pila.pop()
                mostrar = True
                continue
            destino = saltos[int(eleccion)].destino(self.ctx)
            if destino is None:
                mostrar = False  # se canceló la elección: se repite «¿Y ahora?»
                continue
            self.pila.append(destino)
            mostrar = True
