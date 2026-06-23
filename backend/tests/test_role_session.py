"""Tests para get_role_session y motores multi-rol.

Verifica que cada rol obtenga su propio engine con pool_size=1.
"""

import importlib
import os
import sys
from unittest.mock import patch

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


def test_get_role_session_invalid_role_falls_back_to_sessionlocal():
    """Un rol sin URL configurada debe hacer fallback al engine genérico."""
    env = {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "testdb",
        "POSTGRES_USER_SOL": "sol_user",
        "POSTGRES_PASSWORD_SOL": "sol_pass",
    }
    with patch.dict(os.environ, env, clear=False):
        db_mod = _reload_database()
        gen = db_mod.get_role_session("INVALID")
        session = next(gen)
        assert isinstance(session, Session)
        gen.close()


def test_get_role_session_emits_warning_on_fallback():
    """Cuando un rol no tiene URL configurada, se emite un UserWarning."""
    import warnings as warnings_mod

    env = {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "testdb",
        "POSTGRES_USER_SOL": "sol_user",
        "POSTGRES_PASSWORD_SOL": "sol_pass",
    }
    with patch.dict(os.environ, env, clear=False):
        db_mod = _reload_database()
        with warnings_mod.catch_warnings(record=True) as caught:
            warnings_mod.simplefilter("always")
            gen = db_mod.get_role_session("SOL_NO_CONFIGURADO")
            next(gen)
            gen.close()
        role_warnings = [
            w for w in caught if "sin URL configurada" in str(w.message)
        ]
        assert len(role_warnings) == 1


def test_different_roles_get_different_engines():
    """Cada rol configurado obtiene su propio engine (aislamiento)."""
    env = {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "testdb",
        "POSTGRES_USER_SOL": "sol_user",
        "POSTGRES_PASSWORD_SOL": "sol_pass",
        "POSTGRES_USER_EST": "est_user",
        "POSTGRES_PASSWORD_EST": "est_pass",
    }
    with patch.dict(os.environ, env, clear=False):
        db_mod = _reload_database()
        # Forzar creación de ambos engines
        gen1 = db_mod.get_role_session("SOL")
        next(gen1)
        gen1.close()
        gen2 = db_mod.get_role_session("EST")
        next(gen2)
        gen2.close()

        assert "SOL" in db_mod._role_engines
        assert "EST" in db_mod._role_engines
        assert (
            db_mod._role_engines["SOL"]
            is not db_mod._role_engines["EST"]
        )


def test_get_role_db_dependency_reads_role_from_jwt():
    """La dependencia ``get_role_db`` lee el rol del JWT y produce una Session.

    No reimplementa la lógica multi-rol — delega a ``get_role_session``. El
    comportamiento multi-rol está cubierto por los otros tests de este archivo;
    este test solo verifica que la dependencia es invocable con un payload
    de JWT y devuelve una ``Session``.
    """
    from auth.dependencies import get_role_db

    # Caso 1: payload con rol definido
    gen = get_role_db(current_user={"role": "SOL", "sub": "user1"})
    session = next(gen)
    assert isinstance(session, Session)
    gen.close()

    # Caso 2: payload con rol desconocido — fallback también produce Session
    import warnings as warnings_mod

    with warnings_mod.catch_warnings():
        warnings_mod.simplefilter("ignore")
        gen = get_role_db(current_user={"role": "DESCONOCIDO", "sub": "user2"})
        session = next(gen)
        assert isinstance(session, Session)
        gen.close()
