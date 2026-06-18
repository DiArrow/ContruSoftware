"""Pydantic schemas for authentication payloads."""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Payload for user login."""

    email: EmailStr
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


class UsuarioCreate(BaseModel):
    """Payload for creating a new user."""

    nombre: str
    apellido: str
    email: EmailStr
    password: str
    rol: str


class UsuarioResponse(BaseModel):
    """Payload returned for authenticated user profile."""

    id_usuario: str
    nombre: str
    apellido: str
    email: str
    rol: str

    class Config:
        from_attributes = True
