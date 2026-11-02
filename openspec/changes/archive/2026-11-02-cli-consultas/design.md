# Diseño: cli-consultas

## Contexto

Ver `proposal.md`. `Catalogo` devuelve dataclasses con ids, y `cli.acciones()` asocia cada opción del menú a una función.

## Decisiones

### 1. Render separado de la interacción
Cada consulta tiene una función `render_*` (datos → `Table`, `Tree` o `Group` de Rich) y una acción que pregunta, consulta y muestra. Los render se prueban sin base de datos; las acciones, con respuestas simuladas sobre la demo.

### 2. `Preguntas` inyectable
Todas las interacciones (elegir de una lista, pedir una fecha, menú) pasan por `Preguntas`. Las pruebas usan un sustituto que resuelve los textos con la misma función `resolver` que la interfaz real.

### 3. Autocompletado propio
`CompletadorNormalizado` (un `Completer` de prompt_toolkit) compara el texto normalizado: `casefold`, sin tildes (NFKD) y con las comillas tipográficas convertidas en rectas. Los títulos de MusicBrainz usan «’», y así «maxwells» encuentra «Maxwell’s». `resolver` acepta una coincidencia exacta o una parcial única.

### 4. Encabezados que se adaptan al ancho
Se prueban las fuentes `standard` → `small` → `mini` y, si ninguna cabe, se usa texto simple. El arte de los artistas se mide con `rich.cells.cell_len`.

### 5. Traducciones y fechas
Las traducciones de los ENUM en inglés están en `ui.textos`, y la fecha larga se arma con nombres de mes propios, sin depender del *locale* del sistema.

## Riesgos / Compromisos

- [En la CLI, la navegación entre resultados todavía no existe] → Llega en `cli-fichas-navegacion`. Las acciones ya devuelven el elemento elegido para encadenarla.
