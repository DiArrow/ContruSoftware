"""Tests for the GET /health endpoint.

Covers:
- Healthy database → 200 + {"status": "ok"}
- Unreachable database → 503 + {"status": "error"}
"""

import pytest
from sqlalchemy.exc import OperationalError

from database import get_db
from main import app

pytestmark = pytest.mark.integration


def test_health_returns_ok(client):
    """GIVEN PostgreSQL is running, WHEN GET /health, THEN 200 and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_returns_503_on_db_down(client):
    """GIVEN DB is unreachable, WHEN GET /health, THEN 503 and status error."""

    class _FailingSession:
        def execute(self, *args, **kwargs):
            raise OperationalError(
                "connection failed", params=None, orig=Exception("DB down")
            )

    def _failing_db():
        yield _FailingSession()

    # Temporarily override get_db to simulate a failed query
    original_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = _failing_db
    try:
        response = client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "error"
        assert "detail" in data
    finally:
        if original_override is not None:
            app.dependency_overrides[get_db] = original_override
        else:
            app.dependency_overrides.pop(get_db, None)


def test_health_503_detail_contains_exception_message(client):
    """GIVEN DB raises a specific error, WHEN GET /health, THEN detail reflects it."""
    expected_msg = "custom connection failure"

    class _FailingSession:
        def execute(self, *args, **kwargs):
            raise OperationalError(
                "query failed", params=None, orig=Exception(expected_msg)
            )

    def _failing_db():
        yield _FailingSession()

    original_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = _failing_db
    try:
        response = client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "error"
        assert expected_msg in data["detail"]
    finally:
        if original_override is not None:
            app.dependency_overrides[get_db] = original_override
        else:
            app.dependency_overrides.pop(get_db, None)
