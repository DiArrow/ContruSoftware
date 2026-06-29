"""Router de impresiones — creación de solicitudes de impresión 3D."""

import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from auth.dependencies import get_role_db, requiere_rol
from auth.roles import ESTUDIANTE, SOLICITANTE
from models.archivo_impresion import ArchivoImpresion
from models.impresion import Impresion
from utils.files import validar_extension

router = APIRouter()


class ImpresionResponse(BaseModel):
    """Schema de respuesta para una impresión creada."""

    id_impresion: str
    ref_usuario: str
    ref_articulo: str
    cantidad: int
    fecha_impresion: datetime
    estado_impresion: str
    archivos_subidos: int

    model_config = ConfigDict(from_attributes=True)


@router.post(
    "/impresiones",
    response_model=ImpresionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def crear_impresion(
    cantidad: int = Form(...),
    ref_articulo: str = Form(...),
    archivos: List[UploadFile] = File(...),
    # Protegido por rol. Extrae el JWT automáticamente y verifica "SOL" o "EST"
    current_user: dict = Depends(requiere_rol([SOLICITANTE, ESTUDIANTE])),
    db: Session = Depends(get_role_db),
):
    """Crea una nueva solicitud de impresión con sus archivos asociados."""
    # Validación: Sin archivos
    if not archivos or len(archivos) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Se requiere al menos un archivo adjunto.",
        )

    # Validación: Extensiones permitidas
    for archivo in archivos:
        if not validar_extension(archivo.filename):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Extensión de archivo no permitida: {archivo.filename}",
            )

    try:
        id_impresion = str(uuid.uuid4())
        # El ID de usuario se extrae del JWT de forma segura
        ref_usuario = current_user["sub"]

        # 1. Crear el registro en 'impresion' (estado inicial "Pendiente")
        nueva_impresion = Impresion(
            id_impresion=id_impresion,
            ref_usuario=ref_usuario,
            ref_articulo=ref_articulo,
            cantidad=cantidad,
            fecha_impresion=datetime.now(),
            estado_impresion="Pendiente",
        )
        db.add(nueva_impresion)

        # 2. Guardar archivos como binarios (BYTEA)
        for archivo in archivos:
            # 2.1 Leemos los bytes y los guardamos en la variable 'datos_archivo'
            datos_archivo = await archivo.read()

            # 2.2 Creamos el registro usando la columna 'contenido' de la base de datos
            nuevo_archivo = ArchivoImpresion(
                id_archivo=str(uuid.uuid4()),
                ref_impresion=id_impresion,
                nombre_archivo=archivo.filename,
                contenido=datos_archivo,  # Aquí pasamos los bytes leídos
            )
            db.add(nuevo_archivo)
            nueva_impresion.archivos.append(nuevo_archivo)

        db.commit()
        db.refresh(nueva_impresion)

        return nueva_impresion

    except Exception as e:
        # Rollback: Si falla la BD, anula la transacción por completo
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de BD: {str(e)}",
        )
