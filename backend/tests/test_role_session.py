"""Tests para get_role_session y motores multi-rol.

Verifica que cada rol obtenga su propio engine con pool_size=1.
"""

import importlib
import os
import sys
from unittest.mock import patch

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session


def _reload_database():
    """Elimina módulos cacheados para forzar reimportación fresca."""
    sys.modules.pop("src.database", None)
    sys.modules.pop("database", None)
    sys.modules.pop("src.config", None)
    sys.modules.pop("config", None)
    return importlib.import_module("src.database")


def test_get_role_session_returns_session_for_valid_role():
    """SOL con credenciales configuradas debe devolver una Session."""
    env = {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "testdb",
        "POSTGRES_USER_SOL": "sol_user",
        "POSTGRES_PASSWORD_SOL": "sol_pass",
    }
    with patch.dict(os.environ, env, clear=False):
        db_mod = _reload_database()
        gen = db_mod.get_role_session("SOL")
        session = next(gen)
        assert isinstance(session, Session)
        gen.close()


def test_get_role_session_uses_correct_engine():
    """El engine para SOL debe tener pool_size=1 y max_overflow=1."""
    env = {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "testdb",
        "POSTGRES_USER_SOL": "sol_user",
        "POSTGRES_PASSWORD_SOL": "sol_pass",
    }
    with patch.dict(os.environ, env, clear=False):
        db_mod = _reload_database()
        gen = db_mod.get_role_session("SOL")
        next(gen)  # trigger engine creation
        gen.close()
        engine = db_mod._role_engines["SOL"]
        assert isinstance(engine, Engine)
        assert engine.pool.size() == 1
        assert engine.pool._max_overflow == 1


def test_get_role_session_invalid_role_raises_keyerror():
    """Un rol sin URL configurada debe lanzar KeyError."""
    env = {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "testdb",
        "POSTGRES_USER_SOL": "sol_user",
        "POSTGRES_PASSWORD_SOL": "sol_pass",
    }
    with patch.dict(os.environ, env, clear=False):
        db_mod = _reload_database()
        with pytest.raises(KeyError):
            gen = db_mod.get_role_session("INVALID")
            next(gen)
