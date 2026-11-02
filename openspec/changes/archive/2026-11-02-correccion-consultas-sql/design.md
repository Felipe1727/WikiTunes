# Diseño: correccion-consultas-sql

## Contexto

Ver `proposal.md`. Las canciones no tienen fecha propia; la única fecha disponible es `album.fecha_lanzamiento`, a través de `album_cancion`. Una canción puede estar en varios álbumes, como en la compilación *1*.

## Objetivos / No objetivos

**Objetivos:** aplicar la regla de participación aprobada sin añadir columnas, y hacer que las búsquedas por nombre sean exactas e indexables.

**No objetivos:** cambiar `sp_tracklist`, `sp_subgeneros` ni `sp_integrantes_en_fecha`. Tampoco se añaden columnas de fecha de grabación: se descartó en la exploración.

## Decisiones

### 1. La vista se reescribe; la rama de créditos individuales no se toca
La primera rama del `UNION` mantiene sus columnas (`persona_id`, `persona`, `cancion_id`, `cancion`, `via`, `rol`) y añade un `LEFT JOIN` a una tabla derivada con `MIN(al.fecha_lanzamiento)` por canción. El `WHERE` es:

```
EXISTS (crédito propio de p en c)
OR (fecha_salida IS NOT NULL
    AND (m.fecha_inicio IS NULL OR m.fecha_inicio <= fecha_salida)
    AND (m.fecha_fin    IS NULL OR m.fecha_fin    >= fecha_salida))
```

El `UNION` sin `ALL` elimina los duplicados que aparecen cuando una persona tiene varias membresías (si sale y vuelve).
- *Alternativa descartada:* una vista auxiliar `v_fecha_salida_cancion`. Añadiría un objeto más al esquema sin necesidad; la tabla derivada basta.

### 2. Búsqueda exacta con `OR` sobre dos índices
`WHERE p.nombre_conocido = p_nombre OR p.nombre_legal = p_nombre`. MySQL puede resolverlo con *index merge union*, o elegir un recorrido completo si la tabla es diminuta. Por eso la prueba comprueba que el `EXPLAIN` incluye ambos índices en `possible_keys` (el plan los considera), no el plan concreto que elija el optimizador.

### 3. Índices con nombre dentro de `CREATE TABLE`
Se declaran `UNIQUE KEY uq_artista_nombre (nombre)`, `KEY idx_persona_nombre_conocido (nombre_conocido)` y `KEY idx_persona_nombre_legal (nombre_legal)`, con un comentario que da la justificación. Con nombres explícitos, las pruebas pueden comprobarlos.

### 4. `sp_historial_integrantes` devuelve también `persona_id`
Devuelve las mismas columnas que `sp_integrantes_en_fecha` más `persona_id` al principio, para que la CLI pueda navegar a la ficha de la persona sin buscar por nombre. Al ser un procedimiento nuevo, no rompe nada.

### 5. Pruebas con datos ficticios dentro de una transacción
Un fixture inserta como `root` un escenario ficticio, marcado como tal: una banda, cinco personas y álbumes de 2003, 2010 y 2015 (compilación). Llama a la vista y a los procedimientos dentro de la misma transacción y termina con un `ROLLBACK`. Los nombres llevan el sufijo "(ficticio)" para no chocar con los datos reales.

## Riesgos / Compromisos

- [La regla cuenta de más: "era integrante cuando salió" no es lo mismo que "tocó en ella"] → Es la semántica aprobada en el roadmap. Se documentará en `obtencion_datos/README.md` (spec `cargador-datos`).
- [Las búsquedas parciales dejan de funcionar en `sp_canciones_de_persona`] → La CLI siempre pasa el nombre exacto que elige con el autocompletado.
