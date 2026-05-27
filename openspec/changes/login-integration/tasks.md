# Tasks: Login Integration

## Review Workload Forecast

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Backend Foundation — hasher, model, schemas, deps, migration/seed | PR 1 | Base: `feat/login-integration`. Tests included. |
| 2 | Auth Endpoints — POST /auth/token, GET /auth/me, router registration | PR 2 | Base: PR 1 branch. Depends on hasher + schema from PR 1. |
| 3 | Frontend Auth — client.js, AuthContext, Login.jsx, App.jsx | PR 3 | Base: PR 2 branch. Needs backend endpoints from PR 2. |
| 4 | Docker + Integration — nginx proxy_pass, compose verify, e2e login | PR 4 | Base: PR 3 branch. Requires all previous changes. |

## Phase 1: Backend Foundation

- [x] 1.1 Add `passlib[bcrypt]` and `email-validator` to `backend/requirements.txt`
- [x] 1.2 Create `backend/src/auth/hasher.py` — `CryptContext`, `verificar_password()`, `hash_password()`
- [x] 1.3 Add `password_hash = Column(String, nullable=False, default="")` to `backend/src/models/usuario.py`
- [x] 1.4 Create `db/migrations/02-add-password-hash.sh` — psql ALTER TABLE with env vars for DB creds
- [x] 1.5 Create `db/seeds/02-admin-user.sh` — psql INSERT admin user with env vars for credentials
- [x] 1.6 Update `backend/src/auth/schemas.py` — `LoginRequest.rut` → `LoginRequest.email: EmailStr`, add `UsuarioResponse`
- [x] 1.7 Update `backend/tests/auth/test_schemas.py` — replace `rut` tests with `email: EmailStr` + validation scenarios

## Phase 2: Auth Endpoints

- [ ] 2.1 Create `backend/src/auth/router.py` — `POST /auth/token` with credential validation + JWT issuance (scenarios: valid, wrong password, unknown email, empty body, missing fields)
- [ ] 2.2 Add `GET /auth/me` to `backend/src/auth/router.py` — decode JWT, query Usuario, return UsuarioResponse (scenarios: valid token, missing, expired, deleted user)
- [ ] 2.3 Register auth router in `backend/src/main.py`: `app.include_router(auth_router)`
- [ ] 2.4 Write backend integration tests — FastAPI TestClient for login success, 401, 422; GET /auth/me auth/unauth

## Phase 3: Frontend Auth

- [ ] 3.1 Create `frontend/src/api/client.js` — native fetch wrapper with base URL `/api/`, auto Bearer injection from localStorage, JSON error handling
- [ ] 3.2 Create `frontend/src/context/AuthContext.jsx` — React context with `currentUser`, login(email,pw), logout(), localStorage persistence, `/auth/me` fetch on mount
- [ ] 3.3 Update `frontend/src/pages/Login.jsx` — controlled inputs, `authContext.login()` call, error display, loading state
- [ ] 3.4 Update `frontend/src/App.jsx` — wrap with `AuthProvider`, conditional render, pass currentUser to Topbar
- [ ] 3.5 Write frontend unit tests — client.js mock fetch, AuthContext login/logout/persistence, Login.jsx controlled form + error states

## Phase 4: Docker + Integration

- [ ] 4.1 Update `frontend/nginx.conf` — add `location /api/ { proxy_pass http://backend:8000/; }`, `/docs`, `/openapi.json`
- [ ] 4.2 Verify Docker containers build: `docker compose build` with no errors
- [ ] 4.3 E2E login flow in Docker: `docker compose up` → POST /api/auth/token → GET /api/auth/me → frontend reaches backend via proxy

## Implementation Order

Phase 1 (db + backend core) must complete before Phase 2 (endpoints) since endpoints depend on hasher and schema. Phase 3 (frontend) needs Phase 2 endpoints live. Phase 4 (Docker) wraps all changes together. Each phase produces independently testable output — tests are bundled in the same phase as the code they verify.
