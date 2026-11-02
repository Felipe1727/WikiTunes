# Roadmap

Roadmap aprobado en la Fase 1 (exploración) el 2026-11-02. Es la fuente de verdad para el alcance,
las pautas y el orden de trabajo de la Fase 2.

## Objetivos

WikiTunes es una **aplicación de línea de comandos (CLI) en línea, muy estética**, para consultar un
catálogo musical guardado en MySQL. No es un reproductor ni tiene usuarios: es un explorador de
información sobre artistas, personas, álbumes, canciones, géneros y créditos.

1. **Arranque animado:** un conejito tierno con audífonos escuchando música, en arte ASCII, con una
   animación corta al estilo del arranque de Claude Code (notas que aparecen, cabeceo al ritmo o
   aparición progresiva) que desemboca en el menú principal "¿Qué quieres consultar?".
2. **Consultas centrales** (procedimientos almacenados):
   - canciones en las que participó una persona (`sp_canciones_de_persona`);
   - árbol de un género con sus subgéneros (`sp_subgeneros`);
   - tracklist de un álbum con intérpretes y duración total (`sp_tracklist`, dos resultados);
   - integrantes de un artista en una fecha (`sp_integrantes_en_fecha`);
   - historial completo de integrantes (nuevo `sp_historial_integrantes`).
3. **Fichas y navegación:** ficha de artista, de persona y de canción, y la vista de un género con
   sus artistas y álbumes. Desde cada resultado se puede saltar a otro (canción → álbum,
   integrante → sus otras bandas, género → artista).
4. **Arte ASCII por artista:** guardado en una tabla nueva y mostrado como encabezado en toda
   consulta cuyo protagonista sea un artista. Las demás consultas generan su encabezado al vuelo
   con pyfiglet.
5. **Demo con datos reales y verificables:** The Beatles (con los proyectos en solitario de sus
   integrantes) y King Crimson (con todas sus formaciones), cargados desde CSV, con la procedencia
   de cada dato documentada.

## Pautas

### Idioma

- **Todo en español, sin excepciones:** specs, propuestas, diseños, tareas, documentación, README,
  comentarios, nombres de variables, funciones, clases, módulos y archivos, mensajes de commit
  (descripción en español con prefijo Conventional Commits), PRs, textos de la interfaz, mensajes
  de error y logs.
- Solo queda en inglés lo que no se puede cambiar: palabras reservadas, nombres de librerías y
  APIs externas, y los valores ENUM ya existentes en el esquema (`'Compilation'`, `'Live'`...),
  que la interfaz traduce al mostrarlos ("Compilación", "En vivo"...).
- Los datos conservan sus nombres reales (títulos de canciones y álbumes, nombres de artistas).
  Los nombres de géneros van en español (ver "Árbol de géneros").

### Stack

- **Python** `>= 3.12` (desarrollo en 3.14; la CI prueba 3.12 y 3.14).
- **uv** para dependencias y entorno: `pyproject.toml` y `uv.lock` versionado. El comando
  `wikitunes` se declara en `[project.scripts]`. Código en `src/wikitunes/`.
- Dependencias de ejecución: `rich` (render, tablas, árboles, `Live` para la animación),
  `questionary` (menús y autocompletado; usa prompt_toolkit), `pyfiglet` (encabezados generados),
  `mysql-connector-python` (conector, decisión ya tomada), `python-dotenv`.
- Dependencias de desarrollo: `pytest`, `ruff`.
- **No** se usa Textual: la app es una CLI en línea (el historial queda en el scrollback).

### Base de datos

- El esquema (`Diagrama/musica_schema_mysql.sql`) y los procedimientos
  (`procedimientos_almacenados/musica_procedimientos_mysql.sql`) son la fuente de verdad. Se editan
  en su lugar; no se mueven de directorio. Los únicos cambios aprobados son:
  1. **Tabla `arte_artista`** (spec `tabla-arte-artista`): `artista_id INT` PK y FK a `artista` con
     `ON DELETE CASCADE`, `arte TEXT NOT NULL` (utf8mb4), `estilo VARCHAR(40) NULL` (estilo Rich,
     p. ej. `"bold red"`).
  2. **Correcciones justificadas** (spec `correccion-consultas-sql`):
     - Índice **UNIQUE** en `artista.nombre` (acelera la búsqueda y elimina la ambigüedad de los
       procedimientos que buscan por nombre de artista).
     - Índices (no únicos) en `persona.nombre_conocido` y `persona.nombre_legal`.
     - `sp_canciones_de_persona` busca por **igualdad** (`nombre_conocido = p_nombre OR
       nombre_legal = p_nombre`), sin `LIKE`, para que use los índices.
     - `v_participacion_persona` corrige el defecto actual (unía membresía y créditos del artista
       sin mirar fechas, así Pete Best "participaba" en *Hey Jude*). **Regla aprobada:**
       una persona *x* participó en la canción *c* vía el artista *y* si *y* está acreditado en *c*
       (`credito_artista`) **y además** (*x* tiene un crédito propio en *c* (`credito_persona`)
       **o** *x* era integrante de *y* en la fecha de salida de *c*). La fecha de salida de *c* es
       la fecha del **primer** álbum que la contiene (`MIN(album.fecha_lanzamiento)` vía
       `album_cancion`); una canción sin fecha no cumple la condición de membresía. Los créditos de
       una persona que no es integrante del artista acreditado siguen saliendo como
       `(crédito individual)`. Semántica documentada: "vía banda" significa "era integrante cuando
       salió la canción", no necesariamente "tocó en ella".
     - Nuevo `sp_historial_integrantes(p_artista VARCHAR(150))`: todas las membresías del artista
       (persona, rol, fecha de inicio, fecha de fin), ordenadas por fecha de inicio y persona.
  Cualquier otro cambio al esquema o a los procedimientos queda fuera de alcance.
- El diagrama ER se mantiene sincronizado: `Diagrama/musica_er.mmd` y `Diagrama/musica_er.png`
  (generado con `scripts/generar_diagrama.sh` usando la imagen Docker `minlag/mermaid-cli`; no se
  instala Node).
- **Docker Compose** con `mysql:8.4`. Los scripts de esquema, tabla de arte y procedimientos se montan
  en `/docker-entrypoint-initdb.d`. El host usa SELinux en modo *Enforcing*: todo volumen montado
  lleva el sufijo `:z`.
- Un servicio de un solo uso, `cargador`, espera a que la base esté sana y carga los datos de la
  demo, de modo que `docker compose up -d --wait` deja la base lista.
- La app se conecta con un usuario que solo tiene permisos de `SELECT` y `EXECUTE` sobre `musica`.
- Configuración por variables de entorno en un `.env` ignorado por git, con un `.env.ejemplo`
  versionado. Nombres en español con prefijo `WIKITUNES_` (p. ej. `WIKITUNES_BD_HOST`,
  `WIKITUNES_BD_PUERTO`, `WIKITUNES_BD_USUARIO`, `WIKITUNES_BD_CLAVE`, `WIKITUNES_BD_NOMBRE`).

### Arquitectura de la aplicación

```
ui/ (Rich + questionary + pyfiglet)  -->  consultas (devuelven dataclasses)  -->  conexión (mysql-connector)
```

- Una única conexión por sesión (no hace falta un pool).
- Los procedimientos se llaman con `cursor.callproc()` y sus resultados se recorren con
  `cursor.stored_results()`. Las columnas se mapean con `cursor.description` (históricamente
  `stored_results()` ignora `dictionary=True`); se verifica con la versión fijada del conector.
  `sp_tracklist` devuelve dos resultados: pistas y resumen. El `SEC_TO_TIME` llega como `timedelta`
  y se formatea en la presentación.
- Los listados de apoyo (para el autocompletado y las fichas) son `SELECT` simples desde la app.
- Para `sp_canciones_de_persona`, la app elige a la persona en el autocompletado, llama al
  procedimiento con su nombre exacto y filtra las filas por la columna `persona`.
- Manejo de errores:
  - base caída (p. ej. errno 2003): excepción propia con un mensaje amable en español que sugiere
    `docker compose up -d`, nunca un traceback;
  - consulta sin resultados: un panel "Sin resultados";
  - Ctrl+C: salida limpia.

### Interfaz (CLI en línea)

- **Arranque:** animación con Rich `Live` de 2 a 3 segundos. Se salta con cualquier tecla, se
  desactiva con `--sin-animacion` y se desactiva sola si no hay TTY o si está definida `NO_COLOR`.
  Desemboca en el menú "¿Qué quieres consultar?".
- **Selección sin ids:** artistas, personas, álbumes y géneros se eligen con autocompletado
  (`questionary.autocomplete`). Los nombres se cargan una vez y se filtran en Python por
  subcadena, de modo que "McCartney" encuentra "Paul McCartney".
- **Encabezados:** en las consultas con un artista como protagonista (integrantes en una fecha,
  historial de integrantes, ficha de artista) va primero el arte ASCII guardado en la base, con su
  `estilo`, y después el resultado. En las demás (tracklist, árbol de géneros, persona, canción) el
  encabezado se genera al vuelo con pyfiglet (p. ej. con el título del álbum). Si el arte no cabe en
  la terminal, se usa el nombre del artista con pyfiglet.
- **Resultados:** tablas Rich con estilo; el árbol de géneros con `rich.tree`. Los periodos de
  membresía se muestran como años ("1972–1974"; "1969–" si sigue abierto).
- **Navegación:** después de cada resultado aparece el menú contextual "¿Y ahora?" con saltos
  (p. ej. "Ver ficha de Bill Bruford", "Ver álbum *Abbey Road*", "Cambiar fecha"), "Volver" (una
  pila de pantallas) y "Menú principal".
- **Fichas:**
  - *Artista:* arte, tipo, años de formación y disolución, ciudad y país de origen, géneros,
    discografía (vía `album_artista`) e historial de integrantes.
  - *Persona:* nombre legal y conocido, nacimiento (fecha y ciudad), fallecimiento, artistas de los
    que fue integrante (con periodo) y acceso a sus canciones (`sp_canciones_de_persona`).
  - *Canción:* duración, intérpretes (principal y featuring), créditos individuales (compositor,
    productor...), géneros y álbumes en los que aparece.
  - *Género:* el árbol (`sp_subgeneros`) y, al elegir un nodo, los artistas y álbumes de ese género
    y de sus subgéneros.

### Datos de la demo

- **CSV**, uno por tabla, en `datos/<tabla>.csv`: UTF-8, fila de encabezado con los nombres de las
  columnas, separador coma, comillas según RFC 4180, ids explícitos y celda vacía = `NULL`. El
  cargador respeta el orden de las llaves foráneas y, en las tablas autorreferenciadas (`genero`,
  `sello`), pone los padres antes que los hijos. Todo se carga en una sola transacción.
- **Arte ASCII** (formato alternativo para esa tabla): un archivo por artista en
  `datos/arte/<nombre>.txt`, y `datos/arte_artista.csv` con `artista_id,archivo,estilo`. Reglas:
  - se permiten ASCII imprimible y caracteres Unicode de bloque y de marcos de ancho 1
    (`█ ▀ ▄ ░ ╔ ═`...);
  - se prohíben emojis, caracteres de ancho doble y tabuladores;
  - finales de línea LF, forzados con `.gitattributes`;
  - como máximo 80 columnas.
  Cada arte imita la tipografía característica del artista (p. ej. el logo de The Beatles con la
  "T" alargada); si no tiene una reconocible, se diseña una acorde con su estilo.
- **Selección aprobada.** Todo álbum que entra, entra con su **tracklist completo**.
  - The Beatles:
    - *Abbey Road* (LP, 1969);
    - *Magical Mystery Tour* (EP doble del Reino Unido, 1967);
    - *Let It Be* (LP, 1970);
    - single *Get Back* / *Don't Let Me Down* (1969, "The Beatles with Billy Preston": el featuring);
    - *1* (compilación, 2000).
  - John Lennon: *Imagine* (LP, 1971). Plastic Ono Band: single *Give Peace a Chance* (1969).
  - Paul McCartney: *Band on the Run* (LP, 1973, como Wings) y el single en solitario
    *Another Day* (1971), para que McCartney aparezca con The Beatles, con Wings y en solitario.
  - George Harrison: single *My Sweet Lord* (1970). Traveling Wilburys: *Traveling Wilburys Vol. 1*
    (LP, 1988).
  - Ringo Starr: *Ringo* (LP, 1973).
  - King Crimson:
    - *In the Court of the Crimson King* (LP, 1969);
    - *Red* (LP, 1974);
    - *Discipline* (LP, 1981);
    - *VROOOM* (EP, 1994).
- **Artistas** (cada uno con su arte): The Beatles, John Lennon, Paul McCartney, George Harrison,
  Ringo Starr, Plastic Ono Band, Wings, Traveling Wilburys, Billy Preston y King Crimson.
  - Los integrantes de Wings, Plastic Ono Band y Traveling Wilburys (Linda McCartney, Denny Laine,
    Yoko Ono, Bob Dylan, Roy Orbison, Tom Petty, Jeff Lynne...) son **personas**, no artistas.
  - Cada artista solista tiene su fila de `membresia` con la persona correspondiente.
- **Membresías:**
  - The Beatles incluye a Pete Best y a Stuart Sutcliffe con sus fechas reales.
  - King Crimson incluye todas sus formaciones con fechas de entrada y salida. No se incluyen otros
    proyectos de Robert Fripp ni de los demás integrantes.
  - **Convención aprobada:** las membresías de John Lennon, Paul McCartney, George Harrison y Ringo
    Starr en The Beatles terminan el **1970-04-10** (anuncio público de la separación). La salida
    privada de Lennon (septiembre de 1969) se anota en `obtencion_datos/`. Consecuencia aceptada:
    en las pistas que solo están en el LP *Let It Be* (mayo de 1970), la participación sale
    únicamente de los créditos.
- **Créditos:** cada canción tiene al menos un crédito de artista `Principal` y sus créditos de
  compositor (p. ej. Lennon–McCartney como dos filas `Compositor`) y de productor
  (`credito_persona`).
- **Regla de versiones (aprobada):** la misma grabación, aunque esté remasterizada, es la misma
  fila en `cancion`, con la duración de su primer lanzamiento. Una mezcla o edición distinta, con
  otra duración (p. ej. *Get Back* o *Let It Be* en versión de single y de LP), es otra fila con el
  mismo título.
- **Créditos con nombre variante:** si el lanzamiento acredita una variante del nombre de un artista
  de la base (p. ej. "Paul McCartney & Wings"), se usa ese artista y el crédito original se anota en
  `obtencion_datos/`.
- **Edición de referencia** de cada álbum: la original del Reino Unido (o, si no aplica, la del país
  de origen del artista), identificada por su MBID de MusicBrainz.

### Árbol de géneros (aprobado)

```
Rock
+-- Rock and roll
+-- Pop rock
+-- Rock psicodélico
+-- Folk rock
+-- Roots rock
|   +-- Heartland rock
+-- Hard rock
|   +-- Heavy metal
+-- Art rock
|   +-- Rock experimental
+-- Rock progresivo
    +-- Rock sinfónico
    +-- Metal progresivo
Pop
+-- Pop psicodélico
+-- Pop barroco
New wave
```

1. Los nombres van en español, con el nombre que usa Wikipedia en español. Si allí se usa el
   término en inglés, se queda en inglés.
2. Cada género tiene un solo padre. En los casos ambiguos se decide y se anota en
   `obtencion_datos/`.
3. `album_genero` y `artista_genero` se toman del infobox de Wikipedia. `cancion_genero` solo se
   llena cuando la canción tiene un artículo que indica su género; si no, queda sin asignar.
4. Un género de la fuente que no esté en el árbol se asigna al nodo más cercano y se anota. El árbol
   no crece. Los nodos que no use ninguna asignación se quitan, siempre que siga habiendo algún
   camino de tres niveles.

### Procedencia de los datos (sin inventar nada)

- Directorio `obtencion_datos/`:
  - `README.md`: metodología y convenciones (fechas aproximadas, regla de versiones, regla de
    participación, nota sobre Lennon, decisiones del árbol de géneros);
  - `fuentes.csv`: entidad, id, URL de la fuente, campos que respalda y nota;
  - `crudo/`: respuestas JSON de MusicBrainz guardadas (para reproducir sin red);
  - `scripts/`: script que consulta la API de MusicBrainz por MBID y genera borradores de CSV.
- Las duraciones (de ms a segundos, redondeadas), los tracklists y las fechas de lanzamiento salen
  del script de MusicBrainz. Las membresías, los créditos y los datos biográficos se curan a mano,
  cada uno con su cita (Wikipedia, MusicBrainz o Discogs).
- Fechas: si la fuente da el día exacto, se usa. Si solo da el mes o el año, se usa el día 1 (o el
  1 de enero) y se anota como aproximada en `fuentes.csv`.
- **Si una fuente no se puede consultar (sin red, bloqueada) o las fuentes se contradicen sin
  resolverse, la ejecución se detiene y lo reporta. Nunca se completan datos de memoria.**

### Pruebas y calidad

- pytest. Las pruebas unitarias no necesitan base de datos. Las de integración llevan la marca
  `integracion` y usan la base de Docker Compose. Si la base no responde, se **saltan** en local
  con un aviso y **fallan** si está definida `WIKITUNES_EXIGIR_BD=1` (que la CI define).
- El render de la interfaz se prueba con `rich.console.Console(record=True)` / `export_text()`.
- Los datos tienen pruebas de integridad: tracklists completos y comparados con `crudo/`, ninguna
  membresía se solapa de forma inválida, todo artista tiene arte, todos los tipos de álbum exigidos
  existen y las consultas devuelven los hechos esperados.
- Los datos ficticios solo se permiten en `tests/` para probar el SQL, y deben estar marcados como
  ficticios. Nunca van en `datos/`.
- ruff (`ruff check` y `ruff format --check`).
- **CI con GitHub Actions:** `docker compose up -d --wait`, lint y pruebas en Python 3.12 y 3.14.
- Comandos (también en `.claude/CLAUDE.md`):
  - Install: `uv sync`
  - Test: `docker compose up -d --wait && uv run pytest`
  - Lint: `uv run ruff check . && uv run ruff format --check .`
  - Build: `none`

## Fuera de alcance

- Usuarios, autenticación o cuentas.
- Reproducción de audio.
- Interfaz web, API HTTP o TUI a pantalla completa (Textual).
- Escritura desde la app: la CLI es de solo lectura.
- Cambios al esquema o a los procedimientos distintos de los listados en "Base de datos".
- Discografías completas. Fuera de la demo: The Quarrymen, la All-Starr Band de Ringo, los demás
  proyectos de Robert Fripp y de otros integrantes de King Crimson, y artistas que no estén en la
  lista aprobada.
- Consultas sobre sellos y estadísticas o rankings.
- Reorganizar los directorios `Diagrama/` y `procedimientos_almacenados/`.

## Specs (ejecutar en orden)

- [x] `base-proyecto` — Esqueleto en Python, MySQL con Docker Compose y CI.
  - Aceptación:
    - Existen `pyproject.toml`, `uv.lock`, `src/wikitunes/` con módulos en español, `tests/`,
      `.gitignore` (con `.env`, `.venv/` e `.idea/`), `.gitattributes`, `.env.ejemplo` y un
      `README.md` inicial en español.
    - `docker compose up -d --wait` levanta MySQL 8.4 con el esquema y los procedimientos actuales:
      16 tablas, 4 triggers, `v_participacion_persona` y los 4 procedimientos. Los volúmenes llevan
      `:z`. Existe un usuario de solo lectura (`SELECT` y `EXECUTE`).
    - Una prueba de humo de integración comprueba que existen esos objetos. Se salta si no hay base
      y falla con `WIKITUNES_EXIGIR_BD=1`.
    - `uv sync`, el lint y las pruebas pasan, y la CI de GitHub Actions está en verde en 3.12 y 3.14.
  - Depende de: —

- [x] `tabla-arte-artista` — Tabla nueva `arte_artista` en el esquema y en el diagrama ER.
  - Aceptación:
    - La tabla existe con la definición de "Base de datos" (PK/FK con `ON DELETE CASCADE`,
      `arte TEXT`, `estilo VARCHAR(40) NULL`).
    - Se actualizan `musica_er.mmd` y `musica_er.png` (regenerado con
      `scripts/generar_diagrama.sh`).
    - Una prueba de integración guarda y lee arte de varias líneas con `\`, `"`, `'` y bloques
      Unicode y recupera exactamente lo mismo.
  - Depende de: `base-proyecto`

- [x] `correccion-consultas-sql` — Índices, búsqueda por igualdad, vista de participación corregida y `sp_historial_integrantes`.
  - Aceptación:
    - Índice UNIQUE en `artista.nombre` e índices en `persona.nombre_conocido` y
      `persona.nombre_legal`.
    - `sp_canciones_de_persona` busca por igualdad y `EXPLAIN` de la consulta equivalente muestra
      uso de índices.
    - `v_participacion_persona` aplica la regla aprobada, con pruebas sobre datos ficticios
      marcados como tales:
      - integrante en la fecha de salida: incluido;
      - integrante fuera de esa fecha y sin crédito: excluido;
      - fuera de esa fecha pero con crédito propio: incluido;
      - no integrante con crédito: sale como `(crédito individual)`;
      - canción en una compilación posterior: usa la fecha del primer álbum.
    - `sp_historial_integrantes` devuelve todas las membresías ordenadas, incluidas las de quien
      sale y vuelve (dos filas).
    - El `.mmd` y el `.png` reflejan los índices UNIQUE si el diagrama los representa. Cada cambio
      está justificado en la propuesta.
  - Depende de: `base-proyecto`

- [x] `cargador-datos` — Cargador de CSV y arte en Python, servicio `cargador` en Compose y el directorio `obtencion_datos/`.
  - Aceptación:
    - El cargador lee `datos/*.csv` y `datos/arte/*.txt` según las convenciones del roadmap, en el
      orden de las llaves foráneas y en una sola transacción. Si algo falla, no queda nada a medias
      y el mensaje de error en español indica el archivo y la fila.
    - El servicio `cargador` corre después de que la base esté sana. Con datos vacíos funciona.
    - `obtencion_datos/` existe con `README.md` (todas las convenciones de datos del roadmap),
      `fuentes.csv` (con su encabezado), `crudo/` y el script de MusicBrainz (con User-Agent
      identificable y respetando el límite de 1 petición por segundo).
    - Pruebas con CSV de ejemplo: celdas vacías como `NULL`, textos con comas, comillas y saltos de
      línea, y arte con barras invertidas.
  - Depende de: `tabla-arte-artista`, `correccion-consultas-sql`

- [ ] `datos-beatles` — Catálogos (países, ciudades, sellos, árbol de géneros) y la demo de The Beatles con sus proyectos en solitario.
  - Aceptación:
    - Están todos los álbumes aprobados de The Beatles, Lennon, Plastic Ono Band, McCartney, Wings,
      Harrison, Traveling Wilburys y Ringo, con su tracklist completo. Hay al menos un LP, un
      single, un EP y una compilación, y Billy Preston aparece como featuring.
    - Cada canción tiene crédito `Principal` y créditos de compositor, y donde la fuente lo indica,
      de productor.
    - Cada fila tiene su fuente en `obtencion_datos/fuentes.csv`, y una prueba compara duraciones,
      tracklists y fechas contra `obtencion_datos/crudo/`.
    - Hechos comprobados con pruebas:
      - `sp_integrantes_en_fecha('The Beatles', '1961-06-01')` incluye a Pete Best y a Stuart
        Sutcliffe;
      - con `'1963-01-01'` devuelve exactamente a los cuatro;
      - Lennon participa en las canciones de *Abbey Road* y no en *I Me Mine*;
      - Pete Best no tiene canciones;
      - McCartney aparece vía The Beatles, vía Wings y vía Paul McCartney;
      - las canciones reutilizadas en *1* son las mismas filas que en sus álbumes originales.
    - `sp_subgeneros('Rock')` recorre al menos tres niveles.
  - Depende de: `cargador-datos`

- [ ] `datos-king-crimson` — Todas las formaciones de King Crimson y sus álbumes aprobados.
  - Aceptación:
    - Están todas las membresías de King Crimson, con fechas de entrada y salida y su fuente.
    - Están *In the Court of the Crimson King*, *Red*, *Discipline* y *VROOOM* con su tracklist
      completo y sus créditos, y una prueba los compara contra `crudo/`.
    - Ninguna persona tiene membresías solapadas en el mismo artista.
    - `sp_integrantes_en_fecha('King Crimson', ...)` devuelve formaciones distintas en 1969, 1974,
      1981 y 1995.
    - No se incluyen otros proyectos de Fripp ni de los demás integrantes.
  - Depende de: `datos-beatles`

- [ ] `arte-artistas` — Arte ASCII para cada artista de la demo.
  - Aceptación:
    - Cada artista tiene su `datos/arte/<nombre>.txt` y su fila en `datos/arte_artista.csv` con un
      `estilo` acorde.
    - Las pruebas comprueban que todo artista de `artista.csv` tiene arte, que tiene como máximo 80
      columnas, que no hay tabuladores, emojis ni caracteres de ancho doble, y que los finales de
      línea son LF.
    - El arte de The Beatles imita su logo (la "T" alargada) y el de King Crimson su tipografía
      característica.
    - La procedencia o el criterio de diseño de cada arte queda en `obtencion_datos/README.md`.
  - Depende de: `datos-king-crimson`

- [ ] `capa-datos` — Conexión configurable y consultas tipadas sobre procedimientos y listados.
  - Aceptación:
    - La configuración se lee de las variables `WIKITUNES_BD_*` (con `.env`).
    - Hay funciones que devuelven dataclasses para los 5 procedimientos, incluidos los dos
      resultados de `sp_tracklist` y la duración total formateada.
    - Hay funciones para las fichas de artista, persona, canción y género (este con sus
      subgéneros), y los listados para el autocompletado.
    - Si la base está caída, se lanza una excepción propia con un mensaje en español.
    - Las pruebas de integración usan los datos de la demo.
  - Depende de: `arte-artistas`

- [ ] `cli-arranque` — Comando `wikitunes`, animación del conejito y menú principal.
  - Aceptación:
    - `uv run wikitunes` muestra la animación del conejito con audífonos (2 a 3 segundos,
      saltable con una tecla) y termina en "¿Qué quieres consultar?".
    - `--sin-animacion`, la ausencia de TTY y `NO_COLOR` la desactivan.
    - Si la base está caída, se muestra un aviso amable que sugiere `docker compose up -d`, sin
      traceback.
    - Ctrl+C sale sin traceback.
    - Hay pruebas de los fotogramas y del menú renderizados a texto.
  - Depende de: `capa-datos`

- [ ] `cli-consultas` — Las cinco consultas con autocompletado, encabezados y tablas con estilo.
  - Aceptación:
    - Las consultas de canciones de una persona, árbol de géneros, tracklist, integrantes en una
      fecha e historial de integrantes se hacen desde el menú, eligiendo con autocompletado y sin
      escribir ids. La fecha se valida (formato AAAA-MM-DD).
    - Las consultas de artista muestran primero su arte con su `estilo`. Las demás llevan un
      encabezado de pyfiglet. Si la terminal es estrecha, se usa el nombre con pyfiglet.
    - Los resultados van en tablas Rich y el árbol en `rich.tree`, con los enums traducidos y los
      periodos en años. Una consulta sin resultados muestra un panel "Sin resultados".
    - Hay pruebas de render a texto.
  - Depende de: `cli-arranque`

- [ ] `cli-fichas-navegacion` — Fichas de artista, persona, canción y género, y el menú "¿Y ahora?" con pila para volver.
  - Aceptación:
    - Las fichas muestran los campos listados en "Interfaz".
    - Después de cada resultado aparece "¿Y ahora?", con saltos contextuales, "Volver" y
      "Menú principal".
    - Recorridos probados: canción → álbum (tracklist); integrante → ficha de persona → otra banda;
      género → artista; tracklist → canción → otro álbum en el que aparece.
  - Depende de: `cli-consultas`

- [ ] `documentacion` — README completo en español.
  - Aceptación:
    - El README cubre requisitos, instalación (`uv sync`), levantar la base y cargar los datos,
      uso de `wikitunes` con ejemplos, arquitectura, el modelo de datos (enlace al diagrama ER),
      la procedencia de los datos (enlace a `obtencion_datos/`) y el resumen de decisiones.
    - Cada comando del README se ejecutó y funciona tal como está escrito.
  - Depende de: `cli-fichas-navegacion`
