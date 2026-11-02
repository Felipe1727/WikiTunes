# interfaz-cli Specification

## Purpose
Define el comportamiento de la línea de comandos `wikitunes`: el arranque animado, el menú principal, los avisos de error y la salida.

## Requirements

### Requirement: Arranque animado
Al ejecutar `wikitunes` en una terminal interactiva con color, la aplicación DEBE (MUST) mostrar una animación de 2 a 3 segundos de un conejito con audífonos escuchando música, que termina en la portada con el título.

#### Scenario: Arranque normal
- **WHEN** se ejecuta `wikitunes` en una terminal
- **THEN** se ve el conejito aparecer, cabecear entre notas musicales y quedar en la portada

#### Scenario: Saltar la animación
- **WHEN** se pulsa cualquier tecla durante la animación
- **THEN** la animación termina enseguida y queda la portada

### Requirement: Animación desactivable
La animación NO DEBE (MUST NOT) mostrarse con `--sin-animacion`, cuando la salida no es una terminal o cuando está definida `NO_COLOR`. En esos casos se muestra la portada directamente.

#### Scenario: Sin terminal
- **WHEN** la salida de `wikitunes` se redirige a un archivo
- **THEN** no hay animación y aparece la portada

### Requirement: Menú principal
Después del arranque, la aplicación DEBE (MUST) preguntar «¿Qué quieres consultar?» con un menú de las consultas disponibles y la opción «Salir».

#### Scenario: Salir
- **WHEN** se elige «Salir»
- **THEN** la aplicación se despide y termina con código 0

### Requirement: Base de datos caída
Si la base no responde al arrancar, la aplicación DEBE (MUST) mostrar un aviso en español que sugiera `docker compose up -d`, sin traceback, y terminar con código 1.

#### Scenario: Arranque sin base
- **WHEN** se ejecuta `wikitunes` con la base apagada
- **THEN** aparece el aviso y no se muestra ningún traceback

### Requirement: Interrupción
Ctrl+C o el cierre de la entrada DEBEN (MUST) terminar la aplicación con una despedida y sin traceback.

#### Scenario: Ctrl+C en el menú
- **WHEN** se pulsa Ctrl+C en el menú principal
- **THEN** la aplicación se despide y termina sin traceback

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
