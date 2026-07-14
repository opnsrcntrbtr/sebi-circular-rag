# Dataset Card Accuracy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the root cause of stale numbers on the live `opnsrcntrbtrian/sebi-circulars` dataset card (hardcoded literals in `scripts/export_datasets.py`'s four card generators), regenerate and repush the corrected card, hand-correct `README.md`, and redeploy the Space so its README matches the already-fixed local `README-spaces.md`.

**Architecture:** A new `_compute_stats(out_dir)` helper in `scripts/export_datasets.py` reads the just-exported `dist/datasets/corpus/corpus.jsonl` to derive the `issuing_department` UNKNOWN fraction, the corpus's real min/max `issue_date`, and today's date. `write_dataset_cards()` computes this once and threads it through all four card-generator functions as a new `stats` parameter, replacing every hardcoded number with a value read from `datasets[cfg]["rows"]` (already available, just unused) or the new `stats` dict.

**Tech Stack:** Python 3.12–3.13, stdlib only (`re`, `json`, `datetime`), pytest, existing `push_datasets.py`/`deploy_space.py` scripts.

## Global Constraints

- `PYTHONPATH=src` not required for `scripts/export_datasets.py` (it's a standalone script under `scripts/`, imported directly in tests via `sys.path.insert(0, str(ROOT / "scripts"))` — see `tests/test_dataset_cards.py:11`).
- Offline test suite must stay green at every task boundary: `.venv/bin/python -m pytest -q -m "not integration"` (baseline 233 passed, per the master-circular-coverage plan's final state).
- Stored numbers reflect real, computed data — never re-hardcode a literal that could drift; every number in a card must trace to `datasets[cfg]["rows"]` or `stats[...]`.
- `dist/datasets/` and `graphify-out/` are gitignored — do not `git add` them; only commit tracked files (`scripts/export_datasets.py`, `tests/test_dataset_cards.py`, `README.md`, `README-spaces.md`).
- Live HF pushes (`push_datasets.py --yes`, Space redeploy) are shared, hard-to-reverse actions — pause for explicit user confirmation before running them, per this repo's established pattern (master-circular-coverage plan Tasks 9–10).
- Commit after every task.

## Ground truth (measured 2026-07-14)

```
corpus rows: 705       chunks rows: 77,859     lineage rows: 4,483
eval rows: 56           citation-normalization rows: 8,802
supersession-pairs rows: 2,769
issuing_department UNKNOWN: 158/705
issue_date range: 2010-04-06 to 2026-07-07
```

## File Structure

| Path | Responsibility |
|------|----------------|
| `scripts/export_datasets.py` (modify) | Add `_compute_stats()`; thread `stats` param through `build_hf_card`, `build_kaggle_metadata`, `build_zenodo_pack`, `build_aikosh_pack`; replace hardcoded literals |
| `tests/test_dataset_cards.py` (modify) | Update all existing card-builder tests to pass `stats` explicitly; add dynamism + manifest-accuracy regression tests |
| `README.md` (modify) | Dataset Configurations table, corpus-count prose, coverage disclaimer, UNKNOWN caveat |
| `README-spaces.md` (modify, maybe) | Audit for any other stale numeric mention beyond the already-fixed corpus line |

---

### Task 1: `_compute_stats()` helper + wire `stats` through all four builder signatures + fix `build_hf_card`

**Files:**
- Modify: `scripts/export_datasets.py` (add helper near top of "Task 4: Dataset Cards" section, ~line 400; modify `build_hf_card` signature and body, ~lines 403–580; modify `build_kaggle_metadata`, `build_zenodo_pack`, `build_aikosh_pack` signatures only — bodies fixed in Tasks 2–4; modify `write_dataset_cards`, ~line 676)
- Test: `tests/test_dataset_cards.py`

**Interfaces:**
- Consumes: nothing new (stdlib `re`, `json`, `datetime` — `datetime` needs a new top-of-file import).
- Produces: `_compute_stats(out_dir: Path) -> dict` returning `{"snapshot_date": str, "dept_unknown": int, "dept_total": int, "date_min": str, "date_max": str}`. Later tasks (2–4) consume this exact dict shape via the `stats` parameter now present on all four builders.
- New builder signatures (Tasks 2–4 rely on these exact names/order):
  `build_hf_card(datasets: dict[str, dict], stats: dict) -> str`
  `build_kaggle_metadata(datasets: dict[str, dict], stats: dict) -> str`
  `build_zenodo_pack(datasets: dict[str, dict], stats: dict) -> dict`
  `build_aikosh_pack(datasets: dict[str, dict], stats: dict) -> dict`

- [ ] **Step 1: Write the failing tests**

```python
# append to tests/test_dataset_cards.py
def test_compute_stats_from_exported_corpus(tmp_path):
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    rows = [
        {"circular_number": "A/1", "issue_date": "2019-03-01", "issuing_department": "CFD"},
        {"circular_number": "A/2", "issue_date": "2024-06-15", "issuing_department": None},
        {"circular_number": "A/3", "issue_date": "2021-01-10", "issuing_department": ""},
    ]
    (corpus_dir / "corpus.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    stats = X._compute_stats(tmp_path)
    assert stats["dept_unknown"] == 2
    assert stats["dept_total"] == 3
    assert stats["date_min"] == "2019-03-01"
    assert stats["date_max"] == "2024-06-15"
    assert stats["snapshot_date"]  # non-empty, computed today


def test_compute_stats_ignores_non_iso_dates(tmp_path):
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    rows = [
        {"circular_number": "A/1", "issue_date": "2020-05-01", "issuing_department": "CFD"},
        {"circular_number": "A/2", "issue_date": None, "issuing_department": "MRD"},
        {"circular_number": "A/3", "issue_date": "not-a-date", "issuing_department": "MRD"},
    ]
    (corpus_dir / "corpus.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    stats = X._compute_stats(tmp_path)
    assert stats["date_min"] == stats["date_max"] == "2020-05-01"
```

Now update the three EXISTING tests in `tests/test_dataset_cards.py` that call `X.build_hf_card(datasets)` with one argument — they must pass `stats` too, and the row-count/UNKNOWN assertions must use values that couldn't pass by coincidence with the old hardcoded literals (proving dynamism, not just echoing back `603`/`124`):

```python
# REPLACE test_hf_card_includes_actual_row_counts in tests/test_dataset_cards.py
def test_hf_card_includes_actual_row_counts():
    """Card must cite actual row counts from datasets, not hardcoded literals."""
    datasets = {
        "corpus": {"rows": 705, "schema": X.CORPUS_SCHEMA},
        "chunks": {"rows": 77859, "schema": X.CHUNKS_SCHEMA},
        "citation-normalization": {"rows": 8802, "schema": X.CITATION_SCHEMA},
        "supersession-pairs": {"rows": 2769, "schema": X.SUPERSESSION_SCHEMA},
    }
    stats = {"snapshot_date": "2026-07-14", "dept_unknown": 158, "dept_total": 705,
             "date_min": "2010-04-06", "date_max": "2026-07-07"}
    card = X.build_hf_card(datasets, stats)
    assert "705" in card
    assert "77,859" in card or "77859" in card
    assert "8,802" in card or "8802" in card
    assert "2,769" in card or "2769" in card
    assert "603" not in card       # old hardcoded value must be gone
    assert "34,883" not in card and "34883" not in card


# REPLACE test_hf_card_includes_data_quality_caveats in tests/test_dataset_cards.py
def test_hf_card_includes_data_quality_caveats():
    """Card must document known data-quality issues using computed stats."""
    datasets = {k: {"rows": 705, "schema": v} for k, v in [
        ("corpus", X.CORPUS_SCHEMA), ("chunks", X.CHUNKS_SCHEMA)]}
    stats = {"snapshot_date": "2026-07-14", "dept_unknown": 158, "dept_total": 705,
             "date_min": "2010-04-06", "date_max": "2026-07-07"}
    card = X.build_hf_card(datasets, stats)
    assert "158" in card and "705" in card  # UNKNOWN count, computed not hardcoded
    assert "124" not in card                # old hardcoded value must be gone
    assert "department" in card.lower()
    assert "subject" in card.lower()
    assert ("oversized" in card.lower() or "2900" in card or "large" in card.lower())


# REPLACE test_hf_card_exists_and_has_yaml_front_matter, test_hf_card_includes_licensing_section,
# test_card_validation_yaml_parses, test_idempotency_same_cards_on_repeat_run: add a stats arg
# to every X.build_hf_card(...) call site, e.g.:
#   stats = {"snapshot_date": "2026-07-14", "dept_unknown": 1, "dept_total": 1,
#            "date_min": "2020-01-01", "date_max": "2026-01-01"}
#   card = X.build_hf_card(datasets, stats)
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest -q tests/test_dataset_cards.py -v`
Expected: FAIL — `AttributeError: module 'export_datasets' has no attribute '_compute_stats'`, and `TypeError: build_hf_card() missing 1 required positional argument: 'stats'` for the updated tests.

- [ ] **Step 3: Implement `_compute_stats()` and update `write_dataset_cards()`**

In `scripts/export_datasets.py`, add near the top-level imports (the file already has `import json`, `import re`; add `datetime`):

```python
import datetime as dt
```

Add this helper just above `def build_hf_card(...)` (~line 402):

```python
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _compute_stats(out_dir: Path) -> dict:
    """Corpus-derived numbers for the card prose (UNKNOWN fraction, date
    range) plus today's date, so cards can't silently drift from the data
    they describe. Reads the just-exported corpus config, not the raw
    source — guarantees the card matches what's actually being published."""
    corpus_path = out_dir / "corpus" / "corpus.jsonl"
    dept_unknown = dept_total = 0
    dates: list[str] = []
    if corpus_path.exists():
        for line in corpus_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            dept_total += 1
            if not r.get("issuing_department"):
                dept_unknown += 1
            d = r.get("issue_date")
            if d and _ISO_DATE_RE.match(d):
                dates.append(d)
    return {
        "snapshot_date": dt.date.today().isoformat(),
        "dept_unknown": dept_unknown,
        "dept_total": dept_total,
        "date_min": min(dates) if dates else "",
        "date_max": max(dates) if dates else "",
    }
```

Update `write_dataset_cards()` (~line 676) to compute stats once and pass to every builder:

```python
def write_dataset_cards(out_dir: Path) -> None:
    """Generate and write HF/Kaggle/Zenodo/AIKosh cards to disk."""
    manifest_path = out_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"No manifest found at {manifest_path}; skipping card generation")
        return

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    datasets = {}
    for cfg, info in manifest.get("configs", {}).items():
        rows = info.get("rows", 0)
        schema_name = cfg.replace("-", "_").upper() + "_SCHEMA"
        schema = globals().get(schema_name, [])
        datasets[cfg] = {"rows": rows, "schema": schema}

    stats = _compute_stats(out_dir)

    # HuggingFace card
    hf_card = build_hf_card(datasets, stats)
    (out_dir / "README.md").write_text(hf_card, encoding="utf-8")

    # Kaggle metadata
    kaggle_meta = build_kaggle_metadata(datasets, stats)
    (out_dir / "metadata.json").write_text(kaggle_meta, encoding="utf-8")

    # Zenodo pack
    zenodo_pack = build_zenodo_pack(datasets, stats)
    zenodo_dir = out_dir / "ZENODO_SUBMISSION_PACK"
    zenodo_dir.mkdir(exist_ok=True)
    (zenodo_dir / "metadata.json").write_text(json.dumps(zenodo_pack["metadata"], indent=2, ensure_ascii=False), encoding="utf-8")
    (zenodo_dir / "README_TARBALL.txt").write_text(zenodo_pack["instructions"], encoding="utf-8")

    # AIKosh pack
    aikosh_pack = build_aikosh_pack(datasets, stats)
    aikosh_dir = out_dir / "AIKOSH_SUBMISSION_PACK"
    aikosh_dir.mkdir(exist_ok=True)
    (aikosh_dir / "manifest.csv").write_text(aikosh_pack["manifest_csv"], encoding="utf-8")
    (aikosh_dir / "metadata.json").write_text(json.dumps(aikosh_pack["metadata"], indent=2, ensure_ascii=False), encoding="utf-8")
    (aikosh_dir / "LICENSING.txt").write_text(aikosh_pack["licensing"], encoding="utf-8")

    print(f"Dataset cards written to {out_dir}/")
```

- [ ] **Step 4: Fix `build_hf_card`'s hardcoded values**

Change the signature and the hardcoded lines in `build_hf_card` (~lines 403–460):

```python
def build_hf_card(datasets: dict[str, dict], stats: dict) -> str:
    """Build HuggingFace dataset card (README.md with YAML front matter)."""
    corpus_rows = datasets.get("corpus", {}).get("rows", 0)
    date_range = f"{stats['date_min'][:4]}–{stats['date_max'][:4]}" if stats["date_min"] else "unknown"
    yaml_block = f"""---
language:
  - en
license: cc-by-4.0
pretty_name: SEBI Circulars
size_categories:
  - 100K<n<1M
source_datasets: []
task_categories:
  - text-retrieval
  - text-generation
  - text-classification
tags:
  - regulatory
  - sebi
  - india
  - circulars
  - citation
  - knowledge-graph
---

# SEBI Circulars Dataset

A comprehensive, structured dataset of Indian Securities and Exchange Board (SEBI) regulatory circulars, public-domain government works compiled and annotated for AI/ML research.

**Date:** {stats['snapshot_date']}
**Snapshot Version:** v2026.07
**Corpus:** {corpus_rows:,} circulars ({date_range})

## Dataset Configurations

| Config | Rows | Schema | Purpose |
|---|---|---|---|
| **corpus** | {datasets.get('corpus', {}).get('rows', 0):,} | Full circular + metadata | Flagship: regulatory text, lineage, effective dates |
| **chunks** | {datasets.get('chunks', {}).get('rows', 0):,} | Section-aware retrieval chunks | RAG, dense retrieval, section-level analysis |
| **lineage** | {datasets.get('lineage', {}).get('rows', 0):,} | Regulatory supersession edges | Citation graph, link prediction, lineage reasoning |
| **eval** | {datasets.get('eval', {}).get('rows', 0):,} | Curated benchmark queries | Retrieval/abstention evaluation, domain regression |
| **citation-normalization** | {datasets.get('citation-normalization', {}).get('rows', 0):,} | Raw reference → normalized circular | String normalization, entity recognition (NER/seq2seq) |
| **supersession-pairs** | {datasets.get('supersession-pairs', {}).get('rows', 0):,} | Circular pairs + labels | Pair classification, regulatory relationship prediction |

## Schema Details

### corpus
"""
```

(The `f"""..."""` conversion means every literal `{` or `}` already present elsewhere in this block — there are none in the YAML/table text above — is safe; no escaping needed.)

Further down in the same function, fix the UNKNOWN-department caveat (~line 458, inside the `if "corpus" in datasets:` block):

```python
        yaml_block += f"""
- `circular_number` (str): Unique identifier (e.g., `SEBI/HO/CFD/P/CIR/2023/123`).
- `issue_date` (date): Publication date.
- `effective_date` (date, nullable): When the circular takes effect.
- `subject` (str): Circular title/summary.
- `issuing_department` (str): Issuing SEBI department (e.g., CFD, MRD). **Known limitation:** {stats['dept_unknown']}/{stats['dept_total']} records have `issuing_department=UNKNOWN` due to pre-existing parsing artifacts.
- `supersession_status` (str): `in_force`, `superseded`, or `amended`.
- `version_lineage` (list[str]): Prior circular numbers this updates/references.
- `source_url` (str): Original SEBI publication page.
- `text` (str): Full circular text.
- `excerpt` (bool): Whether the text is a partial excerpt.
- `extraction_date` (date): When this record was extracted from source.

**Known data-quality caveat:** Some master-circular `subject` fields capture body text (~2900 chars) due to a pre-existing PDF parsing artifact in `src/sebi_rag/ingest_pdf.py`. This is not a regression from this work; document it in your analysis.
"""
```

Fix the Disclaimers section (~line 543) and Citation/Repository sections (~lines 556–570) — locate these four literal strings in the function and replace:

```python
# "3. **Coverage:** Corpus spans 2021–2026 and is not exhaustive of all SEBI circulars."
# becomes (f-string, using date_range computed at the top of the function):
    yaml_block += f"""
## Licensing & Compliance

**Underlying Regulatory Text:** SEBI circulars are Indian government works. Per India's Copyright Act 1957 §52(1)(q), government orders/notifications may be freely reproduced. We attribute SEBI and provide `source_url` per record for verification.

**Compilation & Annotations:** The metadata extraction, chunking, lineage graph, normalized citations, and pair labels are original annotations licensed under **CC-BY-4.0**.

### Disclaimers

1. **Not legal advice.** These circulars are informational only. Verify against sebi.gov.in before regulatory reliance.
2. **Not SEBI-endorsed.** This dataset is independent; not affiliated with or endorsed by the Securities and Exchange Board of India.
3. **Coverage:** Corpus spans {date_range} and is not exhaustive of all SEBI circulars.
4. **Data quality:** `issuing_department` is UNKNOWN for {stats['dept_unknown']} records (parsing artifact). Some master-circular `subject` fields may be oversized (~2900 chars, also a parsing artifact).

## Citation

Please cite this dataset if you use it:

```bibtex
@dataset{{sebi_circulars_2026,
  title={{SEBI Circulars: Indian Regulatory Texts, {date_range}}},
  author={{OpenSourceContributor}},
  year={{2026}},
  url={{https://huggingface.co/datasets/...}},
  license={{CC-BY-4.0}}
}}
```

## Repository

Full dataset extraction pipeline and reproducibility information:
- **GitHub:** https://github.com/opnsrcntrbtr/sebi-circular-rag
- **Extraction date:** {stats['snapshot_date']}
- **Snapshot:** v2026.07 (max issue_date across corpus)

## Suggested Use Cases

- **Retrieval & RAG:** chunks config for dense/hybrid retrieval pipelines.
- **Citation Mining:** citation-normalization for training sequence-to-sequence or NER models.
- **Regulatory Reasoning:** lineage for link prediction, temporal reasoning, and regulatory change tracking.
- **Pair Classification:** supersession-pairs for supervised learning on relationship prediction.
- **Benchmark:** eval config ({datasets.get('eval', {}).get('rows', 0)} curated queries) for domain-specific retrieval evaluation.

## Contact

For questions or issues: [https://github.com/opnsrcntrbtr/sebi-circular-rag/issues]
"""
    return yaml_block
```

Note the doubled `{{` / `}}` inside the ```` ```bibtex ```` block — required because this section is now an f-string and the bibtex's own `{...}` braces must be escaped to appear literally.

Update the four other builder signatures now (bodies still fixed in Tasks 2–4) so `write_dataset_cards()` from Step 3 works end-to-end:

```python
def build_kaggle_metadata(datasets: dict[str, dict], stats: dict) -> str:
```
```python
def build_zenodo_pack(datasets: dict[str, dict], stats: dict) -> dict:
```
```python
def build_aikosh_pack(datasets: dict[str, dict], stats: dict) -> dict:
```

(Leave their bodies untouched for now — `stats` is accepted but unused inside these three until Tasks 2–4. This keeps Task 1 focused on `build_hf_card` while unblocking `write_dataset_cards()`.)

- [ ] **Step 5: Run to verify pass**

Run: `.venv/bin/python -m pytest -q tests/test_dataset_cards.py -v`
Expected: all tests in this file pass (the ones not yet touching kaggle/zenodo/aikosh signature bodies still pass unchanged since those functions now merely accept-and-ignore `stats`).

- [ ] **Step 6: Full suite + commit**

```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
.venv/bin/python -m pytest -q -m "not integration"   # expected: 235 passed (233 baseline + 2 new _compute_stats tests)
git add scripts/export_datasets.py tests/test_dataset_cards.py
git commit -m "feat(export): compute card stats from real corpus data; fix build_hf_card hardcoding"
```

---

### Task 2: Fix `build_kaggle_metadata`'s hardcoded values

**Files:**
- Modify: `scripts/export_datasets.py` (`build_kaggle_metadata`, ~line 581)
- Test: `tests/test_dataset_cards.py`

**Interfaces:**
- Consumes: `stats` dict shape from Task 1 (`snapshot_date`, `dept_unknown`, `dept_total`, `date_min`, `date_max`).
- Produces: no new interface — same `build_kaggle_metadata(datasets, stats) -> str` (JSON) signature from Task 1.

- [ ] **Step 1: Write the failing test**

```python
# REPLACE test_kaggle_metadata_includes_dataset_descriptions in tests/test_dataset_cards.py
def test_kaggle_metadata_includes_dataset_descriptions():
    """Description must cite actual row counts, not hardcoded literals."""
    datasets = {
        "corpus": {"rows": 705, "schema": X.CORPUS_SCHEMA},
        "chunks": {"rows": 77859, "schema": X.CHUNKS_SCHEMA},
        "lineage": {"rows": 4483, "schema": X.LINEAGE_SCHEMA},
        "eval": {"rows": 56, "schema": X.EVAL_SCHEMA},
        "citation-normalization": {"rows": 8802, "schema": X.CITATION_SCHEMA},
        "supersession-pairs": {"rows": 2769, "schema": X.SUPERSESSION_SCHEMA},
    }
    stats = {"snapshot_date": "2026-07-14", "dept_unknown": 158, "dept_total": 705,
             "date_min": "2010-04-06", "date_max": "2026-07-07"}
    metadata = json.loads(X.build_kaggle_metadata(datasets, stats))
    desc = metadata["description"]
    assert "705" in desc and "77,859" in desc and "4,483" in desc
    assert "8,802" in desc and "2,769" in desc
    assert "603" not in desc and "34,883" not in desc
    assert "2010" in metadata["title"] or "2010" in desc  # date range, not fixed 2021
```

Also add `stats` to the two existing calls (`test_kaggle_metadata_json_valid`,
`test_kaggle_metadata_includes_dataset_descriptions` is replaced above; update
`test_kaggle_metadata_json_valid`'s single `X.build_kaggle_metadata(datasets)`
call to `X.build_kaggle_metadata(datasets, stats)` with the same `stats` dict
literal shown above).

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest -q tests/test_dataset_cards.py::test_kaggle_metadata_includes_dataset_descriptions -v`
Expected: FAIL — assertion on `"705" in desc` fails (description still says "603 circulars").

- [ ] **Step 3: Implement**

Replace the hardcoded `title`/`description` in `build_kaggle_metadata` (~lines 583–591):

```python
def build_kaggle_metadata(datasets: dict[str, dict], stats: dict) -> str:
    """Build Kaggle metadata.json."""
    date_range = f"{stats['date_min'][:4]}–{stats['date_max'][:4]}" if stats["date_min"] else "unknown"
    corpus_rows = datasets.get("corpus", {}).get("rows", 0)
    chunks_rows = datasets.get("chunks", {}).get("rows", 0)
    lineage_rows = datasets.get("lineage", {}).get("rows", 0)
    eval_rows = datasets.get("eval", {}).get("rows", 0)
    citation_rows = datasets.get("citation-normalization", {}).get("rows", 0)
    supersession_rows = datasets.get("supersession-pairs", {}).get("rows", 0)
    meta = {
        "id": "sebi-circulars-india-regulatory",
        "title": f"SEBI Circulars: Indian Regulatory Texts ({date_range})",
        "subtitle": "Structured dataset of public-domain SEBI circulars for AI/ML research",
        "description": (
            f"Six configurations: corpus ({corpus_rows:,} circulars), "
            f"chunks ({chunks_rows:,} retrieval chunks), "
            f"lineage ({lineage_rows:,} supersession/amendment edges), "
            f"eval ({eval_rows}-query benchmark), "
            f"citation-normalization ({citation_rows:,} reference pairs), "
            f"supersession-pairs ({supersession_rows:,} labeled pairs). "
            "Formats: Parquet + JSONL. Licensing: CC-BY-4.0 (annotations); government works (underlying text)."
        ),
        "owner": "opnsrcntrbtrian",
        "tags": [
            "regulatory", "india", "sebi", "circulars", "knowledge-graph", "nlp", "information-retrieval",
            "pair-classification", "citation-mining", "public-domain"
        ],
        "licenses": [{"name": "CC-BY-4.0"}],
        "resources": [
            {"path": f"{cfg}/corpus.parquet", "type": "parquet", "description": f"{cfg} config"}
            for cfg in sorted(datasets.keys())
        ] + [
            {"path": "manifest.json", "type": "json", "description": "Export metadata + checksums"},
            {"path": "README.md", "type": "markdown", "description": "Dataset card with usage guide"},
        ],
    }
    return json.dumps(meta, indent=2, ensure_ascii=False)
```

- [ ] **Step 4: Run to verify pass**

Run: `.venv/bin/python -m pytest -q tests/test_dataset_cards.py -v`
Expected: all pass.

- [ ] **Step 5: Full suite + commit**

```bash
.venv/bin/python -m pytest -q -m "not integration"
git add scripts/export_datasets.py tests/test_dataset_cards.py
git commit -m "feat(export): fix build_kaggle_metadata hardcoded row counts and date range"
```

---

### Task 3: Fix `build_zenodo_pack`'s hardcoded values

**Files:**
- Modify: `scripts/export_datasets.py` (`build_zenodo_pack`, ~line 610)
- Test: `tests/test_dataset_cards.py`

**Interfaces:**
- Consumes: same `stats` dict shape as Tasks 1–2.
- Produces: no new interface — `build_zenodo_pack(datasets, stats) -> dict` signature already set in Task 1.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_dataset_cards.py
def test_zenodo_pack_uses_computed_row_count_and_date():
    datasets = {"corpus": {"rows": 705, "schema": X.CORPUS_SCHEMA}}
    stats = {"snapshot_date": "2026-07-14", "dept_unknown": 158, "dept_total": 705,
             "date_min": "2010-04-06", "date_max": "2026-07-07"}
    pack = X.build_zenodo_pack(datasets, stats)
    assert "705" in pack["metadata"]["description"]
    assert "603" not in pack["metadata"]["description"]
    assert pack["metadata"]["publication_date"] == "2026-07-14"
    assert "2010" in pack["metadata"]["title"]
```

Update the two existing tests (`test_zenodo_submission_pack_structure`,
`test_zenodo_metadata_has_doi_fields`) to pass `stats` as a second argument
using the same literal shown above.

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest -q tests/test_dataset_cards.py::test_zenodo_pack_uses_computed_row_count_and_date -v`
Expected: FAIL — `pack["metadata"]["publication_date"]` is `"2026-07-13"`, not `"2026-07-14"`.

- [ ] **Step 3: Implement**

```python
def build_zenodo_pack(datasets: dict[str, dict], stats: dict) -> dict:
    """Build Zenodo submission metadata + tarball instructions."""
    date_range = f"{stats['date_min'][:4]}–{stats['date_max'][:4]}" if stats["date_min"] else "unknown"
    corpus_rows = datasets.get("corpus", {}).get("rows", 0)
    return {
        "metadata": {
            "title": f"SEBI Circulars: Indian Regulatory Texts ({date_range})",
            "description": (
                f"Structured dataset of {corpus_rows:,} SEBI regulatory circulars with lineage, "
                "retrieval chunks, citations, and evaluation benchmark. Six configurations "
                "in Parquet + JSONL format. Licensing: CC-BY-4.0 (annotations); "
                "government works (underlying text)."
            ),
            "creators": [{"name": "OpenSourceContributor"}],
            "version": "v2026.07",
            "license": "CC-BY-4.0",
            "keywords": ["regulatory", "india", "sebi", "circulars", "knowledge-graph", "nlp"],
            "subjects": ["Government", "Regulatory", "India", "Securities", "Machine Learning"],
            "upload_type": "dataset",
            "publication_date": stats["snapshot_date"],
        },
        "instructions": (
            "1. Create tarball: tar czf sebi-circulars-v2026.07.tar.gz dist/datasets/\n"
            "2. Upload to Zenodo via web UI or API\n"
            "3. Record DOI and update HF/Kaggle cards with DOI link"
        ),
    }
```

- [ ] **Step 4: Run to verify pass**

Run: `.venv/bin/python -m pytest -q tests/test_dataset_cards.py -v`
Expected: all pass.

- [ ] **Step 5: Full suite + commit**

```bash
.venv/bin/python -m pytest -q -m "not integration"
git add scripts/export_datasets.py tests/test_dataset_cards.py
git commit -m "feat(export): fix build_zenodo_pack hardcoded row count, date range, publication date"
```

---

### Task 4: Fix `build_aikosh_pack`'s hardcoded values

**Files:**
- Modify: `scripts/export_datasets.py` (`build_aikosh_pack`, ~line 637)
- Test: `tests/test_dataset_cards.py`

**Interfaces:**
- Consumes: same `stats` dict shape as Tasks 1–3.
- Produces: no new interface — `build_aikosh_pack(datasets, stats) -> dict` signature already set in Task 1. This is the last builder; after this task all four generators are fully dynamic.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_dataset_cards.py
def test_aikosh_pack_uses_computed_date_range():
    datasets = {"corpus": {"rows": 705, "schema": X.CORPUS_SCHEMA}}
    stats = {"snapshot_date": "2026-07-14", "dept_unknown": 158, "dept_total": 705,
             "date_min": "2010-04-06", "date_max": "2026-07-07"}
    pack = X.build_aikosh_pack(datasets, stats)
    assert "2010" in pack["metadata"]["title"]
    assert "2021" not in pack["metadata"]["title"]
    assert "2010" in pack["licensing"] or "2010" in pack["metadata"]["description"]
```

Update the two existing tests (`test_aikosh_submission_pack_includes_csv_and_metadata`,
`test_aikosh_pack_manifest_includes_all_configs`) to pass `stats` as a second
argument using the same literal shown above.

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest -q tests/test_dataset_cards.py::test_aikosh_pack_uses_computed_date_range -v`
Expected: FAIL — `pack["metadata"]["title"]` still contains `"2021–2026"`.

- [ ] **Step 3: Implement**

```python
def build_aikosh_pack(datasets: dict[str, dict], stats: dict) -> dict:
    """Build AIKosh (IndiaAI) submission pack: CSV manifest + metadata + licensing."""
    date_range = f"{stats['date_min'][:4]}–{stats['date_max'][:4]}" if stats["date_min"] else "unknown"
    manifest_rows = [["config", "rows", "description"]]
    descriptions = {
        "corpus": "Full circular + metadata",
        "chunks": "Section-aware retrieval chunks",
        "lineage": "Supersession/amendment edges",
        "eval": "Benchmark queries",
        "citation-normalization": "Citation normalization pairs",
        "supersession-pairs": "Labeled regulatory pairs",
    }
    for cfg, info in sorted(datasets.items()):
        manifest_rows.append([cfg, str(info["rows"]), descriptions.get(cfg, "")])

    manifest_csv = "\n".join(",".join(r) for r in manifest_rows)

    return {
        "manifest_csv": manifest_csv,
        "metadata": {
            "title": f"SEBI Circulars: Indian Regulatory Texts ({date_range})",
            "organization": "OpenSourceContributor",
            "dataset_type": "Regulatory / Government",
            "regions": ["India"],
            "languages": ["English"],
            "version": "v2026.07",
            "description": (
                "Structured dataset of SEBI regulatory circulars for AI/ML research. "
                "Non-personal, public-domain regulatory text with annotations."
            ),
        },
        "licensing": (
            "Underlying Text: Indian government works (Copyright Act 1957 §52(1)(q)).\n"
            "Annotations: CC-BY-4.0 (metadata, lineage, chunking, citations, labels).\n"
            "Attribution: SEBI; provide source_url per record.\n"
            f"Disclaimers: Not legal advice; not SEBI-endorsed; corpus is {date_range} (not exhaustive)."
        ),
    }
```

- [ ] **Step 4: Run to verify pass**

Run: `.venv/bin/python -m pytest -q tests/test_dataset_cards.py -v`
Expected: all pass (should now be the original 15 tests + 6 new ones = 21 tests, all green).

- [ ] **Step 5: Full suite + commit**

```bash
.venv/bin/python -m pytest -q -m "not integration"   # expected: 239 passed (233 + 6 new)
git add scripts/export_datasets.py tests/test_dataset_cards.py
git commit -m "feat(export): fix build_aikosh_pack hardcoded date range"
```

---

### Task 5: Manifest-accuracy regression test

**Files:**
- Test: `tests/test_dataset_cards.py`

**Interfaces:**
- Consumes: `X.write_dataset_cards`, `X.build_hf_card` from Task 1; a real `manifest.json` + exported `corpus/corpus.jsonl` fixture (synthetic, offline).
- Produces: nothing new consumed downstream — this is the spec's explicit "can't silently drift again" guard, exercising the full `write_dataset_cards()` → generated-card path end-to-end rather than unit-testing each builder in isolation.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_dataset_cards.py
import re as _re


def test_generated_hf_card_row_counts_match_manifest(tmp_path):
    """End-to-end: every row count printed in the generated card's summary
    table must equal the corresponding manifest.json row count. Catches a
    future regression back to hardcoded literals without needing to know
    what the 'right' numbers are — it compares the card against its own
    manifest, not against an expected literal."""
    out_dir = tmp_path / "dist"
    corpus_dir = out_dir / "corpus"
    corpus_dir.mkdir(parents=True)
    rows = [
        {"circular_number": f"A/{i}", "issue_date": "2022-01-01",
         "issuing_department": "CFD" if i % 2 else ""}
        for i in range(1, 6)
    ]
    (corpus_dir / "corpus.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    manifest = {
        "version": "v2099.01",
        "configs": {
            "corpus": {"rows": 5, "source": "x", "source_sha256": "x"},
            "chunks": {"rows": 42, "source": "x", "source_sha256": "x"},
            "lineage": {"rows": 7, "source": "x", "source_sha256": "x"},
            "eval": {"rows": 3, "source": "x", "source_sha256": "x"},
            "citation-normalization": {"rows": 11, "source": "x", "source_sha256": "x"},
            "supersession-pairs": {"rows": 9, "source": "x", "source_sha256": "x"},
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    X.write_dataset_cards(out_dir)
    card = (out_dir / "README.md").read_text(encoding="utf-8")

    table_start = card.index("| Config | Rows")
    table = card[table_start:table_start + 800]
    for cfg, info in manifest["configs"].items():
        expected = f"{info['rows']:,}"
        assert expected in table, f"{cfg}: expected {expected} in card table, not found"
```

- [ ] **Step 2: Run to verify failure or pass**

Run: `.venv/bin/python -m pytest -q tests/test_dataset_cards.py::test_generated_hf_card_row_counts_match_manifest -v`
Expected: PASS immediately (Tasks 1–4 already made the generators dynamic — this test's purpose is to *lock in* that behavior going forward, not introduce it). If it fails, one of Tasks 1–4 left a hardcoded value; go back and find it before continuing.

- [ ] **Step 3: Full suite + commit**

```bash
.venv/bin/python -m pytest -q -m "not integration"   # expected: 240 passed
git add tests/test_dataset_cards.py
git commit -m "test(export): lock in card-generator dynamism with a manifest-accuracy regression test"
```

---

### Task 6: Regenerate, dry-run, and push the corrected dataset to HF Hub

**Files:** none (operational — regenerates `dist/datasets/`, which is gitignored).

**Interfaces:**
- Consumes: the fixed `scripts/export_datasets.py` (Tasks 1–4) and `scripts/push_datasets.py` (unchanged, from the master-circular-coverage plan).
- Produces: corrected live dataset card at `https://huggingface.co/datasets/opnsrcntrbtrian/sebi-circulars`.

- [ ] **Step 1:** `.venv/bin/python scripts/export_datasets.py` — regenerates `dist/datasets/README.md`, `metadata.json`, and the Kaggle/Zenodo/AIKOSH packs.
- [ ] **Step 2:** Inspect the regenerated card: `head -40 dist/datasets/README.md` — confirm it shows `705`, `77,859`, `4,483`, `8,802`, `2,769`, `158/705`, and a `2010–2026` date range, with no `603`/`34,883`/`124` anywhere.

```bash
grep -n "603\|34,883\|34883\|124/603" dist/datasets/README.md dist/datasets/metadata.json
```

Expected: no output (no stale numbers remain).

- [ ] **Step 3:** `.venv/bin/python -m pytest -q -m "not integration"` — expected: 240 passed.
- [ ] **Step 4:** Dry-run: `.venv/bin/python scripts/push_datasets.py` — confirm the upload plan lists the same 16 files as before (content changed, file list unchanged).
- [ ] **Step 5 (pause for user confirmation — live, shared action):** `.venv/bin/python scripts/push_datasets.py --yes` — pushes the corrected card to `opnsrcntrbtrian/sebi-circulars`.
- [ ] **Step 6:** Verify remotely:

```bash
curl -s https://huggingface.co/datasets/opnsrcntrbtrian/sebi-circulars/raw/main/README.md | grep -c "705\|77,859"
```

Expected: non-zero (the live card reflects the fix).

---

### Task 7: Hand-correct `README.md` (project root)

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: the ground-truth numbers from this plan's header (`corpus rows: 705`, etc.) — same values Task 6 verified live on HF.
- Produces: nothing consumed downstream — this is a terminal documentation fix.

- [ ] **Step 1:** Update the Dataset Configurations table (README.md:52–63):

```markdown
Six structured dataset configs available in JSONL + Parquet formats (v2026.07 snapshot, 705 circulars):

| Config | Rows | Purpose |
|---|---|---|
| **corpus** | 705 | Full circular text + metadata, regulatory lineage, effective dates |
| **chunks** | 77,859 | Section-aware retrieval chunks for RAG and dense retrieval |
| **lineage** | 4,483 | Regulatory supersession/amendment edges (citation graph) |
| **eval** | 56 | Curated benchmark queries for domain-specific retrieval evaluation |
| **citation-normalization** | 8,802 | Raw reference → normalized circular pairs (seq2seq/NER task) |
| **supersession-pairs** | 2,769 | Labeled circular pairs (supersedes/amends/unrelated classification) |
```

- [ ] **Step 2:** Update the Disclaimers section (README.md:82–87):

```markdown
### Disclaimers

1. **Not legal advice.** Circulars are informational only; verify against [sebi.gov.in](https://sebi.gov.in) before regulatory reliance.
2. **Not SEBI-endorsed.** This dataset is independent and not affiliated with or endorsed by the Securities and Exchange Board of India.
3. **Coverage:** Corpus spans 2010–2026, including all 130 SEBI master circulars, and is not exhaustive of all SEBI circulars.
4. **Data quality:** `issuing_department` is UNKNOWN for 158/705 records (parsing artifact). Some master-circular `subject` fields may be oversized (~2900 chars, also pre-existing).
```

- [ ] **Step 3:** Update the citation bibtex year range (README.md:94–101, the `@dataset{sebi_circulars_2026, title={SEBI Circulars: Indian Regulatory Texts, 2021–2026}...}` block) — change `2021–2026` to `2010–2026`.
- [ ] **Step 4:** Search for any other `603`/`34,603`/`2021–2026`/`124` occurrence in `README.md` and correct it:

```bash
grep -n "603\|34,603\|2021.2026\|124" README.md
```

Fix any remaining hits following the same values used above.

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: correct README.md dataset numbers to post-master-circular-coverage state"
```

---

### Task 8: Audit `README-spaces.md`, redeploy the Space

**Files:**
- Modify: `README-spaces.md` (only if Step 1 finds anything)

**Interfaces:**
- Consumes: `scripts/deploy_space.py` (unchanged, from the master-circular-coverage plan).
- Produces: corrected live Space README at `https://huggingface.co/spaces/opnsrcntrbtrian/sebi-circular-rag-demo`.

- [ ] **Step 1:** Audit for any stale numeric mention beyond the corpus-count line already fixed (commit `9e6b727`):

```bash
grep -n "603\|34,883\|34883\|124\|2021" README-spaces.md
```

Expected: no output. If anything is found, correct it using the same ground-truth values from this plan's header.

- [ ] **Step 2 (pause for user confirmation — live, shared action):** Redeploy so the live Space's README.md (rendered from `README-spaces.md`) matches:

```bash
.venv/bin/python scripts/deploy_space.py --repo opnsrcntrbtrian/sebi-circular-rag-demo
```

- [ ] **Step 3:** Wait for the Space to finish rebuilding (poll `space_info` runtime stage until `RUNNING`, same pattern as the master-circular-coverage plan's Task 10 Step 2), then verify:

```bash
curl -s https://huggingface.co/spaces/opnsrcntrbtrian/sebi-circular-rag-demo/raw/main/README.md | grep -c "77.9k\|705"
```

Expected: non-zero. No functional smoke test is needed for this task — it's a README-only redeploy (no code/index change), so retrieval/generation behavior is unaffected.
- [ ] **Step 4 (only if Step 1 found changes):** Commit:

```bash
git add README-spaces.md
git commit -m "docs(spaces): correct remaining stale dataset numbers"
```
