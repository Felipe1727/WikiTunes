# Propuesta: tabla-arte-artista

## Por qué

El roadmap exige mostrar, como encabezado de toda consulta cuyo protagonista sea un artista, un logo en arte ASCII que imite su tipografía. Hoy el esquema no tiene dónde guardarlo. Es el único cambio de esquema que ya estaba decidido desde el principio.

## Qué cambia

- Tabla nueva `arte_artista` en `Diagrama/musica_schema_mysql.sql`, en relación 1:1 opcional con `artista`:
  - `artista_id INT` como PK y FK a `artista` con `ON DELETE CASCADE`;
  - `arte TEXT NOT NULL` (utf8mb4, heredado de la base);
  - `estilo VARCHAR(40) NULL`, con un estilo de Rich (p. ej. `bold red`).
- Diagrama ER: entidad `ARTE_ARTISTA` y su relación en `Diagrama/musica_er.mmd`, y `Diagrama/musica_er.png` regenerado.
- `scripts/generar_diagrama.sh`: genera el PNG a partir del `.mmd` con la imagen Docker `minlag/mermaid-cli`, sin instalar Node.
- La base pasa a tener 17 tablas.

## Capacidades

### Capacidades nuevas
- `arte-artista`: almacenamiento del arte ASCII de cada artista (varias líneas, sin pérdida de caracteres) y su estilo de presentación.

### Capacidades modificadas
- `entorno-base-datos`: el primer arranque crea 17 tablas (se suma `arte_artista`).

## Impacto

- El esquema SQL y el diagrama ER (`.mmd` y `.png`).
- Las bases locales existentes deben reinicializarse con `docker compose down -v`.
- No afecta a los procedimientos ni a la vista.
