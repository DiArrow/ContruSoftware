"""Router del recurso Curso."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy.orm import Session

from auth.dependencies import get_role_db, requiere_rol
from models.curso import Curso
from models.semestre import Semestre
from models.usuario import Usuario

router = APIRouter(prefix="/api/cursos", tags=["cursos"])


class CursoCreate(BaseModel):
    """Payload para crear un curso."""

    nombre: str
    ref_semestre: UUID
    ref_profesor: Optional[UUID] = None
    bloque_id: Optional[str] = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        """El nombre no puede estar vacío ni ser solo espacios."""
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío")
        return v


class CursoUpdate(BaseModel):
    """Payload para actualizar parcialmente un curso."""

    nombre: Optional[str] = None
    ref_semestre: Optional[UUID] = None
    ref_profesor: Optional[UUID] = None
    bloque_id: Optional[str] = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío")
        return v


class CursoResponse(BaseModel):
    """Payload de respuesta para un curso."""

    id_curso: str
    nombre: str
    ref_semestre: str
    semestre_nombre: Optional[str]
    ref_profesor: Optional[str]
    bloque_id: Optional[str]
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)


def _construir_respuesta(curso: Curso) -> CursoResponse:
    """Construye la respuesta a partir de un objeto Curso con semestre cargado."""
    return CursoResponse(
        id_curso=curso.id_curso,
        nombre=curso.nombre,
        ref_semestre=curso.ref_semestre,
        semestre_nombre=curso.semestre.nombre if curso.semestre else None,
        ref_profesor=curso.ref_profesor,
        bloque_id=curso.bloque_id,
        creado_en=curso.creado_en,
        actualizado_en=curso.actualizado_en,
    )


@router.post("", response_model=CursoResponse, status_code=status.HTTP_201_CREATED)
def crear_curso(
    payload: CursoCreate,
    db: Session = Depends(get_role_db),
    current_user: dict = Depends(requiere_rol(["PRO", "AYU"])),
):
    """Crea un curso. PRO usa su JWT como profesor; AYU debe indicarlo."""
    user_role = current_user["role"]
    user_sub = current_user["sub"]

    if user_role == "PRO":
        if payload.ref_profesor is not None and str(payload.ref_profesor) != user_sub:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El campo ref_profesor no puede diferir del usuario PRO",
            )
        ref_profesor = user_sub
    else:  # AYU
        if not payload.ref_profesor:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El campo ref_profesor es requerido para el rol AYU",
            )
        profesor = (
            db.query(Usuario)
            .filter(Usuario.id_usuario == str(payload.ref_profesor))
            .first()
        )
        if not profesor or profesor.rol != "PRO":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El profesor indicado no existe o no tiene rol PRO",
            )
        ref_profesor = str(payload.ref_profesor)

    semestre = (
        db.query(Semestre)
        .filter(Semestre.id_semestre == str(payload.ref_semestre))
        .first()
    )
    if not semestre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semestre no encontrado",
        )

    nuevo_curso = Curso(
        id_curso=str(uuid4()),
        nombre=payload.nombre,
        ref_semestre=str(payload.ref_semestre),
        ref_profesor=ref_profesor,
        bloque_id=payload.bloque_id,
    )
    db.add(nuevo_curso)
    db.commit()
    db.refresh(nuevo_curso)

    return _construir_respuesta(nuevo_curso)


@router.get("", response_model=list[CursoResponse])
def listar_cursos(
    db: Session = Depends(get_role_db),
    current_user: dict = Depends(requiere_rol(["PRO", "AYU"])),
):
    """Lista cursos. PRO ve solo los suyos; AYU ve todos."""
    query = db.query(Curso).outerjoin(
        Semestre, Curso.ref_semestre == Semestre.id_semestre
    )

    if current_user["role"] == "PRO":
        query = query.filter(Curso.ref_profesor == current_user["sub"])

    cursos = query.all()
    return [_construir_respuesta(curso) for curso in cursos]


@router.get("/{id_curso}", response_model=CursoResponse)
def obtener_curso(
    id_curso: str,
    db: Session = Depends(get_role_db),
    current_user: dict = Depends(requiere_rol(["PRO", "AYU"])),
):
    """Retorna el detalle de un curso incluyendo el nombre del semestre."""
    curso = (
        db.query(Curso)
        .outerjoin(Semestre, Curso.ref_semestre == Semestre.id_semestre)
        .filter(Curso.id_curso == id_curso)
        .first()
    )
    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso no encontrado",
        )

    return _construir_respuesta(curso)


@router.put("/{id_curso}", response_model=CursoResponse)
def actualizar_curso(
    id_curso: str,
    payload: CursoUpdate,
    db: Session = Depends(get_role_db),
    current_user: dict = Depends(requiere_rol(["ADM"])),
):
    """Actualiza parcialmente un curso (solo ADM)."""
    curso = db.query(Curso).filter(Curso.id_curso == id_curso).first()
    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso no encontrado",
        )

    datos = payload.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        if campo == "ref_semestre" and valor is not None:
            semestre = (
                db.query(Semestre)
                .filter(Semestre.id_semestre == str(valor))
                .first()
            )
            if not semestre:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Semestre no encontrado",
                )

        if campo == "ref_profesor" and valor is not None:
            profesor = (
                db.query(Usuario)
                .filter(Usuario.id_usuario == str(valor))
                .first()
            )
            if not profesor or profesor.rol != "PRO":
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="El profesor indicado no existe o no tiene rol PRO",
                )

        setattr(curso, campo, str(valor) if isinstance(valor, UUID) else valor)

    curso.actualizado_en = datetime.now()
    db.commit()
    db.refresh(curso)

    return _construir_respuesta(curso)


@router.delete("/{id_curso}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_curso(
    id_curso: str,
    db: Session = Depends(get_role_db),
    current_user: dict = Depends(requiere_rol(["ADM"])),
):
    """Elimina físicamente un curso (solo ADM)."""
    curso = db.query(Curso).filter(Curso.id_curso == id_curso).first()
    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso no encontrado",
        )

    db.delete(curso)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
