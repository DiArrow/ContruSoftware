"""Database configuration read from environment variables.

Constructs ``SQLALCHEMY_DATABASE_URL`` from ``POSTGRES_*`` env vars.
Missing required variables raise ``ValueError`` at import time.
"""

import os

REQUIRED_VARS = [
    "POSTGRES_HOST",
    "POSTGRES_APP_USER",
    "POSTGRES_APP_PASSWORD",
    "POSTGRES_DB",
]


def _build_database_url() -> str:
    """Build a ``postgresql+psycopg2://`` URL from environment variables.

    Raises:
        ValueError: If any required environment variable is missing or empty.
    """
    missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing required environment variable: {missing[0]}")

    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_APP_USER")
    password = os.getenv("POSTGRES_APP_PASSWORD")
    db = os.getenv("POSTGRES_DB")

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


SQLALCHEMY_DATABASE_URL = _build_database_url()

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Credenciales de base de datos específicas por rol.
#
# Si las variables ``POSTGRES_USER_<ROL>`` y ``POSTGRES_PASSWORD_<ROL>`` están
# definidas, el rol obtiene su propio engine SQLAlchemy. Si no, el sistema
# hace fallback al engine genérico (``POSTGRES_APP_USER`` + ``POSTGRES_DB``)
# al usar ``get_role_db`` en los routers.
#
# Los roles definidos en el sistema son:
ROLES = ["SOL", "EST", "AYU", "PRO", "ADM"]

# Mapeo de rol -> URL de base de datos específica. Se puebla automáticamente
# a partir de las variables de entorno. Roles sin URL definida hacen fallback.
ROL_DATABASE_URLS: dict[str, str] = {}

for _rol in ROLES:
    _user = os.getenv(f"POSTGRES_USER_{_rol}")
    _password = os.getenv(f"POSTGRES_PASSWORD_{_rol}")
    if _user and _password:
        _host = os.getenv("POSTGRES_HOST", "localhost")
        _port = os.getenv("POSTGRES_PORT", "5432")
        _db = os.getenv("POSTGRES_DB", "postgres")
        ROL_DATABASE_URLS[_rol] = (
            f"postgresql+psycopg2://{_user}:{_password}@{_host}:{_port}/{_db}"
        )
