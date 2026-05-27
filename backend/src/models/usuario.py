"""SQLAlchemy model for the ``usuario`` table."""

from sqlalchemy import TIMESTAMP, Boolean, Column, String, func, text
from sqlalchemy.orm import relationship, validates

from database import Base

_ROLES_VALIDOS = {"SOL", "EST", "AYU", "PRO", "ADM"}


class Usuario(Base):
    """Representa un usuario del sistema."""

    __tablename__ = "usuario"

    id_usuario = Column(String(36), primary_key=True)
    nombre = Column(String(255))
    apellido = Column(String(255))
    correo = Column(String(255))
    email = Column(String(255), unique=True, nullable=True)
    rol = Column(String(50))
    estado = Column(Boolean, default=True, server_default=text("true"))
    creado_en = Column(TIMESTAMP, server_default=func.now())
    actualizado_en = Column(TIMESTAMP, server_default=func.now())

    impresiones = relationship("Impresion", back_populates="usuario", lazy="select")
    reservas = relationship("Reserva", back_populates="usuario", lazy="select")

    @validates("rol")
    def _validate_rol(self, key: str, value: str) -> str:
        if value not in _ROLES_VALIDOS:
            raise ValueError("Rol inválido")
        return value
