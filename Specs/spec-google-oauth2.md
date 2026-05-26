# Spec: Integración Google OAuth2 y Registro Automático

**Issue**: #6  
**Label**: Backend, Infraestructura  
**Dependencias**: spec-auth-core (necesita JWT + RBAC funcionando)

## Contexto

El sistema debe permitir autenticación mediante Google OAuth2. El flujo recibe credenciales de Google, valida la identidad, y vincula al usuario con el sistema interno de permisos (JWT/RBAC). Los usuarios nuevos se registran automáticamente con rol `SOL` (Solicitante).

## Requisitos

### R1 — Estrategia OAuth2

- [ ] Usar `authlib` o `fastapi-sso` para el flujo OAuth2 con Google
- [ ] Credenciales de Google (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`) desde variables de entorno
- [ ] `REDIRECT_URI` configurable vía variable de entorno

### R2 — Endpoint `/auth/login`

- [ ] `GET /auth/login` genera y retorna la URL de redirección a Google
- [ ] La URL incluye los scopes mínimos necesarios: `openid`, `email`, `profile`
- [ ] Visible en `/docs` (Swagger) con esquema de respuesta

### R3 — Endpoint `/auth/callback`

- [ ] `GET /auth/callback` procesa el `code` de autorización de Google
- [ ] Verifica el `id_token` recibido
- [ ] Extrae: `email`, `nombre`, `imagen` (si disponible)
- [ ] Retorna JWT propio del sistema con `sub` y `role`

### R4 — Sincronización de Usuarios

- [ ] Si el email NO existe en PostgreSQL: crear usuario con rol `SOL`, estado activo
- [ ] Si el email YA existe: actualizar `nombre` e `imagen` si hubo cambios
- [ ] El usuario creado/actualizado recibe un JWT del sistema

### R5 — Respuesta del Flujo

- [ ] El JWT retornado contiene: `sub` (id_usuario), `role`, `exp`
- [ ] Formato de respuesta coherente con el spec de auth-core
- [ ] Endpoints visibles en `/docs` con esquemas de respuesta

### R6 — Estándares de Código

- [ ] Tipado estático en todas las funciones
- [ ] PEP 8 + Black verificado por Ruff
- [ ] Máximo 3 argumentos por función
- [ ] Inyección de dependencias para `SessionLocal` y configuración OAuth

## Escenarios

### Escenario 1: Login — primer acceso

**Dado** un usuario que nunca ha ingresado al sistema  
**Cuando** completa el flujo OAuth2 con Google  
**Entonces**:
- Se crea un registro en `usuario` con su email, nombre, rol `SOL`, estado activo
- Se retorna un JWT con `sub=id_usuario`, `role="SOL"`

### Escenario 2: Login — usuario existente

**Dado** un usuario que ya existe en la base de datos  
**Cuando** completa el flujo OAuth2 con Google  
**Entonces**:
- Se actualizan sus datos de perfil si cambiaron en Google
- Se retorna un JWT con su `sub` y `role` actual

### Escenario 3: Token de Google inválido

**Dado** un `code` de autorización expirado o manipulado  
**Cuando** se llama `/auth/callback`  
**Entonces** retorna `401 Unauthorized` con mensaje de error descriptivo

### Escenario 4: Google no responde

**Dado** que el servidor de Google no responde  
**Cuando** se llama `/auth/callback`  
**Entonces** retorna `502 Bad Gateway` con mensaje de error

### Escenario 5: Redirección de login

**Dado** un usuario que accede a `/auth/login`  
**Cuando** el endpoint responde  
**Entonces** retorna la URL de autorización de Google a la que el usuario debe ser redirigido

## Estructura Propuesta

```
backend/src/
├── auth/
│   ├── __init__.py          # (ya existe)
│   ├── jwt_handler.py       # (ya existe)
│   ├── dependencies.py      # (ya existe)
│   ├── schemas.py           # (ya existe)
│   └── google_oauth.py      # NUEVO — OAuth2 con Google
├── config.py                # Modificar — agregar GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, REDIRECT_URI
├── database.py              # (ya existe)
├── models/                  # (ya existe)
│   └── usuario.py           # (ya existe)
└── main.py                  # Modificar — registrar endpoints /auth/*
```

## Constantes

```python
GOOGLE_SCOPES = ["openid", "email", "profile"]
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
ROL_POR_DEFECTO = "SOL"
```

## Variables de Entorno Nuevas

```
GOOGLE_CLIENT_ID=<client_id>
GOOGLE_CLIENT_SECRET=<client_secret>
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
```

## Criterios de Aceptación

- [ ] `GET /auth/login` retorna URL de redirección a Google
- [ ] `GET /auth/callback?code=...` procesa el código y retorna JWT
- [ ] Usuarios nuevos se crean con rol `SOL` automáticamente
- [ ] Usuarios existentes se actualizan si hubo cambios
- [ ] Tokens de Google inválidos retornan `401`
- [ ] Endpoints visibles en `/docs` con esquemas de respuesta
- [ ] Credenciales de Google NO están hardcodeadas
- [ ] `ruff check backend/src/` pasa sin errores
- [ ] Tipado estático en todas las funciones

## Archivos Afectados

| Archivo | Acción |
|---------|--------|
| `backend/src/auth/google_oauth.py` | Crear nuevo |
| `backend/src/config.py` | Modificar — agregar credenciales Google |
| `backend/src/main.py` | Modificar — registrar endpoints /auth/* |
| `env.example` | Modificar — agregar variables de Google OAuth |
| `backend/requirements.txt` o `pyproject.toml` | Agregar `authlib` o `fastapi-sso` |
