-- ============================================================
-- users.sql — Usuario de aplicación con permisos limitados
-- Credenciales vía variable de entorno, nunca hardcodeadas
-- ============================================================

CREATE ROLE app_user WITH LOGIN PASSWORD '${POSTGRES_APP_PASSWORD}';

GRANT CONNECT ON DATABASE postgres TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
