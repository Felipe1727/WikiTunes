# Propuesta: correccion-consultas-sql

## Por qué

El SQL actual tiene tres problemas concretos, que se justifican uno por uno y que los datos de la demo harían visibles:

1. **La vista `v_participacion_persona` atribuye canciones de más.** Une la membresía con los créditos del artista sin mirar fechas, así que Pete Best y Stuart Sutcliffe "participarían" en *Hey Jude* y Adrian Belew en el King Crimson de 1969. Con una demo que incluye a propósito a los primeros Beatles y todas las formaciones de King Crimson, el defecto se vería en casi cada consulta.
2. **`sp_canciones_de_persona` busca con `LIKE '%x%'`.** No puede usar índices y además mezcla personas: "Lennon" encontraría a cualquier Lennon. La CLI elige a la persona con autocompletado y ya conoce su nombre exacto.
3. **No hay forma de ver el historial completo de integrantes de un artista.** `sp_integrantes_en_fecha` solo filtra por una fecha, y `artista.nombre` no es único, así que los procedimientos que buscan por nombre son ambiguos.

## Qué cambia

- **Índices.** Índice `UNIQUE` en `artista.nombre`, e índices (no únicos) en `persona.nombre_conocido` y `persona.nombre_legal`.
- **`sp_canciones_de_persona`** busca por igualdad en `nombre_conocido` o `nombre_legal`. **BREAKING:** una búsqueda parcial ("McCartney") ya no devuelve filas; hay que pasar el nombre exacto.
- **`v_participacion_persona`** aplica la regla aprobada en el roadmap: *x* participó en *c* vía *y* si *y* está acreditado en *c*, *x* es integrante de *y* (en algún periodo) y además (*x* tiene un crédito propio en *c* **o** era integrante de *y* en la fecha de salida de *c*). La fecha de salida es la del primer álbum que contiene la canción. La rama de créditos individuales no cambia.
- **Procedimiento nuevo `sp_historial_integrantes(p_artista)`**, con todas las membresías del artista.
- **Diagrama ER:** `artista.nombre` se marca como `UK`.

## Capacidades

### Capacidades nuevas
- `participacion-persona`: qué canciones se atribuyen a una persona y por qué vía, y cómo se busca a la persona.
- `integrantes-artista`: identificación única de un artista por nombre e historial completo de sus integrantes.

### Capacidades modificadas
- `entorno-base-datos`: el primer arranque crea también `sp_historial_integrantes`.

## Impacto

- `Diagrama/musica_schema_mysql.sql` (índices y vista), `procedimientos_almacenados/musica_procedimientos_mysql.sql`, el `.mmd` y el `.png`.
- Si hay nombres de artista duplicados, ahora fallan al cargar los datos. Ningún dato real de la demo se repite.
- Las bases locales deben reinicializarse con `docker compose down -v`.
