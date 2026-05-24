# Spec: Modelos SQLAlchemy e Integración con Base de Datos

**Issue**: #4  
**Label**: Infraestructura, backend  
**Dependencias**: spec-db-init (el esquema SQL debe existir primero)

## Contexto

El backend (`backend/src/main.py`) es un esqueleto FastAPI sin conexión a base de datos. Se necesitan modelos SQLAlchemy que reflejen las 13 tablas del esquema SQL, configuración de conexión, y la integración con PostgreSQL.

## Requisitos

### R1 — Configuración de Base de Datos

- [ ] Módulo de configuración con `SQLALCHEMY_DATABASE_URL` desde variables de entorno
- [ ] Crear `engine`, `SessionLocal`, y `Base` exportables
- [ ] Inyección de dependencias: la sesión se pasa como parámetro, no se instancia internamente

### R2 — Modelos SQLAlchemy

- [ ] Los 13 modelos reflejan exactamente las columnas del `init.sql`
- [ ] Primary keys como `String(36)` (UUID)
- [ ] Foreign keys con `ForeignKey()` y relaciones `relationship()` donde aplique
- [ ] Timestamps con `server_default=func.now()` para `creado_en` y `actualizado_en`
- [ ] Nombres de tablas en minúsculas (coherencia con SQLFluff)

### R3 — Conexión y Verificación

- [ ] La app FastAPI se conecta a PostgreSQL al iniciar
- [ ] Endpoint de health check que verifica conexión a DB
- [ ] Credenciales leídas desde variables de entorno (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`)

### R4 — Estándares de Código

- [ ] Todo código Python con tipado estático
- [ ] PEP 8 + Black verificado por Ruff
- [ ] Máximo 3 argumentos por función
- [ ] Inyección de dependencias para la sesión de DB

## Escenarios

### Escenario 1: Conexión exitosa

**Dado** que las variables de entorno están configuradas  
**Cuando** el backend inicia  
**Entonces** se conecta a PostgreSQL y el health check retorna `{"status": "ok"}`

### Escenario 2: Modelo refleja esquema

**Dado** el modelo `Usuario` en SQLAlchemy  
**Cuando** se consulta `usuario.__table__.columns`  
**Entonces** las columnas coinciden con `init.sql`: `id_usuario`, `nombre`, `apellido`, `correo`, `rol`, `creado_en`, `actualizado_en`

### Escenario 3: Relación entre modelos

**Dado** los modelos `Curso` y `Semestre`  
**Cuando** se accede `curso.semestre`  
**Entonces** se obtiene el objeto `Semestre` relacionado vía `ref_semestre`

## Estructura Propuesta

```
backend/src/
├── main.py              # FastAPI app + rutas
├── config.py            # Variables de entorno + DB URL
├── database.py          # engine, SessionLocal, Base, get_db
└── models/
    ├── __init__.py      # Exporta todos los modelos
    ├── usuario.py
    ├── semestre.py
    ├── curso.py
    ├── estudiante.py
    ├── grupo_estudiante.py
    ├── ayudantia.py
    ├── inscripcion_ayudantia.py
    ├── articulo.py
    ├── impresion.py
    ├── uso_impresora.py
    ├── reserva.py
    ├── bloque_horario.py
    ├── bloque_reservado.py
    └── movimiento_stock.py
```

## Criterios de Aceptación

- [ ] `backend/src/database.py` exporta `engine`, `SessionLocal`, `Base`, `get_db`
- [ ] Cada modelo en `backend/src/models/` tiene su archivo propio
- [ ] Los modelos reflejan las 13 tablas del `init.sql`
- [ ] `ruff check backend/src/` pasa sin errores
- [ ] Las credenciales NO están hardcodeadas
- [ ] Endpoint `GET /health` verifica conexión a DB

## Archivos Afectados

| Archivo | Acción |
|---------|--------|
| `backend/src/config.py` | Crear nuevo |
| `backend/src/database.py` | Crear nuevo |
| `backend/src/models/__init__.py` | Crear nuevo |
| `backend/src/models/*.py` (13 archivos) | Crear nuevos |
| `backend/src/main.py` | Modificar — agregar health check, eliminar ejemplo |
| `backend/.env` o `env.example` | Agregar variables de DB |
