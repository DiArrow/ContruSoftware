# Tasks: spec-db-init — PostgreSQL Schema Initialization

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~120 (additions + deletions) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy: pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Complete DB initialization (scripts + Docker + compose) | Single PR | All tasks are tightly coupled; no independent slice |

## Phase 1: Script Renaming and Ordering

- [x] 1.1 Rename `db/init/init.sql` → `db/init/01-init.sql`
- [x] 1.2 Rename `db/init/users.sql` → `db/init/02-users.sh` (simpler approach: .sh with embedded SQL instead of .sql + entrypoint.sh)
- Verify: `ls db/init/` shows `01-init.sql` and `02-users.sh` ✅

## Phase 2: Fix users.sql — Env Var Bug and Idempotency

- [x] 2.1 Replace `CREATE ROLE` with idempotent `DO $$` block using `psql :'app_password'` syntax (embedded in 02-users.sh)
- [x] 2.2 Add `GRANT CONNECT`, `GRANT USAGE`, and `GRANT SELECT/INSERT/UPDATE/DELETE` statements
- [x] 2.3 Add `ALTER DEFAULT PRIVILEGES` for future table permissions
- Verify: `02-users.sh` contains no `${...}` shell syntax in SQL, uses `:'app_password'` psql variable syntax, and includes `IF NOT EXISTS` guard ✅

## Phase 3: Create entrypoint.sh Wrapper

- [x] 3.1 **Adapted**: Created `db/init/02-users.sh` with bash script that passes `POSTGRES_APP_PASSWORD` to psql via `-v` flag. The postgres docker image natively executes `.sh` files in `/docker-entrypoint-initdb.d/`, making a custom entrypoint unnecessary.
- [x] 3.2 Made `02-users.sh` executable (`chmod +x`)
- Verify: `db/init/02-users.sh` passes manual review for correctness ✅

## Phase 4: Update db/Dockerfile

- [x] 4.1 **Skipped**: No Dockerfile changes needed — the default postgres entrypoint handles `.sh` files natively
- [x] 4.2 **Skipped**: No custom ENTRYPOINT required
- Verify: `db/Dockerfile` unchanged, default entrypoint handles init scripts ✅

## Phase 5: Update docker-compose.yml

- [x] 5.1 Add `POSTGRES_APP_PASSWORD: ${POSTGRES_APP_PASSWORD}` to `db` service `environment` block
- Verify: `docker compose config` shows `POSTGRES_APP_PASSWORD` in db environment ✅

## Phase 6: Fix SQLFluff Keyword Capitalization in 01-init.sql

- [x] 6.1 Run `sqlfluff lint db/init/01-init.sql --dialect postgres` — file already uses UPPERCASE keywords
- [x] 6.2 No changes needed — keywords already compliant
- [x] 6.3 `sqlfluff lint` passes with exit code 0
- Verify: `sqlfluff lint` passes with no violations ✅

## Phase 7: Verification

- [ ] 7.1 Run `docker compose down -v && docker compose up -d db` — container starts without errors
- [ ] 7.2 Verify 14 tables exist: `docker compose exec db psql -U postgres -d postgres -c "\dt"` returns 14 rows
- [ ] 7.3 Verify `app_user` role exists: `docker compose exec db psql -U postgres -d postgres -c "\du app_user"` shows LOGIN role
- [ ] 7.4 Verify idempotency: run `docker compose down -v && docker compose up -d db` a second time — no duplicate role error
- [x] 7.5 Verify no hardcoded passwords: `grep -ri "password" db/init/` shows only variable references, no literals
- [x] 7.6 Verify SQLFluff: `sqlfluff lint db/init/01-init.sql db/init/02-users.sh --dialect postgres` exits 0
