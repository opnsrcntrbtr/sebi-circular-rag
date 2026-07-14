---
title: SEBI Circular RAG
emoji: 📜
colorFrom: indigo
colorTo: green
sdk: gradio
app_file: app.py
python_version: "3.11"
pinned: false
hardware: cpu-basic
license: other
sdk_version: 6.20.0
---

# SEBI Circular RAG — Hugging Face Spaces demo

CPU-only demo of the [sebi-circular-rag](https://github.com/opnsrcntrbtr/sebi-circular-rag)
system: hybrid FAISS + BM25 retrieval with cross-encoder reranking,
supersession-aware citations, faithfulness checking and an abstention gate
over Indian SEBI circulars.

> This file doubles as the Space README: copy it to `README.md` in the Space
> repo (the YAML header above is the Space metadata).

## How this demo differs from the full local system

| | Local (Apple Silicon) | This Space (free CPU) |
|---|---|---|
| Corpus | `data/corpus/circulars.jsonl` (scraped + ingested locally) | [`opnsrcntrbtrian/sebi-circulars`](https://huggingface.co/datasets/opnsrcntrbtrian/sebi-circulars) HF dataset, `chunks` config (77.9k section-aware chunks, 705 circulars incl. all 130 SEBI master circulars, snapshot v2026.07) |
| Index | Built/loaded from `data/index` | Same artifacts, prebuilt locally and downloaded from the `[spaces] index_repo` HF dataset repo (`scripts/upload_spaces_index.py`) — retrieval is numerically identical |
| Embeddings / reranker | BAAI/bge-m3 + BAAI/bge-reranker-v2-m3 on `mps` | Same models on `cpu` (queries only; corpus vectors are prebuilt) |
| Generator | MLX `Qwen2.5-1.5B-Instruct-4bit` (or Ollama) | External LLM Space via `gradio_client` (`[spaces] external_space`, fill before deploy) with CPU fallback `Qwen/Qwen2.5-0.5B-Instruct`, `max_tokens = 200` |
| Abstention gate | SubjectSimJudge (0.42 / 0.60) | Identical |
| Auth / rate limit | FastAPI `X-API-Key` + per-key limit | None — anonymous in-process demo |

## UI modes

- **rag** — full pipeline: retrieve → rerank → supersession demotion →
  abstention gate → grounded generation with bracketed citations.
- **retrieval_only** — academic retrieval-benchmark mode: no LLM runs
  (deterministic extractive stub); citations, supersession lineage,
  certainty and abstention metadata are still real.
- **As of date (optional)** — YYYY-MM-DD; scores retrieval against the law
  in force on that date (circulars issued later are excluded; the circular
  governing on that date is not demoted for being superseded today).

Generation order: the external Space is tried first and any failure or
timeout (`external_timeout_s`, default 20 s) falls back to the in-Space CPU
model. Leave `external_space = ""` to run fallback-only.

## ZeroGPU-hardware workaround

This Space was originally provisioned on `zero-a10g` (ZeroGPU) hardware.
ZeroGPU Spaces refuse to start unless at least one function is decorated
with `@spaces.GPU` ("No @spaces.GPU function detected"), so `app.py`
declares an unused `warm_up_gpu()` decorated with `@spaces.GPU` purely to
satisfy that startup check — it is never called. The `@spaces.GPU`
decorator only grants a real GPU to the call it wraps; every other code
path (the RAG pipeline, retrieval, reranking, generation) runs on the CPU
host process ZeroGPU allocates outside GPU-decorated calls, so behavior is
identical to a true `cpu-basic` Space. See `tests/test_app_zerogpu.py` for
regression coverage (the decorator must stay present and `warm_up_gpu`
must stay uncalled).

**Caveat:** the `hardware: cpu-basic` line in this file's YAML front matter
is a human-readable note only — `hardware` is not a documented Spaces
config key (only `suggested_hardware` is, and even that doesn't
auto-assign hardware; see the
[Spaces config reference](https://huggingface.co/docs/hub/spaces-config-reference)).
It does **not** change the Space's actual provisioned hardware. Downgrading
from `zero-a10g` to `cpu-basic` requires either a PRO subscription (HF
returns 402 to `request_space_hardware` for a ZeroGPU→CPU downgrade on a
free account — see `scripts/deploy_space.py`) or a manual change in the
Space's Settings UI. Until then, the workaround above is the permanent
fix for the CPU-only workload on this specific Space; it is not a
temporary stopgap.

## Deploying

1. Locally: `make reindex` then
   `python scripts/upload_spaces_index.py --repo <you>/sebi-circulars-index`.
2. Set `[spaces] index_repo` (and optionally `external_space`) in `config.toml`.
3. Create a Gradio-SDK Space; push this repo (or `app.py`, `src/`,
   `config.toml`, `requirements-spaces.txt` renamed to `requirements.txt`,
   and this file as `README.md`).

First query builds the pipeline (model downloads + index fetch): expect a
few minutes cold, seconds warm for retrieval, longer when the CPU fallback
generates.

## Data, licensing and citation

The corpus is a research snapshot of publicly available SEBI circulars.
SEBI is the authoritative source; this demo is not regulatory guidance —
answers can abstain, flag superseded circulars and mark unsupported
citations, but must not be relied on for compliance decisions. See the
[dataset card](https://huggingface.co/datasets/opnsrcntrbtrian/sebi-circulars)
for schema, licensing and citation details.
