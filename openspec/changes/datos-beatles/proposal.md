# Propuesta: datos-beatles

## Por qué

La aplicación necesita un catálogo real y verificable para lucirse. El primer caso de la demo es The Beatles con los proyectos en solitario de sus integrantes: muestra la tabla `membresia` (con Pete Best y Stuart Sutcliffe), las relaciones persona ↔ artista y los créditos individuales.

## Qué cambia

- **Catálogos en `datos/`:** países, ciudades (las de nacimiento de las personas y las de origen de las bandas), sellos (con la jerarquía Parlophone → Warner Music Group) y el **árbol de géneros completo** del roadmap.
- **Artistas:** The Beatles, John Lennon, Paul McCartney, George Harrison, Ringo Starr, Plastic Ono Band, Wings, Traveling Wilburys y Billy Preston, con sus géneros y membresías.
- **Personas:** los integrantes de esas bandas y las personas con crédito (George Martin, Phil Spector, Glyn Johns, Richard Perry, compositores externos...).
- **Los 12 lanzamientos aprobados, con su tracklist completo:**
  - LP: *Abbey Road*, *Let It Be*, *Imagine*, *Ringo*, *Band on the Run* y *Traveling Wilburys Vol. 1*;
  - EP: *Magical Mystery Tour*;
  - singles: *Get Back*, *Give Peace a Chance*, *My Sweet Lord* y *Another Day*;
  - compilación: *1*.
- **Créditos:** de artista (Principal y Featuring de Billy Preston) y de persona (compositores, productores y los arreglistas de un tema tradicional).
- **Procedencia:** `obtencion_datos/crudo/` con las 12 respuestas de MusicBrainz y `obtencion_datos/fuentes.csv` con una fuente (con enlace permanente) por cada dato. El README suma las decisiones de esta carga.
- **Pruebas** que comparan los CSV con `crudo/`, comprueban la integridad de los datos y verifican los hechos del roadmap.

## Capacidades

### Capacidades nuevas
- `datos-demo`: contenido y garantías de los datos de la demo (completitud, procedencia e integridad).

### Capacidades modificadas
Ninguna.

## Impacto

- `datos/*.csv`, `obtencion_datos/` y `tests/`. No se toca el código ni el esquema.
- Cada `docker compose up` carga estos datos.
