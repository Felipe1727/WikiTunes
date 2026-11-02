# Propuesta: cli-consultas

## Por qué

El menú principal ya existe, pero sus cinco consultas todavía no hacen nada. Son la funcionalidad central de WikiTunes y deben sentirse naturales: elegir sin escribir ids, con encabezados vistosos, tablas con estilo y avisos claros cuando no hay resultados.

## Qué cambia

- **Las cinco consultas del menú:**
  - canciones de una persona;
  - árbol de un género;
  - tracklist de un álbum;
  - integrantes en una fecha;
  - historial de integrantes.
- **Elección con autocompletado.** Busca por subcadena sin distinguir mayúsculas, tildes ni comillas tipográficas, y valida que la opción exista. Los álbumes se muestran con año y tipo.
- **Fecha con validación** (`AAAA-MM-DD`).
- **Encabezados.** Las consultas de artista muestran su arte ASCII con su estilo; las demás, un título de pyfiglet. Si el arte no cabe en la terminal, se usa el nombre en la fuente de pyfiglet más grande que quepa, y si ninguna cabe, texto simple.
- **Resultados** en tablas de Rich y en un árbol (`rich.tree`), con los valores del esquema traducidos («Compilación», «Invitado (feat.)») y los periodos en años. Si no hay resultados, un panel «Sin resultados».

## Capacidades

### Capacidades nuevas
Ninguna.

### Capacidades modificadas
- `interfaz-cli`: se agregan las consultas, el autocompletado, los encabezados y la presentación de resultados.

## Impacto

- `src/wikitunes/ui/` (módulos nuevos: `consultas`, `preguntas`, `encabezados` y `textos`), `src/wikitunes/cli.py`, `tests/` y `README.md`.
