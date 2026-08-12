#!/usr/bin/env bash
# Daily eval canary: emit retrieval/citation/abstention metrics JSON (no LLM).
set -uo pipefail
DIR="/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
cd "$DIR"; mkdir -p logs
export HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
       PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src
# Pin the stub: config.toml sets eval_generator="mlx" so the GATE matches
# production, but MLX costs ~20 min over 260 rows.
#
# This is NOT a ~40s job, despite what the docs long claimed. Measured
# 2026-08-12: 840s on stub. The old figure predates the reporting set moving
# from golden_v5 (n=56) to golden_v7 (n=260) and B' scoring every row with a
# cross-encoder. The ops/n8n budgets were raised to 1800s to match; pinning
# the stub alone does not fit a 300s window.
#
# golden_v5 would fit (183s) but carries pre-2026-07-30 abstain labels and
# reports abstention 0.804, so it would alert forever. Correct labels beat a
# faster tripwire.
#
# Consequence: canary citation metrics are stub-basis and do NOT correspond to
# the MLX-derived gate floors in eval/golden/gate_v7.json. Compare canary
# numbers against canary history, never against the gate.
export SEBI_RAG_EVAL_GENERATOR=stub
.venv/bin/python scripts/eval_json.py 2>> logs/canary.log
