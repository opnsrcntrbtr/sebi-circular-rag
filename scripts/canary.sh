#!/usr/bin/env bash
# Daily eval canary: emit retrieval/citation/abstention metrics JSON (no LLM).
set -uo pipefail
DIR="/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
cd "$DIR"; mkdir -p logs
export HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
       PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src
# Pin the stub: config.toml sets eval_generator="mlx" so the GATE matches
# production, but that costs ~20 min over 260 rows and ops_server runs this
# under a hard 300s timeout (n8n budgets the same 5 min). The canary is a fast
# regression tripwire, not the gate.
# Consequence: canary citation metrics are stub-basis and do NOT correspond to
# the MLX-derived gate floors in eval/golden/gate_v7.json. Compare canary
# numbers against canary history, never against the gate.
export SEBI_RAG_EVAL_GENERATOR=stub
.venv/bin/python scripts/eval_json.py 2>> logs/canary.log
