"""SQLAlchemy model for the ``movimiento_stock`` table."""

from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class MovimientoStock(Base):
    """Representa un movimiento de stock de un artículo."""

    __tablename__ = "movimiento_stock"

    id_movimiento = Column(String(36), primary_key=True)
    ref_articulo = Column(String(36), ForeignKey("articulo.id_articulo"))
    tipo_movimiento = Column(String(50))
    cantidad = Column(Integer)
    fecha_movimiento = Column(TIMESTAMP)

    articulo = relationship(
        "Articulo", back_populates="movimientos_stock", lazy="select"
    )
