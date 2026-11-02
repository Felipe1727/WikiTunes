# Delta de spec

## ADDED Requirements

### Requirement: Arte ASCII para cada artista
Cada artista de la demo DEBE (MUST) tener un arte en `datos/arte/` con un estilo de Rich válido. Cada archivo DEBE tener como máximo 80 columnas, finales de línea LF y ningún tabulador, y solo caracteres que ocupen una columna.

#### Scenario: Artista nuevo sin arte
- **WHEN** se agrega un artista sin su fila en `arte_artista.csv`
- **THEN** la prueba de arte falla

#### Scenario: Carácter de doble ancho
- **WHEN** un arte contiene un emoji o un carácter de ancho doble
- **THEN** la prueba de arte falla indicando la línea

### Requirement: Arte reproducible
El arte DEBE (MUST) poder regenerarse con `obtencion_datos/scripts/generar_arte.py`, y los archivos guardados DEBEN coincidir con lo que genera.

#### Scenario: Arte editado a mano
- **WHEN** alguien edita un `.txt` de arte sin actualizar el generador
- **THEN** la prueba de reproducibilidad falla
