#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# migrate.sh — Apply pending SQL migrations in order
# ---------------------------------------------------------------------------
# Reads DB connection from environment variables (same as backend/.env).
#
# Usage:
#   ./scripts/migrate.sh                    # apply all pending migrations
#   ./scripts/migrate.sh --dry-run          # show what would run, don't execute
#   ./scripts/migrate.sh --run 03           # apply only migration 03 and up
# ---------------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MIGRATIONS_DIR="$PROJECT_ROOT/db/migrations"

# ---- Resolve DB connection ------------------------------------------------
: "${POSTGRES_HOST:=localhost}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_DB:=makerbox}"
# Migrations require a user with DDL permissions (table owner).
# Default to POSTGRES_USER (admin) since the app user typically only has DML.
: "${MIGRATE_USER:=${POSTGRES_USER}}"
: "${MIGRATE_PASSWORD:=${POSTGRES_PASSWORD}}"

if [ -z "$MIGRATE_PASSWORD" ]; then
  echo "ERROR: MIGRATE_PASSWORD / POSTGRES_PASSWORD is not set." >&2
  echo "       Create a .env file or export the variable." >&2
  exit 1
fi

export PGPASSWORD="$MIGRATE_PASSWORD"
PSQL=(psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$MIGRATE_USER" -d "$POSTGRES_DB")

# ---- Helpers -------------------------------------------------------------
DRY_RUN=false
FROM_FILTER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --run)     FROM_FILTER="$2"; shift 2 ;;
    *)         echo "Usage: $0 [--dry-run] [--run NN]"; exit 1 ;;
  esac
done

log()   { echo "  ▪ $*"; }
warn()  { echo "  ⚠ $*" >&2; }
action(){ echo "  ▶ $*"; }

# ---- Find migrations to apply --------------------------------------------
echo ""
echo "  Migrations directory: $MIGRATIONS_DIR"
echo "  Target database:      $POSTGRES_DB @ $POSTGRES_HOST:$POSTGRES_PORT"
echo ""

shopt -s nullglob
migrations=("$MIGRATIONS_DIR"/*.sql)
shopt -u nullglob

if [ ${#migrations[@]} -eq 0 ]; then
  echo "  No SQL migrations found."
  exit 0
fi

IFS=$'\n' sorted=($(sort <<<"${migrations[*]}")); unset IFS

for m in "${sorted[@]}"; do
  basename="$(basename "$m")"
  num="${basename%%-*}"

  # Skip if --run filter is active and this migration is older
  if [ -n "$FROM_FILTER" ]; then
    if [ "$(echo "$num" | sed 's/^0*//')" -lt "$(echo "$FROM_FILTER" | sed 's/^0*//')" ]; then
      continue
    fi
  fi

  if [ "$DRY_RUN" = true ]; then
    log "[dry-run] $basename"
    continue
  fi

  action "Applying $basename ..."
  "${PSQL[@]}" -f "$m" -1
  log "done."
done

echo ""
echo "  ✅ Migration run complete."
