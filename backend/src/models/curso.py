"""SQLAlchemy model for the ``curso`` table."""

from sqlalchemy import TIMESTAMP, Column, ForeignKey, String, func
from sqlalchemy.orm import relationship

from database import Base


class Curso(Base):
    """Representa un curso académico."""

    __tablename__ = "curso"

    id_curso = Column(String(36), primary_key=True)
    nombre = Column(String(255))
    ref_semestre = Column(String(36), ForeignKey("semestre.id_semestre"))
    bloque_id = Column(String(36))
    creado_en = Column(TIMESTAMP, server_default=func.now())
    actualizado_en = Column(TIMESTAMP, server_default=func.now())

    semestre = relationship("Semestre", back_populates="cursos", lazy="select")
    ayudantias = relationship(
        "Ayudantia", back_populates="curso", lazy="select"
    )
