# Delta de spec

## MODIFIED Requirements

### Requirement: Arranque reproducible de la base
El sistema DEBE (MUST) levantar con `docker compose up -d --wait` un servidor MySQL 8.4 que, partiendo de un volumen vacío, ejecute el esquema y los procedimientos del repositorio sin modificarlos. El comando DEBE terminar solo cuando la base acepta conexiones por red con todos los objetos creados.

#### Scenario: Primer arranque
- **WHEN** se ejecuta `docker compose up -d --wait` sin volumen de datos previo
- **THEN** el comando termina con éxito y la base `musica` contiene 17 tablas (incluida `arte_artista`), 4 triggers, la vista `v_participacion_persona` y los procedimientos `sp_canciones_de_persona`, `sp_subgeneros`, `sp_tracklist` y `sp_integrantes_en_fecha`

#### Scenario: Arranque sin archivo .env
- **WHEN** no existe el archivo `.env` en el repositorio
- **THEN** el arranque usa los valores por defecto de desarrollo documentados en `.env.ejemplo` y funciona igual
