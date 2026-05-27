"""Authentication router — login and profile endpoints."""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from auth.hasher import verificar_password
from auth.jwt_handler import crear_token_jwt
from auth.schemas import LoginRequest, TokenResponse, UsuarioResponse
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from database import get_db
from models.usuario import Usuario

router = APIRouter()


@router.post("/auth/token", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    usuario = db.query(Usuario).filter(Usuario.email == credentials.email).first()
    if not usuario or not verificar_password(
        credentials.password, usuario.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = crear_token_jwt(
        data={"sub": usuario.id_usuario, "role": usuario.rol},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(access_token=token, token_type="bearer")


@router.get("/auth/me", response_model=UsuarioResponse)
def get_me(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return current authenticated user profile."""
    usuario = (
        db.query(Usuario).filter(Usuario.id_usuario == current_user["sub"]).first()
    )
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return UsuarioResponse(
        id_usuario=usuario.id_usuario,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        email=usuario.email,
        rol=usuario.rol,
    )
