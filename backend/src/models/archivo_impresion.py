from sqlalchemy import Column, ForeignKey, LargeBinary, String
from sqlalchemy.orm import relationship

from database import Base


class ArchivoImpresion(Base):
    __tablename__ = "archivo_impresion"

    id_archivo = Column(String(36), primary_key=True)

    ref_impresion = Column(
        String(36), ForeignKey("impresion.id_impresion"), nullable=False
    )

    nombre_archivo = Column(String(255), nullable=False)
    contenido = Column("contenido_archivo", LargeBinary, nullable=False)
    impresion = relationship("Impresion", back_populates="archivos")
