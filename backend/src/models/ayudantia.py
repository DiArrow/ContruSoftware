"""SQLAlchemy model for the ``ayudantia`` table."""

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.database import Base


class Ayudantia(Base):
    """Representa una ayudantía programada para un curso."""

    __tablename__ = "ayudantia"

    id_ayudantia = Column(String(36), primary_key=True)
    nombre_ayudantia = Column(String(255))
    ref_curso = Column(String(36), ForeignKey("curso.id_curso"))
    ref_grupo = Column(String(36))
    ref_ayudante = Column(String(36))
    estado = Column(String(50))

    curso = relationship("Curso", back_populates="ayudantias", lazy="select")
    inscripciones = relationship(
        "InscripcionAyudantia", back_populates="ayudantia", lazy="select"
    )
    usos_impresora = relationship(
        "UsoImpresora", back_populates="ayudantia", lazy="select"
    )
    reservas = relationship(
        "Reserva", back_populates="ayudantia", lazy="select"
    )
