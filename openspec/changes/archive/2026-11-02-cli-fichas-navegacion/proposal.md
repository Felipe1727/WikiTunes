# Propuesta: cli-fichas-navegacion

## Por qué

Las consultas ya funcionan, pero cada una termina en el menú principal. El roadmap pide navegar entre resultados (de una canción a su álbum, de un integrante a sus otras bandas, de un género a sus artistas) y tener fichas de artista, persona, canción y género como nodos de esa navegación.

## Qué cambia

- **Fichas:**
  - artista: arte, tipo, años, origen, géneros, discografía e historial;
  - persona: nombre legal, nacimiento, fallecimiento y membresías;
  - canción: intérpretes, duración, géneros, créditos y álbumes;
  - género: árbol, artistas y álbumes del género o de sus subgéneros.
- **Tres opciones nuevas en el menú principal:** «Ficha de un artista», «Ficha de una persona» y «Ficha de una canción». La ficha de género se alcanza desde el árbol de géneros.
- **Menú «¿Y ahora?»** después de cada resultado, con saltos contextuales, «Volver a …» y «Menú principal». Cuando hay muchos destinos posibles, el salto abre un autocompletado.
- **Pila de pantallas y línea de migas** (`Menú › Paul McCartney › Wings`).
- **Catálogo:** nueva consulta `artistas_de_album`.

## Capacidades

### Capacidades nuevas
Ninguna.

### Capacidades modificadas
- `interfaz-cli`: se agregan las fichas, la navegación y las opciones nuevas del menú.
- `consultas-catalogo`: se agrega la consulta de los artistas de un álbum.

## Impacto

- `src/wikitunes/ui/` (módulos nuevos: `fichas`, `navegacion` y `acciones`; cambian `consultas` y `menu`), `src/wikitunes/cli.py`, `src/wikitunes/catalogo.py`, `tests/` y `README.md`.
