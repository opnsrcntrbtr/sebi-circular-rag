#!/usr/bin/env bash
# Start the local ops HTTP server (n8n calls it instead of using Execute Command).
set -euo pipefail
cd "$(dirname "$0")"
exec .venv/bin/python scripts/ops_server.py
