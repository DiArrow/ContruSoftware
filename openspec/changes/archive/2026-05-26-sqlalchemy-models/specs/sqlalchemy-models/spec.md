# SQLAlchemy Models Specification

## Purpose

Define 14 SQLAlchemy ORM models that exactly mirror the SQL schema in `db/init/01-init.sql`, including columns, types, foreign keys, relationships, UUID primary keys, and timestamps.

## Requirements

### Requirement: Model File Structure

The system SHALL provide one model file per table under `backend/src/models/`. The `__init__.py` SHALL re-export all 14 models. Models SHALL be created in dependency order so `relationship()` backrefs resolve.

| File | Table | Dependencies |
|------|-------|-------------|
| `usuario.py` | usuario | None |
| `semestre.py` | semestre | None |
| `estudiante.py` | estudiante | None |
| `articulo.py` | articulo | None |
| `bloque_horario.py` | bloque_horario | None |
| `curso.py` | curso | semestre |
| `grupo_estudiante.py` | grupo_estudiante | estudiante |
| `impresion.py` | impresion | usuario, articulo |
| `movimiento_stock.py` | movimiento_stock | articulo |
| `ayudantia.py` | ayudantia | curso |
| `inscripcion_ayudantia.py` | inscripcion_ayudantia | ayudantia, estudiante |
| `uso_impresora.py` | uso_impresora | estudiante, ayudantia |
| `reserva.py` | reserva | usuario, ayudantia |
| `bloque_reservado.py` | bloque_reservado | bloque_horario, reserva |

#### Scenario: all models are importable

- GIVEN `backend/src/models/__init__.py` re-exports all models
- WHEN `from backend.src.models import *` is executed
- THEN all 14 model classes are available
- AND no circular import errors occur

### Requirement: Primary Keys as UUID Strings

All models SHALL use `VARCHAR(36)` for primary key columns, matching the SQL schema. Composite PKs SHALL use multiple `primary_key=True` columns.

#### Scenario: single-column PK model

- GIVEN the `Usuario` model
- WHEN `Usuario.__table__.primary_key.columns` is inspected
- THEN it contains `id_usuario` with type `VARCHAR(36)`

#### Scenario: composite PK model

- GIVEN the `GrupoEstudiante` model
- WHEN its primary key is inspected
- THEN it contains both `ref_grupo` and `ref_estudiante` as PK columns

### Requirement: Foreign Key Constraints

Models SHALL define `ForeignKey()` constraints matching the SQL schema exactly. String-based references SHALL be used to avoid circular imports.

| Model | FK Column | References |
|-------|-----------|------------|
| Curso | ref_semestre | semestre.id_semestre |
| GrupoEstudiante | ref_estudiante | estudiante.id_estudiante |
| Impresion | ref_usuario | usuario.id_usuario |
| Impresion | ref_articulo | articulo.id_articulo |
| MovimientoStock | ref_articulo | articulo.id_articulo |
| Ayudantia | ref_curso | curso.id_curso |
| InscripcionAyudantia | ref_ayudantia | ayudantia.id_ayudantia |
| InscripcionAyudantia | ref_estudiante | estudiante.id_estudiante |
| UsoImpresora | ref_estudiante | estudiante.id_estudiante |
| UsoImpresora | ref_ayudantia | ayudantia.id_ayudantia |
| Reserva | ref_usuario | usuario.id_usuario |
| Reserva | ref_ayudantia | ayudantia.id_ayudantia |
| BloqueReservado | bloque_id | bloque_horario.id_bloque_horario |
| BloqueReservado | reserva_id | reserva.id_reserva |

**Note**: `uso_impresora.ref_impresora` has no FK in SQL — model SHALL NOT define one.

#### Scenario: FK constraint matches SQL

- GIVEN the `Curso` model
- WHEN `Curso.ref_semestre.property.argument` is inspected
- THEN it references `semestre.id_semestre`

### Requirement: Timestamps with server_default

Models with `creado_en` and `actualizado_en` columns SHALL use `server_default=func.now()` for automatic timestamp assignment.

| Model | creado_en | actualizado_en |
|-------|-----------|----------------|
| Usuario | Yes | Yes |
| Semestre | Yes | Yes |
| Curso | Yes | Yes |
| Articulo | No | Yes |
| Others | No | No |

#### Scenario: timestamp auto-populates

- GIVEN a `Usuario` instance is inserted without `creado_en`
- WHEN the row is committed
- THEN `creado_en` is set by the database default

### Requirement: SQLAlchemy Relationships

Models SHALL define `relationship()` where foreign keys exist, using `lazy="select"` and string-based backref names to avoid circular imports.

#### Scenario: relationship resolves correctly

- GIVEN a `Curso` instance with a valid `ref_semestre`
- WHEN `curso.semestre` is accessed
- THEN the related `Semestre` object is loaded
- AND no circular import error occurs

## Acceptance Criteria

- [ ] All 14 models exist as individual files under `backend/src/models/`
- [ ] Each model's columns match `01-init.sql` exactly
- [ ] All 15 FK constraints are defined (matching SQL)
- [ ] `ref_impresora` in `UsoImpresora` has no FK (matches SQL gap)
- [ ] `__init__.py` re-exports all 14 models
- [ ] `ruff check backend/src/models/` passes with zero errors
