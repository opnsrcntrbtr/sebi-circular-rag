# Evidence Base Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the SEBI RAG intervention archive readable by standard IR tooling, comparable across time, and honest about label provenance — so that statistically decidable research can be built on top of it.

**Architecture:** A new `src/sebi_rag/autoresearch/` package holds two pure, offline modules — `trecio.py` (standards-compliant TREC run/qrels emission) and `epoch.py` (corpus-snapshot identity and a comparability guard). Driver scripts in `scripts/autoresearch/` apply them to the existing 31-run archive and to `golden_v7`. Existing code is reused rather than reimplemented: `benchmark.read_trec_run` already recovers the malformed legacy doc ids, and `benchmark.run_metadata` already pins the fingerprints that make epochs derivable.

**Tech Stack:** Python 3.12 (`.venv`), pytest 9.1.1, numpy 2.5.1, scipy 1.18.0, `ir_measures` (new, optional extra only).

## Global Constraints

- **Never add fields to `CircularMeta`** (`src/sebi_rag/segment.py`). `hierarchical_chunk()` does `meta=asdict(meta)` at `segment.py:131`; a new field lands in all 78,523 chunk payloads and mutates the 1.0 GB persisted index. `golden_v7.jsonl` is the eval set, not `CircularMeta` — editing it is permitted.
- **Never edit `*_spaces.py` or root `app.py`.** Those are the CPU-only HF Spaces path.
- **Never mutate `data/index/`.** Every task in this plan opens it read-only.
- All Python runs via `.venv/bin/python` with `PYTHONPATH=src`. The Makefile provides this as `$(PY)` and `$(ENV)`.
- `make test` must still pass at **≥667** after every task.
- New tests are offline: no network, no model weights, no `data/index/` load. Anything needing real models gets `@pytest.mark.integration`.
- `benchmark.write_qrels` (`src/sebi_rag/benchmark.py:375`) emits **BEIR TSV**, not TREC qrels. Do not modify, shadow, or rename it.
- Preserve retrieval anchors character-for-character: file paths, function names, and metric keys must match existing spellings exactly.

---

### Task 1: `chunk_docid` — whitespace-free TREC doc ids

**Files:**
- Create: `src/sebi_rag/autoresearch/__init__.py`
- Create: `src/sebi_rag/autoresearch/trecio.py`
- Test: `tests/test_trecio.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `chunk_docid(chunk_id: str) -> str`; `class MalformedChunkId(ValueError)`.

Chunk ids have the grammar `<circular_id>#<heading_text>#<ordinal>`, e.g. `SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123#preamble#0`. The `circular_id` contains `/` but never whitespace or `#`; `heading_text` contains whitespace; `ordinal` is an integer. Keeping `circular_id` and `ordinal` and dropping the heading gives a whitespace-free id that is still unique.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_trecio.py
import pytest

from sebi_rag.autoresearch.trecio import MalformedChunkId, chunk_docid


def test_drops_heading_and_keeps_circular_and_ordinal():
    cid = "SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123#preamble#0"
    assert chunk_docid(cid) == "SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123#0"


def test_drops_heading_containing_spaces_and_hashes():
    cid = (
        "SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123"
        "#1. SEBI vide circular no. CIR/CFD/CMD/4/2015 dated September#1"
    )
    assert chunk_docid(cid) == "SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123#1"


def test_result_never_contains_whitespace():
    cid = "HO/43/15/12(3)2025-ISD-POD2/I/11734/2026#3. With the issuance of this#8"
    assert not any(ch.isspace() for ch in chunk_docid(cid))


def test_chunk_id_without_hash_is_returned_unchanged():
    assert chunk_docid("SEBI/HO/CFD/P/CIR/2023/123") == "SEBI/HO/CFD/P/CIR/2023/123"


def test_circular_id_containing_whitespace_raises():
    with pytest.raises(MalformedChunkId):
        chunk_docid("SEBI/HO/BAD ID/2023/1#heading#0")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_trecio.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sebi_rag.autoresearch'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/sebi_rag/autoresearch/__init__.py
"""Auto-research support: standards-compliant eval artifacts and epoch identity."""
```

```python
# src/sebi_rag/autoresearch/trecio.py
"""Standards-compliant TREC run and qrels emission.

The archived runfiles are not valid TREC: chunk ids embed a section heading
containing spaces, so a run line splits into ~15 fields instead of 6 and
trec_eval cannot read it. `benchmark.read_trec_run` recovers those legacy
files; this module is the forward path that stops producing them.
"""
from __future__ import annotations


class MalformedChunkId(ValueError):
    """Raised when a chunk id cannot yield a whitespace-free TREC doc id."""


def chunk_docid(chunk_id: str) -> str:
    """Map a chunk id to a whitespace-free TREC doc id.

    `<circular>#<heading with spaces>#<ordinal>` -> `<circular>#<ordinal>`.
    The heading is dropped; `docids.tsv` preserves the full id for reversal.
    """
    if "#" not in chunk_id:
        docid = chunk_id
    else:
        circular = chunk_id.split("#", 1)[0]
        ordinal = chunk_id.rsplit("#", 1)[1]
        docid = f"{circular}#{ordinal}"
    if any(ch.isspace() for ch in docid):
        raise MalformedChunkId(
            f"doc id still contains whitespace after heading removal: {docid!r}"
        )
    return docid
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_trecio.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Verify injectivity against the real chunk store**

The mapping is only safe if `(circular, ordinal)` is unique per chunk. Verify against the real 78,523 chunks — this is a one-off check, not a unit test (the file is ~312 MB).

Run:
```bash
.venv/bin/python -c "
import json, collections, sys
sys.path.insert(0, 'src')
from sebi_rag.autoresearch.trecio import chunk_docid
seen = collections.defaultdict(list)
for line in open('data/index/chunks.jsonl'):
    cid = json.loads(line)['id']
    seen[chunk_docid(cid)].append(cid)
collisions = {d: v for d, v in seen.items() if len(v) > 1}
print('chunks:', sum(len(v) for v in seen.values()), 'docids:', len(seen))
print('collisions:', len(collisions))
for d, v in list(collisions.items())[:5]:
    print(' ', d, '<-', v[:3])
"
```
Expected: `collisions: 0`.

**If collisions are non-zero, STOP.** Do not proceed. Report the collision examples — the docid scheme needs a disambiguator (append a short hash of the heading) and Task 2 depends on the final scheme.

- [ ] **Step 6: Commit**

```bash
git add src/sebi_rag/autoresearch/__init__.py src/sebi_rag/autoresearch/trecio.py tests/test_trecio.py
git commit -m "feat(autoresearch): add chunk_docid for whitespace-free TREC doc ids"
```

---

### Task 2: TREC run writers

**Files:**
- Modify: `src/sebi_rag/autoresearch/trecio.py`
- Test: `tests/test_trecio.py`

**Interfaces:**
- Consumes: `chunk_docid` from Task 1.
- Produces:
  - `write_run_chunk(path, run_name: str, rankings: dict[str, list[tuple[str, float]]]) -> None`
  - `write_run_doc(path, run_name: str, rankings: dict[str, list[tuple[str, float]]]) -> None`
  - `write_docids(path, rankings: dict[str, list[tuple[str, float]]]) -> None`

`rankings` is the existing shape used by `benchmark.write_trec_run` and returned by `benchmark.read_trec_run`: `{qid: [(chunk_id, score), ...]}` in rank order.

`write_run_doc` collapses chunks to circular level, because relevance judgments in `golden_v7` are circular-level (`relevant_circulars`). Scoring a chunk-level run against circular-level qrels is a category error. Circular extraction uses the existing helper `eval_harness._doc` (`chunk_id.split("#", 1)[0]`).

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_trecio.py
from sebi_rag.autoresearch.trecio import write_docids, write_run_chunk, write_run_doc

RANKINGS = {
    "q1": [
        ("SEBI/A/2023/1#preamble#0", 0.90),
        ("SEBI/B/2023/2#2. Some heading here#5", 0.80),
        ("SEBI/A/2023/1#3. Another heading#7", 0.70),
    ],
    "q2": [("SEBI/C/2023/3#intro#0", 0.60)],
}


def test_run_chunk_lines_have_exactly_six_fields(tmp_path):
    p = tmp_path / "run.chunk.trec"
    write_run_chunk(p, "unit-test", RANKINGS)
    lines = p.read_text().splitlines()
    assert len(lines) == 4
    for line in lines:
        assert len(line.split()) == 6, line


def test_run_chunk_preserves_rank_order_and_tag(tmp_path):
    p = tmp_path / "run.chunk.trec"
    write_run_chunk(p, "unit-test", RANKINGS)
    first = p.read_text().splitlines()[0].split()
    assert first[0] == "q1"
    assert first[1] == "Q0"
    assert first[2] == "SEBI/A/2023/1#0"
    assert first[3] == "1"
    assert first[5] == "unit-test"


def test_run_doc_dedupes_to_best_rank(tmp_path):
    p = tmp_path / "run.doc.trec"
    write_run_doc(p, "unit-test", RANKINGS)
    lines = [line.split() for line in p.read_text().splitlines()]
    q1 = [line for line in lines if line[0] == "q1"]
    # SEBI/A/2023/1 appears at chunk ranks 1 and 3; it must appear once, at rank 1.
    assert [line[2] for line in q1] == ["SEBI/A/2023/1", "SEBI/B/2023/2"]
    assert [line[3] for line in q1] == ["1", "2"]


def test_run_doc_lines_have_exactly_six_fields(tmp_path):
    p = tmp_path / "run.doc.trec"
    write_run_doc(p, "unit-test", RANKINGS)
    for line in p.read_text().splitlines():
        assert len(line.split()) == 6, line


def test_docids_maps_docid_back_to_full_chunk_id(tmp_path):
    p = tmp_path / "docids.tsv"
    write_docids(p, RANKINGS)
    rows = dict(line.split("\t") for line in p.read_text().splitlines())
    assert rows["SEBI/B/2023/2#5"] == "SEBI/B/2023/2#2. Some heading here#5"
    assert len(rows) == 4
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_trecio.py -v`
Expected: FAIL — `ImportError: cannot import name 'write_run_chunk'`

- [ ] **Step 3: Write minimal implementation**

```python
# append to src/sebi_rag/autoresearch/trecio.py
from pathlib import Path

from ..eval_harness import _doc

Rankings = dict[str, list[tuple[str, float]]]


def _write_lines(path: str | Path, lines: list[str]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(lines), encoding="utf-8")


def write_run_chunk(path: str | Path, run_name: str, rankings: Rankings) -> None:
    """Valid 6-field TREC run at chunk granularity."""
    lines = []
    for qid, ranked in rankings.items():
        for rank, (chunk_id, score) in enumerate(ranked, start=1):
            lines.append(
                f"{qid} Q0 {chunk_docid(chunk_id)} {rank} {score:.8f} {run_name}\n"
            )
    _write_lines(path, lines)


def write_run_doc(path: str | Path, run_name: str, rankings: Rankings) -> None:
    """Valid 6-field TREC run collapsed to circular level.

    Keeps each circular once, at its best (lowest) chunk rank, carrying that
    chunk's score. Ranks are renumbered 1..n so the file is well-formed.
    """
    lines = []
    for qid, ranked in rankings.items():
        best: dict[str, float] = {}
        for chunk_id, score in ranked:
            circular = _doc(chunk_id)
            if circular not in best:
                best[circular] = score
        for rank, (circular, score) in enumerate(best.items(), start=1):
            lines.append(f"{qid} Q0 {circular} {rank} {score:.8f} {run_name}\n")
    _write_lines(path, lines)


def write_docids(path: str | Path, rankings: Rankings) -> None:
    """Reverse map `docid -> full chunk id`, so nothing is lost."""
    mapping: dict[str, str] = {}
    for ranked in rankings.values():
        for chunk_id, _ in ranked:
            mapping[chunk_docid(chunk_id)] = chunk_id
    lines = [f"{d}\t{c}\n" for d, c in mapping.items()]
    _write_lines(path, lines)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_trecio.py -v`
Expected: PASS (10 tests)

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/autoresearch/trecio.py tests/test_trecio.py
git commit -m "feat(autoresearch): emit valid chunk-level and doc-level TREC runs"
```

---

### Task 3: TREC qrels writer

**Files:**
- Modify: `src/sebi_rag/autoresearch/trecio.py`
- Test: `tests/test_trecio.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `write_trec_qrels(path, golden: list[dict]) -> int` — returns the number of qrels lines written.

TREC qrels format is `<qid> 0 <docid> <rel>`, space-separated, **no header**. This is deliberately different from `benchmark.write_qrels`, which emits BEIR TSV with a `query-id\tcorpus-id\tscore` header for `export_benchmark`. Both must coexist.

Rows with `abstain: true` contribute no lines — they are scored by `abstention_accuracy`, not retrieval metrics. This matches `benchmark.per_query_recall`, which skips them.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_trecio.py
from sebi_rag.autoresearch.trecio import write_trec_qrels

GOLDEN = [
    {"id": "q1", "abstain": False, "relevant_circulars": ["SEBI/A/2023/1", "SEBI/B/2023/2"]},
    {"id": "q2", "abstain": True, "relevant_circulars": []},
    {"id": "q3", "abstain": False, "relevant_circulars": ["SEBI/C/2023/3"]},
]


def test_qrels_lines_are_four_space_separated_fields(tmp_path):
    p = tmp_path / "e4.qrels"
    write_trec_qrels(p, GOLDEN)
    for line in p.read_text().splitlines():
        parts = line.split()
        assert len(parts) == 4, line
        assert parts[1] == "0"
        assert parts[3] == "1"


def test_qrels_has_no_header(tmp_path):
    p = tmp_path / "e4.qrels"
    write_trec_qrels(p, GOLDEN)
    assert p.read_text().splitlines()[0].split()[0] == "q1"


def test_qrels_expands_relevant_circulars(tmp_path):
    p = tmp_path / "e4.qrels"
    n = write_trec_qrels(p, GOLDEN)
    pairs = {(line.split()[0], line.split()[2]) for line in p.read_text().splitlines()}
    assert pairs == {
        ("q1", "SEBI/A/2023/1"),
        ("q1", "SEBI/B/2023/2"),
        ("q3", "SEBI/C/2023/3"),
    }
    assert n == 3


def test_qrels_excludes_abstain_rows(tmp_path):
    p = tmp_path / "e4.qrels"
    write_trec_qrels(p, GOLDEN)
    assert "q2" not in p.read_text()


def test_qrels_raises_when_nothing_would_be_written(tmp_path):
    with pytest.raises(ValueError, match="no qrels"):
        write_trec_qrels(tmp_path / "empty.qrels", [{"id": "q9", "abstain": True}])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_trecio.py -v`
Expected: FAIL — `ImportError: cannot import name 'write_trec_qrels'`

- [ ] **Step 3: Write minimal implementation**

```python
# append to src/sebi_rag/autoresearch/trecio.py
def write_trec_qrels(path: str | Path, golden: list[dict]) -> int:
    """Write TREC qrels (`qid 0 docid rel`) at circular level.

    Binary relevance: golden_v7 carries no graded judgments and none are
    invented. Abstain rows contribute nothing, matching per_query_recall.
    Returns the number of lines written.
    """
    lines = []
    for row in golden:
        if row.get("abstain"):
            continue
        qid = row["id"]
        for circular in row.get("relevant_circulars", []):
            lines.append(f"{qid} 0 {circular} 1\n")
    if not lines:
        raise ValueError(f"no qrels to write for {path}: every row was abstain or empty")
    _write_lines(path, lines)
    return len(lines)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_trecio.py -v`
Expected: PASS (15 tests)

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/autoresearch/trecio.py tests/test_trecio.py
git commit -m "feat(autoresearch): add TREC qrels writer, distinct from BEIR export"
```

---

### Task 4: Legacy run converter

**Files:**
- Create: `scripts/autoresearch/__init__.py`
- Create: `scripts/autoresearch/convert_legacy_runs.py`
- Test: `tests/test_convert_legacy_runs.py`

**Interfaces:**
- Consumes: `write_run_chunk`, `write_run_doc`, `write_docids` (Task 2); `benchmark.read_trec_run` (existing, `src/sebi_rag/benchmark.py:395`).
- Produces: `convert_run_dir(run_dir: Path) -> dict` with keys `status` (`"converted"` / `"skipped"` / `"failed"`), `reason`, `n_lines`.

`read_trec_run` already recovers space-bearing doc ids via `parts[2:-3]`, and its docstring documents the defect. This task is a thin driver over it, not a reimplementation. The original `run.trec` is never modified — it is the historical record.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_convert_legacy_runs.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from autoresearch.convert_legacy_runs import convert_run_dir

LEGACY = (
    "q1 Q0 SEBI/A/2023/1#preamble#0 1 0.90000000 baseline-retrieval\n"
    "q1 Q0 SEBI/B/2023/2#2. Some heading here#5 2 0.80000000 baseline-retrieval\n"
    "q1 Q0 SEBI/A/2023/1#3. Another heading#7 3 0.70000000 baseline-retrieval\n"
)


def _make_run(tmp_path: Path, text: str = LEGACY) -> Path:
    run_dir = tmp_path / "iv2-golden"
    run_dir.mkdir()
    (run_dir / "run.trec").write_text(text, encoding="utf-8")
    return run_dir


def test_emits_three_artifacts(tmp_path):
    run_dir = _make_run(tmp_path)
    result = convert_run_dir(run_dir)
    assert result["status"] == "converted"
    assert (run_dir / "run.chunk.trec").exists()
    assert (run_dir / "run.doc.trec").exists()
    assert (run_dir / "docids.tsv").exists()


def test_original_runfile_is_untouched(tmp_path):
    run_dir = _make_run(tmp_path)
    convert_run_dir(run_dir)
    assert (run_dir / "run.trec").read_text(encoding="utf-8") == LEGACY


def test_converted_chunk_run_is_valid_trec(tmp_path):
    run_dir = _make_run(tmp_path)
    convert_run_dir(run_dir)
    for line in (run_dir / "run.chunk.trec").read_text().splitlines():
        assert len(line.split()) == 6, line


def test_docids_recovers_the_space_bearing_chunk_id(tmp_path):
    run_dir = _make_run(tmp_path)
    convert_run_dir(run_dir)
    rows = dict(
        line.split("\t")
        for line in (run_dir / "docids.tsv").read_text().splitlines()
    )
    assert rows["SEBI/B/2023/2#5"] == "SEBI/B/2023/2#2. Some heading here#5"


def test_missing_runfile_is_skipped_not_failed(tmp_path):
    run_dir = tmp_path / "pool-sweep"
    run_dir.mkdir()
    (run_dir / "sweep.json").write_text("{}", encoding="utf-8")
    result = convert_run_dir(run_dir)
    assert result["status"] == "skipped"
    assert "no run.trec" in result["reason"]


def test_whitespace_in_run_tag_fails_without_writing(tmp_path):
    # A tag with a space breaks the fixed-tail assumption read_trec_run relies on.
    bad = "q1 Q0 SEBI/A/2023/1#preamble#0 1 0.90000000 bad tag\n"
    run_dir = _make_run(tmp_path, bad)
    result = convert_run_dir(run_dir)
    assert result["status"] == "failed"
    assert not (run_dir / "run.chunk.trec").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_convert_legacy_runs.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'autoresearch.convert_legacy_runs'`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/autoresearch/__init__.py
"""Driver scripts for auto-research evidence-base maintenance."""
```

```python
# scripts/autoresearch/convert_legacy_runs.py
"""Back-convert archived runfiles into standards-compliant TREC artifacts.

The archived `run.trec` files embed section headings inside the doc id, so a
line splits into ~15 fields and trec_eval cannot read them. `read_trec_run`
already recovers them; this writes the valid artifacts alongside. The original
`run.trec` is never modified.

    .venv/bin/python scripts/autoresearch/convert_legacy_runs.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.autoresearch.trecio import (  # noqa: E402
    write_docids,
    write_run_chunk,
    write_run_doc,
)
from sebi_rag.benchmark import read_trec_run  # noqa: E402

RUNS_DIR = ROOT / "eval" / "runs"


def _run_tag(runfile: Path) -> str:
    """Trailing field of the first line; also the whitespace precondition check."""
    for line in runfile.read_text(encoding="utf-8").splitlines():
        if line.strip():
            return line.split()[-1]
    raise ValueError("runfile is empty")


def _assert_fixed_tail(runfile: Path) -> None:
    """read_trec_run assumes qid and tag carry no whitespace. Verify per line."""
    tag = _run_tag(runfile)
    for n, line in enumerate(runfile.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 6:
            raise ValueError(f"line {n}: fewer than 6 fields")
        if parts[-1] != tag:
            raise ValueError(
                f"line {n}: run tag {parts[-1]!r} != {tag!r}; tag may contain whitespace"
            )
        try:
            int(parts[-3])
            float(parts[-2])
        except ValueError as exc:
            raise ValueError(f"line {n}: rank/score not at fixed tail positions") from exc


def convert_run_dir(run_dir: Path) -> dict:
    """Write run.chunk.trec, run.doc.trec and docids.tsv for one archived run."""
    runfile = run_dir / "run.trec"
    if not runfile.exists():
        return {"status": "skipped", "reason": "no run.trec", "n_lines": 0}
    try:
        _assert_fixed_tail(runfile)
        rankings = read_trec_run(runfile)
        tag = _run_tag(runfile)
    except ValueError as exc:
        return {"status": "failed", "reason": str(exc), "n_lines": 0}

    write_run_chunk(run_dir / "run.chunk.trec", tag, rankings)
    write_run_doc(run_dir / "run.doc.trec", tag, rankings)
    write_docids(run_dir / "docids.tsv", rankings)
    n = sum(len(v) for v in rankings.values())
    return {"status": "converted", "reason": "", "n_lines": n}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs-dir", type=Path, default=RUNS_DIR)
    args = ap.parse_args()

    report = {}
    for run_dir in sorted(p for p in args.runs_dir.iterdir() if p.is_dir()):
        report[run_dir.name] = convert_run_dir(run_dir)

    for name, r in report.items():
        print(f"{name:<32} {r['status']:<10} {r['reason']}")
    counts: dict[str, int] = {}
    for r in report.values():
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print("\n" + json.dumps(counts))
    if counts.get("failed"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_convert_legacy_runs.py -v`
Expected: PASS (6 tests)

- [ ] **Step 5: Convert the real archive**

Run: `.venv/bin/python scripts/autoresearch/convert_legacy_runs.py`
Expected: every directory reports `converted` or `skipped`. `{"converted": N, "skipped": M}` with **zero `failed`**.

If any directory reports `failed`, record the run name and reason in the commit message and report it — do not hand-edit the archive.

- [ ] **Step 6: Commit**

```bash
git add scripts/autoresearch/__init__.py scripts/autoresearch/convert_legacy_runs.py \
        tests/test_convert_legacy_runs.py eval/runs
git commit -m "feat(autoresearch): back-convert archived runs to valid TREC"
```

---

### Task 5: Emit the new artifacts on every future run

**Files:**
- Modify: `scripts/bench_retrieval.py:175`
- Test: `tests/test_bench_retrieval_artifacts.py`

**Interfaces:**
- Consumes: `write_run_chunk`, `write_run_doc`, `write_docids` (Task 2).
- Produces: no new symbols; `bench_retrieval` now writes four run artifacts instead of one.

`scripts/bench_retrieval.py:175` currently writes only the legacy file:

```python
write_trec_run(out / "run.trec", "baseline-retrieval", result["rankings"])
```

Keep it — existing tooling (`rescore_runs.py`) reads it — and add the three valid artifacts alongside.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_bench_retrieval_artifacts.py
"""bench_retrieval must emit valid TREC alongside the legacy runfile."""
import re
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "bench_retrieval.py"


def test_bench_retrieval_writes_all_four_artifacts():
    src = SCRIPT.read_text(encoding="utf-8")
    for name in ("run.trec", "run.chunk.trec", "run.doc.trec", "docids.tsv"):
        assert re.search(rf'["\']{re.escape(name)}["\']', src), f"{name} not written"


def test_bench_retrieval_imports_the_valid_writers():
    src = SCRIPT.read_text(encoding="utf-8")
    assert "from sebi_rag.autoresearch.trecio import" in src
    for fn in ("write_run_chunk", "write_run_doc", "write_docids"):
        assert fn in src
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_bench_retrieval_artifacts.py -v`
Expected: FAIL — `run.chunk.trec not written`

- [ ] **Step 3: Write minimal implementation**

Add to the import block of `scripts/bench_retrieval.py`, next to the existing `from sebi_rag.benchmark import ...` line:

```python
from sebi_rag.autoresearch.trecio import (  # noqa: E402
    write_docids,
    write_run_chunk,
    write_run_doc,
)
```

Replace line 175 with:

```python
    write_trec_run(out / "run.trec", "baseline-retrieval", result["rankings"])
    # Valid 6-field TREC alongside the legacy file, which embeds headings in the
    # doc id and cannot be read by trec_eval / ir_measures.
    write_run_chunk(out / "run.chunk.trec", "baseline-retrieval", result["rankings"])
    write_run_doc(out / "run.doc.trec", "baseline-retrieval", result["rankings"])
    write_docids(out / "docids.tsv", result["rankings"])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_bench_retrieval_artifacts.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/bench_retrieval.py tests/test_bench_retrieval_artifacts.py
git commit -m "feat(bench): emit valid TREC artifacts alongside legacy runfile"
```

---

### Task 6: Epoch and Frame model

**Files:**
- Create: `src/sebi_rag/autoresearch/epoch.py`
- Test: `tests/test_epoch.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `@dataclass(frozen=True) class Frame` with fields `epoch: str`, `eval_set: str`
  - `class IncomparableFramesError(RuntimeError)`
  - `frame_of(results: dict, epoch_by_corpus: dict[str, str]) -> Frame | None`
  - `assert_comparable(a: Frame | None, b: Frame | None, *, label_a: str, label_b: str) -> None`

An **epoch** is a corpus snapshot keyed by `corpus_sha256`. An **eval set** is keyed by `golden_sha256`. A **frame** is the pair; two runs are comparable if and only if they share a frame. Epoch is keyed on corpus alone because `golden`, `probes` and `asof` are different instruments applied to the same corpus — folding them into the epoch key would wrongly split one corpus into three.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_epoch.py
import pytest

from sebi_rag.autoresearch.epoch import (
    Frame,
    IncomparableFramesError,
    assert_comparable,
    frame_of,
)

EPOCHS = {"4083518f": "E1", "913e762c": "E2"}


def _results(corpus: str, golden: str) -> dict:
    return {"metadata": {"corpus_sha256": corpus, "golden_sha256": golden}}


def test_frame_pairs_epoch_with_eval_set():
    f = frame_of(_results("913e762c", "f01d8779"), EPOCHS)
    assert f == Frame(epoch="E2", eval_set="f01d8779")


def test_same_corpus_different_instruments_share_an_epoch():
    golden = frame_of(_results("913e762c", "f01d8779"), EPOCHS)
    probes = frame_of(_results("913e762c", "99a9da66"), EPOCHS)
    assert golden.epoch == probes.epoch == "E2"
    assert golden != probes


def test_unknown_corpus_yields_no_frame():
    assert frame_of(_results("deadbeef", "f01d8779"), EPOCHS) is None


def test_missing_corpus_sha_yields_no_frame():
    assert frame_of({"metadata": {"golden_sha256": "f01d8779"}}, EPOCHS) is None


def test_identical_frames_are_comparable():
    f = Frame(epoch="E2", eval_set="f01d8779")
    assert_comparable(f, f, label_a="iv7", label_b="iv8")


def test_different_epochs_raise():
    a = Frame(epoch="E1", eval_set="f01d8779")
    b = Frame(epoch="E2", eval_set="f01d8779")
    with pytest.raises(IncomparableFramesError, match="E1.*E2"):
        assert_comparable(a, b, label_a="ft", label_b="iv8")


def test_different_eval_sets_raise():
    a = Frame(epoch="E2", eval_set="f01d8779")
    b = Frame(epoch="E2", eval_set="99a9da66")
    with pytest.raises(IncomparableFramesError, match="f01d8779.*99a9da66"):
        assert_comparable(a, b, label_a="iv7-golden", label_b="iv7-probes")


def test_unframed_run_raises():
    a = Frame(epoch="E2", eval_set="f01d8779")
    with pytest.raises(IncomparableFramesError, match="no frame"):
        assert_comparable(a, None, label_a="iv7", label_b="pool-sweep")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_epoch.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sebi_rag.autoresearch.epoch'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/sebi_rag/autoresearch/epoch.py
"""Epoch and frame identity for comparable measurement.

The corpus drifts on a weekly n8n refresh, so it needs a controlled identity:
an *epoch* is a corpus snapshot keyed by corpus_sha256. An *eval set* is a
golden file keyed by golden_sha256. A *frame* is the pair, and two runs are
comparable if and only if they share one.

Epoch is keyed on the corpus alone: `golden`, `probes` and `asof` are separate
instruments applied to the same corpus, not separate corpora.
"""
from __future__ import annotations

from dataclasses import dataclass


class IncomparableFramesError(RuntimeError):
    """Raised when a paired comparison spans two frames."""


@dataclass(frozen=True)
class Frame:
    epoch: str
    eval_set: str

    def __str__(self) -> str:  # pragma: no cover - formatting only
        return f"{self.epoch}/{self.eval_set[:8]}"


def frame_of(results: dict, epoch_by_corpus: dict[str, str]) -> Frame | None:
    """Derive a run's frame from its results.json payload.

    Returns None when the run predates fingerprinting or its corpus is not in
    the registry — such runs are excluded from comparisons rather than guessed.
    """
    meta = results.get("metadata") or {}
    corpus = meta.get("corpus_sha256")
    golden = meta.get("golden_sha256")
    if not corpus or not golden:
        return None
    epoch = epoch_by_corpus.get(corpus[:8]) or epoch_by_corpus.get(corpus)
    if not epoch:
        return None
    return Frame(epoch=epoch, eval_set=golden[:8])


def assert_comparable(
    a: Frame | None,
    b: Frame | None,
    *,
    label_a: str,
    label_b: str,
) -> None:
    """Raise unless both runs sit in the same frame."""
    if a is None or b is None:
        missing = label_a if a is None else label_b
        raise IncomparableFramesError(
            f"cannot compare {label_a} with {label_b}: {missing} has no frame"
        )
    if a.epoch != b.epoch:
        raise IncomparableFramesError(
            f"cannot compare {label_a} (epoch {a.epoch}) with "
            f"{label_b} (epoch {b.epoch}): different corpora"
        )
    if a.eval_set != b.eval_set:
        raise IncomparableFramesError(
            f"cannot compare {label_a} (eval set {a.eval_set}) with "
            f"{label_b} (eval set {b.eval_set}): different golden files"
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_epoch.py -v`
Expected: PASS (8 tests)

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/autoresearch/epoch.py tests/test_epoch.py
git commit -m "feat(autoresearch): add epoch/frame identity and comparability guard"
```

---

### Task 7: Backfill epochs onto the archive

**Files:**
- Modify: `src/sebi_rag/autoresearch/epoch.py`
- Create: `scripts/autoresearch/backfill_epochs.py`
- Test: `tests/test_backfill_epochs.py`

**Interfaces:**
- Consumes: `Frame`, `frame_of` (Task 6).
- Produces:
  - `assign_epochs(runs: list[tuple[str, dict]]) -> dict[str, str]` — maps `corpus_sha256[:8] -> epoch id`, added to `epoch.py`
  - `load_epoch_registry(path) -> dict[str, str]`, added to `epoch.py`
  - `scripts/autoresearch/backfill_epochs.py` writing `eval/epochs/epochs.jsonl`

Epoch ids are assigned deterministically: corpora are ordered by the earliest run timestamp observed for each, then numbered `E1`, `E2`, … so re-running the backfill is stable.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_backfill_epochs.py
import json

from sebi_rag.autoresearch.epoch import assign_epochs, load_epoch_registry


def _r(corpus: str, ts: str) -> dict:
    return {"metadata": {"corpus_sha256": corpus, "golden_sha256": "f01d8779", "ts": ts}}


RUNS = [
    ("iv6-golden", _r("913e762c11", "2026-07-18T15:28:00+0530")),
    ("iv2-golden", _r("4083518f22", "2026-07-16T20:51:00+0530")),
    ("asof-baseline", _r("5f626dd933", "2026-08-04T13:19:00+0530")),
    ("baseline_retrieval", _r("8971de0f44", "2026-07-31T02:19:00+0530")),
    ("ft-golden", _r("4083518f22", "2026-07-16T11:41:00+0530")),
]


def test_epochs_numbered_by_earliest_observation():
    assert assign_epochs(RUNS) == {
        "4083518f": "E1",
        "913e762c": "E2",
        "8971de0f": "E3",
        "5f626dd9": "E4",
    }


def test_assignment_is_order_independent():
    assert assign_epochs(RUNS) == assign_epochs(list(reversed(RUNS)))


def test_runs_without_corpus_sha_are_ignored():
    runs = RUNS + [("pool-sweep", {"metadata": {}})]
    assert assign_epochs(runs) == assign_epochs(RUNS)


def test_registry_round_trips(tmp_path):
    path = tmp_path / "epochs.jsonl"
    path.write_text(
        json.dumps({"epoch": "E4", "corpus_sha256": "5f626dd933", "status": "open"}) + "\n",
        encoding="utf-8",
    )
    assert load_epoch_registry(path) == {"5f626dd9": "E4"}


def test_missing_registry_is_empty(tmp_path):
    assert load_epoch_registry(tmp_path / "absent.jsonl") == {}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_backfill_epochs.py -v`
Expected: FAIL — `ImportError: cannot import name 'assign_epochs'`

- [ ] **Step 3: Write minimal implementation**

Append to `src/sebi_rag/autoresearch/epoch.py`:

```python
import json
from pathlib import Path

EPOCH_REGISTRY = "eval/epochs/epochs.jsonl"


def assign_epochs(runs: list[tuple[str, dict]]) -> dict[str, str]:
    """Number corpora E1..En by earliest observed run timestamp.

    Deterministic and order-independent, so re-running the backfill never
    renumbers an existing epoch.
    """
    first_seen: dict[str, str] = {}
    for _name, results in runs:
        meta = results.get("metadata") or {}
        corpus = meta.get("corpus_sha256")
        ts = meta.get("ts")
        if not corpus or not ts:
            continue
        key = corpus[:8]
        if key not in first_seen or ts < first_seen[key]:
            first_seen[key] = ts
    ordered = sorted(first_seen.items(), key=lambda kv: (kv[1], kv[0]))
    return {corpus: f"E{i}" for i, (corpus, _ts) in enumerate(ordered, start=1)}


def load_epoch_registry(path: str | Path) -> dict[str, str]:
    """Read `eval/epochs/epochs.jsonl` into `{corpus_sha256[:8]: epoch}`."""
    p = Path(path)
    if not p.exists():
        return {}
    out: dict[str, str] = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        out[rec["corpus_sha256"][:8]] = rec["epoch"]
    return out
```

```python
# scripts/autoresearch/backfill_epochs.py
"""Assign epochs to the archived runs and write the epoch registry.

Every run's results.json already pins corpus_sha256 and golden_sha256, so the
archive can be retro-labelled rather than discarded. Runs without those fields
are recorded with epoch null and excluded from all comparisons.

    .venv/bin/python scripts/autoresearch/backfill_epochs.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.autoresearch.epoch import assign_epochs, frame_of  # noqa: E402

RUNS_DIR = ROOT / "eval" / "runs"
REGISTRY = ROOT / "eval" / "epochs" / "epochs.jsonl"


def load_runs(runs_dir: Path) -> list[tuple[str, dict]]:
    runs = []
    for run_dir in sorted(p for p in runs_dir.iterdir() if p.is_dir()):
        results = run_dir / "results.json"
        if not results.exists():
            runs.append((run_dir.name, {}))
            continue
        runs.append((run_dir.name, json.loads(results.read_text(encoding="utf-8"))))
    return runs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs-dir", type=Path, default=RUNS_DIR)
    ap.add_argument("--registry", type=Path, default=REGISTRY)
    args = ap.parse_args()

    runs = load_runs(args.runs_dir)
    epochs = assign_epochs(runs)

    members: dict[str, list[str]] = {e: [] for e in epochs.values()}
    unframed: list[str] = []
    for name, results in runs:
        frame = frame_of(results, epochs)
        if frame is None:
            unframed.append(name)
        else:
            members[frame.epoch].append(name)

    first_ts: dict[str, str] = {}
    full_sha: dict[str, str] = {}
    for _name, results in runs:
        meta = results.get("metadata") or {}
        corpus, ts = meta.get("corpus_sha256"), meta.get("ts")
        if not corpus or not ts:
            continue
        key = corpus[:8]
        full_sha[key] = corpus
        if key not in first_ts or ts < first_ts[key]:
            first_ts[key] = ts

    args.registry.parent.mkdir(parents=True, exist_ok=True)
    with args.registry.open("w", encoding="utf-8") as f:
        for corpus, epoch in sorted(epochs.items(), key=lambda kv: kv[1]):
            f.write(
                json.dumps(
                    {
                        "epoch": epoch,
                        "corpus_sha256": full_sha[corpus],
                        "first_seen": first_ts[corpus],
                        "runs": sorted(members[epoch]),
                        "status": "open",
                    }
                )
                + "\n"
            )

    for epoch in sorted(set(epochs.values())):
        print(f"{epoch}: {len(members[epoch])} runs")
    print(f"unframed (excluded from comparisons): {len(unframed)} {sorted(unframed)}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_backfill_epochs.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Backfill the real archive**

Run: `.venv/bin/python scripts/autoresearch/backfill_epochs.py`
Expected: four epochs, matching Spec A §6.3 —
```
E1: 4 runs      (ft-golden, ft-probes, iv2-golden, iv2-probes)
E2: 20 runs
E3: 1 runs      (baseline_retrieval)
E4: 1 runs      (asof-baseline)
unframed (excluded from comparisons): 5 [...]
```

If the counts differ from 4 / 20 / 1 / 1, stop and report — the spec's epoch table was derived from these exact fingerprints.

- [ ] **Step 6: Commit**

```bash
git add src/sebi_rag/autoresearch/epoch.py scripts/autoresearch/backfill_epochs.py \
        tests/test_backfill_epochs.py eval/epochs/epochs.jsonl
git commit -m "feat(autoresearch): backfill epochs E1-E4 onto the run archive"
```

---

### Task 8: Frame guard in `rescore_runs.py`

**Files:**
- Modify: `scripts/rescore_runs.py`
- Test: `tests/test_rescore.py`

**Interfaces:**
- Consumes: `Frame`, `frame_of`, `assert_comparable`, `load_epoch_registry` (Tasks 6–7).
- Produces: no new public symbols; `score_run` returns a `frame` key, and paired comparison raises `IncomparableFramesError` on cross-frame pairs.

`rescore_runs.py` already documents comparability as a *flag* ("a pair whose corpus or index fingerprint differs by more than the intended treatment is flagged"). This upgrades it to a hard refusal, and regenerates `reports/ci_rescore.md` grouped by frame so the report never sits in a state its own generator cannot reproduce.

Every declared pair in `PAIRS` sits within one frame — control and treatment always shared a corpus — so the guard should not break any existing comparison. What it removes is the *implicit cross-intervention ranking* the summary table invites.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_rescore.py
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from sebi_rag.autoresearch.epoch import Frame, IncomparableFramesError


class TestFrameGuard:
    def test_cross_epoch_pair_raises(self):
        from rescore_runs import guard_pair

        with pytest.raises(IncomparableFramesError, match="different corpora"):
            guard_pair(
                Frame(epoch="E1", eval_set="f01d8779"),
                Frame(epoch="E2", eval_set="f01d8779"),
                "ft",
                "iv8",
            )

    def test_cross_eval_set_pair_raises(self):
        from rescore_runs import guard_pair

        with pytest.raises(IncomparableFramesError, match="different golden files"):
            guard_pair(
                Frame(epoch="E2", eval_set="f01d8779"),
                Frame(epoch="E2", eval_set="99a9da66"),
                "iv7-golden",
                "iv7-probes",
            )

    def test_same_frame_pair_passes(self):
        from rescore_runs import guard_pair

        f = Frame(epoch="E2", eval_set="f01d8779")
        guard_pair(f, f, "iv7", "iv8")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_rescore.py -v -k FrameGuard`
Expected: FAIL — `ImportError: cannot import name 'guard_pair' from 'rescore_runs'`

- [ ] **Step 3: Write minimal implementation**

Add to the import block of `scripts/rescore_runs.py`, after the existing `from sebi_rag.stats import ...` line:

```python
from sebi_rag.autoresearch.epoch import (  # noqa: E402
    Frame,
    assert_comparable,
    frame_of,
    load_epoch_registry,
)

EPOCHS = load_epoch_registry(ROOT / "eval" / "epochs" / "epochs.jsonl")


def guard_pair(a: Frame | None, b: Frame | None, label_a: str, label_b: str) -> None:
    """Refuse any paired comparison that spans two frames.

    The archive covers four corpora and three eval sets. Each declared A/B pair
    is internally clean, but nothing previously stopped a cross-frame pair from
    being reported as a number.
    """
    assert_comparable(a, b, label_a=label_a, label_b=label_b)
```

In `score_run` (`scripts/rescore_runs.py:51`), `meta` is already extracted from `results.json`. Add two keys to the returned dict, next to the existing `"golden_sha256": meta.get("golden_sha256", ""),` line — a JSON-safe string and the `Frame` object:

```python
        "frame": (lambda f: str(f) if f else None)(frame_of({"metadata": meta}, EPOCHS)),
        "_frame": frame_of({"metadata": meta}, EPOCHS),
```

`Frame` is a frozen dataclass and is not JSON-serializable, so the report writer must drop it. Change the runs projection in `main` from excluding only `_scores` to excluding every private key:

```python
            "runs": [{k: v for k, v in r.items() if not k.startswith("_")}
                     for r in scored.values()],
```

In `main`, guard each pair immediately after the existing `if not (a and b): continue`:

```python
        for control, treatment, label in PAIRS:
            a, b = scored.get(control), scored.get(treatment)
            if not (a and b):
                continue
            guard_pair(a["_frame"], b["_frame"], control, treatment)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_rescore.py -v`
Expected: PASS — the three new tests plus all pre-existing `TestReadTrecRun` tests

- [ ] **Step 5: Add a frame column and the not-comparable appendix**

In the per-run table in `main`, add a `frame` column. Replace the two header lines:

```python
        lines += [f"## {suite}", "",
                  "| run | frame | n | recall@10 | 95% CI | replay == archive |",
                  "|---|---|---|---|---|---|"]
```

and the row emitter:

```python
            lines.append(
                f"| {r['run']} | {r['frame'] or '—'} | {r['n']} | "
                f"{_fmt(r['recall_at_10'])} | "
                f"{_fmt(r['ci_lo'])}–{_fmt(r['ci_hi'])} | {match} |"
            )
```

Then append the appendix to `lines`, immediately before the existing `## Reading this table` block:

```python
    lines += [
        "## Appendix — cross-frame figures are NOT COMPARABLE",
        "",
        "A *frame* is the pair (corpus snapshot, eval set); two runs are "
        "comparable only within one frame. This archive spans four corpora "
        "(E1–E4) and three eval sets. Every A/B pair above is internally "
        "valid — control and treatment always shared a frame — but runs from "
        "different frames cannot be ranked against one another, and no "
        "intervention here was measured on the current corpus (`5f626dd9`) "
        "or on golden_v7. `rescore_runs.py` now raises rather than emitting a "
        "cross-frame comparison.",
        "",
    ]
```

Run: `make rescore`
Expected: exits 0; `reports/ci_rescore.{md,json}` regenerated; every run row carries a frame such as `E2/f01d8779`; the appendix is present. A non-zero exit with `IncomparableFramesError` means a declared pair genuinely spans frames — report it rather than relaxing the guard.

- [ ] **Step 6: Commit**

```bash
git add scripts/rescore_runs.py tests/test_rescore.py reports/ci_rescore.md reports/ci_rescore.json
git commit -m "feat(rescore): refuse cross-frame comparison, regroup report by frame"
```

---

### Task 9: `ir_measures` parity test

**Files:**
- Modify: `pyproject.toml:24-32`
- Create: `tests/test_trec_parity.py`
- Modify: `Makefile`

**Interfaces:**
- Consumes: `write_run_doc` (Task 2), `write_trec_qrels` (Task 3), `eval.recall_at_k` / `eval.mrr` / `eval.ndcg_at_k` (existing, `src/sebi_rag/eval.py:11,18,25`).
- Produces: no new symbols; a `[project.optional-dependencies] eval` extra and a `make trec-parity` target.

`ir_measures` and `pytrec_eval` are absent from `.venv` (`scipy` 1.18.0, `numpy` 2.5.1 and `ir_datasets` 0.6.1 are present). `pytrec_eval` is a C extension, so it is an optional extra: `make test` stays green at ≥667 whether or not it is installed.

Per Spec A §5, if a metric disagrees the **internal implementation is what changes** — the standard defines the term.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_trec_parity.py
"""Prove the internal retrieval metrics are the standard ones.

Skips unless the optional `eval` extra is installed:
    uv pip install -e '.[eval]'    # or: make trec-parity
"""
import pytest

ir_measures = pytest.importorskip(
    "ir_measures",
    reason="optional [eval] extra not installed; run `make trec-parity`",
)

from sebi_rag.autoresearch.trecio import write_run_doc, write_trec_qrels  # noqa: E402
from sebi_rag.eval import mrr, ndcg_at_k, recall_at_k  # noqa: E402

GOLDEN = [
    {"id": "q1", "abstain": False, "relevant_circulars": ["SEBI/A/2023/1", "SEBI/D/2023/4"]},
    {"id": "q2", "abstain": False, "relevant_circulars": ["SEBI/C/2023/3"]},
    {"id": "q3", "abstain": True, "relevant_circulars": []},
]

RANKINGS = {
    "q1": [
        ("SEBI/B/2023/2#h#0", 0.90),
        ("SEBI/A/2023/1#h#1", 0.80),
        ("SEBI/E/2023/5#h#2", 0.70),
    ],
    "q2": [
        ("SEBI/C/2023/3#h#0", 0.95),
        ("SEBI/B/2023/2#h#1", 0.60),
    ],
}


@pytest.fixture
def artifacts(tmp_path):
    run = tmp_path / "run.doc.trec"
    qrels = tmp_path / "test.qrels"
    write_run_doc(run, "parity", RANKINGS)
    write_trec_qrels(qrels, GOLDEN)
    return qrels, run


def _standard(qrels, run, measure_str):
    measure = ir_measures.parse_measure(measure_str)
    return ir_measures.calc_aggregate(
        [measure],
        ir_measures.read_trec_qrels(str(qrels)),
        ir_measures.read_trec_run(str(run)),
    )[measure]


def _internal(fn):
    vals = []
    for row in GOLDEN:
        if row["abstain"]:
            continue
        ranked = [c.split("#", 1)[0] for c, _ in RANKINGS[row["id"]]]
        seen, docs = set(), []
        for d in ranked:
            if d not in seen:
                seen.add(d)
                docs.append(d)
        vals.append(fn(docs, set(row["relevant_circulars"])))
    return sum(vals) / len(vals)


def test_recall_at_10_matches_ir_measures(artifacts):
    qrels, run = artifacts
    assert _internal(lambda d, r: recall_at_k(d, r, 10)) == pytest.approx(
        _standard(qrels, run, "R@10"), abs=1e-9
    )


def test_mrr_matches_ir_measures(artifacts):
    qrels, run = artifacts
    assert _internal(mrr) == pytest.approx(_standard(qrels, run, "RR"), abs=1e-9)


def test_ndcg_at_10_matches_ir_measures(artifacts):
    qrels, run = artifacts
    assert _internal(lambda d, r: ndcg_at_k(d, r, 10)) == pytest.approx(
        _standard(qrels, run, "nDCG@10"), abs=1e-9
    )
```

- [ ] **Step 2: Run test to verify it skips cleanly**

Run: `.venv/bin/python -m pytest tests/test_trec_parity.py -v`
Expected: 3 SKIPPED with reason "optional [eval] extra not installed". `make test` must stay green.

- [ ] **Step 3: Add the optional extra and Makefile target**

In `pyproject.toml`, after the `dev` extra at line 25:

```toml
# Standard IR scoring, used only to prove metric parity. pytrec_eval is a C
# extension, so this stays optional and the parity test skips without it.
eval = ["ir_measures>=0.3.7"]
```

In `Makefile`, add to `.PHONY` and define:

```makefile
trec-parity:
	uv pip install -e '.[eval]'
	$(ENV) $(PY) -m pytest tests/test_trec_parity.py -v
```

- [ ] **Step 4: Run the parity test for real**

Run: `make trec-parity`
Expected: PASS (3 tests).

**If any assertion fails, STOP and report the exact numbers.** Per Spec A §5 the internal implementation is what changes — but that is a finding to surface, not a silent edit. Most likely divergence is `ndcg_at_k`'s ideal-DCG or log base.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml Makefile tests/test_trec_parity.py
git commit -m "test: prove internal recall/mrr/ndcg match ir_measures"
```

---

### Task 10: Label provenance audit (read-only)

**Files:**
- Create: `scripts/autoresearch/audit_label_provenance.py`
- Create: `reports/label_provenance_audit.md` (generated)
- Test: `tests/test_label_provenance_audit.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `audit(golden_rows: list[dict], artifacts: dict[str, set[str]]) -> dict` returning `{"by_source": {...}, "coverage": {...}, "unaccounted": [...]}`.

`golden_v7.jsonl` already carries `label_source` on all 260 rows, but as free-text prose with 14 distinct values; `review_status` is `adjudicated` for all 260 and carries no information. This task reports what the annotation artifacts can actually account for **before** any classification rule is written. It writes no changes to the golden file.

The 30 human labels from the `packet_human/` ingest do not surface as a distinct `label_source` value — locating them is the audit's main question.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_label_provenance_audit.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from autoresearch.audit_label_provenance import audit

ROWS = [
    {"id": "a", "label_source": "claude (draft adjudication)"},
    {"id": "b", "label_source": "claude (draft adjudication)"},
    {"id": "c", "label_source": "corrected: actually SEBI SAST topic"},
    {"id": "d", "label_source": "v7-draft-2026-07"},
]
ARTIFACTS = {
    "votes.jsonl": {"a", "b"},
    "packet_human": {"c"},
    "arbitration_queue.jsonl": set(),
}


def test_counts_rows_per_label_source():
    result = audit(ROWS, ARTIFACTS)
    assert result["by_source"]["claude (draft adjudication)"] == 2
    assert result["by_source"]["v7-draft-2026-07"] == 1


def test_reports_artifact_coverage_per_source():
    result = audit(ROWS, ARTIFACTS)
    assert result["coverage"]["claude (draft adjudication)"]["votes.jsonl"] == 2
    assert result["coverage"]["corrected: actually SEBI SAST topic"]["packet_human"] == 1


def test_lists_rows_no_artifact_accounts_for():
    result = audit(ROWS, ARTIFACTS)
    assert result["unaccounted"] == ["d"]


def test_empty_artifact_sets_do_not_crash():
    result = audit(ROWS, {"arbitration_queue.jsonl": set()})
    assert sorted(result["unaccounted"]) == ["a", "b", "c", "d"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_label_provenance_audit.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'autoresearch.audit_label_provenance'`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/autoresearch/audit_label_provenance.py
"""Report what the annotation artifacts can account for, before classifying.

golden_v7 already carries `label_source`, but as 14 free-text prose values, and
`review_status` is `adjudicated` for all 260 rows. This is read-only: it writes
a report, never the golden file. Classification rules (Task 11) are written
against these findings rather than assumed.

    .venv/bin/python scripts/autoresearch/audit_label_provenance.py
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "eval" / "golden" / "golden_v7.jsonl"
ANNOT = ROOT / "eval" / "golden" / "v7_annotations"
REPORT = ROOT / "reports" / "label_provenance_audit.md"


def audit(golden_rows: list[dict], artifacts: dict[str, set[str]]) -> dict:
    """Cross-tabulate label_source against which artifacts mention each row."""
    by_source: collections.Counter[str] = collections.Counter()
    coverage: dict[str, collections.Counter[str]] = {}
    unaccounted: list[str] = []

    for row in golden_rows:
        source = row.get("label_source") or "(missing)"
        by_source[source] += 1
        cov = coverage.setdefault(source, collections.Counter())
        hit = False
        for name, ids in artifacts.items():
            if row["id"] in ids:
                cov[name] += 1
                hit = True
        if not hit:
            unaccounted.append(row["id"])

    return {
        "by_source": dict(by_source),
        "coverage": {k: dict(v) for k, v in coverage.items()},
        "unaccounted": unaccounted,
    }


def _ids_from_jsonl(path: Path, key: str = "id") -> set[str]:
    if not path.exists():
        return set()
    out = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        val = rec.get(key) or rec.get("row_id") or rec.get("qid")
        if val:
            out.add(val)
    return out


def _ids_from_dir(path: Path) -> set[str]:
    if not path.exists():
        return set()
    out = set()
    for p in path.rglob("*"):
        if p.is_file():
            out.add(p.stem)
    return out


def collect_artifacts(annot: Path) -> dict[str, set[str]]:
    return {
        "votes.jsonl": _ids_from_jsonl(annot / "votes.jsonl"),
        "arbitration_queue.jsonl": _ids_from_jsonl(annot / "arbitration_queue.jsonl"),
        "packet_human": _ids_from_dir(annot / "packet_human"),
        "gemini": _ids_from_dir(annot / "gemini"),
        "qwen": _ids_from_dir(annot / "qwen"),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--golden", type=Path, default=GOLDEN)
    ap.add_argument("--annotations", type=Path, default=ANNOT)
    ap.add_argument("--out", type=Path, default=REPORT)
    args = ap.parse_args()

    rows = [
        json.loads(line)
        for line in args.golden.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    artifacts = collect_artifacts(args.annotations)
    result = audit(rows, artifacts)

    lines = [
        "# Label provenance audit",
        "",
        f"Rows: {len(rows)}. Artifacts scanned: "
        + ", ".join(f"{k} ({len(v)} ids)" for k, v in artifacts.items()),
        "",
        "| label_source | n | accounted by |",
        "|---|---|---|",
    ]
    for source, n in sorted(result["by_source"].items(), key=lambda kv: -kv[1]):
        cov = result["coverage"].get(source, {})
        detail = ", ".join(f"{k}={v}" for k, v in sorted(cov.items())) or "—"
        lines.append(f"| `{source}` | {n} | {detail} |")
    lines += [
        "",
        f"**Unaccounted rows: {len(result['unaccounted'])}**",
        "",
        "```",
        json.dumps(result["unaccounted"][:40], indent=1),
        "```",
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:12]))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_label_provenance_audit.py -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Run the audit on the real golden set**

Run: `.venv/bin/python scripts/autoresearch/audit_label_provenance.py`
Expected: `reports/label_provenance_audit.md` written, with a row per `label_source` value.

Read the report before starting Task 11. Specifically answer: **which rows, if any, `packet_human` accounts for.** Task 11's mapping table depends on it.

- [ ] **Step 6: Commit**

```bash
git add scripts/autoresearch/audit_label_provenance.py \
        tests/test_label_provenance_audit.py reports/label_provenance_audit.md
git commit -m "feat(autoresearch): audit golden_v7 label provenance"
```

---

### Task 11: `label_tier` controlled vocabulary and tiered reporting

**Files:**
- Create: `scripts/autoresearch/normalize_label_tier.py`
- Modify: `eval/golden/golden_v7.jsonl`
- Modify: `scripts/golden_v7/agreement.py`
- Test: `tests/test_label_tier.py`

**Interfaces:**
- Consumes: `reports/label_provenance_audit.md` (Task 10, read by a human before writing the mapping).
- Produces: `classify_tier(label_source: str) -> str` returning one of `human`, `arbitrated`, `model_single`, `inherited_v5`, `draft_seeded`, `unknown`.

A **new** field `label_tier` is added; free-text `label_source` is preserved unchanged as the provenance trail. `golden_v7.jsonl` is the eval set, not `CircularMeta` — no index impact.

Reporting rule (Spec A §8.4): **tiered reporting with no designated primary set.** The human tier is n≈9; promoting it to primary would reintroduce the exact powerlessness this programme exists to remove.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_label_tier.py
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from autoresearch.normalize_label_tier import TIERS, classify_tier

GOLDEN = Path(__file__).resolve().parents[1] / "eval" / "golden" / "golden_v7.jsonl"


def test_human_corrections_are_human():
    assert classify_tier("corrected: actually SEBI SAST topic") == "human"
    assert classify_tier("corrected: actually SEBI topic") == "human"


def test_arbitration_resolved_is_arbitrated():
    assert classify_tier("claude (arbitration resolved: title_direct)") == "arbitrated"
    assert classify_tier("claude (qwen failed to find governing)") == "arbitrated"


def test_single_claude_pass_is_model_single():
    assert classify_tier("claude (draft adjudication)") == "model_single"
    assert classify_tier("claude (abstain validation)") == "model_single"


def test_v5_inheritance_is_flagged():
    assert classify_tier("golden_v5") == "inherited_v5"
    assert classify_tier("golden_v5 (promoted golden_v5)") == "inherited_v5"


def test_seeded_draft_is_draft_seeded():
    assert classify_tier("v7-draft-2026-07") == "draft_seeded"


def test_unrecognised_value_is_unknown_not_an_error():
    assert classify_tier("something nobody wrote down") == "unknown"


def test_every_tier_is_in_the_vocabulary():
    for src in [
        "corrected: actually SEBI SAST topic",
        "claude (arbitration resolved: title_direct)",
        "claude (draft adjudication)",
        "golden_v5",
        "v7-draft-2026-07",
        "mystery",
    ]:
        assert classify_tier(src) in TIERS


def test_every_golden_row_carries_a_valid_tier():
    rows = [
        json.loads(line)
        for line in GOLDEN.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(rows) == 260
    for row in rows:
        assert row["label_tier"] in TIERS
        assert row["label_source"], "free-text provenance must be preserved"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_label_tier.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'autoresearch.normalize_label_tier'`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/autoresearch/normalize_label_tier.py
"""Add a controlled-vocabulary `label_tier` alongside free-text `label_source`.

golden_v7 carries label_source as 14 distinct prose values. This maps them to a
fixed vocabulary so metrics can be reported per tier, and leaves label_source
untouched as the provenance trail.

Reporting rule (spec A 8.4): tiered reporting with NO designated primary set.
The human tier is ~9 rows; promoting it to primary would have no power.

    .venv/bin/python scripts/autoresearch/normalize_label_tier.py --write
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "eval" / "golden" / "golden_v7.jsonl"

TIERS = ("human", "arbitrated", "model_single", "inherited_v5", "draft_seeded", "unknown")


def classify_tier(label_source: str) -> str:
    """Map a free-text label_source to the controlled vocabulary.

    Order matters: 'corrected:' and 'external-flip' are human acts and win over
    any model prefix; arbitration outranks a plain single-model pass.
    """
    s = (label_source or "").strip().lower()
    if s.startswith("corrected:") or s == "external-flip":
        return "human"
    if "arbitration resolved" in s or "qwen failed to find governing" in s:
        return "arbitrated"
    if s.startswith("golden_v5"):
        return "inherited_v5"
    if s.startswith("v7-draft"):
        return "draft_seeded"
    if s.startswith("claude"):
        return "model_single"
    return "unknown"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--golden", type=Path, default=GOLDEN)
    ap.add_argument("--write", action="store_true", help="write the file in place")
    args = ap.parse_args()

    lines = [
        line
        for line in args.golden.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    rows = [json.loads(line) for line in lines]
    counts: collections.Counter[str] = collections.Counter()
    for row in rows:
        row["label_tier"] = classify_tier(row.get("label_source", ""))
        counts[row["label_tier"]] += 1

    total = len(rows)
    print(f"rows: {total}")
    for tier in TIERS:
        n = counts.get(tier, 0)
        print(f"  {tier:<14} {n:>4}  ({100 * n / total:.1f}%)")

    if args.write:
        args.golden.write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
            encoding="utf-8",
        )
        print(f"\nwrote {args.golden}")
    else:
        print("\ndry run; pass --write to apply")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Dry-run, then apply**

Run: `.venv/bin/python scripts/autoresearch/normalize_label_tier.py`
Expected: tier counts printed, roughly `human 9`, `arbitrated 15`, `model_single 121`, `inherited_v5 33`, `draft_seeded 82`, `unknown 0`.

**If `unknown` is non-zero, stop** and add the missing values to `classify_tier` before writing — an unclassified row is a mapping gap, not a valid tier.

Then run: `.venv/bin/python scripts/autoresearch/normalize_label_tier.py --write`

- [ ] **Step 5: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_label_tier.py -v`
Expected: PASS (8 tests)

- [ ] **Step 6: Add `--by-tier` to `agreement.py`**

⚠️ `agreement.py::main` **rewrites `eval/golden/golden_v7.jsonl`** via `write_jsonl(DEFAULT_GOLDEN_PATH, updated_rows)` unless `report_only` is set. `--by-tier` must therefore never reach that path, or it could drop the `label_tier` field just added.

Add a read-only branch that returns before any promotion logic. In `scripts/golden_v7/agreement.py`, add `_tier_kappas` next to `_stratum_kappas` (`:328`) — identical except it groups on `label_tier` instead of `task_type`:

```python
def _tier_kappas(rows_by_id: dict, votes_by_row: dict, external_ids: list,
                 pools_by_id: dict | None = None) -> list:
    """As `_stratum_kappas`, grouped by label provenance tier rather than
    task_type. Reports agreement per tier so no tier is silently pooled into
    a headline figure it does not support."""
    llm = _llm_annotator(
        {a for rid in external_ids for a in votes_by_row.get(rid, {})})
    pairs = ([("claude", llm), ("claude", "human"), (llm, "human")]
             if llm else [("claude", "human")])
    by_tier_pair: dict = defaultdict(lambda: defaultdict(list))
    for rid in external_ids:
        row = rows_by_id.get(rid)
        if row is None:
            continue
        tier = row.get("label_tier", "unknown")
        pool = pools_by_id.get(rid) if pools_by_id else None
        row_votes = votes_by_row.get(rid, {})
        claude = row_votes.get("claude", [])
        available = {"claude": claude,
                     **{k: v for k, v in row_votes.items() if k != "claude"}}
        for a, b in pairs:
            if a in available and b in available:
                by_tier_pair[tier][(a, b)].append(
                    (available[a], available[b], row, pool))

    out = []
    for tier in sorted(by_tier_pair):
        for pair in pairs:
            paired = by_tier_pair[tier].get(pair)
            if not paired:
                continue
            a_list = [p[0] for p in paired]
            b_list = [p[1] for p in paired]
            if len(paired) < 2:
                out.append((tier, pair, len(paired), None, None))
                continue
            out.append((tier, pair, len(paired),
                        cohen_kappa(a_list, b_list), gwet_ac1(a_list, b_list)))
    return out
```

Then add the read-only entry point at the top of `main`, before `decisions` is built:

```python
def main(report_only: bool = False, by_tier: bool = False) -> None:
    rows = load_golden(DEFAULT_GOLDEN_PATH)
    rows_by_id = {r["id"]: r for r in rows}
    votes = [json.loads(line) for line in
             DEFAULT_VOTES_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    votes_by_row = _votes_by_row(votes)
    pools = [json.loads(line) for line in
             DEFAULT_POOLS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    pools_by_id = {p["id"]: p for p in pools}
    sample = json.loads(DEFAULT_SAMPLE_PATH.read_text(encoding="utf-8"))
    external_ids = sample["external"]

    if by_tier:
        # Read-only: never reaches write_jsonl, so label_tier cannot be lost.
        print(f"{'tier':<14}{'pair':<22}{'n':>5}{'kappa':>9}{'AC1':>9}")
        for tier, pair, n, kappa, ac1 in _tier_kappas(
                rows_by_id, votes_by_row, external_ids, pools_by_id):
            k = "n/a" if kappa is None else f"{kappa:.3f}"
            a = "n/a" if ac1 is None else f"{ac1:.3f}"
            print(f"{tier:<14}{pair[0] + '-' + pair[1]:<22}{n:>5}{k:>9}{a:>9}")
        return
```

Wire the flag into the existing `if __name__ == "__main__":` block alongside `--report-only`, passing `by_tier=True`.

Run: `.venv/bin/python scripts/golden_v7/agreement.py --by-tier`
Expected: one line per (tier, annotator-pair) with `n`, κ and AC1; tiers with `n < 2` show `n/a` rather than a spurious coefficient. Coverage is limited to the external sample (`external_ids`), not all 260 rows — state that limit wherever these numbers are published.

- [ ] **Step 7: Verify `label_tier` survives the agreement rewrite**

`agreement.py` without `--report-only` rewrites the golden file. Confirm the new field is preserved:

```bash
.venv/bin/python scripts/golden_v7/agreement.py --report-only
.venv/bin/python -c "
import json
rows=[json.loads(l) for l in open('eval/golden/golden_v7.jsonl') if l.strip()]
print('rows', len(rows), 'with label_tier', sum('label_tier' in r for r in rows))
"
```
Expected: `rows 260 with label_tier 260`.

If the count drops, `apply()` is not preserving unknown keys — fix that before committing, since any later `agreement.py` run would silently erase the tiers.

- [ ] **Step 8: Commit**

```bash
git add scripts/autoresearch/normalize_label_tier.py scripts/golden_v7/agreement.py \
        tests/test_label_tier.py eval/golden/golden_v7.jsonl
git commit -m "feat(golden-v7): add label_tier vocabulary and tiered agreement reporting"
```

---

### Task 12: Establish frame E4 / golden_v7 baseline

**Files:**
- Create: `scripts/autoresearch/emit_qrels.py`
- Create: `eval/qrels/golden_v7.qrels` + `eval/qrels/golden_v7.qrels.meta.json` (generated)
- Create: `eval/runs/E4-baseline-golden/` (generated)
- Modify: `eval/epochs/epochs.jsonl`
- Modify: `Makefile`
- Modify: `docs/status.md`

**Interfaces:**
- Consumes: everything above.
- Produces: a baselined frame, which is Spec B's precondition.

**Scope:** baseline only. The five intervention re-runs (iv2, iv8, iv9, iv10, iv11) are deferred to a follow-up plan — they are long-running measurement jobs with no code deliverable, and iv9/iv11 may need stale sidecars rebuilt.

Note that `golden_v7` changed in Task 11 (`label_tier` added), so its `golden_sha256` is **not** `3e44dfb9…` any more. The baseline must be run *after* Task 11 so the frame is pinned to the final file.

- [ ] **Step 1: Add the qrels Makefile target**

```makefile
qrels:
	$(ENV) $(PY) scripts/autoresearch/emit_qrels.py
```

Create `scripts/autoresearch/emit_qrels.py` as a thin driver:

```python
"""Emit TREC qrels for an eval set, keyed by its golden_sha256.

    .venv/bin/python scripts/autoresearch/emit_qrels.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.autoresearch.trecio import write_trec_qrels  # noqa: E402
from sebi_rag.benchmark import sha256_file  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--golden", type=Path, default=ROOT / "eval/golden/golden_v7.jsonl")
    ap.add_argument("--out-dir", type=Path, default=ROOT / "eval" / "qrels")
    args = ap.parse_args()

    rows = [
        json.loads(line)
        for line in args.golden.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    out = args.out_dir / f"{args.golden.stem}.qrels"
    n = write_trec_qrels(out, rows)
    sha = sha256_file(args.golden)
    n_abstain = sum(1 for r in rows if r.get("abstain"))
    # TREC qrels carries no comment syntax, so the eval-set key lives in a
    # sidecar. Without it a qrels file could silently be applied to a
    # different golden set.
    out.with_suffix(".qrels.meta.json").write_text(
        json.dumps(
            {
                "golden_path": str(args.golden.relative_to(ROOT)),
                "golden_sha256": sha,
                "rows": len(rows),
                "abstain_excluded": n_abstain,
                "qrels_lines": n,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"{out}: {n} lines from {len(rows)} rows ({n_abstain} abstain excluded)")
    print(f"golden_sha256={sha}")


if __name__ == "__main__":
    main()
```

Run: `make qrels`
Expected: `eval/qrels/golden_v7.qrels` written; 41 abstain rows excluded; the printed `golden_sha256` is the post-Task-11 hash. **Record it** — it is the frame's eval-set key.

- [ ] **Step 2: Run the E4 baseline**

⚠️ `make bench-retrieval` runs `scripts/bench_retrieval.py` with no arguments, and its `--golden` default is **`golden_v6.jsonl`** (`scripts/bench_retrieval.py:62`), with `--out` defaulting to `eval/runs/baseline_retrieval` (`:63`). Using the Makefile target would baseline the wrong eval set into the wrong directory. Invoke the script directly with both paths explicit — do **not** change the defaults, since other tooling relies on them:

```bash
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0 PYTHONPATH=src \
.venv/bin/python scripts/bench_retrieval.py \
  --golden eval/golden/golden_v7.jsonl \
  --out eval/runs/E4-baseline-golden
```

This loads real BGE-M3 and cross-encoder weights and reads `data/index/` — expect minutes, not seconds. It reads the index; it must not write to it.

Verify the run landed in frame E4 on the current golden file:

```bash
.venv/bin/python -c "
import json
d=json.load(open('eval/runs/E4-baseline-golden/results.json'))
m=d['metadata']
print('corpus', m['corpus_sha256'][:8], '(expect 5f626dd9)')
print('golden', m['golden_sha256'][:8], '(expect the hash from step 1)')
print('n', d['metrics'].get('n'), '(expect 219)')
print('recall_at_10', d['metrics'].get('recall_at_10'))
"
```
Expected: `corpus 5f626dd9`, `golden` matching step 1, `n 219`.

Confirm the index was not mutated:

```bash
.venv/bin/python -c "
import sys; sys.path.insert(0,'src')
from sebi_rag.benchmark import dir_fingerprint
print(dir_fingerprint('data/index')[:16])
"
```
Compare against `index_fingerprint` in `eval/runs/asof-baseline/results.json` — they must match.

- [ ] **Step 3: Re-backfill the registry**

```bash
.venv/bin/python scripts/autoresearch/backfill_epochs.py
```
Expected: E4 now lists both `asof-baseline` and `E4-baseline-golden`. Epoch numbering must be unchanged (E1–E4), since `assign_epochs` orders by earliest timestamp per corpus.

- [ ] **Step 4: Verify the whole suite still passes**

Run: `make test`
Expected: ≥667 passing, 0 failures.

- [ ] **Step 5: Record the baseline in `docs/status.md`**

Add to the Current Snapshot table, in the existing key-value style with no prose:

```markdown
| **Epochs** | E1 `4083518f` (4 runs), E2 `913e762c` (20), E3 `8971de0f` (1), E4 `5f626dd9` (2, current). Registry `eval/epochs/epochs.jsonl`; `rescore_runs.py` refuses cross-frame pairs |
| **Frame E4/golden_v7** | baseline `eval/runs/E4-baseline-golden`, n=219 answerable, qrels `eval/qrels/golden_v7.qrels`. Interventions iv2/iv8/iv9/iv10/iv11 NOT yet re-run on E4 |
| **Label tiers** | human 9, arbitrated 15, model_single 121, inherited_v5 33, draft_seeded 82 (verify against `reports/label_provenance_audit.md`). Tiered reporting, no primary set |
```

Replace the counts with the actual values produced in Tasks 7 and 11.

- [ ] **Step 6: Commit**

```bash
git add scripts/autoresearch/emit_qrels.py Makefile eval/qrels eval/runs/E4-baseline-golden \
        eval/epochs/epochs.jsonl docs/status.md
git commit -m "feat(eval): establish frame E4/golden_v7 baseline at n=219"
```

---

## Completion checklist

Spec A §12 acceptance, mapped to tasks:

| # | Acceptance criterion | Task |
|---|---|---|
| 1 | Every run dir has the three artifacts or an exclusion reason | 4 |
| 2 | `eval/qrels/` has a qrels file per eval set | 3, 12 |
| 3 | `make trec-parity` passes | 9 |
| 4 | `eval/epochs/epochs.jsonl` lists E1–E4 | 7 |
| 5 | `rescore_runs.py` raises on cross-frame, with a regression test | 8 |
| 6 | Frame E4/golden_v7 baselined, `ci_rescore.md` regrouped | 8, 12 |
| 7 | `label_tier` on every row; `agreement.py --by-tier` | 10, 11 |
| 8 | `make test` ≥667 | 12 |

Deferred to a follow-up plan: the five E4 intervention re-runs (Spec A §7 table rows 2–6).
