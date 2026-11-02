# integrantes-artista Specification

## Purpose
Identifica a cada artista de forma única por su nombre y permite consultar el historial completo de integrantes, además de los integrantes en una fecha.

## Requirements

### Requirement: Nombre de artista único
La base DEBE (MUST) rechazar dos artistas con el mismo nombre, para que los procedimientos que reciben un nombre de artista no sean ambiguos.

#### Scenario: Nombre repetido
- **WHEN** se inserta un artista con el nombre de otro ya existente
- **THEN** la base rechaza la inserción por clave duplicada

### Requirement: Historial completo de integrantes
`sp_historial_integrantes` DEBE (MUST) devolver, para el artista con el nombre exacto recibido, una fila por cada periodo de membresía, con el id y el nombre de la persona, el rol, la fecha de inicio y la fecha de fin, ordenadas por fecha de inicio y luego por persona.

#### Scenario: Integrante que sale y vuelve
- **WHEN** una persona tiene dos periodos de membresía en el artista
- **THEN** el historial devuelve dos filas para esa persona, en orden cronológico

#### Scenario: Integrante activo
- **WHEN** una membresía no tiene fecha de fin
- **THEN** la fila devuelve la fecha de fin en `NULL`

#### Scenario: Artista inexistente
- **WHEN** se llama con un nombre que no corresponde a ningún artista
- **THEN** no se devuelve ninguna fila
