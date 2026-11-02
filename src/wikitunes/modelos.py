"""Modelos de datos (dataclasses) que devuelve la capa de consultas."""

from dataclasses import dataclass, field
from datetime import date, timedelta

from wikitunes.formato import formatear_duracion, formatear_periodo


@dataclass(frozen=True)
class Referencia:
    """Un elemento con id y nombre (para listas, autocompletado y navegación)."""

    id: int
    nombre: str


@dataclass(frozen=True)
class ResumenAlbum:
    id: int
    titulo: str
    tipo: str
    fecha_lanzamiento: date | None


@dataclass(frozen=True)
class Participacion:
    """Una fila de `sp_canciones_de_persona`, con el id de la canción para navegar."""

    cancion_id: int | None
    cancion: str
    via: str
    rol: str


@dataclass(frozen=True)
class NodoGenero:
    """Una fila de `sp_subgeneros`."""

    id: int
    nombre: str
    nivel: int
    ruta: str


@dataclass(frozen=True)
class Pista:
    """Una pista de `sp_tracklist`, con el id de la canción para navegar."""

    disco: int
    numero: int
    cancion_id: int | None
    cancion: str
    interpretes: str | None
    duracion: str | None


@dataclass(frozen=True)
class Tracklist:
    """Los dos resultados de `sp_tracklist`: las pistas y el resumen del álbum."""

    album_id: int
    titulo: str
    tipo: str
    cantidad_pistas: int
    duracion_total: timedelta | None
    pistas: list[Pista] = field(default_factory=list)

    @property
    def duracion_total_texto(self) -> str:
        return formatear_duracion(self.duracion_total)


@dataclass(frozen=True)
class Integrante:
    """Un periodo de membresía (de `sp_integrantes_en_fecha` o `sp_historial_integrantes`)."""

    persona_id: int | None
    persona: str
    rol: str | None
    fecha_inicio: date | None
    fecha_fin: date | None

    @property
    def periodo(self) -> str:
        return formatear_periodo(self.fecha_inicio, self.fecha_fin)


@dataclass(frozen=True)
class Arte:
    texto: str
    estilo: str | None


@dataclass(frozen=True)
class FichaArtista:
    id: int
    nombre: str
    tipo: str
    anio_formacion: int | None
    anio_disolucion: int | None
    ciudad: str | None
    pais: str | None
    generos: list[str]
    arte: Arte | None
    discografia: list[ResumenAlbum]
    integrantes: list[Integrante]


@dataclass(frozen=True)
class Membresia:
    artista_id: int
    artista: str
    rol: str | None
    fecha_inicio: date | None
    fecha_fin: date | None

    @property
    def periodo(self) -> str:
        return formatear_periodo(self.fecha_inicio, self.fecha_fin)


@dataclass(frozen=True)
class FichaPersona:
    id: int
    nombre: str
    nombre_legal: str
    fecha_nacimiento: date | None
    fecha_fallecimiento: date | None
    ciudad: str | None
    pais: str | None
    membresias: list[Membresia]


@dataclass(frozen=True)
class CreditoArtista:
    artista_id: int
    artista: str
    rol: str


@dataclass(frozen=True)
class CreditoPersona:
    persona_id: int
    persona: str
    rol: str


@dataclass(frozen=True)
class AparicionEnAlbum:
    album_id: int
    titulo: str
    tipo: str
    fecha_lanzamiento: date | None
    disco: int
    pista: int


@dataclass(frozen=True)
class FichaCancion:
    id: int
    titulo: str
    duracion_seg: int | None
    interpretes: list[CreditoArtista]
    creditos: list[CreditoPersona]
    generos: list[str]
    albumes: list[AparicionEnAlbum]

    @property
    def duracion_texto(self) -> str:
        return formatear_duracion(self.duracion_seg)


@dataclass(frozen=True)
class FichaGenero:
    """Un género, su árbol de subgéneros y lo que pertenece a él o a sus subgéneros."""

    nombre: str
    arbol: list[NodoGenero]
    artistas: list[Referencia]
    albumes: list[ResumenAlbum]
