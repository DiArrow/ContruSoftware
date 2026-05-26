"""SQLAlchemy model for the ``inscripcion_ayudantia`` table."""

from sqlalchemy import TIMESTAMP, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.database import Base


class InscripcionAyudantia(Base):
    """Representa la inscripción de un estudiante a una ayudantía."""

    __tablename__ = "inscripcion_ayudantia"

    ref_ayudantia = Column(
        String(36), ForeignKey("ayudantia.id_ayudantia"), primary_key=True
    )
    ref_estudiante = Column(
        String(36), ForeignKey("estudiante.id_estudiante"), primary_key=True
    )
    fecha_inscripcion = Column(TIMESTAMP)
    estado_inscripcion = Column(String(50))

    ayudantia = relationship(
        "Ayudantia", back_populates="inscripciones", lazy="select"
    )
    estudiante = relationship(
        "Estudiante", back_populates="inscripciones", lazy="select"
    )
