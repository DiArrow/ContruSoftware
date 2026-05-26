# Proposal: SQLAlchemy Models & Database Integration

## Intent

The FastAPI backend (`backend/src/main.py`) is a skeleton with no database connection. We need SQLAlchemy ORM models mirroring the 14 tables from `db/init/01-init.sql`, a configuration/session module, a health check endpoint, and pytest infrastructure with model/connection tests — so the app can persist data via PostgreSQL with verified correctness.

**Note**: The input spec references "13 models" but `01-init.sql` defines **14 tables**. This proposal covers all 14.

## Scope

### In Scope
- 14 SQLAlchemy models (one file each) reflecting `01-init.sql` exactly
- `backend/src/config.py` — env vars + `SQLALCHEMY_DATABASE_URL`
- `backend/src/database.py` — `engine`, `SessionLocal`, `Base`, `get_db`
- `backend/src/models/__init__.py` — re-exports all models
- `GET /health` endpoint verifying DB connectivity
- Update `main.py` — remove skeleton code, add health route
- `backend/.env.example` — document required env vars
- **Pytest setup**: pytest, pytest-asyncio, pytest-cov in requirements; `conftest.py` with test DB fixtures
- **Model tests**: verify each model maps to SQL schema (columns, types, FKs)
- **Connection tests**: verify DB connection and health check endpoint
- PEP 8 / Black / Ruff compliance, type hints, max 3 args per function

### Out of Scope
- Alembic migrations (future change)
- CRUD endpoints / repositories / services
- `.gitignore` fix for `__pycache__`, `.ruff_cache`, `venv`

## Capabilities

### New Capabilities
- `sqlalchemy-models`: 14 ORM models with columns, types, FKs, and `relationship()` matching `01-init.sql`
- `database-connection`: Engine, session factory, `Base`, `get_db` dependency injection, env-driven config
- `health-check`: `GET /health` returning `{"status": "ok"}` after DB connectivity verification
- `testing-infrastructure`: pytest framework with async support, coverage config, test DB fixtures, and conftest.py

### Modified Capabilities
- None

## Approach

1. **Config first** — `config.py` reads env vars and builds the URL.
2. **Database module** — `database.py` creates `engine`, `SessionLocal`, `Base`; `get_db` yields a session and closes it.
3. **Models bottom-up** — create tables in dependency order so `relationship()` backrefs resolve.
4. **Health check** — execute `SELECT 1` via dependency-injected session; return JSON.
5. **Testing setup** — install pytest/pytest-asyncio/pytest-cov; create `conftest.py` with test DB engine/session fixtures (uses `POSTGRES_TEST_DB` env var).
6. **Model tests** — each model test verifies table name, column names/types, and FK constraints against `01-init.sql`.
7. **Connection tests** — test DB connectivity and `GET /health` via `TestClient`.
8. **Lint gate** — `ruff check backend/src/` must pass before merge.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/src/config.py` | New | Env-based DB URL builder |
| `backend/src/database.py` | New | Engine, session, Base, get_db |
| `backend/src/models/__init__.py` | New | Re-export all 14 models |
| `backend/src/models/*.py` (14 files) | New | One model per table |
| `backend/src/main.py` | Modified | Remove skeleton, add /health |
| `backend/.env.example` | New | Document DB env vars |
| `backend/tests/conftest.py` | New | Test DB fixtures (engine, session, client) |
| `backend/tests/test_models.py` | New | Column/type/FK verification for all 14 models |
| `backend/tests/test_connection.py` | New | DB connectivity and health endpoint tests |
| `backend/pyproject.toml` | New | pytest config, asyncio mode, coverage settings |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Model-to-SQL column mismatch | Med | Cross-reference each model against `01-init.sql` line by line; add model tests |
| Missing env var crashes startup | Low | `config.py` validates with `ValueError` on missing vars |
| `relationship()` circular imports | Med | Use `lazy="select"` and string-based backref names |
| Test DB pollutes dev data | Low | Separate `POSTGRES_TEST_DB` env var; test fixtures use isolated DB |

## Rollback Plan

Delete all new files (`config.py`, `database.py`, `models/`, `tests/`, `pyproject.toml`), revert `main.py` to skeleton. No schema changes to the DB itself.

## Dependencies

- `sqlalchemy` package (add to `requirements.txt`)
- `psycopg2-binary` or `asyncpg` driver
- `pytest`, `pytest-asyncio`, `pytest-cov` (add to `requirements.txt`)
- `httpx` (for FastAPI `TestClient` async testing)
- PostgreSQL running (Docker / existing instance)

## Success Criteria

- [ ] All 14 models match `01-init.sql` columns, types, and constraints
- [ ] `ruff check backend/src/` passes with zero errors
- [ ] `GET /health` returns `{"status": "ok"}` when DB is reachable
- [ ] No hardcoded credentials in any Python file
- [ ] `get_db` dependency injection works (session yields and closes)
- [ ] `pytest backend/tests/` passes with model and connection tests
- [ ] `pytest-cov` reports ≥80% coverage on `models/` and `database.py`

## Size Estimate

~750-900 lines of Python: ~40 config+database, ~400 models (~28 avg/model), ~30 main.py, ~80 `__init__.py` + `.env.example`, ~50 conftest.py, ~100 test_models.py, ~50 test_connection.py, ~10 pyproject.toml pytest section.
