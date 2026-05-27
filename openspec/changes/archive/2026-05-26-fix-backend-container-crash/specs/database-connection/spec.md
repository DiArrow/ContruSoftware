# Delta for database-connection

## MODIFIED Requirements

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

### Requirement: .env.example Documentation

The system SHALL provide `backend/.env.example` documenting all required database environment variables with placeholder values.

(Previously: Documented `POSTGRES_USER`/`POSTGRES_PASSWORD`; now documents `POSTGRES_APP_USER`/`POSTGRES_APP_PASSWORD`.)

#### Scenario: env example is complete

- GIVEN `.env.example` exists
- WHEN the file is read
- THEN all 5 required variables are listed with descriptions
- AND variable names use `POSTGRES_APP_USER`/`POSTGRES_APP_PASSWORD`
- AND no real credentials are included

## ADDED Requirements

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

## Scenarios

| # | Scenario | Type | Requirement |
|---|----------|------|-------------|
| 1 | Valid APP_ env vars produce correct URL | Happy path | Environment-Driven Configuration |
| 2 | Missing POSTGRES_APP_PASSWORD raises ValueError | Edge case | Environment-Driven Configuration |
| 3 | Old POSTGRES_USER env var rejected | Edge case | Environment-Driven Configuration |
| 4 | .env.example documents APP_ variables | Happy path | .env.example Documentation |
| 5 | Source file imports resolve without src prefix | Happy path | Direct Import Convention |
| 6 | models/__init__.py uses direct imports | Happy path | Direct Import Convention |
| 7 | Test imports resolve without src prefix | Happy path | Direct Import Convention |
| 8 | pytest pythonpath resolves direct imports | Happy path | Direct Import Convention |
