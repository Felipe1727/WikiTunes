# Tareas

## 1. Esquema

- [ ] 1.1 Añadir `arte_artista` a `Diagrama/musica_schema_mysql.sql` (PK/FK `artista_id` con `ON DELETE CASCADE`, `arte TEXT NOT NULL`, `estilo VARCHAR(40) NULL`); verificar que tras `docker compose down -v && docker compose up -d --wait` la tabla existe
- [ ] 1.2 Crear `tests/integracion/test_arte_artista.py`: ida y vuelta exacta con `\`, `"`, `'`, espacios iniciales y bloques Unicode; clave duplicada; FK inexistente; estilo `NULL`; cascada; todo dentro de una transacción con `ROLLBACK`. Actualizar la prueba de humo a 17 tablas. Verificar con `uv run pytest`

## 2. Diagrama ER

- [ ] 2.1 Añadir `ARTE_ARTISTA` y la relación con `ARTISTA` a `Diagrama/musica_er.mmd`; verificar que el PNG se genera sin errores
- [ ] 2.2 Crear `scripts/generar_diagrama.sh` y regenerar `Diagrama/musica_er.png`; verificar que el PNG existe y muestra la entidad nueva
- [ ] 2.3 Documentar en el README cómo regenerar el diagrama; verificar que el comando documentado funciona

## Workflow follow-up

- Fusionar la PR y archivar el cambio con `/opsx:archive`.
