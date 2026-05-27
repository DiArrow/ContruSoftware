# Archive Report: fix-backend-container-crash

**Archived**: 2026-05-26
**Source branch**: `fix/backend-container`
**Artifact mode**: openspec

## Summary

The backend container was crashing immediately on `docker compose up` due to three root causes:
1. **Import mismatch**: All source files used `from src.xxx` imports but the Dockerfile flattens `src/` into `/app/`, causing `ModuleNotFoundError`
2. **Missing environment variables**: The backend service in `docker-compose.yml` had zero env vars, causing `ValueError` in `config.py` at import time
3. **Dev deps in production**: `requirements.txt` bundled pytest, ruff, sqlfluff into the production image

Additionally, security improvements were made: config.py now uses `POSTGRES_APP_USER`/`POSTGRES_APP_PASSWORD` (app user, not admin), and a `.dockerignore` was added to prevent secrets from leaking into the Docker build context.

## What Changed

| Area | Change | Files |
|------|--------|-------|
| Import convention | `from src.xxx` → direct imports (e.g. `from database`, `from config`, `from models.xxx`) | 18 source + test files |
| Dependencies | Split `requirements.txt` (prod) / `requirements-dev.txt` (dev) | 2 files |
| Config | Env var names: `POSTGRES_USER`→`POSTGRES_APP_USER`, `POSTGRES_PASSWORD`→`POSTGRES_APP_PASSWORD` | 3 files (config.py, conftest.py, test_config.py) |
| Docker compose | Added `environment:` block to backend service | `docker-compose.yml` |
| Build context | Added `.dockerignore` excluding secrets, caches, tests | `backend/.dockerignore` |
| Test resolution | `pythonpath = ["src"]` in `pyproject.toml` | `pyproject.toml` |
| Documentation | `.env.example` with APP_ var names | `backend/.env.example` |

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| `database-connection` | Updated | MODIFIED: 2 requirements updated (env vars table, .env.example), 1 requirement ADDED (Direct Import Convention). 3 scenarios updated, 1 new scenario added. |
| `container-config` | Created | NEW capability: 5 requirements (dep separation, Dockerfile structure, env injection, .dockerignore). 8 scenarios. |

## Files Affected

### Source Files (modified)
- `backend/src/config.py` — Env var rename + docstring
- `backend/src/database.py` — Import `from src.config` → `from config`
- `backend/src/main.py` — Import `from src.database` → `from database`
- `backend/src/models/__init__.py` — 14 imports + docstring updated
- `backend/src/models/*.py` (13 files) — `from src.database` → `from database`

### Test Files (modified)
- `backend/tests/conftest.py` — Imports + env var names
- `backend/tests/test_config.py` — Import paths + env var keys
- `backend/tests/test_database.py` — Import paths
- `backend/tests/test_connection.py` — Import paths
- `backend/tests/test_models_tier0.py` — Import paths
- `backend/tests/test_models_tier1.py` — Import paths
- `backend/tests/test_models_tier2.py` — Import paths

### Configuration Files (created)
- `backend/requirements-dev.txt` — Dev deps split
- `backend/.dockerignore` — Build context filter
- `backend/.env.example` — Env var template

### Configuration Files (modified)
- `backend/requirements.txt` — Production-only deps
- `backend/pyproject.toml` — pythonpath
- `docker-compose.yml` — Backend env injection

## Verification Results

Per the user's confirmation:
- All specs pass
- Container starts without crash
- Health check returns `{"status":"ok"}`
- Dev dependencies absent from production image
- All tests pass with direct imports

**No formal verify-report.md was generated** (verify phase was not run through SDD). Verification was confirmed manually.

## Lessons Learned

1. **Dockerfile layout drives import convention**: When `COPY ./src/ .` flattens the source directory, imports must NOT include the `src.` prefix. This is a fundamental constraint that should be documented in the spec to prevent regression.

2. **App vs admin credentials**: Using `POSTGRES_USER`/`POSTGRES_PASSWORD` (admin) for the application was a security anti-pattern. The DB init script already created an app user — the config just wasn't using it. The spec now explicitly documents `POSTGRES_APP_USER`/`POSTGRES_APP_PASSWORD`.

3. **Env var injection is easy to forget**: The docker-compose.yml had no `environment:` block on the backend service, despite `.env` having all the right variables. The container-config spec now requires env injection as a hard requirement.

4. **Dev deps in production images**: Without explicit separation, `requirements.txt` naturally accumulates dev dependencies. The two-file pattern (`requirements.txt` + `requirements-dev.txt`) makes the intent explicit and CI can install both independently.

## Archive Contents

- `proposal.md` ✅
- `specs/database-connection/spec.md` ✅
- `specs/container-config/spec.md` ✅
- `design.md` ✅
- `tasks.md` ✅ (13 of 13 tasks complete)

## Source of Truth Updated

The following specs now reflect the new behavior:
- `openspec/specs/database-connection/spec.md` — Updated with APP_ env vars and Direct Import Convention
- `openspec/specs/container-config/spec.md` — New capability specification
