# Spec: Inicialización del Esquema de Datos en PostgreSQL

**Issue**: #2  
**Label**: Infraestructura  
**Dependencias**: Ninguna (primera en la cadena)

## Contexto

El archivo `db/init/init.sql` existe pero está vacío. El modelo de datos ya está definido en `Specs/Modelo de datos.md` con 13 tablas. Se necesita materializar ese modelo en SQL ejecutable que cumpla con SQLFluff.

## Requisitos

### R1 — Archivo `init.sql`

- [ ] Contener el DDL completo de las 13 tablas del modelo de datos
- [ ] Las tablas deben crearse en orden de dependencias (tablas sin FK primero)
- [ ] Primary keys con `VARCHAR(36)` (UUID)
- [ ] Foreign keys correctamente referenciadas
- [ ] Cumplir estilo SQLFluff: keywords en MAYÚSCULAS, identificadores en minúsculas

### R2 — Archivo `users.sql`

- [ ] Crear un rol de usuario para la aplicación con permisos limitados
- [ ] El usuario debe tener acceso solo a las tablas del esquema público
- [ ] Las credenciales deben referenciar variables de entorno, NO hardcodearse

### R3 — Verificación

- [ ] Las tablas existen tras ejecutar `docker compose up db`
- [ ] `\dt` muestra las 13 tablas
- [ ] `SELECT column_name FROM information_schema.columns WHERE table_name = '...'` muestra los atributos correctos

## Escenarios

### Escenario 1: Orden de creación de tablas

**Dado** que las tablas tienen dependencias por foreign keys  
**Cuando** se ejecuta `init.sql`  
**Entonces** las tablas sin dependencias se crean primero:
1. `usuario`
2. `semestre`
3. `estudiante`
4. `articulo`
5. `bloque_horario`
6. `curso` (depende de `semestre`)
7. `grupo_estudiante` (depende de `estudiante`)
8. `ayudantia` (depende de `curso`, `grupo_estudiante`, `usuario`)
9. `inscripcion_ayudantia` (depende de `ayudantia`, `estudiante`)
10. `impresion` (depende de `usuario`, `articulo`)
11. `uso_impresora` (depende de `estudiante`, `ayudantia`)
12. `reserva` (depende de `usuario`, `ayudantia`)
13. `bloque_reservado` (depende de `bloque_horario`, `reserva`)
14. `movimiento_stock` (depende de `articulo`)

### Escenario 2: Ejecución idempotente

**Dado** que el contenedor de DB se reinicia  
**Cuando** se monta `init.sql` como init script  
**Entonces** las tablas se crean solo si no existen (`CREATE TABLE IF NOT EXISTS` o `DROP TABLE IF EXISTS` + `CREATE TABLE`)

### Escenario 3: Usuario de aplicación

**Dado** que la aplicación necesita conectarse a la DB  
**Cuando** se ejecuta `users.sql`  
**Entonces** se crea un usuario con:
- Permisos `SELECT, INSERT, UPDATE, DELETE` en todas las tablas
- Sin permisos de `DROP` o `ALTER`
- Contraseña definida vía variable de entorno `${POSTGRES_APP_PASSWORD}`

## Criterios de Aceptación

- [ ] `db/init/init.sql` contiene DDL de las 13 tablas en orden correcto
- [ ] `db/init/users.sql` crea el usuario de aplicación
- [ ] `sqlfluff lint db/init/init.sql --dialect postgres` pasa sin errores
- [ ] `docker compose up db` crea las tablas exitosamente
- [ ] `\dt` muestra las 13 tablas
- [ ] No hay credenciales hardcodeadas en ningún archivo SQL

## Archivos Afectados

| Archivo | Acción |
|---------|--------|
| `db/init/init.sql` | Escribir DDL completo |
| `db/init/users.sql` | Crear nuevo |
| `db/.sqlfluff` | Verificar configuración existente |
