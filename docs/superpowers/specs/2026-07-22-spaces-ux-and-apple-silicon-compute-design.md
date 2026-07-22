# Design: Port Spaces UX into the local pipeline + Apple-Silicon compute best practice

**Date:** 2026-07-22
**Status:** Approved (design phase) — pending user review before implementation plan
**Scope:** Two independent tracks in one spec.
- **Track A — UX port.** Bring the proven Hugging Face Spaces demo UX (`app.py`) into the
  local Apple-Silicon pipeline (`src/sebi_rag/ui.py` + `src/sebi_rag/api.py`), keeping the
  local thin-client architecture.
- **Track B — Apple-Silicon compute.** MPS/unified-memory hardening + an optional MLX-native
  embeddings/reranker backend, aligned to best practice as of 22 July 2026. ANE/NPU is
  consciously declined (see B6).

## Guiding constraints

- **Respect the two-parallel-paths rule** (`CLAUDE.md`): edit **only** the local modules
  (`api.py`, `ui.py`, `embeddings.py`, `rerank.py`, `settings.py`, `device.py`, `Makefile`).
  Do **not** edit the Spaces modules (`app.py`, `*_spaces.py`). The two code paths stay
  separate; they merely converge in features.
- **Thin-client architecture preserved.** `ui.py` remains a pure HTTP client; every new
  capability routes through the FastAPI `/query` endpoint. All logic lives server-side.
- **Measurement-first.** Any change that can move retrieval quality (fp16, MLX backend) is
  gated by an A/B run (`make bench-retrieval` / `make eval-asof`) against the golden/probe
  sets before it becomes the default.
- **Tracks are independent** and can be implemented/sequenced separately.

---

## Current state (as analyzed)

### Local pipeline
- `ui.py`: thin HTTP client → `/query`. Inputs: Question, API URL, API Key, Top-K.
  Outputs: latency, faithfulness, certainty+abstention, superseded (JSON), unsupported.
  **Missing:** as-of date field, mode selector, advisory toggle, richer output surfacing.
- `api.py` `QueryRequest`: **already accepts `as_of` and `advisory`**; **no `mode` field**.
  `QueryResponse` already returns `confidence`, `draft_answer`, `retrieved` — the UI ignores
  them today. `create_app` caches a single pipeline under `state["p"]`.
- `pipeline.query(question, pool, top_k, advisory, as_of)`: as-of uses per-edge supersession
  timing. `RAGPipeline` is a dataclass (Spaces relies on `dataclasses.replace`).

### Spaces demo (reference for UX only; not edited)
- `app.py` (in-process): adds a **Mode radio** (`rag`/`retrieval_only`), an **As-of date**
  field with strict ISO validation + friendly error, and a retrieval-only answer banner.
  `retrieval_only` swaps in `ExtractiveStubGenerator` via
  `dataclasses.replace(base, generator=ExtractiveStubGenerator())`, cached per mode
  (`get_pipeline`).

### Compute
- `BGEM3Embedder`: BGE-M3 via FlagEmbedding, **hardcoded `device="mps"`, `use_fp16=False`** (fp32).
- `CrossEncoderReranker`: bge-reranker-v2-m3 via sentence-transformers, **hardcoded `device="mps"`**,
  no dtype/batch control.
- `MLXGenerator`: MLX-LM Qwen2.5-1.5B-4bit (Metal GPU + unified memory) — already Apple-native
  and optimal; `OllamaGenerator` (llama.cpp/Metal) is the alternative. **No generation change needed.**
- `Settings` (frozen dataclass): `env SEBI_RAG_<FIELD> > [service] in config.toml > default`
  via `_get`. `Embedder` is a `Protocol` (`dim`, `encode`); the reranker is duck-typed on `.rerank()`.

---

## Track A — UX port

### A1. Backend — `src/sebi_rag/api.py` (one real change)

**`QueryRequest`** — add one field:
```python
mode: Literal["rag", "retrieval_only"] = "rag"
```
`as_of` and `advisory` already exist — no schema change for them. Invalid `mode` → 422
(Pydantic `Literal`). `QueryResponse` is **unchanged**.

**`create_app` pipeline routing** — replace the single `state["p"]` cache with a per-mode
cache mirroring `app.py:get_pipeline()`:
- `rag` → base pipeline (lazy build, as today).
- `retrieval_only` → `dataclasses.replace(base, generator=ExtractiveStubGenerator())`, cached.
  Cheap: shares retriever/reranker/lineage. `ExtractiveStubGenerator` lives in `generate.py`
  (local module).

**`/query` handler** — select the pipeline by `req.mode`, then submit to the existing
`ThreadPoolExecutor` exactly as now (timeout budget, guard, response shaping unchanged).

**Banner stays client-side** (presentation, not API) — keeps `QueryResponse` clean.

### A2. Frontend — `src/sebi_rag/ui.py` (thin client; most of the work)

Mirror `run_query_spaces` behavior over HTTP.

**New inputs** (right sidebar, "Query controls" accordion):
- `mode` radio: `rag` / `retrieval_only`.
- `as_of` textbox (optional).
- `advisory` checkbox.

**`submit_query` logic:**
- Validate `as_of` **client-side** via a pure helper `_parse_as_of(raw) -> str | None`
  (empty → `None`; else strict `date.fromisoformat`). Malformed → friendly
  `"'As of date' must be YYYY-MM-DD (e.g. 2025-01-10)."` with no server round-trip.
- Send `{question, top_k, mode, advisory, as_of}` (as_of omitted/None when blank).
- Prepend the **retrieval-only banner** to the answer when
  `mode == "retrieval_only" and not abstained` (text mirrors `app.py`).
- Render `draft_answer` only when non-empty, labeled *"Advisory draft — not authoritative"*.

**New outputs** (new **collapsed** "Advanced outputs" accordion):
- `confidence` (`gr.Code`, JSON).
- `draft_answer` (`gr.Markdown`).
- `retrieved` list (`gr.Dataframe` or `gr.Code`).

### A3. Layout (grouped-accordions — approved)

- **Left column:** question → Submit → answer (+banner) → citations.
- **Right sidebar accordions:**
  - **Connection** — API URL, API Key.
  - **Query controls** — Top-K, mode, as-of, advisory.
  - **Metadata** — latency, faithfulness, certainty, superseded, unsupported (unchanged set).
  - **Advanced outputs** (collapsed by default) — confidence, draft, retrieved.

### A4. Data flow

```
UI validates as_of
  → POST /query {question, top_k, mode, advisory, as_of}
  → guard (auth + rate limit)
  → select pipeline by mode (rag | retrieval_only)
  → executor.submit(pipeline.query, question, top_k=, advisory=, as_of=)
  → QueryResponse
  → UI renders: answer (+banner) / citations / metadata / advanced outputs
```

### A5. Testing (Track A)

- `tests/test_api.py`:
  - `mode="retrieval_only"` routes through `ExtractiveStubGenerator` (deterministic, non-LLM
    answer) using the existing tiny-pipeline factory pattern.
  - `mode` defaults to `rag` (existing behavior unchanged).
  - Invalid `mode` → 422.
  - Base and stub pipelines share retrieval (same citations for a fixed query).
- UI helper: `_parse_as_of` extracted as a pure function and unit-tested (valid / empty /
  malformed). This adds the first test coverage for `ui.py`.
- `make test` (offline, `-m "not integration"`) stays green.

### A6. Out of scope (Track A — YAGNI)

`generate_spaces.py` backends (external LLM Space, HF/CPU fallback), the `@spaces.GPU`
warmup, and the `spaces` import — all HF-architecture-specific and irrelevant to MLX/Ollama.

---

## Track B — Apple-Silicon compute (best practice, mid-2026)

### B1. Device + dtype abstraction — new `src/sebi_rag/device.py`

- `pick_device(pref: str | None) -> str`: honor explicit `pref`; else
  `torch.backends.mps.is_available() → "mps"`, else `"cpu"`. Removes the hardcoded `"mps"`
  so CI/Linux/non-Apple hosts don't crash. `torch` imported lazily inside the function.
- `resolve_dtype(device: str, use_fp16: bool)`: `float16` on `mps`/`cuda` when `use_fp16`,
  else `float32`; always `float32` on `cpu`. **bfloat16 deliberately avoided on MPS**
  (poorly optimized — up to ~10× slower; see Sources).

### B2. Settings additions — `settings.py` + `config.toml [service]`

Add to `Settings` (resolved via existing `_get`, overridable by `SEBI_RAG_*`):
- `device: str | None = None` (None = auto-detect).
- `use_fp16: bool = True`.
- `encode_batch_size: int = 32`.
- `embed_backend: str = "torch"`  (`torch` | `mlx`).
- `rerank_backend: str = "torch"` (`torch` | `mlx`).

### B3. Wire through — `embeddings.py`, `rerank.py`, `api.py`

- `BGEM3Embedder.__init__` and `CrossEncoderReranker.__init__` take resolved
  `device`, `use_fp16` (→ `use_fp16`/dtype), and `batch_size`.
- `build_default_pipeline` resolves `device` via `device.py` and passes Settings-derived
  values instead of the literal `"mps"`.
- **fp16 flip is eval-gated:** default lands on whatever `make bench-retrieval` /
  `make eval-asof` proves holds recall parity vs the current fp32 baseline. The knob ships
  either way; the *default value* is set by the A/B result and recorded in `reports/`.

### B4. MPS memory hygiene — `Makefile` ENV

Add `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0` (documented OOM guard for unified memory; a
full-corpus encode previously hit OOM). Keep existing `PYTORCH_ENABLE_MPS_FALLBACK=1`,
`HF_HUB_DISABLE_XET=1`, `TOKENIZERS_PARALLELISM=false`, `OMP_NUM_THREADS=1`, `PYTHONPATH=src`.

### B5. MLX-native backends — new `embeddings_mlx.py`, `rerank_mlx.py`

Selected when `embed_backend`/`rerank_backend == "mlx"`:
- `MLXEmbedder` satisfies the `Embedder` protocol (`dim=1024`, dense, L2-normalized) using a
  BGE-M3 MLX port.
- `MLXReranker` satisfies `.rerank(query, candidates) -> list[tuple[Chunk, float]]` using a
  bge-reranker-v2-m3 MLX port.
- `build_default_pipeline` selects torch vs MLX backends by Settings.
- **Eval-gated for parity:** an A/B (`make bench-retrieval` for embedder, reranker benchmark
  for reranker) must show recall/nDCG parity with the torch backend before MLX becomes a
  default. Until then it is opt-in via config/env.
- Packaging: MLX deps (`mlx`, `mlx-lm` already present; add an MLX embeddings/reranker dep)
  live in an **optional dependency group** so the torch-only install still works.

### B6. ANE / NPU — declined (record as ADR)

Write a short ADR (`docs/adr-003-ane-declined.md` or equivalent) recording the decision:
- ANE is an **energy-efficiency** engine (~2 W vs ~20 W GPU), **not a throughput** engine;
  for raw speed on a plugged-in Mac, MLX on the GPU wins (e.g., ~93+ tok/s vs ~9 tok/s on an
  8B model in published comparisons).
- ANE access requires **Core ML conversion** (`apple/ml-ane-transformers`), with finicky op
  support and significant engineering cost.
- This is a **server RAG on plugged-in Apple Silicon** — throughput-oriented, not
  battery/thermal/always-on constrained. ANE does not win on the metric that matters here.
- **Revisit only if** battery life, thermal envelope, or always-on background inference
  becomes an explicit goal.

### B7. Testing (Track B)

- `tests/test_device.py`: `pick_device` fallback matrix (explicit pref honored; mps when
  available; cpu otherwise), `resolve_dtype` selection, and no hard torch/mps dependency on
  the cpu path.
- Settings round-trip for the new fields (env > toml > default), including `SEBI_RAG_*`
  overrides.
- MLX backends: exercised under the existing `integration` marker (real weights, slow — same
  policy as the bge-m3/cross-encoder tests). `make test` (`-m "not integration"`) stays green
  and never loads MLX weights.

### B8. Sequencing (Track B)

1. B1–B4 (device abstraction, Settings, wiring, memory hygiene) — low risk, no quality delta
   except the eval-gated fp16 default.
2. B5 (MLX-native backends) — larger, opt-in, eval-gated; lands after B1–B4.
3. B6 (ADR) — can land any time; documents the boundary of the work.

---

## Consolidated file impact

| File | Track | Change |
|---|---|---|
| `src/sebi_rag/api.py` | A | `QueryRequest.mode`; per-mode pipeline cache; mode routing in `/query`; pass Settings compute fields in `build_default_pipeline` |
| `src/sebi_rag/ui.py` | A | New inputs (mode/as-of/advisory), `_parse_as_of` helper, banner + advisory rendering, Advanced-outputs accordion, layout regroup |
| `src/sebi_rag/device.py` (new) | B | `pick_device`, `resolve_dtype` |
| `src/sebi_rag/settings.py` | B | `device`, `use_fp16`, `encode_batch_size`, `embed_backend`, `rerank_backend` |
| `src/sebi_rag/embeddings.py` | B | `BGEM3Embedder` accepts device/fp16/batch; new `MLXEmbedder` (B5) |
| `src/sebi_rag/rerank.py` | B | `CrossEncoderReranker` accepts device/fp16/batch; new `MLXReranker` (B5) |
| `config.toml` `[service]` | B | New compute keys (documented defaults) |
| `Makefile` | B | `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0` in ENV |
| `docs/adr-003-ane-declined.md` (new) | B | ANE decision record |
| `tests/test_api.py` | A | mode routing + 422 + shared-retrieval tests |
| `tests/test_device.py` (new) | B | device/dtype + Settings round-trip |

**Untouched:** `pipeline.py`, `generate.py`, `retrieve.py`, all `*_spaces.py`, `app.py`.

---

## Sources — Apple-Silicon compute research (as of 22 July 2026)

Retained for future reference; findings that drove B1–B6.

**PyTorch MPS — dtype & memory**
- kokoro-coreml, PyTorch-MPS guide — fp16 vs bf16 vs fp32 on MPS; unified-memory OOM guard:
  https://github.com/mattmireles/kokoro-coreml/blob/main/README/Guides/apple-silicon/pytorch-mps.md
- "Accelerating PyTorch on Apple Silicon: A Practical Guide to MPS Optimization":
  https://medium.com/@bytethoughts/accelerating-pytorch-on-apple-silicon-a-practical-guide-to-mps-optimization-b607b1293e15
- "Apple Silicon PyTorch MPS: Setup and Speed":
  https://tillcode.com/apple-silicon-pytorch-mps-setup-and-speed-expectations/
- PyTorch MPS comprehensive guide (codegenes.net):
  https://www.codegenes.net/blog/pytorch-mps/
  - Key takeaways applied: for **inference**, `float16` is consistently faster than `bfloat16`
    and both beat `float32` (memory-bandwidth bound); **bf16 on MPS is poorly optimized**;
    `PYTORCH_MPS_HIGH_WATERMARK_RATIO` is the primary OOM defense on unified memory; MPS wins
    only at sufficient batch size (dispatch overhead dominates tiny batches).

**MLX — embeddings & rerankers on Apple Silicon**
- jina-ai/mlx-retrieval — train/run embedding + reranker models on Apple Silicon with MLX:
  https://github.com/jina-ai/mlx-retrieval
- MemTensor/mlx-memos — bge-reranker-v2-m3 MLX port:
  https://github.com/MemTensor/mlx-memos/tree/main/models/bge-reranker-v2-m3
- embed-rerank (PyPI) — local macOS/MLX embed+rerank service:
  https://pypi.org/project/embed-rerank/
- mlx-community — Embed + Rerank API for Apple Silicon (discussion):
  https://huggingface.co/spaces/mlx-community/README/discussions/20
  - Key takeaways applied: mature MLX ports exist for **BGE-M3 (dense/sparse/multi-vector,
    ~1.2 GB)** and **bge-reranker-v2-m3 / ModernBERT rerankers**; sub-ms single-text embed
    latency reported; viable end-to-end MLX path that drops the torch/MPS dependency.

**ANE / NPU — why declined**
- Apple ML Research — "Deploying Transformers on the Apple Neural Engine":
  https://machinelearning.apple.com/research/neural-engine-transformers
- apple/ml-ane-transformers — reference ANE-optimized Transformer:
  https://github.com/apple/ml-ane-transformers
- "Apple Neural Engine for LLM Inference: What Actually Works" (InsiderLLM):
  https://insiderllm.com/guides/apple-neural-engine-llm-inference/
  - Key takeaways applied: ANE optimizations can hit large latency/energy wins for encoder
    transformers **but** the win is **energy** (~2 W vs ~20 W GPU), not throughput — "for raw
    speed on a Mac, MLX on the GPU still wins"; requires Core ML conversion with finicky op
    support. Not worth it for a throughput-oriented, plugged-in server RAG.
