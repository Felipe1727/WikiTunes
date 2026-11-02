# Tareas

## 1. Fichas y navegación

- [ ] 1.1 Agregar `Catalogo.artistas_de_album` y crear `ui/fichas.py` con el render de las cuatro fichas; verificar con las pruebas de integración de fichas
- [ ] 1.2 Crear `ui/navegacion.py` (pantallas, saltos, `Navegador` con pila y migas) y `ui/acciones.py`, agregar las tres fichas al menú principal y conectar todo en `cli.py`; verificar con `uv run pytest` y con una ejecución real en terminal
- [ ] 1.3 Crear `tests/integracion/test_navegacion.py` con los recorridos (canción → álbum, integrante → persona → otra banda, género → artista, tracklist → canción → otro álbum, volver, cancelar); verificar con `uv run pytest`
- [ ] 1.4 Documentar las fichas y la navegación en el README; verificar que coincide con el menú

## Workflow follow-up

- Fusionar la PR y archivar el cambio con `/opsx:archive`.
