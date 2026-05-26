"""SQLAlchemy model for the ``grupo_estudiante`` table."""

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.database import Base


class GrupoEstudiante(Base):
    """Representa la relación entre un grupo y un estudiante."""

    __tablename__ = "grupo_estudiante"

    ref_grupo = Column(String(36), primary_key=True)
    ref_estudiante = Column(
        String(36), ForeignKey("estudiante.id_estudiante"), primary_key=True
    )

    estudiante = relationship(
        "Estudiante", back_populates="grupo_estudiantes", lazy="select"
    )
