#!/usr/bin/env bash
# ============================================================
# Seed: inserta usuario administrador con contraseña bcrypt
# Uso de variables de entorno para credenciales de BD
# ============================================================

set -euo pipefail

: "${DB_HOST:?Variable DB_HOST no definida}"
: "${DB_PORT:?Variable DB_PORT no definida}"
: "${DB_NAME:?Variable DB_NAME no definida}"
: "${DB_USER:?Variable DB_USER no definida}"
: "${DB_PASSWORD:?Variable DB_PASSWORD no definida}"

ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123}"

# Generar hash bcrypt usando Python (psql no soporta bcrypt nativamente)
HASHED_PASSWORD=$(python3 -c "
from passlib.context import CryptContext
ctx = CryptContext(schemes=['bcrypt'], deprecated='auto')
print(ctx.hash('${ADMIN_PASSWORD}'))
")

export PGPASSWORD="${DB_PASSWORD}"

# Verificar si el usuario admin ya existe
EXISTS=$(psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -d "${DB_NAME}" \
    -U "${DB_USER}" \
    -tA \
    -c "SELECT 1 FROM usuario WHERE correo = 'admin@makerbox.cl' LIMIT 1;")

if [ "${EXISTS}" = "1" ]; then
    echo "Usuario admin@makerbox.cl ya existe. Saltando seed."
    exit 0
fi

psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -d "${DB_NAME}" \
    -U "${DB_USER}" \
    -v ON_ERROR_STOP=1 \
    -c "
INSERT INTO usuario (
    id_usuario, nombre, apellido, correo, email, rol, estado, password_hash
) VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'Admin',
    'MakerBox',
    'admin@makerbox.cl',
    'admin@makerbox.cl',
    'ADM',
    true,
    '${HASHED_PASSWORD}'
);
"

echo "Seed 02-admin-user completado con éxito."
