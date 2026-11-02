# Delta de spec

## Purpose

Define qué canciones se atribuyen a una persona, ya sea a través de un artista del que fue integrante o por un crédito propio, y cómo se busca a la persona por su nombre exacto.

## ADDED Requirements

### Requirement: Participación vía artista
Una persona DEBE (MUST) figurar en una canción vía un artista solo si ese artista está acreditado en la canción, la persona fue integrante del artista en algún periodo, y además tiene un crédito propio en la canción o era integrante en su fecha de salida (un inicio o fin `NULL` cuenta como abierto).

#### Scenario: Integrante en la fecha de salida
- **WHEN** la persona era integrante del artista acreditado cuando salió la canción
- **THEN** la canción figura con la vía igual al nombre del artista y el rol del crédito del artista

#### Scenario: Antiguo integrante sin crédito
- **WHEN** la persona fue integrante del artista, pero no en la fecha de salida, y no tiene crédito propio en la canción
- **THEN** la canción no figura vía ese artista para esa persona

#### Scenario: Antiguo integrante con crédito propio
- **WHEN** la persona fue integrante del artista, no en la fecha de salida, pero tiene un crédito propio (p. ej. de compositor) en la canción
- **THEN** la canción figura vía ese artista

#### Scenario: Canción sin fecha de salida
- **WHEN** la canción no está en ningún álbum con fecha de lanzamiento y la persona no tiene crédito propio en ella
- **THEN** la canción no figura vía el artista

### Requirement: Fecha de salida de una canción
La fecha de salida de una canción DEBE (MUST) ser la fecha de lanzamiento más antigua entre los álbumes que la contienen.

#### Scenario: Canción reutilizada en una compilación posterior
- **WHEN** una canción salió en un LP y años después en una compilación
- **THEN** la membresía se compara con la fecha del LP, no con la de la compilación

### Requirement: Créditos individuales
Cada crédito propio de una persona en una canción DEBE (MUST) figurar con la vía `(crédito individual)` y el rol del crédito, sea o no integrante de algún artista acreditado.

#### Scenario: Productor externo
- **WHEN** una persona que no es integrante del artista acreditado tiene un crédito de productor en la canción
- **THEN** la canción figura solo con la vía `(crédito individual)` y el rol `Productor`

### Requirement: Búsqueda exacta por nombre de persona
`sp_canciones_de_persona` DEBE (MUST) devolver las participaciones de las personas cuyo nombre conocido o nombre legal es exactamente el nombre recibido, y esa búsqueda DEBE poder resolverse con índices.

#### Scenario: Nombre exacto
- **WHEN** se llama con el nombre conocido completo de una persona
- **THEN** se devuelven todas sus participaciones

#### Scenario: Nombre parcial
- **WHEN** se llama con solo una parte del nombre
- **THEN** no se devuelve ninguna fila

#### Scenario: Plan de ejecución
- **WHEN** se obtiene el `EXPLAIN` de la búsqueda de una persona por nombre conocido o legal
- **THEN** el plan considera los índices de `nombre_conocido` y `nombre_legal`
