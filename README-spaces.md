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
| Corpus | `data/corpus/circulars.jsonl` (scraped + ingested locally) | [`opnsrcntrbtrian/sebi-circulars`](https://huggingface.co/datasets/opnsrcntrbtrian/sebi-circulars) HF dataset, `chunks` config (78,585 section-aware chunks, 728 circulars incl. all 130 SEBI master circulars, snapshot v2026.08 — dataset repo not re-published since 2026-08-14; see `docs/status.md`'s dated entries for the corpus's current 1,490-circular/83,752-chunk state, which the Space serves via the separately-covered prebuilt `index_repo` below, not via this dataset) |
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
- **As of date (optional)** — calendar picker (`gr.DateTime`, date-only; a
  typed `YYYY-MM-DD` is also accepted); scores retrieval against the law in
  force on that date (circulars issued later are excluded; the circular
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

**Code changes deploy automatically.** `.github/workflows/deploy-space.yml`
runs `scripts/deploy_space.py` on every push to `main` that touches `app.py`,
`src/sebi_rag/**`, `config.toml`, `requirements-spaces.txt` or this file.

Requires an `HF_TOKEN` secret on the GitHub `space-deploy` environment
(Settings → Environments → New environment → `space-deploy` → Environment
secrets) — not a bare repo secret, so it isn't exposed outside this job.
Use a **fine-grained** token from huggingface.co/settings/tokens scoped to
write-only on `spaces/opnsrcntrbtrian/sebi-circular-rag-demo` (not the whole
account), with an expiration date set — HF has no automatic rotation, so
put the expiry on your own calendar. Until the environment + secret exist,
the workflow fails loudly at the deploy step rather than silently skipping.

For a manual/local push: `make deploy-space` (`SPACE_REPO=` to override the
target). Both paths run the same script, which uploads `app.py`,
`src/sebi_rag/`, `config.toml`, `requirements-spaces.txt` (as
`requirements.txt`) and this file (as `README.md`) via `HfApi.upload_folder`.

`create_repo`/`request_space_hardware` inside that script routinely return
`402 Payment Required` on a free account when the Space already exists —
**this is expected and non-fatal**, not a deploy blocker: both calls are
wrapped in `try/except` and the actual upload does not depend on either
succeeding (confirmed working end-to-end via `.superpowers/sdd/task-5-report.md`,
2026-07-13). Only the initial *creation* of a new paid-tier Space needs PRO.

One-time index setup (not part of the automated deploy):
1. `make reindex` then
   `python scripts/upload_spaces_index.py --repo <you>/sebi-circulars-index`.
2. Set `[spaces] index_repo` (and optionally `external_space`) in
   `config.toml` — this is one of the files the deploy workflow watches, so
   committing the change ships it.

First query builds the pipeline (model downloads + index fetch): expect a
few minutes cold, seconds warm for retrieval, longer when the CPU fallback
generates.

### Troubleshooting: `exit code 128` with an empty build log

Seen 2026-09-16: `hf spaces info <repo> --expand runtime` reports
`stage: BUILD_ERROR`, `errorMessage: "Job failed with exit code: 128. Reason:
Error"`, and `hf spaces logs <repo> --build` shows nothing past the
`===== Build Queued =====` line. **This is an HF infra scheduling failure,
not a repo defect** — confirmed by a byte-identical diff of `app.py`,
`requirements.txt` and `config.toml` against the prior (successful) commit,
and by `git clone` of the Space repo succeeding cleanly. Root-caused via the
`huggingface-spaces` skill's `references/known-errors.md` § "Exit code 128 /
containerd / scheduling failure".

**Fix**: click *Restart this Space* on the Space's Settings page (or
`hf spaces restart <repo> --factory-reboot`). No file change is required —
do not spend a session diffing commits before trying this first.
`scripts/deploy_space.py` now prints the Space's post-deploy `stage` and
`hardware.current`/`requested` after every upload (and a `WARNING:` line
with the `errorMessage` if `stage == BUILD_ERROR`), so this state is visible
in the deploy log going forward instead of requiring a manual `hf spaces
info` check. It compares the runtime's `sha` against the commit it just
pushed and suppresses the warning when they don't match yet — the read-back
happens immediately after `upload_folder` returns, before HF has moved the
Space into `BUILDING` for the new commit, so an unguarded check would
either reprint the *previous* build's stale error or miss a fresh one.

## Data, licensing and citation

The corpus is a research snapshot of publicly available SEBI circulars.
SEBI is the authoritative source; this demo is not regulatory guidance —
answers can abstain, flag superseded circulars and mark unsupported
citations, but must not be relied on for compliance decisions. See the
[dataset card](https://huggingface.co/datasets/opnsrcntrbtrian/sebi-circulars)
for schema, licensing and citation details.
