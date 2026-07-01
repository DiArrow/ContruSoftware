"""Tests for PUT /auth/me profile update endpoint."""


import pytest
from fastapi import status

from models.usuario import Usuario


def _crear_usuario(session, user_id: str, rol: str = "EST") -> Usuario:
    usuario = Usuario(
        id_usuario=user_id,
        nombre="Juan",
        apellido="Pérez",
        email="juan@p.com",
        rol=rol,
        password_hash="x",
        estado=True,
    )
    session.add(usuario)
    session.flush()
    return usuario


class TestPutMe:
    """PUT /auth/me scenarios."""

    @pytest.mark.integration
    def test_estudiante_actualiza_su_perfil(
        self, client, db_session, estudiante_headers
    ):
        user_id = "test_user@test.com"
        _crear_usuario(db_session, user_id, "EST")

        response = client.put(
            "/auth/me",
            headers=estudiante_headers,
            json={
                "nombre": "Carlos",
                "apellido": "López",
                "email": "carlos@p.com",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nombre"] == "Carlos"
        assert data["apellido"] == "López"
        assert data["email"] == "carlos@p.com"

        actualizado = db_session.get(Usuario, user_id)
        assert actualizado.nombre == "Carlos"
        assert actualizado.apellido == "López"
        assert actualizado.email == "carlos@p.com"

    @pytest.mark.integration
    def test_actualizacion_parcial_preserva_campos(
        self, client, db_session, estudiante_headers
    ):
        user_id = "test_user@test.com"
        _crear_usuario(db_session, user_id, "EST")

        response = client.put(
            "/auth/me",
            headers=estudiante_headers,
            json={"email": "nuevo@p.com"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nombre"] == "Juan"
        assert data["apellido"] == "Pérez"
        assert data["email"] == "nuevo@p.com"

        actualizado = db_session.get(Usuario, user_id)
        assert actualizado.nombre == "Juan"
        assert actualizado.apellido == "Pérez"
        assert actualizado.email == "nuevo@p.com"

    def test_email_invalido_retorna_422(self, client_unit, estudiante_headers):
        response = client_unit.put(
            "/auth/me",
            headers=estudiante_headers,
            json={"email": "no-es-un-email"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_sin_token_retorna_401(self, client_unit):
        response = client_unit.put("/auth/me", json={"nombre": "Carlos"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
