#!/bin/bash
set -e

# ============================================================
# 02-role-users.sh — Usuarios PostgreSQL por rol con permisos diferenciados
# Variables de entorno provienen de docker-compose.yml
# ============================================================

psql -v ON_ERROR_STOP=1 \
    --username "$POSTGRES_USER" \
    --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${POSTGRES_USER_SOL:-sol_user}') THEN
            CREATE ROLE ${POSTGRES_USER_SOL:-sol_user} WITH LOGIN PASSWORD '${POSTGRES_PASSWORD_SOL}';
        END IF;
    END
    \$\$;
    GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER_SOL:-sol_user};
    GRANT USAGE ON SCHEMA public TO ${POSTGRES_USER_SOL:-sol_user};
    GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO ${POSTGRES_USER_SOL:-sol_user};
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT ON TABLES TO ${POSTGRES_USER_SOL:-sol_user};

    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${POSTGRES_USER_EST:-est_user}') THEN
            CREATE ROLE ${POSTGRES_USER_EST:-est_user} WITH LOGIN PASSWORD '${POSTGRES_PASSWORD_EST}';
        END IF;
    END
    \$\$;
    GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER_EST:-est_user};
    GRANT USAGE ON SCHEMA public TO ${POSTGRES_USER_EST:-est_user};
    GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO ${POSTGRES_USER_EST:-est_user};
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT ON TABLES TO ${POSTGRES_USER_EST:-est_user};

    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${POSTGRES_USER_AYU:-ayu_user}') THEN
            CREATE ROLE ${POSTGRES_USER_AYU:-ayu_user} WITH LOGIN PASSWORD '${POSTGRES_PASSWORD_AYU}';
        END IF;
    END
    \$\$;
    GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER_AYU:-ayu_user};
    GRANT USAGE ON SCHEMA public TO ${POSTGRES_USER_AYU:-ayu_user};
    GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO ${POSTGRES_USER_AYU:-ayu_user};
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT ON TABLES TO ${POSTGRES_USER_AYU:-ayu_user};

    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${POSTGRES_USER_PRO:-pro_user}') THEN
            CREATE ROLE ${POSTGRES_USER_PRO:-pro_user} WITH LOGIN PASSWORD '${POSTGRES_PASSWORD_PRO}';
        END IF;
    END
    \$\$;
    GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER_PRO:-pro_user};
    GRANT USAGE ON SCHEMA public TO ${POSTGRES_USER_PRO:-pro_user};
    GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO ${POSTGRES_USER_PRO:-pro_user};
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO ${POSTGRES_USER_PRO:-pro_user};

    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${POSTGRES_USER_ADM:-adm_user}') THEN
            CREATE ROLE ${POSTGRES_USER_ADM:-adm_user} WITH LOGIN PASSWORD '${POSTGRES_PASSWORD_ADM}';
        END IF;
    END
    \$\$;
    GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER_ADM:-adm_user};
    GRANT USAGE ON SCHEMA public TO ${POSTGRES_USER_ADM:-adm_user};
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${POSTGRES_USER_ADM:-adm_user};
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${POSTGRES_USER_ADM:-adm_user};
EOSQL
