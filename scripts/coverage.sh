#!/usr/bin/env bash
# =============================================================================
# coverage.sh — Genera informes de cobertura para backend (pytest) y
#               frontend (vitest). Los informes HTML se guardan en docs/.
#
# Uso:
#   ./scripts/coverage.sh              # backend + frontend
#   ./scripts/coverage.sh backend      # solo backend
#   ./scripts/coverage.sh frontend     # solo frontend
#
# Requisitos:
#   - Backend:  Python 3.12+, virtualenv con requirements-dev.txt instalado
#   - Frontend: Node.js 20+, npm ci ejecutado, @vitest/coverage-v8 instalado
#   - PostgreSQL corriendo (para cobertura completa del backend; sin DB
#     solo se ejecutan tests unitarios)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCS_DIR="$REPO_ROOT/docs"
BACKEND_DIR="$REPO_ROOT/backend"
FRONTEND_DIR="$REPO_ROOT/frontend"

COV_BACKEND="$DOCS_DIR/coverage-backend"
COV_FRONTEND="$DOCS_DIR/coverage-frontend"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ── Helpers ──────────────────────────────────────────────────────────────────

_ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
_warn() { echo -e "  ${YELLOW}⚠${NC} $1"; }
_fail() { echo -e "  ${RED}✗${NC} $1"; }
_step() { echo -e "\n${BOLD}━ $1${NC}"; }

_has_postgres() {
    # Returns 0 if PostgreSQL is reachable with the configured credentials.
    local host="${POSTGRES_HOST:-localhost}"
    local port="${POSTGRES_PORT:-5432}"
    local user="${POSTGRES_APP_USER:-${POSTGRES_USER:-backend}}"
    local db="${POSTGRES_DB:-makerbox}"
    local pass="${POSTGRES_APP_PASSWORD:-${POSTGRES_PASSWORD:-}}"

    PGPASSWORD="$pass" psql -h "$host" -p "$port" -U "$user" -d "$db" -c "SELECT 1" >/dev/null 2>&1
}

TARGET="${1:-all}"

# ── Backend coverage ─────────────────────────────────────────────────────────

run_backend() {
    _step "Backend — pytest + coverage"

    mkdir -p "$COV_BACKEND"
    cd "$BACKEND_DIR"

    # Cargar variables de entorno si existe .env
    if [ -f "$REPO_ROOT/.env" ]; then
        set -a && source "$REPO_ROOT/.env" && set +a
    fi

    # Verificar si hay DB disponible para incluir tests de integración
    local marker="not integration"
    if _has_postgres; then
        marker=""
        _ok "PostgreSQL disponible — incluyendo tests de integración"
    else
        _warn "PostgreSQL no disponible — solo tests unitarios"
    fi

    local extra_args=""
    if [ -n "$marker" ]; then
        extra_args="-m '$marker'"
    fi

    echo ""

    # Ejecutar pytest con coverage (HTML + terminal)
    # shellcheck disable=SC2086
    if python -m pytest tests/ \
        --cov \
        --cov-report="html:$COV_BACKEND" \
        --cov-report=term \
        $extra_args \
        -q 2>&1; then
        _ok "Backend: informe generado en docs/coverage-backend/index.html"
    else
        _fail "Backend: algunos tests fallaron (ver salida arriba)"
        return 1
    fi
}

# ── Frontend coverage ────────────────────────────────────────────────────────

run_frontend() {
    _step "Frontend — vitest + coverage"

    mkdir -p "$COV_FRONTEND"
    cd "$FRONTEND_DIR"

    # Verificar que el provider de coverage está instalado
    if [ ! -d "node_modules/@vitest/coverage-v8" ]; then
        _warn "@vitest/coverage-v8 no instalado. Instalando..."
        npm install --save-dev @vitest/coverage-v8
    fi

    echo ""

    # Ejecutar vitest con coverage
    if npx vitest run \
        --coverage \
        --coverage.provider=v8 \
        --coverage.reporter=html \
        --coverage.reportsDirectory="$COV_FRONTEND" \
        --coverage.reporter=text \
        2>&1; then
        _ok "Frontend: informe generado en docs/coverage-frontend/index.html"
    else
        _fail "Frontend: algunos tests fallaron (ver salida arriba)"
        return 1
    fi
}

# ── Main ─────────────────────────────────────────────────────────────────────

echo -e "${BOLD}╔══════════════════════════════════════╗${NC}"
echo -e "${BOLD}║   Coverage Report — ContruSoftware  ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════╝${NC}"

mkdir -p "$DOCS_DIR"

EXIT=0

case "$TARGET" in
    all)
        run_backend || EXIT=1
        run_frontend || EXIT=1
        ;;
    backend)
        run_backend || EXIT=1
        ;;
    frontend)
        run_frontend || EXIT=1
        ;;
    *)
        echo "Uso: $0 [backend|frontend|all]"
        exit 1
        ;;
esac

echo ""
echo -e "${BOLD}Informes generados:${NC}"
[ -f "$COV_BACKEND/index.html" ] && echo "  • Backend:  $COV_BACKEND/index.html"
[ -f "$COV_FRONTEND/index.html" ] && echo "  • Frontend: $COV_FRONTEND/index.html"

if [ "$EXIT" -eq 0 ]; then
    echo -e "\n${GREEN}${BOLD}✓ Coverage completo${NC}"
else
    echo -e "\n${RED}${BOLD}✗ Coverage con errores (revisar arriba)${NC}"
fi

exit $EXIT
