# Database Connection Specification

## Purpose

Define database configuration module, engine/session creation, dependency injection via `get_db`, and environment variable management for PostgreSQL connectivity.

## Requirements

### Requirement: Environment-Driven Configuration

The system SHALL provide `backend/src/config.py` that reads database connection parameters from environment variables and constructs `SQLALCHEMY_DATABASE_URL`. Missing required variables SHALL raise `ValueError`.

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| POSTGRES_HOST | Yes | — | Database host |
| POSTGRES_PORT | No | 5432 | Database port |
| POSTGRES_USER | Yes | — | Database user |
| POSTGRES_PASSWORD | Yes | — | Database password |
| POSTGRES_DB | Yes | — | Database name |

#### Scenario: valid env vars produce connection URL

- GIVEN all required env vars are set
- WHEN `config.py` builds the database URL
- THEN URL format is `postgresql+psycopg2://user:pass@host:port/db`
- AND no credentials are hardcoded

#### Scenario: missing env var raises error

- GIVEN `POSTGRES_PASSWORD` is not set
- WHEN config module is imported
- THEN `ValueError` is raised
- AND error message identifies the missing variable

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

#### Scenario: env example is complete

- GIVEN `.env.example` exists
- WHEN the file is read
- THEN all 5 required variables are listed with descriptions
- AND no real credentials are included

## Acceptance Criteria

- [ ] `config.py` validates all required env vars on import
- [ ] `database.py` exports `engine`, `SessionLocal`, `Base`, `get_db`
- [ ] `get_db` yields session and closes/rolls back correctly
- [ ] `.env.example` documents all required variables
- [ ] No hardcoded credentials in any Python file
