# Delta de spec

## Purpose

Verifica automáticamente cada cambio enviado al repositorio con el lint y las pruebas, incluidas las de integración contra una base MySQL real, en las versiones de Python soportadas.

## ADDED Requirements

### Requirement: Verificación automática de cada cambio
El repositorio DEBE (MUST) ejecutar en GitHub Actions, en cada push y en cada pull request contra `main`, el lint (`ruff check` y `ruff format --check`) y las pruebas en Python 3.12 y 3.14.

#### Scenario: Pull request correcta
- **WHEN** se abre una pull request cuyo código pasa el lint y las pruebas
- **THEN** los checks de CI terminan en verde para Python 3.12 y 3.14

#### Scenario: Error de lint
- **WHEN** una pull request introduce código que no pasa `ruff check`
- **THEN** el check de CI de esa pull request falla

### Requirement: Pruebas de integración obligatorias en la CI
La CI DEBE (MUST) levantar la base con Docker Compose y ejecutar las pruebas con `WIKITUNES_EXIGIR_BD=1`, de modo que una prueba de integración nunca se salte en silencio.

#### Scenario: La base no arranca en la CI
- **WHEN** la base no logra arrancar durante la ejecución de la CI
- **THEN** el check falla en lugar de saltar las pruebas de integración
