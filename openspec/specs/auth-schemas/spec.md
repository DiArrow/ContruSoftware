# Auth Schemas Specification

## Purpose

Pydantic models for auth contracts.

## Requirements

### Requirement: LoginRequest

`LoginRequest` with `rut: str`, `password: str`, both required.

| Scenario | Given | When | Then |
|----------|-------|------|------|
| valid | `rut="12345678-9"`, `password="secret"` | instantiated | accepted |
| missing | only `rut` | instantiated | validation error |

### Requirement: TokenResponse

`TokenResponse` with `access_token: str`, `token_type: str` (default `"bearer"`).

| Scenario | Given | When | Then |
|----------|-------|------|------|
| created | `access_token="eyJ..."` | instantiated | `token_type` = `"bearer"` |

### Requirement: TokenData

`TokenData` with `sub: str`, `role: str`, `exp: datetime | None`.

| Scenario | Given | When | Then |
|----------|-------|------|------|
| from payload | `{"sub":"u1","role":"ADM","exp":1700000000}` | instantiated | all fields set |
