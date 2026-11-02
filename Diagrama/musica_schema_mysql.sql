-- =====================================================================
--  Base de datos demo de música — esquema (MySQL 8.0.16+)
--  Persona es la unidad atómica; Artista agrupa personas vía Membresía.
-- =====================================================================

DROP DATABASE IF EXISTS musica;
CREATE DATABASE musica
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE musica;

-- ---------------------------------------------------------------------
--  Geografía
-- ---------------------------------------------------------------------
CREATE TABLE pais (
    pais_id     INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL UNIQUE,
    codigo_iso2 CHAR(2)      NOT NULL UNIQUE
) ENGINE = InnoDB;

CREATE TABLE ciudad (
    ciudad_id INT AUTO_INCREMENT PRIMARY KEY,
    nombre    VARCHAR(100) NOT NULL,
    pais_id   INT NOT NULL,
    UNIQUE (nombre, pais_id),
    FOREIGN KEY (pais_id) REFERENCES pais(pais_id)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
--  Catálogos
-- ---------------------------------------------------------------------
-- Nota: MySQL no permite CHECK sobre columnas AUTO_INCREMENT, así que
-- "un género no puede ser su propio padre" se valida con triggers (abajo).
CREATE TABLE genero (
    genero_id       INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(80) NOT NULL UNIQUE,
    genero_padre_id INT NULL,                              -- NULL = género raíz
    FOREIGN KEY (genero_padre_id) REFERENCES genero(genero_id)
) ENGINE = InnoDB;

CREATE TABLE sello (
    sello_id        INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(120) NOT NULL UNIQUE,
    pais_id         INT NULL,
    anio_fundacion  SMALLINT NULL,
    sello_padre_id  INT NULL,                              -- subsidiarias (p. ej. Parlophone → Warner)
    FOREIGN KEY (pais_id)        REFERENCES pais(pais_id),
    FOREIGN KEY (sello_padre_id) REFERENCES sello(sello_id)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
--  Personas y artistas
-- ---------------------------------------------------------------------
CREATE TABLE persona (
    persona_id           INT AUTO_INCREMENT PRIMARY KEY,
    nombre_legal         VARCHAR(150) NOT NULL,
    nombre_conocido      VARCHAR(150) NULL,                -- "Paul McCartney" vs "James Paul McCartney"
    fecha_nacimiento     DATE NULL,
    fecha_fallecimiento  DATE NULL,
    ciudad_nacimiento_id INT NULL,
    CONSTRAINT chk_persona_fechas
        CHECK (fecha_fallecimiento IS NULL OR fecha_fallecimiento >= fecha_nacimiento),
    FOREIGN KEY (ciudad_nacimiento_id) REFERENCES ciudad(ciudad_id)
) ENGINE = InnoDB;

CREATE TABLE artista (
    artista_id       INT AUTO_INCREMENT PRIMARY KEY,
    nombre           VARCHAR(150) NOT NULL,
    tipo             ENUM('Solista', 'Banda', 'Duo', 'Colectivo', 'Orquesta') NOT NULL,
    anio_formacion   SMALLINT NULL,
    anio_disolucion  SMALLINT NULL,
    ciudad_origen_id INT NULL,
    CONSTRAINT chk_artista_anios
        CHECK (anio_disolucion IS NULL OR anio_disolucion >= anio_formacion),
    FOREIGN KEY (ciudad_origen_id) REFERENCES ciudad(ciudad_id)
) ENGINE = InnoDB;

-- Relación Persona ↔ Artista. Una fila por periodo de pertenencia
-- (alguien que sale y vuelve a la banda tiene dos filas).
CREATE TABLE membresia (
    membresia_id INT AUTO_INCREMENT PRIMARY KEY,
    persona_id   INT NOT NULL,
    artista_id   INT NOT NULL,
    rol          VARCHAR(100) NULL,                        -- "Bajo, voz"
    fecha_inicio DATE NULL,
    fecha_fin    DATE NULL,                                -- NULL = sigue activo
    CONSTRAINT chk_membresia_fechas
        CHECK (fecha_fin IS NULL OR fecha_fin >= fecha_inicio),
    FOREIGN KEY (persona_id) REFERENCES persona(persona_id),
    FOREIGN KEY (artista_id) REFERENCES artista(artista_id) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE artista_genero (
    artista_id INT NOT NULL,
    genero_id  INT NOT NULL,
    PRIMARY KEY (artista_id, genero_id),
    FOREIGN KEY (artista_id) REFERENCES artista(artista_id) ON DELETE CASCADE,
    FOREIGN KEY (genero_id)  REFERENCES genero(genero_id)
) ENGINE = InnoDB;

-- Arte ASCII de cada artista: logo en texto que imita su tipografía.
-- Relación 1:1 opcional (un artista sin arte no tiene fila). `arte` guarda
-- varias líneas separadas por LF; `estilo` es un estilo de Rich ("bold red").
CREATE TABLE arte_artista (
    artista_id INT PRIMARY KEY,
    arte       TEXT        NOT NULL,
    estilo     VARCHAR(40) NULL,
    FOREIGN KEY (artista_id) REFERENCES artista(artista_id) ON DELETE CASCADE
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
--  Álbumes y canciones
-- ---------------------------------------------------------------------
CREATE TABLE album (
    album_id          INT AUTO_INCREMENT PRIMARY KEY,
    titulo            VARCHAR(200) NOT NULL,
    tipo              ENUM('LP', 'EP', 'Single', 'Compilation', 'Live', 'Soundtrack', 'Remix') NOT NULL,
    fecha_lanzamiento DATE NULL,
    sello_id          INT NULL,
    FOREIGN KEY (sello_id) REFERENCES sello(sello_id)
) ENGINE = InnoDB;

-- N:M — álbumes colaborativos o compilaciones de varios artistas.
CREATE TABLE album_artista (
    album_id   INT NOT NULL,
    artista_id INT NOT NULL,
    orden      SMALLINT NOT NULL DEFAULT 1,               -- orden de aparición en la portada
    PRIMARY KEY (album_id, artista_id),
    FOREIGN KEY (album_id)   REFERENCES album(album_id) ON DELETE CASCADE,
    FOREIGN KEY (artista_id) REFERENCES artista(artista_id)
) ENGINE = InnoDB;

CREATE TABLE album_genero (
    album_id  INT NOT NULL,
    genero_id INT NOT NULL,
    PRIMARY KEY (album_id, genero_id),
    FOREIGN KEY (album_id)  REFERENCES album(album_id) ON DELETE CASCADE,
    FOREIGN KEY (genero_id) REFERENCES genero(genero_id)
) ENGINE = InnoDB;

CREATE TABLE cancion (
    cancion_id   INT AUTO_INCREMENT PRIMARY KEY,
    titulo       VARCHAR(200) NOT NULL,
    duracion_seg INT NULL,
    CONSTRAINT chk_cancion_duracion CHECK (duracion_seg > 0)
) ENGINE = InnoDB;

-- Género propio de la canción (puede diferir del género del álbum).
CREATE TABLE cancion_genero (
    cancion_id INT NOT NULL,
    genero_id  INT NOT NULL,
    PRIMARY KEY (cancion_id, genero_id),
    FOREIGN KEY (cancion_id) REFERENCES cancion(cancion_id) ON DELETE CASCADE,
    FOREIGN KEY (genero_id)  REFERENCES genero(genero_id)
) ENGINE = InnoDB;

-- Tracklist: una canción puede aparecer en varios álbumes.
CREATE TABLE album_cancion (
    album_id     INT NOT NULL,
    cancion_id   INT NOT NULL,
    numero_disco SMALLINT NOT NULL DEFAULT 1,
    numero_pista SMALLINT NOT NULL,
    PRIMARY KEY (album_id, numero_disco, numero_pista),
    UNIQUE (album_id, cancion_id),
    CONSTRAINT chk_album_cancion_num CHECK (numero_disco > 0 AND numero_pista > 0),
    FOREIGN KEY (album_id)   REFERENCES album(album_id) ON DELETE CASCADE,
    FOREIGN KEY (cancion_id) REFERENCES cancion(cancion_id)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
--  Créditos
-- ---------------------------------------------------------------------
-- Quién "firma" la canción (intérprete principal, featuring...).
CREATE TABLE credito_artista (
    cancion_id INT NOT NULL,
    artista_id INT NOT NULL,
    rol        ENUM('Principal', 'Featuring', 'Remixer') NOT NULL,
    PRIMARY KEY (cancion_id, artista_id, rol),
    FOREIGN KEY (cancion_id) REFERENCES cancion(cancion_id) ON DELETE CASCADE,
    FOREIGN KEY (artista_id) REFERENCES artista(artista_id)
) ENGINE = InnoDB;

-- Créditos individuales (compositor, productor...), siempre a una Persona.
CREATE TABLE credito_persona (
    cancion_id INT NOT NULL,
    persona_id INT NOT NULL,
    rol        ENUM('Compositor', 'Letrista', 'Productor', 'Arreglista', 'Ingeniero', 'Musico de sesion') NOT NULL,
    PRIMARY KEY (cancion_id, persona_id, rol),
    FOREIGN KEY (cancion_id) REFERENCES cancion(cancion_id) ON DELETE CASCADE,
    FOREIGN KEY (persona_id) REFERENCES persona(persona_id)
) ENGINE = InnoDB;

-- (InnoDB crea automáticamente índices para las columnas FK.)

-- ---------------------------------------------------------------------
--  Triggers
-- ---------------------------------------------------------------------
DELIMITER //

-- Un artista 'Solista' solo puede tener UNA persona asociada (relación 1:1).
CREATE TRIGGER trg_membresia_solista_ins
BEFORE INSERT ON membresia
FOR EACH ROW
BEGIN
    IF (SELECT tipo FROM artista WHERE artista_id = NEW.artista_id) = 'Solista'
       AND EXISTS (SELECT 1 FROM membresia
                   WHERE artista_id = NEW.artista_id
                     AND persona_id <> NEW.persona_id) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El artista solista ya tiene una persona asociada';
    END IF;
END//

CREATE TRIGGER trg_membresia_solista_upd
BEFORE UPDATE ON membresia
FOR EACH ROW
BEGIN
    IF (SELECT tipo FROM artista WHERE artista_id = NEW.artista_id) = 'Solista'
       AND EXISTS (SELECT 1 FROM membresia
                   WHERE artista_id = NEW.artista_id
                     AND persona_id <> NEW.persona_id
                     AND membresia_id <> OLD.membresia_id) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El artista solista ya tiene una persona asociada';
    END IF;
END//

-- Un género / sello no puede ser su propio padre.
CREATE TRIGGER trg_genero_padre_upd
BEFORE UPDATE ON genero
FOR EACH ROW
BEGIN
    IF NEW.genero_padre_id = NEW.genero_id THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Un género no puede ser su propio padre';
    END IF;
END//

CREATE TRIGGER trg_sello_padre_upd
BEFORE UPDATE ON sello
FOR EACH ROW
BEGIN
    IF NEW.sello_padre_id = NEW.sello_id THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Un sello no puede ser su propio padre';
    END IF;
END//

DELIMITER ;

-- ---------------------------------------------------------------------
--  Vista: todas las participaciones de una persona en canciones,
--  ya sea a través de un artista (banda/solista) o con crédito propio.
-- ---------------------------------------------------------------------
CREATE VIEW v_participacion_persona AS
SELECT p.persona_id,
       COALESCE(p.nombre_conocido, p.nombre_legal) AS persona,
       c.cancion_id,
       c.titulo                                    AS cancion,
       a.nombre                                    AS via,
       CAST(ca.rol AS CHAR(30))                    AS rol
FROM persona p
JOIN membresia m        ON m.persona_id  = p.persona_id
JOIN artista a          ON a.artista_id  = m.artista_id
JOIN credito_artista ca ON ca.artista_id = a.artista_id
JOIN cancion c          ON c.cancion_id  = ca.cancion_id
UNION
SELECT p.persona_id,
       COALESCE(p.nombre_conocido, p.nombre_legal),
       c.cancion_id,
       c.titulo,
       '(crédito individual)',
       CAST(cp.rol AS CHAR(30))
FROM persona p
JOIN credito_persona cp ON cp.persona_id = p.persona_id
JOIN cancion c          ON c.cancion_id  = cp.cancion_id;
