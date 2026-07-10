---
title: SEBI Circular RAG
emoji: 📜
colorFrom: indigo
colorTo: green
sdk: gradio
app_file: app.py
python_version: "3.11"
pinned: false
license: other
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
| Corpus | `data/corpus/circulars.jsonl` (scraped + ingested locally) | [`opnsrcntrbtrian/sebi-circulars`](https://huggingface.co/datasets/opnsrcntrbtrian/sebi-circulars) HF dataset, `chunks` config (36.6k section-aware chunks, 603 circulars, snapshot v2026.07) |
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

Generation order: the external Space is tried first and any failure or
timeout (`external_timeout_s`, default 20 s) falls back to the in-Space CPU
model. Leave `external_space = ""` to run fallback-only.

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
