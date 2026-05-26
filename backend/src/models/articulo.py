"""SQLAlchemy model for the ``articulo`` table."""

from sqlalchemy import Boolean, Column, Integer, String, TIMESTAMP, func
from sqlalchemy.orm import relationship

from src.database import Base


class Articulo(Base):
    """Representa un artículo de inventario."""

    __tablename__ = "articulo"

    id_articulo = Column(String(36), primary_key=True)
    nombre_articulo = Column(String(255))
    stock_actual = Column(Integer)
    stock_minimo = Column(Integer)
    alerta_stock = Column(Boolean)
    actualizado_en = Column(TIMESTAMP, server_default=func.now())

    impresiones = relationship(
        "Impresion", back_populates="articulo", lazy="select"
    )
    movimientos_stock = relationship(
        "MovimientoStock", back_populates="articulo", lazy="select"
    )
