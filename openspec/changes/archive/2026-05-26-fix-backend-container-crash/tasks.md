# Tasks: Fix Backend Container Crash

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 80–120 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

## Phase 1: Dependency Separation & Config

- [ ] 1.1 **Split `requirements.txt`** — Remove dev deps (pytest, ruff, sqlfluff, yamllint, pytest-cov, pytest-asyncio, httpx). Create `backend/requirements-dev.txt` with those 7 dev deps.
  - Files: `backend/requirements.txt` (modify), `backend/requirements-dev.txt` (create)
  - Verify: `pip install -r requirements.txt` installs only fastapi/uvicorn/sqlalchemy/psycopg2-binary/python-dotenv

- [ ] 1.2 **Rename env vars in `config.py`** — Change `POSTGRES_USER` → `POSTGRES_APP_USER`, `POSTGRES_PASSWORD` → `POSTGRES_APP_PASSWORD` in `REQUIRED_VARS` list and both `os.getenv()` calls.
  - Files: `backend/src/config.py` (modify)
  - Verify: `import config` with APP_ vars succeeds; raises `ValueError` with old `POSTGRES_USER`/`POSTGRES_PASSWORD` only

- [ ] 1.3 **Create `.env.example`** — Document all 5 required env vars (`POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_APP_USER`, `POSTGRES_APP_PASSWORD`, `POSTGRES_DB`) with placeholder values.
  - Files: `backend/.env.example` (create)
  - Verify: File lists all 5 vars with `POSTGRES_APP_*` naming, no real credentials

## Phase 2: Import Rename — Source Files

- [ ] 2.1 **Rename import in `database.py`** — Change `from src.config import SQLALCHEMY_DATABASE_URL` → `from config import SQLALCHEMY_DATABASE_URL`.
  - Files: `backend/src/database.py` (modify)
  - Verify: `python -c "from database import engine"` succeeds from `backend/src/`

- [ ] 2.2 **Rename import in `main.py`** — Change `from src.database import get_db` → `from database import get_db`.
  - Files: `backend/src/main.py` (modify)
  - Verify: `python -c "from main import app"` succeeds from `backend/src/`

- [ ] 2.3 **Rename imports in all 13 model files** — Change `from src.database import Base` → `from database import Base` in each model.
  - Files: `backend/src/models/*.py` (13 files, modify)
  - Verify: Each model file `python -c "from models.xxx import Xxx"` succeeds from `backend/src/`

- [ ] 2.4 **Rename imports in `models/__init__.py`** — Change 14 `from src.models.xxx` → `from models.xxx`, update docstring example.
  - Files: `backend/src/models/__init__.py` (modify)
  - Verify: `python -c "from models import Usuario, Curso"` succeeds from `backend/src/`

- [ ] 2.5 **Verify zero `from src.` in source** — Run `grep -rn "from src\." backend/src/` — expect empty.
  - Verify: No results from grep

## Phase 3: Import Rename — Tests & Config

- [ ] 3.1 **Update `pyproject.toml`** — Change `pythonpath = ["."]` → `pythonpath = [".", "src"]` so direct imports resolve from `backend/` dir.
  - Files: `backend/pyproject.toml` (modify)
  - Verify: `pytest --collect-only` finds all tests from `backend/`

- [ ] 3.2 **Update test imports in `conftest.py`** — Change `from src.main import app` → `from main import app` and both `from src.database import get_db` → `from database import get_db`.
  - Files: `backend/tests/conftest.py` (modify)
  - Verify: `python -c "from conftest import *"` succeeds from `backend/tests/`

- [ ] 3.3 **Update `test_config.py`** — Change `sys.modules.pop("src.config", None)` → `sys.modules.pop("config", None)`, `import src.config` → `import config`, and all env var keys from `POSTGRES_USER`/`POSTGRES_PASSWORD` → `POSTGRES_APP_USER`/`POSTGRES_APP_PASSWORD`.
  - Files: `backend/tests/test_config.py` (modify)
  - Verify: `pytest tests/test_config.py -v` passes

- [ ] 3.4 **Update `test_database.py`** — Change `from src.database import Base, SessionLocal, engine, get_db` → `from database import ...`.
  - Files: `backend/tests/test_database.py` (modify)
  - Verify: `pytest tests/test_database.py -v` passes

- [ ] 3.5 **Update `test_connection.py`** — Change `from src.database` → `from database`, `from src.main` → `from main`.
  - Files: `backend/tests/test_connection.py` (modify)
  - Verify: `pytest tests/test_connection.py -v` passes

- [ ] 3.6 **Update test model imports** — Change all `from src.models.xxx` → `from models.xxx` across tier0, tier1, tier2 test files.
  - Files: `backend/tests/test_models_tier0.py`, `test_models_tier1.py`, `test_models_tier2.py` (modify)
  - Verify: `pytest tests/test_models_tier0.py tests/test_models_tier1.py tests/test_models_tier2.py -v` passes

- [ ] 3.7 **Full test suite pass** — Run `cd backend && pytest` — all tests pass with direct imports.
  - Verify: `pytest` exits 0 from `backend/`

## Phase 4: Container Configuration

- [ ] 4.1 **Create `.dockerignore`** — Exclude `.venv/`, `__pycache__/`, `*.pyc`, `.env`, `.env.*`, `tests/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `.coverage`, `htmlcov/`, `*.egg-info/`.
  - Files: `backend/.dockerignore` (create)
  - Verify: `docker build -t test-backend backend/` context is under 1MB, `.env` is excluded

- [ ] 4.2 **Add environment block to `docker-compose.yml`** — Add `environment:` to backend service with `POSTGRES_HOST: db`, `POSTGRES_PORT: "5432"`, `${POSTGRES_APP_USER}`, `${POSTGRES_APP_PASSWORD}`, `${POSTGRES_DB}`.
  - Files: `docker-compose.yml` (modify)
  - Verify: `docker compose config` renders env vars from `.env`

- [ ] 4.3 **Final smoke test** — `docker compose up backend` starts, `curl localhost:8000/health` returns `{"status":"ok"}`.
  - Verify: Container starts without crash; no `ModuleNotFoundError` or `ValueError`
