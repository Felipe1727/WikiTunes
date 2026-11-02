# consultas-catalogo Specification

## Purpose
Ofrece a la interfaz consultas tipadas y de solo lectura sobre el catálogo musical: los procedimientos almacenados, las fichas, los listados para autocompletar y errores de base de datos en español.

## Requirements

### Requirement: Procedimientos almacenados tipados
La capa DEBE (MUST) exponer los 5 procedimientos (`sp_canciones_de_persona`, `sp_subgeneros`, `sp_tracklist`, `sp_integrantes_en_fecha` y `sp_historial_integrantes`) como funciones que devuelven dataclasses, con los ids necesarios para navegar.

#### Scenario: Tracklist con sus dos resultados
- **WHEN** se pide el tracklist de *Abbey Road*
- **THEN** se obtienen las 17 pistas con el id de cada canción y el resumen con la duración total formateada

#### Scenario: Canciones de una persona
- **WHEN** se piden las canciones de Paul McCartney
- **THEN** cada participación incluye el id de la canción, y las dos versiones de *Get Back* tienen ids distintos

### Requirement: Fichas
La capa DEBE (MUST) devolver la ficha de un artista (datos, géneros, arte, discografía e historial), de una persona (datos y artistas de los que fue integrante), de una canción (intérpretes, créditos, géneros y álbumes) y de un género (árbol, y artistas y álbumes del género o de sus subgéneros).

#### Scenario: Ficha de género
- **WHEN** se pide la ficha de Rock progresivo
- **THEN** incluye sus subgéneros y a King Crimson y *Red*, que están clasificados en ellos

#### Scenario: Elemento inexistente
- **WHEN** se pide la ficha de un id que no existe
- **THEN** se devuelve `None` sin error

### Requirement: Listados para el autocompletado
La capa DEBE (MUST) devolver, ordenados, todas las personas, los artistas, los álbumes, los géneros y las canciones con su id.

#### Scenario: Personas
- **WHEN** se piden las personas
- **THEN** la lista incluye a Paul McCartney con su id

### Requirement: Errores en español
Si la base no está disponible, la capa DEBE (MUST) lanzar una excepción propia con un mensaje en español que sugiera levantarla con Docker Compose.

#### Scenario: Base caída
- **WHEN** se intenta conectar a un puerto sin servidor
- **THEN** se lanza `ErrorDeConexion` con un mensaje que menciona `docker compose up -d --wait`

### Requirement: Artistas de un álbum
La capa DEBE (MUST) devolver los artistas de la portada de un álbum, en su orden.

#### Scenario: Álbum de Wings
- **WHEN** se piden los artistas de *Band on the Run*
- **THEN** se obtiene Wings
