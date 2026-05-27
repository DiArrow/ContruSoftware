# Proposal: Auth Core — JWT Authentication & RBAC Middleware

## Intent

The system lacks authentication and authorization. Any endpoint is freely accessible. This change establishes the auth foundation — JWT creation/validation, OAuth2 token extraction, and role-based access control (RBAC) — so all future endpoints (including Google OAuth2) can secure access by role.

## Scope

### In Scope
- JWT creation and validation with `HS256`, `SECRET_KEY` from env, configurable expiry
- `OAuth2PasswordBearer` token extraction from `Authorization` header
- RBAC dependency `requiere_rol(roles)` returning 401/403 appropriately
- Pydantic schemas for login request and token response
- Extend `Usuario` model with `email` (unique), `estado` (boolean), and `rol` validation (SOL/EST/AYU/PRO/ADM)
- Auth config constants in `config.py` (`SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`)

### Out of Scope
- Google OAuth2 login flow (deferred to `spec-google-oauth2`)
- `/auth/token` endpoint implementation (authentication layer, not auth core)
- Password hashing (part of auth endpoint, not core middleware)
- Frontend auth integration

## Capabilities

### New Capabilities
- `jwt-handler`: JWT creation (`crear_token_jwt`) and validation (`validar_token_jwt`) with `HS256`, env-driven `SECRET_KEY`, and configurable `expires_delta`
- `auth-dependencies`: FastAPI dependencies — `get_current_user` (decodes token), `requiere_rol(roles)` (RBAC gate returning 401/403), and `OAuth2PasswordBearer` scheme pointing to `/auth/token`
- `auth-schemas`: Pydantic models for `LoginRequest`, `TokenResponse`, and `TokenData` (sub, role, exp)

### Modified Capabilities
- `sqlalchemy-models`: Add `email` `VARCHAR(255)` unique column, `estado` `BOOLEAN` default `True`, and enforce `rol` values via enum validation (`SOL`, `EST`, `AYU`, `PRO`, `ADM`) on `Usuario`

## Approach

Create `backend/src/auth/` module with `jwt_handler.py`, `dependencies.py`, and `schemas.py`. Add auth config vars to `config.py`. Extend `Usuario` model with `email`, `estado`, and role validation. Use dependency injection for `SECRET_KEY` and `SessionLocal`. TDD: write tests first for each component.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/src/auth/__init__.py` | New | Package init |
| `backend/src/auth/jwt_handler.py` | New | JWT creation & validation |
| `backend/src/auth/dependencies.py` | New | get_current_user, requiere_rol, OAuth2 scheme |
| `backend/src/auth/schemas.py` | New | Pydantic login/token schemas |
| `backend/src/config.py` | Modified | Add SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES |
| `backend/src/models/usuario.py` | Modified | Add email, estado, rol validation |
| `backend/src/main.py` | Modified | Register auth dependencies |
| `backend/.env.example` | Modified | Add SECRET_KEY entry |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| SECRET_KEY leaked in code | Low | Env-var-only, never hardcode, add to .gitignore |
| Token format breaks future Google OAuth2 | Med | Design JWT payload to be extensible (sub + role, not email-specific) |
| Usuario migration needed for new columns | Med | SQL ALTER TABLE script for existing deployments |

## Rollback Plan

Remove `backend/src/auth/` directory, revert `config.py`, `usuario.py`, `main.py`, and `.env.example` to previous versions. No database migration tool exists yet, so rollback SQL for new columns must be documented.

## Dependencies

- `spec-sqlalchemy-models` (Usuario model must exist)
- `python-jose[cryptography]` for JWT encoding/decoding
- `passlib[bcrypt]` for future password hashing (install now, use later)

## Success Criteria

- [ ] `crear_token_jwt` returns valid JWT with sub, role, exp
- [ ] `validar_token_jwt` decodes valid tokens, raises on expired/invalid
- [ ] `requiere_rol(["ADM"])` grants access to ADM users, returns 403 for others
- [ ] Invalid/expired token returns 401 Unauthorized
- [ ] `SECRET_KEY` read from env var, never hardcoded
- [ ] All auth functions have static typing, pass `ruff check`
- [ ] Tests written FIRST (TDD), ≥80% coverage on `auth/`