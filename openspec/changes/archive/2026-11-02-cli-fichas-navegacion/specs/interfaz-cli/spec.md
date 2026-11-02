# Delta de spec

## ADDED Requirements

### Requirement: Fichas
La interfaz DEBE (MUST) mostrar la ficha de un artista (arte, tipo, años, origen, géneros, discografía e integrantes), de una persona (nombre legal, nacimiento, fallecimiento y artistas de los que fue integrante), de una canción (intérpretes, duración, géneros, créditos y álbumes) y de un género (árbol, artistas y álbumes).

#### Scenario: Ficha de persona
- **WHEN** se abre la ficha de George Harrison
- **THEN** se ve su nacimiento (25 de febrero de 1943, Liverpool) y sus artistas, entre ellos los Traveling Wilburys (1988–1991)

### Requirement: Menú «¿Y ahora?»
Después de cada resultado, la interfaz DEBE (MUST) ofrecer saltos a los elementos relacionados, «Volver» a la pantalla anterior (si la hay) y «Menú principal».

#### Scenario: De una canción a su álbum
- **WHEN** desde la ficha de *Starless* se elige «Álbum: Red»
- **THEN** se muestra el tracklist de *Red*

#### Scenario: De un integrante a otra banda
- **WHEN** desde los integrantes de The Beatles en 1963 se elige Paul McCartney y luego «Artista: Wings»
- **THEN** se muestra la ficha de Wings con su discografía

#### Scenario: De un género a un artista
- **WHEN** desde el árbol de Rock progresivo se piden sus artistas y álbumes y se elige King Crimson
- **THEN** se muestra la ficha de King Crimson

#### Scenario: Del tracklist a una canción y a otro álbum
- **WHEN** desde el tracklist de *Abbey Road* se elige *Something* y luego «Álbum: 1 (2000)»
- **THEN** se muestra el tracklist de *1*

#### Scenario: Volver
- **WHEN** se elige «Volver a …»
- **THEN** se muestra otra vez la pantalla anterior con sus saltos

### Requirement: Migas
Cada pantalla DEBE (MUST) mostrar el camino recorrido desde el menú principal.

#### Scenario: Camino de navegación
- **WHEN** se navega de la ficha de Paul McCartney a la de Wings
- **THEN** se ve `Menú › Paul McCartney › Wings`
