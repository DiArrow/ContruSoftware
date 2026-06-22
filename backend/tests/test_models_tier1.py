"""Tests for tier-1 SQLAlchemy models.

Covers estudiante, articulo, bloque_horario, curso, grupo_estudiante,
impresion, movimiento_stock, and ayudantia.

Verifies table names, columns, primary keys, foreign keys, types,
timestamps, and relationship attributes against the SQL schema.
"""

from sqlalchemy import TIMESTAMP, Boolean, Integer, LargeBinary, String, Time
from sqlalchemy.orm import RelationshipProperty

from models.archivo_impresion import ArchivoImpresion
from models.articulo import Articulo
from models.ayudantia import Ayudantia
from models.bloque_horario import BloqueHorario
from models.curso import Curso
from models.estudiante import Estudiante
from models.grupo_estudiante import GrupoEstudiante
from models.impresion import Impresion
from models.movimiento_stock import MovimientoStock


class TestEstudiante:
    """Schema assertions for the ``estudiante`` model."""

    def test_tablename(self):
        assert Estudiante.__tablename__ == "estudiante"

    def test_primary_key(self):
        pk = Estudiante.__table__.primary_key
        assert len(pk.columns) == 1
        assert "id_estudiante" in pk.columns

    def test_id_estudiante_type_and_length(self):
        col = Estudiante.__table__.c.id_estudiante
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert col.primary_key
        assert not col.nullable

    def test_nombre_column(self):
        col = Estudiante.__table__.c.nombre
        assert isinstance(col.type, String)
        assert col.type.length == 255

    def test_apellido_column(self):
        col = Estudiante.__table__.c.apellido
        assert isinstance(col.type, String)
        assert col.type.length == 255

    def test_correo_column(self):
        col = Estudiante.__table__.c.correo
        assert isinstance(col.type, String)
        assert col.type.length == 255

    def test_no_timestamps(self):
        assert not hasattr(Estudiante.__table__.c, "creado_en")
        assert not hasattr(Estudiante.__table__.c, "actualizado_en")

    def test_relationship_attributes_exist(self):
        assert hasattr(Estudiante, "grupo_estudiantes")
        assert hasattr(Estudiante, "inscripciones")
        assert hasattr(Estudiante, "usos_impresora")
        assert Estudiante.grupo_estudiantes is not None
        assert Estudiante.inscripciones is not None
        assert Estudiante.usos_impresora is not None


class TestArticulo:
    """Schema assertions for the ``articulo`` model."""

    def test_tablename(self):
        assert Articulo.__tablename__ == "articulo"

    def test_primary_key(self):
        pk = Articulo.__table__.primary_key
        assert len(pk.columns) == 1
        assert "id_articulo" in pk.columns

    def test_id_articulo_type_and_length(self):
        col = Articulo.__table__.c.id_articulo
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert col.primary_key
        assert not col.nullable

    def test_nombre_articulo_column(self):
        col = Articulo.__table__.c.nombre_articulo
        assert isinstance(col.type, String)
        assert col.type.length == 255

    def test_stock_actual_column(self):
        col = Articulo.__table__.c.stock_actual
        assert isinstance(col.type, Integer)

    def test_stock_minimo_column(self):
        col = Articulo.__table__.c.stock_minimo
        assert isinstance(col.type, Integer)

    def test_alerta_stock_column(self):
        col = Articulo.__table__.c.alerta_stock
        assert isinstance(col.type, Boolean)

    def test_actualizado_en_has_server_default(self):
        col = Articulo.__table__.c.actualizado_en
        assert isinstance(col.type, TIMESTAMP)
        assert col.server_default is not None

    def test_no_creado_en(self):
        assert "creado_en" not in Articulo.__table__.c

    def test_relationship_attributes_exist(self):
        assert hasattr(Articulo, "impresiones")
        assert hasattr(Articulo, "movimientos_stock")
        assert Articulo.impresiones is not None
        assert Articulo.movimientos_stock is not None


class TestBloqueHorario:
    """Schema assertions for the ``bloque_horario`` model."""

    def test_tablename(self):
        assert BloqueHorario.__tablename__ == "bloque_horario"

    def test_primary_key(self):
        pk = BloqueHorario.__table__.primary_key
        assert len(pk.columns) == 1
        assert "id_bloque_horario" in pk.columns

    def test_id_bloque_horario_type_and_length(self):
        col = BloqueHorario.__table__.c.id_bloque_horario
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert col.primary_key
        assert not col.nullable

    def test_dia_semana_column(self):
        col = BloqueHorario.__table__.c.dia_semana
        assert isinstance(col.type, String)
        assert col.type.length == 20

    def test_hora_inicio_column(self):
        col = BloqueHorario.__table__.c.hora_inicio
        assert isinstance(col.type, Time)

    def test_hora_fin_column(self):
        col = BloqueHorario.__table__.c.hora_fin
        assert isinstance(col.type, Time)

    def test_no_timestamps(self):
        assert "creado_en" not in BloqueHorario.__table__.c
        assert "actualizado_en" not in BloqueHorario.__table__.c

    def test_relationship_attributes_exist(self):
        assert hasattr(BloqueHorario, "bloques_reservados")
        assert BloqueHorario.bloques_reservados is not None


class TestCurso:
    """Schema assertions for the ``curso`` model."""

    def test_tablename(self):
        assert Curso.__tablename__ == "curso"

    def test_primary_key(self):
        pk = Curso.__table__.primary_key
        assert len(pk.columns) == 1
        assert "id_curso" in pk.columns

    def test_id_curso_type_and_length(self):
        col = Curso.__table__.c.id_curso
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert col.primary_key
        assert not col.nullable

    def test_nombre_column(self):
        col = Curso.__table__.c.nombre
        assert isinstance(col.type, String)
        assert col.type.length == 255

    def test_ref_semestre_foreign_key(self):
        col = Curso.__table__.c.ref_semestre
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert len(col.foreign_keys) == 1
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "semestre.id_semestre"

    def test_bloque_id_column(self):
        col = Curso.__table__.c.bloque_id
        assert isinstance(col.type, String)
        assert col.type.length == 36

    def test_creado_en_has_server_default(self):
        col = Curso.__table__.c.creado_en
        assert isinstance(col.type, TIMESTAMP)
        assert col.server_default is not None

    def test_actualizado_en_has_server_default(self):
        col = Curso.__table__.c.actualizado_en
        assert isinstance(col.type, TIMESTAMP)
        assert col.server_default is not None

    def test_relationship_attributes_exist(self):
        assert hasattr(Curso, "semestre")
        assert hasattr(Curso, "ayudantias")
        assert hasattr(Curso, "profesor")
        assert Curso.semestre is not None
        assert Curso.ayudantias is not None
        assert Curso.profesor is not None

    def test_ref_profesor_column(self):
        col = Curso.__table__.c.ref_profesor
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert col.nullable

    def test_ref_profesor_foreign_key(self):
        col = Curso.__table__.c.ref_profesor
        assert len(col.foreign_keys) == 1
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "usuario.id_usuario"

    def test_profesor_relationship(self):
        assert hasattr(Curso, "profesor")
        assert Curso.profesor is not None


class TestGrupoEstudiante:
    """Schema assertions for the ``grupo_estudiante`` model."""

    def test_tablename(self):
        assert GrupoEstudiante.__tablename__ == "grupo_estudiante"

    def test_composite_primary_key(self):
        pk = GrupoEstudiante.__table__.primary_key
        assert len(pk.columns) == 2
        assert "ref_grupo" in pk.columns
        assert "ref_estudiante" in pk.columns

    def test_ref_grupo_type_and_length(self):
        col = GrupoEstudiante.__table__.c.ref_grupo
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert col.primary_key
        assert not col.nullable

    def test_ref_estudiante_foreign_key(self):
        col = GrupoEstudiante.__table__.c.ref_estudiante
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert col.primary_key
        assert not col.nullable
        assert len(col.foreign_keys) == 1
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "estudiante.id_estudiante"

    def test_relationship_attributes_exist(self):
        assert hasattr(GrupoEstudiante, "estudiante")
        assert GrupoEstudiante.estudiante is not None


class TestImpresion:
    """Schema assertions for the ``impresion`` model."""

    def test_tablename(self):
        assert Impresion.__tablename__ == "impresion"

    def test_primary_key(self):
        pk = Impresion.__table__.primary_key
        assert len(pk.columns) == 1
        assert "id_impresion" in pk.columns

    def test_id_impresion_type_and_length(self):
        col = Impresion.__table__.c.id_impresion
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert col.primary_key
        assert not col.nullable

    def test_ref_usuario_foreign_key(self):
        col = Impresion.__table__.c.ref_usuario
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert len(col.foreign_keys) == 1
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "usuario.id_usuario"

    def test_ref_articulo_foreign_key(self):
        col = Impresion.__table__.c.ref_articulo
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert len(col.foreign_keys) == 1
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "articulo.id_articulo"

    def test_cantidad_column(self):
        col = Impresion.__table__.c.cantidad
        assert isinstance(col.type, Integer)

    def test_fecha_impresion_column(self):
        col = Impresion.__table__.c.fecha_impresion
        assert isinstance(col.type, TIMESTAMP)

    def test_estado_impresion_column(self):
        col = Impresion.__table__.c.estado_impresion
        assert isinstance(col.type, String)
        assert col.type.length == 50

    def test_no_server_default_timestamps(self):
        assert "creado_en" not in Impresion.__table__.c
        assert "actualizado_en" not in Impresion.__table__.c

    def test_relationship_attributes_exist(self):
        assert hasattr(Impresion, "usuario")
        assert hasattr(Impresion, "articulo")
        assert hasattr(Impresion, "archivos")
        assert Impresion.usuario is not None
        assert Impresion.articulo is not None
        assert Impresion.archivos is not None

    def test_archivos_relationship_is_list(self):
        """La relación archivos debe ser uselist=True (1:N, carga lista)."""
        prop = Impresion.archivos.property
        assert isinstance(prop, RelationshipProperty)
        assert prop.uselist is True, (
            "Impresion.archivos debe configurarse como lista (uselist=True)"
        )


class TestMovimientoStock:
    """Schema assertions for the ``movimiento_stock`` model."""

    def test_tablename(self):
        assert MovimientoStock.__tablename__ == "movimiento_stock"

    def test_primary_key(self):
        pk = MovimientoStock.__table__.primary_key
        assert len(pk.columns) == 1
        assert "id_movimiento" in pk.columns

    def test_id_movimiento_type_and_length(self):
        col = MovimientoStock.__table__.c.id_movimiento
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert col.primary_key
        assert not col.nullable

    def test_ref_articulo_foreign_key(self):
        col = MovimientoStock.__table__.c.ref_articulo
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert len(col.foreign_keys) == 1
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "articulo.id_articulo"

    def test_tipo_movimiento_column(self):
        col = MovimientoStock.__table__.c.tipo_movimiento
        assert isinstance(col.type, String)
        assert col.type.length == 50

    def test_cantidad_column(self):
        col = MovimientoStock.__table__.c.cantidad
        assert isinstance(col.type, Integer)

    def test_fecha_movimiento_column(self):
        col = MovimientoStock.__table__.c.fecha_movimiento
        assert isinstance(col.type, TIMESTAMP)

    def test_no_server_default_timestamps(self):
        assert "creado_en" not in MovimientoStock.__table__.c
        assert "actualizado_en" not in MovimientoStock.__table__.c

    def test_relationship_attributes_exist(self):
        assert hasattr(MovimientoStock, "articulo")
        assert MovimientoStock.articulo is not None


class TestAyudantia:
    """Schema assertions for the ``ayudantia`` model."""

    def test_tablename(self):
        assert Ayudantia.__tablename__ == "ayudantia"

    def test_primary_key(self):
        pk = Ayudantia.__table__.primary_key
        assert len(pk.columns) == 1
        assert "id_ayudantia" in pk.columns

    def test_id_ayudantia_type_and_length(self):
        col = Ayudantia.__table__.c.id_ayudantia
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert col.primary_key
        assert not col.nullable

    def test_nombre_ayudantia_column(self):
        col = Ayudantia.__table__.c.nombre_ayudantia
        assert isinstance(col.type, String)
        assert col.type.length == 255

    def test_ref_curso_foreign_key(self):
        col = Ayudantia.__table__.c.ref_curso
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert len(col.foreign_keys) == 1
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "curso.id_curso"

    def test_ref_grupo_column(self):
        col = Ayudantia.__table__.c.ref_grupo
        assert isinstance(col.type, String)
        assert col.type.length == 36

    def test_ref_ayudante_column(self):
        col = Ayudantia.__table__.c.ref_ayudante
        assert isinstance(col.type, String)
        assert col.type.length == 36

    def test_estado_column(self):
        col = Ayudantia.__table__.c.estado
        assert isinstance(col.type, String)
        assert col.type.length == 50

    def test_no_timestamps(self):
        assert "creado_en" not in Ayudantia.__table__.c
        assert "actualizado_en" not in Ayudantia.__table__.c

    def test_relationship_attributes_exist(self):
        assert hasattr(Ayudantia, "curso")
        assert hasattr(Ayudantia, "inscripciones")
        assert hasattr(Ayudantia, "usos_impresora")
        assert hasattr(Ayudantia, "reservas")
        assert Ayudantia.curso is not None
        assert Ayudantia.inscripciones is not None
        assert Ayudantia.usos_impresora is not None
        assert Ayudantia.reservas is not None


class TestArchivoImpresion:
    """Schema assertions for the ``archivo_impresion`` model."""

    def test_tablename(self):
        assert ArchivoImpresion.__tablename__ == "archivo_impresion"

    def test_primary_key(self):
        pk = ArchivoImpresion.__table__.primary_key
        assert len(pk.columns) == 1
        assert "id_archivo" in pk.columns

    def test_id_archivo_type_and_length(self):
        col = ArchivoImpresion.__table__.c.id_archivo
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert col.primary_key
        assert not col.nullable

    def test_ref_impresion_foreign_key(self):
        col = ArchivoImpresion.__table__.c.ref_impresion
        assert isinstance(col.type, String)
        assert col.type.length == 36
        assert len(col.foreign_keys) == 1
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "impresion.id_impresion"

    def test_nombre_archivo_column(self):
        col = ArchivoImpresion.__table__.c.nombre_archivo
        assert isinstance(col.type, String)
        assert col.type.length == 255
        assert not col.nullable

    def test_contenido_column(self):
        col = ArchivoImpresion.__table__.c.contenido
        assert isinstance(col.type, LargeBinary)
        assert not col.nullable

    def test_no_timestamps(self):
        assert "creado_en" not in ArchivoImpresion.__table__.c
        assert "actualizado_en" not in ArchivoImpresion.__table__.c

    def test_relationship_attributes_exist(self):
        assert hasattr(ArchivoImpresion, "impresion")
        assert ArchivoImpresion.impresion is not None


class TestArchivoImpresionMigration:
    """Verifica la calidad de la migración SQL de archivo_impresion."""

    @staticmethod
    def _migration_path() -> str:
        from pathlib import Path

        project_root = Path(__file__).resolve().parents[2]
        return str(
            project_root / "db" / "migrations" / "03-create-archivo-impresion.sql"
        )

    def test_migration_is_idempotent(self):
        """La migración debe usar IF NOT EXISTS para ser idempotente."""
        with open(self._migration_path()) as f:
            sql = f.read()
        assert "IF NOT EXISTS" in sql, (
            "La migración debe incluir IF NOT EXISTS para ser idempotente"
        )

    def test_migration_column_matches_model(self):
        """La columna contenido en la migración debe coincidir con el modelo."""
        with open(self._migration_path()) as f:
            sql = f.read()
        assert "contenido BYTEA" in sql or "contenido " in sql, (
            "La migración debe usar 'contenido' para coincidir con el modelo SQLAlchemy"
        )


class TestRefProfesorMigration:
    """Verifica la calidad de la migración SQL de ref_profesor en curso."""

    @staticmethod
    def _migration_path() -> str:
        from pathlib import Path

        project_root = Path(__file__).resolve().parents[2]
        return str(project_root / "db" / "migrations" / "04-add-ref-profesor-to-curso.sql")

    def test_migration_is_idempotent(self):
        """La migración debe usar IF NOT EXISTS para ser idempotente."""
        with open(self._migration_path()) as f:
            sql = f.read()
        assert "IF NOT EXISTS" in sql, (
            "La migración debe incluir IF NOT EXISTS para ser idempotente"
        )

    def test_migration_includes_foreign_key(self):
        """La migración debe declarar una foreign key hacia usuario."""
        with open(self._migration_path()) as f:
            sql = f.read()
        assert "REFERENCES usuario" in sql, (
            "La migración debe referenciar la tabla usuario"
        )

    def test_migration_includes_index(self):
        """La migración debe crear un índice para ref_profesor."""
        with open(self._migration_path()) as f:
            sql = f.read()
        assert "CREATE INDEX" in sql, (
            "La migración debe incluir CREATE INDEX"
        )
        assert "idx_curso_ref_profesor" in sql, (
            "El índice debe llamarse idx_curso_ref_profesor"
        )
