"""Tests para los esquemas Pydantic del módulo de autenticación.

Valida ``LoginRequest``, ``TokenResponse`` y ``TokenData``.
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from src.auth.schemas import LoginRequest, TokenData, TokenResponse


class TestLoginRequest:
    """Pruebas para el esquema ``LoginRequest``."""

    def test_valid_login_request(self):
        """Debe aceptar rut y password obligatorios."""
        req = LoginRequest(rut="12345678-9", password="secret")
        assert req.rut == "12345678-9"
        assert req.password == "secret"

    def test_missing_rut_raises_validation_error(self):
        """Falta rut → ``ValidationError``."""
        with pytest.raises(ValidationError):
            LoginRequest(password="secret")

    def test_missing_password_raises_validation_error(self):
        """Falta password → ``ValidationError``."""
        with pytest.raises(ValidationError):
            LoginRequest(rut="12345678-9")


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
