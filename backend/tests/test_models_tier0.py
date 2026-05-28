"""Tests for tier-0 SQLAlchemy models: Usuario and Semestre.

Verifies table names, columns, primary keys, types, and timestamp defaults.
"""

from sqlalchemy import TIMESTAMP, Boolean, Date, String

from models.semestre import Semestre
from models.usuario import Usuario


class TestUsuario:
    """Schema assertions for the ``usuario`` model."""

    def test_tablename(self):
        assert Usuario.__tablename__ == "usuario"

    def test_primary_key(self):
        pk = Usuario.__table__.primary_key
        assert len(pk.columns) == 1
        assert "id_usuario" in pk.columns

    def test_id_usuario_type_and_length(self):
        col = Usuario.__table__.c.id_usuario
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert col.primary_key
        assert not col.nullable

    def test_nombre_column(self):
        col = Usuario.__table__.c.nombre
        assert isinstance(col.type, String)
        assert col.type.length == 255

    def test_apellido_column(self):
        col = Usuario.__table__.c.apellido
        assert isinstance(col.type, String)
        assert col.type.length == 255

    def test_correo_column(self):
        col = Usuario.__table__.c.correo
        assert isinstance(col.type, String)
        assert col.type.length == 255

    def test_rol_column(self):
        col = Usuario.__table__.c.rol
        assert isinstance(col.type, String)
        assert col.type.length == 50

    def test_creado_en_has_server_default(self):
        col = Usuario.__table__.c.creado_en
        assert isinstance(col.type, TIMESTAMP)
        assert col.server_default is not None

    def test_actualizado_en_has_server_default(self):
        col = Usuario.__table__.c.actualizado_en
        assert isinstance(col.type, TIMESTAMP)
        assert col.server_default is not None

    def test_relationship_attributes_exist(self):
        assert hasattr(Usuario, "impresiones")
        assert hasattr(Usuario, "reservas")
        # In SQLAlchemy 2.0 relationship descriptors become InstrumentedAttribute
        assert Usuario.impresiones is not None
        assert Usuario.reservas is not None


class TestSemestre:
    """Schema assertions for the ``semestre`` model."""

    def test_tablename(self):
        assert Semestre.__tablename__ == "semestre"

    def test_primary_key(self):
        pk = Semestre.__table__.primary_key
        assert len(pk.columns) == 1
        assert "id_semestre" in pk.columns

    def test_id_semestre_type_and_length(self):
        col = Semestre.__table__.c.id_semestre
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert col.primary_key
        assert not col.nullable

    def test_nombre_column(self):
        col = Semestre.__table__.c.nombre
        assert isinstance(col.type, String)
        assert col.type.length == 255

    def test_fecha_inicio_column(self):
        col = Semestre.__table__.c.fecha_inicio
        assert isinstance(col.type, Date)

    def test_fecha_fin_column(self):
        col = Semestre.__table__.c.fecha_fin
        assert isinstance(col.type, Date)

    def test_estado_column(self):
        col = Semestre.__table__.c.estado
        assert isinstance(col.type, Boolean)

    def test_creado_en_has_server_default(self):
        col = Semestre.__table__.c.creado_en
        assert isinstance(col.type, TIMESTAMP)
        assert col.server_default is not None

    def test_actualizado_en_has_server_default(self):
        col = Semestre.__table__.c.actualizado_en
        assert isinstance(col.type, TIMESTAMP)
        assert col.server_default is not None

    def test_relationship_attributes_exist(self):
        assert hasattr(Semestre, "cursos")
        assert Semestre.cursos is not None
