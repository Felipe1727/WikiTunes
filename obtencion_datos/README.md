# Obtención de los datos

Este directorio documenta **de dónde sale cada dato** de la demo (`datos/`) y con qué convenciones
se registró. La regla principal es: **no se inventa nada**. Si un dato no se puede respaldar con
una fuente, no entra; si las fuentes se contradicen y no se puede resolver, se detiene el trabajo
y se reporta.

## Contenido

| Ruta | Qué es |
|---|---|
| `README.md` | Metodología y convenciones (este archivo) |
| `fuentes.csv` | Una fila por dato respaldado: `tabla,id,url,campos,nota` |
| `crudo/` | Respuestas JSON de MusicBrainz guardadas tal cual (`<mbid>.json`), para reproducir sin red |
| `scripts/musicbrainz.py` | Descarga un lanzamiento por MBID, lo guarda en `crudo/` e imprime un borrador del tracklist |

## Fuentes permitidas

1. **MusicBrainz** (https://musicbrainz.org): tracklists, duraciones, fechas de lanzamiento, sellos
   y créditos de grabación. Es la fuente principal para todo lo numérico.
2. **Wikipedia** (en inglés o en español): membresías y sus fechas, datos biográficos (nombre
   legal, nacimiento, fallecimiento, ciudad), géneros (infobox) y créditos de composición y
   producción.
3. **Discogs** (https://www.discogs.com): solo para confirmar créditos o ediciones cuando las dos
   anteriores no alcanzan.

Cada dato usado se registra en `fuentes.csv`. En `campos` se listan las columnas que respalda la
fuente (por ejemplo `fecha_inicio;fecha_fin`), y en `nota`, cualquier aproximación o decisión.

## Cómo se obtiene cada tipo de dato

| Dato | Fuente | Cómo |
|---|---|---|
| Tracklist, número de disco y pista | MusicBrainz | `scripts/musicbrainz.py <mbid>` sobre la **edición de referencia** |
| Duración de cada canción | MusicBrainz | Milisegundos de la pista, redondeados al segundo más cercano |
| Fecha de lanzamiento y sello | MusicBrainz | Campos `date` y `label-info` del lanzamiento |
| Tipo de álbum | MusicBrainz | Tipo primario del *release group* (Album, Single, EP) y secundario (Compilation) |
| Membresías (rol, inicio, fin) | Wikipedia | Sección de integrantes del artista, con la URL citada |
| Personas (nombres, fechas, ciudad) | Wikipedia | Infobox de la persona |
| Compositores y productores | Wikipedia / MusicBrainz | Créditos del álbum o de la canción |
| Géneros | Wikipedia | Infobox del álbum, del artista o de la canción (ver reglas abajo) |

## Convenciones

### Edición de referencia

Cada álbum se toma de **una sola edición**: la original del Reino Unido o, si no aplica, la del
país de origen del artista. Se identifica por su MBID, que queda en `fuentes.csv` (`tabla=album`).

### Fechas aproximadas

Si la fuente da el día exacto, se usa. Si solo da el mes, se usa el **día 1** de ese mes; si solo
da el año, el **1 de enero**. En ambos casos la fila de `fuentes.csv` lo indica en `nota`
("fecha aproximada: solo mes"). La interfaz muestra los periodos de membresía en años.

### Regla de versiones

- La **misma grabación**, aunque esté remasterizada, es **la misma fila** en `cancion`, con la
  duración de su primer lanzamiento. Por eso las canciones de la compilación *1* que ya están en
  otros álbumes de la demo reutilizan esas filas.
- Una **mezcla o edición distinta, con otra duración** (por ejemplo *Get Back* o *Let It Be* en
  versión de single y de LP) es **otra fila** con el mismo título.

### Regla de participación

La vista `v_participacion_persona` considera que la persona *x* participó en la canción *c* vía el
artista *y* si *y* está acreditado en *c*, *x* fue integrante de *y* y además:

- *x* tiene un crédito propio en *c* (compositor, productor...), **o**
- *x* era integrante de *y* en la **fecha de salida** de *c*, que es la fecha del **primer** álbum
  que la contiene.

"Vía banda" significa "era integrante cuando salió la canción", no necesariamente "tocó en ella".

### Fin de The Beatles y la salida de Lennon

Las membresías de John Lennon, Paul McCartney, George Harrison y Ringo Starr en The Beatles
terminan el **1970-04-10**, el día del anuncio público de la separación. John Lennon comunicó en
privado su salida en **septiembre de 1969**; esa fecha **no** se usa como fin de su membresía, para
que *Abbey Road* (26 de septiembre de 1969) se le atribuya. Consecuencia aceptada: en las pistas que
solo están en el LP *Let It Be* (mayo de 1970), la participación sale únicamente de los créditos.

### Créditos con nombre variante

Si un lanzamiento acredita una variante del nombre de un artista de la base (por ejemplo
"Paul McCartney & Wings" para *Band on the Run*), se usa ese artista (Wings) y el crédito original
se anota en `fuentes.csv`.

### Artistas y personas

- Solo son **artistas** los de la lista aprobada en el roadmap. Los integrantes de Wings, Plastic
  Ono Band y Traveling Wilburys son **personas**.
- Cada artista solista tiene una fila de `membresia` con su persona.

### Árbol de géneros

1. Nombres en español, como en Wikipedia en español. Si allí el término está en inglés, se deja en
   inglés.
2. Cada género tiene un solo padre. Los casos ambiguos se deciden y se anotan aquí.
3. `album_genero` y `artista_genero` salen del infobox de Wikipedia. `cancion_genero` solo se llena
   cuando la canción tiene un artículo que indica su género.
4. Un género de la fuente que no está en el árbol se asigna al nodo más cercano y se anota aquí. El
   árbol no crece. Los nodos que nadie usa se quitan, siempre que siga habiendo un camino de tres
   niveles.

## Uso del script de MusicBrainz

```bash
uv run python obtencion_datos/scripts/musicbrainz.py <mbid> [<mbid> ...]
```

- Si `crudo/<mbid>.json` ya existe, se usa sin conectarse a la red. Con `--refrescar` se vuelve a
  descargar.
- Respeta el límite de MusicBrainz (como máximo 1 petición por segundo) y se identifica con un
  User-Agent propio.
- Imprime el título, la fecha, el país, el sello, el tipo y un borrador del tracklist con
  disco, pista, título, duración en segundos y MBID de la grabación. Es un **borrador**: los CSV se
  escriben a partir de él y se registran en `fuentes.csv`.
