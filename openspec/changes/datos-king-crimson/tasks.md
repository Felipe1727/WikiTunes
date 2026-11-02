# Tareas

## 1. Datos

- [ ] 1.1 Descargar a `crudo/` las 4 ediciones de referencia; verificar el título, la fecha y el país de cada una
- [ ] 1.2 Agregar a los CSV el artista, las personas, las 37 membresías, los álbumes, las canciones, los créditos, los géneros, las ciudades y los sellos, con sus fuentes; verificar que el cargador los carga sin errores
- [ ] 1.3 Documentar en `obtencion_datos/README.md` cómo se obtuvieron (línea de tiempo, producción acreditada a la banda, música y letra, ids); verificar con una revisión contra el diseño

## 2. Pruebas

- [ ] 2.1 Crear `tests/integracion/test_datos_king_crimson.py` (formaciones en 1969, 1974, 1981 y 1995, historial completo, solo King Crimson para Fripp, Belew fuera de 1969) y comprobar que las pruebas genéricas de `tests/test_datos.py` cubren los nuevos datos; verificar con `uv run pytest`

## Workflow follow-up

- Fusionar la PR y archivar el cambio con `/opsx:archive`.
