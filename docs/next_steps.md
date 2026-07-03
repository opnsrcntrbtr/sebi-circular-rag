# Next Steps — Structured Plans

Future-reference plans for three independent tracks. Each is self-contained; do them
in any order. Current baseline (2026-07-01): 29 circulars / 20,349 chunks, persisted
index (reload 0.34s), MLX-LM generation (~2.1s warm /query), calibrated top_k=3
(citation precision 0.97 / recall 1.0), 27 offline tests. See docs/status.md.

---

## (a) Quality bump — larger MLX model  — DONE (2026-07-01)

**Outcome:** sweep run (scripts/bench_generators.py) over golden_v3 — faithfulness
1.00 at all sizes; groundedness 0.84/0.89/0.95 (0.5B/1.5B/3B); latency 2.3/2.6/3.3s.
Default set to **Qwen2.5-1.5B-4bit**; 3B via SEBI_RAG_MLX_MODEL for max groundedness.
Faithfulness metric built and wired (see below). Original plan retained for record:

**Goal:** raise answer quality beyond the terse 0.5B baseline while keeping latency
acceptable; pick the smallest model that clears a quality bar.

**Approach — incremental, measured:**
1. Candidates (MLX 4-bit, Apple-Silicon): `Qwen2.5-1.5B-Instruct-4bit`,
   `Qwen2.5-3B-Instruct-4bit`, `Llama-3.2-3B-Instruct-4bit`. Keep 0.5B as the
   speed floor.
2. Pull each once (`HF_HUB_DISABLE_XET=1`; large weights are Xet-backed — see
   docs/scraping_plan note). Set `SEBI_RAG_MLX_MODEL` to switch; no code change
   (already parameterised in api.py / MLXGenerator).
3. Measure per model on the same queries: generation latency, end-to-end /query
   latency, and groundedness (does the answer stay within cited context, no
   hallucinated circular numbers).
4. ~~Extend the eval harness with a faithfulness check~~ **DONE (2026-07-01)**:
   `generate.faithfulness` flags bracketed citations absent from context; pipeline
   adds a caveat; /query exposes faithfulness + unsupported_citations; eval-harness
   has a `faithfulness` metric. Remaining: use it to compare models in the sweep.

**Files:** `scripts/` (new `bench_generators.py` to sweep models × queries),
`src/sebi_rag/eval_harness.py` (faithfulness metric), `docs/status.md`.

**Decision rule:** choose the smallest model with faithfulness ≥ target and
end-to-end /query under the latency budget (e.g. ≤ 5s warm). Record choice +
numbers in project_context §7.

**Risks:** larger models raise latency and memory (48 GB is ample for ≤3B-4bit);
download time/throttling (mitigated by hf-xet). Keep 0.5B as fallback.

---

## (b) Packaging / deployment  — DONE (2026-07-01)

**Outcome:** config.toml + src/sebi_rag/settings.py (env > file > default, tested);
Lineage.save/load persisted to data/index/lineage.json (build_index.py writes it,
api.py loads it); /ready + config-reporting /health; Makefile, run.sh, launchd plist
in deploy/. `make reindex` = annotate + build index. Original plan kept for record:

**Goal:** make the service reproducibly runnable and operable, not a hand-started
uvicorn.

**Steps:**
1. **Config file** — a single `config.toml` (or env-loaded settings model) for:
   index path, corpus path, generator (mlx/ollama) + model, top_k, abstain
   threshold, superseded_penalty, rate limit, timeout, API key source. Load via a
   small `settings.py`; env vars override file. Removes scattered `os.environ`.
2. **Persist the lineage graph** alongside the index. Today `build_lineage` runs on
   every startup (cheap at 29 circulars, but grows). Save `lineage.json`
   (supersedes / superseded_by / amends maps) in `data/index/` from
   `scripts/build_index.py`; load it in api.py. Add `Lineage.save/load` mirroring
   the retriever. Rebuild only when the corpus changes (checksum guard).
3. **Process manager** — a `launchd` plist (macOS-native) or a `Makefile` /
   `run.sh` target that exports env, activates `.venv`, and runs uvicorn with
   `--workers 1` (MPS is single-process). Document start/stop/logs.
4. **Build-on-change** — a `make reindex` target: ingest new PDFs → annotate
   lineage → build_index → save lineage. One command after corpus changes.
5. **Health/readiness** — extend `/health` to report index build time, model name,
   generator, and lineage version; add `/ready` (200 only once the pipeline is
   built) for process supervision.

**Files:** new `src/sebi_rag/settings.py`, `config.toml`, `Makefile`/`run.sh`,
`deploy/com.sebi-rag.plist`; edits to `src/sebi_rag/lineage.py` (save/load),
`scripts/build_index.py`, `src/sebi_rag/api.py`.

**Validation:** cold start loads index + lineage in <2s; `make reindex` reproduces
`data/index/` deterministically; service restarts cleanly via the process manager.

**Risks:** MPS forbids multi-worker — pin `--workers 1` and scale by request
queueing, not processes. Keep secrets (API key) out of `config.toml` (env only).

---

## (c) Grow the corpus via the scraper  — IMPLEMENTED (2026-07-01)

**Outcome:** scraper now supports `--section circulars|master-circulars` (Circulars
confirmed ssid=7, ~2.8k records), POST pagination with a no-advance guard,
`--from/--to` date filtering, and `--ocr` fallback (ingest_pdf). Offline-tested
(parse_rows, date filter, no-advance, regex). REMAINING: verify the live POST
pagination params on a first >1-page run (guard stops safely if they need tuning);
install OCR deps only if scanned PDFs appear. Original plan kept for record:

**Goal:** expand beyond the current 29 (mostly master) circulars toward broad
coverage, safely and reproducibly. Plan/legality detail in docs/scraping_plan.md.

**Steps:**
1. **Verify pagination** — current `scrape_sebi.py` relies on `&nextValue=`; SEBI
   paginates via a JS POST. Confirm the real request in the browser network tab and
   update the `LISTING` / discovery block so >1 page works (needed for batches >25).
2. **Add the regular Circulars sub-section** — `ssid=6` is Master Circulars; find
   the ssid for "Circulars" (thousands of records) and pass via `--listing`. The
   URL regex already matches both `/legal/circulars/` and `/legal/master-circulars/`.
3. **Batch with date filtering** — add `--from/--to`; stop paging when issue dates
   pass the bound. Run in bounded batches (`--max 25–50`, `--rate 3`), off-peak.
4. **Per-batch validation** (after each run): `wc -l` corpus, spot-check 3 records'
   number/date/subject, `annotate_corpus` (supersession), `pytest -m "not
   integration"`, then `scripts/build_index.py` (re-embed — ~6 min/20k chunks; scales
   with corpus) and re-run `scripts/calibrate.py`.
5. **OCR fallback** — scanned/image PDFs yield no text from pdfplumber and currently
   raise. Add an OCR path (ocrmypdf / pytesseract) gated behind a `--ocr` flag; flag,
   don't silently skip.
6. **Expand the golden set** in step with the corpus — add discriminating queries
   for new departments/topics so calibration stays meaningful; keep one in-force
   label per topic (supersession demotion handles versions).

**Files:** `scripts/scrape_sebi.py` (pagination, date filter, ssid, OCR),
`eval/golden/golden_v3.jsonl` (grow), `docs/scraping_plan.md`, `docs/status.md`.

**Execution note:** the scraper runs on the user's machine (Claude's web tools are
restricted from bulk fetch). Claude handles ingest validation, lineage, index
rebuild, and recalibration on the results.

**Risks:** index rebuild time grows with corpus (mitigated by persistence + the
checksum-guarded `make reindex`); format drift across departments (header parser
already handles 2026 + legacy, raises on unknown rather than mis-tagging); rate
limits (polite defaults already in place).
