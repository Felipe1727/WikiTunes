# Diseño: cli-arranque

## Contexto

Ver `proposal.md`. La capa de datos (`Catalogo`, `conectar` y sus errores) ya existe.

## Decisiones

### 1. Fotogramas como texto puro
`fotogramas()` devuelve 17 cadenas: aparición progresiva, 12 pasos de cabeceo con notas que rotan, y la portada. `renderizable()` colorea con `Text.highlight_regex`: conejito rosa, audífonos magenta y notas celestes. Así la animación se prueba sin terminal, renderizándola a texto.

### 2. Tecla para saltar sin bloquear
`LectorDeTeclas` pone la terminal en modo `cbreak` y espera con `select` (en POSIX) o con `msvcrt.kbhit` (en Windows) durante cada fotograma. Si stdin no es una TTY, solo espera. `reproducir_animacion` recibe la función de espera como parámetro, para poder probarla.

### 3. Menú con questionary
`questionary.select` con estilo propio (puntero rosa, `qmark` ♪). El menú devuelve una clave, y `cli.acciones()` asocia cada clave a una función `(consola, catalogo)`. En esta spec, las cinco consultas usan una acción provisional que avisa que todavía no están disponibles; `cli-consultas` las reemplaza.

### 4. Errores y salida
- La conexión se abre después de la portada. Un `ErrorDeConexion` muestra un panel rojo y sale con código 1.
- Un `ErrorDeBaseDeDatos` durante una consulta muestra el panel y vuelve al menú. Si es de conexión, sale.
- `KeyboardInterrupt` y `EOFError` (Ctrl+D o sin terminal interactiva) terminan con una despedida y el código 130.

## Riesgos / Compromisos

- [Algunos emuladores de terminal muestran las notas ♪ ♫ ♬ con otro ancho] → Rich las mide de una columna y no afectan la alineación del conejito. Además, la animación se puede desactivar.
