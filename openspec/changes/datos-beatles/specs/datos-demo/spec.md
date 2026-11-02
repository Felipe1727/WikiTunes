# Delta de spec

## Purpose

Define el contenido de los datos de la demo y las garantías que deben cumplir: lanzamientos completos, procedencia verificable de cada dato e integridad entre tablas.

## ADDED Requirements

### Requirement: Lanzamientos completos y fieles a la fuente
Cada álbum de la demo DEBE (MUST) tener su tracklist completo según su edición de referencia en MusicBrainz, con el mismo título, la misma fecha y las mismas pistas. La duración de cada canción DEBE ser la de su primer lanzamiento en la demo.

#### Scenario: Comparación con la respuesta guardada
- **WHEN** se compara cada álbum con su JSON en `obtencion_datos/crudo/`
- **THEN** coinciden el título, la fecha, la cantidad de pistas y, por pista, el disco, el número, el título y la duración

#### Scenario: Canción reutilizada en una compilación
- **WHEN** una canción de *Abbey Road* aparece también en *1*
- **THEN** es la misma fila de `cancion` y conserva la duración de *Abbey Road*

### Requirement: Procedencia de cada dato
Cada fila de `persona`, `artista`, `membresia`, `album`, `cancion`, `sello` y `genero` DEBE (MUST) tener al menos una fuente en `obtencion_datos/fuentes.csv`.

#### Scenario: Persona sin fuente
- **WHEN** se agrega una persona sin su fila en `fuentes.csv`
- **THEN** la prueba de procedencia falla indicando la tabla y el id

### Requirement: Integridad de créditos y membresías
Cada canción DEBE (MUST) tener al menos un crédito de artista `Principal` y al menos un crédito de `Compositor`, salvo los temas tradicionales, que llevan `Arreglista`. Una persona NO DEBE tener membresías solapadas en el mismo artista.

#### Scenario: Tema tradicional
- **WHEN** una canción es tradicional (como *Maggie Mae*)
- **THEN** no tiene compositor y tiene al menos un arreglista

### Requirement: Tipos de lanzamiento exigidos
La demo DEBE (MUST) incluir al menos un LP, un single, un EP y una compilación, y al menos un crédito `Featuring`.

#### Scenario: Featuring en un single
- **WHEN** se consulta el tracklist del single *Get Back*
- **THEN** sus intérpretes son The Beatles y Billy Preston como featuring

### Requirement: Hechos verificables de The Beatles
Las consultas sobre los datos de The Beatles DEBEN (MUST) reflejar las fechas reales y la regla de participación aprobada.

#### Scenario: Primeros integrantes
- **WHEN** se piden los integrantes de The Beatles en 1961-06-01
- **THEN** aparecen Pete Best y Stuart Sutcliffe

#### Scenario: Los cuatro
- **WHEN** se piden los integrantes de The Beatles en 1963-01-01
- **THEN** aparecen exactamente Lennon, McCartney, Harrison y Starr

#### Scenario: Lennon y Abbey Road
- **WHEN** se piden las canciones de John Lennon
- **THEN** figuran todas las de *Abbey Road* vía The Beatles y no figura *I Me Mine*

#### Scenario: Pete Best
- **WHEN** se piden las canciones de Pete Best
- **THEN** no hay ninguna

#### Scenario: McCartney por tres vías
- **WHEN** se piden las canciones de Paul McCartney
- **THEN** figuran vías The Beatles, Wings y Paul McCartney
