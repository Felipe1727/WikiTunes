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

## Cómo se obtuvieron los datos de The Beatles (y proyectos en solitario)

1. **MusicBrainz:** se buscaron los *release groups* de los 12 lanzamientos y, dentro de cada uno, la
   edición de referencia. Se descargaron con `scripts/musicbrainz.py` y están en `crudo/`.
2. **Wikipedia en inglés:** el wikitext de cada artículo (personas, bandas, álbumes y canciones) se
   leyó con la API de MediaWiki. Cada fila de `fuentes.csv` enlaza a la **revisión exacta**
   consultada (`oldid`), así la fuente no cambia aunque el artículo se edite.
3. **Wikipedia en español:** se comprobó que el nombre de cada género del árbol existe como artículo.

### Ediciones de referencia elegidas

| Lanzamiento | Edición | Nota |
|---|---|---|
| *Magical Mystery Tour* | EP doble, Reino Unido, 1967-12-08, estéreo | |
| *Get Back* / *Don't Let Me Down* | Single, Reino Unido, 1969-04-11 | Acreditado a «The Beatles with Billy Preston» |
| *Give Peace a Chance* / *Remember Love* | Single, Reino Unido, 1969-07-04 | |
| *Abbey Road* | LP, Reino Unido, 1969-09-26 | |
| *Let It Be* | LP, Reino Unido, 1970-05-08 | |
| *My Sweet Lord* / *What Is Life* | Single, Reino Unido, 1971-01-15 | En EE. UU. salió antes con otra cara B |
| *Another Day* / *Oh Woman, Oh Why* | Single, Reino Unido, 1971-02-19 | |
| *Imagine* | LP, Reino Unido, 1971-10-08 | En EE. UU. salió el 9 de septiembre |
| *Ringo* | LP, Reino Unido, 1973-11-23 | |
| *Band on the Run* | LP, Reino Unido, 1973-12-07 | Sin «Helen Wheels» (solo en la edición de EE. UU.) |
| *Traveling Wilburys Vol. 1* | LP, **EE. UU.**, 1988-10-18 | No hubo edición original británica; la banda es de Los Ángeles |
| *1* | Compilación, Reino Unido, 2000-11-13 | |

Los títulos se copian **tal cual** de MusicBrainz, incluidas las comillas tipográficas
(«Maxwell’s Silver Hammer»).

### Misma grabación en varios lanzamientos

- MusicBrainz identifica como la misma grabación *Something* y *Come Together* (*Abbey Road* y *1*)
  y *The Long and Winding Road* (*Let It Be* y *1*).
- El *Get Back* de *1* es la **versión del single** (artículo «Get Back» de Wikipedia), aunque
  MusicBrainz la registra con otro id: se reutiliza la fila del single.
- *Let It Be* en *1* es la versión del single y *Get Back* en el LP *Let It Be* es otra mezcla: ambas
  son filas distintas de sus otras versiones (regla de versiones).

### Créditos

- **Compositores:** los que figuran en la edición de referencia.
  - Las canciones acreditadas a Lennon–McCartney tienen a los dos como compositores, aunque la
    fuente indique que la escribió solo uno.
  - *Give Peace a Chance* se acredita a Lennon–McCartney (crédito original; luego pasó a Lennon).
  - *Imagine* se acredita solo a Lennon (crédito original del LP; Yoko Ono fue reconocida como
    coautora en 2017).
  - Las canciones de *Traveling Wilburys Vol. 1* están acreditadas a la banda: se registran sus cinco
    integrantes como compositores.
  - *Maggie Mae* es tradicional: no tiene compositor y los cuatro Beatles figuran como arreglistas.
- **Productores:** los del artículo de la canción, si trata de esa grabación; si no, los del álbum.
  En todas las pistas del LP *Let It Be*, Phil Spector (productor del álbum).
- **Featuring:** Billy Preston en *Get Back* y *Don't Let Me Down*.

### Personas, artistas y lugares

- Si la fuente no da un nombre de nacimiento distinto, `nombre_legal` es el nombre conocido.
- Las ciudades se escriben en español (Londres, Edimburgo, Nueva York, Tokio, Madrás). Los barrios
  se asignan a su ciudad (Lewisham y Stepney → Londres; Tyseley → Birmingham).
- Los artistas solistas tienen una membresía sin fechas (la persona es el artista) y no tienen año de
  formación ni ciudad de origen.
- Plastic Ono Band: solo se registran como integrantes Lennon y Ono, los únicos permanentes de la
  etapa original (1969–1974). Los músicos de cada formación eran invitados.

### Correspondencia de géneros

| Género en la fuente | Nodo del árbol |
|---|---|
| beat, Merseybeat, power pop, jangle pop, soft rock | Pop rock |
| psychedelia, acid rock | Rock psicodélico |
| psychedelic pop | Pop psicodélico |
| folk, folk-pop | Folk rock |
| country rock, swamp rock | Roots rock |
| blues rock, glam rock, instrumental rock | Rock |
| chamber pop | Pop barroco |
| art pop, progressive pop, jazz pop | Pop |
| experimental | Rock experimental |

**Se omiten**, porque no hay ningún nodo razonablemente cercano: blues, country blues, R&B, soul,
blue-eyed soul, orchestral soul, Afro-soul, funk, gospel, doo-wop, swamp pop, boogie-woogie,
music hall, vaudeville-rock, bagatelle, children's music, skiffle, country, honky tonk, ballad,
bossa nova, Indian classical, classical, electronic, conceptual art y avant-garde.

En las versiones de canciones ajenas (*Have You Seen My Baby?*, *You're Sixteen*), el artículo
describe la grabación original de otro artista: esas canciones quedan sin género.

### Consecuencias de la regla de participación

- **LP *Let It Be* (mayo de 1970):** sale después del 1970-04-10. En sus pistas exclusivas, la
  participación solo sale de los créditos (por ejemplo, Ringo Starr no figura en *Two of Us*).
- **Compilación *1* (2000):** las canciones que solo están en *1* (sus singles originales no forman
  parte de la demo) también salen después del fin de la banda. Solo figuran sus compositores
  (Lennon y McCartney): Ringo Starr y George Harrison no aparecen, por ejemplo, en *Hey Jude*. Es
  una consecuencia de la regla aprobada; las canciones de *1* que ya estaban en *Abbey Road* o
  *Let It Be* mantienen su fecha original.

## Cómo se obtuvieron los datos de King Crimson

1. **MusicBrainz:** ediciones originales del Reino Unido de *In the Court of the Crimson King*
   (Island, 1969-10-10), *Red* (Island, 1974-09-27), *Discipline* (E.G., 1981-09-22) y *VROOOM*
   (Discipline Global Mobile, 1994-11-08). Las cuatro están en `crudo/`.
   - *Red* figura en MusicBrainz también como «Compilation». Se registra como LP (álbum de estudio).
   - La primera pista de *VROOOM* es una pieza sin título de 0:19. Wikipedia la describe como una
     «Intro» sin listar de las ediciones originales, y MusicBrainz la registra como «[untitled]».
2. **Membresías:** la lista «List of King Crimson members» solo da años, así que se usan las
   **fechas exactas de su línea de tiempo** (EasyTimeline, `dd/mm/yyyy`), uniendo las barras de cada
   persona en periodos. Con solo años, la formación de 1972–1974 habría «terminado» el 1 de enero de
   1974, antes de *Red*. Excepciones:
   - Los cinco fundadores empiezan el **30 de noviembre de 1968**, la fecha de formación según el
     artículo «King Crimson». La línea de tiempo empieza en 1969 porque ahí empieza el gráfico.
   - Las membresías activas al final terminan el **31 de diciembre de 2021**, fin de la línea de
     tiempo y último año activo según el infobox. Ese mismo año se toma como disolución del artista.
3. **Créditos** (artículos de cada álbum):
   - Cuando la fuente separa música y letra (*In the Court...*: letra de Peter Sinfield;
     *Discipline*: letra de Adrian Belew), la música es `Compositor` y la letra `Letrista`. Las
     piezas instrumentales no tienen letrista.
   - Cuando la producción se acredita a «King Crimson», se registran como productores los integrantes
     de la banda en la fecha de lanzamiento, más los productores externos nombrados (Rhett Davies en
     *Discipline* y David Bottrill en *VROOOM*). En *Red*, el personal del álbum nombra a Fripp, Wetton
     y Bruford.
4. **Ids:** los datos de King Crimson usan ids propios (personas, artistas, membresías y álbumes desde
   101; canciones desde 201) para no mezclarse con los de The Beatles.

### Correspondencia de géneros (además de la tabla anterior)

| Género en la fuente | Nodo del árbol |
|---|---|
| post-progressive | Rock progresivo |
| symphonic rock | Rock sinfónico |
| progressive metal | Metal progresivo |
| jazz metal | Heavy metal |

Se omiten jazz rock, jazz-rock, free improvisation, funk rock y dance-rock.

Con los datos de King Crimson, **todos los nodos del árbol de géneros tienen al menos una
asignación**, así que no se quitó ninguno.

## Arte ASCII de los artistas

El arte de cada artista (`datos/arte/*.txt`) se genera con `scripts/generar_arte.py`:

```bash
uv run python obtencion_datos/scripts/generar_arte.py
```

Cada logo parte de una fuente de [pyfiglet](https://github.com/pwaller/pyfiglet) y se completa con
el rasgo que identifica al artista. Cuando el artista tiene una tipografía reconocible, el arte la
imita; si no, se diseña un estilo acorde. No se copia ningún logo ni imagen.

| Artista | Criterio | Base (pyfiglet) | Estilo Rich |
|---|---|---|---|
| The Beatles | Imita su logo: la **«T» alargada** (*drop-T*) que baja bajo la línea, con «THE» pequeño | `ansi_regular` | `bold white` |
| King Crimson | Sin tipografía única entre sus portadas: letras «ensangrentadas» en el **rojo carmesí** del nombre | `bloody` | `bold red` |
| John Lennon | Su **firma** manuscrita bajo sus **lentes redondos** | `script` | `bold bright_white` |
| Paul McCartney | Firma en cursiva y su **bajo Höfner** de violín | `smscript` | `bold cyan` |
| George Harrison | Letras inclinadas entre guirnaldas, por su vínculo con la **música de la India** | `smslant` | `bold magenta` |
| Ringo Starr | Juego con el **«star»** de su nombre: letras de cartel estelar entre estrellas | `starwars` | `bold yellow` |
| Plastic Ono Band | Banda **conceptual**: minúsculas dentro de un marco, minimalista | `smslant` | `bold white` |
| Wings | El nombre entre dos **alas** | `ansi_shadow` | `bold bright_blue` |
| Traveling Wilburys | Rótulo de **marquesina de época** entre bordes de carretera (el «viaje» del nombre) | `broadway_kb` | `bold yellow` |
| Billy Preston | El nombre sobre un **teclado de piano**, su instrumento | `small_shadow` | `bold bright_magenta` |

Reglas que comprueban las pruebas (`tests/test_arte.py`): todo artista tiene arte; máximo 80
columnas; sin tabuladores; solo caracteres de una columna (ASCII, bloques `█ ▀ ▄ ░ ▒ ▓` y marcos
`╔ ═ ┌ ─`); finales de línea LF; estilo válido de Rich; y los archivos coinciden con lo que genera el
script.
