# Diseño: tabla-arte-artista

## Contexto

Ver `proposal.md`. La base usa `utf8mb4` / `utf8mb4_unicode_ci` por defecto, así que una columna `TEXT` admite los caracteres de bloques y marcos. El formato de los archivos de arte y su carga son de la spec `cargador-datos`; aquí solo se define el almacenamiento.

## Objetivos / No objetivos

**Objetivos:** guardar el arte sin pérdidas y mantener el diagrama ER sincronizado.

**No objetivos:** el contenido del arte (spec `arte-artistas`), las reglas de ancho y caracteres de los archivos (pruebas de `arte-artistas`) y su presentación (specs de la CLI).

## Decisiones

### 1. Tabla aparte con PK = FK
La relación es 1:1 opcional, así que la PK es el propio `artista_id`, lo que impide un segundo arte para el mismo artista. Una columna `arte` en `artista` habría evitado la tabla, pero el roadmap pide una tabla nueva y así el esquema original de `artista` no se toca.

### 2. `TEXT NOT NULL`
`TEXT` admite 65 535 bytes, más que suficiente para 80 columnas por unas 20 líneas (con bloques de 3 bytes, son unos 5 KB). No hace falta `MEDIUMTEXT`. Se usa `NOT NULL` porque una fila sin arte no tiene sentido: si un artista no tiene arte, simplemente no tiene fila.

### 3. Lugar en el esquema
La tabla va en la sección "Personas y artistas", justo después de `artista_genero`, y el comentario de cabecera explica el formato. Tiene `ON DELETE CASCADE`, igual que las demás tablas dependientes de `artista`.

### 4. Generación del PNG
`scripts/generar_diagrama.sh` ejecuta `docker run --rm -u "$(id -u):$(id -g)" -v "$PWD/Diagrama:/data:z" minlag/mermaid-cli -i musica_er.mmd -o musica_er.png` con un ancho y un fondo fijos para que el resultado sea estable. Se usa `:z` por SELinux.

### 5. Pruebas con `root` en una transacción
El usuario de la aplicación es de solo lectura, así que la prueba de ida y vuelta usa la conexión `root`. Dentro de una transacción inserta un artista ficticio, marcado como tal, junto con su arte; lee el arte, comprueba la cascada y termina con un `ROLLBACK`, de modo que la base no queda modificada.

## Riesgos / Compromisos

- [Alguien guarda arte con finales CRLF] → La base los conserva tal cual. La normalización a LF se exige en los archivos fuente (`.gitattributes`, pruebas de `arte-artistas`).
- [La imagen `minlag/mermaid-cli` cambia y el PNG varía un poco] → Solo afecta al aspecto visual del PNG. El `.mmd` es la fuente.
