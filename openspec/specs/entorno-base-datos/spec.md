# entorno-base-datos Specification

## Purpose
Permite levantar de forma reproducible, con un solo comando, la base de datos `musica` de WikiTunes con su esquema, sus procedimientos y un usuario de solo lectura para la aplicación.

## Requirements

### Requirement: Arranque reproducible de la base
El sistema DEBE (MUST) levantar con `docker compose up -d --wait` un servidor MySQL 8.4 que, partiendo de un volumen vacío, ejecute el esquema y los procedimientos del repositorio sin modificarlos. El comando DEBE terminar solo cuando la base acepta conexiones por red con todos los objetos creados.

#### Scenario: Primer arranque
- **WHEN** se ejecuta `docker compose up -d --wait` sin volumen de datos previo
- **THEN** el comando termina con éxito y la base `musica` contiene 17 tablas (incluida `arte_artista`), 4 triggers, la vista `v_participacion_persona` y los procedimientos `sp_canciones_de_persona`, `sp_subgeneros`, `sp_tracklist` y `sp_integrantes_en_fecha`

#### Scenario: Arranque sin archivo .env
- **WHEN** no existe el archivo `.env` en el repositorio
- **THEN** el arranque usa los valores por defecto de desarrollo documentados en `.env.ejemplo` y funciona igual

### Requirement: Usuario de solo lectura para la aplicación
El sistema DEBE (MUST) crear un usuario de aplicación, configurable con `WIKITUNES_BD_USUARIO` y `WIKITUNES_BD_CLAVE`, que solo tenga permisos de `SELECT` y `EXECUTE` sobre la base `musica`.

#### Scenario: Consulta y ejecución permitidas
- **WHEN** el usuario de aplicación ejecuta un `SELECT` o llama a un procedimiento de `musica`
- **THEN** la operación se completa sin error de permisos

#### Scenario: Escritura rechazada
- **WHEN** el usuario de aplicación intenta un `INSERT` en cualquier tabla de `musica`
- **THEN** MySQL rechaza la operación con un error de permisos

### Requirement: Configuración de conexión por variables de entorno
El sistema DEBE (MUST) tomar los datos de conexión de las variables `WIKITUNES_BD_HOST`, `WIKITUNES_BD_PUERTO`, `WIKITUNES_BD_USUARIO`, `WIKITUNES_BD_CLAVE` y `WIKITUNES_BD_NOMBRE`, leídas del entorno o de un archivo `.env` no versionado, con valores por defecto de desarrollo.

#### Scenario: Puerto personalizado
- **WHEN** `WIKITUNES_BD_PUERTO` vale `3310` en `.env`
- **THEN** MySQL queda publicado en el puerto 3310 del host y las pruebas se conectan a ese puerto

### Requirement: Pruebas de integración según disponibilidad de la base
Las pruebas marcadas como `integracion` DEBEN (MUST) saltarse con un aviso cuando la base no responde, salvo que `WIKITUNES_EXIGIR_BD=1`, en cuyo caso DEBEN fallar.

#### Scenario: Base caída en local
- **WHEN** la base no está levantada y no está definida `WIKITUNES_EXIGIR_BD`
- **THEN** las pruebas de integración aparecen como saltadas con un motivo en español y el resto de pruebas se ejecuta

#### Scenario: Base caída con la base exigida
- **WHEN** la base no está levantada y `WIKITUNES_EXIGIR_BD=1`
- **THEN** las pruebas de integración fallan con un mensaje en español que indica que no hay conexión
