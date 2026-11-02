# Delta de spec

## ADDED Requirements

### Requirement: Hechos verificables de King Crimson
Las consultas sobre King Crimson DEBEN (MUST) reflejar todas sus formaciones con fechas reales, sin incluir otros proyectos de sus integrantes.

#### Scenario: Formaciones distintas según la fecha
- **WHEN** se piden los integrantes de King Crimson en 1969-06-01, 1974-06-01, 1981-06-01 y 1995-06-01
- **THEN** cada fecha devuelve una formación distinta: el quinteto original, el cuarteto de *Red*, el de *Discipline* y el doble trío

#### Scenario: Historial completo
- **WHEN** se pide el historial de integrantes de King Crimson
- **THEN** aparece cada periodo de membresía, por ejemplo los cuatro periodos de Robert Fripp

#### Scenario: Solo King Crimson
- **WHEN** se buscan los artistas de los que fue integrante Robert Fripp
- **THEN** solo aparece King Crimson
