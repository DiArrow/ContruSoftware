# Design: spec-db-init — PostgreSQL Schema Initialization

## Technical Approach

Initialize a PostgreSQL 14.22 database with 14 tables via Docker entrypoint init scripts, then create an `app_user` role with limited CRUD permissions. The existing `init.sql` DDL is structurally correct (14 tables, proper dependency order, DROP CASCADE + CREATE idempotency). The primary work is fixing the `users.sql` environment variable expansion bug, adding the missing `POSTGRES_APP_PASSWORD` to docker-compose, and ensuring idempotent user creation.

## Architecture Decisions

### Decision: PostgreSQL Entrypoint Script Ordering

**Choice**: Rename init scripts with numeric prefixes (`01-init.sql`, `02-users.sql`) to guarantee execution order.

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Alphabetical (current: init.sql, users.sql) | Works by coincidence, fragile to new files | Rejected |
| Numeric prefixes (`01-`, `02-`) | Explicit ordering, scales to future scripts | **Selected** |
| Single combined file | Simpler but mixes DDL and DCL concerns | Rejected |

**Rationale**: PostgreSQL's `docker-entrypoint-initdb.d/` executes `.sql` files in lexicographic order. Numeric prefixes make ordering explicit and survive future additions (migrations, seed data).

### Decision: Environment Variable Substitution for Password

**Choice**: Custom Dockerfile ENTRYPOINT wrapper that passes `POSTGRES_APP_PASSWORD` to psql via `-v` flag, combined with psql `:'var'` syntax in users.sql.

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Shell syntax `${VAR}` in SQL | Does NOT expand in psql — current bug | Rejected |
| psql `\set` + `:var` | Requires passing via `-v` flag | **Selected** |
| `envsubst` preprocessing | Adds build dependency, fragile | Rejected |
| Hardcoded password | Security violation per spec | Rejected |

**Rationale**: psql does NOT expand shell environment variables. The `psql -v var=value` mechanism combined with `:'var'` (quoted substitution) is the native PostgreSQL approach. The ENTRYPOINT wrapper is minimal (~5 lines) and only affects the init phase.

### Decision: Idempotent User Creation

**Choice**: `DO` block with `pg_roles` check for `CREATE ROLE`, since PostgreSQL has no `CREATE ROLE IF NOT EXISTS`.

**Rationale**: The spec requires graceful re-execution. A PL/pgSQL anonymous block checking `SELECT FROM pg_roles WHERE rolname = 'app_user'` is the standard pattern.

### Decision: init.sql DDL — No Changes Required

**Choice**: Keep existing `init.sql` as-is (189 lines, 14 tables, correct order).

**Rationale**: The DDL already implements the spec correctly — DROP CASCADE + CREATE pattern, proper dependency ordering, named constraints. Only SQLFluff keyword capitalization may need adjustment (existing file uses lowercase keywords, sqlfluff config requires uppercase).

## Data Flow

```
docker compose up db
  │
  ├─→ PostgreSQL container starts
  │     │
  │     ├─→ First init? ──Yes──→ Execute /docker-entrypoint-initdb.d/*.sql
  │     │                        │
  │     │                        ├─→ 01-init.sql (DDL: 14 tables)
  │     │                        │     DROP IF EXISTS CASCADE
  │     │                        │     CREATE TABLE (dependency order)
  │     │                        │
  │     │                        └─→ 02-users.sql (DCL: app_user)
  │     │                              DO block (idempotent)
  │     │                              GRANT CRUD permissions
  │     │
  │     └─→ Subsequent starts ──→ Skip init scripts (data volume exists)
  │
  └─→ Database ready on port 5432
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `db/init/init.sql` → `db/init/01-init.sql` | Rename | Add numeric prefix for ordering |
| `db/init/users.sql` → `db/init/02-users.sql` | Rename + Modify | Fix env var syntax, add idempotent DO block |
| `db/Dockerfile` | Modify | Add custom ENTRYPOINT wrapper for psql `-v` flag |
| `db/init/entrypoint.sh` | Create | Shell script that passes POSTGRES_APP_PASSWORD to psql |
| `docker-compose.yml` | Modify | Add `POSTGRES_APP_PASSWORD` to db service environment |
| `db/.sqlfluff` | No change | Existing config is correct |

## Interfaces / Contracts

### Fixed users.sql (02-users.sql)

```sql
-- ============================================================
-- 02-users.sql — Usuario de aplicación con permisos limitados
-- Password passed via psql -v app_password='value'
-- ============================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_user') THEN
        CREATE ROLE app_user WITH LOGIN PASSWORD :'app_password';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE postgres TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
```

### entrypoint.sh

```sh
#!/bin/bash
set -e

# Run default postgres docker entrypoint
docker-entrypoint.sh postgres &
PG_PID=$!

# Wait for PostgreSQL to be ready
until pg_isready -U "${POSTGRES_USER:-postgres}" 2>/dev/null; do
    sleep 1
done

# Execute init scripts with variable substitution
for f in /docker-entrypoint-initdb.d/*.sql; do
    psql -v ON_ERROR_STOP=1 \
         -U "${POSTGRES_USER:-postgres}" \
         -v app_password="${POSTGRES_APP_PASSWORD}" \
         -f "$f"
done

wait $PG_PID
```

### docker-compose.yml (db service addition)

```yaml
  db:
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_APP_PASSWORD: ${POSTGRES_APP_PASSWORD}  # NEW
```

### .env (new or updated)

```
POSTGRES_APP_PASSWORD=<secure-password>
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Container | All 14 tables created | `docker compose up db` then `\dt` returns 14 rows |
| Container | Table dependency order | Verify no "relation does not exist" errors in logs |
| Container | Idempotent init | Run `docker compose down -v && docker compose up db` twice |
| Container | app_user exists | `\du app_user` shows role with LOGIN |
| Container | CRUD permissions | Connect as app_user, run SELECT/INSERT/UPDATE/DELETE |
| Container | DDL denied | Connect as app_user, run DROP TABLE — expect permission denied |
| Lint | SQLFluff passes | `sqlfluff lint db/init/01-init.sql --dialect postgres` exit 0 |
| Security | No hardcoded passwords | `grep -r "password" db/init/*.sql` — no literals |
| Security | Env var required | Unset POSTGRES_APP_PASSWORD, verify container fails |

## Migration / Rollout

No migration required. This is a greenfield initialization. Existing data volumes should be destroyed (`docker compose down -v`) before first run to ensure clean init.

## Open Questions

- [ ] Should `postgres` database be the target, or should a dedicated app database be created via `POSTGRES_DB`? (Current docker-compose sets `POSTGRES_DB` but init scripts connect to default `postgres`)
- [ ] SQLFluff keyword capitalization: existing `init.sql` uses lowercase keywords (`create table`, `constraint`) while `.sqlfluff` config requires uppercase. Needs fix during apply phase.
