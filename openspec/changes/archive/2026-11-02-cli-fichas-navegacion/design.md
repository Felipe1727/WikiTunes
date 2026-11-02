# Diseño: cli-fichas-navegacion

## Contexto

Ver `proposal.md`. Las consultas tienen funciones de render, y `Catalogo` devuelve fichas con ids.

## Decisiones

### 1. Pantallas y saltos
Cada `Pantalla` (artista, persona, canción, álbum, género, árbol, canciones de una persona, integrantes en una fecha e historial) es un dataclass inmutable con `titulo` y `mostrar(ctx) -> list[Salto]`. Un `Salto` tiene un texto y una función `destino(ctx)`, que devuelve la pantalla siguiente o `None` si el usuario cancela.

### 2. Saltos directos o con elección
Cuando hay pocos destinos (los álbumes de una canción, los artistas de una persona), cada uno es una opción. Cuando son muchos (los integrantes de King Crimson, las canciones de McCartney), un único salto «Ir a … …» abre el autocompletado. Los títulos repetidos (las dos versiones de *Get Back*) llevan su número.

### 3. `Navegador`
Mantiene una pila de pantallas. «Volver» saca la pantalla actual y vuelve a mostrar la anterior; «Menú principal» termina. Si se cancela una elección, se repite «¿Y ahora?» sin volver a mostrar la pantalla.

### 4. Reorganización
- Las acciones del menú pasan de `ui.consultas` a `ui.acciones`, porque ahora arrancan la navegación.
- `ui.consultas` conserva el render y las funciones «mostrar» (encabezado + resultado).
- Así se evita una importación circular con `ui.navegacion`.

## Riesgos / Compromisos

- [Una pila muy larga hace largas las migas] → Las migas son una sola línea, y Rich la corta según el ancho de la terminal.
