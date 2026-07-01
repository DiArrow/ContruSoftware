"""Router de impresiones — creación de solicitudes de impresión 3D."""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session, joinedload

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


class ImpresionMiaResponse(BaseModel):
    """Schema de respuesta para el historial de impresiones del usuario."""

    id_impresion: str
    nombre_archivo: Optional[str]
    estado: str
    fecha_solicitud: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# 1. Definir el esquema para el cuerpo (Payload) que enviará el Ayudante
class CambiarEstadoRequest(BaseModel):
    """Esquema para recibir el cambio de estado de una impresión."""

    estado: str


# 2. Agregar la constante del rol si no viene importada (o impórtala de auth.roles)
AYUDANTE = "AYU"  # Ajusta el string exacto que use tu sistema si es diferente


@router.put(
    "/impresiones/{impresion_id}/estado",
    response_model=ImpresionResponse,
)
def cambiar_estado_impresion(
    impresion_id: str,
    payload: CambiarEstadoRequest,
    current_user: dict = Depends(requiere_rol([AYUDANTE])),
    db: Session = Depends(get_role_db),
):
    impresion = (
        db.query(Impresion)
        .options(joinedload(Impresion.articulo))
        .filter(Impresion.id_impresion == impresion_id)
        .first()
    )
    if not impresion:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    if payload.estado == "En Impresion" and impresion.articulo.stock_actual < 1:
        raise HTTPException(
            status_code=400,
            detail="Stock insuficiente de filamento",
        )

    impresion.estado_impresion = payload.estado

    try:
        db.commit()
        db.refresh(impresion)
        return impresion
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al actualizar estado: {str(e)}"
        )


@router.get(
    "/impresiones/mias",
    response_model=list[ImpresionMiaResponse],
)
def listar_mis_impresiones(
    db: Session = Depends(get_role_db),
    current_user: dict = Depends(requiere_rol([ESTUDIANTE, SOLICITANTE])),
):
    """Retorna el historial de impresiones del usuario autenticado."""
    user_sub = current_user["sub"]
    impresiones = (
        db.query(Impresion)
        .options(joinedload(Impresion.archivos))
        .filter(Impresion.ref_usuario == user_sub)
        .order_by(Impresion.fecha_impresion.desc())
        .all()
    )
    return [
        ImpresionMiaResponse(
            id_impresion=imp.id_impresion,
            nombre_archivo=imp.archivos[0].nombre_archivo if imp.archivos else None,
            estado=imp.estado_impresion,
            fecha_solicitud=imp.fecha_impresion,
        )
        for imp in impresiones
    ]


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
