# Datos de la demo

Un CSV por tabla (`<tabla>.csv`) y el arte ASCII de cada artista en `arte/`. Se cargan con
`docker compose up -d --wait` (servicio `cargador`) o con `uv run python -m wikitunes.cargador`.

Formato:

- UTF-8, fila de encabezado con nombres de columnas de la tabla, separador coma, comillas según
  RFC 4180 (una comilla dentro de un texto se escribe `""`).
- Ids explícitos. Una celda vacía es `NULL`.
- En `genero.csv` y `sello.csv`, los padres van antes que los hijos.
- `arte_artista.csv` tiene las columnas `artista_id,archivo,estilo`; `archivo` es el nombre de un
  `.txt` dentro de `arte/` (finales de línea LF, máximo 80 columnas, sin tabuladores).

Cada carga **reemplaza** todo el contenido de la base. La procedencia de cada dato está en
[`obtencion_datos/`](../obtencion_datos/).
