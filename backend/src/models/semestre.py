"""SQLAlchemy model for the ``semestre`` table."""

from sqlalchemy import TIMESTAMP, Boolean, Column, Date, String, func
from sqlalchemy.orm import relationship

from src.database import Base


class Semestre(Base):
    """Representa un semestre académico."""

    __tablename__ = "semestre"

    id_semestre = Column(String(36), primary_key=True)
    nombre = Column(String(255))
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    estado = Column(Boolean)
    creado_en = Column(TIMESTAMP, server_default=func.now())
    actualizado_en = Column(TIMESTAMP, server_default=func.now())

    cursos = relationship("Curso", back_populates="semestre", lazy="select")
