"""Dependencias de autenticación para FastAPI.

Exporta:
    oauth2_scheme:     Instancia de OAuth2PasswordBearer apuntando a ``/auth/token``.
    get_current_user:  Decodifica y valida el JWT del header de la request.
    requiere_rol:      Fábrica que devuelve una dependencia que valida el rol.
    get_role_session:  Re-export de ``database.get_role_session`` por conveniencia.
    get_role_db:       Dependencia FastAPI que produce la sesión del rol del usuario.
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
    """Decodifica el JWT bearer y devuelve el payload.

    Args:
        token: String del JWT extraído del header ``Authorization``.

    Returns:
        Diccionario con el payload del JWT decodificado.

    Raises:
        HTTPException: 401 si el token es inválido o está expirado.
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
    """Proporciona una sesión de base de datos para el rol del usuario actual.

    Actúa como dependencia de FastAPI: lee el rol del JWT ya autenticado
    y delega en ``get_role_session`` para obtener la sesión. Si el rol
    no tiene URL configurada, hace fallback al engine genérico con un
    warning.

    Yields:
        Sesión de SQLAlchemy apropiada para el rol del usuario.
    """
    role = current_user.get("role", "")
    yield from get_role_session(role)


def requiere_rol(roles: list[str] | set[str]) -> callable:
    """Devuelve una dependencia que valida el acceso por rol.

    Args:
        roles: Lista o conjunto de strings con los roles permitidos.

    Returns:
        Un callable apto para ``Depends()`` que valida el rol del usuario.

    Raises:
        HTTPException: 403 si ``roles`` está vacío.
        HTTPException: 403 si el rol del usuario no está en la lista permitida.
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
