# Propuesta: datos-king-crimson

## Por qué

King Crimson es el segundo caso de la demo por sus muchos cambios de alineación: la consulta de integrantes en una fecha y el historial completo deben mostrar formaciones realmente distintas.

## Qué cambia

- **Artista King Crimson** con sus géneros y las **37 membresías** de sus 23 integrantes, con fechas de entrada y salida.
- **Personas:** los 23 integrantes y las personas con crédito (Richard Palmer-James, Rhett Davies y David Bottrill).
- **Cuatro lanzamientos con su tracklist completo:** *In the Court of the Crimson King* (1969), *Red* (1974), *Discipline* (1981) y el EP *VROOOM* (1994), con créditos de compositor, letrista y productor.
- **Catálogos:** las ciudades de nacimiento nuevas y los sellos Island Records, E.G. Records, Discipline Global Mobile y Universal Music Group (este último como empresa matriz).
- **Procedencia:** las 4 respuestas de MusicBrainz en `crudo/`, las fuentes en `fuentes.csv` y una sección propia en `obtencion_datos/README.md`.
- No se incluyen otros proyectos de Robert Fripp ni de los demás integrantes.

## Capacidades

### Capacidades nuevas
Ninguna.

### Capacidades modificadas
- `datos-demo`: se agregan los hechos verificables de King Crimson.

## Impacto

- `datos/*.csv`, `obtencion_datos/` y `tests/`. Las pruebas genéricas de datos ya cubren estos datos.
