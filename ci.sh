#!/bin/bash

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

echo "[INFO] Clearing environment (orphans only)"
docker compose down --remove-orphans

echo "[INFO] Building images..."
docker compose build

echo "[INFO] Running tests..."
docker compose run --rm tees-test

echo "[INFO] Service OK"
