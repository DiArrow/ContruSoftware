#!/bin/bash
set -e

# ============================================================
# 02-users.sh — Usuario de aplicación con permisos limitados
# Password passed via POSTGRES_APP_PASSWORD environment variable
# Executed by postgres docker entrypoint (supports .sh files)
# ============================================================

psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER:-postgres}" -v app_password="${POSTGRES_APP_PASSWORD}" <<'EOSQL'
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
EOSQL
