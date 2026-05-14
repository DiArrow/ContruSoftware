#!/bin/bash
# Moverse a la raíz del proyecto (un directorio hacia atrás desde test_linters)
cd "$(dirname "$0")/.." || exit 1

echo "=== [1/4] Ejecutando Linters Frontend (ESLint + Prettier) ==="
cd frontend
npm install
npx eslint . --fix
npx prettier --write .
cd ..

echo "=== [2/4] Creando Entorno Virtual Temporal de Python ==="
# Creamos el entorno dentro de test_linters para aislarlo
python3 -m venv test_linters/.temp_venv
source test_linters/.temp_venv/bin/activate

# Instalamos las dependencias necesarias en modo silencioso
pip install --quiet ruff sqlfluff yamllint

echo "=== [3/4] Ejecutando Linters Python, SQL y YAML ==="
echo "--> Ruff (Backend)"
ruff check backend/ --fix
ruff format backend/

echo "--> SQLFluff (Base de Datos)"
sqlfluff fix db/ --dialect postgres

echo "--> Yamllint (Infraestructura)"
yamllint .

echo "--> Destruyendo Entorno Virtual..."
deactivate
rm -rf test_linters/.temp_venv

echo "=== [4/4] Ejecutando Hadolint (Docker) ==="
# Busca todos los archivos llamados Dockerfile en el proyecto y los evalúa
find . -name "Dockerfile" -print0 | while IFS= read -r -d '' file; do
    echo "Linting: $file"
    docker run --rm -i hadolint/hadolint <"$file"
done

echo "=== ¡Proceso Completado! ==="
