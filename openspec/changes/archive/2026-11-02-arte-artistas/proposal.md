# Propuesta: arte-artistas

## Por qué

Toda consulta cuyo protagonista sea un artista abre con su logo en arte ASCII, y la tabla `arte_artista` ya existe. Faltan el arte de cada uno de los 10 artistas de la demo y las garantías de formato que necesita la CLI.

## Qué cambia

- **Un arte por artista en `datos/arte/<nombre>.txt`**, más `datos/arte_artista.csv` con su archivo y un estilo de Rich. Cuando el artista tiene una tipografía reconocible (p. ej. la «T» alargada de The Beatles), el arte la imita; si no, se diseña uno acorde a su estilo (p. ej. el rojo carmesí de King Crimson).
- **`obtencion_datos/scripts/generar_arte.py`**, que genera el arte de forma reproducible a partir de fuentes de pyfiglet más los rasgos de cada artista.
- **Criterio de cada logo** en `obtencion_datos/README.md`.
- **Pruebas de formato:** todos tienen arte, máximo 80 columnas, sin tabuladores, solo caracteres de una columna, finales LF, estilo válido y coincidencia con el generador.

## Capacidades

### Capacidades nuevas
Ninguna.

### Capacidades modificadas
- `datos-demo`: se agrega el requisito de que cada artista tenga un arte con formato válido.

## Impacto

- `datos/arte/`, `datos/arte_artista.csv`, `obtencion_datos/` y `tests/`.
