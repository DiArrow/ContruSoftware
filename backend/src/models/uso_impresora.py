"""SQLAlchemy model for the ``uso_impresora`` table."""

from sqlalchemy import TIMESTAMP, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.database import Base


class UsoImpresora(Base):
    """Representa el uso de una impresora durante una ayudantía."""

    __tablename__ = "uso_impresora"

    id_uso_impresora = Column(String(36), primary_key=True)
    ref_impresora = Column(String(36))
    ref_estudiante = Column(String(36), ForeignKey("estudiante.id_estudiante"))
    ref_ayudantia = Column(String(36), ForeignKey("ayudantia.id_ayudantia"))
    fecha_uso = Column(TIMESTAMP)

    estudiante = relationship(
        "Estudiante", back_populates="usos_impresora", lazy="select"
    )
    ayudantia = relationship(
        "Ayudantia", back_populates="usos_impresora", lazy="select"
    )
