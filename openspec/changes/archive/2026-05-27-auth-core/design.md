# Design: Auth Core — JWT Authentication & RBAC Middleware

## Technical Approach

Extract-only auth core — no `/auth/token` endpoint, no password hashing. New `backend/src/auth/` module: JWT handler, FastAPI dependencies, Pydantic schemas. Extend `Usuario` with `email` (unique), `estado` (default True), rol enum. DB hardening via role-specific PostgreSQL users. TDD-first.

## Architecture Decisions

| Decision | Option A | Option B | Choice | Rationale |
|----------|----------|----------|--------|-----------|
| JWT library | `python-jose[cryptography]` | `PyJWT` directly | **python-jose** | FastAPI-recommended; wraps PyJWT with easier API for encode/decode |
| SECRET_KEY handling | Config constant from env | FastAPI settings with pydantic-settings | **Config constant** | Matches existing config.py pattern; no new dependency |
| Role DB connection | One engine per role | Single engine + SET ROLE | **Multi-engine** | Clear permission boundaries; PostgreSQL `SET ROLE` adds complexity per-session; explicit is safer |
| rol enum validation | Python `Enum` in model validator | SQLAlchemy `Enum` column | **Python validator** | Matches existing `VARCHAR(50)` schema; avoids dialect lock-in; `ValueError` before DB |
| Token extraction | `OAuth2PasswordBearer(tokenUrl="/auth/token")` | Custom header dependency | **OAuth2PasswordBearer** | FastAPI-native; swagger UI auto-docs the lock icon; future endpoint already planned |
| Role dep factory | `requiere_rol(*roles) -> Callable` | Class-based guard | **Factory closure** | Concise; reads naturally at endpoint: `Depends(requiere_rol("ADM"))` |

## Data Flow

```
Request → OAuth2PasswordBearer (extract token) → get_current_user (decode JWT)
→ TokenData(sub, role) → requiere_rol("PRO") (check) → get_role_session (connect)
→ endpoint logic
```

Auth verification uses `get_db` (app user). Data-mutating endpoints use `get_role_session` matching `TokenData.role` — DB-level permissions as defense-in-depth.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/src/auth/__init__.py` | Create | Package init, re-exports |
| `backend/src/auth/jwt_handler.py` | Create | `crear_token_jwt`, `validar_token_jwt`, HS256 |
| `backend/src/auth/dependencies.py` | Create | `oauth2_scheme`, `get_current_user`, `requiere_rol`, `get_role_session` |
| `backend/src/auth/schemas.py` | Create | `LoginRequest`, `TokenResponse`, `TokenData` |
| `backend/src/config.py` | Modify | Add `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, 5× `POSTGRES_USER_{ROL}` vars, `ROL_DATABASE_URLS` dict |
| `backend/src/models/usuario.py` | Modify | Add `email VARCHAR(255) unique`, `estado BOOLEAN default True`, rol enum validator |
| `backend/src/database.py` | Modify | Add `get_role_session(role)` generator — picks engine from `ROL_DATABASE_URLS` |
| `docker-compose.yml` | Modify | Add env vars for 5 role-specific DB users + `SECRET_KEY` |
| `backend/.env.example` | Modify | Add `SECRET_KEY`, 5 role credentials |
| `db/init/02-role-users.sql` | Create | CREATE USER + GRANT per role (SOL/EST/AYU/PRO/ADM) |
| `db/migrations/01-add-usuario-columns.sql` | Create | ALTER TABLE usuario ADD COLUMN email, estado |
| `db/seeds/01-test-usuarios.sql` | Create | INSERT test users for each role |
| `backend/tests/auth/` (3 files) | Create | TDD tests: jwt_handler, dependencies, schemas |
| `backend/tests/models/test_usuario_extended.py` | Create | TDD tests: email unique, estado default, rol validation |

## Interfaces

| Module | Exports |
|--------|---------|
| `jwt_handler.py` | `crear_token_jwt(data, expires_delta?) -> str`, `validar_token_jwt(token) -> dict` |
| `dependencies.py` | `oauth2_scheme`, `get_current_user -> TokenData`, `requiere_rol(*roles) -> Dep`, `get_role_session -> Session` |
| `schemas.py` | `LoginRequest(rut, password)`, `TokenResponse(access_token, token_type)`, `TokenData(sub, role, exp?)` |

## DB Permission Matrix

| Role | ABBR | SELECT | INSERT | UPDATE | DELETE |
|------|------|--------|--------|--------|--------|
| Solicitante | SOL | Own data only | — | — | — |
| Estudiante | EST | Read tables | Own data | — | — |
| Ayudante | AYU | Read tables | Ayudantías | — | — |
| Profesor | PRO | Read tables | Cursos/Ayud. | Cursos/Ayud. | — |
| Admin | ADM | Full | Full | Full | Full |

Implemented via `02-role-users.sql` with `CREATE USER` + `GRANT SELECT/INSERT/UPDATE/DELETE ON <table> TO <role_user>`.

## Testing Strategy (TDD)

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | JWT create/validate, schema validation, rol enum | `pytest` with `db_session` isolation; patch `os.environ` for SECRET_KEY |
| Integration | Token lifecycle, required_rol 401/403, role session | `TestClient` with dependency overrides; real JWT tokens against mocked DB |
| Docker | Env var validation, role DB connectivity | `docker compose up` smoke test — app starts, `/health` returns 200 |

Coverage target: ≥80% on `backend/src/auth/`.

## Migration / Rollout

- **Migration script** (`db/migrations/01-add-usuario-columns.sql`): `ALTER TABLE usuario ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE, ADD COLUMN IF NOT EXISTS estado BOOLEAN DEFAULT TRUE`. DB is empty, but script exists for pipeline.
- **Seed script** (`db/seeds/01-test-usuarios.sql`): INSERT one usuario per role with hardcoded UUIDs for deterministic tests.
- **Rollback**: Remove `auth/` dir, revert model/config/database changes, `ROLLBACK 01-add-usuario-columns` for columns.

## Open Questions

- [ ] Should `get_role_session` be the **only** DB dependency for endpoints, or does `get_db` (app user) remain for health/auth lookups? Recommend: `get_db` for auth layer, `get_role_session` for business endpoints.
- [ ] Confirm `POSTGRES_USER_SOL` pattern — are these secondary PostgreSQL users in the same DB, or separate DBs? Design assumes same DB, different users with GRANTs.
