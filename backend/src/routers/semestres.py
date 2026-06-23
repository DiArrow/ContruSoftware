"""Router del recurso Semestre."""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy.orm import Session

from auth.dependencies import get_role_db, requiere_rol
from auth.roles import PUEDEN_CREAR_SEMESTRE
from models.semestre import Semestre

router = APIRouter(prefix="/api/semestres", tags=["semestres"])


class SemestreCreate(BaseModel):
    """Payload para crear un semestre."""

    nombre: str
    fecha_inicio: date
    fecha_fin: date

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        """Valida que el nombre no esté vacío ni solo contenga espacios."""
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío")
        return v


class SemestreResponse(BaseModel):
    """Payload de respuesta para un semestre."""

    id_semestre: str
    nombre: str
    fecha_inicio: date
    fecha_fin: date
    estado: bool

    model_config = ConfigDict(from_attributes=True)


@router.get("", response_model=list[SemestreResponse])
def listar_semestres(db: Session = Depends(get_role_db)):
    """Retorna todos los semestres ordenados por fecha_inicio DESC."""
    return (
        db.query(Semestre)
        .order_by(Semestre.fecha_inicio.desc())
        .all()
    )


@router.post(
    "", response_model=SemestreResponse, status_code=status.HTTP_201_CREATED
)
def crear_semestre(
    payload: SemestreCreate,
    db: Session = Depends(get_role_db),
    _: object = Depends(requiere_rol(PUEDEN_CREAR_SEMESTRE)),
):
    """Crea un nuevo semestre. Requiere rol ADM o AYU."""
    if payload.fecha_fin < payload.fecha_inicio:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="fecha_fin debe ser posterior o igual a fecha_inicio",
        )

    semestre = Semestre(
        id_semestre=str(uuid.uuid4()),
        nombre=payload.nombre,
        fecha_inicio=payload.fecha_inicio,
        fecha_fin=payload.fecha_fin,
        estado=True,
    )
    db.add(semestre)
    db.commit()
    db.refresh(semestre)
    return semestre
