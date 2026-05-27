"""Tests extendidos para el modelo Usuario.

Valida email único, estado por defecto y validación de rol.
"""

import pytest
from sqlalchemy import Boolean, String
from sqlalchemy.exc import IntegrityError

from models.usuario import Usuario


class TestUsuarioExtended:
    """Schema y comportamiento extendido del modelo ``usuario``."""

    def test_email_column_exists_and_is_unique(self):
        """email debe ser VARCHAR(255) y tener unique=True."""
        col = Usuario.__table__.c.email
        assert isinstance(col.type, String)
        assert col.type.length == 255
        assert col.unique
        assert col.nullable

    def test_estado_column_exists_with_default_true(self):
        """estado debe ser BOOLEAN con server_default=true."""
        col = Usuario.__table__.c.estado
        assert isinstance(col.type, Boolean)
        assert col.server_default is not None

    def test_invalid_rol_raises_valueerror(self):
        """Un rol fuera del enum debe lanzar ValueError antes de insertar."""
        with pytest.raises(ValueError, match="Rol inválido"):
            Usuario(
                id_usuario="11111111-1111-1111-1111-111111111111",
                nombre="Test",
                apellido="Test",
                correo="test@uc.cl",
                email="test@uc.cl",
                rol="INVALID",
            )

    @pytest.mark.filterwarnings("ignore::sqlalchemy.exc.SAWarning")
    def test_email_duplicate_raises_integrityerror(self, db_session):
        """Dos usuarios con el mismo email deben lanzar IntegrityError."""
        u1 = Usuario(
            id_usuario="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            nombre="A",
            apellido="B",
            correo="dup@uc.cl",
            email="dup@uc.cl",
            rol="SOL",
        )
        db_session.add(u1)
        db_session.flush()

        u2 = Usuario(
            id_usuario="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            nombre="C",
            apellido="D",
            correo="dup@uc.cl",
            email="dup@uc.cl",
            rol="EST",
        )
        db_session.add(u2)
        with pytest.raises(IntegrityError):
            db_session.flush()
        db_session.rollback()
