# procedencia-datos Specification

## Purpose
Garantiza que cada dato de la demo sea real y verificable: documenta la metodología y las convenciones, y registra la fuente de cada dato y las respuestas crudas de MusicBrainz.

## Requirements

### Requirement: Metodología y convenciones documentadas
`obtencion_datos/README.md` DEBE (MUST) documentar las fuentes permitidas, la edición de referencia, la convención de fechas aproximadas, la regla de versiones, la regla de participación, los créditos con nombre variante, la nota sobre la salida de Lennon y las reglas del árbol de géneros.

#### Scenario: Consulta de una convención
- **WHEN** alguien necesita saber por qué una membresía empieza el día 1 del mes
- **THEN** el README explica la convención de fechas aproximadas y remite a `fuentes.csv`

### Requirement: Registro de fuentes
`obtencion_datos/fuentes.csv` DEBE (MUST) tener las columnas `tabla,id,url,campos,nota`, con una fila por cada dato respaldado.

#### Scenario: Archivo inicial
- **WHEN** todavía no hay datos de la demo
- **THEN** `fuentes.csv` existe solo con su encabezado

### Requirement: Descarga reproducible desde MusicBrainz
El script de MusicBrainz DEBE (MUST) descargar un lanzamiento por su MBID con un User-Agent identificable y a lo sumo 1 petición por segundo, guardar la respuesta en `obtencion_datos/crudo/<mbid>.json`, reutilizarla si ya existe y mostrar un borrador del tracklist con duraciones en segundos redondeados.

#### Scenario: Respuesta ya guardada
- **WHEN** el JSON del MBID ya está en `crudo/`
- **THEN** el script no hace ninguna petición de red y muestra el borrador

#### Scenario: Duración en milisegundos
- **WHEN** una pista dura 185 600 ms
- **THEN** el borrador indica 186 segundos
