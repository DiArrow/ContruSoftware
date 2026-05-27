# Design: SQLAlchemy Models & Database Integration

## Technical Approach

Synchronous SQLAlchemy ORM with `psycopg2` driver. Config reads env vars → `database.py` builds engine/session → models in `src/models/` declare tables via `Base` → FastAPI `main.py` mounts `/health` using `Depends(get_db)` → pytest validates schema mapping via isolated test DB. Everything passes `ruff` (E/W/F/I).

## Architecture Decisions

| Decision | Option A | Option B | Choice | Rationale |
|----------|----------|----------|--------|-----------|
| Sync vs Async | `psycopg2` (sync) | `asyncpg` (async) | **Sync** | Simpler DI; no async CRUD in scope; can migrate later via `create_async_engine` |
| Model files | One file per table | Single `models.py` | **One per table** | Matches spec; avoids monolithic 500-line file; clear ownership |
| PK type | `VARCHAR(36)` SQLAlchemy String | `UUID` type with postgresql dialect | **`VARCHAR(36)` String** | Direct mirror of SQL schema; no dialect dependency; UUID generation is app-layer concern |
| FK references | String-based `"tabla.columna"` | Import-based `Table.column` | **String-based** | Prevents circular imports; cleaner `relationship()` backrefs |
| Test DB isolation | Separate `POSTGRES_TEST_DB` env var | SQLite in-memory | **Separate PostgreSQL DB** | Real dialect behavior; `TIMESTAMP`/`TIME` type fidelity; matches production |
| Session handling | `get_db` generator with try/finally | Context manager `with Session()` | **Generator + Depends** | FastAPI native pattern; session lifecycle tied to request scope |

## Data Flow

```
Env Vars ──→ config.py ──→ database.py ──→ FastAPI Depends(get_db)
                                │                    │
                           engine+Base          /health route
                                │                    │
                           models/*.py  ←───────────┘
                                │
                           PostgreSQL (14 tables)
```

`get_db` yields a `Session`; the health route executes `session.execute(text("SELECT 1"))`; on `finally`, session closes (commit on success, rollback on exception).

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/src/config.py` | Create | Reads 5 env vars, builds `DATABASE_URL`, raises `ValueError` on missing |
| `backend/src/database.py` | Create | `engine` (pool_size=5, max_overflow=10), `SessionLocal`, `Base`, `get_db()` generator |
| `backend/src/models/*.py` (14) | Create | One declarative model per table; string FKs; `relationship()` with `lazy="select"` |
| `backend/src/models/__init__.py` | Create | Re-exports all 14 models |
| `backend/src/main.py` | Modify | Remove skeleton routes + Item model; add `GET /health` with `Depends(get_db)` |
| `backend/.env.example` | Create | Template with 5 vars + `POSTGRES_TEST_DB` |
| `backend/tests/conftest.py` | Create | `test_engine`, `db_session` (yield+rollback), `client` (TestClient) fixtures |
| `backend/tests/test_models.py` | Create | Table name, columns/types, PKs, FKs for all 14 models vs `01-init.sql` |
| `backend/tests/test_connection.py` | Create | `SELECT 1` succeeds; `/health` returns `{"status":"ok"}`, 503 on DB down |
| `backend/pyproject.toml` | Create | `[tool.pytest.ini_options]`: asyncio_mode, testpaths, coverage targets ≥80% |
| `backend/requeriments.txt` | Modify | Add: `sqlalchemy`, `psycopg2-binary`, `pytest`, `pytest-asyncio`, `pytest-cov`, `httpx` |

## Model Relationships (Dependency Tiers)

```
Tier 0 (no FKs)            Tier 1 (1-level)         Tier 2 (multi-level)          Tier 3
┌──────────────┐           ┌─────────────┐          ┌──────────────────┐       ┌──────────────────┐
│ usuario      │──┐        │ curso       │──┐       │ ayudantia        │──┐    │ bloque_reservado │
│ semestre     │  │    ┌──→│   └ semestre│  │   ┌──→│   └ curso       │  │    │   └ bloque_hor.  │
│ estudiante   │  │    │   └─────────────┘  │   │   └────────────────┘  │    │   └ reserva      │
│ articulo     │  │    │                    │   │                       │    └──────────────────┘
│ bloque_hor.  │  │    │   ┌──────────────┐ │   │   ┌──────────────────┐│
└──────────────┘  │    │   │ impresion    │ │   │   │ inscripcion_ayud.││
                  │    │   │   └ usuario  │ │   ├──→│   └ ayudantia   ││
                  ├────┤   │   └ articulo │ │   │   │   └ estudiante  ││
                  │    │   └──────────────┘ │   │   └──────────────────┘│
                  │    │                    │   │                       │
                  │    │   ┌──────────────┐ │   │   ┌──────────────────┐│
                  │    │   │ mov_stock    │ │   │   │ uso_impresora    ││
                  │    │   │   └ articulo │ │   ├──→│   └ estudiante   ││
                  │    │   └──────────────┘ │   │   │   └ ayudantia    ││
                  │    │                    │   │   └──────────────────┘│
                  │    │   ┌──────────────┐ │   │                       │
                  │    └──→│ grupo_estud. │ │   │   ┌──────────────────┐│
                  │        │   └ estudiant│ │   │   │ reserva          ││
                  │        └──────────────┘ │   └──→│   └ usuario      ││
                  │                         │       │   └ ayudantia    ││
                  └─────────────────────────┘       └──────────────────┘│
                                                                        │
                  Note: uso_impresora.ref_impresora has NO FK (matches SQL)
```

Models are defined in tier order so `relationship()` string backrefs resolve in a single import pass. All 15 FK constraints match `01-init.sql` exactly; `ref_impresora` in `UsoImpresora` is a plain column without FK.

## Test Architecture

```
conftest.py
├── test_engine (scope="session")  →  create_engine(POSTGRES_TEST_DB)
├── db_session (scope="function")  →  Session(bind=test_engine), yield, rollback+close
├── client (scope="function")      →  TestClient(app), overrides get_db → db_session
```

- **Isolation**: Each test function gets a fresh session that rolls back, leaving DB clean.
- **Model tests**: Inspect `Model.__table__` to verify `__tablename__`, column names/types, PK/FK constraints.
- **Coverage**: `pytest-cov` targets ≥80% on `models/` and `database.py`; ran via `pytest backend/tests/ --cov=backend.src.models --cov=backend.src.database`.

## Chained PR Slices (Stacked-to-Main)

| Slice | Branch targets | Contents | ~Lines | Budget |
|-------|---------------|----------|--------|--------|
| PR #1 | `main` | `config.py`, `database.py`, `.env.example`, `requirements.txt`, tier-0 models (5 files) | ~230 | OK |
| PR #2 | PR #1 branch | Tier-1/2/3 models (9 files) + `models/__init__.py` | ~295 | OK |
| PR #3 | PR #2 branch | `main.py` (+`/health`, −skeleton) | ~30 | OK |
| PR #4 | PR #3 branch | `pyproject.toml`, `conftest.py`, `test_models.py`, `test_connection.py` | ~220 | OK |

Each PR is autonomous: PR #1 verifies engine creation and env validation. PR #2 verifies all models import without circular errors. PR #3 verifies `/health` endpoint. PR #4 verifies full integration with tests and coverage.

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Missing env var (`POSTGRES_HOST`, etc.) | `config.py` raises `ValueError` at import; FastAPI fails to start |
| DB unreachable at startup | `engine.connect()` fails; FastAPI starts but `/health` returns 503 |
| DB unreachable mid-request | SQLAlchemy `OperationalError` propagates; FastAPI returns 500 |
| Session rollback on route error | `get_db`'s `finally: db.close()` handles rollback implicitly |

## Integration with main.py

The existing skeleton (`GET /`, `POST /items/`, `Item` model) is **replaced entirely**. `main.py` becomes:

1. Import `FastAPI`, `Depends` from fastapi; `get_db` from database; all models (for `Base.metadata.create_all`)
2. `app = FastAPI()`
3. `@app.get("/health")` → `Depends(get_db)` → `SELECT 1` → `{"status": "ok"}` or 503 `{"status": "error"}`
4. No `Base.metadata.create_all` on startup — deferred to Alembic in a future change

## Open Questions

- [ ] Should `Base.metadata.create_all()` run on startup as a dev convenience until Alembic is introduced? (Proposal says out of scope — recommend **not** including it.)
- [ ] Confirm `POSTGRES_TEST_DB` naming convention (`{DB_NAME}_test`) or allow full override.
