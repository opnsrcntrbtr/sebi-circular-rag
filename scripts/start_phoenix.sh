#!/usr/bin/env bash
# Launch Arize Phoenix telemetry server (http://localhost:6006).
# Safe to call multiple times — idempotent.
set -euo pipefail

PHOENIX_PORT=6006
PHOENIX_URL="http://localhost:${PHOENIX_PORT}"

# Check if Phoenix is already running
if curl -s -o /dev/null -w "%{http_code}" "${PHOENIX_URL}/" 2>/dev/null | grep -q '^2'; then
  echo "[phoenix] Already running at ${PHOENIX_URL}"
  exit 0
fi

# Start Phoenix in background
echo "[phoenix] Starting Arize Phoenix on ${PHOENIX_URL} ..."
nohup phoenix serve > /tmp/phoenix.log 2>&1 &
PHOENIX_PID=$!

# Wait for server to become ready (up to 30s)
for i in $(seq 1 30); do
  if curl -s -o /dev/null -w "%{http_code}" "${PHOENIX_URL}/" 2>/dev/null | grep -q '^2'; then
    echo "[phoenix] Ready at ${PHOENIX_URL} (PID ${PHOENIX_PID})"
    echo "${PHOENIX_PID}" > /tmp/phoenix.pid
    exit 0
  fi
  sleep 1
done

echo "[phoenix] ERROR: did not become ready within 30s. Check /tmp/phoenix.log"
kill "${PHOENIX_PID}" 2>/dev/null || true
exit 1
