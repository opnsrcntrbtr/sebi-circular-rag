# SEBI Circular RAG — Usage Guide

A local-first, Apple-Silicon Retrieval-Augmented Generation system over Indian SEBI
circulars. The current stack scrapes official circulars, segments and indexes them,
retrieves with hybrid search + cross-encoder reranking, generates grounded answers
with an abstention gate, and returns citations with supersession status and a
faithfulness check behind a config-driven, authenticated FastAPI service.

This guide covers setup, the data pipeline, running and querying the service,
configuration, operations, evaluation, extension, and troubleshooting. For the
current shipped state see [docs/status.md](status.md); for roadmap details see
[docs/next_steps.md](next_steps.md); for the user-facing overview see the project
[README.md](../README.md).

---

## 1. Concepts at a glance

```
scrape (SEBI) ─▶ data/raw/*.pdf ─▶ ingest_pdf ─▶ data/corpus/circulars.jsonl
                                                        │
                            lineage (supersession) ◀────┤
                                                        ▼
                              build_index ─▶ data/index/ (FAISS + BM25 + chunks + lineage)
                                                        │
   query ─▶ hybrid retrieve (dense bge-m3 + sparse BM25 + RRF)
              ─▶ cross-encoder rerank (+ demote superseded)
              ─▶ MLX generation (abstain if weak) + faithfulness check
              ─▶ answer + citations + supersession + faithfulness
```

- **Hybrid retrieval:** FAISS dense (bge-m3) + BM25 sparse, fused by Reciprocal Rank
  Fusion. Legal text needs exact matches (circular numbers, dates), hence hybrid.
- **Reranking:** `bge-reranker-v2-m3` cross-encoder; chunks from superseded circulars
  are demoted so the in-force version is cited.
- **Abstention:** if the top reranked score is below threshold, the system answers
  "I don't know based on the available evidence." rather than guessing.
- **Faithfulness:** any circular the answer cites in brackets is checked against the
  retrieved context; unsupported citations are flagged.
- **Supersession:** a lineage graph marks each circular in_force / superseded /
  amended and records which circular supersedes which.

---

## 2. Requirements & setup

- macOS on Apple Silicon (built/validated on M4 Pro, 48 GB). MPS is used for models.
- Python 3.12 (project venv `.venv`), `uv`, Homebrew, Xcode CLT, Git.
- Optional: Ollama (alternative generator); Tesseract + Poppler (OCR of scanned PDFs).

Install dependencies into the pinned venv:

```
uv venv -p 3.12 .venv
uv pip install -p .venv/bin/python \
    mlx mlx-lm torch sentence-transformers FlagEmbedding faiss-cpu bm25s hf-xet \
    pdfplumber fastapi uvicorn
uv pip install -p .venv/bin/python pytest reportlab httpx        # dev/test
```

First model use downloads weights from Hugging Face (bge-m3 ~2.3 GB, cross-encoder
~2.2 GB, MLX model ~1 GB). Authenticate for higher rate limits: `.venv/bin/hf auth
login`.

**Environment guards (always set these when running models):**

```
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src
```

They are required — running bge-m3 (FlagEmbedding) and the cross-encoder together on
MPS segfaults without `TOKENIZERS_PARALLELISM=false` / `OMP_NUM_THREADS=1`. The
`Makefile` and `run.sh` set them for you.

---

## 3. Directory structure

```
SEBI circular RAG/
├── config.toml                 # service configuration (env-overridable)
├── Makefile / run.sh           # operations
├── deploy/com.sebi-rag.plist   # launchd user agent
├── data/
│   ├── raw/                    # downloaded PDFs (+ .sha256 dedupe files)
│   ├── corpus/circulars.jsonl  # one JSON record per circular (text + metadata)
│   └── index/                  # persisted: dense.faiss, bm25/, chunks.jsonl,
│                               #            meta.json, lineage.json
├── eval/golden/golden_v6.jsonl # labelled evaluation set (query -> relevant circulars)
├── scripts/                    # scrape, ingest, build_index, calibrate, bench, ...
├── src/sebi_rag/               # the package (see §9)
├── tests/                      # offline test suite
└── docs/                       # project_context, status, next_steps, this guide, ...
```

---

## 4. The data pipeline

All commands run from the repo root. The `Makefile` wraps them with the env guards.

### 4.1 Scrape circulars (runs on your machine)

```
PYTHONPATH=src .venv/bin/python scripts/scrape_sebi.py \
    --section circulars --from 2025-01-01 --to 2026-06-30 --max 100 --rate 3
```

- `--section` `circulars` (ssid=7, ~2.8k) or `master-circulars` (ssid=6, ~135).
- `--from/--to` issue-date window (YYYY-MM-DD); discovery stops once older than `from`.
- `--max` cap per run; `--rate` seconds between requests (be polite, ≥3).
- `--ocr` enables OCR fallback for scanned PDFs (needs the OCR deps).

It discovers via SEBI's AJAX pager (POST `/sebiweb/ajax/home/getnewslistinfo.jsp`
with `doDirect=<page>`), downloads each PDF to `data/raw/` (SHA-256 deduped), and
ingests it. Legality: SEBI robots.txt allows `/legal/circulars` and the PDF store;
the scraper rate-limits, sends a descriptive User-Agent, and records the official
`source_url`. See `docs/scraping_plan.md`.

### 4.2 Ingest a single PDF

```
PYTHONPATH=src .venv/bin/python -m sebi_rag.ingest_pdf data/raw/<file>.pdf \
    --source-url "<official url>" [--replace] [--ocr]
```

Extracts circular number, issue date (and "Last updated on" as effective date for
master circulars), subject, issuing department, and version lineage; records
provenance; dedupes by circular number.

### 4.3 Resolve supersession + rebuild the index

```
make reindex        # = annotate lineage in the corpus, then build+persist the index
```

`reindex` runs (a) `lineage.annotate_corpus` (updates each record's
supersession_status / superseded_by) and (b) `scripts/build_index.py` which encodes
every chunk with bge-m3 (the slow step, ~5 min for ~22k chunks) and writes
`data/index/` including `lineage.json`. Re-run after any corpus change.

### 4.4 Maintenance helpers

- `scripts/renumber.py` — re-derive circular numbers/dates from stored text after a
  parser improvement (no re-download); then `make reindex`.
- `scripts/build_golden.py` — regenerate the evaluation set from the current corpus.

---

## 5. Running the service

```
make serve                 # PORT=8000 by default; set SEBI_RAG_API_KEY in the env
# or:
SEBI_RAG_API_KEY=secret ./run.sh
```

MPS is single-process, so the server runs with `--workers 1`. The pipeline (index +
models) loads lazily on the first request (~10–15 s cold), then stays resident.

### Endpoints

| Method | Path      | Auth | Purpose |
|--------|-----------|------|---------|
| GET    | `/ready`  | no   | `{"ready": bool}` — true once the pipeline is built |
| GET    | `/health` | no   | status + chunk/circular counts + active config |
| POST   | `/query`  | yes* | run a query (see below) |

\* `/query` requires the `X-API-Key` header **only if** `SEBI_RAG_API_KEY` is set.

### Query request

```
POST /query
Content-Type: application/json
X-API-Key: <your key>

{ "question": "Master circular for mutual funds", "top_k": 3 }   # top_k optional
```

### Query response

```json
{
  "answer": "…grounded answer…",
  "citations": ["<chunk id>", …],
  "citations_meta": [
    {"circular": "HO/…/2026", "status": "in_force", "superseded_by": []}
  ],
  "abstained": false,
  "superseded": {},                     // cited circular -> [superseding circulars]
  "faithfulness": 1.0,                  // fraction of bracketed citations grounded
  "unsupported_citations": [],          // bracketed citations not in retrieved context
  "retrieved": ["<chunk id>", …],       // top retrieved chunk ids (≤20)
  "latency_ms": 2100.4
}
```

**Field meaning**

- `abstained` — true when evidence was too weak; `answer` is the abstention string.
- `citations` / `citations_meta` — the chunks used; each circular's supersession
  status. If a cited circular is superseded, the answer text also appends a note.
- `faithfulness` = 1.0 means every circular the model cited in brackets was actually
  in the retrieved context; < 1.0 lists offenders in `unsupported_citations` and the
  answer carries a caution note.
- `latency_ms` — end-to-end processing time.

### Example

```
curl -s -X POST http://127.0.0.1:8000/query \
  -H 'Content-Type: application/json' -H 'X-API-Key: secret' \
  -d '{"question":"What are the modified norms for nomination in demat accounts?"}'
```

### Errors

- `401` — missing/incorrect `X-API-Key` (when a key is configured).
- `429` — rate limit exceeded (`SEBI_RAG_RATE_PER_MIN` per key or IP per minute).
- `504` — query exceeded `SEBI_RAG_TIMEOUT_S`.

---

## 6. Configuration

Edit `config.toml` (`[service]` table) or override any field with `SEBI_RAG_<FIELD>`
(uppercased). Precedence: **env var > config.toml > built-in default**.

| Field | Default | Meaning |
|-------|---------|---------|
| `generator` | `mlx` | `mlx` (Apple-Silicon native) or `ollama` |
| `mlx_model` | `mlx-community/Qwen2.5-1.5B-Instruct-4bit` | MLX model; use the 3B for higher groundedness |
| `top_k` | `3` | contexts passed to the LLM / cited (calibrated) |
| `abstain_threshold` | `0.40` | cross-encoder score gate for abstention |
| `superseded_penalty` | `0.3` | rerank multiplier for superseded chunks (0 = drop) |
| `rate_per_min` | `60` | requests/min per key or IP |
| `timeout_s` | `30` | `/query` time budget → 504 |

Secrets are **env only**: `SEBI_RAG_API_KEY` (never put it in `config.toml`).
Paths `corpus_path` / `index_dir` default to `data/corpus/circulars.jsonl` and
`data/index`.

Examples:

```
SEBI_RAG_MLX_MODEL=mlx-community/Qwen2.5-3B-Instruct-4bit make serve   # higher quality
SEBI_RAG_GENERATOR=ollama make serve                                   # use Ollama
SEBI_RAG_RATE_PER_MIN=120 SEBI_RAG_TIMEOUT_S=15 make serve
```

---

## 7. Operations

- **Makefile targets:** `make help | test | scrape | annotate | index | reindex |
  calibrate | serve`. Variables: `PORT` (serve), `MAX` (scrape).
- **Run as a background service (macOS launchd):**
  ```
  # edit deploy/com.sebi-rag.plist: set the paths and SEBI_RAG_API_KEY
  cp deploy/com.sebi-rag.plist ~/Library/LaunchAgents/
  launchctl load ~/Library/LaunchAgents/com.sebi-rag.plist     # start (RunAtLoad + KeepAlive)
  launchctl unload ~/Library/LaunchAgents/com.sebi-rag.plist   # stop
  ```
  Logs: `/tmp/sebi-rag.out.log`, `/tmp/sebi-rag.err.log`.
- **After adding circulars:** `make reindex` (then optionally `make calibrate`).
- **Readiness/health probes:** poll `GET /ready` for supervision; `GET /health` to
  confirm the active model, generator, corpus size, and rate limit.

---

## 8. Evaluation

The eval set `eval/golden/golden_v6.jsonl` maps queries to the relevant in-force
circular(s). The harness computes retrieval Recall@k, MRR, nDCG, citation precision /
recall, abstention accuracy, faithfulness, and latency.

```
make calibrate      # sweeps top_k × abstain_threshold over the golden set
```

Current profile (124 circulars): recall@10 = 1.0, citation_recall = 1.0 @ top_k=3,
abstention = 1.0, faithfulness = 1.0, citation precision ≈ 0.73–0.77. Interpretation:
the governing circular is always retrieved and cited; precision reflects genuinely-
related circulars co-surfacing in a dense corpus rather than a retrieval defect.

Benchmark generator models:

```
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src .venv/bin/python scripts/bench_generators.py
```

Regenerate the golden set from the current corpus: `python scripts/build_golden.py`.

---

## 9. Package modules (`src/sebi_rag/`)

| Module | Responsibility |
|--------|----------------|
| `segment.py` | hierarchical, clause-aware chunking + metadata + stable chunk IDs |
| `embeddings.py` | `Embedder` protocol; `BGEM3Embedder` (MPS); `HashEmbedder` (offline tests) |
| `retrieve.py` | `DenseIndex` (FAISS), `SparseIndex` (bm25s), `rrf_fuse`, `HybridRetriever` (+ save/load) |
| `rerank.py` | `CrossEncoderReranker` (bge-reranker-v2-m3); `LexicalReranker` (offline) |
| `lineage.py` | supersession graph, re-issue detection, `demote_superseded`, save/load |
| `generate.py` | `MLXGenerator`, `OllamaGenerator`, abstention gate, `faithfulness` |
| `pipeline.py` | wires retrieve → rerank → demote → generate; supersession + faithfulness on the answer |
| `ingest_pdf.py` | PDF → corpus record (number/date/subject/lineage), dedupe, OCR hook |
| `corpus.py` | load circulars → chunks |
| `eval.py` / `eval_harness.py` | metrics + golden-set runner |
| `api.py` | FastAPI app (auth, rate limit, timeout, endpoints) |
| `settings.py` | config.toml + env loading |

The pipeline depends on `Embedder`/`Reranker`/`Generator` protocols, so tests run
offline with lightweight stand-ins and production injects the real models.

---

## 10. Extending

- **Change the LLM:** set `SEBI_RAG_MLX_MODEL` (e.g. `…Qwen2.5-3B-Instruct-4bit`) or
  `SEBI_RAG_GENERATOR=ollama`. No code change.
- **Tune retrieval:** adjust `top_k`, `abstain_threshold`, `superseded_penalty` in
  `config.toml`, then `make calibrate` to check the effect.
- **Swap the embedder/reranker:** implement the `Embedder` / `Reranker` protocol and
  wire it in `api.build_default_pipeline`; rebuild the index.
- **Add circulars:** scrape or `ingest_pdf`, then `make reindex`.

---

## 11. Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| Segfault / "leaked semaphore" loading models | Missing env guards — set `TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 PYTORCH_ENABLE_MPS_FALLBACK=1` (Makefile/run.sh do this). |
| HF download stalls at ~93 % | Xet throttling — ensure `hf-xet` is installed, run `hf auth login`, and set `HF_HUB_DISABLE_XET=1` (weights resume). |
| `mlx-lm` won't install | Needs Python 3.12 — the project venv is pinned to 3.12 (no 3.14 wheels). |
| Ingest: "No SEBI circular number found" | Scanned/image PDF — re-ingest with `--ocr` (install `pytesseract pdf2image` + tesseract/poppler). |
| Odd numbers like `HO/(92)2026-…` | pdfplumber dropped digits in that PDF; parser is correct. OCR or manual fix; `renumber.py` re-derives fixable cases. |
| Scrape stops after 25 (`pagination did not advance`) | Page-0 only — the AJAX pager params changed; re-verify `_page()` (see docs/scraping_plan.md). Non-fatal: keeps page-0 results. |
| `/query` returns 504 | Generation slower than `SEBI_RAG_TIMEOUT_S`; raise it, or use a smaller MLX model. |
| First `/query` slow (~10–15 s) | Cold model load; subsequent queries are ~2–4 s. Use `/ready` to warm-gate. |

---

## 12. Testing

```
make test        # offline suite (no model downloads); should be all green
```

Integration tests that exercise the real bge-m3 + cross-encoder + generator are
marked `integration` and skipped by default; run them with
`.venv/bin/python -m pytest -m integration`.

---

## 13. Legal & safety notes

- Treat SEBI publications as authoritative; the system abstains rather than guessing
  when evidence is insufficient, and flags any citation not grounded in retrieved
  context (faithfulness). It is an assistant, not legal advice.
- The scraper respects `robots.txt`, rate-limits, records provenance, and never
  bypasses logins/captchas. Review SEBI's Terms of Use before redistribution.
- Superseded circulars are demoted and flagged so answers reference the in-force
  version; always confirm currency against the official source for legal use.
```
