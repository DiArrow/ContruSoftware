"""
Engine de base de datos, fábrica de sesiones, base declarativa e
inyección de dependencias.
Exporta:
    engine:         SQLAlchemy Engine (pool_size=5, max_overflow=10)
    SessionLocal:   Fábrica de sesiones ligada al engine
    Base:           Base declarativa para todos los modelos ORM
    get_db:         Generador compatible con FastAPI que produce sesiones
    get_role_session: Generador que produce sesiones específicas por rol
"""

import warnings
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
    """Proporciona una sesión de base de datos y asegura su cierre tras su uso.

    Diseñada para usarse con ``Depends(get_db)`` de FastAPI. Pensada para
    endpoints sin autenticación (login, health check). Para endpoints
    autenticados, usar ``get_role_db`` desde ``auth.dependencies``.
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
    """Proporciona una sesión de base de datos ligada al engine del rol.

    Si el rol tiene una URL configurada en ``ROL_DATABASE_URLS``, usa el
    engine específico. Si no, hace fallback al engine genérico
    (``SessionLocal``) emitiendo un warning para no enmascarar errores
    de configuración.

    Args:
        role: Rol del usuario (por ejemplo, ``"ADM"`` o ``"EST"``).

    Yields:
        Sesión de SQLAlchemy apropiada para el rol.
    """
    url = ROL_DATABASE_URLS.get(role)
    if not url:
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
