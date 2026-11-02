# Tareas

## 1. Proyecto Python

- [x] 1.1 Crear `pyproject.toml` (hatchling, `requires-python >= 3.12`, dependencias de ejecución y de desarrollo, configuración de ruff y pytest con la marca `integracion`) y `src/wikitunes/__init__.py`; verificar que `uv sync` termina sin errores y genera `uv.lock`
- [x] 1.2 Ampliar `.gitignore` (`.env`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `.idea/`) y crear `.gitattributes` (finales LF); verificar con `git status` que `.venv/` no aparece

## 2. Base de datos con Docker Compose

- [x] 2.1 Crear `compose.yaml` (mysql:8.4, montajes `:z` del esquema y los procedimientos, healthcheck por TCP, volumen `datos_mysql`, puerto `WIKITUNES_BD_PUERTO`) y `.env.ejemplo`; verificar que `docker compose up -d --wait` termina con éxito desde un volumen vacío
- [x] 2.2 Crear `bd/inicializacion/03_usuario_lectura.sh`, que crea el usuario con `SELECT, EXECUTE` sobre `musica`; verificar con `SHOW GRANTS` desde el contenedor

## 3. Pruebas de integración

- [x] 3.1 Crear `tests/conftest.py` con el fixture de conexión (variables `WIKITUNES_BD_*`, `.env` opcional, salto o fallo según `WIKITUNES_EXIGIR_BD`); verificar que con la base apagada las pruebas se saltan y que con `WIKITUNES_EXIGIR_BD=1` fallan
- [x] 3.2 Crear `tests/integracion/test_humo_bd.py` (16 tablas, 4 triggers, la vista, 4 procedimientos, permisos de lectura y escritura rechazada); verificar que `uv run pytest` pasa con la base levantada

## 4. CI y documentación

- [x] 4.1 Crear `.github/workflows/ci.yml` (matriz 3.12 y 3.14, lint, Compose y pruebas con `WIKITUNES_EXIGIR_BD=1`); verificar que el lint pasa en local y que los checks de la PR quedan en verde
- [x] 4.2 Escribir el `README.md` inicial en español (requisitos, `uv sync`, levantar y reiniciar la base, ejecutar pruebas y lint); verificar que cada comando documentado funciona tal como está escrito

## Workflow follow-up

- Fusionar la PR y archivar el cambio con `/opsx:archive`.
