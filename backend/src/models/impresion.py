"""SQLAlchemy model for the ``impresion`` table."""

from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Impresion(Base):
    """Representa una impresión realizada por un usuario."""

    __tablename__ = "impresion"

    id_impresion = Column(String(36), primary_key=True)
    ref_usuario = Column(String(36), ForeignKey("usuario.id_usuario"))
    ref_articulo = Column(String(36), ForeignKey("articulo.id_articulo"))
    cantidad = Column(Integer)
    fecha_impresion = Column(TIMESTAMP)
    estado_impresion = Column(String(50))

    usuario = relationship("Usuario", back_populates="impresiones", lazy="select")
    articulo = relationship("Articulo", back_populates="impresiones", lazy="select")

    archivos = relationship(
        "ArchivoImpresion", back_populates="impresion", lazy="select"
    )
