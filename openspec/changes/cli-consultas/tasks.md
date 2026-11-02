# Tareas

## 1. Piezas de la interfaz

- [ ] 1.1 Crear `ui/textos.py` (traducciones, fecha larga, normalización), `ui/preguntas.py` (autocompletado normalizado, `resolver`, fechas) y `ui/encabezados.py` (arte o pyfiglet según el ancho), con `tests/test_ui_textos.py`; verificar con `uv run pytest`

## 2. Consultas

- [ ] 2.1 Crear `ui/consultas.py` con el render y la acción de las cinco consultas, conectarlas en `cli.acciones()`, y agregar `tests/test_render_consultas.py` y `tests/integracion/test_consultas_cli.py`; verificar con `uv run pytest` y con una ejecución real en terminal
- [ ] 2.2 Documentar las consultas en el README; verificar que la tabla coincide con el menú

## Workflow follow-up

- Fusionar la PR y archivar el cambio con `/opsx:archive`.
