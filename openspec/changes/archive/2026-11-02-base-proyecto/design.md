# Diseño: base-proyecto

## Contexto

Ver `proposal.md`. El esquema (`Diagrama/musica_schema_mysql.sql`) empieza con `DROP DATABASE IF EXISTS musica; CREATE DATABASE musica`, y los procedimientos (`procedimientos_almacenados/musica_procedimientos_mysql.sql`) usan `DELIMITER`. Ambos se ejecutan con el cliente `mysql`. El host de desarrollo es Fedora con SELinux en modo *Enforcing* y tiene Docker 29 con Compose y `uv` 0.9.

## Objetivos / No objetivos

**Objetivos:**
- Que `docker compose up -d --wait` deje la base lista sin pasos manuales, tanto en local como en la CI.
- Que las pruebas de integración se conecten con la misma configuración que usará la aplicación.

**No objetivos:**
- La capa de acceso a datos de la aplicación (spec `capa-datos`) y el comando `wikitunes` (spec `cli-arranque`).
- La carga de datos (spec `cargador-datos`).

## Decisiones

### 1. Scripts de inicialización montados sin copiarlos
`compose.yaml` monta los archivos SQL existentes en `/docker-entrypoint-initdb.d/` con nombres numerados (`01_esquema.sql`, `02_procedimientos.sql`) y suma `bd/inicializacion/03_usuario_lectura.sh`. Así el esquema y los procedimientos siguen teniendo una única fuente.
- *Alternativa descartada:* una imagen propia con `COPY`. Obliga a reconstruir la imagen por cada cambio y no aporta nada.

### 2. Usuario de solo lectura creado con un script de shell
La imagen oficial crea `MYSQL_USER` con todos los permisos sobre `MYSQL_DATABASE`, y no hay forma de limitarlo. Por eso no se usan esas variables: un `.sh` en `initdb.d` crea el usuario con `GRANT SELECT, EXECUTE ON musica.*`, leyendo el usuario y la clave del entorno, algo que un `.sql` no puede hacer. Tampoco se define `MYSQL_DATABASE`, porque el esquema ya crea la base. La carga futura de datos usará `root`.

### 3. Salud de la base por TCP
El healthcheck ejecuta `mysqladmin ping -h 127.0.0.1`. Durante la inicialización, el entrypoint arranca un servidor temporal con `--skip-networking`, así que el ping por TCP solo responde cuando todos los scripts terminaron. Esto hace que `--wait` sea fiable.

### 4. Valores por defecto en Compose y en las pruebas
`compose.yaml` usa `${VARIABLE:-valor}` y las pruebas usan los mismos valores por defecto. El archivo `.env` es opcional: `.env.ejemplo` documenta los valores y no hay secretos reales, porque es un entorno de desarrollo. Volumen con nombre `datos_mysql`. Para reinicializar después de un cambio de esquema se usa `docker compose down -v`, lo que queda documentado en el README.

### 5. SELinux
Los montajes de archivos llevan `:z` (etiqueta compartida). `:Z` no se usa porque relabelaría los archivos del repositorio en exclusiva para el contenedor.

### 6. Disponibilidad de la base en las pruebas
`tests/conftest.py` define la marca `integracion` y un fixture de sesión que intenta conectarse. Si falla: con `WIKITUNES_EXIGIR_BD=1` llama a `pytest.fail`; si no, a `pytest.skip` con un motivo en español. Las pruebas sin la marca no tocan la base.

### 7. Proyecto Python
- Diseño `src/` con el paquete `wikitunes`, backend de construcción `hatchling` y `requires-python = ">=3.12"`.
- Se declaran ya todas las dependencias de ejecución del roadmap, para que `uv.lock` quede estable desde el principio.
- ruff con `line-length = 100`, `target-version = "py312"` y las reglas `E`, `F`, `I`, `UP`, `B`.
- El comando `wikitunes` (`[project.scripts]`) se añade en la spec `cli-arranque`.

### 8. CI
`.github/workflows/ci.yml` tiene un único job con una matriz de Python `3.12` y `3.14`. Usa `astral-sh/setup-uv` y ejecuta, en orden, `uv sync`, el lint, `docker compose up -d --wait` y `uv run pytest` con `WIKITUNES_EXIGIR_BD=1`. Docker viene preinstalado en `ubuntu-latest`.

## Riesgos / Compromisos

- [El puerto 3306 del host ya está en uso] → Configurable con `WIKITUNES_BD_PUERTO`.
- [Un volumen viejo no refleja los cambios de esquema de specs futuras] → Documentar `docker compose down -v`. Las specs que cambien el esquema reinician el volumen antes de sus pruebas.
- [Credenciales de desarrollo en `.env.ejemplo`] → Son solo para el contenedor local. El `.env` real queda ignorado.
