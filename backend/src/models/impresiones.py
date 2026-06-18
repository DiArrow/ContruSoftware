import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

# Importamos tu dependencia de roles
from auth.dependencies import requiere_rol
from database import get_db
from models.archivo_impresion import ArchivoImpresion
from models.impresion import Impresion

router = APIRouter()

# Función pura para validar la extensión aislada de la BD
def validar_extension(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit('.', 1)[-1].lower()
    return ext in ['stl', 'obj', 'gcode']

@router.post("/impresiones", status_code=status.HTTP_201_CREATED)
async def crear_impresion(
    cantidad: int = Form(...),
    ref_articulo: str = Form(...),
    archivos: List[UploadFile] = File(...),

    # Protegido por rol. Extrae el JWT automáticamente y verifica "SOL" o "EST"
    current_user: dict = Depends(requiere_rol(["SOL", "EST"])),
    db: Session = Depends(get_db)
):
    # Validación: Sin archivos
    if not archivos or len(archivos) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Se requiere al menos un archivo adjunto."
        )

    # Validación: Extensiones permitidas
    for archivo in archivos:
        if not validar_extension(archivo.filename):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Extensión no permitida en el archivo: {archivo.filename}"
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
            estado_impresion="Pendiente"
        )
        db.add(nueva_impresion)

        # 2. Guardar archivos como binarios (BYTEA)
        for archivo in archivos:
            # 2.1 Leemos los bytes y los guardamos en la variable 'datos_archivo'
            datos_archivo = await archivo.read()

            # 2.2 Creamos el registro usando la columna 'contenido' de tu base de datos
            nuevo_archivo = ArchivoImpresion(
                id_archivo=str(uuid.uuid4()),
                ref_impresion=id_impresion,
                nombre_archivo=archivo.filename,
                contenido=datos_archivo  # Aquí pasamos los bytes leídos
            )
            db.add(nuevo_archivo)

        # 3. Transacción principal: Guarda ambas tablas. Si algo falló antes de esto, no guarda nada.
        db.commit()

        return {
            "id_impresion": id_impresion,
            "estado": nueva_impresion.estado_impresion,
            "archivos_subidos": len(archivos)
        }

    except Exception as e:
        # Rollback: Si falla la BD, anula la transacción por completo
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de BD: {str(e)}"
        )
