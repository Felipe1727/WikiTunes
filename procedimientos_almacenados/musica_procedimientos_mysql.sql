-- =====================================================================
--  Base de datos demo de música — procedimientos almacenados (MySQL 8)
--  Requiere haber ejecutado antes musica_schema_mysql.sql
-- =====================================================================

-- El archivo está en UTF-8. Sin esto, un cliente con otro juego de caracteres
-- (p. ej. el de la imagen Docker, que usa latin1) guardaría mal los acentos
-- de los literales, como '(crédito individual)'.
SET NAMES utf8mb4;

USE musica;

DROP PROCEDURE IF EXISTS sp_canciones_de_persona;
DROP PROCEDURE IF EXISTS sp_subgeneros;
DROP PROCEDURE IF EXISTS sp_tracklist;
DROP PROCEDURE IF EXISTS sp_integrantes_en_fecha;
DROP PROCEDURE IF EXISTS sp_historial_integrantes;

DELIMITER //

-- ---------------------------------------------------------------------
--  1. Todas las canciones en las que participó una persona:
--     con una banda, como solista o con crédito individual.
--     Busca por nombre EXACTO (conocido o legal) para usar los índices
--     idx_persona_nombre_conocido e idx_persona_nombre_legal.
--     Ej.: CALL sp_canciones_de_persona('Paul McCartney');
-- ---------------------------------------------------------------------
CREATE PROCEDURE sp_canciones_de_persona(IN p_nombre VARCHAR(150))
BEGIN
    SELECT v.persona,
           v.cancion,
           v.via,
           v.rol
    FROM v_participacion_persona v
    JOIN persona p ON p.persona_id = v.persona_id
    WHERE p.nombre_conocido = p_nombre
       OR p.nombre_legal    = p_nombre
    ORDER BY v.persona, v.cancion, v.via;
END//

-- ---------------------------------------------------------------------
--  2. Un género y todos sus subgéneros (a cualquier profundidad),
--     con el nivel y la ruta completa desde el género pedido.
--     Ej.: CALL sp_subgeneros('Rock');
-- ---------------------------------------------------------------------
CREATE PROCEDURE sp_subgeneros(IN p_genero VARCHAR(80))
BEGIN
    WITH RECURSIVE arbol AS (
        SELECT genero_id,
               nombre,
               0 AS nivel,
               CAST(nombre AS CHAR(1000)) AS ruta
        FROM genero
        WHERE nombre = p_genero
        UNION ALL
        SELECT g.genero_id,
               g.nombre,
               a.nivel + 1,
               CONCAT(a.ruta, ' > ', g.nombre)
        FROM genero g
        JOIN arbol a ON g.genero_padre_id = a.genero_id
    )
    SELECT genero_id, nombre, nivel, ruta
    FROM arbol
    ORDER BY ruta;
END//

-- ---------------------------------------------------------------------
--  3. Tracklist de un álbum en orden de disco y pista, con los
--     intérpretes de cada canción. Devuelve dos resultados:
--     las pistas y el resumen (número de pistas y duración total).
--     Ej.: CALL sp_tracklist(1);
-- ---------------------------------------------------------------------
CREATE PROCEDURE sp_tracklist(IN p_album_id INT)
BEGIN
    SELECT ac.numero_disco AS disco,
           ac.numero_pista AS pista,
           c.titulo        AS cancion,
           GROUP_CONCAT(
               CASE WHEN ca.rol = 'Featuring' THEN CONCAT('feat. ', ar.nombre)
                    ELSE ar.nombre END
               ORDER BY ca.rol, ar.nombre SEPARATOR ', ')            AS interpretes,
           CONCAT(c.duracion_seg DIV 60, ':',
                  LPAD(c.duracion_seg MOD 60, 2, '0'))               AS duracion
    FROM album_cancion ac
    JOIN cancion c               ON c.cancion_id  = ac.cancion_id
    LEFT JOIN credito_artista ca ON ca.cancion_id = c.cancion_id
                                AND ca.rol IN ('Principal', 'Featuring')
    LEFT JOIN artista ar         ON ar.artista_id = ca.artista_id
    WHERE ac.album_id = p_album_id
    GROUP BY ac.numero_disco, ac.numero_pista, c.titulo, c.duracion_seg
    ORDER BY ac.numero_disco, ac.numero_pista;

    SELECT al.titulo,
           al.tipo,
           COUNT(ac.cancion_id)                                       AS pistas,
           SEC_TO_TIME(COALESCE(SUM(c.duracion_seg), 0))              AS duracion_total
    FROM album al
    LEFT JOIN album_cancion ac ON ac.album_id  = al.album_id
    LEFT JOIN cancion c        ON c.cancion_id = ac.cancion_id
    WHERE al.album_id = p_album_id
    GROUP BY al.album_id, al.titulo, al.tipo;
END//

-- ---------------------------------------------------------------------
--  4. Integrantes de un artista en una fecha dada.
--     Fechas de inicio/fin NULL se tratan como "desde siempre" /
--     "hasta hoy".
--     Ej.: CALL sp_integrantes_en_fecha('The Beatles', '1961-06-01');
-- ---------------------------------------------------------------------
CREATE PROCEDURE sp_integrantes_en_fecha(IN p_artista VARCHAR(150), IN p_fecha DATE)
BEGIN
    SELECT a.nombre                                    AS artista,
           COALESCE(p.nombre_conocido, p.nombre_legal) AS persona,
           m.rol,
           m.fecha_inicio,
           m.fecha_fin
    FROM artista a
    JOIN membresia m ON m.artista_id = a.artista_id
    JOIN persona p   ON p.persona_id = m.persona_id
    WHERE a.nombre = p_artista
      AND (m.fecha_inicio IS NULL OR m.fecha_inicio <= p_fecha)
      AND (m.fecha_fin    IS NULL OR m.fecha_fin    >= p_fecha)
    ORDER BY m.fecha_inicio, persona;
END//

-- ---------------------------------------------------------------------
--  5. Historial completo de integrantes de un artista: una fila por
--     periodo de membresía (quien sale y vuelve tiene dos filas).
--     Incluye persona_id para poder navegar a la ficha de la persona.
--     Ej.: CALL sp_historial_integrantes('King Crimson');
-- ---------------------------------------------------------------------
CREATE PROCEDURE sp_historial_integrantes(IN p_artista VARCHAR(150))
BEGIN
    SELECT p.persona_id,
           a.nombre                                    AS artista,
           COALESCE(p.nombre_conocido, p.nombre_legal) AS persona,
           m.rol,
           m.fecha_inicio,
           m.fecha_fin
    FROM artista a
    JOIN membresia m ON m.artista_id = a.artista_id
    JOIN persona p   ON p.persona_id = m.persona_id
    WHERE a.nombre = p_artista
    ORDER BY m.fecha_inicio, persona;
END//

DELIMITER ;
