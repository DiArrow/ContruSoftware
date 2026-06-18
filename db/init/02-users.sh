#!/bin/bash
set -e

# ============================================================
# 02-users.sh — Usuario de aplicación con permisos limitados
# Password passed via POSTGRES_APP_PASSWORD environment variable
# Executed by postgres docker entrypoint (supports .sh files)
# ============================================================

psql -v ON_ERROR_STOP=1 \
    -U "${POSTGRES_USER:-postgres}" \
    -d "${POSTGRES_DB:-postgres}" <<EOSQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${POSTGRES_APP_USER:-app_user}') THEN
    CREATE ROLE "${POSTGRES_APP_USER:-app_user}" WITH LOGIN PASSWORD '${POSTGRES_APP_PASSWORD}';
  END IF;
END
\$\$;
GRANT CONNECT ON DATABASE "${POSTGRES_DB:-postgres}" TO "${POSTGRES_APP_USER:-app_user}";
GRANT USAGE ON SCHEMA public TO "${POSTGRES_APP_USER:-app_user}";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "${POSTGRES_APP_USER:-app_user}";
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "${POSTGRES_APP_USER:-app_user}";
EOSQL