"""FastAPI authentication dependencies.

Exports:
    oauth2_scheme: OAuth2PasswordBearer instance pointing to ``/auth/token``.
    get_current_user: Decode and validate the JWT from the request header.
    requiere_rol: Factory that returns a dependency enforcing role-based access.
    get_role_session: Re-export of ``src.database.get_role_session`` for convenience.
"""

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from src.auth.jwt_handler import validar_token_jwt
from src.database import get_role_session

__all__ = [
    "oauth2_scheme",
    "get_current_user",
    "requiere_rol",
    "get_role_session",
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


def requiere_rol(roles: list[str]) -> callable:
    """Return a dependency that enforces role-based access.

    Args:
        roles: List of allowed role strings.

    Returns:
        A callable suitable for ``Depends()`` that validates the user's role.

    Raises:
        HTTPException: 403 if ``roles`` is empty.
        HTTPException: 403 if the user's role is not in the allowed list.
    """
    if not roles:
        raise HTTPException(
            status_code=403,
            detail="Configuración inválida: lista de roles vacía"
        )

    def _check_role(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in roles:
            raise HTTPException(status_code=403, detail="Rol no autorizado")
        return user

    return _check_role
