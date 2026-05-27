# JWT Handler Specification

## Purpose

JWT creation/validation with HS256, env SECRET_KEY.

## Requirements

### Requirement: JWT Creation

`crear_token_jwt(data: dict, expires_delta: timedelta | None = None) -> str` using HS256.

| Scenario | Given | When | Then |
|----------|-------|------|------|
| default | valid SECRET_KEY | `crear_token_jwt({"sub":"u1","role":"ADM"})` | valid JWT, decodes to payload |
| custom expiry | valid SECRET_KEY | `expires_delta=timedelta(minutes=5)` | `exp` = now + 5min |
| missing key | SECRET_KEY unset | `crear_token_jwt(...)` | `RuntimeError` |

### Requirement: JWT Validation

`validar_token_jwt(token: str) -> dict` decodes and validates.

| Scenario | Given | When | Then |
|----------|-------|------|------|
| valid | token from `crear_token_jwt`, within expiry | `validar_token_jwt(token)` | payload returned |
| expired | zero-expiry token, after expiry | `validar_token_jwt(token)` | `JWTError` |
| tampered | valid JWT, signature altered | `validar_token_jwt(token)` | `JWTError` |
