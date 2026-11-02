# Propuesta: capa-datos

## Por qué

La CLI necesita una capa intermedia que se conecte a MySQL, llame a los procedimientos almacenados (incluidos los dos resultados de `sp_tracklist`), arme las fichas y los listados de autocompletado, y traduzca los errores a mensajes en español. Así la interfaz no toca SQL ni el conector.

## Qué cambia

- **`wikitunes.conexion`:** abre la conexión con el usuario de solo lectura, ejecuta SELECT y procedimientos (`CALL` + `nextset()`) y define las excepciones `ErrorDeBaseDeDatos` y `ErrorDeConexion`, con mensajes en español.
- **`wikitunes.modelos`:** dataclasses para las participaciones, los nodos de género, las pistas, el tracklist, los integrantes y las fichas.
- **`wikitunes.catalogo.Catalogo`:**
  - los 5 procedimientos;
  - las fichas de artista, persona, canción y género (este con sus subgéneros);
  - los listados para el autocompletado.

  Los resultados de los procedimientos se enriquecen con los ids necesarios para navegar.
- **`wikitunes.formato`:** duraciones (`m:ss` / `h:mm:ss`) y periodos en años.

## Capacidades

### Capacidades nuevas
- `consultas-catalogo`: consultas tipadas de solo lectura sobre el catálogo y su manejo de errores.

### Capacidades modificadas
Ninguna.

## Impacto

- Módulos nuevos en `src/wikitunes/` y sus pruebas. Lo usarán las specs de la CLI.
