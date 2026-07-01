from datetime import datetime, timedelta
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import status

from auth.dependencies import get_current_user, get_role_db
from auth.jwt_handler import crear_token_jwt
from main import app
from models.archivo_impresion import ArchivoImpresion
from models.articulo import Articulo
from models.impresion import Impresion
from models.usuario import Usuario
from utils.files import validar_extension

# ==========================================
# TESTS UNITARIOS: FUNCIÓN PURA
# ==========================================

USER_IDS = {
    "SOL": "11111111-1111-1111-1111-111111111111",
    "EST": "22222222-2222-2222-2222-222222222222",
    "AYU": "33333333-3333-3333-3333-333333333333",
    "PRO": "44444444-4444-4444-4444-444444444444",
    "ADM": "55555555-5555-5555-5555-555555555555",
}


def token_headers(rol: str, user_id: str | None = None) -> dict:
    sub = user_id if user_id else USER_IDS.get(rol, "test_user@test.com")
    token = crear_token_jwt(
        data={"sub": sub, "role": rol},
        expires_delta=timedelta(hours=24),
    )
    return {"Authorization": f"Bearer {token}"}


def test_validar_extension_permitidas():
    assert validar_extension("modelo.stl") is True
    assert validar_extension("figura.obj") is True
    assert validar_extension("pieza.gcode") is True


def test_validar_extension_no_permitidas():
    assert validar_extension("script.exe") is False
    assert validar_extension("documento.txt") is False
    assert validar_extension("factura.pdf") is False


def test_validar_extension_sin_extension():
    assert validar_extension("archivo_sin_punto") is False


def test_validar_extension_case_insensitive():
    assert validar_extension("MODELO.STL") is True
    assert validar_extension("figura.Stl") is True


def test_validar_extension_vacia():
    assert validar_extension("") is False


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("modelo.stl", True),
        ("figura.obj", True),
        ("pieza.gcode", True),
        ("script.exe", False),
        ("", False),
    ],
)
def test_validar_extension(filename, expected):
    assert validar_extension(filename) is expected


# ==========================================
# TESTS DE INTEGRACIÓN (Mocking de Session)
# ==========================================


@pytest.fixture
def mock_db():
    session = MagicMock()
    yield session


@pytest.fixture
def seed_est(db_session):
    import uuid

    from auth.hasher import hash_password
    from models.articulo import Articulo
    from models.usuario import Usuario

    user_id = str(uuid.uuid4())
    art_id = str(uuid.uuid4())[:8]

    usuario = Usuario(
        id_usuario=user_id,
        nombre="Test",
        apellido="Estudiante",
        email=f"est-{user_id[:8]}@test.com",
        rol="EST",
        estado=True,
        password_hash=hash_password("test123"),
    )
    db_session.add(usuario)
    articulo = Articulo(
        id_articulo=art_id,
        nombre_articulo="Test",
        stock_actual=10,
        stock_minimo=1,
        alerta_stock=False,
    )
    db_session.add(articulo)
    db_session.flush()
    yield user_id, art_id


@pytest.fixture
def seed_pro(db_session):
    import uuid

    from auth.hasher import hash_password
    from models.articulo import Articulo
    from models.usuario import Usuario

    user_id = str(uuid.uuid4())
    art_id = str(uuid.uuid4())[:8]

    usuario = Usuario(
        id_usuario=user_id,
        nombre="Test",
        apellido="Profe",
        email=f"pro-{user_id[:8]}@test.com",
        rol="PRO",
        estado=True,
        password_hash=hash_password("test123"),
    )
    db_session.add(usuario)
    articulo = Articulo(
        id_articulo=art_id,
        nombre_articulo="Test",
        stock_actual=10,
        stock_minimo=1,
        alerta_stock=False,
    )
    db_session.add(articulo)
    db_session.flush()
    yield user_id, art_id


@pytest.fixture
def mock_auth_est():
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "user-123",
        "role": "EST",
    }
    yield
    app.dependency_overrides.pop(get_current_user, None)


def test_happy_path_un_archivo(mock_db, client_unit, mock_auth_est):
    app.dependency_overrides[get_role_db] = lambda: mock_db

    file_content = b"fake-bytea-content-for-stl"

    response = client_unit.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
        files=[("archivos", ("test.stl", file_content, "application/octet-stream"))],
    )

    assert response.status_code == 201
    assert response.json()["estado_impresion"] == "Pendiente"
    assert mock_db.add.call_count == 2
    mock_db.commit.assert_called_once()

    args_archivo = mock_db.add.call_args_list[1][0][0]
    assert args_archivo.contenido == file_content


def test_archivos_multiples(mock_db, client_unit, mock_auth_est):
    app.dependency_overrides[get_role_db] = lambda: mock_db
    response = client_unit.post(
        "/impresiones",
        data={"cantidad": 2, "ref_articulo": "art-002"},
        files=[
            ("archivos", ("uno.stl", b"content1", "application/octet-stream")),
            ("archivos", ("dos.obj", b"content2", "application/octet-stream")),
        ],
    )
    assert response.status_code == 201
    assert response.json()["archivos_subidos"] == 2
    assert mock_db.add.call_count == 3


def test_extension_no_permitida(mock_db, client_unit, mock_auth_est):
    app.dependency_overrides[get_role_db] = lambda: mock_db
    response = client_unit.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
        files=[("archivos", ("foto.png", b"content", "image/png"))],
    )
    assert response.status_code == 422
    mock_db.add.assert_not_called()


def test_rollback_falla_guardado_archivos(mock_db, client_unit, mock_auth_est):
    app.dependency_overrides[get_role_db] = lambda: mock_db

    mock_db.add.side_effect = [None, Exception("Error simulado de base de datos")]

    response = client_unit.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
        files=[("archivos", ("test.stl", b"content", "application/octet-stream"))],
    )

    assert response.status_code == 500
    mock_db.rollback.assert_called_once()
    mock_db.commit.assert_not_called()


@pytest.mark.integration
def test_crear_impresion_un_archivo(db_session, client, seed_est):
    user_id, art_id = seed_est
    headers = token_headers("EST", user_id=user_id)
    archivos = [
        ("archivos", ("test.stl", b"contenido_binario_stl", "application/octet-stream"))
    ]
    data = {"cantidad": 2, "ref_articulo": art_id}

    response = client.post("/impresiones", headers=headers, data=data, files=archivos)

    assert response.status_code == 201
    json_data = response.json()
    assert json_data["estado_impresion"] == "Pendiente"
    assert json_data["cantidad"] == 2


@pytest.mark.integration
def test_crear_impresion_multiples_archivos(db_session, client, seed_est):
    user_id, art_id = seed_est
    headers = token_headers("EST", user_id=user_id)
    archivos = [
        ("archivos", ("modelo1.stl", b"contenido1", "application/octet-stream")),
        ("archivos", ("modelo2.obj", b"contenido2", "application/octet-stream")),
    ]
    data = {"cantidad": 1, "ref_articulo": art_id}
    response = client.post("/impresiones", headers=headers, data=data, files=archivos)
    assert response.status_code == 201


@pytest.mark.integration
def test_crear_impresion_extension_no_permitida(db_session, client):
    headers = token_headers("EST")
    archivos = [("archivos", ("foto.png", b"contenido", "image/png"))]
    data = {"cantidad": 1, "ref_articulo": 3}
    response = client.post("/impresiones", headers=headers, data=data, files=archivos)

    assert response.status_code == 422
    assert "Extensión de archivo no permitida" in response.json()["detail"]


def test_crear_impresion_sin_archivos(client_unit):
    headers = token_headers("EST")
    data = {"cantidad": 1, "ref_articulo": 5}

    response = client_unit.post("/impresiones", headers=headers, data=data)
    assert response.status_code == 422


def test_crear_impresiones_sin_token(client_unit):
    archivos = [
        ("archivos", ("modelo1.stl", b"contenido1", "application/octet-stream"))
    ]
    data = {"cantidad": 1, "ref_articulo": 5}

    response = client_unit.post("/impresiones", data=data, files=archivos)
    assert response.status_code == 401


@pytest.mark.parametrize("rol_invalido", ["ADM", "AYU", "PRO"])
def test_crear_impresion_roles_no_permitidos(rol_invalido, client_unit):
    headers = token_headers(rol_invalido)
    archivos = [("archivos", ("test.stl", b"data", "application/octet-stream"))]
    data = {"cantidad": 1, "ref_articulo": 5}

    response = client_unit.post(
        "/impresiones", headers=headers, data=data, files=archivos
    )
    assert response.status_code == 403


@pytest.mark.integration
def test_crear_impresion_coincidencia_byte_a_byte(db_session, client, seed_est):
    user_id, art_id = seed_est
    headers = token_headers("EST", user_id=user_id)
    contenido_original = b"\x01\x02\x03\x04_string_complejo_STL"
    archivos = [
        ("archivos", ("test.gcode", contenido_original, "application/octet-stream"))
    ]
    data = {"cantidad": 1, "ref_articulo": art_id}

    response = client.post("/impresiones", headers=headers, data=data, files=archivos)
    assert response.status_code == 201


# ==========================================
# NUEVOS TESTS: /impresiones (roles: SOL, EST)
# ==========================================


def test_impresiones_sin_archivos(mock_db, client_unit, mock_auth_est):
    app.dependency_overrides[get_role_db] = lambda: mock_db
    response = client_unit.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
    )
    assert response.status_code == 422
    mock_db.add.assert_not_called()


def test_impresiones_sin_token(mock_db, client_unit):
    app.dependency_overrides[get_role_db] = lambda: mock_db
    response = client_unit.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
        files=[("archivos", ("test.stl", b"data", "application/octet-stream"))],
    )
    assert response.status_code == 401


@pytest.mark.parametrize("rol_invalido", ["PRO", "ADM", "AYU"])
def test_impresiones_rol_no_permitido(rol_invalido, mock_db, client_unit):
    app.dependency_overrides[get_role_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "user-123",
        "role": rol_invalido,
    }
    try:
        response = client_unit.post(
            "/impresiones",
            data={"cantidad": 1, "ref_articulo": "art-001"},
            files=[("archivos", ("test.stl", b"data", "application/octet-stream"))],
        )
        assert response.status_code == 403
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_impresiones_extension_no_permitida(mock_db, client_unit, mock_auth_est):
    app.dependency_overrides[get_role_db] = lambda: mock_db
    response = client_unit.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
        files=[("archivos", ("documento.pdf", b"content", "application/pdf"))],
    )
    assert response.status_code == 422
    mock_db.add.assert_not_called()


def test_impresiones_archivos_mixtos(mock_db, client_unit, mock_auth_est):
    app.dependency_overrides[get_role_db] = lambda: mock_db
    response = client_unit.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
        files=[
            ("archivos", ("valido.stl", b"content", "application/octet-stream")),
            ("archivos", ("invalido.exe", b"content", "application/octet-stream")),
        ],
    )
    assert response.status_code == 422
    mock_db.add.assert_not_called()


def test_impresiones_nombre_con_espacios(mock_db, client_unit, mock_auth_est):
    app.dependency_overrides[get_role_db] = lambda: mock_db
    response = client_unit.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
        files=[
            ("archivos", ("mi modelo 3d.stl", b"content", "application/octet-stream"))
        ],
    )
    assert response.status_code == 201


def test_impresiones_archivo_vacio(mock_db, client_unit, mock_auth_est):
    app.dependency_overrides[get_role_db] = lambda: mock_db
    response = client_unit.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
        files=[("archivos", ("vacio.stl", b"", "application/octet-stream"))],
    )
    assert response.status_code == 201
    mock_db.commit.assert_called_once()


# ==========================================
# NUEVOS TESTS: /impresiones (roles: EST, PRO)
# ==========================================


@pytest.mark.parametrize("rol_invalido", ["ADM", "AYU", "PRO"])
@pytest.mark.integration
def test_api_impresiones_rol_no_permitido(rol_invalido, db_session, client):
    headers = token_headers(rol_invalido)
    archivos = [("archivos", ("test.stl", b"data", "application/octet-stream"))]
    data = {"cantidad": 1, "ref_articulo": 5}

    response = client.post("/impresiones", headers=headers, data=data, files=archivos)
    assert response.status_code == 403


@pytest.mark.integration
def test_api_impresiones_con_rol_permitido(db_session, client, seed_est):
    user_id, art_id = seed_est
    headers = token_headers("EST", user_id=user_id)
    archivos = [("archivos", ("test.stl", b"data", "application/octet-stream"))]
    data = {"cantidad": 1, "ref_articulo": art_id}

    response = client.post("/impresiones", headers=headers, data=data, files=archivos)
    assert response.status_code == 201


@pytest.mark.integration
def test_api_impresiones_archivos_mixtos(db_session, client):
    headers = token_headers("EST")
    archivos = [
        ("archivos", ("valido.stl", b"content1", "application/octet-stream")),
        ("archivos", ("malo.exe", b"content2", "application/octet-stream")),
    ]
    data = {"cantidad": 1, "ref_articulo": 5}

    response = client.post("/impresiones", headers=headers, data=data, files=archivos)
    assert response.status_code == 422


@pytest.mark.integration
def test_api_impresiones_sin_archivos(db_session, client):
    headers = token_headers("EST")
    data = {"cantidad": 1, "ref_articulo": 5}

    response = client.post("/impresiones", headers=headers, data=data)
    assert response.status_code == 422


@pytest.mark.integration
def test_api_impresiones_archivo_vacio(db_session, client, seed_est):
    user_id, art_id = seed_est
    headers = token_headers("EST", user_id=user_id)
    archivos = [("archivos", ("vacio.gcode", b"", "application/octet-stream"))]
    data = {"cantidad": 1, "ref_articulo": art_id}

    response = client.post("/impresiones", headers=headers, data=data, files=archivos)
    assert response.status_code == 201


@pytest.mark.integration
def test_api_impresiones_extension_case_insensitive(db_session, client, seed_est):
    user_id, art_id = seed_est
    headers = token_headers("EST", user_id=user_id)
    archivos = [("archivos", ("MODELO.STL", b"content", "application/octet-stream"))]
    data = {"cantidad": 1, "ref_articulo": art_id}

    response = client.post("/impresiones", headers=headers, data=data, files=archivos)
    assert response.status_code == 201


def _crear_usuario(session, user_id: str, rol: str = "EST") -> str:
    session.add(
        Usuario(
            id_usuario=user_id,
            nombre="Test",
            apellido="User",
            email=f"{user_id[:8]}@test.com",
            correo=f"{user_id[:8]}@test.com",
            rol=rol,
            password_hash="x",
        )
    )
    session.flush()
    return user_id


def _crear_articulo(session) -> str:
    art_id = str(uuid4())[:8]
    session.add(
        Articulo(
            id_articulo=art_id,
            nombre_articulo="Test",
            stock_actual=10,
            stock_minimo=1,
            alerta_stock=False,
        )
    )
    session.flush()
    return art_id


class TestMisImpresiones:
    """GET /impresiones/mias scenarios."""

    @pytest.mark.integration
    def test_estudiante_ve_su_historial_ordenado(
        self, client, db_session, estudiante_headers
    ):
        user_id = "test_user@test.com"
        _crear_usuario(db_session, user_id, "EST")
        art_id = _crear_articulo(db_session)

        imp1_id = str(uuid4())
        imp2_id = str(uuid4())
        db_session.add(
            Impresion(
                id_impresion=imp1_id,
                ref_usuario=user_id,
                ref_articulo=art_id,
                cantidad=1,
                fecha_impresion=datetime(2025, 6, 14, 10, 0, 0),
                estado_impresion="Pendiente",
            )
        )
        db_session.add(
            Impresion(
                id_impresion=imp2_id,
                ref_usuario=user_id,
                ref_articulo=art_id,
                cantidad=1,
                fecha_impresion=datetime(2025, 6, 15, 12, 0, 0),
                estado_impresion="Completada",
            )
        )
        db_session.add(
            ArchivoImpresion(
                id_archivo=str(uuid4()),
                ref_impresion=imp1_id,
                nombre_archivo="modelo1.stl",
                contenido=b"data1",
            )
        )
        db_session.add(
            ArchivoImpresion(
                id_archivo=str(uuid4()),
                ref_impresion=imp2_id,
                nombre_archivo="modelo2.obj",
                contenido=b"data2",
            )
        )
        db_session.flush()

        response = client.get("/impresiones/mias", headers=estudiante_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["id_impresion"] == imp2_id
        assert data[0]["estado"] == "Completada"
        assert data[0]["nombre_archivo"] == "modelo2.obj"
        assert data[1]["id_impresion"] == imp1_id
        assert data[1]["estado"] == "Pendiente"
        assert data[1]["nombre_archivo"] == "modelo1.stl"

    @pytest.mark.integration
    def test_solicitante_ve_su_historial(self, client, db_session):
        user_id = str(uuid4())
        _crear_usuario(db_session, user_id, "SOL")
        art_id = _crear_articulo(db_session)

        imp_id = str(uuid4())
        db_session.add(
            Impresion(
                id_impresion=imp_id,
                ref_usuario=user_id,
                ref_articulo=art_id,
                cantidad=1,
                fecha_impresion=datetime(2025, 6, 15, 12, 0, 0),
                estado_impresion="Rechazada",
            )
        )
        db_session.add(
            ArchivoImpresion(
                id_archivo=str(uuid4()),
                ref_impresion=imp_id,
                nombre_archivo="pieza.gcode",
                contenido=b"data",
            )
        )
        db_session.flush()

        headers = token_headers("SOL", user_id=user_id)
        response = client.get("/impresiones/mias", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["id_impresion"] == imp_id
        assert data[0]["estado"] == "Rechazada"
        assert data[0]["nombre_archivo"] == "pieza.gcode"

    @pytest.mark.integration
    def test_historial_vacio_retorna_lista_vacia(self, client, estudiante_headers):
        response = client.get("/impresiones/mias", headers=estudiante_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    @pytest.mark.parametrize("rol_no_autorizado", ["PRO", "ADM", "AYU"])
    def test_rol_no_autorizado_recibe_403(self, rol_no_autorizado, client_unit):
        headers = token_headers(rol_no_autorizado)
        response = client_unit.get("/impresiones/mias", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_ayudante_aprueba_impresion_con_stock_exitoso(client, db_session):
        solicitud_id = 1

        response = await client.put(
            f"/api/impresiones/{solicitud_id}/estado",
            json={"estado": "En Impresion"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["estado"] == "En Impresion"

    @pytest.mark.asyncio
    async def test_ayudante_aprueba_impresion_con_stock_insuficiente(client, db_session):
        solicitud_id_sin_stock = 999

        response = await client.put(
            f"/api/impresiones/{solicitud_id_sin_stock}/estado",
            json={"estado": "En Impresion"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Stock insuficiente de filamnto"
