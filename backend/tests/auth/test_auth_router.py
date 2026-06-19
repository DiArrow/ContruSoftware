"""Integration tests for the authentication router.

Covers POST /auth/token and GET /auth/me using FastAPI TestClient
with the real database engine and transaction rollback isolation.
"""

from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from auth.hasher import hash_password
from auth.jwt_handler import crear_token_jwt
from database import get_db as db_get_db
from main import app
from models.usuario import Usuario

pytestmark = pytest.mark.integration


@pytest.fixture
def auth_client(client: TestClient, db_session: Session) -> TestClient:
    """Yield a TestClient with ``src.database.get_db`` overridden.

    The root ``conftest.py`` only overrides ``database.get_db``, which is a
    different module object from ``src.database.get_db``.  Without this
    additional override the auth endpoints would open a separate session and
    would not see uncommitted test data.
    """
    app.dependency_overrides[db_get_db] = lambda: db_session
    yield client
    app.dependency_overrides.pop(db_get_db, None)


@pytest.fixture
def test_usuario(db_session: Session) -> Usuario:
    """Create a test user with a hashed password."""
    usuario = Usuario(
        id_usuario=str(uuid4()),
        nombre="Test",
        apellido="User",
        email=f"test-{uuid4()}@example.com",
        rol="SOL",
        password_hash=hash_password("secret123"),
    )
    db_session.add(usuario)
    db_session.flush()
    db_session.refresh(usuario)
    yield usuario


class TestLogin:
    """Pruebas para POST /auth/token."""

    def test_login_success(self, auth_client: TestClient, test_usuario: Usuario):
        """Credenciales válidas → 200 + access_token + token_type."""
        response = auth_client.post(
            "/api/impresiones/auth/token",
            json={"email": test_usuario.email, "password": "secret123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, auth_client: TestClient, test_usuario: Usuario):
        """Contraseña incorrecta → 401."""
        response = auth_client.post(
            "/api/impresiones/auth/token",
            json={"email": test_usuario.email, "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Credenciales inválidas"

    def test_login_unknown_email(self, auth_client: TestClient):
        """Email inexistente → 401."""
        response = auth_client.post(
            "/api/impresiones/auth/token",
            json={"email": "noexiste@example.com", "password": "secret123"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Credenciales inválidas"

    def test_login_empty_body(self, auth_client: TestClient):
        """Cuerpo JSON vacío → 422."""
        response = auth_client.post("/api/impresiones/auth/token", json={})
        assert response.status_code == 422

    def test_login_missing_fields(self, auth_client: TestClient):
        """Falta email o password → 422."""
        response = auth_client.post(
            "/api/impresiones/auth/token",
            json={"email": "test@example.com"},
        )
        assert response.status_code == 422

        response = auth_client.post(
            "/api/impresiones/auth/token",
            json={"password": "secret123"},
        )
        assert response.status_code == 422


class TestGetMe:
    """Pruebas para GET /auth/me."""

    def test_get_me_success(self, auth_client: TestClient, test_usuario: Usuario):
        """Token válido → 200 + datos del usuario."""
        token = crear_token_jwt(
            data={"sub": test_usuario.id_usuario, "role": test_usuario.rol},
            expires_delta=timedelta(minutes=10),
        )
        response = auth_client.get(
            "/api/impresiones/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id_usuario"] == test_usuario.id_usuario
        assert data["nombre"] == test_usuario.nombre
        assert data["apellido"] == test_usuario.apellido
        assert data["email"] == test_usuario.email
        assert data["rol"] == test_usuario.rol

    def test_get_me_no_token(self, auth_client: TestClient):
        """Sin header Authorization → 401."""
        response = auth_client.get("/api/impresiones/auth/me")
        assert response.status_code == 401

    def test_get_me_expired_token(self, auth_client: TestClient, test_usuario: Usuario):
        """Token expirado → 401."""
        expired_token = crear_token_jwt(
            data={"sub": test_usuario.id_usuario, "role": test_usuario.rol},
            expires_delta=timedelta(seconds=-1),
        )
        response = auth_client.get(
            "/api/impresiones/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401

    def test_get_me_deleted_user(
        self, auth_client: TestClient, test_usuario: Usuario, db_session: Session
    ):
        """Usuario eliminado después de emitir el token → 404."""
        token = crear_token_jwt(
            data={"sub": test_usuario.id_usuario, "role": test_usuario.rol},
            expires_delta=timedelta(minutes=10),
        )
        db_session.delete(test_usuario)
        db_session.flush()

        response = auth_client.get(
            "/api/impresiones/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Usuario no encontrado"
