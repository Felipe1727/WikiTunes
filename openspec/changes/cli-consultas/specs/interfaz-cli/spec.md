# Delta de spec

## ADDED Requirements

### Requirement: Elección con autocompletado
Para elegir una persona, un artista, un álbum o un género, la interfaz DEBE (MUST) ofrecer autocompletado por subcadena que no distinga mayúsculas, tildes ni comillas tipográficas, y DEBE rechazar un texto que no corresponda a ninguna opción.

#### Scenario: Búsqueda parcial
- **WHEN** el usuario escribe «mccart» al elegir una persona
- **THEN** se sugiere «Paul McCartney»

#### Scenario: Texto que no existe
- **WHEN** el usuario confirma un texto que no corresponde a ninguna opción
- **THEN** la interfaz pide que elija una opción de la lista

### Requirement: Fecha validada
La consulta de integrantes en una fecha DEBE (MUST) pedir la fecha con el formato `AAAA-MM-DD` y rechazar fechas inválidas.

#### Scenario: Fecha inválida
- **WHEN** el usuario escribe «1974-13-01»
- **THEN** la interfaz explica el formato esperado y vuelve a pedir la fecha

### Requirement: Encabezado según el protagonista
Las consultas cuyo protagonista es un artista DEBEN (MUST) mostrar primero su arte ASCII con su estilo, y las demás un título generado con pyfiglet. Si el arte no cabe en la terminal, DEBE mostrarse el nombre con pyfiglet.

#### Scenario: Integrantes de King Crimson
- **WHEN** se consultan los integrantes de King Crimson en 1974-06-01
- **THEN** primero aparece el arte de King Crimson y después la tabla con Fripp, Wetton, Bruford y Cross con sus periodos en años

#### Scenario: Tracklist
- **WHEN** se consulta el tracklist de *Abbey Road*
- **THEN** el encabezado es el título generado con pyfiglet

### Requirement: Presentación de resultados
Los resultados DEBEN (MUST) mostrarse en tablas con estilo (o en un árbol para los géneros), con los valores del esquema traducidos al español. Una consulta sin resultados DEBE mostrar un panel «Sin resultados».

#### Scenario: Tracklist con resumen
- **WHEN** se consulta el tracklist de *Abbey Road*
- **THEN** aparecen sus 17 pistas y el resumen «LP · 17 pistas · duración total 47:25»

#### Scenario: Fecha sin integrantes
- **WHEN** se consultan los integrantes de King Crimson en 1990-01-01
- **THEN** aparece el panel «Sin resultados»
