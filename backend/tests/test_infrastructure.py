"""Infrastructure tests verifying test fixtures work correctly."""

import pytest
from sqlalchemy import inspect, text

pytestmark = pytest.mark.integration


def test_db_session_can_execute_query(db_session):
    """Verify db_session fixture provides a working database session."""
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


def test_db_session_can_query_real_tables(db_session):
    """Verify db_session is connected to the business database with real tables."""
    result = db_session.execute(text("SELECT COUNT(*) FROM usuario"))
    count = result.scalar()
    assert isinstance(count, int)
    assert count >= 0


def test_test_engine_has_expected_tables(test_engine):
    """Verify test_engine is connected to the correct database schema."""
    inspector = inspect(test_engine)
    tables = inspector.get_table_names()
    assert "usuario" in tables
    assert "semestre" in tables
    assert "curso" in tables
    assert len(tables) == 15


def test_client_can_make_requests(client):
    """Verify client fixture provides a working TestClient."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_client_can_make_post_requests(client):
    """Verify client supports POST requests with JSON payload."""
    # Use a non-existent endpoint to verify POST mechanics without side effects
    response = client.post("/health", json={"probe": True})
    assert response.status_code == 405  # Method Not Allowed — confirms POST works
