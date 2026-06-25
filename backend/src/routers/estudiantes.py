"""Router for estudiantes resource."""

import secrets
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.dependencies import get_role_db, requiere_rol
from auth.hasher import hash_password
from models.curso import Curso
from models.estudiante import Estudiante
from models.grupo_estudiante import GrupoEstudiante
from models.usuario import Usuario
from utils.csv_parser import parse_csv_rows

router = APIRouter(prefix="/api/cursos", tags=["estudiantes"])


class PasswordEntry(BaseModel):
    """A generated password paired with its student email."""

    correo: str
    password: str


class CsvImportReport(BaseModel):
    """Response report for a CSV student import."""

    imported: int
    duplicates: int
    errors: list[str]
    passwords: list[PasswordEntry]


@router.post(
    "/{id_curso}/estudiantes/csv",
    response_model=CsvImportReport,
    status_code=status.HTTP_201_CREATED,
)
def importar_estudiantes_csv(
    id_curso: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_role_db),
    current_user: dict = Depends(requiere_rol(["PRO", "AYU"])),
):
    """Bulk-import students into a course from a CSV file.

    Only PRO and AYU roles can import students. The CSV must have exactly
    three columns: nombre, apellido, correo. Existing emails are counted as
    duplicates and skipped.
    """
    del current_user  # role already validated by dependency

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo debe tener extensión .csv",
        )

    curso = db.query(Curso).filter(Curso.id_curso == id_curso).first()
    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso no encontrado",
        )

    try:
        content = file.file.read().decode("utf-8-sig")
        rows = parse_csv_rows(content)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"CSV inválido: {exc}",
        ) from exc

    imported = 0
    duplicates = 0
    errors: list[str] = []
    passwords: list[PasswordEntry] = []

    for row in rows:
        correo = row["correo"].strip()
        if not correo:
            errors.append(
                f"Fila sin correo: {row['nombre']} {row['apellido']}"
            )
            continue

        existing = db.query(Usuario).filter(Usuario.email == correo).first()
        if existing:
            duplicates += 1
            continue

        password = secrets.token_urlsafe(8)
        hashed_password = hash_password(password)
        user_id = str(uuid4())

        usuario = Usuario(
            id_usuario=user_id,
            nombre=row["nombre"],
            apellido=row["apellido"],
            correo=correo,
            email=correo,
            rol="EST",
            password_hash=hashed_password,
        )
        estudiante = Estudiante(
            id_estudiante=user_id,
            nombre=row["nombre"],
            apellido=row["apellido"],
            correo=correo,
        )
        grupo = GrupoEstudiante(
            ref_grupo=id_curso,
            ref_estudiante=user_id,
        )

        db.add(usuario)
        db.add(estudiante)
        db.add(grupo)

        imported += 1
        passwords.append(PasswordEntry(correo=correo, password=password))

    db.commit()

    return CsvImportReport(
        imported=imported,
        duplicates=duplicates,
        errors=errors,
        passwords=passwords,
    )
