#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== SEBI Circular RAG — Automated Metrics ==="
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# Ensure output directories exist
mkdir -p .auto/runs .auto/reports

# Run the Python benchmark script
python scripts/bench_metrics.py "$@"

echo ""
echo "=== Metrics written to .auto/runs/ and .auto/reports/ ==="
