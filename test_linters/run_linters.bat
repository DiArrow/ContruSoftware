@echo off
:: Moverse a la carpeta raíz del proyecto
cd /d "%~dp0\.."

echo === [1/4] Ejecutando Linters Frontend (ESLint + Prettier) ===
cd frontend
call npm install
call npx eslint . --fix
call npx prettier --write .
cd ..

echo === [2/4] Creando Entorno Virtual Temporal de Python ===
py -m venv test_linters\.temp_venv
call test_linters\.temp_venv\Scripts\activate.bat
pip install --quiet ruff sqlfluff yamllint

echo === [3/4] Ejecutando Linters Python, SQL y YAML ===
echo --^> Ruff (Backend)
ruff check backend/ --fix
ruff format backend/

echo --^> SQLFluff (Base de Datos)
sqlfluff fix db/ --dialect postgres

echo --^> Yamllint (Infraestructura)
yamllint .

echo --^> Destruyendo Entorno Virtual...
call test_linters\.temp_venv\Scripts\deactivate.bat
rmdir /s /q test_linters\.temp_venv

echo === [4/4] Ejecutando Hadolint (Docker) ===
:: Busca recursivamente los Dockerfiles y usa Docker para evaluarlos
for /r %%i in (Dockerfile) do (
    if exist "%%i" (
        echo Linting: %%i
        type "%%i" | docker run --rm -i hadolint/hadolint
    )
)

echo === ¡Proceso Completado! ===
pause
