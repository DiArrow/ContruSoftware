# Archive Report: spec-db-init

## Status: COMPLETE

## Summary
Initialized PostgreSQL 14.22 database with 14-table DDL schema via Docker entrypoint init scripts and created `app_user` role with limited CRUD permissions. Fixed critical environment variable expansion bug in users.sql (shell syntax `${VAR}` does not expand in psql), implemented idempotent user creation via `DO $$` block, and added `POSTGRES_APP_PASSWORD` to docker-compose. Implementation simplified design by using native `.sh` support in postgres docker image instead of custom entrypoint wrapper.

## Artifacts Preserved
- proposal.md (Engram observation #92)
- specs/database-schema/spec.md → merged to openspec/specs/database-schema/spec.md
- specs/database-access/spec.md → merged to openspec/specs/database-access/spec.md
- design.md
- tasks.md
- verify-report.md

## Implementation Files
- db/init/01-init.sql (renamed from init.sql)
- db/init/02-users.sh (new, replaced users.sql with bash script embedding SQL)
- docker-compose.yml (added POSTGRES_APP_PASSWORD)

## Known Issues / Warnings
- FK count spec error: scenario says 15 but implementation has 14 (spec bug — table itself lists 14 FKs)
- Runtime verification deferred: Phase 7 tasks 7.1-7.4 require `docker compose up` (container start, table count, role verification, idempotency test)
- POSTGRES_DB ambiguity: init scripts target default `postgres` database regardless of `POSTGRES_DB` env var setting

## Commits
- e5115f1 feat: agregar spec-db-init y registro de skills
- 605d6a0 feat: renombrar scripts de init y corregir bug de variable de entorno
- 49d72a4 feat: agregar POSTGRES_APP_PASSWORD a docker-compose
- fac7a27 docs: actualizar tasks.md con tareas completadas de spec-db-init
