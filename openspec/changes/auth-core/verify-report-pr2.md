## Verification Report

**Change**: auth-core
**Version**: PR 2 — Auth Module + Integration
**Mode**: Strict TDD

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 10 (PR 2: 3.1–3.6 + 4.1–4.4) |
| Tasks complete | 10 |
| Tasks incomplete | 0 |

### TDD Compliance

| Task | RED | GREEN | REFACTOR |
|------|-----|-------|----------|
| 3.1 jwt_handler RED | tests written, import errors | 7 tests pass | Clean |
| 3.3 schemas RED | tests written, import errors | 9 tests pass | Clean |
| 3.5 dependencies RED | tests written, import errors | 6 tests pass | Clean |

All TDD cycles followed: RED (failing) → GREEN (implementing) → REFACTOR (clean).

### Build & Tests Execution

**Build**: ✅ Passed (Docker compose up --build, all 3 containers healthy)

**Tests (local venv)**: ✅ 22 passed / ❌ 0 failed / ⚠️ 0 skipped

```
cd backend && .venv/bin/python -m pytest tests/auth/ -v
======================== 22 passed, 1 warning in 0.03s =========================
```

**Coverage**: 100% / threshold: 80% → ✅ Above

```
Name                       Stmts   Miss  Cover   Missing
--------------------------------------------------------
src/auth/__init__.py           0      0   100%
src/auth/dependencies.py      21      0   100%
src/auth/jwt_handler.py       15      0   100%
src/auth/schemas.py            6      0   100%
--------------------------------------------------------
TOTAL                         42      0   100%
```

**Ruff linter**: ✅ All checks passed on `src/auth/` and `src/models/` (both local venv and Docker container).

### Spec Compliance Matrix

#### jwt-handler (2 requirements, 6 scenarios)

| Req | Scenario | Test | Result |
|-----|----------|------|--------|
| JWT Creation | default | test_crear_token_jwt_returns_str / test_crear_token_jwt_contains_sub_role_exp | ✅ COMPLIANT |
| JWT Creation | custom expiry | test_crear_token_jwt_exp_is_not_in_the_future_when_zero_delta | ⚠️ PARTIAL — tests zero delta only, not positive delta |
| JWT Creation | missing key | test_crear_token_jwt_missing_secret_key_raises_runtimeerror | ✅ COMPLIANT |
| JWT Validation | valid | test_validar_token_jwt_returns_payload | ✅ COMPLIANT |
| JWT Validation | expired | test_validar_token_jwt_expired_raises_jwt_error | ✅ COMPLIANT |
| JWT Validation | tampered | test_validar_token_jwt_tampered_raises_jwt_error | ✅ COMPLIANT |

#### auth-dependencies (3 requirements, 7 scenarios)

| Req | Scenario | Test | Result |
|-----|----------|------|--------|
| OAuth2 Token Extraction | valid | test_get_current_user_valid_token (token passed directly, not via header) | ⚠️ PARTIAL — FastAPI-native OAuth2 header extraction not unit-tested |
| OAuth2 Token Extraction | missing | Not directly tested; OAuth2PasswordBearer returns 401 natively | ⚠️ PARTIAL — FastAPI-native behavior |
| Get Current User | valid | test_get_current_user_valid_token | ✅ COMPLIANT |
| Get Current User | invalid | test_get_current_user_invalid_token_raises_401 | ✅ COMPLIANT |
| Role-Based Access | matches | test_allowed_role_returns_user | ✅ COMPLIANT |
| Role-Based Access | mismatch | test_forbidden_role_raises_403 | ✅ COMPLIANT |
| Role-Based Access | empty | test_empty_roles_raises_500 | ⚠️ PARTIAL — spec says 403, impl returns 500 (config error vs auth error) |

#### auth-schemas (3 requirements, 4 scenarios)

| Req | Scenario | Test | Result |
|-----|----------|------|--------|
| LoginRequest | valid | test_valid_login_request | ✅ COMPLIANT |
| LoginRequest | missing | test_missing_rut_raises_validation_error / test_missing_password_raises_validation_error | ✅ COMPLIANT |
| TokenResponse | created | test_valid_token_response | ✅ COMPLIANT |
| TokenData | from payload | test_valid_token_data | ✅ COMPLIANT |

**Compliance summary**: 13/17 scenarios fully compliant (4 PARTIAL)

### Correctness (Static Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| crear_token_jwt() creates JWT with HS256 | ✅ Implemented | jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) |
| validar_token_jwt() decodes and validates | ✅ Implemented | jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]), raises JWTError |
| _ensure_secret_key() runtime check | ✅ Implemented | Raises RuntimeError on empty SECRET_KEY |
| LoginRequest(rut, password) Pydantic v2 | ✅ Implemented | Both fields required, ValidationError on missing |
| TokenResponse default token_type="bearer" | ✅ Implemented | Default value set correctly |
| TokenData(sub, role, exp) | ✅ Implemented | All fields required, exp as datetime |
| oauth2_scheme OAuth2PasswordBearer | ✅ Implemented | tokenUrl="/auth/token" |
| get_current_user() → 401 on invalid/expired | ✅ Implemented | Catches JWTError, raises 401 |
| requiere_rol(roles) factory | ✅ Implemented | Returns closure, checks user["role"] in roles |
| get_role_session re-export | ✅ Implemented | Correctly re-exports from src.database |
| main.py imports oauth2_scheme | ✅ Implemented | from src.auth.dependencies import oauth2_scheme |
| python-jose[cryptography] in requirements.txt | ✅ Present | python-jose[cryptography]>=3.3.0 |
| SECRET_KEY from env | ✅ Implemented | SECRET_KEY = os.getenv("SECRET_KEY", "") |

### Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| python-jose for JWT | ✅ Yes | from jose import jwt in both handler and test |
| SECRET_KEY from env via config constant | ✅ Yes | config.py reads from env, empty string default |
| Multi-engine role DB connections | ✅ Yes | get_role_session(role) with per-role engines |
| Python validator for rol enum | ✅ Yes | @validates('rol') on Usuario model |
| OAuth2PasswordBearer(tokenUrl="/auth/token") | ✅ Yes | Defined in dependencies.py |
| Factory closure for role dep | ✅ Yes | requiere_rol(roles) returns _check_role closure |
| Package init with re-exports | ⚠️ Partial | __init__.py is empty — no explicit re-exports |
| DB permission matrix (5 roles) | ✅ Yes | 02-role-users.sh creates 5 role users with tiered GRANTs |
| Seed test users (one per role) | ✅ Yes | 5 rows inserted (SOL/EST/AYU/PRO/ADM) |

### Container Verification

| Check | Result | Evidence |
|-------|--------|----------|
| Backend container starts without errors | ✅ Passed | Application startup complete. Uvicorn running on 0.0.0.0:8000 |
| DB container runs init scripts | ✅ Passed | 02-role-users.sh (DO, GRANT x5), 02-users.sh, 04-seed-test-users.sql (INSERT 0 5) |
| Health endpoint returns 200 | ✅ Passed | curl localhost:8000/health → {"status":"ok"} |
| Auth module importable (src.auth) | ✅ Passed | from src.auth import jwt_handler, schemas, dependencies — OK |
| python-jose available in container | ✅ Passed | from jose import jwt — OK, v3.5.0 |
| JWT roundtrip (create+validate) | ✅ Passed | Token sub=test role=ADM decoded successfully |
| Ruff check in container | ✅ Passed | ruff check src/auth/ src/models/ — all passed |
| 5 role PostgreSQL users created | ✅ Passed | sol_user, est_user, ayu_user, pro_user, adm_user |
| 5 seed usuarios inserted | ✅ Passed | One per role: SOL, EST, AYU, PRO, ADM |
| email column (UNIQUE) exists | ✅ Passed | usuario_email_key UNIQUE CONSTRAINT |
| estado column default=true | ✅ Passed | All seeded users show estado = t |

### Issues Found

**CRITICAL**: None.

**WARNING**:
1. **Dockerfile path mismatch** — Original backend Dockerfile had `COPY ./src/ .` (contents to /app) but code uses `from src.xxx` imports. Fixed during verification: changed to `COPY ./src /app/src/` and `CMD ["uvicorn", "src.main:app", ...]`. This pre-existing issue would have prevented the backend container from starting.
2. **spec vs implementation: empty roles** — The spec says `requiere_rol()` with empty roles should return 403, but the implementation returns 500 (treating it as a configuration error). The test explicitly tests for 500. This is a spec/implementation disagreement to resolve.
3. **python-jose path confusion** — python-jose IS installed in .venv but tests failed when run with system Python. The correct venv interpreter must be used.

**SUGGESTION**:
1. **Empty __init__.py** — backend/src/auth/__init__.py is empty (0 lines). The design says "Package init, re-exports". Consider adding a docstring.
2. **OAuth2 header extraction not integration-tested** — The OAuth2PasswordBearer header extraction scenarios are not directly tested with TestClient. Risk is low (FastAPI-native behavior) but integration tests would increase confidence.
3. **Positive expiry delta not tested** — The spec's "custom expiry" scenario (5-minute delta) is only tested with zero delta. A test with timedelta(minutes=5) would be more thorough.
4. **Full test suite requires PostgreSQL** — The 22 auth tests run independently. The full 166-test suite needs PostgreSQL. Consider documenting local PG requirement.

### Verdict

**PASS WITH WARNINGS**

The auth module implementation is complete, well-tested (22/22 auth tests pass, 100% auth coverage), linter-clean, and verified working inside Docker containers. All 10 PR 2 tasks are complete with strict TDD cycles followed. The 3 warnings are non-blocking: the Dockerfile fix is now applied, the empty-roles spec discrepancy is a design decision to clarify, and the Python path issue is a development environment concern. The 4 suggestions are improvements, not defects. The implementation matches the design decisions and passes container verification with all DB init scripts executing correctly.
