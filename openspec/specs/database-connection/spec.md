# Database Connection Specification

## Purpose

Define database configuration module, engine/session creation, dependency injection via `get_db`, environment variable management for PostgreSQL connectivity, and import conventions for internal module references.

## Requirements

### Requirement: Environment-Driven Configuration

The system SHALL provide `backend/src/config.py` that reads database connection parameters from environment variables and constructs `SQLALCHEMY_DATABASE_URL`. Missing required variables SHALL raise `ValueError`.

(Previously: Used `POSTGRES_USER`/`POSTGRES_PASSWORD`; now uses `POSTGRES_APP_USER`/`POSTGRES_APP_PASSWORD` to match app user created by DB init script.)

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| POSTGRES_HOST | Yes | — | Database host |
| POSTGRES_PORT | No | 5432 | Database port |
| POSTGRES_APP_USER | Yes | — | Application database user (not admin) |
| POSTGRES_APP_PASSWORD | Yes | — | Application database password (not admin) |
| POSTGRES_DB | Yes | — | Database name |

#### Scenario: valid env vars produce connection URL

- GIVEN all required env vars are set (`POSTGRES_HOST`, `POSTGRES_APP_USER`, `POSTGRES_APP_PASSWORD`, `POSTGRES_DB`)
- WHEN `config.py` builds the database URL
- THEN URL format is `postgresql+psycopg2://user:pass@host:port/db`
- AND no credentials are hardcoded

#### Scenario: missing env var raises error

- GIVEN `POSTGRES_APP_PASSWORD` is not set
- WHEN config module is imported
- THEN `ValueError` is raised
- AND error message identifies the missing variable

#### Scenario: old env var names no longer recognized

- GIVEN only `POSTGRES_USER` and `POSTGRES_PASSWORD` are set (without `POSTGRES_APP_USER`/`POSTGRES_APP_PASSWORD`)
- WHEN config module is imported
- THEN `ValueError` is raised for missing `POSTGRES_APP_USER`

### Requirement: Engine and Session Factory

The system SHALL provide `backend/src/database.py` that exports `engine`, `SessionLocal`, and `Base`. The engine SHALL use the URL from `config.py`.

#### Scenario: engine is created from config URL

- GIVEN `SQLALCHEMY_DATABASE_URL` is valid
- WHEN `database.py` is imported
- THEN `engine` is created and exportable
- AND `SessionLocal` is a configured session factory

#### Scenario: Base is declarative and exportable

- GIVEN `database.py` defines `Base = declarative_base()`
- WHEN a model file imports `Base`
- THEN the model can inherit from it
- AND `Base.metadata.create_all()` creates all tables

### Requirement: Dependency Injection via get_db

The system SHALL provide a `get_db()` generator function that yields a `SessionLocal` instance and ensures the session is closed after use. FastAPI routes SHALL use `Depends(get_db)`.

#### Scenario: session yields and closes

- GIVEN a FastAPI route uses `Depends(get_db)`
- WHEN the route handler executes
- THEN a session is yielded to the handler
- AND the session is closed after the response is sent

#### Scenario: session rollback on error

- GIVEN a route raises an exception during execution
- WHEN `get_db` cleanup runs
- THEN the session is rolled back
- AND no partial writes persist

### Requirement: .env.example Documentation

The system SHALL provide `backend/.env.example` documenting all required database environment variables with placeholder values.

(Previously: Documented `POSTGRES_USER`/`POSTGRES_PASSWORD`; now documents `POSTGRES_APP_USER`/`POSTGRES_APP_PASSWORD`.)

#### Scenario: env example is complete

- GIVEN `.env.example` exists
- WHEN the file is read
- THEN all 5 required variables are listed with descriptions
- AND variable names use `POSTGRES_APP_USER`/`POSTGRES_APP_PASSWORD`
- AND no real credentials are included

### Requirement: Direct Import Convention

The system SHALL use direct imports (without `src.` prefix) for all internal module references in source files under `backend/src/` and test files under `backend/tests/`. This matches the Docker container layout where `COPY ./src/ .` places source files directly in `/app/`.

#### Scenario: source file uses direct imports

- GIVEN a source file in `backend/src/` needs to import another internal module
- WHEN the import statement is written
- THEN it uses `from database import ...`, `from config import ...`, or `from models.xxx import ...`
- AND it does NOT use `from src.database`, `from src.config`, or `from src.models`

#### Scenario: models __init__ uses direct imports

- GIVEN `backend/src/models/__init__.py` re-exports model classes
- WHEN the file is read
- THEN all imports use `from models.xxx import Xxx` format
- AND no `from src.models.xxx` imports exist

#### Scenario: test files use direct imports

- GIVEN a test file in `backend/tests/` needs to import application modules
- WHEN the import statement is written
- THEN it uses `from database import ...`, `from main import app`, or `from models.xxx import ...`
- AND it does NOT use `from src.xxx` prefix

#### Scenario: pyproject.toml pythonpath enables direct imports

- GIVEN `pyproject.toml` configures pytest
- WHEN tests are run from `backend/` directory
- THEN `pythonpath = ["src"]` resolves `from database` to `backend/src/database.py`
- AND all direct imports succeed without `ModuleNotFoundError`

## Acceptance Criteria

- [ ] `config.py` validates all required env vars on import (uses `POSTGRES_APP_USER`/`POSTGRES_APP_PASSWORD`)
- [ ] `database.py` exports `engine`, `SessionLocal`, `Base`, `get_db`
- [ ] `get_db` yields session and closes/rolls back correctly
- [ ] `.env.example` documents all required variables including `POSTGRES_APP_USER`/`POSTGRES_APP_PASSWORD`
- [ ] No hardcoded credentials in any Python file
- [ ] All source files use direct imports (no `from src.xxx` prefix)
- [ ] `pyproject.toml` pythonpath enables direct imports for test resolution
