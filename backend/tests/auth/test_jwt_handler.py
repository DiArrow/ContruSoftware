"""Tests para jwt_handler.

Valida creación y validación de JWTs, incluyendo expiración y
manipulación de tokens.
"""

from datetime import datetime, timedelta, timezone

import pytest
from jose import JWTError, jwt

from auth.jwt_handler import crear_token_jwt, validar_token_jwt
from config import ALGORITHM, SECRET_KEY


class TestCrearTokenJwt:
    """Pruebas para la función ``crear_token_jwt``."""

    def test_crear_token_jwt_returns_str(self):
        """Debe retornar un string no vacío."""
        token = crear_token_jwt({"sub": "123", "role": "SOL"}, timedelta(minutes=10))
        assert isinstance(token, str)
        assert len(token) > 0

    def test_crear_token_jwt_contains_sub_role_exp(self):
        """El payload decodificado debe contener sub, role y exp."""
        token = crear_token_jwt({"sub": "123", "role": "SOL"}, timedelta(minutes=10))
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "123"
        assert payload["role"] == "SOL"
        assert "exp" in payload

    def test_crear_token_jwt_exp_is_not_in_the_future_when_zero_delta(self):
        """Si expires_delta es cero, exp no debe estar en el futuro."""
        token = crear_token_jwt({"sub": "123", "role": "SOL"}, timedelta(seconds=0))
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        now = int(datetime.now(timezone.utc).timestamp())
        assert payload["exp"] <= now + 1  # tolerancia de 1s

    def test_crear_token_jwt_missing_secret_key_raises_runtimeerror(self, monkeypatch):
        """Sin SECRET_KEY debe lanzar RuntimeError."""
        monkeypatch.setattr("auth.jwt_handler.SECRET_KEY", "")
        with pytest.raises(RuntimeError, match="SECRET_KEY"):
            crear_token_jwt({"sub": "123", "role": "SOL"}, timedelta(minutes=10))


class TestValidarTokenJwt:
    """Pruebas para la función ``validar_token_jwt``."""

    def test_validar_token_jwt_returns_payload(self):
        """Debe retornar el payload original."""
        token = crear_token_jwt({"sub": "123", "role": "SOL"}, timedelta(minutes=10))
        payload = validar_token_jwt(token)
        assert payload["sub"] == "123"
        assert payload["role"] == "SOL"
        assert "exp" in payload

    def test_validar_token_jwt_expired_raises_jwt_error(self):
        """Un token expirado debe lanzar JWTError."""
        token = crear_token_jwt({"sub": "123", "role": "SOL"}, timedelta(seconds=-1))
        with pytest.raises(JWTError):
            validar_token_jwt(token)

    def test_validar_token_jwt_tampered_raises_jwt_error(self):
        """Un token alterado debe lanzar JWTError."""
        token = crear_token_jwt({"sub": "123", "role": "SOL"}, timedelta(minutes=10))
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(JWTError):
            validar_token_jwt(tampered)
