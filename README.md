# WikiTunes

CLI en línea, muy estética, para explorar un catálogo musical guardado en MySQL: artistas,
personas, álbumes, canciones, géneros y créditos. No reproduce audio ni tiene usuarios.

> Proyecto en construcción. El alcance y el orden de trabajo están en
> [`openspec/roadmap.md`](openspec/roadmap.md).

## Requisitos

- Python 3.12 o superior
- [uv](https://docs.astral.sh/uv/)
- Docker con Docker Compose

## Instalación

```bash
uv sync
```

## Base de datos

La base `musica` corre en un contenedor MySQL 8.4. Al arrancar por primera vez se ejecutan el
esquema (`Diagrama/musica_schema_mysql.sql`) y los procedimientos
(`procedimientos_almacenados/musica_procedimientos_mysql.sql`), y se crea un usuario de solo
lectura para la aplicación.

```bash
docker compose up -d --wait     # levantar la base (espera a que esté lista)
docker compose down             # detenerla (conserva los datos)
docker compose down -v          # detenerla y borrar el volumen (reinicializa en el próximo arranque)
```

Después de cambiar el esquema o los procedimientos, reinicializa la base con `docker compose down -v`
seguido de `docker compose up -d --wait`.

### Configuración

La conexión se configura con variables de entorno o con un archivo `.env` (no versionado). Si no
existe, se usan los valores por defecto de desarrollo:

```bash
cp .env.ejemplo .env    # opcional, para cambiar puertos o credenciales
```

| Variable | Por defecto | Uso |
|---|---|---|
| `WIKITUNES_BD_HOST` | `127.0.0.1` | Host de MySQL |
| `WIKITUNES_BD_PUERTO` | `3306` | Puerto publicado en el host |
| `WIKITUNES_BD_NOMBRE` | `musica` | Base de datos |
| `WIKITUNES_BD_USUARIO` | `wikitunes` | Usuario de solo lectura (`SELECT`, `EXECUTE`) |
| `WIKITUNES_BD_CLAVE` | `wikitunes` | Clave del usuario de solo lectura |
| `WIKITUNES_BD_CLAVE_ROOT` | `raiz_wikitunes` | Clave de `root` del contenedor |

## Pruebas y lint

```bash
docker compose up -d --wait && uv run pytest
uv run ruff check . && uv run ruff format --check .
```

Las pruebas marcadas como `integracion` necesitan la base. Si no está levantada, se saltan con un
aviso; con `WIKITUNES_EXIGIR_BD=1` (como en la CI) fallan.
