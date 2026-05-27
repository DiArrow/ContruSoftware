"""Pydantic schemas for authentication payloads."""

from datetime import datetime

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Payload for user login."""

    rut: str
    password: str


class TokenResponse(BaseModel):
    """Payload returned on successful authentication."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded JWT payload."""

    sub: str
    role: str
    exp: datetime
