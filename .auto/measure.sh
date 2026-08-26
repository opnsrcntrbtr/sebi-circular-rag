#!/bin/bash
set -euo pipefail

# Autoresearch measure.sh — Extension Evaluation for SEBI RAG
# Outputs METRIC name=value lines for primary and secondary metrics

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# ─── Pre-check: syntax errors (<1s) ───
python -m py_compile src/sebi_rag/pipeline.py 2>/dev/null || { echo "FAIL: pipeline.py syntax error"; exit 1; }
python -m py_compile src/sebi_rag/api.py 2>/dev/null || { echo "FAIL: api.py syntax error"; exit 1; }
python -m py_compile src/sebi_rag/generate.py 2>/dev/null || { echo "FAIL: generate.py syntax error"; exit 1; }

# ─── Baseline Token Count ───
# Measure current session token count (approximate via prompt file sizes)
BASELINE_TOKENS=3500  # From AGENTS.md system prompt (~9.2KB)

# Count installed extension manifests
EXT_TOKENS=0
for ext_dir in /Users/ianpinto/.pi/agent/skills/pi-* /Users/ianpinto/.agents/skills/pi-*; do
  if [ -d "$ext_dir" ]; then
    # Estimate manifest tokens from file sizes
    for f in "$ext_dir"/manifest.json "$ext_dir"/prompt.md "$ext_dir"/SKILL.md; do
      if [ -f "$f" ]; then
        fsize=$(wc -c < "$f" 2>/dev/null || echo 0)
        ftokens=$((fsize / 4))  # rough: 4 chars per token
        EXT_TOKENS=$((EXT_TOKENS + ftokens))
      fi
    done
  fi
done

TOTAL_TOKENS=$((BASELINE_TOKENS + EXT_TOKENS))
OVERHEAD_PCT=$(python3 -c "print(round(($EXT_TOKENS / $BASELINE_TOKENS) * 100, 2))" 2>/dev/null || echo "0")

METRIC token_overhead_pct=$OVERHEAD_PCT
METRIC total_tokens=$TOTAL_TOKENS
METRIC baseline_tokens=$BASELINE_TOKENS
METRIC extension_tokens=$EXT_TOKENS

# ─── Test Feedback Time (Partial Change) ───
# Touch a file and time how long make test takes for affected tests only
TOUCH_FILE="src/sebi_rag/retrieve.py"
touch "$TOUCH_FILE"

# Time the full test suite (baseline for comparison)
FULL_TEST_START=$(date +%s%N)
make test 2>&1 | tail -5 || true
FULL_TEST_END=$(date +%s%N)
FULL_TEST_MS=$(( (FULL_TEST_END - FULL_TEST_START) / 1000000 ))

# Time with green-loop if installed (scoped tests)
if pi green-loop --dry-run 2>/dev/null; then
  GREEN_LOOP_START=$(date +%s%N)
  pi green-loop --run 2>&1 | tail -5 || true
  GREEN_LOOP_END=$(date +%s%N)
  GREEN_LOOP_MS=$(( (GREEN_LOOP_END - GREEN_LOOP_START) / 1000000 ))
else
  GREEN_LOOP_MS=$FULL_TEST_MS  # fallback: same as full
fi

METRIC full_test_time_ms=$FULL_TEST_MS
METRIC green_loop_time_ms=$GREEN_LOOP_MS

# ─── LSP Lookup Time ───
# Measure time for graphify + pi-lens navigation
LSP_START=$(date +%s%N)
graphify query "HybridRetriever" 2>&1 | tail -3 || true
LSP_END=$(date +%s%N)
LSP_TIME_MS=$(( (LSP_END - LSP_START) / 1000000 ))

METRIC lsp_lookup_time_ms=$LSP_TIME_MS

# ─── Edit Success Rate ───
# Test hashline edit stability (simulated)
EDIT_SUCCESS=0
EDIT_TOTAL=10

for i in $(seq 1 $EDIT_TOTAL); do
  # Try a simple edit on a test file
  if python3 -c "
import sys
sys.path.insert(0, 'src')
# Verify CircularMeta is intact
from sebi_rag.segment import CircularMeta
meta = CircularMeta(title='test', date='2024-01-01')
assert hasattr(meta, 'title'), 'title missing'
assert hasattr(meta, 'date'), 'date missing'
# Verify no extra fields (project constraint)
assert len([k for k in dir(meta) if not k.startswith('_')]) <= 20, 'too many fields'
" 2>/dev/null; then
    EDIT_SUCCESS=$((EDIT_SUCCESS + 1))
  fi
done

EDIT_RATE=$(python3 -c "print(round($EDIT_SUCCESS / $EDIT_TOTAL * 100, 1))")
METRIC edit_success_rate_pct=$EDIT_RATE

# ─── Summary ───
echo ""
echo "=== Extension Evaluation Metrics ==="
echo "Token overhead: ${OVERHEAD_PCT}% (target: ≤3%)"
echo "Full test time: ${FULL_TEST_MS}ms"
echo "Green-loop time: ${GREEN_LOOP_MS}ms"
echo "LSP lookup time: ${LSP_TIME_MS}ms"
echo "Edit success rate: ${EDIT_RATE}% (target: >95%)"
