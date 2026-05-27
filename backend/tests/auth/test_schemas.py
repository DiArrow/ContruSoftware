"""Tests para los esquemas Pydantic del módulo de autenticación.

Valida ``LoginRequest``, ``TokenResponse``, ``TokenData`` y ``UsuarioResponse``.
"""

from datetime import datetime, timezone

import pytest
from pydantic import EmailStr, ValidationError

from src.auth.schemas import LoginRequest, TokenData, TokenResponse, UsuarioResponse


class TestLoginRequest:
    """Pruebas para el esquema ``LoginRequest``."""

    def test_valid_login_request(self):
        """Debe aceptar email y password obligatorios."""
        req = LoginRequest(email="user@uc.cl", password="secret")
        assert req.email == "user@uc.cl"
        assert req.password == "secret"

    def test_missing_email_raises_validation_error(self):
        """Falta email → ``ValidationError``."""
        with pytest.raises(ValidationError):
            LoginRequest(password="secret")

    def test_missing_password_raises_validation_error(self):
        """Falta password → ``ValidationError``."""
        with pytest.raises(ValidationError):
            LoginRequest(email="user@uc.cl")

    def test_invalid_email_format_raises_validation_error(self):
        """Email con formato inválido → ``ValidationError``."""
        with pytest.raises(ValidationError):
            LoginRequest(email="not-an-email", password="secret")

    def test_invalid_email_no_at_raises_validation_error(self):
        """Email sin @ → ``ValidationError``."""
        with pytest.raises(ValidationError):
            LoginRequest(email="invalid-email.com", password="secret")

    def test_invalid_email_no_domain_raises_validation_error(self):
        """Email sin dominio → ``ValidationError``."""
        with pytest.raises(ValidationError):
            LoginRequest(email="user@", password="secret")

    def test_empty_email_raises_validation_error(self):
        """Email vacío → ``ValidationError``."""
        with pytest.raises(ValidationError):
            LoginRequest(email="", password="secret")

    def test_email_str_type(self):
        """El campo email debe validarse como email y almacenarse como str."""
        req = LoginRequest(email="test@example.com", password="secret")
        assert isinstance(req.email, str)
        assert req.email == "test@example.com"


class TestTokenResponse:
    """Pruebas para el esquema ``TokenResponse``."""

    def test_valid_token_response(self):
        """Debe aceptar access_token y usar 'bearer' por defecto."""
        resp = TokenResponse(access_token="abc123")
        assert resp.access_token == "abc123"
        assert resp.token_type == "bearer"

    def test_missing_access_token_raises_validation_error(self):
        """Falta access_token → ``ValidationError``."""
        with pytest.raises(ValidationError):
            TokenResponse()


class TestTokenData:
    """Pruebas para el esquema ``TokenData``."""

    def test_valid_token_data(self):
        """Debe aceptar sub, role y exp."""
        exp = datetime.now(timezone.utc)
        td = TokenData(sub="123", role="SOL", exp=exp)
        assert td.sub == "123"
        assert td.role == "SOL"
        assert td.exp == exp

    def test_missing_sub_raises_validation_error(self):
        """Falta sub → ``ValidationError``."""
        with pytest.raises(ValidationError):
            TokenData(role="SOL", exp=datetime.now(timezone.utc))

    def test_missing_role_raises_validation_error(self):
        """Falta role → ``ValidationError``."""
        with pytest.raises(ValidationError):
            TokenData(sub="123", exp=datetime.now(timezone.utc))

    def test_missing_exp_raises_validation_error(self):
        """Falta exp → ``ValidationError``."""
        with pytest.raises(ValidationError):
            TokenData(sub="123", role="SOL")


class TestUsuarioResponse:
    """Pruebas para el esquema ``UsuarioResponse``."""

    def test_valid_usuario_response(self):
        """Debe aceptar id_usuario, nombre, apellido, email y rol."""
        user = UsuarioResponse(
            id_usuario="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
            nombre="Juan",
            apellido="Pérez",
            email="juan@uc.cl",
            rol="SOL",
        )
        assert user.id_usuario == "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
        assert user.nombre == "Juan"
        assert user.apellido == "Pérez"
        assert user.email == "juan@uc.cl"
        assert user.rol == "SOL"

    def test_missing_id_usuario_raises_validation_error(self):
        """Falta id_usuario → ``ValidationError``."""
        with pytest.raises(ValidationError):
            UsuarioResponse(
                nombre="Juan", apellido="Pérez", email="juan@uc.cl", rol="SOL"
            )

    def test_missing_nombre_raises_validation_error(self):
        """Falta nombre → ``ValidationError``."""
        with pytest.raises(ValidationError):
            UsuarioResponse(
                id_usuario="1", apellido="Pérez", email="juan@uc.cl", rol="SOL"
            )

    def test_missing_apellido_raises_validation_error(self):
        """Falta apellido → ``ValidationError``."""
        with pytest.raises(ValidationError):
            UsuarioResponse(
                id_usuario="1", nombre="Juan", email="juan@uc.cl", rol="SOL"
            )

    def test_missing_email_raises_validation_error(self):
        """Falta email → ``ValidationError``."""
        with pytest.raises(ValidationError):
            UsuarioResponse(
                id_usuario="1", nombre="Juan", apellido="Pérez", rol="SOL"
            )

    def test_missing_rol_raises_validation_error(self):
        """Falta rol → ``ValidationError``."""
        with pytest.raises(ValidationError):
            UsuarioResponse(
                id_usuario="1", nombre="Juan", apellido="Pérez", email="juan@uc.cl"
            )
