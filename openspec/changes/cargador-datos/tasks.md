# Tareas

## 1. Configuración y cargador

- [ ] 1.1 Crear `src/wikitunes/configuracion.py` (`ConfiguracionBD` desde el entorno y `.env`) y hacer que `tests/conftest.py` la use; verificar que las pruebas existentes siguen pasando
- [ ] 1.2 Crear `src/wikitunes/cargador.py` (lectura de CSV, lectura de arte, validación de columnas, carga transaccional con reemplazo, `ErrorDeCarga`, CLI `python -m wikitunes.cargador`); verificar con las pruebas de 1.3 y 1.4
- [ ] 1.3 Pruebas unitarias en `tests/test_cargador.py` (celdas vacías, comas, comillas y saltos de línea, arte con barras invertidas, ruta fuera de `arte/`, columna desconocida); verificar con `uv run pytest`
- [ ] 1.4 Pruebas de integración en `tests/integracion/test_cargador_bd.py` con datos ficticios de `tests/datos_ejemplo/` (carga, recarga sin duplicados, error con archivo y línea sin cambios en la base, directorio vacío), con `ROLLBACK`; verificar con `uv run pytest`

## 2. Compose y datos

- [ ] 2.1 Añadir el servicio `cargador` a `compose.yaml` y crear `datos/README.md` y `datos/arte/`; verificar que `docker compose up -d --wait` termina con éxito y el registro del cargador indica la carga
- [ ] 2.2 Documentar en el README la recarga de datos y la ejecución manual del cargador; verificar que los comandos funcionan

## 3. Procedencia

- [ ] 3.1 Crear `obtencion_datos/README.md` con la metodología y todas las convenciones de datos del roadmap, `fuentes.csv` con su encabezado y `crudo/`; verificar con una revisión contra la sección "Datos de la demo" del roadmap
- [ ] 3.2 Crear `obtencion_datos/scripts/musicbrainz.py` (descarga con caché, User-Agent, límite de frecuencia, borrador del tracklist) y sus pruebas unitarias con JSON ficticio; verificar con `uv run pytest` y descargando un MBID real

## Workflow follow-up

- Fusionar la PR y archivar el cambio con `/opsx:archive`.
