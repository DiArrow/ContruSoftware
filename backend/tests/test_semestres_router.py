"""Tests for the Semestre router."""

from datetime import date

from fastapi import status


class TestListarSemestres:
    """GET /api/semestres scenarios."""

    def test_lista_vacia_retorna_200(self, client):
        """An empty table returns 200 and an empty list."""
        response = client.get("/api/semestres")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


class TestCrearSemestre:
    """POST /api/semestres scenarios."""

    def test_happy_path_admin(self, client, db_session, admin_headers):
        """Admin can create a semestre and receives 201."""
        payload = {
            "nombre": "Semestre 2026-1",
            "fecha_inicio": "2026-03-01",
            "fecha_fin": "2026-07-15",
        }

        response = client.post(
            "/api/semestres", json=payload, headers=admin_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nombre"] == payload["nombre"]
        assert data["fecha_inicio"] == payload["fecha_inicio"]
        assert data["fecha_fin"] == payload["fecha_fin"]
        assert data["estado"] is True
        assert "id_semestre" in data

    def test_happy_path_ayu(self, client, db_session, ayu_headers):
        """AYU puede crear un semestre y recibe 201."""
        payload = {
            "nombre": "Semestre 2026-2",
            "fecha_inicio": "2026-08-01",
            "fecha_fin": "2026-12-15",
        }

        response = client.post(
            "/api/semestres", json=payload, headers=ayu_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nombre"] == payload["nombre"]
        assert data["estado"] is True

    def test_403_rol_no_autorizado(self, client_unit, estudiante_headers):
        """Non-admin/ayudante role receives 403."""
        payload = {
            "nombre": "Semestre 2026-1",
            "fecha_inicio": "2026-03-01",
            "fecha_fin": "2026-07-15",
        }

        response = client_unit.post(
            "/api/semestres", json=payload, headers=estudiante_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_401_sin_token(self, client_unit):
        """Request without token receives 401."""
        payload = {
            "nombre": "Semestre 2026-1",
            "fecha_inicio": "2026-03-01",
            "fecha_fin": "2026-07-15",
        }

        response = client_unit.post("/api/semestres", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_422_fecha_fin_menor_a_inicio(self, client_unit, admin_headers):
        """fecha_fin before fecha_inicio returns 422."""
        payload = {
            "nombre": "Semestre inválido",
            "fecha_inicio": "2026-07-15",
            "fecha_fin": "2026-03-01",
        }

        response = client_unit.post(
            "/api/semestres", json=payload, headers=admin_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
