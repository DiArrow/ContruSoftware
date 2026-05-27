# Design: Fix Backend Container Crash

## Technical Approach

Three root causes crash the container: (1) `from src.xxx` imports fail because the Dockerfile flattens `src/` into `/app/`, (2) zero env vars on the backend service cause `config.py` to `ValueError` at import, and (3) dev tooling bloats the production image. The fix is a phased mechanical rename of all imports (`from src.xxx` → direct), a `pythonpath` adjustment in `pyproject.toml`, a split of `requirements.txt` into prod/dev, env var rename to match the app user, docker-compose env injection, and a `.dockerignore`.

## Architecture Decisions

| # | Decision | Choice | Rejected Alternative | Rationale |
|---|----------|--------|---------------------|-----------|
| 1 | Import convention | Direct imports: `from database import ...` | Keep `from src.xxx` + change Dockerfile to `COPY . /app/src/` | Dockerfile already copies `./src/` to `/app/` (flat). Direct imports match container layout AND local dev via `pythonpath`. Adding an extra directory layer is unnecessary nesting. |
| 2 | Test resolution | `pythonpath = ["src"]` in `pyproject.toml` | Install as editable package (`pip install -e .`) | Simpler. No `setup.py`/`setup.cfg` boilerplate. Tests run from `backend/`, so `src` → `backend/src/` — mirrors the container exactly. |
| 3 | Env var naming | `POSTGRES_APP_USER` / `POSTGRES_APP_PASSWORD` for app | Keep `POSTGRES_USER` / `POSTGRES_PASSWORD` (admin creds) | DB init script (`02-users.sh`) creates an app user with limited privileges. Using admin creds for the app is a security anti-pattern. The `db` service already passes both sets. |
| 4 | Dep separation | Split `requirements.txt` (prod) and `requirements-dev.txt` (dev) | Use `extras_require` in `setup.cfg` | Two flat files are simpler for Dockerfile `COPY` and `pip install`. No packaging infrastructure needed. |

## Data Flow

```
.env ─── docker-compose.yml (${VAR} substitution) ──→ backend container env
                                                           │
                                              config.py reads POSTGRES_APP_*
                                                           │
                                              SQLALCHEMY_DATABASE_URL built
                                                           │
                                              database.py creates engine + session
                                                           │
                                              main.py FastAPI app serves /health
```

Dockerfile build context (`.dockerignore` filtered):
```
backend/
├── src/          ← COPY ./src/ .     → /app/main.py, /app/database.py, /app/models/...
├── requirements.txt  ← COPY ./requirements.txt . → pip install (prod only)
└── .dockerignore ← excludes .venv, __pycache__, .env, tests/, caches
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/requirements.txt` | Modify | Remove dev deps (pytest, ruff, sqlfluff, yamllint, pytest-cov, pytest-asyncio, httpx). Keep: fastapi, uvicorn, sqlalchemy, psycopg2-binary, python-dotenv. |
| `backend/requirements-dev.txt` | Create | Dev/testing deps: pytest, pytest-asyncio, pytest-cov, httpx, ruff, sqlfluff, yamllint. |
| `backend/src/config.py` | Modify | `REQUIRED_VARS`: `POSTGRES_USER`→`POSTGRES_APP_USER`, `POSTGRES_PASSWORD`→`POSTGRES_APP_PASSWORD`. Update `os.getenv()` calls and docstring. |
| `backend/src/database.py` | Modify | `from src.config` → `from config` |
| `backend/src/main.py` | Modify | `from src.database` → `from database` |
| `backend/src/models/__init__.py` | Modify | 14 imports: `from src.models.xxx` → `from models.xxx`. Docstring example updated. |
| `backend/src/models/*.py` (13 files) | Modify | Each: `from src.database import Base` → `from database import Base` |
| `backend/pyproject.toml` | Modify | `pythonpath = ["."]` → `pythonpath = [".", "src"]` |
| `backend/.dockerignore` | Create | Exclude: `.venv/`, `__pycache__/`, `*.pyc`, `.env`, `.env.*`, `tests/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `.coverage`, `htmlcov/`, `*.egg-info/` |
| `backend/.env.example` | Create | Template with `POSTGRES_APP_USER`, `POSTGRES_APP_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB` |
| `docker-compose.yml` | Modify | Add `environment:` block to `backend` service with `POSTGRES_HOST=db`, `${POSTGRES_APP_USER}`, `${POSTGRES_APP_PASSWORD}`, `${POSTGRES_DB}` |
| `backend/tests/conftest.py` | Modify | `from src.main` → `from main`; `from src.database` → `from database` (in try/except); `_get_database_url` uses `POSTGRES_APP_*` vars |
| `backend/tests/test_config.py` | Modify | Env dict keys: `POSTGRES_USER`→`POSTGRES_APP_USER`, `POSTGRES_PASSWORD`→`POSTGRES_APP_PASSWORD` |
| `backend/tests/test_database.py` | Modify | `from src.database` → `from database` |
| `backend/tests/test_connection.py` | Modify | `from src.database` → `from database`; `from src.main` → `from main` |
| `backend/tests/test_models_tier0.py` | Modify | `from src.models.xxx` → `from models.xxx` |
| `backend/tests/test_models_tier1.py` | Modify | `from src.models.xxx` → `from models.xxx` |
| `backend/tests/test_models_tier2.py` | Modify | `from src.models.xxx` → `from models.xxx` |

## Before/After: Key Changes

**config.py:**
```diff
-    "POSTGRES_USER",
-    "POSTGRES_PASSWORD",
+    "POSTGRES_APP_USER",
+    "POSTGRES_APP_PASSWORD",
-    user = os.getenv("POSTGRES_USER")
-    password = os.getenv("POSTGRES_PASSWORD")
+    user = os.getenv("POSTGRES_APP_USER")
+    password = os.getenv("POSTGRES_APP_PASSWORD")
```

**pyproject.toml:**
```diff
- pythonpath = ["."]
+ pythonpath = [".", "src"]
```

**docker-compose.yml (backend service):**
```yaml
backend:
  build:
    context: ./backend/
  ports:
    - 8000:8000
  depends_on:
    - db
  environment:                        # ← ADDED
    POSTGRES_HOST: db
    POSTGRES_PORT: "5432"
    POSTGRES_APP_USER: ${POSTGRES_APP_USER}
    POSTGRES_APP_PASSWORD: ${POSTGRES_APP_PASSWORD}
    POSTGRES_DB: ${POSTGRES_DB}
```

## Dependency Graph (execution order)

```
1. requirements split     ─── no dependencies
2. config.py env rename   ─── no dependencies (can parallel with 1)
3. src/* imports rename   ─── depends on: (none — pure rename)
4. tests/* imports rename ─── depends on: 3 (must match source convention)
5. pyproject.toml         ─── depends on: 4 (tests need it to resolve)
6. docker-compose.yml     ─── depends on: 2 (uses new var names)
7. .dockerignore          ─── no dependencies
8. .env.example           ─── depends on: 2 (documents new var names)
```

Parallelizable pairs: (1, 2, 3, 7) can run concurrently. (4+5) must follow 3. (6) must follow 2.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit (config) | `POSTGRES_APP_USER`/`POSTGRES_APP_PASSWORD` resolve correctly; missing vars raise `ValueError` | Existing `test_config.py` — update env dict keys, assertions remain |
| Unit (database) | Engine, session, base, `get_db` work after import rename | Existing `test_database.py` — update import path, assertions unchanged |
| Unit (models) | All 13 models import and table metadata loads | Existing tier 0/1/2 model tests — update imports, verify `__tablename__` |
| Integration | `/health` returns 200 with live DB | `test_connection.py` — update imports, assertion `{"status": "ok"}` |
| Integration | Test fixtures work (engine, session, client) | `test_infrastructure.py` — no code changes needed |
| Container | `docker compose up backend` starts, `/health` returns 200 | Manual smoke test: `curl localhost:8000/health` |
| Container | Dev deps absent from image | `docker compose exec backend pip list \| grep -E "pytest|ruff|sqlfluff"` — expect empty |

## Migration / Rollout

**No data migration required.** All changes are configuration and import paths.

**Rollback:** `git revert` the commit. All changes are reversible:
- Import paths: revert `from xxx` → `from src.xxx` across all files
- `pyproject.toml`: restore `pythonpath = ["."]`
- `requirements.txt`: restore original (contains dev deps)
- Delete `requirements-dev.txt` and `.dockerignore`
- `docker-compose.yml`: remove `environment:` block from backend
- `config.py`: restore `POSTGRES_USER`/`POSTGRES_PASSWORD`
- `conftest.py`: restore `from src.main`, `from src.database`
- `.env.example`: delete (didn't exist before)

## Open Questions

- **`.env.example` prior existence**: The spec documents it as "previously existed" but no `.env.example` file exists in the repo. Proceeding with creation since both proposal and spec require it.
- **`pythonpath` dual entry**: `[".", "src"]` keeps backward compat for any remaining `src.` imports during transition. Could simplify to `["src"]` after full rename. Design uses `[".", "src"]` as safer choice.
