# Tasks: Auth Core — JWT Authentication & RBAC Middleware

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~500–600 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (DB + Models + Config) → PR 2 (Auth Module + Tests) |
| Delivery strategy | ask-on-risk |
| Chain strategy | feature-branch-chain |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | DB Foundation + Model Extension | PR 1 → feat/auth-core | Config vars, role DB users (bash script), Usuario columns, get_role_session, Docker env, migration, seed. Tests for model + DB hardening included. ~250 lines |
| 2 | Auth Module + Integration | PR 2 → PR1-branch | jwt_handler, schemas, dependencies, main.py wiring. All auth tests (TDD). ~300 lines |

## Branch Strategy

- Base branch: `Develop`
- Tracker branch: `feat/auth-core` (created from `Develop`)
- PR 1 branch: `feat/auth-core-pr1-db` (targets `feat/auth-core`)
- PR 2 branch: `feat/auth-core-pr2-auth` (targets `feat/auth-core-pr1-db`)
- Only `feat/auth-core` merges to `Develop` at the end

## Phase 1: Dependencies & Configuration

- [x] 1.1 Add `python-jose[cryptography]` to `backend/requirements.txt`
- [x] 1.2 Add `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` + 5× `POSTGRES_USER_{ROL}` vars + `POSTGRES_PASSWORD_{ROL}` to `config.py`
- [x] 1.3 Add `ROL_DATABASE_URLS` dict mapping each role to its DB URL in `config.py`
- [x] 1.4 Add 5 role credentials + `SECRET_KEY` env vars to `docker-compose.yml`
- [x] 1.5 Add `SECRET_KEY` + role credentials to `backend/.env.example`

## Phase 2: DB Hardening & Model Extension

- [x] 2.1 [RED] Write `tests/models/test_usuario_extended.py` — email unique, estado default, rol validation (ValueError)
- [x] 2.2 [GREEN] Extend `Usuario` model: email VARCHAR(255) unique, estado BOOLEAN server_default=true, Python Enum validator for rol
- [x] 2.3 [RED] Write test for `get_role_session()` — verifies role-specific engine selection
- [x] 2.4 [GREEN] Add `get_role_session(role)` to `database.py` — multi-engine with pool_size=1, max_overflow=1
- [x] 2.5 Create `db/init/02-role-users.sh` — bash script using env vars from docker-compose to CREATE USER + GRANT per role
- [x] 2.6 Create `db/migrations/01-add-usuario-columns.sql` — ALTER TABLE ADD COLUMN IF NOT EXISTS email, estado
- [x] 2.7 Create `db/init/04-seed-test-users.sql` — INSERT one deterministic usuario per role (seed runs via db/init/)

## Phase 3: Auth Module Core

- [x] 3.1 [RED] Write `tests/auth/test_jwt_handler.py` — crear/validate/expired/tampered/missing-key scenarios
- [x] 3.2 [GREEN] Implement `auth/jwt_handler.py` — `crear_token_jwt()`, `validar_token_jwt()`, HS256
- [x] 3.3 [RED] Write `tests/auth/test_schemas.py` — LoginRequest, TokenResponse, TokenData validation
- [x] 3.4 [GREEN] Implement `auth/schemas.py` — LoginRequest(rut, password), TokenResponse, TokenData(sub, role, exp)
- [x] 3.5 [RED] Write `tests/auth/test_dependencies.py` — get_current_user, requiere_rol 401/403, get_role_session
- [x] 3.6 [GREEN] Implement `auth/dependencies.py` — OAuth2PasswordBearer, get_current_user, requiere_rol factory, get_role_session

## Phase 4: Integration & Verification

- [x] 4.1 Wire auth module into `main.py` — ensure importable, dependencies registered
- [x] 4.2 Add return-type annotations and pass `ruff check` across auth/ and models/
- [x] 4.3 Run full `pytest` suite — all RED→GREEN tests pass
- [x] 4.4 Verify coverage ≥80% on `backend/src/auth/`
