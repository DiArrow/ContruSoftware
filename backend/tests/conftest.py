"""Pytest fixtures para el conjunto de pruebas.

Usa la base de datos de negocio con un patrón de transacción+rollback
para asegurar aislamiento entre tests sin requerir una base de datos
de prueba separada.
"""

import os
from collections.abc import Generator
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# Carga variables de entorno ANTES de cualquier import que dispare config.py
_project_root = Path(__file__).resolve().parents[2]
_env_path = _project_root / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

from unittest.mock import MagicMock  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from auth.dependencies import get_role_db  # noqa: E402
from auth.roles import ADMIN, AYUDANTE, ESTUDIANTE  # noqa: E402
from database import get_db  # noqa: E402
from main import app  # noqa: E402


def _get_database_url() -> str:
    """Resuelve la URL de la base de datos desde variables de entorno.

    Usa ``DATABASE_URL`` si está presente; de lo contrario construye la URL
    desde variables individuales ``POSTGRES_*`` con valores por defecto razonables.
    """
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "makerbox")
    user = os.getenv("POSTGRES_APP_USER", os.getenv("POSTGRES_USER", "backend"))
    password = os.getenv("POSTGRES_APP_PASSWORD") or os.getenv("POSTGRES_PASSWORD")

    if not password:
        msg = (
            "Database password not found. Set POSTGRES_APP_PASSWORD, "
            "POSTGRES_PASSWORD, or DATABASE_URL."
        )
        raise ValueError(msg)

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


@pytest.fixture(scope="session")
def test_engine() -> Generator:
    """Crea un único engine de SQLAlchemy para toda la sesión de pruebas.

    El engine se dispone después de que todos los tests terminen.
    """
    database_url = _get_database_url()
    engine = create_engine(database_url, pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """Proporciona una sesión de base de datos que hace rollback tras cada test.

    Usa una transacción outer más SAVEPOINTs para que cualquier
    ``session.commit()`` dentro del código bajo test cree SAVEPOINTs
    en lugar de COMMITs reales. El rollback de la transacción outer en
    el teardown deshace todo, incluidos los SAVEPOINTs, manteniendo la
    base de datos limpia entre tests sin requerir una base de datos
    de testing separada.

    El argumento ``join_transaction_mode="create_savepoint"`` le indica
    a la Session que se enlist en la transacción outer mediante un
    SAVEPOINT, de modo que ``session.commit()`` libera el SAVEPOINT en
    lugar de confirmar la transacción outer.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Retorna un TestClient de FastAPI con las dependencias de BD reemplazadas.

    Sobreescribe tanto ``get_db`` como ``get_role_db`` para que todos los
    endpoints usen la sesión de prueba aislada por transacción.
    """
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_role_db] = lambda: db_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_role_db, None)


@pytest.fixture(scope="function")
def client_unit() -> Generator[TestClient, None, None]:
    """Retorna un TestClient de FastAPI que NO requiere una base de datos real.

    Sobreescribe ``get_db`` y ``get_role_db`` con una sesión mock para que
    los tests de autorización (401, 403) puedan ejecutarse sin PostgreSQL.
    """
    app.dependency_overrides[get_db] = lambda: MagicMock(spec=Session)
    app.dependency_overrides[get_role_db] = lambda: MagicMock(spec=Session)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_role_db, None)


def _create_token_with_role(role: str) -> str:
    """Crea un token JWT válido con el rol especificado.

    Args:
        role: El rol a incluir en el token (e.g., ``ADMIN``, ``ESTUDIANTE``).

    Returns:
        Una cadena de token JWT válida.
    """
    from auth.jwt_handler import crear_token_jwt

    data = {"sub": "test_user@test.com", "role": role}
    expires_delta = timedelta(hours=24)
    return crear_token_jwt(data, expires_delta)


@pytest.fixture
def admin_headers() -> dict:
    """Retorna headers con un token de administrador válido."""
    token = _create_token_with_role(ADMIN)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def estudiante_headers() -> dict:
    """Retorna headers con un token de estudiante válido."""
    token = _create_token_with_role(ESTUDIANTE)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def ayu_headers() -> dict:
    """Retorna headers con un token de ayudante válido."""
    token = _create_token_with_role(AYUDANTE)
    return {"Authorization": f"Bearer {token}"}
