#!/usr/bin/env bash
# Daily eval canary: emit retrieval/citation/abstention metrics JSON (no LLM).
set -uo pipefail
DIR="/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
cd "$DIR"; mkdir -p logs
export HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
       PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src
.venv/bin/python scripts/eval_json.py 2>> logs/canary.log
