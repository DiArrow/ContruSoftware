# Spec: Core de Autenticación y Middleware de Seguridad

**Issue**: #5  
**Label**: Backend, Infraestructura  
**Dependencias**: spec-sqlalchemy-models (necesita el modelo `Usuario`)

## Contexto

El sistema necesita autenticación JWT con control de acceso basado en roles (RBAC). Los roles válidos son: `SOL` (Solicitante), `EST` (Estudiante), `AYU` (Ayudante), `PRO` (Profesor), `ADM` (Administrador). Este core es la base para cualquier método de login, incluido Google OAuth2 futuro.

## Requisitos

### R1 — OAuth2PasswordBearer

- [ ] Implementar `OAuth2PasswordBearer` para extraer el token del header `Authorization`
- [ ] El token URL debe ser `/auth/token` (endpoint de login con credenciales)

### R2 — Generación y Validación de JWT

- [ ] Función `crear_token_jwt(data: dict, expires_delta: timedelta) -> str`
- [ ] Función `validar_token_jwt(token: str) -> dict` con verificación de expiración
- [ ] `SECRET_KEY` desde variable de entorno, nunca hardcodeada
- [ ] Algoritmo `HS256`
- [ ] El payload incluye: `sub` (id_usuario), `role`, `exp`

### R3 — Middleware RBAC

- [ ] Dependencia FastAPI `requiere_rol(roles: list[str])` que verifica el rol del usuario
- [ ] Si el rol no está en la lista permitida, retorna `403 Forbidden`
- [ ] Si el token es inválido o expirado, retorna `401 Unauthorized`

### R4 — Modelo de Usuario Extendido

- [ ] El modelo `Usuario` incluye: `email`, `rol`, `estado` (activo/inactivo)
- [ ] `rol` es un enum o string con validación: `SOL`, `EST`, `AYU`, `PRO`, `ADM`
- [ ] `estado` es booleano (activo = True)

### R5 — Estándares de Código

- [ ] Tipado estático en todas las funciones
- [ ] PEP 8 + Black verificado por Ruff
- [ ] Máximo 3 argumentos por función
- [ ] Inyección de dependencias para `SessionLocal` y `SECRET_KEY`

## Escenarios

### Escenario 1: Creación de token

**Dado** un usuario autenticado con `id_usuario="abc-123"` y `rol="EST"`  
**Cuando** se llama `crear_token_jwt({"sub": "abc-123", "role": "EST"})`  
**Entonces** se retorna un JWT válido que al decodificar contiene `sub`, `role`, y `exp`

### Escenario 2: Validación de token válido

**Dado** un JWT creado con `crear_token_jwt`  
**Cuando** se llama `validar_token_jwt(token)` antes de la expiración  
**Entonces** retorna el payload con `sub` y `role`

### Escenario 3: Token expirado

**Dado** un JWT con `expires_delta=timedelta(seconds=0)`  
**Cuando** se llama `validar_token_jwt(token)`  
**Entonces** lanza excepción de token expirado

### Escenario 4: Acceso con rol correcto

**Dado** un endpoint protegido con `requiere_rol(["ADM", "PRO"])`  
**Cuando** un usuario con `role="ADM"` hace la petición con token válido  
**Entonces** el acceso es permitido

### Escenario 5: Acceso con rol incorrecto

**Dado** un endpoint protegido con `requiere_rol(["ADM"])`  
**Cuando** un usuario con `role="EST"` hace la petición con token válido  
**Entonces** retorna `403 Forbidden`

### Escenario 6: Token inválido

**Dado** un endpoint protegido  
**Cuando** la petición tiene un token malformado  
**Entonces** retorna `401 Unauthorized`

## Estructura Propuesta

```
backend/src/
├── auth/
│   ├── __init__.py
│   ├── jwt_handler.py      # crear_token_jwt, validar_token_jwt
│   ├── dependencies.py     # get_current_user, requiere_rol
│   └── schemas.py          # Pydantic schemas para login/token
├── config.py               # SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
├── database.py             # (ya existe del spec anterior)
├── models/                 # (ya existe del spec anterior)
│   └── usuario.py          # Actualizar con campos de auth
└── main.py                 # Registrar dependencias de auth
```

## Constantes

```python
ROLES_VALIDOS = ["SOL", "EST", "AYU", "PRO", "ADM"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

## Criterios de Aceptación

- [ ] `crear_token_jwt` genera tokens decodificables con `sub`, `role`, `exp`
- [ ] `validar_token_jwt` rechaza tokens expirados y malformados
- [ ] `requiere_rol` bloquea accesos con rol incorrecto (403)
- [ ] `requiere_rol` bloquea tokens inválidos (401)
- [ ] `SECRET_KEY` viene de variable de entorno
- [ ] `ruff check backend/src/` pasa sin errores
- [ ] Tipado estático en todas las funciones de auth

## Archivos Afectados

| Archivo | Acción |
|---------|--------|
| `backend/src/auth/__init__.py` | Crear nuevo |
| `backend/src/auth/jwt_handler.py` | Crear nuevo |
| `backend/src/auth/dependencies.py` | Crear nuevo |
| `backend/src/auth/schemas.py` | Crear nuevo |
| `backend/src/config.py` | Modificar — agregar SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES |
| `backend/src/models/usuario.py` | Modificar — agregar campos email, rol (validado), estado |
| `backend/src/main.py` | Modificar — integrar OAuth2PasswordBearer |
| `env.example` | Modificar — agregar SECRET_KEY |
