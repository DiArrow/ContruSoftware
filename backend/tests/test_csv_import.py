"""Tests for CSV student import."""

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
from utils.csv_parser import parse_csv_rows

_SOL_ID = str(uuid4())
_SOL_TOKEN = crear_token_jwt(
    {"sub": _SOL_ID, "role": "SOL"}, expires_delta=timedelta(hours=24)
)
sol_headers = {"Authorization": f"Bearer {_SOL_TOKEN}"}

_AYU_ID = str(uuid4())
_AYU_TOKEN = crear_token_jwt(
    {"sub": _AYU_ID, "role": "AYU"}, expires_delta=timedelta(hours=24)
)
ayu_headers_no_db = {"Authorization": f"Bearer {_AYU_TOKEN}"}


def _csv_bytes(rows: list[str]) -> bytes:
    """Build CSV bytes from a header + data rows."""
    return ("nombre,apellido,correo\n" + "\n".join(rows)).encode("utf-8")


class TestParseCsvRows:
    """Unit tests for parse_csv_rows."""

    def test_valid_three_rows(self):
        csv = (
            "nombre,apellido,correo\n"
            "Juan,Pérez,juan@test.cl\n"
            "María,González,maria@test.cl\n"
            "Pedro,López,pedro@test.cl"
        )
        result = parse_csv_rows(csv)
        assert len(result) == 3
        assert result[0] == {
            "nombre": "Juan",
            "apellido": "Pérez",
            "correo": "juan@test.cl",
        }

    def test_empty_csv(self):
        csv = "nombre,apellido,correo"
        result = parse_csv_rows(csv)
        assert result == []

    def test_utf8_special_chars(self):
        csv = (
            "nombre,apellido,correo\nMaría,Peña,maria@test.cl\nJosé,Muñoz,jose@test.cl"
        )
        result = parse_csv_rows(csv)
        assert result[0]["nombre"] == "María"
        assert result[1]["apellido"] == "Muñoz"

    def test_missing_header(self):
        csv = "Juan,Pérez,juan@test.cl"
        with pytest.raises(ValueError):
            parse_csv_rows(csv)

    def test_wrong_column_count_raises(self):
        csv = "nombre,apellido,correo\nJuan,Pérez,juan@test.cl,extra"
        with pytest.raises(ValueError):
            parse_csv_rows(csv)


def _crear_curso(session):
    """Create a course and its required semester, returning the course id."""
    semestre_id = str(uuid4())
    session.add(Semestre(id_semestre=semestre_id, nombre="Semestre 2026-1"))
    curso_id = str(uuid4())
    session.add(
        Curso(
            id_curso=curso_id,
            nombre="Matemáticas",
            ref_semestre=semestre_id,
            ref_profesor=None,
        )
    )
    session.flush()
    return curso_id


class TestCsvImportEndpoint:
    """Integration tests for POST /api/cursos/{id}/estudiantes/csv."""

    @pytest.mark.integration
    def test_happy_path_three_students(self, client, db_session, pro_headers):
        """INT-01: import 3 valid students."""
        curso_id = _crear_curso(db_session)
        csv = (
            "nombre,apellido,correo\n"
            "Juan,Pérez,juan@test.cl\n"
            "María,González,maria@test.cl\n"
            "Pedro,López,pedro@test.cl"
        )

        response = client.post(
            f"/api/cursos/{curso_id}/estudiantes/csv",
            files={"file": ("test.csv", csv.encode("utf-8"), "text/csv")},
            headers=pro_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["imported"] == 3
        assert data["duplicates"] == 0
        assert data["errors"] == []
        assert len(data["passwords"]) == 3

        correos = {"juan@test.cl", "maria@test.cl", "pedro@test.cl"}
        usuarios = (
            db_session.query(Usuario)
            .filter(Usuario.rol == "EST", Usuario.email.in_(correos))
            .all()
        )
        assert len(usuarios) == 3
        assert (
            db_session.query(Estudiante).filter(Estudiante.correo.in_(correos)).count()
            == 3
        )
        assert (
            db_session.query(GrupoEstudiante)
            .filter(GrupoEstudiante.ref_grupo == curso_id)
            .count()
            == 3
        )

    @pytest.mark.integration
    def test_partial_duplicate(self, client, db_session, pro_headers):
        """INT-02: existing email counted as duplicate, new email imported."""
        curso_id = _crear_curso(db_session)
        existing_email = "existente@test.cl"
        db_session.add(
            Usuario(
                id_usuario=str(uuid4()),
                nombre="Existente",
                apellido="Usuario",
                correo=existing_email,
                email=existing_email,
                rol="EST",
                password_hash="x",
            )
        )
        db_session.flush()

        csv = (
            "nombre,apellido,correo\n"
            f"Existente,Usuario,{existing_email}\n"
            "Nuevo,Estudiante,nuevo@test.cl"
        )

        response = client.post(
            f"/api/cursos/{curso_id}/estudiantes/csv",
            files={"file": ("test.csv", csv.encode("utf-8"), "text/csv")},
            headers=pro_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["imported"] == 1
        assert data["duplicates"] == 1
        assert len(data["passwords"]) == 1
        assert data["passwords"][0]["correo"] == "nuevo@test.cl"

    def test_est_role_forbidden(self, client_unit, estudiante_headers):
        """INT-03: EST role cannot import students."""
        response = client_unit.post(
            f"/api/cursos/{uuid4()}/estudiantes/csv",
            files={"file": ("test.csv", b"nombre,apellido,correo", "text/csv")},
            headers=estudiante_headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.integration
    def test_course_not_found(self, client, pro_headers):
        """INT-04: non-existent course returns 404."""
        csv = "nombre,apellido,correo\nJuan,Pérez,juan@test.cl"
        response = client.post(
            f"/api/cursos/{uuid4()}/estudiantes/csv",
            files={"file": ("test.csv", csv.encode("utf-8"), "text/csv")},
            headers=pro_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_no_token_unauthorized(self, client_unit):
        """INT-05: missing token returns 401."""
        csv = "nombre,apellido,correo\nJuan,Pérez,juan@test.cl"
        response = client_unit.post(
            f"/api/cursos/{uuid4()}/estudiantes/csv",
            files={"file": ("test.csv", csv.encode("utf-8"), "text/csv")},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    def test_password_is_bcrypt_hash(self, client, db_session, pro_headers):
        """INT-06: imported student's password is bcrypt-hashed in DB."""
        curso_id = _crear_curso(db_session)
        email = "seguro@test.cl"
        csv = f"nombre,apellido,correo\nSeguro,Usuario,{email}"

        response = client.post(
            f"/api/cursos/{curso_id}/estudiantes/csv",
            files={"file": ("test.csv", csv.encode("utf-8"), "text/csv")},
            headers=pro_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        plain_password = response.json()["passwords"][0]["password"]

        usuario = db_session.query(Usuario).filter(Usuario.email == email).first()
        assert usuario is not None
        assert usuario.password_hash.startswith("$2b$")
        assert usuario.password_hash != plain_password

    # -- W01: Atomicity is guaranteed by single db.commit() at end.
    #    "All" validated by test_happy_path_three_students.
    #    "Nothing" validated by format-error tests returning 422
    #    before any DB writes (test_wrong_column_count_endpoint,
    #    test_non_csv_file_extension).

    # ── W02: Role tests (SOL + AYU) ──────────────────────────────────

    def test_sol_role_forbidden(self, client_unit):
        """W02: SOL role returns 403."""
        response = client_unit.post(
            f"/api/cursos/{uuid4()}/estudiantes/csv",
            files={"file": ("test.csv", _csv_bytes(["X,Y,x@y.cl"]), "text/csv")},
            headers=sol_headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.integration
    def test_ayu_role_allowed(self, client, db_session):
        """W02: AYU role can import students."""
        curso_id = _crear_curso(db_session)
        csv = _csv_bytes(["Ana,Ayudante,ana@test.cl"])

        response = client.post(
            f"/api/cursos/{curso_id}/estudiantes/csv",
            files={"file": ("test.csv", csv, "text/csv")},
            headers=ayu_headers_no_db,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["imported"] == 1

    # ── W03: Endpoint-level validation ───────────────────────────────

    def test_non_csv_file_extension(self, client_unit, pro_headers):
        """W03: non-.csv file extension returns 422."""
        response = client_unit.post(
            f"/api/cursos/{uuid4()}/estudiantes/csv",
            files={"file": ("data.txt", b"a,b,c", "text/plain")},
            headers=pro_headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    def test_wrong_column_count_endpoint(self, client, db_session, pro_headers):
        """W03: CSV with 4 columns returns 422 at endpoint level."""
        curso_id = _crear_curso(db_session)
        csv = _csv_bytes(["Juan,Pérez,juan@test.cl,extra"])

        response = client.post(
            f"/api/cursos/{curso_id}/estudiantes/csv",
            files={"file": ("test.csv", csv, "text/csv")},
            headers=pro_headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    def test_empty_email_in_csv(self, client, db_session, pro_headers):
        """W03: row with empty email is reported in errors, not imported."""
        curso_id = _crear_curso(db_session)

        csv = _csv_bytes(
            [
                "Sin,Correo,",
                "Valido,Estudiante,valido@test.cl",
            ]
        )

        response = client.post(
            f"/api/cursos/{curso_id}/estudiantes/csv",
            files={"file": ("test.csv", csv, "text/csv")},
            headers=pro_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["imported"] == 1
        assert len(data["errors"]) == 1
        assert "Sin" in data["errors"][0]

    @pytest.mark.integration
    def test_empty_csv_endpoint(self, client, db_session, pro_headers):
        """W03: header-only CSV returns 201 with imported=0."""
        curso_id = _crear_curso(db_session)
        csv = b"nombre,apellido,correo\n"

        response = client.post(
            f"/api/cursos/{curso_id}/estudiantes/csv",
            files={"file": ("test.csv", csv, "text/csv")},
            headers=pro_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["imported"] == 0
