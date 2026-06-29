"""Router de administración — gestión de usuarios."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import hasher
from auth.dependencies import get_role_db, requiere_rol
from auth.roles import ADMIN
from auth.schemas import UsuarioCreate, UsuarioResponse
from models.usuario import Usuario

router = APIRouter(tags=["admin"])


@router.post(
    "/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED
)
def crear_usuario(
    payload: UsuarioCreate,
    db: Session = Depends(get_role_db),
    current_admin: Usuario = Depends(requiere_rol([ADMIN])),
):
    """Endpoint para que un administrador cree nuevos usuarios.

    Verifica duplicados de email, hashea la contraseña y persiste el registro.
    """
    email_existente = db.query(Usuario).filter(Usuario.email == payload.email).first()
    if email_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            # Criterio de aceptacion 409
            detail="El email ya se encuentra registrado",
        )
    hashed_password = hasher.hash_password(payload.password)

    nuevo_usuario = Usuario(
        nombre=payload.nombre,
        apellido=payload.apellido,
        email=payload.email,
        password_hash=hashed_password,
        rol=payload.rol,
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario
