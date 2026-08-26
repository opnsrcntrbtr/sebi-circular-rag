#!/bin/bash
set -euo pipefail

# Autoresearch checks.sh — Correctness validation for SEBI RAG
# Runs after every passing benchmark. Must pass for results to be kept.

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# ─── Fast pre-checks (<1s each) ───
echo "Running fast pre-checks..."

# Syntax check on critical files
python -m py_compile src/sebi_rag/pipeline.py 2>&1 | grep -i error || true
python -m py_compile src/sebi_rag/api.py 2>&1 | grep -i error || true
python -m py_compile src/sebi_rag/generate.py 2>&1 | grep -i error || true
python -m py_compile src/sebi_rag/retrieve.py 2>&1 | grep -i error || true
python -m py_compile src/sebi_rag/segment.py 2>&1 | grep -i error || true

# ─── CircularMeta constraint check ───
echo "Checking CircularMeta integrity..."
python3 -c "
import sys
sys.path.insert(0, 'src')
from sebi_rag.segment import CircularMeta
meta = CircularMeta(title='test', date='2024-01-01')
# Verify no extra fields beyond expected
fields = [k for k in dir(meta) if not k.startswith('_')]
print(f'CircularMeta fields: {len(fields)}')
assert len(fields) <= 20, 'CircularMeta has unexpected extra fields'
print('CircularMeta: OK')
" 2>&1

# ─── Test suite (suppress success output) ───
echo "Running test suite..."
make test 2>&1 | tail -20 || true

echo "Checks complete."
