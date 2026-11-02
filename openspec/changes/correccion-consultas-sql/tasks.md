# Tareas

## 1. Esquema

- [ ] 1.1 Añadir `uq_artista_nombre`, `idx_persona_nombre_conocido` e `idx_persona_nombre_legal` con su justificación en `Diagrama/musica_schema_mysql.sql`; verificar con `information_schema.statistics` tras reinicializar la base
- [ ] 1.2 Reescribir `v_participacion_persona` con la regla aprobada; verificar con las pruebas del grupo 3

## 2. Procedimientos

- [ ] 2.1 Cambiar `sp_canciones_de_persona` a búsqueda por igualdad; verificar con las pruebas de nombre exacto, nombre parcial y `EXPLAIN`
- [ ] 2.2 Crear `sp_historial_integrantes(p_artista)`; verificar con las pruebas de historial (sale y vuelve, activo, inexistente)

## 3. Pruebas y diagrama

- [ ] 3.1 Crear `tests/integracion/test_consultas_sql.py` con el escenario ficticio en una transacción y cubrir cada escenario de las specs `participacion-persona` e `integrantes-artista`; actualizar la prueba de humo con el quinto procedimiento; verificar con `uv run pytest`
- [ ] 3.2 Marcar `nombre` como `UK` en `ARTISTA` dentro de `Diagrama/musica_er.mmd` y regenerar el PNG con `scripts/generar_diagrama.sh`; verificar que el PNG muestra la marca

## Workflow follow-up

- Fusionar la PR y archivar el cambio con `/opsx:archive`.
