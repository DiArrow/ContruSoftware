"""Pytest fixtures for the test suite.

Uses the business database with a transaction+rollback pattern
to ensure test isolation without requiring a separate test database.
"""

import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables BEFORE any import that triggers config.py
_project_root = Path(__file__).resolve().parents[2]
_env_path = _project_root / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from main import app


def _get_database_url() -> str:
    """Resolve the database URL from environment variables.

    Uses ``DATABASE_URL`` if present; otherwise constructs the URL
    from individual ``POSTGRES_*`` variables with sensible defaults.
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
    """Create a single SQLAlchemy engine for the entire test session.

    The engine is disposed of after all tests complete.
    """
    database_url = _get_database_url()
    engine = create_engine(database_url, pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """Yield a database session that rolls back after each test.

    Uses a nested transaction so that any changes made during the test
    are rolled back, keeping the business database clean.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Yield a FastAPI TestClient with the database dependency overridden.

    If ``get_db`` is not yet available (e.g. before ``database.py`` is
    created in a later PR), the fixture falls back to a plain
    ``TestClient``.
    """
    try:
        from database import get_db

        app.dependency_overrides[get_db] = lambda: db_session
    except ImportError:
        pass

    with TestClient(app) as test_client:
        yield test_client

    try:
        from database import get_db

        app.dependency_overrides.pop(get_db, None)
    except ImportError:
        pass
