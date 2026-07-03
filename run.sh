#!/usr/bin/env bash
# Start the SEBI Circular RAG API. Used by launchd / manual start.
set -euo pipefail
cd "$(dirname "$0")"
export HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
       PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src
# MPS is single-process: one worker. Set SEBI_RAG_API_KEY in the environment.
exec .venv/bin/uvicorn sebi_rag.api:app --host 127.0.0.1 --port "${PORT:-8000}" --workers 1
