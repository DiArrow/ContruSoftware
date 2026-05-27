"""Tests para las dependencias de autenticación.

Valida ``get_current_user``, ``requiere_rol`` y ``get_role_session``.
"""

from datetime import timedelta

import pytest
from fastapi import HTTPException

from src.auth.dependencies import get_current_user, get_role_session, requiere_rol
from src.auth.jwt_handler import crear_token_jwt


class TestGetCurrentUser:
    """Pruebas para ``get_current_user``."""

    def test_get_current_user_valid_token(self):
        """Un token válido debe retornar el payload decodificado."""
        token = crear_token_jwt({"sub": "123", "role": "SOL"}, timedelta(minutes=10))
        user = get_current_user(token=token)
        assert user["sub"] == "123"
        assert user["role"] == "SOL"

    def test_get_current_user_invalid_token_raises_401(self):
        """Un token inválido debe lanzar HTTPException 401."""
        with pytest.raises(HTTPException) as exc:
            get_current_user(token="invalid.token.here")
        assert exc.value.status_code == 401


class TestRequiereRol:
    """Pruebas para la factory ``requiere_rol``."""

    def test_allowed_role_returns_user(self):
        """Un rol permitido debe retornar el usuario."""
        dep = requiere_rol(["SOL", "EST"])
        user = dep(user={"sub": "123", "role": "SOL"})
        assert user["role"] == "SOL"

    def test_forbidden_role_raises_403(self):
        """Un rol no permitido debe lanzar HTTPException 403."""
        dep = requiere_rol(["ADM"])
        with pytest.raises(HTTPException) as exc:
            dep(user={"sub": "123", "role": "SOL"})
        assert exc.value.status_code == 403

    def test_empty_roles_raises_500(self):
        """Una lista vacía de roles debe lanzar HTTPException 500 al crear la factory."""
        with pytest.raises(HTTPException) as exc:
            requiere_rol([])
        assert exc.value.status_code == 500


class TestGetRoleSession:
    """Pruebas para ``get_role_session``."""

    def test_get_role_session_reexports_database_function(self):
        """Debe ser la misma función que ``src.database.get_role_session``."""
        import src.database as db_mod

        assert get_role_session is db_mod.get_role_session
