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
