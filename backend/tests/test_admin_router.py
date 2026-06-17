from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from auth.schemas import UsuarioCreate
from models.usuario import Usuario


def test_usuario_create_schema_valido():
    """test pydantic schema."""
    datos = {
        "nombre": "Juan",
        "apellido": "Pérez",
        "email": "juan.perez@test.com",
        "password": "securepassword123",
        "rol": "EST",
    }
    schema = UsuarioCreate(**datos)
    assert schema.nombre == "Juan"
    assert schema.email == "juan.perez@test.com"


def test_usuario_create_schema_invalid_email():
    """test pydantic schema with invalid email"""
    with pytest.raises(ValueError):
        UsuarioCreate(
            nombre="Juan",
            apellido="Pérez",
            email="email-invalido",
            password="password123",
            rol="EST",
        )


# fail
def test_admin_crear_estudiante_happy_path(
    client: TestClient, db_session, admin_headers
):
    """Happy path: admin crea EST -> 201, correct information, without password_hash."""
    payload = {
        "nombre": "Carlos",
        "apellido": "Mendoza",
        "email": "carlos.mendoza@universidad.com",
        "password": "estudiantepassword",
        "rol": "EST",
    }

    with patch(
        "auth.admin.hash_password", return_value="mocked_bcrypt_hash"
    ) as mock_hash:
        response = client.post(
            "/api/admin/usuarios", json=payload, headers=admin_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == payload["email"]
        assert data["rol"] == "EST"
        assert "password_hash" not in data
        assert "password" not in data

        mock_hash.assert_called_once_with("estudiantepassword")


# fail
def test_crear_usuario_403_rol_no_autorizado(client: TestClient, estudiante_headers):
    """403: Responce if don't have the required role (ex. EST, PRO)."""
    payload = {
        "nombre": "Test",
        "apellido": "User",
        "email": "test@test.com",
        "password": "password123",
        "rol": "EST",
    }
    response = client.post(
        "/api/admin/usuarios", json=payload, headers=estudiante_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


# fail
def test_crear_usuario_409_email_duplicado(
    client: TestClient, db_session, admin_headers
):
    """409: Response if the email already exists in db."""
    usuario_existente = Usuario(
        id_usuario=99999999,
        nombre="Existente",
        apellido="User",
        email="duplicado@test.com",
        password_hash="somehash",
        rol="EST",
        estado=True,
    )
    db_session.add(usuario_existente)
    db_session.commit()

    payload = {
        "nombre": "Nuevo",
        "apellido": "Intento",
        "email": "duplicado@test.com",
        "password": "password123",
        "rol": "EST",
    }

    response = client.post("/api/admin/usuarios", json=payload, headers=admin_headers)
    assert response.status_code == status.HTTP_409_CONFLICT


def test_crear_usuario_401_sin_token(client: TestClient):
    """401: Response if the request dosen't contain credentials/token."""
    payload = {
        "nombre": "Anon",
        "apellido": "User",
        "email": "anon@test.com",
        "password": "password123",
        "rol": "EST",
    }
    response = client.post("/api/admin/usuarios", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
