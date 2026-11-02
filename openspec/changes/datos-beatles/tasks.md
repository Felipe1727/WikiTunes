# Tareas

## 1. Datos

- [ ] 1.1 Descargar a `obtencion_datos/crudo/` las 12 ediciones de referencia con `scripts/musicbrainz.py`; verificar que el título, la fecha y el país de cada una son los esperados
- [ ] 1.2 Escribir los CSV de catálogos, personas, artistas, membresías, álbumes, canciones, géneros y créditos, y `obtencion_datos/fuentes.csv` con enlaces permanentes; verificar que `uv run python -m wikitunes.cargador` los carga sin errores
- [ ] 1.3 Documentar en `obtencion_datos/README.md` las decisiones de esta carga (ediciones, créditos, correspondencia de géneros, consecuencias de la regla de participación); verificar con una revisión contra el diseño

## 2. Pruebas

- [ ] 2.1 Crear `tests/test_datos.py` (completitud frente a `crudo/`, procedencia, integridad de créditos y membresías, tipos exigidos y featuring); verificar con `uv run pytest`
- [ ] 2.2 Crear `tests/integracion/test_datos_beatles.py` con los hechos del roadmap (integrantes en 1961 y 1963, Lennon y *Abbey Road* / *I Me Mine*, Pete Best, McCartney por tres vías, canciones reutilizadas en *1*, tres niveles en `sp_subgeneros('Rock')`); verificar con `uv run pytest`

## Workflow follow-up

- Fusionar la PR y archivar el cambio con `/opsx:archive`.
