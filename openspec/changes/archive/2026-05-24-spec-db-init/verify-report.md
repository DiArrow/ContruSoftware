# Verify Report: spec-db-init

## Status: PASS WITH WARNINGS

## Critical Issues

None. All critical spec requirements are met. No blocks to merge.

## Warnings

- [WARNING] **FK count mismatch**: Spec scenario "All FK constraints defined" expects 15 FK constraints, but implementation has exactly 14. The spec table itself lists 14 FKs (1+1+2+1+1+2+2+2+2=14), and the `ref_impresora` column in `uso_impresora` is documented as having no FK. The scenario assertion of 15 appears to be a spec error, not an implementation defect.
- [WARNING] **Design deviation (improvement)**: Design specified `02-users.sql` + custom `entrypoint.sh`, but implementation uses `02-users.sh` directly (leveraging postgres docker image's native `.sh` support). This eliminates the need for a custom Dockerfile ENTRYPOINT wrapper, simplifying the architecture. Tasks document this as an intentional adaptation.
- [WARNING] **Database target ambiguity**: Init scripts operate on the default `postgres` database, but docker-compose sets `POSTGRES_DB`. If `POSTGRES_DB` differs from `postgres`, the init scripts still run against `postgres` (the default psql database), not the app database. The design lists this as an open question — unresolved.

## Suggestions

- [SUGGESTION] The `01-init.sql` header comment still references `init.sql` (line 1: `-- init.sql — Esquema completo...`). Consider updating to `01-init.sql` for consistency.
- [SUGGESTION] The `db/Dockerfile` comment on line 3 has a typo: `# Copiar modelo de datos al contenedord` — trailing `d`.
- [SUGGESTION] Consider adding `GRANT USAGE ON SEQUENCE` to `02-users.sh` if SERIAL columns are ever added to tables.

## Spec Compliance

### database-schema/spec.md

| Requirement | Status | Notes |
|-------------|--------|-------|
| Complete Table Definitions | PASS | All 14 tables defined with correct columns, types, PKs. `usuario`(7), `semestre`(7), `estudiante`(5), `articulo`(6), `bloque_horario`(5), `curso`(6), `grupo_estudiante`(2), `impresion`(6), `movimiento_stock`(5), `ayudantia`(6), `inscripcion_ayudantia`(4), `uso_impresora`(5), `reserva`(5), `bloque_reservado`(2) |
| Dependency Ordering | PASS | 5 base tables first (no FK), then 4 single-dependency, then 5 multi-dependency. All FKs reference previously-created tables. |
| Idempotent Execution | PASS | `DROP TABLE IF EXISTS ... CASCADE` + `CREATE TABLE` pattern. Reverse drop order confirmed. |
| SQLFluff Compliance | PASS | `sqlfluff lint db/init/01-init.sql --dialect postgres` exits 0. Keywords UPPERCASE, identifiers lowercase. |
| Foreign Key Integrity | PASS (partial) | 14 named FK constraints defined. Spec scenario expects 15 — see WARNING above. All FKs use named constraints. `ref_impresora` gap documented per spec. |

### database-access/spec.md

| Requirement | Status | Notes |
|-------------|--------|-------|
| Application User Creation | PASS | `app_user` role created with LOGIN via idempotent `DO $$` block with `IF NOT EXISTS` check on `pg_roles`. |
| Permission Model | PASS | `GRANT CONNECT`, `GRANT USAGE`, `GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES`. No DROP/ALTER/CREATE/TRUNCATE granted. |
| Credential Management | PASS | No hardcoded passwords. `POSTGRES_APP_PASSWORD` env var passed via `psql -v` flag. SQL uses `:'app_password'` psql variable syntax. Heredoc is single-quoted (`<<'EOSQL'`) preventing shell expansion inside SQL. |
| Default Privileges | PASS | `ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user` present. |

## Tasks Completion

- [x] Phase 1: Script Renaming — `01-init.sql` and `02-users.sh` present, correctly named
- [x] Phase 2: Fix users.sql — Idempotent DO block, GRANTs, ALTER DEFAULT PRIVILEGES all present
- [x] Phase 3: Create entrypoint — Adapted to native `.sh` support (simpler than design)
- [x] Phase 4: Update Dockerfile — Skipped (correctly, no custom entrypoint needed)
- [x] Phase 5: Update docker-compose — `POSTGRES_APP_PASSWORD` present at line 24
- [x] Phase 6: SQLFluff fix — Passes clean (exit code 0)
- [ ] Phase 7: Runtime verification — Requires Docker, cannot execute in this environment. Tasks 7.1-7.4 pending. Tasks 7.5-7.6 verified statically.

## Static Verification Evidence

| Check | Command | Result |
|-------|---------|--------|
| SQLFluff lint | `sqlfluff lint db/init/01-init.sql --dialect postgres` | All Finished! (exit 0) |
| Hardcoded passwords | `grep -ri "password" db/init/` | Only variable references found (comment + `:'app_password'` + env var) |
| POSTGRES_APP_PASSWORD | `grep "POSTGRES_APP_PASSWORD" docker-compose.yml` | Present at line 24 |
| Shell syntax in SQL | `grep -rP '\$\{...\}' db/init/01-init.sql` | No matches (exit 1) |
| File permissions | `stat -c '%a' db/init/02-users.sh` | 755 (executable) |
| Table count | `grep -c 'CREATE TABLE' db/init/01-init.sql` (excluding comments) | 14 tables |
| FK count | `grep -c 'FOREIGN KEY' db/init/01-init.sql` | 14 named constraints |

## Recommendation

**Ready to merge** pending runtime verification (Phase 7 tasks 7.1-7.4). All static checks pass. The FK count discrepancy (14 vs 15 in spec) is a spec error, not an implementation defect. The `.sh` adaptation is an improvement over the design.
