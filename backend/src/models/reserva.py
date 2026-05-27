"""SQLAlchemy model for the ``reserva`` table."""

from sqlalchemy import Column, Date, ForeignKey, String
from sqlalchemy.orm import relationship

from src.database import Base


class Reserva(Base):
    """Representa una reserva de ayudantía realizada por un usuario."""

    __tablename__ = "reserva"

    id_reserva = Column(String(36), primary_key=True)
    fecha_reserva = Column(Date)
    estado_reserva = Column(String(50))
    ref_usuario = Column(String(36), ForeignKey("usuario.id_usuario"))
    ref_ayudantia = Column(String(36), ForeignKey("ayudantia.id_ayudantia"))

    usuario = relationship("Usuario", back_populates="reservas", lazy="select")
    ayudantia = relationship(
        "Ayudantia", back_populates="reservas", lazy="select"
    )
    bloques_reservados = relationship(
        "BloqueReservado", back_populates="reserva", lazy="select"
    )
