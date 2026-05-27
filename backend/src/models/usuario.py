"""SQLAlchemy model for the ``usuario`` table."""

from sqlalchemy import TIMESTAMP, Column, String, func
from sqlalchemy.orm import relationship

from database import Base


class Usuario(Base):
    """Representa un usuario del sistema."""

    __tablename__ = "usuario"

    id_usuario = Column(String(36), primary_key=True)
    nombre = Column(String(255))
    apellido = Column(String(255))
    correo = Column(String(255))
    rol = Column(String(50))
    creado_en = Column(TIMESTAMP, server_default=func.now())
    actualizado_en = Column(TIMESTAMP, server_default=func.now())

    impresiones = relationship("Impresion", back_populates="usuario", lazy="select")
    reservas = relationship("Reserva", back_populates="usuario", lazy="select")
