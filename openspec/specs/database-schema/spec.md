# Database Schema Specification

## Purpose
Define the DDL for all 14 tables of the ContruSoftware PostgreSQL schema, ensuring idempotent execution, correct dependency ordering, and SQLFluff compliance.

## Requirements

### Requirement: Complete Table Definitions
The system SHALL define all 14 tables with correct columns, types, constraints, and primary keys.

| Table | Columns | PK Type | FK Count |
|-------|---------|---------|----------|
| usuario | 7 | VARCHAR(36) | 0 |
| semestre | 7 | VARCHAR(36) | 0 |
| estudiante | 5 | VARCHAR(36) | 0 |
| articulo | 6 | VARCHAR(36) | 0 |
| bloque_horario | 5 | VARCHAR(36) | 0 |
| curso | 6 | VARCHAR(36) | 1 (semestre) |
| grupo_estudiante | 2 | COMPOSITE | 1 (estudiante) |
| impresion | 6 | VARCHAR(36) | 2 (usuario, articulo) |
| movimiento_stock | 5 | VARCHAR(36) | 1 (articulo) |
| ayudantia | 6 | VARCHAR(36) | 1 (curso) |
| inscripcion_ayudantia | 4 | COMPOSITE | 2 (ayudantia, estudiante) |
| uso_impresora | 5 | VARCHAR(36) | 2 (estudiante, ayudantia) |
| reserva | 5 | VARCHAR(36) | 2 (usuario, ayudantia) |
| bloque_reservado | 2 | COMPOSITE | 2 (bloque_horario, reserva) |

#### Scenario: All 14 tables created
- GIVEN an empty PostgreSQL database
- WHEN the init script is executed
- THEN all 14 tables exist with correct columns, types, and constraints
- AND `\dt` returns exactly 14 rows

#### Scenario: Missing table detected
- GIVEN the init script is executed
- WHEN counting tables in information_schema
- THEN the count equals 14

### Requirement: Dependency Ordering
The system MUST create tables in dependency order — no-FK tables first, then tables whose dependencies are satisfied.

#### Scenario: Correct creation order
- GIVEN the init script defines 14 tables
- WHEN executed top to bottom
- THEN all 5 base tables created before any referencing table
- AND no "relation does not exist" error

#### Scenario: Reverse drop order
- GIVEN all 14 tables exist
- WHEN DROP section runs before CREATE
- THEN tables dropped in reverse dependency order using CASCADE

### Requirement: Idempotent Execution
The system SHALL support repeated execution using `DROP TABLE IF EXISTS ... CASCADE` + `CREATE TABLE`.

#### Scenario: First execution
- GIVEN an empty database
- WHEN the init script is executed
- THEN all 14 tables created, no warnings

#### Scenario: Re-execution
- GIVEN tables exist with data
- WHEN the init script is executed again
- THEN tables dropped (CASCADE) and recreated without errors

### Requirement: SQLFluff Compliance
The system SHALL pass `sqlfluff lint --dialect postgres` — keywords UPPERCASE, identifiers lowercase.

#### Scenario: Lint passes clean
- GIVEN the init.sql file
- WHEN `sqlfluff lint db/init/init.sql --dialect postgres` is run
- THEN exit code 0, no violations

#### Scenario: Naming convention violation
- GIVEN uppercase identifiers (e.g., `CREATE TABLE USUARIO`)
- WHEN sqlfluff lint is run
- THEN a naming violation is reported

### Requirement: Foreign Key Integrity
The system MUST define all FK constraints with named constraints. `ref_impresora` in `uso_impresora` has no FK (documented gap).

#### Scenario: All FK constraints defined
- WHEN counting FK constraints in information_schema
- THEN the count equals 15

#### Scenario: Orphan FK reference
- GIVEN a FK references a non-existent table
- WHEN the init script is executed
- THEN the script fails with "relation does not exist"
