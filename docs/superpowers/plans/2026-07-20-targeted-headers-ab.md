# Targeted Contextual Headers with A/B Measurement (iv10) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Determine whether contextual headers help at all by isolating scale as the only variable vs. iv9 — apply the same (reused, deterministic) header content to only 3 failure-adjacent documents instead of 18,125 chunks, and A/B it against the current no-headers index using the run's own control rather than a stale baseline.

**Architecture:** A selection script filters iv9's already-generated headers (pulled from git history, since the working tree no longer has that file after the iv9 revert) down to 3 target documents, plus one freshly generated override for probe-sup-04's out-of-scope chunk, into a new small sidecar. `build_index.py` gets one optional `--context-headers PATH` flag so the same enrichment machinery (`apply_context_headers`/`load_headers`, unchanged) can point at this small sidecar instead of the (now-absent) bulk one. Two full builds are benchmarked (A = current, B = targeted-headers), then A is restored via a directory-copy snapshot rather than a rebuild.

**Tech Stack:** Python 3.12 (uv-managed venv), pytest, mlx-lm (Qwen2.5-7B-Instruct-4bit, already proven working), existing benchmark scripts `scripts/bench_retrieval.py` / `scripts/analysis/extract_misses.py`.

**Spec:** `docs/superpowers/specs/2026-07-20-targeted-headers-ab-design.md` (approved).

## Global Constraints

- Target documents, exactly: `SEBI/HO/DDHS/DDHS-POD2/P/CIR/2025/101` (probe-par-03), `SEBI/HO/CFD/PoD2/CIR/P/0155` (probe-sup-04), `SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/91` (probe-tbl-05, probe-num-05).
- Header content for the shared chunks is reused verbatim from the iv9 sidecar (git commit `d6f323f`) — no regeneration; only probe-sup-04's depth-1 override chunk gets a fresh `HeaderGenerator.load()` call.
- New sidecar path: `data/corpus/context_headers_targeted.jsonl` — never conflated with or written to the iv9 filename.
- `build_index.py`'s new `--context-headers` flag defaults to the current hardcoded path (`data/corpus/context_headers.jsonl`, currently absent) — default invocation behavior is byte-identical to today.
- A must be restored via directory-copy snapshot/restore, not a rebuild, after B's benchmarks — the working index must never be left in a regressed or ambiguous state.
- Never overwrite existing run dirs; new runs go to `eval/runs/iv10-a-probes/`, `eval/runs/iv10-a-golden/`, `eval/runs/iv10-b-probes/`, `eval/runs/iv10-b-golden/`.
- Chunk count 77,859 unchanged in both A and B builds.
- `make test` green after every task (279 currently passing; 282 after Task 1's new tests).
- After modifying source code, run `graphify update .` before committing (project rule).
- All commands run from repo root: `/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG`. Use `uv run python …` or `.venv/bin/python …` — bare `python` lacks the project deps.

---

### Task 1: `scripts/select_targeted_headers.py` (TDD)

**Files:**
- Create: `scripts/select_targeted_headers.py`
- Create: `src/sebi_rag/context_headers.py` — add one pure helper function (see below)
- Test: `tests/test_select_targeted_headers.py` (new file)

**Interfaces:**
- Consumes: `HeaderGenerator` (`describe(subject, governing, chunk_text) -> str`, `HeaderGenerator.load(...) -> HeaderGenerator`) and `Chunk` (`id, doc_id, section, text, meta`) — both already defined in `src/sebi_rag/context_headers.py` / `src/sebi_rag/segment.py`.
- Produces: a pure function `filter_targeted_rows(rows: list[dict], target_docs: set[str]) -> list[dict]` in `src/sebi_rag/context_headers.py` (added by this task), and the script's CLI (no args — the target doc set and sup-04 chunk id are fixed constants per the spec, not configurable). Output file: `data/corpus/context_headers_targeted.jsonl`, rows `{"chunk_id", "header", "model"}` — same shape as the iv9 sidecar.

- [ ] **Step 1: Write the failing test for the pure filter function**

Create `tests/test_select_targeted_headers.py`:

```python
"""Selection of targeted headers (iv10): filter iv9's reused headers down
to 3 failure-adjacent documents, plus one fresh override for probe-sup-04's
out-of-scope chunk. Offline only — generation is an injected callable.
"""
from __future__ import annotations

from sebi_rag.context_headers import HeaderGenerator, filter_targeted_rows


def test_filter_keeps_only_target_doc_rows():
    rows = [
        {"chunk_id": "DOC/A#4.1.1.2. body#3", "header": "h-a", "model": "m"},
        {"chunk_id": "DOC/B#5.1. other#0", "header": "h-b", "model": "m"},
        {"chunk_id": "DOC/A#4.1.1.3. body#4", "header": "h-a2", "model": "m"},
    ]
    out = filter_targeted_rows(rows, {"DOC/A"})
    assert [r["chunk_id"] for r in out] == [
        "DOC/A#4.1.1.2. body#3", "DOC/A#4.1.1.3. body#4",
    ]


def test_filter_with_no_matches_returns_empty():
    rows = [{"chunk_id": "DOC/Z#1#0", "header": "h", "model": "m"}]
    assert filter_targeted_rows(rows, {"DOC/A"}) == []


def test_sup04_override_generated_via_injected_callable():
    calls: list[str] = []

    def fake(prompt: str) -> str:
        calls.append(prompt)
        return "Describes circulars rescinded by serial number on issuance."

    gen = HeaderGenerator(fake)
    header = gen.describe(
        "Master circular for LODR compliance",
        "",
        "4. The circulars issued by SEBI listed at Sl.No. 68-74 in the "
        "Appendix shall stand rescinded with the issuance of this Master "
        "Circular.",
    )
    assert header == "Describes circulars rescinded by serial number on issuance."
    assert len(calls) == 1
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_select_targeted_headers.py -v`
Expected: first two tests FAIL with `ImportError: cannot import name 'filter_targeted_rows'`. The third test PASSES already (it only exercises `HeaderGenerator`, unchanged from iv9).

- [ ] **Step 3: Add `filter_targeted_rows` to `context_headers.py`**

In `src/sebi_rag/context_headers.py`, add after `in_scope`:

```python
def filter_targeted_rows(
    rows: list[dict], target_docs: set[str]
) -> list[dict]:
    """Keep only sidecar rows whose chunk belongs to a target document."""
    return [r for r in rows if r["chunk_id"].split("#")[0] in target_docs]
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest tests/test_select_targeted_headers.py -v`
Expected: 3 PASS.

- [ ] **Step 5: Write the selection script**

Create `scripts/select_targeted_headers.py`:

```python
"""Select + reuse iv9 headers for 3 failure-adjacent documents (iv10).

Pulls the iv9 sidecar from git history (the working tree no longer has it
after the iv9 revert), filters to the target documents, and generates one
fresh override header for probe-sup-04's chunk (excluded by iv9's
depth>=3-or-annex scope since its section id is "4.", depth 1).

    PYTHONPATH=src .venv/bin/python scripts/select_targeted_headers.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.context_headers import (  # noqa: E402
    HeaderGenerator, filter_targeted_rows,
)
from sebi_rag.corpus import load_circulars  # noqa: E402

TARGET_DOCS = {
    "SEBI/HO/DDHS/DDHS-POD2/P/CIR/2025/101",   # probe-par-03
    "SEBI/HO/CFD/PoD2/CIR/P/0155",             # probe-sup-04
    "SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/91",   # probe-tbl-05, probe-num-05
}
SUP04_DOC = "SEBI/HO/CFD/PoD2/CIR/P/0155"
OUT = ROOT / "data" / "corpus" / "context_headers_targeted.jsonl"


def main() -> None:
    iv9_text = subprocess.run(
        ["git", "show", "d6f323f:data/corpus/context_headers.jsonl"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    rows = [json.loads(l) for l in iv9_text.splitlines() if l.strip()]
    kept = filter_targeted_rows(rows, TARGET_DOCS)
    print(f"reused {len(kept)} rows from iv9 for {len(TARGET_DOCS)} docs", flush=True)

    chunks = load_circulars(ROOT / "data" / "corpus" / "circulars.jsonl")
    sup04_chunks = [
        c for c in chunks
        if c.doc_id == SUP04_DOC and c.id.split("#")[1].startswith("4.")
    ]
    if not sup04_chunks:
        raise SystemExit(f"no probe-sup-04 chunk found under {SUP04_DOC}")
    sup04 = sup04_chunks[0]
    body = sup04.text.split("\n", 1)[1] if "\n" in sup04.text else sup04.text
    gen = HeaderGenerator.load()
    header = gen.describe(sup04.meta.get("subject", ""), "", body)
    kept.append({"chunk_id": sup04.id, "header": header,
                 "model": "mlx-community/Qwen2.5-7B-Instruct-4bit"})
    print(f"sup-04 override chunk: {sup04.id}\n  header: {header!r}", flush=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in kept:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(kept)} rows -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Run the script and verify output**

Run: `PYTHONPATH=src HF_HUB_DISABLE_XET=1 .venv/bin/python scripts/select_targeted_headers.py`
Expected: prints `reused <n> rows from iv9 for 3 docs` (n in the tens-to-low-hundreds range), then the sup-04 override chunk id and its generated header (should reference circulars/rescission/serial numbers — not markdown, not empty), then `wrote <n+1> rows -> …/context_headers_targeted.jsonl`.

```bash
wc -l data/corpus/context_headers_targeted.jsonl
python3 -c "
import json
rows = [json.loads(l) for l in open('data/corpus/context_headers_targeted.jsonl')]
docs = sorted({r['chunk_id'].split('#')[0] for r in rows})
print('docs:', docs)
print('empty headers:', sum(1 for r in rows if not r['header'].strip()))
"
```

Expected: `docs` lists exactly the 3 target documents; `empty headers: 0` (or very close — if the sup-04 override came back empty, re-run Step 6, since `HeaderGenerator`'s silent-failure contract means a transient issue yields `""` and the script would silently proceed with a blank header, which the manual sanity check here exists to catch).

- [ ] **Step 7: Full test suite, graph update, commit**

Run: `make test` — expected 282 passed (279 previous + 3 new).

```bash
graphify update .
git add scripts/select_targeted_headers.py src/sebi_rag/context_headers.py \
        tests/test_select_targeted_headers.py \
        data/corpus/context_headers_targeted.jsonl graphify-out
git commit -m "feat: select + reuse iv9 headers for 3 failure-adjacent docs (iv10)"
```

Note: `data/corpus/` is gitignored wholesale (see iv9 commit `d6f323f`'s note); this commit needs `git add -f data/corpus/context_headers_targeted.jsonl` for that one file specifically (same pattern as iv9 — do not force-add anything else in `data/corpus/`).

---

### Task 2: `--context-headers` flag on `build_index.py`

**Files:**
- Modify: `scripts/build_index.py` (add `argparse`, replace the hardcoded sidecar path)

**Interfaces:**
- Consumes: `load_headers(path) -> dict[str, str]` and `apply_context_headers(chunks, headers) -> list[Chunk]` (both unchanged from iv9, `src/sebi_rag/context_headers.py`).
- Produces: `scripts/build_index.py --context-headers PATH` — Task 3's A/B builds invoke this directly.

- [ ] **Step 1: Add argparse and the new flag**

`scripts/build_index.py` currently detects `--full` via a raw `"--full" in sys.argv` check (line 33) rather than `argparse`. Replace the whole flag-handling section. Current (lines 9-33):

```python
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
for k, v in {
    "TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
    "PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_DISABLE_XET": "1",
}.items():
    os.environ.setdefault(k, v)

from sebi_rag.context_headers import apply_context_headers, load_headers  # noqa: E402
from sebi_rag.corpus import load_circulars  # noqa: E402
from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.lineage import build_lineage, load_records  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402

CORPUS = ROOT / "data" / "corpus" / "circulars.jsonl"
INDEX = ROOT / "data" / "index"

FULL = "--full" in sys.argv  # force re-encode of every document

chunks = load_circulars(CORPUS)
# iv9: merge contextual headers (no-op when the sidecar is absent)
chunks = apply_context_headers(
    chunks, load_headers(ROOT / "data" / "corpus" / "context_headers.jsonl")
)
```

Replace with:

```python
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
for k, v in {
    "TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
    "PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_DISABLE_XET": "1",
}.items():
    os.environ.setdefault(k, v)

from sebi_rag.context_headers import apply_context_headers, load_headers  # noqa: E402
from sebi_rag.corpus import load_circulars  # noqa: E402
from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.lineage import build_lineage, load_records  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402

CORPUS = ROOT / "data" / "corpus" / "circulars.jsonl"
INDEX = ROOT / "data" / "index"

ap = argparse.ArgumentParser()
ap.add_argument("--full", action="store_true",
                 help="force re-encode of every document")
ap.add_argument("--context-headers",
                 default=str(ROOT / "data" / "corpus" / "context_headers.jsonl"))
args, _ = ap.parse_known_args()
FULL = args.full

chunks = load_circulars(CORPUS)
# iv9/iv10: merge contextual headers (no-op when the sidecar is absent)
chunks = apply_context_headers(chunks, load_headers(args.context_headers))
```

`parse_known_args` (not `parse_args`) so any other flags historically passed to this script via `make reindex` wrapping keep working without this task needing to enumerate them.

- [ ] **Step 2: Verify default behavior is unchanged**

Run: `PYTHONPATH=src HF_HUB_DISABLE_XET=1 .venv/bin/python scripts/build_index.py --help`
Expected: shows `--full` and `--context-headers` options, no errors.

```bash
make test
```
Expected: 282 passed (no test exercises `build_index.py` directly, so this just re-confirms nothing else broke).

- [ ] **Step 3: Commit**

```bash
git add scripts/build_index.py
git commit -m "feat: --context-headers flag on build_index.py (iv10 A/B support)"
```

---

### Task 3: A/B builds, benchmarks, and A restoration

**Files:**
- Output: `eval/runs/iv10-a-probes/`, `eval/runs/iv10-a-golden/`, `eval/runs/iv10-b-probes/`, `eval/runs/iv10-b-golden/`
- Modify: `data/index/` (rebuilt for B, then restored to A)

**Interfaces:**
- Consumes: Task 1's `data/corpus/context_headers_targeted.jsonl`; Task 2's `scripts/build_index.py --context-headers PATH`; `scripts/bench_retrieval.py --golden <jsonl> --out <dir>`; `scripts/analysis/extract_misses.py --run <trec> --golden <jsonl> --out <jsonl> --source <label>`.
- Produces: the iv10-a and iv10-b run directories Task 4 diffs.

- [ ] **Step 1: Snapshot the current (A) index**

The working index is already in the no-headers (post-iv9-revert) state.

```bash
cp -R data/index "/private/tmp/claude-501/-Users-ianpinto-sebi-circular-sota-rag-SEBI-circular-RAG/f852e1f2-7ea4-40ff-b185-9166f6902277/scratchpad/iv10-index-a-snapshot"
```

Expected: the copy completes; `ls "/private/tmp/claude-501/-Users-ianpinto-sebi-circular-sota-rag-SEBI-circular-RAG/f852e1f2-7ea4-40ff-b185-9166f6902277/scratchpad/iv10-index-a-snapshot"` shows the same files as `data/index/` (`chunks.jsonl`, `dense.faiss`, `embeddings.npy`, `bm25/`, `lineage.json`, `manifest.json`, `meta.json`).

- [ ] **Step 2: Benchmark A**

```bash
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python scripts/bench_retrieval.py \
  --golden eval/probes/probes_v1.jsonl --out eval/runs/iv10-a-probes

HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python scripts/bench_retrieval.py \
  --golden eval/golden/golden_v6.jsonl --out eval/runs/iv10-a-golden

.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv10-a-probes/run.trec --golden eval/probes/probes_v1.jsonl \
  --out eval/runs/iv10-a-probes/failures.jsonl --source probes_v1

.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv10-a-golden/run.trec --golden eval/golden/golden_v6.jsonl \
  --out eval/runs/iv10-a-golden/failures.jsonl --source golden_v6
```

Expected: numbers close to iv7's (this run is on the reverted, iv7-equivalent index) — probes 4 answer-level failures, golden 2, recall@10 ~1.0 / ~0.956. Record the exact numbers; they are A's control values for Task 4's diff, not iv7's.

- [ ] **Step 3: Build B (incremental — only the 3 target docs re-embed)**

```bash
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src .venv/bin/python scripts/build_index.py \
  --context-headers data/corpus/context_headers_targeted.jsonl
```

Expected: `chunks=77859 building index...` then `built in <n>s {'mode': 'incremental', ..., 'chunks_encoded': <small number>}` — the encoded count should reflect only the ~3 target documents' chunks, not the full corpus (a large `chunks_encoded` here means the checksum/manifest logic re-embedded more than expected — stop and debug before benchmarking). Should finish in well under 10 minutes.

- [ ] **Step 4: Benchmark B**

```bash
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python scripts/bench_retrieval.py \
  --golden eval/probes/probes_v1.jsonl --out eval/runs/iv10-b-probes

HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python scripts/bench_retrieval.py \
  --golden eval/golden/golden_v6.jsonl --out eval/runs/iv10-b-golden

.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv10-b-probes/run.trec --golden eval/probes/probes_v1.jsonl \
  --out eval/runs/iv10-b-probes/failures.jsonl --source probes_v1

.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv10-b-golden/run.trec --golden eval/golden/golden_v6.jsonl \
  --out eval/runs/iv10-b-golden/failures.jsonl --source golden_v6
```

- [ ] **Step 5: Restore A from the snapshot**

```bash
rm -rf data/index
cp -R "/private/tmp/claude-501/-Users-ianpinto-sebi-circular-sota-rag-SEBI-circular-RAG/f852e1f2-7ea4-40ff-b185-9166f6902277/scratchpad/iv10-index-a-snapshot" data/index
```

Expected: `data/index/meta.json` shows `{"n": 77859, "dim": 1024}` again (same as before Step 3).

```bash
python3 -c "
import json
for l in open('data/index/chunks.jsonl'):
    c = json.loads(l)
    if 'CIR/2025/101#4.1.1.2' in c['id']:
        assert 'This provision governs' not in c['text'], 'A restore failed: header still present'
        print('A restore verified: no header in 4.1.1.2')
        break
"
```

Expected: prints `A restore verified: no header in 4.1.1.2` — confirms the working index is back to the no-headers control state regardless of B's outcome, per the spec's mandatory restore step.

- [ ] **Step 6: Full test suite against restored A**

Run: `make test`
Expected: 282 passed.

- [ ] **Step 7: Commit the run results**

```bash
git add eval/runs/iv10-a-probes eval/runs/iv10-a-golden \
        eval/runs/iv10-b-probes eval/runs/iv10-b-golden
git commit -m "eval: targeted contextual-header A/B runs (iv10-a, iv10-b)"
```

---

### Task 4: Item-by-item diff, gate verdict, report §5.5

**Files:**
- Modify: `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md` (append §5.5 after §5.4)

**Interfaces:**
- Consumes: `eval/runs/iv10-a-{probes,golden}/failures.jsonl` and `eval/runs/iv10-b-{probes,golden}/failures.jsonl` (Task 3).
- Produces: the report §5.5, the final recorded verdict for this cycle.

- [ ] **Step 1: Compute the item-by-item diff**

```bash
python3 -c "
import json

def load(path):
    return {r['id']: r for r in (json.loads(l) for l in open(path))}

for kind in ('probes', 'golden'):
    a = load(f'eval/runs/iv10-a-{kind}/failures.jsonl')
    b = load(f'eval/runs/iv10-b-{kind}/failures.jsonl')
    a_fail = {k for k, v in a.items() if v['answer_class'] != 'hit'}
    b_fail = {k for k, v in b.items() if v['answer_class'] != 'hit'}
    print(f'== {kind}: A failures={len(a_fail)} B failures={len(b_fail)}')
    print('  resolved (A fail -> B hit):', a_fail - b_fail)
    print('  new regressions (A hit -> B fail):', b_fail - a_fail)
    for k in sorted(a_fail | b_fail):
        av = a.get(k, {})
        bv = b.get(k, {})
        print(f'  {k}: A={av.get(\"answer_class\")}/{av.get(\"first_answer_rank\")}'
              f'  B={bv.get(\"answer_class\")}/{bv.get(\"first_answer_rank\")}')

am = json.load(open('eval/runs/iv10-a-golden/results.json'))['metrics']
bm = json.load(open('eval/runs/iv10-b-golden/results.json'))['metrics']
print(f'golden recall@10: A={am[\"recall_at_10\"]:.4f} B={bm[\"recall_at_10\"]:.4f}')
am = json.load(open('eval/runs/iv10-a-probes/results.json'))['metrics']
bm = json.load(open('eval/runs/iv10-b-probes/results.json'))['metrics']
print(f'probes recall@10: A={am[\"recall_at_10\"]:.4f} B={bm[\"recall_at_10\"]:.4f}')
"
```

Record every line of this output verbatim for the report.

- [ ] **Step 2: Append §5.5 to the report**

Append to `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md`, directly after §5.4 (before `## Self-check vs spec success criteria`):

```markdown
### 5.5 Targeted contextual headers, A/B (iv10, <date>)

Isolates scale as the only variable vs. iv9: same reused 7B header content
(git `d6f323f`), applied to 3 failure-adjacent documents (<n> chunks) +
1 fresh override for probe-sup-04's previously out-of-scope chunk, instead
of the 18,125-chunk bulk pass. A/B against the run's own control (A =
current no-headers index), not a stale baseline. Commits <sha-task1>,
<sha-task2>, <sha-task3>. Spec:
`docs/superpowers/specs/2026-07-20-targeted-headers-ab-design.md`, plan:
`docs/superpowers/plans/2026-07-20-targeted-headers-ab.md`.

| run | answerable | answer-level failures | doc recall@10 |
|---|---|---|---|
| probes A (`iv10-a-probes`) | 25 | <n> | <x> |
| probes B (`iv10-b-probes`) | 25 | <n> | <x> |
| golden A (`iv10-a-golden`) | 45 | <n> | <x> |
| golden B (`iv10-b-golden`) | 45 | <n> | <x> |

Resolved (A fail → B hit): <ids or "none">. New regressions (A hit → B
fail): <ids or "none">. probe-par-03: A=<class>/<rank> → B=<class>/<rank>.
probe-sup-04: A=<class>/<rank> → B=<class>/<rank>.

Gate verdict: <met / not met — did B resolve a target failure without
regressing anything A passed>. <If B still regresses items despite the
100x-smaller scope: this is a stronger, more localized negative signal
than iv9's — the header-injection mechanism itself, not just its scale, is
implicated; recommend abandoning contextual headers as a direction and
pursuing SPLADE (report §4) instead. If B is clean but doesn't resolve the
targets: the mechanism is safe at small scale but insufficient — the
paraphrase-gap residue (probe-par-03, probe-sup-04) needs a different
technique. If B resolves a target cleanly: recommend a graduated scale-up
(e.g. 10x, then 100x) with A/B at each step, never another single bulk
pass.>
```

Fill every `<…>` with measured values; keep only the applicable branch of the verdict sentence.

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md
git commit -m "eval: targeted contextual-header A/B verdict (iv10) + report update"
```

---

## Self-review notes

- Spec coverage: Scope § → Task 1's `TARGET_DOCS` constant (exact match); Header reuse § → Task 1 Steps 1-6 (`filter_targeted_rows` + git-history pull, no regeneration for shared rows); Components §1 → Task 1's script; Components §2 → Task 2 (`--context-headers` flag, default unchanged); A/B mechanism § → Task 3 (two full builds, snapshot/restore via directory copy, not rebuild); Testing § → Task 1's 3 tests; Measurement & gates § → Task 4 (item-by-item diff against A not iv7, chunk-count gate in Task 3 Step 3, `make test` in Task 3 Step 6, report §5.5 with all three verdict branches spelled out).
- Type consistency: `filter_targeted_rows(rows: list[dict], target_docs: set[str]) -> list[dict]` defined in Task 1 Step 3, used identically in Task 1 Step 5's script and Task 1 Step 1's tests; `HeaderGenerator.describe`/`.load` signatures unchanged from iv9, reused as-is in Task 1 Step 5.
- The `data/corpus/` gitignore-exception pattern from iv9 (`git add -f`) is carried forward explicitly in Task 1 Step 7 so the new sidecar doesn't silently fail to commit.
- Task 3's restore step includes an executable verification (Step 5's chunk-content check), not just a file-count assertion, directly addressing the operational near-miss (accidental concurrent reindex) that occurred during iv9's execution.
