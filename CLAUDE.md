# CLAUDE.md

Local-first, Apple Silicon RAG over Indian SEBI Circulars. FastAPI + Gradio UI. Hybrid retrieval (FAISS + BM25) with cross-encoder reranking, citation generation, supersession-aware lineage.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `make serve` | FastAPI backend on port 8000 |
| `make ui` | Gradio UI dashboard |
| `make test` | Offline tests (`pytest -q -m "not integration"`) — 790 passed |
| `make reindex` | Annotate corpus + rebuild index |
| `make index` | Build/persist FAISS+BM25 only |
| `make scrape` | Fetch SEBI circulars (MAX=N) |
| `make calibrate` | Retrieval calibration sweep |
| `make eval-asof` | As-of-date golden eval |
| `make bench-retrieval` | Retrieval-only benchmark |
| `make bench-rerank` | Reranker benchmark |
| `make measure` | Pipeline metrics (parsing latency, recall, MRR) |
| `make golden-v7-gate` | CI gate (refuses <100 adjudicated) |
| `make validate-corpus` | Corpus integrity check after ingest/repair |

Full targets: `README.md`.

## Context Files (read on demand)

| File | When to read |
|------|-------------|
| `docs/project_context.md` | Architecture details, validation sequence (12 steps), calibration params, golden-set info, directory structure |
| `docs/status.md` | Completed work, blockers, historical decisions. Read before requesting info. Infer status from here first. |

## Architecture

Pipeline: `scrape → ingest_pdf → lineage.annotate → build_index → retrieve → rerank → generate`

| Module | Purpose |
|--------|---------|
| `src/sebi_rag/api.py` | FastAPI entry, app factory, key-in-body auth |
| `src/sebi_rag/pipeline.py` | `RAGPipeline` orchestration; `regulatory_basis_status` per-citation |
| `src/sebi_rag/retrieve.py` | `HybridRetriever` — FAISS + BM25 RRF fusion (SPLADE eval-only) |
| `src/sebi_rag/rerank.py` / `embeddings.py` | Cross-encoder / BGE-M3 embedding |
| `src/sebi_rag/segment.py` | Hierarchical chunking (`CircularMeta`, `Chunk`) |
| `src/sebi_rag/lineage.py` | Supersession tracking + corpus annotation |
| `src/sebi_rag/regulations.py` | Regulation identity, alias table, name resolution |
| `src/sebi_rag/reg_citations.py` | Regulation citations from circular text |
| `src/sebi_rag/reg_lineage.py` | Circular→regulation edges + `regulatory_basis_status` |
| `src/sebi_rag/generate.py` | Local generation + abstention gate (MLX-LM/Ollama) |
| `src/sebi_rag/eval.py` / `eval_harness.py` / `benchmark.py` | Metrics, golden-set runner, BEIR/TREC export |
| `src/sebi_rag/splade.py` / `hyde.py` / `context_headers.py` | Retrieval experiments (opt-in, off by default) |

### ⚠️ Two parallel code paths

`*_spaces.py` (`api_spaces`, `corpus_spaces`, `generate_spaces`) + root `app.py` = CPU-only HF Spaces demo — no MLX/MPS. **Do not edit when fixing Apple-Silicon pipeline.** Config in `config.toml [spaces]`; runbook in `README-spaces.md`.

### ⚠️ Never add fields to `CircularMeta`

`hierarchical_chunk()` does `meta=asdict(meta)` (`segment.py:131`). New fields land in every chunk payload (78k chunks) and mutate the persisted index. Additive per-circular metadata goes on corpus JSONL record only — see `master_meta.annotate_master_fields` and `reg_lineage.annotate_regulation_fields`.

## Testing & Evaluation

- Golden sets: `eval/golden/`; benchmark runs: `eval/runs/`
- `golden_v7.jsonl` (n=260) is the reporting set; CI gates on `adjudicated_n >= 100`
- Interventions specced in `docs/superpowers/specs/`, planned in `plans/`, results in `reports/`

## Environment

| Variable | Value / Purpose |
|----------|----------------|
| `SEBI_RAG_API_KEY` | API auth token (FastAPI key-in-body guard) |
| `HF_HUB_DISABLE_XET=1` | Disable Xet-backed HF downloads (throttle workaround) |
| `TOKENIZERS_PARALLELISM=false` | Prevent fork safety warnings |
| `OMP_NUM_THREADS=1` | Avoid thread contention |
| `PYTORCH_ENABLE_MPS_FALLBACK=1` | Enable MPS fallback for unsupported ops |
| `PYTHONPATH=src` | Set via Makefile ENV |
| `PORT` | Default 8000; override: `PORT=9000 make serve` |
| `SEBI_RAG_GENERATOR` | `mlx` or `ollama` (default: mlx) |
| `SEBI_RAG_MLX_MODEL` | MLX model override (default: Qwen2.5-0.5B-4bit) |

## Principles

- Local-first, reproducible engineering
- Apple Silicon first (MLX/MLX-LM preferred)
- Treat official SEBI publications as authoritative

## Refusal Criteria (explicit triggers)

| Trigger | Response |
|---------|----------|
| Insufficient retrieved evidence for legal/regulatory question | "I don't know based on the available evidence." |
| Request to redesign architecture without explicit instruction | "Not without explicit request. Current architecture is validated — 790 tests passing." |
| Request to review files not provided | "I can only review files you provide. Please supply the diff or file contents." |
| Request to fabricate citations, legal interpretations, or data | Refuse outright. No fabrication of SEBI circulars, regulations, or metrics. |
| Retrieval confidence below abstention threshold (~0.4) | Return evidence only; do not generate a conclusion. |
| Task outside coding agent scope (infra ops, non-code) | Decline and suggest appropriate owner/tool. |

**Golden rule**: When in doubt, say "I don't know based on the available evidence." — never guess.

## Workflow Conventions

### Code Review
Review only supplied files. Never infer contents of unseen files. If changes elsewhere are needed, describe them abstractly and request those files.

### Debugging
Inputs: Goal, Command, Last 20–30 log lines. Return: PASS/FAIL, one root cause, one best fix, verification command.

### Performance
Optimize only validated stages. Recommend changes expected to produce measurable (>10%) benefit.

### Status Documentation
Maintain `docs/status.md` as high-density context anchor:
- Convert prose to YAML/JSON key-value blocks
- Use emoji flags (✅, ⚠️, ❌, ⏳) and single-line tables
- Zero meta-commentary — only facts
- Preserve retrieval anchors: file paths, API routes, variable names must match character-for-character

### Output Format
- Explicit schemas (JSON, markdown tables, bullet lists)
- Ask for diffs instead of full rewrites
- Concise — prefer bullets over prose
- Validation fail: Status, Reason, Root cause, Exact commands, Verification command
- Validation pass: PASS + Next recommended step

### Session Management
- Split work into phases: discovery → implementation → verification. Start fresh sessions (`/new`) per phase.
- Carry forward specs/summaries between sessions via files (write to file, read in next session).
- Use `--fork` to branch from decision points without stale history.

### Model Routing
- Simple tasks (extraction, classification, formatting, short edits) → `low` thinking
- Standard tasks (debugging, multi-file changes, testing) → `medium` thinking
- Complex tasks (architecture decisions, validation sequences, complex refactoring) → `high` thinking via `/model`

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
