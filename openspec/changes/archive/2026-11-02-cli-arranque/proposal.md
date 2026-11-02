# Propuesta: cli-arranque

## Por qué

El punto de entrada de la aplicación todavía no existe. El roadmap pide un arranque con un conejito animado, al estilo de Claude Code, que desemboque en el menú principal y que se comporte bien cuando la base no responde o se interrumpe con Ctrl+C.

## Qué cambia

- **Comando `wikitunes`** (`[project.scripts]` y `python -m wikitunes`), con las opciones `--sin-animacion` y `--version`.
- **Animación de arranque** con Rich `Live`: un conejito con audífonos que aparece de forma progresiva, cabecea al ritmo entre notas musicales y termina en la portada con el título.
  - Dura unos 2,5 s y se salta con cualquier tecla.
  - No se muestra con `--sin-animacion`, si no hay TTY o si está definida `NO_COLOR`.
- **Menú principal** «¿Qué quieres consultar?», con questionary y estilo propio.
  - Tiene las cinco consultas y «Salir».
  - Por ahora, las consultas avisan que todavía no están disponibles; llegan en `cli-consultas`.
- **Base caída:** aviso amable en un panel, sin traceback, con código de salida 1.
- **Ctrl+C o fin de la entrada:** despedida sin traceback.

## Capacidades

### Capacidades nuevas
- `interfaz-cli`: el comportamiento de la línea de comandos (arranque, menú, errores y salida).

### Capacidades modificadas
Ninguna.

## Impacto

- `pyproject.toml` (script `wikitunes`), `src/wikitunes/cli.py`, `src/wikitunes/ui/`, `tests/` y `README.md`.
