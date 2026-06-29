"""Tests for the Semestre router."""

import pytest
from fastapi import status


class TestListarSemestres:
    """GET /api/semestres scenarios."""

    @pytest.mark.integration
    def test_lista_vacia_retorna_200(self, client):
        """An empty table returns 200 and an empty list."""
        response = client.get("/api/semestres")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


class TestCrearSemestre:
    """POST /api/semestres scenarios."""

    @pytest.mark.parametrize(
        "payload",
        [
            {
                "nombre": "Semestre 2026-1",
                "fecha_inicio": "2026-03-01",
                "fecha_fin": "2026-07-15",
            },
            {
                "nombre": "Semestre 2025-2",
                "fecha_inicio": "2025-08-01",
                "fecha_fin": "2025-12-15",
            },
            {
                "nombre": "Semestre 2024-1",
                "fecha_inicio": "2024-03-04",
                "fecha_fin": "2024-07-19",
            },
        ],
        ids=["2026-1", "2025-2", "2024-1"],
    )
    @pytest.mark.integration
    def test_happy_path_admin(self, client, db_session, admin_headers, payload):
        """Admin puede crear un semestre y recibe 201."""
        response = client.post("/api/semestres", json=payload, headers=admin_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nombre"] == payload["nombre"]
        assert data["fecha_inicio"] == payload["fecha_inicio"]
        assert data["fecha_fin"] == payload["fecha_fin"]
        assert data["estado"] is True
        assert "id_semestre" in data

    @pytest.mark.parametrize(
        "payload",
        [
            {
                "nombre": "Semestre 2026-2",
                "fecha_inicio": "2026-08-01",
                "fecha_fin": "2026-12-15",
            },
            {
                "nombre": "Semestre 2025-1",
                "fecha_inicio": "2025-03-03",
                "fecha_fin": "2025-07-18",
            },
        ],
        ids=["2026-2", "2025-1"],
    )
    @pytest.mark.integration
    def test_happy_path_ayu(self, client, db_session, ayu_headers, payload):
        """AYU puede crear un semestre y recibe 201."""
        response = client.post("/api/semestres", json=payload, headers=ayu_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nombre"] == payload["nombre"]
        assert data["estado"] is True

    @pytest.mark.parametrize(
        "payload",
        [
            {
                "nombre": "Semestre 2026-1",
                "fecha_inicio": "2026-03-01",
                "fecha_fin": "2026-07-15",
            },
            {
                "nombre": "Otro",
                "fecha_inicio": "2026-01-01",
                "fecha_fin": "2026-06-30",
            },
        ],
        ids=["payload_1", "payload_2"],
    )
    def test_403_rol_no_autorizado(self, client_unit, estudiante_headers, payload):
        """Rol no autorizado (EST) recibe 403."""
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

    @pytest.mark.parametrize(
        "fecha_inicio,fecha_fin",
        [
            ("2026-07-15", "2026-03-01"),
            ("2026-12-31", "2026-01-01"),
        ],
        ids=["swap_medio_anio", "swap_fin_a_inicio"],
    )
    def test_422_fecha_fin_menor_a_inicio(
        self, client_unit, admin_headers, fecha_inicio, fecha_fin
    ):
        """fecha_fin anterior a fecha_inicio devuelve 422."""
        payload = {
            "nombre": "Semestre inválido",
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
        }
        response = client_unit.post(
            "/api/semestres", json=payload, headers=admin_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize(
        "nombre_invalido",
        ["", "   ", "\t\n"],
        ids=["vacio", "solo_espacios", "whitespace_variado"],
    )
    def test_422_nombre_vacio_o_whitespace(
        self, client_unit, admin_headers, nombre_invalido
    ):
        """nombre vacío o solo whitespace devuelve 422."""
        payload = {
            "nombre": nombre_invalido,
            "fecha_inicio": "2026-03-01",
            "fecha_fin": "2026-07-15",
        }
        response = client_unit.post(
            "/api/semestres", json=payload, headers=admin_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
