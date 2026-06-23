"""Constantes de roles de usuario del sistema."""

# Roles individuales
ADMIN = "ADM"
AYUDANTE = "AYU"
ESTUDIANTE = "EST"
PROFESOR = "PRO"
SOLICITANTE = "SOL"

# Conjunto completo de roles definidos
TODOS = {ADMIN, AYUDANTE, ESTUDIANTE, PROFESOR, SOLICITANTE}

# Roles autorizados para crear semestres académicos
PUEDEN_CREAR_SEMESTRE = {ADMIN, AYUDANTE}
