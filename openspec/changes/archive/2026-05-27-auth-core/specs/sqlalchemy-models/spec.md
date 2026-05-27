# Delta for SQLAlchemy Models

## MODIFIED Requirements

### Requirement: Model File Structure

The system SHALL provide one model file per table under `backend/src/models/`, re-exported via `__init__.py`. The `usuario.py` model SHALL include `email VARCHAR(255) UNIQUE`, `estado BOOLEAN DEFAULT True`, and `rol` constrained to `SOL | EST | AYU | PRO | ADM`.

(Previously: Usuario had no email, estado, or rol validation.)

14 models: usuario, semestre, estudiante, articulo, bloque_horario, curso, grupo_estudiante, impresion, movimiento_stock, ayudantia, inscripcion_ayudantia, uso_impresora, reserva, bloque_reservado.

#### Scenario: all models importable

- GIVEN `__init__.py` re-exports all models
- WHEN `from backend.src.models import *` executes
- THEN all 14 classes available

#### Scenario: Usuario has new columns

- GIVEN the `Usuario` model
- WHEN `email`, `estado`, `rol` accessed
- THEN columns exist with correct types/constraints

## ADDED Requirements

### Requirement: Usuario Email Unique

`Usuario.email` SHALL be `VARCHAR(255)` with `unique=True`, `nullable=True`.

| Scenario | Given | When | Then |
|----------|-------|------|------|
| duplicate rejected | Usuario with `email="test@uc.cl"` exists | second Usuario same email | `IntegrityError` |

### Requirement: Usuario Estado Default

`Usuario.estado` SHALL be `BOOLEAN` with `default=True`, `server_default=text("true")`.

| Scenario | Given | When | Then |
|----------|-------|------|------|
| active by default | new Usuario without `estado` | row inserted | `estado` is `True` |

### Requirement: Usuario Rol Enum Validation

`Usuario.rol` SHALL be constrained to `SOL | EST | AYU | PRO | ADM`. Invalid values raise `ValueError` before DB insertion.

| Scenario | Given | When | Then |
|----------|-------|------|------|
| valid rol | `rol="ADM"` | Usuario created | row inserted |
| invalid rol | `rol="INVALID"` | Usuario created | `ValueError` |

## Acceptance Criteria (Updated)

- [ ] All 14 models exist under `backend/src/models/`
- [ ] `Usuario` has `email VARCHAR(255) UNIQUE`, `estado BOOLEAN DEFAULT True`, `rol` validates enum
- [ ] All 15 FK constraints defined (unchanged)
- [ ] `ruff check backend/src/models/` passes
