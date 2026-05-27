# Tasks: SQLAlchemy Models & Database Integration

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~775 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR #1 → PR #2 → PR #3 → PR #4 |
| Delivery strategy | force-chained |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Base |
|------|------|-----------|------|
| 1 | Testing infrastructure | PR #1 | `main` |
| 2 | DB layer + tier-0 models (usuario, semestre) | PR #2 | `main` |
| 3 | Tier-1/2/3 models (12 files) + `__init__.py` | PR #3 | `main` |
| 4 | Health endpoint | PR #4 | `main` |

## PR #1: Testing Infrastructure

- [x] 1.1 Rename `backend/requeriments.txt` → `backend/requirements.txt` (fix typo)
- [x] 1.2 Add `pytest`, `pytest-asyncio`, `pytest-cov`, `httpx` to `backend/requirements.txt`
- [x] 1.3 Create `backend/pyproject.toml` with `[tool.pytest.ini_options]` (asyncio_mode, testpaths, coverage)
- [x] 1.4 Create `backend/tests/conftest.py` — `test_engine` (session), `db_session` (yield+rollback using business DB), `client` (TestClient)
- [x] 1.5 (VERIFY) `pytest backend/tests/ --setup-show` discovers fixtures without errors

## PR #2: DB Layer + Tier-0 Models (STRICT TDD)

- [x] 2.1 (RED) Write `backend/tests/test_config.py` — missing var raises ValueError; valid vars produce URL
- [x] 2.2 (GREEN) Create `backend/src/config.py` — read 5 env vars, build `postgresql+psycopg2://` URL
- [x] 2.3 (RED) Write `backend/tests/test_database.py` — engine, SessionLocal, Base exist; get_db yields session
- [x] 2.4 (GREEN) Create `backend/src/database.py` — `engine` (pool_size=5), `SessionLocal`, `Base`, `get_db` generator
- [x] 2.5 Create `backend/.env.example` — document 5 required vars (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT)
- [x] 2.6 Add `sqlalchemy`, `psycopg2-binary` to `backend/requirements.txt` *(completed in PR #1)*
- [x] 2.7 (RED) Write tier-0 model tests for Usuario + Semestre — table name, columns, PK, timestamps
- [x] 2.8 (GREEN) Create `backend/src/models/usuario.py` — VARCHAR(36) PK, timestamps, relationships
- [x] 2.9 (GREEN) Create `backend/src/models/semestre.py` — VARCHAR(36) PK, timestamps
- [x] 2.10 (VERIFY) `pytest backend/tests/ -v` — all PR #2 tests pass

## PR #3: Tier-1/2/3 Models (STRICT TDD)

- [x] 3.1 (RED) Write tier-1 model tests for estudiante, articulo, bloque_horario, curso, grupo_estudiante, impresion, movimiento_stock, ayudantia — schema + FK verification
- [x] 3.2 (GREEN) Create remaining tier-0: `estudiante.py`, `articulo.py`, `bloque_horario.py`
- [x] 3.3 (GREEN) Create tier-1: `curso.py`, `grupo_estudiante.py`, `impresion.py`, `movimiento_stock.py`, `ayudantia.py`
- [x] 3.4 (RED) Write tier-2 model tests for inscripcion_ayudantia, uso_impresora, reserva, bloque_reservado — schema + FK + composite PK checks
- [x] 3.5 (GREEN) Create tier-2/3: `inscripcion_ayudantia.py`, `uso_impresora.py`, `reserva.py`, `bloque_reservado.py`
- [x] 3.6 (GREEN) Create `backend/src/models/__init__.py` — re-export all 14 models
- [x] 3.7 (VERIFY) `pytest backend/tests/ -v && ruff check backend/src/models/` — all pass

## PR #4: Health Endpoint (STRICT TDD)

- [x] 4.1 (RED) Write `backend/tests/test_connection.py` — /health returns 200 + `{"status":"ok"}`; 503 on DB down
- [x] 4.2 (GREEN) Rewrite `backend/src/main.py` — remove skeleton, add `GET /health` with `Depends(get_db)`, `SELECT 1`
- [x] 4.3 (VERIFY) `pytest backend/tests/ -v --cov=backend.src.models --cov=backend.src.database --cov=backend.src.main` — full pass, 100% coverage
