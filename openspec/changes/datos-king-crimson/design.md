# Diseño: datos-king-crimson

## Contexto

Ver `proposal.md`. Las convenciones y las pruebas genéricas son las de `datos-beatles`.

## Objetivos / No objetivos

**Objetivos:** fechas de membresía con la mayor precisión que den las fuentes, para que las consultas por fecha sean correctas.

**No objetivos:** el arte ASCII (spec `arte-artistas`) y otros artistas relacionados.

## Decisiones

### 1. Fechas de membresía desde la línea de tiempo
La lista «List of King Crimson members» da solo años. Con la convención del 1 de enero, toda la formación de 1972–1974 habría terminado antes de *Red*, y la consulta de 1974 saldría vacía. Por eso se usan las fechas de la línea de tiempo (EasyTimeline, formato `dd/mm/yyyy`) del mismo artículo, unidas por persona y periodo. Hay dos excepciones:
- **Inicio de los fundadores:** el 30 de noviembre de 1968, la formación según el artículo «King Crimson». La línea de tiempo empieza en 1969 porque ahí empieza el gráfico.
- **Fin de las últimas membresías:** el 31 de diciembre de 2021, fin de la línea de tiempo y último año activo según el infobox.

### 2. Producción acreditada a la banda
Si la producción figura como «King Crimson», se registran como productores los integrantes en la fecha de lanzamiento, más los productores externos que nombre la fuente (Rhett Davies y David Bottrill). En *Red*, el personal del álbum nombra explícitamente a Fripp, Wetton y Bruford.

### 3. Música y letra
Cuando la fuente separa música de letra (*In the Court of the Crimson King* y *Discipline*), la música es `Compositor` y la letra `Letrista`. Las piezas instrumentales no tienen letrista.

### 4. Ids
Los datos de King Crimson usan ids propios (personas, artistas, membresías y álbumes desde 101; canciones desde 201) para no mezclarse con los de The Beatles.

### 5. Ediciones
Las originales del Reino Unido. En *VROOOM*, la británica (1994-11-08), con la pieza sin título del principio: Wikipedia confirma que es una «Intro» sin listar de las ediciones originales.

## Riesgos / Compromisos

- [Algunos bordes de la línea de tiempo son aproximaciones de sus editores (p. ej. 30 de junio / 1 de julio de 1970)] → Se citan como tales en `fuentes.csv`. La interfaz muestra años.
- [*Red* figura en MusicBrainz también como «Compilation»] → Se registra como LP (álbum de estudio, según Wikipedia), y queda anotado.
