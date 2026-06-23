"""FastAPI authentication dependencies.

Exports:
    oauth2_scheme: OAuth2PasswordBearer instance pointing to ``/auth/token``.
    get_current_user: Decode and validate the JWT from the request header.
    requiere_rol: Factory that returns a dependency enforcing role-based access.
    get_role_session: Re-export of ``src.database.get_role_session`` for convenience.
"""

from collections.abc import Generator

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from auth.jwt_handler import validar_token_jwt
from database import get_role_session

__all__ = [
    "oauth2_scheme",
    "get_current_user",
    "requiere_rol",
    "get_role_session",
    "get_role_db",
]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Decode the JWT bearer token and return the payload.

    Args:
        token: JWT string extracted from the ``Authorization`` header.

    Returns:
        Decoded JWT payload dictionary.

    Raises:
        HTTPException: 401 if the token is invalid or expired.
    """
    try:
        payload = validar_token_jwt(token)
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado",
        )
    return payload


def get_role_db(
    current_user: dict = Depends(get_current_user),
) -> Generator[Session, None, None]:
    """Yield a database session for the current user's role.

    Acts as a FastAPI dependency: reads the role from the authenticated
    user's JWT and delegates to ``get_role_session`` for the actual session.
    Falls back to the generic engine if the role is not configured.

    Yields:
        Sesión de SQLAlchemy apropiada para el rol del usuario.
    """
    role = current_user.get("role", "")
    yield from get_role_session(role)


def requiere_rol(roles: list[str] | set[str]) -> callable:
    """Return a dependency that enforces role-based access.

    Args:
        roles: List or set of allowed role strings.

    Returns:
        A callable suitable for ``Depends()`` that validates the user's role.

    Raises:
        HTTPException: 403 if ``roles`` is empty.
        HTTPException: 403 if the user's role is not in the allowed list.
    """
    if not roles:
        raise HTTPException(
            status_code=403, detail="Configuración inválida: lista de roles vacía"
        )

    def _check_role(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in roles:
            raise HTTPException(status_code=403, detail="Rol no autorizado")
        return user

    return _check_role
