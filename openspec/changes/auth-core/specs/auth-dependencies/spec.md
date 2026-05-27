# Auth Dependencies Specification

## Purpose

FastAPI deps for token extraction, user resolution, RBAC.

## Requirements

### Requirement: OAuth2 Token Extraction

`OAuth2PasswordBearer(tokenUrl="/auth/token")`.

| Scenario | Given | When | Then |
|----------|-------|------|------|
| valid | `Authorization: Bearer <jwt>` | scheme invoked | JWT extracted |
| missing | no Authorization header | scheme invoked | 401 |

### Requirement: Get Current User

`get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData`.

| Scenario | Given | When | Then |
|----------|-------|------|------|
| valid | JWT with `sub`, `role` | called | `TokenData` returned |
| invalid | malformed/expired JWT | called | 401, `"Invalid or expired token"` |

### Requirement: Role-Based Access Control

`requiere_rol(*roles: str) -> Callable`.

| Scenario | Given | When | Then |
|----------|-------|------|------|
| matches | user `"ADM"` | `requiere_rol("ADM","PRO")` | proceeds |
| mismatch | user `"EST"` | `requiere_rol("ADM","PRO")` | 403, `"Insufficient role"` |
| empty | any user | `requiere_rol()` | 403 |
