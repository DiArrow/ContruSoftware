from datetime import timedelta
from unittest.mock import MagicMock

import pytest

from auth.dependencies import get_current_user
from auth.jwt_handler import crear_token_jwt
from database import get_db
from main import app
from models.impresiones import validar_extension

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


def token_headers(rol: str) -> dict:
    user_id = USER_IDS.get(rol, "test_user@test.com")
    token = crear_token_jwt(
        data={"sub": user_id, "role": rol},
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
def mock_auth_est():
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "user-123",
        "role": "EST",
    }
    yield
    app.dependency_overrides.pop(get_current_user, None)


def test_happy_path_un_archivo(mock_db, client, mock_auth_est):
    app.dependency_overrides[get_db] = lambda: mock_db

    file_content = b"fake-bytea-content-for-stl"

    response = client.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
        files=[("archivos", ("test.stl", file_content, "application/octet-stream"))],
    )

    assert response.status_code == 201
    assert response.json()["estado"] == "Pendiente"
    assert mock_db.add.call_count == 2
    mock_db.commit.assert_called_once()

    args_archivo = mock_db.add.call_args_list[1][0][0]
    assert args_archivo.contenido == file_content


def test_archivos_multiples(mock_db, client, mock_auth_est):
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.post(
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


def test_extension_no_permitida(mock_db, client, mock_auth_est):
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
        files=[("archivos", ("foto.png", b"content", "image/png"))],
    )
    assert response.status_code == 422
    mock_db.add.assert_not_called()


def test_rollback_falla_guardado_archivos(mock_db, client, mock_auth_est):
    app.dependency_overrides[get_db] = lambda: mock_db

    mock_db.add.side_effect = [None, Exception("Error simulado de base de datos")]

    response = client.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
        files=[("archivos", ("test.stl", b"content", "application/octet-stream"))],
    )

    assert response.status_code == 500
    mock_db.rollback.assert_called_once()
    mock_db.commit.assert_not_called()


def test_crear_impresion_un_archivo(db_session, client):
    headers = token_headers("EST")
    archivos = [
        ("archivos", ("test.stl", b"contenido_binario_stl", "application/octet-stream"))
    ]
    data = {"cantidad": 2, "ref_articulo": "art-001"}

    response = client.post(
        "/api/impresiones/upload", headers=headers, data=data, files=archivos
    )

    assert response.status_code == 201
    json_data = response.json()
    assert json_data["estado_impresion"] == "Pendiente"
    assert json_data["cantidad"] == 2


def test_crear_impresion_multiples_archivos(db_session, client):
    headers = token_headers("EST")
    archivos = [
        ("archivos", ("modelo1.stl", b"contenido1", "application/octet-stream")),
        ("archivos", ("modelo2.obj", b"contenido2", "application/octet-stream")),
    ]
    data = {"cantidad": 1, "ref_articulo": "art-001"}
    response = client.post(
        "/api/impresiones/upload", headers=headers, data=data, files=archivos
    )
    assert response.status_code == 201


def test_crear_impresion_extension_no_permitida(db_session, client):
    headers = token_headers("EST")
    archivos = [("archivos", ("foto.png", b"contenido", "image/png"))]
    data = {"cantidad": 1, "ref_articulo": 3}
    response = client.post(
        "/api/impresiones/upload", headers=headers, data=data, files=archivos
    )

    assert response.status_code == 422
    assert "Extensión de archivo no permitida" in response.json()["detail"]


def test_crear_impresion_sin_archivos(client):
    headers = token_headers("EST")
    data = {"cantidad": 1, "ref_articulo": 5}

    response = client.post("/api/impresiones/upload", headers=headers, data=data)
    assert response.status_code == 422


def test_crear_impresiones_sin_token(client):
    archivos = [
        ("archivos", ("modelo1.stl", b"contenido1", "application/octet-stream"))
    ]
    data = {"cantidad": 1, "ref_articulo": 5}

    response = client.post("/api/impresiones/upload", data=data, files=archivos)
    assert response.status_code == 401


@pytest.mark.parametrize("rol_invalido", ["ADM", "AYU", "SOL"])
def test_crear_impresion_roles_no_permitidos(rol_invalido, client):
    headers = token_headers(rol_invalido)
    archivos = [("archivos", ("test.stl", b"data", "application/octet-stream"))]
    data = {"cantidad": 1, "ref_articulo": 5}

    response = client.post(
        "/api/impresiones/upload", headers=headers, data=data, files=archivos
    )
    assert response.status_code == 403


def test_crear_impresion_coincidencia_byte_a_byte(db_session, client):
    headers = token_headers("EST")
    contenido_original = b"\x01\x02\x03\x04_string_complejo_STL"
    archivos = [
        ("archivos", ("test.gcode", contenido_original, "application/octet-stream"))
    ]
    data = {"cantidad": 1, "ref_articulo": "art-001"}

    response = client.post(
        "/api/impresiones/upload", headers=headers, data=data, files=archivos
    )
    assert response.status_code == 201


# ==========================================
# NUEVOS TESTS: /impresiones (roles: SOL, EST)
# ==========================================


def test_impresiones_sin_archivos(mock_db, client, mock_auth_est):
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
    )
    assert response.status_code == 422
    mock_db.add.assert_not_called()


def test_impresiones_sin_token(mock_db, client):
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
        files=[("archivos", ("test.stl", b"data", "application/octet-stream"))],
    )
    assert response.status_code == 401


@pytest.mark.parametrize("rol_invalido", ["PRO", "ADM", "AYU"])
def test_impresiones_rol_no_permitido(rol_invalido, mock_db, client):
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "user-123",
        "role": rol_invalido,
    }
    try:
        response = client.post(
            "/impresiones",
            data={"cantidad": 1, "ref_articulo": "art-001"},
            files=[("archivos", ("test.stl", b"data", "application/octet-stream"))],
        )
        assert response.status_code == 403
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_impresiones_extension_no_permitida(mock_db, client, mock_auth_est):
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
        files=[("archivos", ("documento.pdf", b"content", "application/pdf"))],
    )
    assert response.status_code == 422
    mock_db.add.assert_not_called()


def test_impresiones_archivos_mixtos(mock_db, client, mock_auth_est):
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
        files=[
            ("archivos", ("valido.stl", b"content", "application/octet-stream")),
            ("archivos", ("invalido.exe", b"content", "application/octet-stream")),
        ],
    )
    assert response.status_code == 422
    mock_db.add.assert_not_called()


def test_impresiones_nombre_con_espacios(mock_db, client, mock_auth_est):
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
        files=[
            ("archivos", ("mi modelo 3d.stl", b"content", "application/octet-stream"))
        ],
    )
    assert response.status_code == 201


def test_impresiones_archivo_vacio(mock_db, client, mock_auth_est):
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
        files=[("archivos", ("vacio.stl", b"", "application/octet-stream"))],
    )
    assert response.status_code == 201
    mock_db.commit.assert_called_once()


# ==========================================
# NUEVOS TESTS: /api/impresiones/upload (roles: EST, PRO)
# ==========================================


@pytest.mark.parametrize("rol_invalido", ["ADM", "AYU", "SOL"])
def test_api_impresiones_rol_no_permitido(rol_invalido, db_session, client):
    headers = token_headers(rol_invalido)
    archivos = [("archivos", ("test.stl", b"data", "application/octet-stream"))]
    data = {"cantidad": 1, "ref_articulo": 5}

    response = client.post(
        "/api/impresiones/upload", headers=headers, data=data, files=archivos
    )
    assert response.status_code == 403


def test_api_impresiones_con_rol_permitido(db_session, client):
    headers = token_headers("EST")
    archivos = [("archivos", ("test.stl", b"data", "application/octet-stream"))]
    data = {"cantidad": 1, "ref_articulo": "art-001"}

    response = client.post(
        "/api/impresiones/upload", headers=headers, data=data, files=archivos
    )
    assert response.status_code == 201


def test_api_impresiones_archivos_mixtos(db_session, client):
    headers = token_headers("EST")
    archivos = [
        ("archivos", ("valido.stl", b"content1", "application/octet-stream")),
        ("archivos", ("malo.exe", b"content2", "application/octet-stream")),
    ]
    data = {"cantidad": 1, "ref_articulo": 5}

    response = client.post(
        "/api/impresiones/upload", headers=headers, data=data, files=archivos
    )
    assert response.status_code == 422


def test_api_impresiones_sin_archivos(db_session, client):
    headers = token_headers("EST")
    data = {"cantidad": 1, "ref_articulo": 5}

    response = client.post("/api/impresiones/upload", headers=headers, data=data)
    assert response.status_code == 422


def test_api_impresiones_archivo_vacio(db_session, client):
    headers = token_headers("EST")
    archivos = [("archivos", ("vacio.gcode", b"", "application/octet-stream"))]
    data = {"cantidad": 1, "ref_articulo": "art-001"}

    response = client.post(
        "/api/impresiones/upload", headers=headers, data=data, files=archivos
    )
    assert response.status_code == 201


def test_api_impresiones_extension_case_insensitive(db_session, client):
    headers = token_headers("PRO")
    archivos = [("archivos", ("MODELO.STL", b"content", "application/octet-stream"))]
    data = {"cantidad": 1, "ref_articulo": "art-001"}

    response = client.post(
        "/api/impresiones/upload", headers=headers, data=data, files=archivos
    )
    assert response.status_code == 201
