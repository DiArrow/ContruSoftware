"""SQLAlchemy model for the ``bloque_horario`` table."""

from sqlalchemy import Column, String, Time
from sqlalchemy.orm import relationship

from database import Base


class BloqueHorario(Base):
    """Representa un bloque horario para reservas."""

    __tablename__ = "bloque_horario"

    id_bloque_horario = Column(String(36), primary_key=True)
    dia_semana = Column(String(20))
    hora_inicio = Column(Time)
    hora_fin = Column(Time)

    bloques_reservados = relationship(
        "BloqueReservado", back_populates="bloque_horario", lazy="select"
    )
