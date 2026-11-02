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

## Uso

Con la base levantada (ver abajo):

```bash
uv run wikitunes                  # arranca con la animación del conejito
uv run wikitunes --sin-animacion  # directo a la portada
uv run wikitunes --version
```

En el menú «¿Qué quieres consultar?» están las consultas:

| Consulta | Qué muestra | Encabezado |
|---|---|---|
| Canciones de una persona | En qué canciones participó, por qué vía (banda, solista o crédito propio) y con qué rol | Nombre con pyfiglet |
| Árbol de un género | El género y todos sus subgéneros | Nombre con pyfiglet |
| Tracklist de un álbum | Pistas, intérpretes, duraciones y duración total | Título con pyfiglet |
| Integrantes de un artista en una fecha | Quiénes eran integrantes ese día (`AAAA-MM-DD`) | Arte ASCII del artista |
| Historial de integrantes | Todos los periodos de membresía | Arte ASCII del artista |

Además hay tres fichas:

| Ficha | Qué muestra |
|---|---|
| Artista | Arte ASCII, tipo, años, origen, géneros, discografía e historial de integrantes |
| Persona | Nombre legal, nacimiento, fallecimiento y artistas de los que fue integrante |
| Canción | Intérpretes, duración, géneros, créditos (compositores, productores...) y álbumes donde aparece |

Después de cada resultado, el menú **«¿Y ahora?»** permite seguir navegando: de una canción a su
álbum, de un integrante a sus otras bandas, de un género a sus artistas, del tracklist a una canción
y de ahí a otro álbum donde aparece. «Volver» regresa a la pantalla anterior, y la línea gris
`Menú › Paul McCartney › Wings` muestra el camino recorrido.

Para elegir personas, artistas, álbumes o géneros no hace falta escribir ids: se escribe parte del
nombre y el autocompletado sugiere opciones (sin importar mayúsculas, tildes ni comillas tipográficas).
`Tab` muestra las sugerencias.

La animación dura unos dos segundos y medio y se salta con cualquier tecla. No se muestra si la
salida no es una terminal o si está definida la variable `NO_COLOR`. Para salir, elige «Salir» o
pulsa `Ctrl+C`.

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

### Datos de la demo

Cada `docker compose up -d --wait` vuelve a cargar los datos de [`datos/`](datos/) (servicio
`cargador`): reemplaza todo el contenido de la base por el de los CSV en una sola transacción. Si un
CSV tiene un error, el comando falla y la base no cambia; el detalle está en
`docker compose logs cargador`.

También se puede cargar a mano desde el host:

```bash
uv run python -m wikitunes.cargador
```

El formato de los archivos está en [`datos/README.md`](datos/README.md) y la procedencia de cada
dato, en [`obtencion_datos/`](obtencion_datos/).

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

## Diagrama entidad-relación

La fuente del diagrama es [`Diagrama/musica_er.mmd`](Diagrama/musica_er.mmd) y la imagen es
[`Diagrama/musica_er.png`](Diagrama/musica_er.png). Después de editar el `.mmd`, regenera la
imagen (usa Docker, no hace falta instalar Node):

```bash
./scripts/generar_diagrama.sh
```

## Pruebas y lint

```bash
docker compose up -d --wait && uv run pytest
uv run ruff check . && uv run ruff format --check .
```

Las pruebas marcadas como `integracion` necesitan la base. Si no está levantada, se saltan con un
aviso; con `WIKITUNES_EXIGIR_BD=1` (como en la CI) fallan.
