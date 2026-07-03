#!/usr/bin/env bash
# Weekly corpus refresh: scrape new circulars -> reindex -> restart API -> emit metrics.
# Heavy output goes to logs/refresh.log; stdout is only the final metrics JSON.
set -uo pipefail
DIR="/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
cd "$DIR"; mkdir -p logs
export HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
       PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src
FROM=$(date -v-45d +%F 2>/dev/null || date -d '45 days ago' +%F)
TO=$(date +%F)
{
  echo "=== refresh $(date '+%F %T') section=circulars from=$FROM to=$TO ==="
  .venv/bin/python scripts/scrape_sebi.py --section circulars --from "$FROM" --to "$TO" --max 100 --rate 3
  make reindex
  # reload the API so it serves the fresh index (best-effort; ignore if not installed)
  launchctl kickstart -k "gui/$(id -u)/com.sebi-rag" 2>/dev/null || true
} >> logs/refresh.log 2>&1
.venv/bin/python scripts/eval_json.py 2>> logs/refresh.log
