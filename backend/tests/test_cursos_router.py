"""Tests for the Curso router."""

from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi import status

from auth.jwt_handler import crear_token_jwt
from models.curso import Curso
from models.estudiante import Estudiante
from models.grupo_estudiante import GrupoEstudiante
from models.semestre import Semestre
from models.usuario import Usuario

USER_IDS = {
    "PRO": uuid4(),
    "AYU": uuid4(),
    "EST": uuid4(),
    "ADM": uuid4(),
}


def _token_headers(rol: str, user_id: str | None = None) -> dict:
    sub = str(user_id) if user_id else str(USER_IDS.get(rol, uuid4()))
    token = crear_token_jwt(
        data={"sub": sub, "role": rol},
        expires_delta=timedelta(hours=24),
    )
    return {"Authorization": f"Bearer {token}"}


def _crear_profesor(session, user_id: str | None = None) -> str:
    """Crea un usuario con rol PRO y retorna su id."""
    uid = user_id or str(uuid4())
    session.add(
        Usuario(
            id_usuario=uid,
            nombre="Profe",
            email=f"pro_{uid[:8]}@test.com",
            password_hash="x",
            rol="PRO",
        )
    )
    session.flush()
    return uid


def _crear_semestre(session, nombre: str = "Semestre 2026-1") -> str:
    """Crea un semestre y retorna su id."""
    sid = str(uuid4())
    session.add(Semestre(id_semestre=sid, nombre=nombre))
    session.flush()
    return sid


def _crear_estudiante(session, user_id: str | None = None) -> str:
    """Crea un estudiante y retorna su id."""
    uid = user_id or str(uuid4())
    session.add(
        Estudiante(
            id_estudiante=uid,
            nombre="Estudiante",
            apellido="Test",
            correo=f"est_{uid[:8]}@test.com",
        )
    )
    session.flush()
    return uid


# ───────────────────────────────
# GET /cursos
# ───────────────────────────────


class TestListarCursos:
    """GET /cursos scenarios."""

    @pytest.mark.integration
    def test_lista_vacia_retorna_200(self, client, ayu_headers):
        """An empty table returns 200 and an empty list."""
        response = client.get("/cursos", headers=ayu_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    @pytest.mark.integration
    def test_pro_ve_solo_sus_cursos(self, client, db_session):
        """PRO ve solo los cursos donde es profesor."""
        pro_id = _crear_profesor(db_session)
        otro_pro_id = _crear_profesor(db_session)
        semestre_id = _crear_semestre(db_session, "S1")
        otro_semestre_id = _crear_semestre(db_session, "S2")

        curso_pro = Curso(
            id_curso=str(uuid4()),
            nombre="Mi curso",
            ref_semestre=semestre_id,
            ref_profesor=pro_id,
        )
        curso_otro = Curso(
            id_curso=str(uuid4()),
            nombre="Curso ajeno",
            ref_semestre=otro_semestre_id,
            ref_profesor=otro_pro_id,
        )
        db_session.add_all([curso_pro, curso_otro])
        db_session.flush()

        headers = _token_headers("PRO", pro_id)
        response = client.get("/cursos", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["nombre"] == "Mi curso"

    @pytest.mark.integration
    def test_ayu_ve_todos_los_cursos(self, client, db_session):
        """AYU ve todos los cursos."""
        semestre_id = _crear_semestre(db_session, "S1")

        cursos = [
            Curso(
                id_curso=str(uuid4()),
                nombre="Curso A",
                ref_semestre=semestre_id,
                ref_profesor=None,
            ),
            Curso(
                id_curso=str(uuid4()),
                nombre="Curso B",
                ref_semestre=semestre_id,
                ref_profesor=None,
            ),
        ]
        db_session.add_all(cursos)
        db_session.flush()

        headers = _token_headers("AYU", str(USER_IDS["AYU"]))
        response = client.get("/cursos", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_401_sin_token(self, client_unit):
        """Request without token returns 401."""
        response = client_unit.get("/cursos")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ───────────────────────────────
# GET /cursos/mis-cursos
# ───────────────────────────────


class TestMisCursos:
    """GET /cursos/mis-cursos scenarios."""

    @pytest.mark.integration
    def test_est_ve_sus_cursos(self, client, db_session):
        """EST inscrito en cursos retorna su lista."""
        estudiante_id = _crear_estudiante(db_session)
        semestre_id = _crear_semestre(db_session, "2026-1")

        curso_id = str(uuid4())
        db_session.add(
            Curso(
                id_curso=curso_id,
                nombre="Matemáticas",
                ref_semestre=semestre_id,
                ref_profesor=None,
            )
        )
        db_session.add(
            GrupoEstudiante(ref_grupo=curso_id, ref_estudiante=estudiante_id)
        )
        db_session.flush()

        headers = _token_headers("EST", estudiante_id)
        response = client.get("/cursos/mis-cursos", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["id_curso"] == curso_id
        assert data[0]["nombre"] == "Matemáticas"
        assert data[0]["semestre_nombre"] == "2026-1"

    @pytest.mark.integration
    def test_est_sin_cursos_retorna_vacio(self, client, db_session):
        """EST sin inscripciones retorna lista vacía."""
        estudiante_id = _crear_estudiante(db_session)
        headers = _token_headers("EST", estudiante_id)

        response = client.get("/cursos/mis-cursos", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    @pytest.mark.integration
    def test_est_sin_registro_retorna_404(self, client, db_session):
        """EST autenticado pero sin registro Estudiante → 404."""
        fake_id = str(uuid4())
        headers = _token_headers("EST", fake_id)
        response = client.get("/cursos/mis-cursos", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_pro_no_puede_ver_mis_cursos(self, client_unit, pro_headers):
        """Rol no EST → 403."""
        response = client_unit.get("/cursos/mis-cursos", headers=pro_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ───────────────────────────────
# POST /cursos
# ───────────────────────────────


class TestCrearCurso:
    """POST /cursos scenarios."""

    @pytest.mark.integration
    def test_happy_path_pro(self, client, db_session):
        """PRO crea curso con ref_profesor desde JWT → 201."""
        pro_id = _crear_profesor(db_session)
        semestre_id = _crear_semestre(db_session, "Semestre 2026-1")

        payload = {"nombre": "Matemáticas", "ref_semestre": semestre_id}
        headers = _token_headers("PRO", pro_id)

        response = client.post("/cursos", json=payload, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nombre"] == payload["nombre"]
        assert data["ref_semestre"] == semestre_id
        assert data["ref_profesor"] == pro_id
        assert "id_curso" in data
        assert "semestre_nombre" in data

    @pytest.mark.integration
    def test_happy_path_ayu(self, client, db_session):
        """AYU crea curso con ref_profesor explícito → 201."""
        pro_id = _crear_profesor(db_session)
        semestre_id = _crear_semestre(db_session, "Semestre 2026-1")

        payload = {
            "nombre": "Física",
            "ref_semestre": semestre_id,
            "ref_profesor": pro_id,
        }
        headers = _token_headers("AYU", str(USER_IDS["AYU"]))

        response = client.post("/cursos", json=payload, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nombre"] == payload["nombre"]
        assert data["ref_profesor"] == pro_id

    def test_403_rol_no_autorizado_est(self, client_unit, estudiante_headers):
        """EST no puede crear cursos → 403."""
        payload = {"nombre": "Curso", "ref_semestre": str(uuid4())}
        response = client_unit.post("/cursos", json=payload, headers=estudiante_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_401_sin_token(self, client_unit):
        """Request without token returns 401."""
        payload = {"nombre": "Curso", "ref_semestre": str(uuid4())}
        response = client_unit.post("/cursos", json=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_422_pro_con_ref_profesor_distinto(self, client_unit, pro_headers):
        """PRO enviando ref_profesor distinto a su JWT → 422."""
        payload = {
            "nombre": "Curso",
            "ref_semestre": str(uuid4()),
            "ref_profesor": str(uuid4()),
        }
        response = client_unit.post("/cursos", json=payload, headers=pro_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_422_nombre_vacio(self, client_unit, pro_headers):
        """Nombre vacío o whitespace returns 422."""
        payload = {"nombre": "", "ref_semestre": str(uuid4())}
        response = client_unit.post("/cursos", json=payload, headers=pro_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("uuid_field", ["ref_semestre", "ref_profesor"])
    def test_422_uuid_invalido(self, client_unit, pro_headers, uuid_field):
        """UUID mal formado returns 422."""
        payload = {
            "nombre": "Curso",
            "ref_semestre": str(uuid4()),
            uuid_field: "no-es-uuid",
        }
        response = client_unit.post("/cursos", json=payload, headers=pro_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    def test_404_semestre_no_existe(self, client, db_session, pro_headers):
        """ref_semestre inexistente → 404."""
        payload = {"nombre": "Curso", "ref_semestre": str(uuid4())}
        response = client.post("/cursos", json=payload, headers=pro_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.integration
    def test_422_ayu_sin_ref_profesor(self, client, db_session):
        """AYU sin ref_profesor en body → 422."""
        semestre_id = _crear_semestre(db_session, "S1")

        payload = {"nombre": "Curso", "ref_semestre": semestre_id}
        headers = _token_headers("AYU", str(USER_IDS["AYU"]))
        response = client.post("/cursos", json=payload, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    def test_422_ayu_ref_profesor_invalido(self, client, db_session):
        """AYU con ref_profesor que no existe o no es PRO → 422."""
        semestre_id = _crear_semestre(db_session, "S1")

        payload = {
            "nombre": "Curso",
            "ref_semestre": semestre_id,
            "ref_profesor": str(uuid4()),
        }
        headers = _token_headers("AYU", str(USER_IDS["AYU"]))
        response = client.post("/cursos", json=payload, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ───────────────────────────────
# GET /cursos/{id}
# ───────────────────────────────


class TestObtenerCurso:
    """GET /cursos/{id} scenarios."""

    @pytest.mark.integration
    def test_happy_path(self, client, db_session):
        """Curso existente retorna detalle con nombre del semestre."""
        semestre_id = _crear_semestre(db_session, "Semestre 2026-1")
        curso_id = str(uuid4())
        db_session.add(
            Curso(
                id_curso=curso_id,
                nombre="Matemáticas",
                ref_semestre=semestre_id,
                ref_profesor=None,
            )
        )
        db_session.flush()

        headers = _token_headers("PRO", str(USER_IDS["PRO"]))
        response = client.get(f"/cursos/{curso_id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nombre"] == "Matemáticas"
        assert data["semestre_nombre"] == "Semestre 2026-1"

    @pytest.mark.integration
    def test_404_no_encontrado(self, client, db_session, pro_headers):
        """ID inexistente → 404."""
        response = client.get(f"/cursos/{uuid4()}", headers=pro_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_401_sin_token(self, client_unit):
        """Request without token returns 401."""
        response = client_unit.get(f"/cursos/{uuid4()}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ───────────────────────────────
# PUT /cursos/{id}
# ───────────────────────────────


class TestActualizarCurso:
    """PUT /cursos/{id} scenarios."""

    @pytest.mark.integration
    def test_happy_path_adm(self, client, db_session):
        """ADM actualiza curso → 200."""
        semestre_id = _crear_semestre(db_session, "S1")
        curso_id = str(uuid4())
        db_session.add(
            Curso(
                id_curso=curso_id,
                nombre="Original",
                ref_semestre=semestre_id,
                ref_profesor=None,
            )
        )
        db_session.flush()

        headers = _token_headers("ADM", str(USER_IDS["ADM"]))
        response = client.put(
            f"/cursos/{curso_id}", json={"nombre": "Actualizado"}, headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nombre"] == "Actualizado"

    def test_403_no_adm(self, client_unit, pro_headers):
        """Rol no ADM → 403."""
        response = client_unit.put(
            f"/cursos/{uuid4()}", json={"nombre": "x"}, headers=pro_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.integration
    def test_404_no_encontrado(self, client, db_session):
        """ID inexistente → 404."""
        headers = _token_headers("ADM", str(USER_IDS["ADM"]))
        response = client.put(
            f"/cursos/{uuid4()}", json={"nombre": "x"}, headers=headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ───────────────────────────────
# DELETE /cursos/{id}
# ───────────────────────────────


class TestEliminarCurso:
    """DELETE /cursos/{id} scenarios."""

    @pytest.mark.integration
    def test_happy_path_adm(self, client, db_session):
        """ADM elimina curso → 204."""
        semestre_id = _crear_semestre(db_session, "S1")
        curso_id = str(uuid4())
        db_session.add(
            Curso(
                id_curso=curso_id,
                nombre="Borrar",
                ref_semestre=semestre_id,
                ref_profesor=None,
            )
        )
        db_session.flush()

        headers = _token_headers("ADM", str(USER_IDS["ADM"]))
        response = client.delete(f"/cursos/{curso_id}", headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_403_no_adm(self, client_unit, ayu_headers):
        """Rol no ADM → 403."""
        response = client_unit.delete(f"/cursos/{uuid4()}", headers=ayu_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.integration
    def test_404_no_encontrado(self, client, db_session):
        """ID inexistente → 404."""
        headers = _token_headers("ADM", str(USER_IDS["ADM"]))
        response = client.delete(f"/cursos/{uuid4()}", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
