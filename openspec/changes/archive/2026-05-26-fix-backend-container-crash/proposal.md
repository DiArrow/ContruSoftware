# Proposal: Fix backend container crash and separate prod/dev dependencies

## Intent

The backend container crashes immediately on `docker compose up` due to three critical failures: (1) all source imports use `from src.xxx` but the Dockerfile flattens `src/` into `/app/`, causing `ModuleNotFoundError`, (2) the backend service in docker-compose.yml has zero environment variables, causing `ValueError` in config.py at import time, and (3) no `.dockerignore` sends `.env` with credentials to the Docker daemon. Additionally, `requirements.txt` bundles dev dependencies (pytest, ruff, sqlfluff) into the production image, and config.py uses admin credentials instead of the app user created by the DB init script.

## Scope

### In Scope
- Change all `from src.xxx` imports to direct imports in source files (`from database`, `from models.xxx`, `from config`)
- Update `backend/src/models/__init__.py` to use direct imports (`from models.xxx`)
- Update `pyproject.toml` pythonpath to `["src"]` so tests resolve direct imports from `backend/src/`
- Update test imports from `from src.xxx` to direct imports (matching source convention)
- Split `requirements.txt` into `requirements.txt` (prod) and `requirements-dev.txt` (dev)
- Update Dockerfile to install from production requirements only
- Change `config.py` env vars from `POSTGRES_USER`/`POSTGRES_PASSWORD` to `POSTGRES_APP_USER`/`POSTGRES_APP_PASSWORD`
- Add environment variables to backend service in `docker-compose.yml`
- Add `.dockerignore` to backend directory

### Out of Scope
- Python version upgrade (3.11.1 CVEs — separate change)
- Duplicate DB init script cleanup (`01_init.sql` vs `01-init.sql`)
- Frontend container changes
- Adding new API endpoints or models

## Capabilities

### New Capabilities
- `container-config`: Container environment variable injection and `.dockerignore` for secure, lean builds

### Modified Capabilities
- `database-connection`: Change env var names from `POSTGRES_USER`/`POSTGRES_PASSWORD` to `POSTGRES_APP_USER`/`POSTGRES_APP_PASSWORD`; update import paths from `src.xxx` to direct imports

## Approach

Phased execution in dependency order:

1. **Split requirements** — Create `requirements-dev.txt` with pytest/ruff/sqlfluff/yamllint/pytest-cov/pytest-asyncio/httpx; keep only fastapi/uvicorn/sqlalchemy/psycopg2-binary/python-dotenv in `requirements.txt`. Update Dockerfile to `COPY requirements.txt` (already correct) — it will now only install prod deps.

2. **Update config.py** — Change `REQUIRED_VARS` and `os.getenv` calls from `POSTGRES_USER`/`POSTGRES_PASSWORD` to `POSTGRES_APP_USER`/`POSTGRES_APP_PASSWORD`. These match the variables already passed to the `db` service and match the app user created by `02-users.sh`.

3. **Fix imports (source files)** — Mechanical rename across `backend/src/`: `from src.database` → `from database`, `from src.config` → `from config`, `from src.models.xxx` → `from models.xxx`. This matches the container layout where `COPY ./src/ .` puts files directly in `/app/`.

4. **Fix imports (tests)** — Change `from src.xxx` to direct `from database`, `from models.xxx`, `from main` etc. Update `pyproject.toml` pythonpath from `["."]` to `["src"]` so `from database` resolves to `backend/src/database.py` during test runs.

5. **Update docker-compose.yml** — Add `environment:` block to backend service injecting `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_APP_USER`, `POSTGRES_APP_PASSWORD`, `POSTGRES_DB` from `.env` variables.

6. **Add .dockerignore** — Exclude `.venv/`, `__pycache__/`, `.env`, `tests/`, `.ruff_cache/`, `*.pyc`.

7. **Update models/__init__.py docstring** — Change usage example from `from src.models` to `from models`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/src/config.py` | Modified | Env var names changed to APP_ variants |
| `backend/src/database.py` | Modified | Import `from src.config` → `from config` |
| `backend/src/main.py` | Modified | Import `from src.database` → `from database` |
| `backend/src/models/__init__.py` | Modified | 14 imports changed from `from src.models.xxx` → `from models.xxx` |
| `backend/src/models/*.py` (13 files) | Modified | `from src.database` → `from database` |
| `backend/tests/conftest.py` | Modified | Imports changed to direct; `_get_database_url` uses APP_ vars |
| `backend/tests/test_*.py` (7 files) | Modified | `from src.xxx` → direct imports |
| `backend/requirements.txt` | Modified | Dev deps removed (prod only) |
| `backend/requirements-dev.txt` | New | Dev dependencies split out |
| `backend/pyproject.toml` | Modified | pythonpath `["."]` → `["src"]` |
| `backend/Dockerfile` | Modified | May need requirements-dev.txt for test stages (future) |
| `backend/.dockerignore` | New | Exclude non-prod files from build context |
| `docker-compose.yml` | Modified | Add environment block to backend service |
| `openspec/specs/database-connection/spec.md` | Modified | Update env var names in requirements table |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Import rename misses a file | Low | Grep for `from src\.` catches all; CI would catch remaining |
| Test breakage from pythonpath change | Low | `pythonpath = ["src"]` adds `backend/src/` to sys.path; direct imports resolve identically to container |
| `.env` variable names don't match docker-compose env injection | Low | Both use `POSTGRES_APP_USER`/`POSTGRES_APP_PASSWORD` — already defined in `.env` and `db` service |
| Dev deps needed in CI | Low | CI can install `requirements-dev.txt` separately; production image stays lean |

## Rollback Plan

Revert all import changes (`from xxx` → `from src.xxx`), restore `requirements.txt` to original, remove `requirements-dev.txt`, remove `.dockerignore`, remove backend environment block from docker-compose.yml, revert `pyproject.toml` and `config.py`. All changes are reversible via git revert.

## Dependencies

- The `db` service already creates the app user via `02-users.sh` and passes `POSTGRES_APP_USER`/`POSTGRES_APP_PASSWORD` — no DB changes needed.

## Success Criteria

- [ ] `docker compose up backend` starts without crash; `/health` endpoint responds 200
- [ ] `docker compose exec backend python -c "from database import engine"` succeeds inside container
- [ ] `pytest` passes with direct imports from `backend/` directory
- [ ] Backend container image does NOT include pytest, ruff, sqlfluff, yamllint, pytest-cov, pytest-asyncio, or httpx
- [ ] `config.py` reads `POSTGRES_APP_USER`/`POSTGRES_APP_PASSWORD` (not admin credentials)
- [ ] No `.env` file or secrets in Docker build context (verified by `.dockerignore`)