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

from config import ROL_DATABASE_URLS, SQLALCHEMY_DATABASE_URL

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


_role_engines: dict[str, object] = {}
_role_sessions: dict[str, object] = {}


def get_role_session(role: str) -> Generator[Session, None, None]:
    """Yield a database session bound to the role-specific engine.

    Si el rol tiene una URL configurada en ROL_DATABASE_URLS, usa el engine
    específico. Si no, hace fallback al engine genérico (SessionLocal) con
    un warning para no enmascarar errores de configuración.

    Args:
        role: Rol del usuario (e.g. "ADM", "EST").

    Yields:
        Sesión de SQLAlchemy.
    """
    url = ROL_DATABASE_URLS.get(role)
    if not url:
        import warnings

        warnings.warn(
            f"Rol '{role}' sin URL configurada — usando engine genérico",
            stacklevel=2,
        )
        db = SessionLocal()
        try:
            yield db
        finally:
            db.rollback()
            db.close()
        return

    if role not in _role_engines:
        _role_engines[role] = create_engine(url, pool_size=1, max_overflow=1)
        _role_sessions[role] = sessionmaker(
            autocommit=False, autoflush=False, bind=_role_engines[role]
        )

    db = _role_sessions[role]()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
