import pytest
from unittest.mock import MagicMock
from routers.impresiones import validar_extension

# ==========================================
# TESTS UNITARIOS: FUNCIÓN PURA
# ==========================================

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

# ==========================================
# TESTS DE INTEGRACIÓN (Mocking de Session)
# ==========================================
# Nota: Ajusta las importaciones de TestClient y app según tu proyecto

from fastapi.testclient import TestClient
from main import app 
from database import get_db
from auth.dependencies import requiere_rol

client = TestClient(app)

# Simulamos que un estudiante inició sesión
def override_requiere_rol():
    return {"sub": "user-123", "role": "EST"}

app.dependency_overrides[requiere_rol(["SOL", "EST"])] = override_requiere_rol

@pytest.fixture
def mock_db():
    # Creamos un Mock de la sesión de base de datos
    session = MagicMock()
    yield session

def test_happy_path_un_archivo(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    
    file_content = b"fake-bytea-content-for-stl"
    
    response = client.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
        files=[("archivos", ("test.stl", file_content, "application/octet-stream"))]
    )
    
    assert response.status_code == 201
    assert response.json()["estado"] == "Pendiente"
    # Verificamos que se llamó a db.add dos veces (Impresion y ArchivoImpresion)
    assert mock_db.add.call_count == 2
    mock_db.commit.assert_called_once()
    
    # Test del Binario: Verificamos que el archivo se guardó byte a byte correctamente
    args_archivo = mock_db.add.call_args_list[1][0][0]
    assert args_archivo.contenido == file_content

def test_archivos_multiples(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.post(
        "/impresiones",
        data={"cantidad": 2, "ref_articulo": "art-002"},
        files=[
            ("archivos", ("uno.stl", b"content1", "application/octet-stream")),
            ("archivos", ("dos.obj", b"content2", "application/octet-stream"))
        ]
    )
    assert response.status_code == 201
    assert response.json()["archivos_subidos"] == 2
    # 1 modelo Impresion + 2 modelos ArchivoImpresion = 3 llamadas
    assert mock_db.add.call_count == 3 

def test_extension_no_permitida(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
        files=[("archivos", ("foto.png", b"content", "image/png"))]
    )
    assert response.status_code == 422
    # Nos aseguramos de que no se guardó NADA en la BD
    mock_db.add.assert_not_called()

def test_rollback_falla_guardado_archivos(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # Simulamos que al intentar guardar el archivo en la base de datos se cae el servidor
    mock_db.add.side_effect = [None, Exception("Error simulado de base de datos")]
    
    response = client.post(
        "/impresiones",
        data={"cantidad": 1, "ref_articulo": "art-001"},
        files=[("archivos", ("test.stl", b"content", "application/octet-stream"))]
    )
    
    assert response.status_code == 500
    # Verificamos que el ROLLBACK actuó y eliminó el registro de Impresión que iba a guardar
    mock_db.rollback.assert_called_once()
    mock_db.commit.assert_not_called()