#!/bin/bash
# start-local.sh - Starts Grocery Tracker locally without Docker

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend_python_fastAPI"
FRONTEND_DIR="$ROOT_DIR/frontend"
ROOT_ENV_FILE="$ROOT_DIR/.env"
BACKEND_ENV_FILE="$BACKEND_DIR/.env"
INIT_SQL_FILE="$BACKEND_DIR/init.sql"

CHROMA_PID=""
BACKEND_PID=""
FRONTEND_PID=""
LOCAL_FRONTEND_API_URL=""

echo "==============================================="
echo "   AI Grocery Tracker - Local Startup Script   "
echo "==============================================="

require_command() {
    local cmd="$1"
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Error: Required command '$cmd' was not found in PATH."
        exit 1
    fi
}

load_env_file() {
    local env_file="$1"
    if [ -f "$env_file" ]; then
        set -a
        # shellcheck disable=SC1090
        source "$env_file"
        set +a
    fi
}

parse_database_url() {
    local url="${DATABASE_URL:-}"
    if [[ "$url" =~ ^postgres(ql)?://([^:]+):([^@]+)@([^:/]+):([0-9]+)/(.+)$ ]]; then
        DB_USER="${BASH_REMATCH[2]}"
        DB_PASSWORD="${BASH_REMATCH[3]}"
        DB_HOST="${BASH_REMATCH[4]}"
        DB_PORT="${BASH_REMATCH[5]}"
        DB_NAME="${BASH_REMATCH[6]}"
    else
        echo "Error: DATABASE_URL must match postgresql://user:password@host:port/database"
        exit 1
    fi
}

cleanup() {
    local exit_code=$?

    for pid in "$FRONTEND_PID" "$BACKEND_PID" "$CHROMA_PID"; do
        if [ -n "$pid" ] && kill -0 "$pid" >/dev/null 2>&1; then
            kill "$pid" >/dev/null 2>&1 || true
        fi
    done

    wait >/dev/null 2>&1 || true

    if [ "$exit_code" -ne 0 ]; then
        echo ""
        echo "Local startup stopped with an error."
    fi
}

trap cleanup EXIT INT TERM

load_env_file "$ROOT_ENV_FILE"
load_env_file "$BACKEND_ENV_FILE"

LOCAL_FRONTEND_API_URL="${LOCAL_VITE_API_URL:-http://localhost:8000}"

require_command python
require_command npm
require_command psql
require_command pg_isready
require_command chroma

if [ -z "${DATABASE_URL:-}" ]; then
    echo "Error: DATABASE_URL is not set. Add it to .env or backend_python_fastAPI/.env."
    exit 1
fi

if [ -z "${GEMINI_API_KEY:-}" ]; then
    echo "Warning: GEMINI_API_KEY is not set. Gemini-backed features will fail until it is configured."
fi

parse_database_url

echo ""
echo "Checking PostgreSQL availability at ${DB_HOST}:${DB_PORT}..."
if ! PGPASSWORD="$DB_PASSWORD" pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; then
    echo "Error: PostgreSQL is not reachable."
    echo "Start your local PostgreSQL server first, then rerun this script."
    exit 1
fi

echo "Initializing database schema from $INIT_SQL_FILE..."
PGPASSWORD="$DB_PASSWORD" psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$INIT_SQL_FILE" >/dev/null

echo "Starting Chroma on ${CHROMA_HOST:-localhost}:${CHROMA_PORT:-8000}..."
(
    cd "$ROOT_DIR"
    chroma run --host "${CHROMA_HOST:-localhost}" --port "${CHROMA_PORT:-8000}"
) &
CHROMA_PID=$!

echo "Starting FastAPI backend on http://127.0.0.1:8000 ..."
(
    cd "$BACKEND_DIR"
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
) &
BACKEND_PID=$!

echo "Starting React frontend on http://localhost:5173 ..."
(
    cd "$FRONTEND_DIR"
    VITE_API_URL="$LOCAL_FRONTEND_API_URL" npm run dev -- --host 0.0.0.0
) &
FRONTEND_PID=$!

echo ""
echo "==============================================="
echo "Local services are starting."
echo "Frontend: http://localhost:5173"
echo "Backend:  http://127.0.0.1:8000"
echo "Docs:     http://127.0.0.1:8000/docs"
echo "Frontend API target: $LOCAL_FRONTEND_API_URL"
echo "Chroma:   http://${CHROMA_HOST:-localhost}:${CHROMA_PORT:-8000}"
echo "Press Ctrl+C to stop all local processes started by this script."
echo "==============================================="
echo ""

wait "$CHROMA_PID" "$BACKEND_PID" "$FRONTEND_PID"
