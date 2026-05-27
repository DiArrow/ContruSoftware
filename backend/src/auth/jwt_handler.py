"""JWT token creation and validation using python-jose."""

from datetime import datetime, timedelta, timezone

from jose import jwt

from src.config import ALGORITHM, SECRET_KEY


def _ensure_secret_key() -> None:
    """Raise ``RuntimeError`` if ``SECRET_KEY`` is not configured."""
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable is required")


def crear_token_jwt(data: dict, expires_delta: timedelta) -> str:
    """Encode a JWT with the given data and expiration delta.

    Args:
        data: Payload dictionary (must include at least ``sub`` and ``role``).
        expires_delta: Time delta after which the token expires.

    Returns:
        Encoded JWT string.
    """
    _ensure_secret_key()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def validar_token_jwt(token: str) -> dict:
    """Decode and validate a JWT.

    Args:
        token: Encoded JWT string.

    Returns:
        Decoded payload dictionary.

    Raises:
        jose.exceptions.JWTError: If the token is invalid or expired.
    """
    _ensure_secret_key()
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
