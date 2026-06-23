"""Utilidades para validación de archivos subidos."""

import os

# Extensiones permitidas para archivos de impresión 3D.
ALLOWED_EXTENSIONS = {".stl", ".obj", ".gcode"}


def validar_extension(filename: str) -> bool:
    """Verifica si un archivo tiene una extensión permitida para impresión 3D.

    Args:
        filename: Nombre del archivo a validar (incluyendo extensión).

    Returns:
        True si la extensión está en ALLOWED_EXTENSIONS, False en caso contrario.
    """
    if not filename:
        return False
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS
