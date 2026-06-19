"""Authentication router — login and profile endpoints."""

import os
import uuid
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user, requiere_rol
from auth.hasher import verificar_password
from auth.jwt_handler import crear_token_jwt
from auth.schemas import LoginRequest, TokenResponse, UsuarioResponse
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from database import get_db
from models.archivo_impresion import ArchivoImpresion
from models.impresion import Impresion
from models.usuario import Usuario

router = APIRouter(prefix="/api/impresiones", tags=["ArchivoImpresion"])
ALLOWED_EXTENSIONS = {".stl", ".obj", ".gcode"}


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


def validar_extension(filename: str) -> bool:
    """Check if the file has an allowed extension."""
    if not filename:
        return False
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS


@router.post("/upload", status_code=status.HTTP_201_CREATED)
def crear_solicitud_impresion(
    cantidad: int = Form(...),
    ref_articulo: str = Form(...),
    archivos: List[UploadFile] = File(...),
    current_user: dict = Depends(requiere_rol(["EST", "PRO"])),
    db: Session = Depends(get_db),
):
    if not archivos or len(archivos) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Se requiere al menos un archivo para la solicitud de impresión.",
        )
    for archivo in archivos:
        if not validar_extension(archivo.filename):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Extensión de archivo no permitida: {archivo.filename}",
            )
    ref_usuario = current_user.get("id") or current_user.get("sub")

    try:
        id_impresion = str(uuid.uuid4())
        nueva_impresion = Impresion(
            id_impresion=id_impresion,
            cantidad=cantidad,
            ref_articulo=ref_articulo,
            ref_usuario=ref_usuario,
            fecha_impresion=datetime.now(),
            estado_impresion="Pendiente",
        )
        db.add(nueva_impresion)

        for archivo in archivos:
            contenido_binario = archivo.file.read()
            nuevo_archivo = ArchivoImpresion(
                id_archivo=str(uuid.uuid4()),
                ref_impresion=id_impresion,
                nombre_archivo=archivo.filename,
                contenido=contenido_binario,
            )
            db.add(nuevo_archivo)
        db.commit()
        db.refresh(nueva_impresion)

        return {
            "id": nueva_impresion.id_impresion,
            "cantidad": nueva_impresion.cantidad,
            "ref_articulo": nueva_impresion.ref_articulo,
            "estado_impresion": nueva_impresion.estado_impresion,
            "ref_usuario": nueva_impresion.ref_usuario,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la solicitud de impresión: {e}",
        )
