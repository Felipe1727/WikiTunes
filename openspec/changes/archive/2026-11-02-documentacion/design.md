# Diseño: documentacion

## Contexto

Ver `proposal.md`. Los detalles de datos ya están en `datos/README.md` y `obtencion_datos/README.md`, y las decisiones completas en `openspec/roadmap.md`.

## Decisiones

### 1. El README resume y enlaza
No duplica la metodología de datos ni el roadmap: los resume en «Procedencia de los datos» y «Decisiones principales» y enlaza a esos documentos.

### 2. Muestra real
El fragmento de salida (integrantes de King Crimson en 1974) se generó con la propia aplicación, renderizada a texto.

### 3. Verificación de los comandos
Se ejecutaron todos los comandos del README:
- `uv sync`, `docker compose up -d --wait`, `down` y `down -v`, y `docker compose logs cargador`;
- `uv run wikitunes` (en una pseudoterminal: animación + «Salir»), `--sin-animacion`, `--version` y `python -m wikitunes`;
- el cargador manual, `cp .env.ejemplo .env` y `scripts/generar_diagrama.sh`;
- los scripts de `obtencion_datos/`, las pruebas y el lint.
