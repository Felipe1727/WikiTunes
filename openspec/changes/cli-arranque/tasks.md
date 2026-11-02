# Tareas

## 1. Arranque

- [ ] 1.1 Crear `wikitunes/ui/arranque.py` (fotogramas, color, lector de teclas, reproducción y portada) con `tests/test_arranque.py`; verificar con `uv run pytest`
- [ ] 1.2 Crear `wikitunes/ui/menu.py` (menú «¿Qué quieres consultar?» con estilo propio); verificar con `tests/test_cli.py`

## 2. Comando

- [ ] 2.1 Crear `wikitunes/cli.py` y `wikitunes/__main__.py`, registrar el script `wikitunes` y manejar la base caída, Ctrl+C y el fin de la entrada, con `tests/test_cli.py`; verificar con `uv run pytest` y ejecutando `uv run wikitunes` en una terminal
- [ ] 2.2 Documentar el uso en el README; verificar que los comandos documentados funcionan

## Workflow follow-up

- Fusionar la PR y archivar el cambio con `/opsx:archive`.
