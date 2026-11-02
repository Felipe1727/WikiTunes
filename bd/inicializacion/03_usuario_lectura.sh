#!/bin/bash
# Crea el usuario de la aplicación con permisos de solo lectura (SELECT y EXECUTE).
# Lo ejecuta el entrypoint de la imagen oficial de MySQL una sola vez, cuando el volumen de
# datos está vacío. El archivo NO es ejecutable a propósito: así el entrypoint lo carga con
# `source` y la función `docker_process_sql` está disponible.

wikitunes_nombre_bd="${WIKITUNES_BD_NOMBRE:-musica}"
wikitunes_usuario="${WIKITUNES_BD_USUARIO:-wikitunes}"
wikitunes_clave="${WIKITUNES_BD_CLAVE:-wikitunes}"

docker_process_sql <<SQL
CREATE USER IF NOT EXISTS '${wikitunes_usuario}'@'%' IDENTIFIED BY '${wikitunes_clave}';
GRANT SELECT, EXECUTE ON \`${wikitunes_nombre_bd}\`.* TO '${wikitunes_usuario}'@'%';
FLUSH PRIVILEGES;
SQL

echo "Usuario de solo lectura '${wikitunes_usuario}' creado sobre '${wikitunes_nombre_bd}'."
