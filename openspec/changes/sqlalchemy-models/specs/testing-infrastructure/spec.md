# Testing Infrastructure Specification

## Purpose

Establish pytest framework with async support, test database fixtures, model verification tests, connection tests, and coverage requirements for the SQLAlchemy integration.

## Requirements

### Requirement: Pytest Framework Setup

The system SHALL install and configure pytest, pytest-asyncio, and pytest-cov. A `pyproject.toml` section SHALL define asyncio mode and coverage thresholds.

| Component | Version | Purpose |
|-----------|---------|---------|
| pytest | latest | Test runner |
| pytest-asyncio | latest | Async test support |
| pytest-cov | latest | Coverage reporting |
| httpx | latest | FastAPI TestClient |

#### Scenario: pytest discovers and runs tests

- GIVEN pytest is installed and `pyproject.toml` configured
- WHEN `pytest backend/tests/` is executed
- THEN all test files are discovered and executed
- AND exit code is 0 when all tests pass

#### Scenario: coverage threshold enforced

- GIVEN pytest-cov is configured with 80% threshold for `models/` and `database.py`
- WHEN tests run with coverage enabled
- THEN coverage report shows ≥80% on target modules
- AND build fails if threshold is not met

### Requirement: Test Database Fixtures

The system SHALL provide `conftest.py` with fixtures for test database engine, session, and FastAPI TestClient. Fixtures SHALL use a separate `POSTGRES_TEST_DB` database.

#### Scenario: test session fixture yields and cleans

- GIVEN `conftest.py` defines a `db_session` fixture
- WHEN a test requests the fixture
- THEN a fresh session is yielded from the test database engine
- AND the session is rolled back after the test completes

#### Scenario: isolated test database

- GIVEN `POSTGRES_TEST_DB` env var points to a test database
- WHEN test fixtures initialize
- THEN connections target the test database only
- AND the development database is never affected

### Requirement: Model Verification Tests

The system SHALL include `test_models.py` that verifies each of the 14 models maps correctly to the SQL schema defined in `db/init/01-init.sql`.

| Verification | Description |
|--------------|-------------|
| Table name | Model `__tablename__` matches SQL table |
| Column names | All SQL columns exist in model |
| Column types | SQLAlchemy types match SQL types |
| Primary keys | PK columns match SQL PK definitions |
| Foreign keys | FK constraints reference correct tables/columns |

#### Scenario: model table name matches SQL

- GIVEN the `Usuario` model and `usuario` table in `01-init.sql`
- WHEN the test checks `Usuario.__tablename__`
- THEN the value equals `"usuario"`

#### Scenario: model columns match SQL schema

- GIVEN the `Curso` model with columns from SQL
- WHEN the test inspects `Curso.__table__.columns`
- THEN column names match: `id_curso`, `nombre`, `ref_semestre`, `bloque_id`, `creado_en`, `actualizado_en`
- AND column types match: `VARCHAR(36)`, `VARCHAR(255)`, `VARCHAR(36)`, `VARCHAR(36)`, `TIMESTAMP`, `TIMESTAMP`

### Requirement: Connection Tests

The system SHALL include `test_connection.py` that verifies database connectivity and the health check endpoint.

#### Scenario: database connection succeeds

- GIVEN PostgreSQL is running and env vars are set
- WHEN the connection test executes `SELECT 1`
- THEN the query returns successfully
- AND no exception is raised

#### Scenario: health endpoint returns ok

- GIVEN the FastAPI app is running with DB connected
- WHEN `GET /health` is called via TestClient
- THEN response status is 200
- AND response body is `{"status": "ok"}`

## Acceptance Criteria

- [ ] `pytest backend/tests/` passes with zero failures
- [ ] Coverage ≥80% on `models/` and `database.py`
- [ ] All 14 models verified against `01-init.sql` schema
- [ ] Health endpoint test passes
- [ ] Test database is isolated from development data
