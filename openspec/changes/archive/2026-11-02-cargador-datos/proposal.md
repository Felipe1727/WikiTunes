# Propuesta: cargador-datos

## Por qué

Los datos de la demo se entregan como CSV (uno por tabla) más archivos de arte ASCII, y hace falta un mecanismo fiable para cargarlos. El roadmap exige además documentar cómo se obtuvo cada dato, sin inventar nada, antes de escribir los datos de The Beatles y de King Crimson.

## Qué cambia

- **Cargador en Python** (`python -m wikitunes.cargador`):
  - lee `datos/<tabla>.csv` (UTF-8, encabezado, RFC 4180, ids explícitos, celda vacía = `NULL`) y el arte de `datos/arte/*.txt` (referenciado desde `datos/arte_artista.csv`);
  - reemplaza el contenido de la base en una sola transacción, respetando el orden de las llaves foráneas;
  - si algo falla, deshace todo e informa en español el archivo y la línea.
- **Servicio `cargador` en `compose.yaml`:** de un solo uso, corre cuando la base está sana, así que `docker compose up -d --wait` deja los datos cargados. Funciona también sin datos.
- **`src/wikitunes/configuracion.py`:** lectura de las variables `WIKITUNES_BD_*` (con `.env`), compartida por el cargador, las pruebas y, más adelante, la aplicación.
- **Directorio `obtencion_datos/`:**
  - `README.md` con la metodología y todas las convenciones de datos del roadmap;
  - `fuentes.csv` (con su encabezado);
  - `crudo/` para las respuestas de MusicBrainz;
  - `scripts/musicbrainz.py`, que descarga un lanzamiento por MBID (con un User-Agent identificable y como máximo 1 petición por segundo), guarda el JSON crudo e imprime un borrador del tracklist.
- **`datos/`** vacío, con su `README.md` y `arte/`.

## Capacidades

### Capacidades nuevas
- `carga-datos`: carga transaccional y reproducible de los CSV y el arte en la base.
- `procedencia-datos`: documentación y herramientas que respaldan con fuentes cada dato de la demo.

### Capacidades modificadas
Ninguna.

## Impacto

- `compose.yaml` (servicio nuevo con la imagen `ghcr.io/astral-sh/uv`), `src/wikitunes/`, `tests/`, `datos/` y `obtencion_datos/`.
- Cada `docker compose up` vuelve a cargar los datos desde los CSV. La base siempre refleja el repositorio.
- `tests/conftest.py` pasa a usar `wikitunes.configuracion`.
