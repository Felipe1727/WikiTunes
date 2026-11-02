# Diseño: capa-datos

## Contexto

Ver `proposal.md`. El conector instalado (mysql-connector-python 26.10) marca `cursor.stored_results()` como obsoleto. La configuración ya existe en `wikitunes.configuracion`.

## Decisiones

### 1. `CALL` + `nextset()`
`llamar_procedimiento` ejecuta `CALL sp(...)` y recorre los conjuntos con `nextset()`, armando cada fila como diccionario a partir de `cursor.description`. Funciona igual para los procedimientos de uno y de dos resultados.

### 2. Una conexión por sesión, en autocommit
Es una CLI de un solo usuario y de solo lectura: el `autocommit` evita transacciones abiertas que dejarían ver datos viejos después de una recarga.

### 3. Ids para navegar
Los procedimientos devuelven nombres, no ids, salvo `sp_historial_integrantes`. La capa los completa con consultas auxiliares:
- **canciones de una persona:** desde la vista, haciendo coincidir canción, vía y rol;
- **tracklist:** desde `album_cancion`, por disco y pista;
- **integrantes en una fecha:** desde `membresia`, por persona y fecha de inicio.

Así la interfaz puede ir a cualquier ficha sin buscar por título, que sería ambiguo con *Get Back*.

### 4. Canciones de una persona
Se llama al procedimiento con el nombre exacto y se filtran las filas por la columna `persona`, tal como fija el roadmap.

### 5. Errores
Los errores del conector se traducen a `ErrorDeConexion`, si significan que la base no está (2003, 2006, 2013, 1045...), o a `ErrorDeBaseDeDatos` en los demás casos. Los mensajes van en español.

## Riesgos / Compromisos

- [Una persona con el mismo nombre que otra recibiría las participaciones de ambas desde el procedimiento] → Ningún nombre se repite en la demo. Los ids se resuelven por `persona_id` desde la vista.
