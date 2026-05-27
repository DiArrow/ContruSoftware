"""SQLAlchemy model for the ``estudiante`` table."""

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from database import Base


class Estudiante(Base):
    """Representa un estudiante del sistema."""

    __tablename__ = "estudiante"

    id_estudiante = Column(String(36), primary_key=True)
    nombre = Column(String(255))
    apellido = Column(String(255))
    correo = Column(String(255))

    grupo_estudiantes = relationship(
        "GrupoEstudiante", back_populates="estudiante", lazy="select"
    )
    inscripciones = relationship(
        "InscripcionAyudantia", back_populates="estudiante", lazy="select"
    )
    usos_impresora = relationship(
        "UsoImpresora", back_populates="estudiante", lazy="select"
    )
