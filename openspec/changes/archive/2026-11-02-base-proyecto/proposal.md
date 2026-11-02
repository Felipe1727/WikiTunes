# Propuesta: base-proyecto

## Por qué

El repositorio solo tiene el esquema SQL, los procedimientos y el diagrama ER. No hay forma reproducible de levantar la base, ni proyecto Python, ni pruebas, ni CI. Todas las specs siguientes del roadmap dependen de esta base y de sus comandos de calidad (`uv sync`, pruebas y lint).

## Qué cambia

- Proyecto Python gestionado con `uv`: `pyproject.toml`, `uv.lock`, paquete `src/wikitunes/` y directorio `tests/`. Se declaran las dependencias de ejecución del roadmap (`rich`, `questionary`, `pyfiglet`, `mysql-connector-python`, `python-dotenv`) y las de desarrollo (`pytest`, `ruff`).
- `compose.yaml` con MySQL 8.4. Al arrancar con un volumen vacío ejecuta el esquema y los procedimientos actuales tal como están y crea un usuario de solo lectura (`SELECT` y `EXECUTE`). Los montajes llevan `:z` por SELinux.
- Configuración por variables `WIKITUNES_BD_*` con valores por defecto de desarrollo; `.env.ejemplo` versionado y `.env` ignorado.
- Prueba de humo de integración (marca `integracion`) que comprueba los objetos de la base y los permisos del usuario de solo lectura. Si la base no responde, se salta en local y falla con `WIKITUNES_EXIGIR_BD=1`.
- CI en GitHub Actions: lint y pruebas en Python 3.12 y 3.14 con la base de Compose.
- `.gitignore` (con `.env`, `.venv/` e `.idea/`), `.gitattributes` y un `README.md` inicial en español.
- No se modifican el esquema ni los procedimientos.

## Capacidades

### Capacidades nuevas
- `entorno-base-datos`: levantar de forma reproducible la base `musica` con su esquema, procedimientos y usuario de solo lectura, y verificarla con pruebas de integración.
- `integracion-continua`: verificación automática (lint y pruebas contra una base real) de cada cambio enviado al repositorio.

### Capacidades modificadas
Ninguna.

## Impacto

- Archivos nuevos: `pyproject.toml`, `uv.lock`, `compose.yaml`, `bd/`, `src/wikitunes/`, `tests/`, `.github/workflows/`, `.env.ejemplo`, `.gitattributes`, `README.md`. Se amplía `.gitignore`.
- Requiere Docker con Compose en el equipo de desarrollo y en la CI.
- El puerto 3306 del host queda ocupado por defecto (configurable con `WIKITUNES_BD_PUERTO`).
