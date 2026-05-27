#!/usr/bin/env bash
# ============================================================
# Migración: agrega columna password_hash a la tabla usuario
# Uso de variables de entorno para credenciales de BD
# ============================================================

set -euo pipefail

: "${DB_HOST:?Variable DB_HOST no definida}"
: "${DB_PORT:?Variable DB_PORT no definida}"
: "${DB_NAME:?Variable DB_NAME no definida}"
: "${DB_USER:?Variable DB_USER no definida}"
: "${DB_PASSWORD:?Variable DB_PASSWORD no definida}"

export PGPASSWORD="${DB_PASSWORD}"

psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -d "${DB_NAME}" \
    -U "${DB_USER}" \
    -v ON_ERROR_STOP=1 \
    -c "ALTER TABLE usuario ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) NOT NULL DEFAULT '';"

echo "Migración 02-add-password-hash completada con éxito."
