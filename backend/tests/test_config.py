"""Tests for backend/src/config.py.

Validates environment-driven database configuration.
"""

import os
import sys
from unittest.mock import patch

import pytest


def _reload_config():
    """Remove cached config module so the next import is fresh."""
    sys.modules.pop("config", None)


def test_missing_required_env_var_raises_valueerror():
    """Missing POSTGRES_APP_PASSWORD must raise ValueError with variable name."""
    env = {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_APP_USER": "user",
        "POSTGRES_DB": "db",
    }
    _reload_config()
    with patch.dict(os.environ, env, clear=True):
        with pytest.raises(ValueError, match="POSTGRES_APP_PASSWORD"):
            import config  # noqa: F401


def test_valid_env_vars_produce_connection_url():
    """All required vars set must yield a postgresql+psycopg2 URL."""
    env = {
        "POSTGRES_HOST": "db.example.com",
        "POSTGRES_PORT": "5433",
        "POSTGRES_APP_USER": "admin",
        "POSTGRES_APP_PASSWORD": "secret",
        "POSTGRES_DB": "mydb",
    }
    _reload_config()
    with patch.dict(os.environ, env, clear=True):
        import config

        assert config.SQLALCHEMY_DATABASE_URL == "postgresql+psycopg2://admin:secret@db.example.com:5433/mydb"


def test_default_port_when_postgres_port_not_set():
    """POSTGRES_PORT defaults to 5432 when omitted."""
    env = {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_APP_USER": "user",
        "POSTGRES_APP_PASSWORD": "pass",
        "POSTGRES_DB": "db",
    }
    _reload_config()
    with patch.dict(os.environ, env, clear=True):
        import config

        assert config.SQLALCHEMY_DATABASE_URL == "postgresql+psycopg2://user:pass@localhost:5432/db"
