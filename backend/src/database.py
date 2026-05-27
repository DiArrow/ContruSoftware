"""Database engine, session factory, declarative base, and dependency injection.

Exports:
    engine:     SQLAlchemy Engine (pool_size=5, max_overflow=10)
    SessionLocal:  Session factory bound to engine
    Base:       Declarative base for all ORM models
    get_db:     FastAPI-compatible generator yielding Session instances
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from src.config import SQLALCHEMY_DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and ensure it is closed after use.

    Intended for FastAPI ``Depends(get_db)``.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
