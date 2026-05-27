# Container Configuration Specification

## Purpose

Define container build configuration, production/development dependency separation, environment variable injection via docker-compose, and build context filtering via `.dockerignore` for secure, lean Docker images.

## Requirements

### Requirement: Production/Development Dependency Separation

The system SHALL maintain two dependency files: `backend/requirements.txt` for production-only dependencies and `backend/requirements-dev.txt` for development/testing dependencies. The production Dockerfile SHALL install from `requirements.txt` only.

| File | Purpose | Dependencies |
|------|---------|-------------|
| requirements.txt | Production image | fastapi, uvicorn, sqlalchemy, psycopg2-binary, python-dotenv |
| requirements-dev.txt | Local development/testing | pytest, pytest-asyncio, pytest-cov, httpx, ruff, sqlfluff, yamllint |

#### Scenario: production image has no dev dependencies

- GIVEN the Dockerfile builds from `requirements.txt`
- WHEN the image is built
- THEN only production packages are installed
- AND pytest, ruff, sqlfluff, yamllint are NOT present in the image

#### Scenario: developer can install dev dependencies locally

- GIVEN a developer runs `pip install -r requirements-dev.txt`
- WHEN the command completes
- THEN all testing and linting tools are available
- AND production dependencies are included as transitive deps

### Requirement: Dockerfile Structure for Flattened Source

The system SHALL provide a Dockerfile that copies source files directly into `/app/` using `COPY ./src/ .` and sets `CMD` to reference `main:app` (not `src.main:app`).

#### Scenario: container imports resolve at runtime

- GIVEN the Dockerfile copies `./src/` contents to `/app/`
- WHEN the container starts and imports `main`
- THEN `main:app` resolves correctly
- AND no `ModuleNotFoundError` occurs

#### Scenario: CMD references correct module path

- GIVEN the Dockerfile sets the container entrypoint
- WHEN the container starts
- THEN CMD uses `main:app` (not `src.main:app`)
- AND uvicorn starts the FastAPI application

### Requirement: Environment Injection via docker-compose

The system SHALL inject database environment variables into the backend service via `docker-compose.yml` `environment:` block. Variables SHALL be sourced from `.env` file or host environment.

#### Scenario: backend service receives all required env vars

- GIVEN `docker-compose.yml` defines backend service
- WHEN `docker compose up backend` starts
- THEN environment block includes `POSTGRES_HOST`, `POSTGRES_APP_USER`, `POSTGRES_APP_PASSWORD`, `POSTGRES_DB`
- AND `POSTGRES_PORT` defaults to 5432 if not specified

#### Scenario: env vars reference host .env values

- GIVEN `.env` file defines `POSTGRES_APP_USER=myappuser`
- WHEN docker-compose substitutes `${POSTGRES_APP_USER}`
- THEN the backend container receives `POSTGRES_APP_USER=myappuser`
- AND the value matches the app user created by DB init script

### Requirement: Build Context Filtering via .dockerignore

The system SHALL provide `backend/.dockerignore` to exclude non-production files from Docker build context. This SHALL prevent secrets, caches, test files, and virtual environments from being sent to the Docker daemon.

#### Scenario: .dockerignore excludes sensitive files

- GIVEN `backend/.dockerignore` exists
- WHEN Docker builds the image
- THEN `.env` is excluded from build context
- AND `.venv/` is excluded from build context

#### Scenario: .dockerignore excludes non-essential files

- GIVEN `backend/.dockerignore` exists
- WHEN Docker builds the image
- THEN `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `*.egg-info/`, `.coverage`, `htmlcov/`, and `tests/` are excluded
- AND build context size is minimized

## Scenarios

| # | Scenario | Type | Requirement |
|---|----------|------|-------------|
| 1 | Production image excludes dev deps | Happy path | Production/Development Dependency Separation |
| 2 | Local dev install includes all tools | Happy path | Production/Development Dependency Separation |
| 3 | Container imports resolve without src prefix | Happy path | Dockerfile Structure |
| 4 | CMD uses main:app not src.main:app | Happy path | Dockerfile Structure |
| 5 | Backend service receives all env vars | Happy path | Environment Injection |
| 6 | docker-compose substitutes .env values | Happy path | Environment Injection |
| 7 | .dockerignore excludes .env and .venv | Edge case | Build Context Filtering |
| 8 | .dockerignore excludes caches and tests | Edge case | Build Context Filtering |
