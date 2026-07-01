#!/usr/bin/env bash
# start-all.sh — launch the full FinIntel stack (Linux/macOS/Git-Bash)
#   Usage: ./scripts/start-all.sh   (Ctrl-C stops all services)
# Assumes: PostgreSQL running, python env active, migrations applied.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ML="$ROOT/ml-services"
PIDS=()

start() {  # name port
  ( cd "$ML/$1" && uvicorn main:app --port "$2" ) &
  PIDS+=($!)
  echo "  $1 -> http://localhost:$2"
  sleep 0.4
}

echo "Launching FinIntel services..."
start ocr 8001
start standardize 8002
start entity 8003
start validation 8004
start graph 8005
start anomaly 8007
start temporal 8008
start trail 8009
start report 8010

( cd "$ROOT/backend" && cargo run ) &
PIDS+=($!)
echo "  backend -> http://localhost:8080"
echo ""
echo "Swagger UI: http://localhost:8080/docs"

trap 'echo "Stopping..."; kill ${PIDS[*]} 2>/dev/null || true' INT TERM
wait
