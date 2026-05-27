"""SQLAlchemy model for the ``bloque_reservado`` table."""

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.database import Base


class BloqueReservado(Base):
    """Representa un bloque horario reservado para una reserva."""

    __tablename__ = "bloque_reservado"

    bloque_id = Column(
        String(36), ForeignKey("bloque_horario.id_bloque_horario"), primary_key=True
    )
    reserva_id = Column(
        String(36), ForeignKey("reserva.id_reserva"), primary_key=True
    )

    bloque_horario = relationship(
        "BloqueHorario", back_populates="bloques_reservados", lazy="select"
    )
    reserva = relationship(
        "Reserva", back_populates="bloques_reservados", lazy="select"
    )
