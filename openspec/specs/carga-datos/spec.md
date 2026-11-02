# carga-datos Specification

## Purpose
Carga en la base, de forma transaccional y reproducible, los datos de la demo guardados como CSV por tabla y el arte ASCII guardado como archivos de texto.

## Requirements

### Requirement: Formato de los CSV
El cargador DEBE (MUST) leer `datos/<tabla>.csv` en UTF-8, con una fila de encabezado cuyos nombres son columnas de la tabla, separador coma y comillas según RFC 4180. Una celda vacía DEBE cargarse como `NULL`.

#### Scenario: Textos con comas, comillas y saltos de línea
- **WHEN** una celda entre comillas contiene comas, comillas dobladas (`""`) y saltos de línea
- **THEN** se guarda el texto exacto, con una comilla por cada `""`

#### Scenario: Celda vacía
- **WHEN** una celda de una columna que admite nulos está vacía
- **THEN** se guarda `NULL`

#### Scenario: Columna desconocida
- **WHEN** el encabezado de un CSV nombra una columna que no existe en la tabla
- **THEN** la carga falla con un mensaje en español que nombra el archivo y la columna

### Requirement: Arte desde archivos de texto
El arte DEBE (MUST) leerse del archivo `datos/arte/<archivo>` que indica cada fila de `datos/arte_artista.csv` (`artista_id,archivo,estilo`) y guardarse sin modificar, salvo los saltos de línea finales, que se eliminan. Un archivo fuera de `datos/arte/` DEBE rechazarse.

#### Scenario: Arte con barras invertidas
- **WHEN** un archivo de arte contiene `\`, `\n` literal, comillas y bloques Unicode
- **THEN** la base guarda exactamente ese texto, sin el salto de línea final

#### Scenario: Ruta fuera del directorio de arte
- **WHEN** `archivo` es `../secreto.txt`
- **THEN** la carga falla con un mensaje en español

### Requirement: Carga transaccional que reemplaza los datos
Cada carga DEBE (MUST) reemplazar el contenido de todas las tablas del esquema por el de los CSV en una única transacción, insertando en el orden de las llaves foráneas. Un CSV ausente equivale a una tabla vacía.

#### Scenario: Recarga
- **WHEN** se ejecuta la carga dos veces seguidas con los mismos CSV
- **THEN** la base queda con exactamente las filas de los CSV, sin duplicados

#### Scenario: Error en una fila
- **WHEN** una fila viola una restricción (p. ej. una llave foránea inexistente)
- **THEN** no queda ningún cambio en la base y el error en español indica el archivo y la línea

#### Scenario: Sin datos
- **WHEN** el directorio `datos/` no tiene CSV
- **THEN** la carga termina con éxito y la base queda vacía

### Requirement: Carga automática al levantar la base
`docker compose up -d --wait` DEBE (MUST) cargar los datos después de que la base esté sana y terminar con error si la carga falla.

#### Scenario: Arranque con datos
- **WHEN** se ejecuta `docker compose up -d --wait`
- **THEN** al terminar el comando la base contiene los datos de `datos/`
