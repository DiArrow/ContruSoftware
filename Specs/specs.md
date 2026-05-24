# SDD Specs — ContruSoftware

Este directorio contiene las especificaciones técnicas para cada cambio del proyecto, alineadas con las issues definidas en `Specs/Issues.md`.

## Especificaciones

| Spec | Issue | Estado | Dependencias |
|------|-------|--------|-------------|
| [spec-db-init.md](./spec-db-init.md) | #2 — Esquema de Datos en PostgreSQL | ✅ Completado | Ninguna |
| [spec-sqlalchemy-models.md](./spec-sqlalchemy-models.md) | #4 — Modelos SQLAlchemy + DB | Pendiente | spec-db-init |
| [spec-auth-core.md](./spec-auth-core.md) | #5 — Auth JWT + RBAC | Pendiente | spec-sqlalchemy-models |
| [spec-google-oauth2.md](./spec-google-oauth2.md) | #6 — Google OAuth2 | Pendiente | spec-auth-core |

## Cadena de Dependencias

```
spec-db-init → spec-sqlalchemy-models → spec-auth-core → spec-google-oauth2
```

## Estándares Aplicables

Todos los specs deben cumplir con los estándares del `README.md`:

- **Python**: PEP 8 + Black (Ruff), tipado estático, máximo 3 argumentos por función, inyección de dependencias
- **SQL**: SQLFluff — keywords MAYÚSCULAS, identificadores minúsculas
- **Indentación**: 4 espacios en todo el proyecto
- **Commits**: `feat:`, `fix:`, `docs:`, `refactor:`
- **Seguridad**: cero credenciales en código, todo vía variables de entorno
