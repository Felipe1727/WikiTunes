# Delta de spec

## Purpose

Define el comportamiento de la línea de comandos `wikitunes`: el arranque animado, el menú principal, los avisos de error y la salida.

## ADDED Requirements

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
