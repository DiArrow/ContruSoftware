"""Tests for tier-2 SQLAlchemy models.

Covers inscripcion_ayudantia, uso_impresora, reserva, and bloque_reservado.

Verifies table names, columns, primary keys (including composite),
foreign keys, types, timestamps, and relationship attributes.
"""

from sqlalchemy import TIMESTAMP, Date, String

from models.bloque_reservado import BloqueReservado
from models.inscripcion_ayudantia import InscripcionAyudantia
from models.reserva import Reserva
from models.uso_impresora import UsoImpresora


class TestInscripcionAyudantia:
    """Schema assertions for the ``inscripcion_ayudantia`` model."""

    def test_tablename(self):
        assert InscripcionAyudantia.__tablename__ == "inscripcion_ayudantia"

    def test_composite_primary_key(self):
        pk = InscripcionAyudantia.__table__.primary_key
        assert len(pk.columns) == 2
        assert "ref_ayudantia" in pk.columns
        assert "ref_estudiante" in pk.columns

    def test_ref_ayudantia_foreign_key(self):
        col = InscripcionAyudantia.__table__.c.ref_ayudantia
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert col.primary_key
        assert not col.nullable
        assert len(col.foreign_keys) == 1
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "ayudantia.id_ayudantia"

    def test_ref_estudiante_foreign_key(self):
        col = InscripcionAyudantia.__table__.c.ref_estudiante
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert col.primary_key
        assert not col.nullable
        assert len(col.foreign_keys) == 1
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "estudiante.id_estudiante"

    def test_fecha_inscripcion_column(self):
        col = InscripcionAyudantia.__table__.c.fecha_inscripcion
        assert isinstance(col.type, TIMESTAMP)

    def test_estado_inscripcion_column(self):
        col = InscripcionAyudantia.__table__.c.estado_inscripcion
        assert isinstance(col.type, String)
        assert col.type.length == 50

    def test_no_server_default_timestamps(self):
        assert "creado_en" not in InscripcionAyudantia.__table__.c
        assert "actualizado_en" not in InscripcionAyudantia.__table__.c

    def test_relationship_attributes_exist(self):
        assert hasattr(InscripcionAyudantia, "ayudantia")
        assert hasattr(InscripcionAyudantia, "estudiante")
        assert InscripcionAyudantia.ayudantia is not None
        assert InscripcionAyudantia.estudiante is not None


class TestUsoImpresora:
    """Schema assertions for the ``uso_impresora`` model."""

    def test_tablename(self):
        assert UsoImpresora.__tablename__ == "uso_impresora"

    def test_primary_key(self):
        pk = UsoImpresora.__table__.primary_key
        assert len(pk.columns) == 1
        assert "id_uso_impresora" in pk.columns

    def test_id_uso_impresora_type_and_length(self):
        col = UsoImpresora.__table__.c.id_uso_impresora
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert col.primary_key
        assert not col.nullable

    def test_ref_impresora_no_foreign_key(self):
        col = UsoImpresora.__table__.c.ref_impresora
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert len(col.foreign_keys) == 0

    def test_ref_estudiante_foreign_key(self):
        col = UsoImpresora.__table__.c.ref_estudiante
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert len(col.foreign_keys) == 1
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "estudiante.id_estudiante"

    def test_ref_ayudantia_foreign_key(self):
        col = UsoImpresora.__table__.c.ref_ayudantia
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert len(col.foreign_keys) == 1
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "ayudantia.id_ayudantia"

    def test_fecha_uso_column(self):
        col = UsoImpresora.__table__.c.fecha_uso
        assert isinstance(col.type, TIMESTAMP)

    def test_no_server_default_timestamps(self):
        assert "creado_en" not in UsoImpresora.__table__.c
        assert "actualizado_en" not in UsoImpresora.__table__.c

    def test_relationship_attributes_exist(self):
        assert hasattr(UsoImpresora, "estudiante")
        assert hasattr(UsoImpresora, "ayudantia")
        assert UsoImpresora.estudiante is not None
        assert UsoImpresora.ayudantia is not None


class TestReserva:
    """Schema assertions for the ``reserva`` model."""

    def test_tablename(self):
        assert Reserva.__tablename__ == "reserva"

    def test_primary_key(self):
        pk = Reserva.__table__.primary_key
        assert len(pk.columns) == 1
        assert "id_reserva" in pk.columns

    def test_id_reserva_type_and_length(self):
        col = Reserva.__table__.c.id_reserva
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert col.primary_key
        assert not col.nullable

    def test_fecha_reserva_column(self):
        col = Reserva.__table__.c.fecha_reserva
        assert isinstance(col.type, Date)

    def test_estado_reserva_column(self):
        col = Reserva.__table__.c.estado_reserva
        assert isinstance(col.type, String)
        assert col.type.length == 50

    def test_ref_usuario_foreign_key(self):
        col = Reserva.__table__.c.ref_usuario
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert len(col.foreign_keys) == 1
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "usuario.id_usuario"

    def test_ref_ayudantia_foreign_key(self):
        col = Reserva.__table__.c.ref_ayudantia
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert len(col.foreign_keys) == 1
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "ayudantia.id_ayudantia"

    def test_no_server_default_timestamps(self):
        assert "creado_en" not in Reserva.__table__.c
        assert "actualizado_en" not in Reserva.__table__.c

    def test_relationship_attributes_exist(self):
        assert hasattr(Reserva, "usuario")
        assert hasattr(Reserva, "ayudantia")
        assert hasattr(Reserva, "bloques_reservados")
        assert Reserva.usuario is not None
        assert Reserva.ayudantia is not None
        assert Reserva.bloques_reservados is not None


class TestBloqueReservado:
    """Schema assertions for the ``bloque_reservado`` model."""

    def test_tablename(self):
        assert BloqueReservado.__tablename__ == "bloque_reservado"

    def test_composite_primary_key(self):
        pk = BloqueReservado.__table__.primary_key
        assert len(pk.columns) == 2
        assert "bloque_id" in pk.columns
        assert "reserva_id" in pk.columns

    def test_bloque_id_foreign_key(self):
        col = BloqueReservado.__table__.c.bloque_id
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert col.primary_key
        assert not col.nullable
        assert len(col.foreign_keys) == 1
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "bloque_horario.id_bloque_horario"

    def test_reserva_id_foreign_key(self):
        col = BloqueReservado.__table__.c.reserva_id
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert col.primary_key
        assert not col.nullable
        assert len(col.foreign_keys) == 1
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "reserva.id_reserva"

    def test_no_extra_columns(self):
        expected = {"bloque_id", "reserva_id"}
        actual = {c.name for c in BloqueReservado.__table__.columns}
        assert actual == expected

    def test_relationship_attributes_exist(self):
        assert hasattr(BloqueReservado, "bloque_horario")
        assert hasattr(BloqueReservado, "reserva")
        assert BloqueReservado.bloque_horario is not None
        assert BloqueReservado.reserva is not None
