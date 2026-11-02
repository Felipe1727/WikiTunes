# Diseño: datos-beatles

## Contexto

Ver `proposal.md`. Los CSV se cargan con el cargador de `cargador-datos`. Las convenciones de datos están en `obtencion_datos/README.md`.

## Objetivos / No objetivos

**Objetivos:** datos reales, completos y verificables para el caso The Beatles, y pruebas que impidan regresiones.

**No objetivos:** King Crimson (spec `datos-king-crimson`) y el arte ASCII (spec `arte-artistas`). El árbol de géneros se carga completo ahora; los nodos sin uso se revisan al terminar los datos de King Crimson.

## Decisiones

### 1. Obtención
- **MusicBrainz**, con `scripts/musicbrainz.py`: tracklists, duraciones (ms → s), fechas y sellos.
- **Wikipedia en inglés**, con la API de wikitext: biografías, membresías, créditos y géneros.
- **Wikipedia en español**: nombres de los géneros.

Cada fuente de Wikipedia se cita con un **enlace permanente** (`oldid`) a la revisión consultada. Así la fuente no cambia aunque cambie el artículo.

### 2. Ediciones de referencia
La edición original del Reino Unido de cada lanzamiento. Excepción: *Traveling Wilburys Vol. 1* no tuvo edición británica en 1988, así que se usa la de EE. UU., país de origen de la banda (Los Ángeles). En *Magical Mystery Tour* se usa la edición estéreo.

### 3. Misma grabación
La misma grabación se detecta por el id de grabación de MusicBrainz (*Something*, *Come Together* y *The Long and Winding Road* en *1*). Hay una sola equivalencia manual, verificada en Wikipedia: el *Get Back* de *1* es la versión del single. *Let It Be* en *1* es la versión del single y es otra fila, distinta de la del LP.

### 4. Créditos
- **Compositores:** los que figuran en la edición de referencia. Por ejemplo, Lennon–McCartney en *Give Peace a Chance* (crédito original) e *Imagine* solo de Lennon (crédito original del LP). Las atribuciones posteriores se anotan en las fuentes.
- **Traveling Wilburys:** sus canciones se acreditan a la banda, así que se registran los cinco integrantes como compositores.
- **Productores:** los del artículo de la canción, si es sobre esa grabación; si no, los del álbum. En las pistas de *Let It Be*, el productor del álbum (Phil Spector).

### 5. Correspondencia de géneros
Los géneros de las fuentes que no están en el árbol se asignan al nodo más cercano según una tabla fija documentada en `obtencion_datos/README.md`. Los que no tienen ningún nodo razonablemente cercano (blues, R&B, soul, funk, gospel, music hall...) se omiten: asignarlos a la fuerza sería inventar.

### 6. Pruebas sin base de datos
`tests/test_datos.py` lee los CSV y `crudo/` directamente. Comprueba la completitud frente a MusicBrainz, la procedencia, la integridad y los tipos exigidos. Es genérica, así que también cubrirá los datos de King Crimson. Los hechos que dependen de la vista y los procedimientos van en `tests/integracion/test_datos_beatles.py`.

## Riesgos / Compromisos

- [Las canciones que solo están en *1* (2000) salen después del fin de The Beatles] → Con la regla aprobada, su participación vía banda no cuenta; solo cuentan los créditos (Lennon y McCartney como compositores). Es una consecuencia de la regla, igual que la de *Let It Be*, y queda documentada.
- [Fechas aproximadas en Wings, Plastic Ono Band y Traveling Wilburys] → Siguen la convención (día 1 o 1 de enero) y se marcan en `fuentes.csv`.
