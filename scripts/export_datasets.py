"""Export SEBI RAG data into publishable dataset configs (HF/Kaggle/Zenodo/AIKosh).

Six configs: corpus, chunks, lineage, eval (Tasks 1-2), citation-normalization
and supersession-pairs (Task 3, transformed task datasets). Cards + platform
packaging are a later task (Haiku). Spec:
docs/superpowers/specs/2026-07-09-sebi-public-datasets-design.md.

Stages: validate (reuse validate_corpus/validate_golden invariants) ->
transform (pure per-config builders) -> emit (Parquet + JSONL under
dist/datasets/<config>/ plus manifest.json with source checksums and
snapshot version).

Usage: uv run python scripts/export_datasets.py \
    [--corpus data/corpus/circulars.jsonl] [--out dist/datasets]
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_corpus import validate  # noqa: E402
from sebi_rag.benchmark import validate_golden  # noqa: E402
from sebi_rag.ingest_pdf import REF_RE, normalize_circular_number  # noqa: E402
import sebi_rag.ingest_pdf as _ingest_pdf  # noqa: E402

# Column order is the published schema (spec Config 1). provenance is replaced
# by extraction_date (local PDF filenames have no research value); empty
# amendment_history is not exported.
CORPUS_SCHEMA = [
    "circular_number", "issue_date", "effective_date", "subject",
    "issuing_department", "supersession_status", "version_lineage",
    "source_url", "text", "excerpt", "extraction_date",
]
_EXTRACTION_DATE = re.compile(r"on (\d{4}-\d{2}-\d{2})\s*$")

# One row per retrieval chunk. context_header is the repeated
# "{circular_number} | {truncated subject} | {section}" line every chunk's
# text starts with (see build_index chunking); split out so researchers can
# choose either representation. meta.amendment_history is empty across the
# whole corpus (verified 2026-07-09) so, like CORPUS_SCHEMA, it isn't exported.
CHUNKS_SCHEMA = [
    "chunk_id", "doc_id", "section", "context_header", "text",
    "circular_number", "issue_date", "effective_date", "subject",
    "issuing_department", "supersession_status", "version_lineage",
]

# Forward edges only (supersedes/amends); superseded_by/amended_by in
# lineage.json are the same edges inverted for fast reverse lookup at query
# time and would duplicate rows here.
LINEAGE_SCHEMA = [
    "source_circular", "relation", "target_circular",
    "source_issue_date", "target_in_corpus",
]

# Pass-through of the golden_v6 RAG schema (scripts/build_golden_v6.py).
EVAL_SCHEMA = [
    "id", "query", "relevant_circulars", "relevant_chunks", "answer_contains",
    "must_contain", "must_not_contain", "abstain", "task_type", "difficulty",
    "expected_citation_level", "rationale", "label_source", "review_status",
]

# Seq2seq/NER pairs: raw in-text citation -> normalized circular number.
# format_family classifies each match against REF_RE's three sub-grammars
# (pinned by tests/test_ingest_refs.py::test_ref_re_matches_all_three_reference_grammars);
# a REF_RE match always fulfills exactly one of these by construction.
CITATION_SCHEMA = [
    "raw_reference", "normalized_circular_number", "context_window",
    "source_doc_id", "format_family",
]
_FAMILY_PATTERNS = [
    ("new-standard", re.compile(_ingest_pdf._NEW)),
    ("old-standard", re.compile(_ingest_pdf._OLD)),
    ("dept-order-2026", re.compile(_ingest_pdf._NEW_FMT2)),
]


def _format_family(raw: str) -> str:
    for name, pattern in _FAMILY_PATTERNS:
        if pattern.fullmatch(raw):
            return name
    return "unknown"  # unreachable for a REF_RE match; kept as an explicit guard


def build_citation_pairs(corpus_records: list[dict], context_chars: int = 60) -> list[dict]:
    """Pure transform: corpus text -> citation-normalization rows.

    Mines in-body references with REF_RE (src/sebi_rag/ingest_pdf.py), the
    same regex lineage.py uses to build the supersession graph. Excludes the
    document's own number (exact-string match, mirroring lineage.py's
    detect_relations self-reference check) since that identifies the
    document, not a citation.
    """
    rows = []
    for r in corpus_records:
        text = r.get("text", "")
        own = r["circular_number"]
        for m in REF_RE.finditer(text):
            raw = m.group(0)
            if raw == own:
                continue
            start, end = max(0, m.start() - context_chars), m.end() + context_chars
            window = " ".join(text[start:end].split())
            rows.append({
                "raw_reference": raw,
                "normalized_circular_number": normalize_circular_number(raw),
                "context_window": window,
                "source_doc_id": own,
                "format_family": _format_family(raw),
            })
    return rows


# Pair-classification: is circular_b superseded/amended by circular_a, or
# unrelated? Positives come from lineage edges where BOTH endpoints are in
# the corpus (so a subject is available for circular_b); negatives are
# same-department pairs with no lineage edge in either direction.
SUPERSESSION_SCHEMA = [
    "circular_a_number", "circular_a_subject", "circular_b_number",
    "circular_b_subject", "label",
]


def build_supersession_pairs(corpus_records: list[dict], lineage: dict,
                             negative_ratio: float = 2.0, seed: int = 42) -> list[dict]:
    """Pure transform: corpus + lineage -> labeled circular pairs.

    label is 'supersedes', 'amends', or 'unrelated'. Deterministic given the
    same seed (negatives are sampled, not exhaustive, to keep the class ratio
    at ~negative_ratio:1).
    """
    by_norm = {normalize_circular_number(r["circular_number"]): r for r in corpus_records}

    positives = []
    linked: set[frozenset[str]] = set()
    for relation in ("supersedes", "amends"):
        for source, targets in lineage.get(relation, {}).items():
            src_rec = by_norm.get(normalize_circular_number(source))
            for target in targets:
                linked.add(frozenset((normalize_circular_number(source),
                                     normalize_circular_number(target))))
                tgt_rec = by_norm.get(normalize_circular_number(target))
                if src_rec is None or tgt_rec is None:
                    continue
                positives.append({
                    "circular_a_number": src_rec["circular_number"],
                    "circular_a_subject": src_rec.get("subject") or "",
                    "circular_b_number": tgt_rec["circular_number"],
                    "circular_b_subject": tgt_rec.get("subject") or "",
                    "label": relation,
                })

    by_dept: dict[str, list[dict]] = {}
    for r in corpus_records:
        dept = r.get("issuing_department")
        if dept:
            by_dept.setdefault(dept, []).append(r)

    candidates = []
    for dept in sorted(by_dept):
        recs = sorted(by_dept[dept], key=lambda r: r["circular_number"])
        for a, b in itertools.combinations(recs, 2):
            pair = frozenset((normalize_circular_number(a["circular_number"]),
                             normalize_circular_number(b["circular_number"])))
            if pair not in linked:
                candidates.append((a, b))

    rng = random.Random(seed)
    rng.shuffle(candidates)
    target_neg = round(len(positives) * negative_ratio)
    negatives = [{
        "circular_a_number": a["circular_number"],
        "circular_a_subject": a.get("subject") or "",
        "circular_b_number": b["circular_number"],
        "circular_b_subject": b.get("subject") or "",
        "label": "unrelated",
    } for a, b in candidates[:target_neg]]

    return positives + negatives


def _null(v: str | None) -> str | None:
    return v if v else None


def build_corpus_rows(records: list[dict]) -> list[dict]:
    """Pure transform: corpus JSONL records -> publishable rows (CORPUS_SCHEMA)."""
    rows = []
    for r in records:
        m = _EXTRACTION_DATE.search(r.get("provenance", ""))
        rows.append({
            "circular_number": r["circular_number"],
            "issue_date": _null(r.get("issue_date")),
            "effective_date": _null(r.get("effective_date")),
            "subject": _null(r.get("subject")),
            "issuing_department": _null(r.get("issuing_department")),
            "supersession_status": _null(r.get("supersession_status")),
            "version_lineage": r.get("version_lineage", []),
            "source_url": _null(r.get("source_url")),
            "text": r.get("text", ""),
            "excerpt": bool(r.get("excerpt", False)),
            "extraction_date": m.group(1) if m else None,
        })
    return rows


def build_chunk_rows(chunks: list[dict]) -> list[dict]:
    """Pure transform: chunks.jsonl records -> publishable rows (CHUNKS_SCHEMA)."""
    rows = []
    for c in chunks:
        header, _, body = c["text"].partition("\n")
        m = c["meta"]
        rows.append({
            "chunk_id": c["id"],
            "doc_id": c["doc_id"],
            "section": c["section"],
            "context_header": header,
            "text": body,
            "circular_number": m["circular_number"],
            "issue_date": _null(m.get("issue_date")),
            "effective_date": _null(m.get("effective_date")),
            "subject": _null(m.get("subject")),
            "issuing_department": _null(m.get("issuing_department")),
            "supersession_status": _null(m.get("supersession_status")),
            "version_lineage": m.get("version_lineage", []),
        })
    return rows


def build_lineage_rows(lineage: dict, corpus_index: dict[str, str]) -> list[dict]:
    """Pure transform: lineage.json forward maps -> edge list (LINEAGE_SCHEMA).

    corpus_index maps normalize_circular_number(n) -> issue_date, for every
    circular actually in the corpus (built by _load_corpus_index).
    """
    rows = []
    for relation in ("supersedes", "amends"):
        for source, targets in lineage.get(relation, {}).items():
            source_date = corpus_index.get(normalize_circular_number(source))
            for target in targets:
                rows.append({
                    "source_circular": source,
                    "relation": relation,
                    "target_circular": target,
                    "source_issue_date": source_date,
                    "target_in_corpus": normalize_circular_number(target) in corpus_index,
                })
    return rows


def build_eval_rows(golden: list[dict]) -> list[dict]:
    """Pure transform: golden_v6 records -> publishable rows (EVAL_SCHEMA)."""
    return [{field: row[field] for field in EVAL_SCHEMA} for row in golden]


def _load_corpus_index(corpus_path: Path) -> dict[str, str]:
    records = [json.loads(l) for l in
               corpus_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return {normalize_circular_number(r["circular_number"]): r.get("issue_date", "")
            for r in records}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshot_version(rows: list[dict]) -> str:
    dates = [r["issue_date"] for r in rows if r["issue_date"]]
    return "v" + max(dates)[:7].replace("-", ".") if dates else "v0000.00"


def _update_manifest(out_dir: Path, config_name: str, entry: dict,
                     version: str | None = None) -> dict:
    """Merge one config's entry into the shared manifest.json and return it."""
    path = out_dir / "manifest.json"
    manifest = json.loads(path.read_text()) if path.exists() else \
        {"version": "v0000.00", "configs": {}}
    if version:
        manifest["version"] = version
    manifest["configs"][config_name] = entry
    out_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def _config_entry(rows: list[dict], source_path: Path) -> dict:
    return {"rows": len(rows), "source": str(source_path),
            "source_sha256": _sha256(source_path)}


def _emit(rows: list[dict], config_dir: Path, name: str, schema: list[str]) -> None:
    config_dir.mkdir(parents=True, exist_ok=True)
    with (config_dir / f"{name}.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    import pyarrow as pa
    import pyarrow.parquet as pq
    if rows:
        table = pa.Table.from_pylist(rows).select(schema)
    else:
        table = pa.Table.from_pylist([], schema=pa.schema([(c, pa.null()) for c in schema]))
    pq.write_table(table, config_dir / f"{name}.parquet")


def export_corpus(corpus_path: Path, out_dir: Path) -> dict:
    """Validate -> transform -> emit the corpus config; return the manifest."""
    records = [json.loads(l) for l in
               corpus_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    violations = validate(records)
    if violations:
        raise ValueError(f"{len(violations)} corpus violation(s); fix before "
                         f"export: {violations[:3]}")
    rows = build_corpus_rows(records)
    _emit(rows, out_dir / "corpus", "corpus", CORPUS_SCHEMA)
    return _update_manifest(out_dir, "corpus", _config_entry(rows, corpus_path),
                            version=_snapshot_version(rows))


def export_chunks(chunks_path: Path, out_dir: Path) -> dict:
    """Transform -> emit the chunks config; return the manifest."""
    chunks = [json.loads(l) for l in
              chunks_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = build_chunk_rows(chunks)
    _emit(rows, out_dir / "chunks", "chunks", CHUNKS_SCHEMA)
    return _update_manifest(out_dir, "chunks", _config_entry(rows, chunks_path))


def export_lineage(lineage_path: Path, corpus_path: Path, out_dir: Path) -> dict:
    """Transform -> emit the lineage config; return the manifest."""
    lineage = json.loads(lineage_path.read_text(encoding="utf-8"))
    corpus_index = _load_corpus_index(corpus_path)
    rows = build_lineage_rows(lineage, corpus_index)
    _emit(rows, out_dir / "lineage", "lineage", LINEAGE_SCHEMA)
    return _update_manifest(out_dir, "lineage", _config_entry(rows, lineage_path))


def export_eval(golden_path: Path, out_dir: Path) -> dict:
    """Validate -> transform -> emit the eval config; return the manifest."""
    golden = [json.loads(l) for l in
              golden_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    issues = validate_golden(golden)
    if issues:
        raise ValueError(f"{len(issues)} golden issue(s); fix before export: "
                         f"{issues[:3]}")
    rows = build_eval_rows(golden)
    _emit(rows, out_dir / "eval", "eval", EVAL_SCHEMA)
    return _update_manifest(out_dir, "eval", _config_entry(rows, golden_path))


def export_citation_normalization(corpus_path: Path, out_dir: Path) -> dict:
    """Transform -> emit the citation-normalization config; return the manifest."""
    records = [json.loads(l) for l in
               corpus_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = build_citation_pairs(records)
    _emit(rows, out_dir / "citation-normalization", "citation-normalization",
         CITATION_SCHEMA)
    return _update_manifest(out_dir, "citation-normalization",
                            _config_entry(rows, corpus_path))


def export_supersession_pairs(corpus_path: Path, lineage_path: Path,
                              out_dir: Path) -> dict:
    """Transform -> emit the supersession-pairs config; return the manifest."""
    records = [json.loads(l) for l in
               corpus_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    lineage = json.loads(lineage_path.read_text(encoding="utf-8"))
    rows = build_supersession_pairs(records, lineage)
    _emit(rows, out_dir / "supersession-pairs", "supersession-pairs",
         SUPERSESSION_SCHEMA)
    return _update_manifest(out_dir, "supersession-pairs",
                            _config_entry(rows, lineage_path))


def export_all(corpus: Path, chunks: Path, lineage: Path, golden: Path,
               out_dir: Path) -> dict:
    """Run every config export in sequence; return the merged manifest."""
    export_corpus(corpus, out_dir)
    export_chunks(chunks, out_dir)
    export_lineage(lineage, corpus, out_dir)
    export_eval(golden, out_dir)
    export_citation_normalization(corpus, out_dir)
    return export_supersession_pairs(corpus, lineage, out_dir)


# --- Task 4: Dataset Cards & Platform Packaging ---

def build_hf_card(datasets: dict[str, dict]) -> str:
    """Build HuggingFace dataset card (README.md with YAML front matter)."""
    yaml_block = """---
language:
  - en
license: cc-by-4.0
pretty_name: SEBI Circulars
size_categories:
  - 100K<n<1M
source_datasets: []
task_categories:
  - text-retrieval
  - text2text-generation
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

**Date:** 2026-07-09
**Snapshot Version:** v2026.07
**Corpus:** 603 circulars (2021–2026)

## Dataset Configurations

| Config | Rows | Schema | Purpose |
|---|---|---|---|
| **corpus** | 603 | Full circular + metadata | Flagship: regulatory text, lineage, effective dates |
| **chunks** | 36,603 | Section-aware retrieval chunks | RAG, dense retrieval, section-level analysis |
| **lineage** | 1,434 | Regulatory supersession edges | Citation graph, link prediction, lineage reasoning |
| **eval** | 56 | Curated benchmark queries | Retrieval/abstention evaluation, domain regression |
| **citation-normalization** | 2,951 | Raw reference → normalized circular | String normalization, entity recognition (NER/seq2seq) |
| **supersession-pairs** | 1,281 | Circular pairs + labels | Pair classification, regulatory relationship prediction |

## Schema Details

### corpus
"""

    if "corpus" in datasets:
        corpus_schema = datasets["corpus"]["schema"]
        yaml_block += "\n**Columns:** " + ", ".join(f"`{c}`" for c in corpus_schema) + "\n"
        yaml_block += """
- `circular_number` (str): Unique identifier (e.g., `SEBI/HO/CFD/P/CIR/2023/123`).
- `issue_date` (date): Publication date.
- `effective_date` (date, nullable): When the circular takes effect.
- `subject` (str): Circular title/summary.
- `issuing_department` (str): Issuing SEBI department (e.g., CFD, MRD). **Known limitation:** 124/603 records have `issuing_department=UNKNOWN` due to pre-existing parsing artifacts.
- `supersession_status` (str): `in_force`, `superseded`, or `amended`.
- `version_lineage` (list[str]): Prior circular numbers this updates/references.
- `source_url` (str): Original SEBI publication page.
- `text` (str): Full circular text.
- `excerpt` (bool): Whether the text is a partial excerpt.
- `extraction_date` (date): When this record was extracted from source.

**Known data-quality caveat:** Some master-circular `subject` fields capture body text (~2900 chars) due to a pre-existing PDF parsing artifact in `src/sebi_rag/ingest_pdf.py`. This is not a regression from this work; document it in your analysis.
"""

    if "chunks" in datasets:
        chunks_schema = datasets["chunks"]["schema"]
        yaml_block += "\n### chunks\n\n"
        yaml_block += "**Columns:** " + ", ".join(f"`{c}`" for c in chunks_schema) + "\n"
        yaml_block += f"\n{datasets['chunks']['rows']:,} section-aware retrieval chunks derived from corpus text, one row per chunk.\n"
        yaml_block += """
- `chunk_id` (str): Unique chunk identifier (e.g., `SEBI/HO/CFD/P/CIR/2023/123#preamble#0`).
- `doc_id` (str): Parent circular number.
- `section` (str): Section path (e.g., `SEBI/HO/CFD/.../preamble/p0`).
- `context_header` (str): Repeated contextual header extracted from chunk text (circular_number | subject | section).
- `text` (str): Chunk text body (header removed for clarity).
- Flattened metadata: `circular_number`, `issue_date`, `effective_date`, `subject`, `issuing_department`, `supersession_status`, `version_lineage`.
"""

    if "lineage" in datasets:
        lineage_schema = datasets["lineage"]["schema"]
        yaml_block += "\n### lineage\n\n"
        yaml_block += "**Columns:** " + ", ".join(f"`{c}`" for c in lineage_schema) + "\n"
        yaml_block += f"\n{datasets['lineage']['rows']:,} regulatory supersession/amendment edges (forward-direction only).\n"
        yaml_block += """
- `source_circular` (str): Circular that supersedes/amends another.
- `relation` (str): `supersedes` or `amends`.
- `target_circular` (str): Older circular being superseded/amended.
- `source_issue_date` (date): Publication date of source (for temporal reasoning).
- `target_in_corpus` (bool): Whether the target circular is in this corpus (allows filtering for pair-classification tasks).

**Note:** Inverse relationships (`superseded_by`, `amended_by`) are omitted to avoid duplication; regenerate them at query time.
"""

    if "citation-normalization" in datasets:
        citation_schema = datasets["citation-normalization"]["schema"]
        yaml_block += "\n### citation-normalization\n\n"
        yaml_block += "**Columns:** " + ", ".join(f"`{c}`" for c in citation_schema) + "\n"
        yaml_block += f"\n{datasets['citation-normalization']['rows']:,} in-text reference citations mined and normalized.\n"
        yaml_block += """
- `raw_reference` (str): Raw citation text as it appears in the circular (e.g., `CIR/CFD/CMD/4/2015`).
- `normalized_circular_number` (str): Canonical form (lowercase, standardized).
- `context_window` (str): Surrounding text (~60 characters on each side, whitespace collapsed).
- `source_doc_id` (str): Circular containing the reference.
- `format_family` (str): Reference format category:
  - `new-standard`: SEBI/HO/DEPT/P/CIR/YYYY/NNN (post-2015 format).
  - `old-standard`: CIR/DEPT/YYYY/NNN (legacy format).
  - `dept-order-2026`: HO/(NN)YYYY-DEPT (departmental order format, 2026).

**Task:** Seq2seq/NER: predict normalized circular number from raw reference; or use as training set for reference extraction/normalization models.
"""

    if "supersession-pairs" in datasets:
        supersession_schema = datasets["supersession-pairs"]["schema"]
        yaml_block += "\n### supersession-pairs\n\n"
        yaml_block += "**Columns:** " + ", ".join(f"`{c}`" for c in supersession_schema) + "\n"
        yaml_block += f"\n{datasets['supersession-pairs']['rows']:,} labeled circular pairs: positives from lineage, negatives sampled same-department (2:1 ratio).\n"
        yaml_block += """
- `circular_a_number` (str): First circular.
- `circular_a_subject` (str): Subject of circular A.
- `circular_b_number` (str): Second circular.
- `circular_b_subject` (str): Subject of circular B.
- `label` (str): `supersedes`, `amends`, or `unrelated`.

**Task:** Pair classification: does circular A supersede/amend circular B? Positives from lineage edges (both endpoints in corpus); negatives sampled deterministically (seed=42) from same-department non-linked pairs.
"""

    yaml_block += """
## Licensing & Compliance

**Underlying Regulatory Text:** SEBI circulars are Indian government works. Per India's Copyright Act 1957 §52(1)(q), government orders/notifications may be freely reproduced. We attribute SEBI and provide `source_url` per record for verification.

**Compilation & Annotations:** The metadata extraction, chunking, lineage graph, normalized citations, and pair labels are original annotations licensed under **CC-BY-4.0**.

### Disclaimers

1. **Not legal advice.** These circulars are informational only. Verify against sebi.gov.in before regulatory reliance.
2. **Not SEBI-endorsed.** This dataset is independent; not affiliated with or endorsed by the Securities and Exchange Board of India.
3. **Coverage:** Corpus spans 2021–2026 and is not exhaustive of all SEBI circulars.
4. **Data quality:** `issuing_department` is UNKNOWN for 124 records (parsing artifact). Some master-circular `subject` fields may be oversized (~2900 chars, also a parsing artifact).

## Citation

Please cite this dataset if you use it:

```bibtex
@dataset{sebi_circulars_2026,
  title={SEBI Circulars: Indian Regulatory Texts, 2021–2026},
  author={OpenSourceContributor},
  year={2026},
  url={https://huggingface.co/datasets/...},
  license={CC-BY-4.0}
}
```

## Repository

Full dataset extraction pipeline and reproducibility information:
- **GitHub:** https://github.com/your-repo/sebi-rag
- **Extraction date:** 2026-07-09
- **Snapshot:** v2026.07 (max issue_date across corpus)

## Suggested Use Cases

- **Retrieval & RAG:** chunks config for dense/hybrid retrieval pipelines.
- **Citation Mining:** citation-normalization for training sequence-to-sequence or NER models.
- **Regulatory Reasoning:** lineage for link prediction, temporal reasoning, and regulatory change tracking.
- **Pair Classification:** supersession-pairs for supervised learning on relationship prediction.
- **Benchmark:** eval config (56 curated queries) for domain-specific retrieval evaluation.

## Contact

For questions or issues: [your-email]
"""
    return yaml_block


def build_kaggle_metadata(datasets: dict[str, dict]) -> str:
    """Build Kaggle metadata.json."""
    meta = {
        "id": "sebi-circulars-india-regulatory",
        "title": "SEBI Circulars: Indian Regulatory Texts (2021–2026)",
        "subtitle": "Structured dataset of public-domain SEBI circulars for AI/ML research",
        "description": (
            "Six configurations: corpus (603 circulars), chunks (36,603 retrieval chunks), "
            "lineage (1,434 supersession/amendment edges), eval (56-query benchmark), "
            "citation-normalization (2,951 reference pairs), supersession-pairs (1,281 labeled pairs). "
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


def build_zenodo_pack(datasets: dict[str, dict]) -> dict:
    """Build Zenodo submission metadata + tarball instructions."""
    return {
        "metadata": {
            "title": "SEBI Circulars: Indian Regulatory Texts (2021–2026)",
            "description": (
                "Structured dataset of 603 SEBI regulatory circulars with lineage, "
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
            "publication_date": "2026-07-09",
        },
        "instructions": (
            "1. Create tarball: tar czf sebi-circulars-v2026.07.tar.gz dist/datasets/\n"
            "2. Upload to Zenodo via web UI or API\n"
            "3. Record DOI and update HF/Kaggle cards with DOI link"
        ),
    }


def build_aikosh_pack(datasets: dict[str, dict]) -> dict:
    """Build AIKosh (IndiaAI) submission pack: CSV manifest + metadata + licensing."""
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
            "title": "SEBI Circulars: Indian Regulatory Texts (2021–2026)",
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
            "Disclaimers: Not legal advice; not SEBI-endorsed; corpus is 2021–2026 (not exhaustive)."
        ),
    }


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
        # Get schema from globals (CORPUS_SCHEMA, CHUNKS_SCHEMA, etc.)
        schema_name = cfg.replace("-", "_").upper() + "_SCHEMA"
        schema = globals().get(schema_name, [])
        datasets[cfg] = {"rows": rows, "schema": schema}

    # HuggingFace card
    hf_card = build_hf_card(datasets)
    (out_dir / "README.md").write_text(hf_card, encoding="utf-8")

    # Kaggle metadata
    kaggle_meta = build_kaggle_metadata(datasets)
    (out_dir / "metadata.json").write_text(kaggle_meta, encoding="utf-8")

    # Zenodo pack
    zenodo_pack = build_zenodo_pack(datasets)
    zenodo_dir = out_dir / "ZENODO_SUBMISSION_PACK"
    zenodo_dir.mkdir(exist_ok=True)
    (zenodo_dir / "metadata.json").write_text(json.dumps(zenodo_pack["metadata"], indent=2, ensure_ascii=False), encoding="utf-8")
    (zenodo_dir / "README_TARBALL.txt").write_text(zenodo_pack["instructions"], encoding="utf-8")

    # AIKosh pack
    aikosh_pack = build_aikosh_pack(datasets)
    aikosh_dir = out_dir / "AIKOSH_SUBMISSION_PACK"
    aikosh_dir.mkdir(exist_ok=True)
    (aikosh_dir / "manifest.csv").write_text(aikosh_pack["manifest_csv"], encoding="utf-8")
    (aikosh_dir / "metadata.json").write_text(json.dumps(aikosh_pack["metadata"], indent=2, ensure_ascii=False), encoding="utf-8")
    (aikosh_dir / "LICENSING.txt").write_text(aikosh_pack["licensing"], encoding="utf-8")

    print(f"Dataset cards written to {out_dir}/")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", default="data/corpus/circulars.jsonl")
    ap.add_argument("--chunks", default="data/index/chunks.jsonl")
    ap.add_argument("--lineage", default="data/index/lineage.json")
    ap.add_argument("--golden", default="eval/golden/golden_v6.jsonl")
    ap.add_argument("--out", default="dist/datasets")
    args = ap.parse_args(argv)
    out_dir = Path(args.out)
    manifest = export_all(Path(args.corpus), Path(args.chunks), Path(args.lineage),
                          Path(args.golden), out_dir)
    write_dataset_cards(out_dir)  # Task 4: generate platform-specific cards
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
