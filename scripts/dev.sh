#!/usr/bin/env bash
# Dev server wrapper — starts FastAPI + Gradio via hub lifecycle.
# Usage: ./scripts/dev.sh [api|ui|both]
set -euo pipefail

cd "$(dirname "$0")/.."

MODE="${1:-both}"

case "$MODE" in
  api)
    echo "Starting FastAPI on port 8000..."
    make serve
    ;;
  ui)
    echo "Starting Gradio UI on port 7860..."
    make ui
    ;;
  both)
    echo "Starting FastAPI on port 8000..."
    make serve &
    API_PID=$!
    
    echo "Starting Gradio UI on port 7860..."
    make ui &
    UI_PID=$!
    
    echo "Dev servers running (API: $API_PID, UI: $UI_PID)"
    echo "Press Ctrl+C to stop both."
    
    trap 'kill $API_PID $UI_PID 2>/dev/null; wait' EXIT
    wait
    ;;
  *)
    echo "Usage: $0 [api|ui|both]"
    exit 1
    ;;
esac
