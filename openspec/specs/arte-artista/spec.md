# arte-artista Specification

## Purpose
Guarda en la base de datos el arte ASCII (logo en texto) de cada artista y su estilo de presentación, para usarlo como encabezado de las consultas cuyo protagonista es un artista.

## Requirements

### Requirement: Un arte opcional por artista
La base DEBE (MUST) permitir como máximo un arte por artista, en la tabla `arte_artista`, cuya clave es el `artista_id`. Todo arte DEBE referirse a un artista existente.

#### Scenario: Segundo arte para el mismo artista
- **WHEN** se inserta un arte para un artista que ya tiene uno
- **THEN** la base rechaza la inserción por clave duplicada

#### Scenario: Arte de un artista inexistente
- **WHEN** se inserta un arte con un `artista_id` que no existe
- **THEN** la base rechaza la inserción por la llave foránea

### Requirement: Conservación exacta del arte
La base DEBE (MUST) devolver el arte exactamente como se guardó, incluidos los saltos de línea, los espacios iniciales y finales, las barras invertidas, las comillas simples y dobles, y los caracteres Unicode de bloques y marcos.

#### Scenario: Arte de varias líneas con caracteres especiales
- **WHEN** se guarda un arte de varias líneas que contiene `\`, `"`, `'`, espacios al inicio y caracteres como `█`, `▀` y `╔`
- **THEN** al leerlo se obtiene una cadena idéntica a la guardada

### Requirement: Estilo de presentación opcional
Cada arte DEBE (MUST) poder tener un estilo de presentación de hasta 40 caracteres, o ninguno.

#### Scenario: Arte sin estilo
- **WHEN** se guarda un arte sin estilo
- **THEN** su estilo queda en `NULL`

### Requirement: Borrado en cascada
Al borrar un artista, la base DEBE (MUST) borrar también su arte.

#### Scenario: Borrar un artista con arte
- **WHEN** se borra un artista que tiene arte
- **THEN** su fila de `arte_artista` desaparece
