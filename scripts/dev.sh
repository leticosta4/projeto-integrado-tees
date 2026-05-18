#!/bin/bash

# Errors on failed commands and cleanup
set -ouxe pipefail
trap cleanup ERR SIGINT SIGTERM
cleanup() {
	local exit_code=$?
	if [[ $exit_code -ne 0 ]]; then
		echo "[ERROR] $exit_code, bringing down services..."
		docker compose down --remove-orphans
	fi
	exit "$exit_code"
}

# Change to project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "[INFO] Clearing environment (orphans only)"
docker compose down --remove-orphans

echo "[INFO] Building images..."
docker compose build

echo "[INFO] Starting database..."
docker compose up --wait tees-pgvector

echo "[INFO] Running migrations..."
docker compose run --rm tees-migrations

echo "[INFO] Service OK"
