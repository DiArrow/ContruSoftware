"""Tests for backend/src/database.py.

Validates engine, session factory, declarative base, and dependency-injection
generator.
"""

from unittest.mock import patch

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine, get_db

pytestmark = pytest.mark.integration


def test_engine_is_created_and_exportable():
    """engine must be a SQLAlchemy Engine with pool_size=5."""
    assert isinstance(engine, Engine)
    assert engine.pool.size() == 5


def test_session_local_creates_sessions():
    """SessionLocal must be a callable that produces Session instances."""
    session = SessionLocal()
    assert isinstance(session, Session)
    session.close()


def test_base_has_metadata_and_supports_inheritance():
    """Base must be a declarative base with usable metadata."""
    assert hasattr(Base, "metadata")
    assert Base.metadata is not None

    # Verify a model can inherit from Base
    from sqlalchemy import Column, Integer, String

    class DummyModel(Base):
        __tablename__ = "dummy_model"
        id = Column(Integer, primary_key=True)
        name = Column(String)

    assert "dummy_model" in Base.metadata.tables


def test_get_db_yields_session_and_closes():
    """get_db generator must yield a Session and then close it."""
    with patch("database.SessionLocal") as mock_factory:
        mock_session = mock_factory.return_value
        gen = get_db()
        db = next(gen)
        assert db is mock_session

        # Generator exhausts after the single yield
        with pytest.raises(StopIteration):
            next(gen)

        mock_session.close.assert_called_once()


def test_get_db_rollback_on_error():
    """If close() raises, rollback() must still have been called before it."""
    with patch("database.SessionLocal") as mock_factory:
        mock_session = mock_factory.return_value
        mock_session.close.side_effect = RuntimeError("close failed")

        gen = get_db()
        db = next(gen)
        assert db is mock_session

        with pytest.raises(RuntimeError, match="close failed"):
            gen.close()

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
