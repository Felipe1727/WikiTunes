# Diseño: cargador-datos

## Contexto

Ver `proposal.md`. El usuario de la aplicación es de solo lectura, así que la carga usa `root`. Hay tablas autorreferenciadas (`genero`, `sello`) y un trigger en `membresia` que impide que un solista tenga más de una persona. El conector instalado es mysql-connector-python 26.10.

## Objetivos / No objetivos

**Objetivos:** que la base refleje siempre los CSV; que los errores sean claros; y que las pruebas puedan cargar datos de ejemplo sin destruir los datos reales.

**No objetivos:** los datos en sí (specs `datos-*` y `arte-artistas`) y la comparación de los CSV con `crudo/` (spec `datos-beatles`).

## Decisiones

### 1. Siempre reemplazar, en una sola transacción
`cargar(conexion, directorio, confirmar=True)` hace lo siguiente:
1. desactiva `FOREIGN_KEY_CHECKS` solo durante los `DELETE` (por las tablas autorreferenciadas) y lo reactiva;
2. inserta fila por fila en el orden fijo de las llaves foráneas;
3. hace `COMMIT` solo si `confirmar` es verdadero.

Las pruebas usan `confirmar=False` y luego `ROLLBACK`, de modo que los datos de la demo no se pierden.
- *Alternativa descartada:* no cargar nada si ya hay datos. Deja la base desactualizada cuando cambian los CSV.

Orden de carga: `pais`, `ciudad`, `genero`, `sello`, `persona`, `artista`, `membresia`, `artista_genero`, `arte_artista`, `album`, `album_artista`, `album_genero`, `cancion`, `cancion_genero`, `album_cancion`, `credito_artista`, `credito_persona`. Dentro de `genero` y `sello`, el CSV ya trae los padres antes que los hijos (convención del roadmap), y el `INSERT` fila por fila lo respeta.

### 2. Validar el encabezado contra `information_schema`
Las columnas de cada tabla se leen de `information_schema.columns`. Un encabezado con una columna desconocida falla antes de insertar nada. Una columna omitida toma su valor por defecto.

### 3. Errores con archivo y línea
`ErrorDeCarga` lleva el mensaje en español. La línea es `csv.reader.line_num`, la última línea física del registro, que coincide con el número de línea en registros de una sola línea.

### 4. Arte: `rstrip("\n")` y nada más
Los editores agregan un salto final. Se quitan solo los `\n` del final; los espacios finales de cada línea se conservan. La ruta se resuelve y debe quedar dentro de `datos/arte/`.

### 5. Servicio de un solo uso con la imagen de uv
El servicio `cargador` usa `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` y monta el repositorio en `/app` (de solo lectura, con `:z`). Además:
- `UV_PROJECT_ENVIRONMENT=/opt/venv`, para no tocar el `.venv` del host;
- un volumen `cache_uv` para la caché de uv;
- comando `uv run --frozen --no-dev python -m wikitunes.cargador`;
- `depends_on: bd: condition: service_healthy`.

Con Compose v5, `up --wait` acepta un servicio de un solo uso que termina con código 0 (verificado), y un `up` posterior lo vuelve a ejecutar.
- *Alternativa descartada:* un Dockerfile propio. Habría que reconstruir la imagen cada vez que cambian las dependencias.

### 6. `wikitunes.configuracion`
Define una dataclass `ConfiguracionBD` construida desde el entorno (y `.env` mediante python-dotenv), con un método para obtener los parámetros del conector. Tiene variantes para el usuario de la aplicación y para `root`, y la usan el cargador y `tests/conftest.py`.

### 7. Script de MusicBrainz fuera del paquete
`obtencion_datos/scripts/musicbrainz.py` es una herramienta de desarrollo y no se distribuye. Usa solo la biblioteca estándar (`urllib`, `json`):
- consulta `release/<mbid>?inc=recordings+artist-credits+labels+release-groups&fmt=json`;
- envía el User-Agent `WikiTunes/0.1 (https://github.com/Felipe1727/WikiTunes)`;
- espera 1 segundo entre peticiones.

La transformación JSON → borrador es una función pura y tiene pruebas unitarias con un JSON ficticio mínimo.

## Riesgos / Compromisos

- [`--wait` se comporta distinto en versiones antiguas de Compose] → La CI usa la versión del runner. Si falla allí, se ajusta en esta misma spec.
- [La primera ejecución del cargador descarga dependencias] → Una caché en volumen. Son unos segundos.
- [Recargar todo en cada `up` es más lento que una carga incremental] → Con cientos de filas, tarda menos de un segundo.
