# Diseño: arte-artistas

## Contexto

Ver `proposal.md`. El formato de los archivos y su carga los define `cargador-datos`. pyfiglet ya es dependencia del proyecto.

## Decisiones

### 1. Generador en lugar de arte escrito a mano
Cada logo combina una fuente de pyfiglet con elementos dibujados en el script: el tronco de la «T», las alas, el teclado, los lentes. Así el arte es reproducible y revisable en un diff de código, y una prueba garantiza que los `.txt` no se desvían del generador.
- *Alternativa descartada:* escribir los `.txt` a mano. Funciona, pero no deja constancia del criterio de cada logo ni permite ajustarlos de forma consistente.

### 2. Medición de columnas con Rich
`rich.cells.cell_len` y `get_character_cell_size` son las funciones que usa la CLI para medir el ancho, así que la prueba y la presentación coinciden.

### 3. Estilos
Un estilo de Rich por artista, elegido según su identidad: rojo para King Crimson, blanco para The Beatles, etc. Se valida con `Style.parse`.

## Riesgos / Compromisos

- [Los caracteres de bloque `█ ▀ ░` son de ancho «ambiguo» en terminales configuradas para CJK] → El roadmap los permite expresamente. La CLI usará el nombre con pyfiglet si el arte no cabe.
