"""SQLAlchemy model for the ``curso`` table."""

from sqlalchemy import TIMESTAMP, Column, ForeignKey, String, func
from sqlalchemy.orm import relationship, validates

from database import Base


class Curso(Base):
    """Representa un curso académico."""

    __tablename__ = "curso"

    id_curso = Column(String(36), primary_key=True)
    nombre = Column(String(255))
    ref_semestre = Column(String(36), ForeignKey("semestre.id_semestre"))
    bloque_id = Column(String(36))
    ref_profesor = Column(String(36), ForeignKey("usuario.id_usuario"), nullable=True)
    creado_en = Column(TIMESTAMP, server_default=func.now())
    actualizado_en = Column(TIMESTAMP, server_default=func.now())

    semestre = relationship("Semestre", back_populates="cursos", lazy="select")
    ayudantias = relationship("Ayudantia", back_populates="curso", lazy="select")
    profesor = relationship(
        "Usuario", foreign_keys=[ref_profesor], back_populates="cursos_profesor", lazy="select"
    )

    @validates("profesor")
    def _validate_profesor_rol(self, key: str, value) -> object:
        """Valida que el usuario asignado como profesor tenga rol PRO."""
        if value is not None and value.rol != "PRO":
            raise ValueError("El profesor debe tener rol PRO")
        return value
