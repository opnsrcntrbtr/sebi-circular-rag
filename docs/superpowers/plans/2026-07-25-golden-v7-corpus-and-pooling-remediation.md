# Golden v7 Corpus & Pooling Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair 6 text-corrupted and 17 stale-numbered corpus records, add the missing corpus text-integrity guardrail, fix the `assemble_pool` cap-saturation defect, and recover the 25 escalated golden_v7 chunk labels — so golden_v7 is trustworthy before Tasks 9–14 of the expansion plan build a CI gate on it.

**Architecture:** Guardrail first (a validator that would have caught both bug classes), then data repair in strict dependency order (text before renumber — reversed, renumbering collapses 5 records onto one number), then reindex, then the pooling fix and label recovery. Label recovery is deterministic where possible: 18 of 25 escalations map to exactly one Task-5 candidate chunk via their `answer_contains` literal, so they need no re-judgment.

**Tech Stack:** Python 3.12 (`.venv`), pytest offline suite (`-m "not integration"`), existing `scripts/validate_corpus.py` / `scripts/renumber.py` / `sebi_rag.ingest_pdf.ingest`, bge-m3 + bm25s + FAISS for the reindex and re-pool steps.

**Investigation record (evidence this plan is built on):**
- 699/705 corpus records verified byte-identical to their provenance PDF; exactly 6 mismatch (lines 597–602), 0 missing PDFs.
- Corpus-wide sha256 clustering of `text`: exactly 1 duplicate cluster (6 records sharing one text).
- `scripts/validate_corpus.py` reports "705 records, 0 violations" — it has no invariant tying `text` to its record.
- `assemble_pool` step 1 saturated 92/207 pools (44%); 24 of 25 escalations sit in that group.
- `parse_meta` on current code already derives the correct number for all 3 hand-checked mis-numbered records → A2 is stale data, not a live parser bug.

## Global Constraints

- Python is ALWAYS `.venv/bin/python`; tests run as `.venv/bin/python -m pytest -q -m "not integration"` from repo root.
- Real-stack scripts need env: `HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src` (Makefile `$(ENV)` provides them).
- Work happens in the existing worktree `.worktrees/golden-v7` on branch `golden-v7-expansion` for anything touching `eval/golden/`; corpus and `src/` repairs also land on that branch. `data/corpus/` and `data/index/` are gitignored and shared via symlink — repairs mutate the REAL shared corpus, so Task 2 takes a backup first.
- **Ordering is load-bearing:** Task 2 (text repair) MUST precede Task 3 (renumber). Running `renumber.py` on the current corpus renames all 5 wrong-text records to `PoD-1/P/CIR/2024/163`, a 5-way collision.
- Frozen files — never modify: `eval/golden/golden_v1..v6.jsonl`, `eval/probes/probes_v1.jsonl`, `eval/golden/golden_asof_v1.jsonl`.
- Golden spans are `{"doc", "quote"}` and resolve by quote match, so they survive re-chunking; only the `doc` value is affected by renumbering.
- Never "fix" a validator failure by loosening the validator. If a check fires on data believed correct, establish which is wrong first.
- Commits end with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

---

### Task 1: Corpus text-integrity invariants in `validate_corpus.py`

The guardrail that was missing. Must land before any repair so repairs are verified by it.

**Files:**
- Modify: `scripts/validate_corpus.py` (extend `validate()`, add a deep mode to `main()`)
- Test: `tests/test_validate_corpus.py` (create)
- Modify: `Makefile` (append `validate-corpus` target)

**Interfaces:**
- Consumes: `sebi_rag.ingest_pdf.normalize_circular_number`, `parse_meta`, `extract_text`.
- Produces: `validate(records) -> list[str]` gains two cheap invariants (duplicate text, own-number-derivable). New `validate_deep(records, raw_dir) -> list[str]` does the PDF comparison. `main()` gains `--deep`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_validate_corpus.py
"""Corpus integrity invariants (2026-07-25 remediation Task 1).

Guards the two bug classes that shipped undetected: records sharing one
body text, and records whose stored circular_number cannot be derived
from their own text.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_corpus import validate  # noqa: E402

_TEXT_A = (
    "CIRCULAR\nAFD/P/CIR/2022/125\nSeptember 26, 2022\nTo,\n"
    "All Foreign Portfolio Investors\nDear Sir / Madam,\n"
    "Subject: Modification in the Operational Guidelines\n\n"
    "1. This is the body of circular one.\n"
)
_TEXT_B = (
    "CIRCULAR\nDOF3/P/CIR/2022/82\nJune 15, 2022\nTo,\nAll Mutual Funds\n"
    "Dear Sir / Madam,\nSubject: Nomination for Mutual Fund Unit Holders\n\n"
    "1. This is the body of circular two.\n"
)


def _rec(num, text, **over):
    r = {"circular_number": num, "issue_date": "2022-06-15", "text": text,
         "version_lineage": [], "provenance": "Parsed from PDF x.pdf on 2026-07-25"}
    r.update(over)
    return r


def test_clean_corpus_has_no_violations():
    recs = [_rec("AFD/P/CIR/2022/125", _TEXT_A), _rec("DOF3/P/CIR/2022/82", _TEXT_B)]
    assert validate(recs) == []


def test_duplicate_text_across_records_flagged():
    recs = [_rec("AFD/P/CIR/2022/125", _TEXT_A), _rec("DOF3/P/CIR/2022/82", _TEXT_A)]
    issues = validate(recs)
    assert any("duplicate text" in v for v in issues)


def test_number_not_derivable_from_own_text_flagged():
    # stored number belongs to a circular this text merely cites
    recs = [_rec("SEBI/HO/MRD2/DCAP/CIR/P/2019/146", _TEXT_A)]
    issues = validate(recs)
    assert any("not derivable" in v for v in issues)


def test_empty_text_is_not_a_duplicate_cluster():
    recs = [_rec("AFD/P/CIR/2022/125", ""), _rec("DOF3/P/CIR/2022/82", "")]
    assert not any("duplicate text" in v for v in validate(recs))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest -q tests/test_validate_corpus.py`
Expected: FAIL — `test_duplicate_text_across_records_flagged` and `test_number_not_derivable_from_own_text_flagged` fail because `validate()` has no such checks.

- [ ] **Step 3: Implement in `scripts/validate_corpus.py`**

Extend the import line to bring in `parse_meta`, and add these two blocks to `validate()`. Insert the duplicate-text scan after the `for i, r in enumerate(records)` loop ends (it is a cross-record check), and the own-number check inside the loop right after the `key = normalize_circular_number(n)` line:

```python
# --- inside the per-record loop, after `key = normalize_circular_number(n)` ---
        # A record's own number must be derivable from its own text. Catches
        # both the R3 last-resort fallback picking up a CITED number and a
        # record whose text was overwritten with another circular's body.
        derived = parse_meta(r.get("text", "")).get("circular_number", "")
        if derived and normalize_circular_number(derived) != key:
            violations.append(
                f"{where}: circular_number not derivable from own text "
                f"(text yields {derived!r})")
```

```python
# --- after the per-record loop, before `return violations` ---
    # Two records may never share one body text (catches the shared-text
    # backfill bug: metadata written per-record, text from a stale variable).
    by_text: dict[str, str] = {}
    for i, r in enumerate(records):
        t = " ".join((r.get("text") or "").split())
        if not t:
            continue
        n = r.get("circular_number", "") or "<empty>"
        if t in by_text:
            violations.append(
                f"record {i} ({n}): duplicate text — identical body to "
                f"{by_text[t]}")
        else:
            by_text[t] = n
```

Then add the deep (PDF-comparing) mode and wire `--deep` into `main()`:

```python
PROV_RE = re.compile(r"Parsed from PDF (\S+\.pdf)", re.I)


def validate_deep(records: list[dict], raw_dir: Path) -> list[str]:
    """Every record's text must match the PDF its provenance names.

    Slow (re-extracts every PDF) — opt in with --deep after any
    ingest/backfill/repair.
    """
    from sebi_rag.ingest_pdf import extract_text

    violations: list[str] = []
    for i, r in enumerate(records):
        n = r.get("circular_number", "") or "<empty>"
        m = PROV_RE.search(r.get("provenance", ""))
        if not m:
            violations.append(f"record {i} ({n}): provenance names no PDF")
            continue
        pdf = raw_dir / m.group(1)
        if not pdf.exists():
            violations.append(f"record {i} ({n}): provenance PDF missing: {m.group(1)}")
            continue
        try:
            got = " ".join(extract_text(pdf).split())
        except Exception as exc:  # noqa: BLE001
            violations.append(f"record {i} ({n}): PDF extract failed: {exc}")
            continue
        if got != " ".join((r.get("text") or "").split()):
            violations.append(
                f"record {i} ({n}): text does not match provenance PDF {m.group(1)}")
    return violations
```

In `main()`, replace the body with:

```python
def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--deep"]
    deep = "--deep" in sys.argv[1:]
    path = Path(args[0] if args else "data/corpus/circulars.jsonl")
    records = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
               if l.strip()]
    violations = validate(records)
    if deep:
        violations += validate_deep(records, path.parents[1] / "raw")
    for v in violations:
        print(v)
    print(f"{len(records)} records, {len(violations)} violations"
          f"{' (deep)' if deep else ''}")
    return 1 if violations else 0
```

Append to `Makefile`:

```make
validate-corpus:
	$(ENV) $(PY) scripts/validate_corpus.py data/corpus/circulars.jsonl
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest -q tests/test_validate_corpus.py`
Expected: PASS (4 tests)

- [ ] **Step 5: Confirm the validator now catches the real bugs**

Run: `make validate-corpus`
Expected: EXIT 1. The output must include 5 `duplicate text` lines (lines 597–601 against 602) and ~17 `not derivable from own text` lines. **This is the point of the task** — record the exact counts in the task report; they are the baseline Tasks 2–3 must drive to zero.

- [ ] **Step 6: Full offline suite, then commit**

Run: `.venv/bin/python -m pytest -q -m "not integration"`
Expected: no regressions (baseline 490 passing + 4 new = 494).

```bash
git add scripts/validate_corpus.py tests/test_validate_corpus.py Makefile
git commit -m "feat(corpus): text-integrity invariants — duplicate text, own-number derivability, deep PDF match

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: Repair the 6 text-corrupted records from local orphan PDFs

Lines 597–602 share one body text. The correct PDF for each is already on disk in `data/raw/` as an orphan (no record references it) — no network needed.

**Files:**
- Create: `scripts/repair_corpus_text.py`
- Modify: `data/corpus/circulars.jsonl` (gitignored; backed up first)
- Test: `tests/test_repair_corpus_text.py` (create)

**Interfaces:**
- Consumes: `sebi_rag.ingest_pdf.ingest` (signature `ingest(pdf_path, corpus_path, source_url="", replace=False, ocr=False) -> dict`), `normalize_circular_number`.
- Produces: `REPAIRS: dict[str, str]` (circular_number → orphan PDF filename) and `main()`. Task 3 depends on this having run.

**The verified mapping** (each PDF's `parse_meta` already yields the matching number, date and subject):

| corrupted record | correct PDF in `data/raw/` |
|---|---|
| `DOF3/P/CIR/2022/39` | `1648639233807.pdf` |
| `DOF3/P/CIR/2022/49` | `1649673908121.pdf` |
| `DOF3/P/CIR/2022/82` | `1655291815532.pdf` |
| `DOF1/P/CIR/2022/105` | `1659094793301.pdf` |
| `DOF2/P/CIR/2022/161` | `1669373687117.pdf` |
| `PoD-1/P/CIR/2024/163` | `1732618015389.pdf` (text already correct; provenance was wrong) |

- [ ] **Step 1: Back up the corpus (it is gitignored — this is the only undo)**

```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
cp data/corpus/circulars.jsonl "data/corpus/circulars.jsonl.bak-$(date +%Y%m%d-%H%M%S)"
ls -la data/corpus/*.bak-*
```
Expected: a backup file listed. Do not proceed without it.

- [ ] **Step 2: Write the failing test**

```python
# tests/test_repair_corpus_text.py
"""The repair map must name a real orphan PDF that parses to the
circular_number it claims to repair (2026-07-25 remediation Task 2)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
from repair_corpus_text import REPAIRS  # noqa: E402
from sebi_rag.ingest_pdf import normalize_circular_number  # noqa: E402


def test_repair_map_covers_the_six_known_records():
    assert set(REPAIRS) == {
        "DOF3/P/CIR/2022/39", "DOF3/P/CIR/2022/49", "DOF3/P/CIR/2022/82",
        "DOF1/P/CIR/2022/105", "DOF2/P/CIR/2022/161", "PoD-1/P/CIR/2024/163",
    }


def test_every_mapped_pdf_exists_on_disk():
    for num, pdf in REPAIRS.items():
        assert (ROOT / "data" / "raw" / pdf).exists(), f"{num} -> {pdf} missing"


def test_mapped_pdfs_are_distinct():
    assert len(set(REPAIRS.values())) == len(REPAIRS)


def test_numbers_normalize_distinctly():
    keys = {normalize_circular_number(n) for n in REPAIRS}
    assert len(keys) == len(REPAIRS)
```

- [ ] **Step 3: Run test to verify it fails**

Run: `.venv/bin/python -m pytest -q tests/test_repair_corpus_text.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'repair_corpus_text'`

- [ ] **Step 4: Implement `scripts/repair_corpus_text.py`**

```python
"""Repair the 6 records whose body text was overwritten with one shared
circular's text (2026-07-25 remediation Task 2).

Root cause: a batch write assigned `text` and `provenance` from stale
variables while metadata came per-record from elsewhere; `ingest()` cannot
produce this shape. The correct PDFs were left on disk unreferenced.

Idempotent: re-ingests each record from its real PDF with replace=True.
Offline — every PDF is already in data/raw/.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.ingest_pdf import ingest, normalize_circular_number  # noqa: E402

# circular_number -> the orphan PDF in data/raw/ that actually contains it.
# Verified: parse_meta() on each PDF yields this number, its issue_date and
# its subject.
REPAIRS = {
    "DOF3/P/CIR/2022/39": "1648639233807.pdf",
    "DOF3/P/CIR/2022/49": "1649673908121.pdf",
    "DOF3/P/CIR/2022/82": "1655291815532.pdf",
    "DOF1/P/CIR/2022/105": "1659094793301.pdf",
    "DOF2/P/CIR/2022/161": "1669373687117.pdf",
    "PoD-1/P/CIR/2024/163": "1732618015389.pdf",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=str(ROOT / "data/corpus/circulars.jsonl"))
    ap.add_argument("--raw", default=str(ROOT / "data/raw"))
    args = ap.parse_args()
    corpus, raw = Path(args.corpus), Path(args.raw)

    before = {normalize_circular_number(json.loads(l)["circular_number"])
              for l in corpus.read_text(encoding="utf-8").splitlines() if l.strip()}
    for num, pdf in REPAIRS.items():
        if normalize_circular_number(num) not in before:
            print(f"WARNING: {num} not in corpus — skipping", file=sys.stderr)
            continue
        rec = ingest(raw / pdf, corpus, replace=True)
        got = rec.get("circular_number", "")
        status = "OK " if normalize_circular_number(got) == normalize_circular_number(num) else "DRIFT"
        print(f"{status} {num}: re-ingested from {pdf} -> {got} ({rec.get('issue_date')})")
    after = [json.loads(l) for l in corpus.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"corpus now {len(after)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Note: `ingest(..., replace=True)` calls `_rewrite_replacing`, which drops the
existing record and appends the new one — so the 6 repaired records move to the
end of the file and lose the lineage/regulation annotations added by
`annotate_corpus`. Task 5's `make reindex` re-runs `annotate`, which restores
them. Do not hand-copy annotation fields.

- [ ] **Step 5: Run test, then the real repair**

Run: `.venv/bin/python -m pytest -q tests/test_repair_corpus_text.py` → PASS (4 tests)

Run: `HF_HUB_DISABLE_XET=1 PYTHONPATH=src .venv/bin/python scripts/repair_corpus_text.py`
Expected: 6 lines all prefixed `OK `, then `corpus now 705 records`. A `DRIFT` line means the PDF does not parse to the number claimed — STOP and report; do not continue to Task 3.

- [ ] **Step 6: Verify the duplicate-text class is gone**

Run: `make validate-corpus`
Expected: zero `duplicate text` lines remain. The `not derivable from own text` lines still appear (Task 3 fixes those) — confirm the duplicate-text count went from 5 to 0 and report both counts.

- [ ] **Step 7: Commit**

```bash
git add scripts/repair_corpus_text.py tests/test_repair_corpus_text.py
git commit -m "fix(corpus): repair 6 records whose text was overwritten with a shared circular body

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: Adjudicate and apply the 17 stale circular numbers

`parse_meta` on current code already derives the right number for these; they
are stale records from before the parser improved. `scripts/renumber.py` exists
for exactly this. But renumbering is not blind — each change needs a verdict
against the document's own header, because two candidates look wrong.

**Files:**
- Create: `scripts/analysis/renumber_audit.py` (dry-run report; `scripts/analysis/` already exists)
- Modify: `data/corpus/circulars.jsonl` (via `scripts/renumber.py`)
- Modify: `scripts/renumber.py` only if the audit shows a rejected change (see Step 3)

**Interfaces:**
- Consumes: `parse_meta`, `normalize_circular_number`, `sebi_rag.ingest_pdf._header`.
- Produces: an audit table; a corpus whose `validate()` reports zero `not derivable` violations.

- [ ] **Step 1: Write the audit script**

```python
"""Dry-run audit of every circular_number renumber.py would change, with the
document's own header alongside, so each change gets a human verdict before
the corpus is rewritten (2026-07-25 remediation Task 3).

Read-only. Run AFTER Task 2 — on the unrepaired corpus the 5 shared-text
records all resolve to PoD-1/P/CIR/2024/163 (a 5-way collision).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.ingest_pdf import (  # noqa: E402
    _header, normalize_circular_number, parse_meta,
)


def main() -> int:
    corpus = ROOT / "data/corpus/circulars.jsonl"
    recs = [json.loads(l) for l in corpus.read_text(encoding="utf-8").splitlines()
            if l.strip()]
    changes = []
    for i, r in enumerate(recs, 1):
        m = parse_meta(r.get("text", ""))
        new = m.get("circular_number", "")
        old = r.get("circular_number", "")
        if new and new != old:
            changes.append((i, old, new, r.get("issue_date", ""),
                            m.get("issue_date", ""), _header(r.get("text", ""))))
    print(f"{len(changes)} of {len(recs)} records would be renumbered\n")
    for i, old, new, od, nd, head in changes:
        print(f"line {i}")
        print(f"  old: {old}")
        print(f"  new: {new}")
        if od != nd:
            print(f"  issue_date: {od} -> {nd}")
        print(f"  header: {' '.join(head.split())[:160]}")
        print()
    # collision check: the rewrite must keep numbers unique
    final = {}
    for i, r in enumerate(recs, 1):
        m = parse_meta(r.get("text", ""))
        n = m.get("circular_number", "") or r.get("circular_number", "")
        final.setdefault(normalize_circular_number(n), []).append(i)
    dupes = {k: v for k, v in final.items() if len(v) > 1}
    print(f"post-renumber collisions: {len(dupes)}")
    for k, v in dupes.items():
        print(f"  {k}: lines {v}")
    return 1 if dupes else 0
```

- [ ] **Step 2: Run the audit**

Run: `PYTHONPATH=src .venv/bin/python scripts/analysis/renumber_audit.py`
Expected: `post-renumber collisions: 0`. If any collision is reported, STOP and report — Task 2 did not fully land.

- [ ] **Step 3: Give each change a verdict, using the printed header as ground truth**

For every listed change, confirm the `new` number appears in that record's own
`header` line. Two need special handling — both were checked at plan-write time,
and one is already resolved for you:

- **line 397 — needs an OVERRIDE, not the derived value.** The header reads
  `SEBI/ HO/ AFD/ AFD – PoD – 2/ CIR/ P/ 2023/ 148`, so the document's literal
  number is `SEBI/HO/AFD/AFD-PoD-2/CIR/P/2023/148`. `_rejoin_split` turns the
  en-dashes into slashes, so `parse_meta` yields the doubled
  `SEBI/HO/AFD/AFD/PoD/2/CIR/P/2023/148`. **Verified at plan-write time: these
  two spellings do NOT share a normalization key**
  (`ho/afd/afd-pod-2/cir/p/2023/148` vs `ho/afd/afd/pod/2/cir/p/2023/148`), so
  storing the derived spelling would leave every reference to this circular
  unresolvable. Write the canonical spelling via `OVERRIDES` below. Do not
  "fix" `_rejoin_split` — its en-dash healing is load-bearing for other records
  (see its docstring) and changing it risks silent regressions across the corpus;
  note the parser limitation in the task report instead.
- **line 417** → `3/CIR/P/2023/104`. A leading bare `3/` is not a valid SEBI
  prefix. Verify against the printed header; if the header does not contain
  `3/CIR/P/2023/104` as its own number, REJECT via `SKIP_LINES`.

Add both mechanisms to `scripts/renumber.py` rather than editing the corpus by
hand:

```python
# Lines whose re-derived number was rejected on audit (2026-07-25 Task 3).
# Keyed by 1-based corpus line; value is the reason.
SKIP_LINES: dict[int, str] = {}

# Lines where parse_meta's derived spelling is wrong but the correct number is
# known. _rejoin_split converts the en-dashes in "AFD – PoD – 2" to slashes,
# producing a spelling that does not normalize-match the real number.
OVERRIDES: dict[int, str] = {
    397: "SEBI/HO/AFD/AFD-PoD-2/CIR/P/2023/148",
}

for lineno, r in enumerate(recs, 1):
    if lineno in SKIP_LINES:
        print(f"  skip line {lineno}: {SKIP_LINES[lineno]}", flush=True)
        continue
    m = parse_meta(r["text"])
    number = OVERRIDES.get(lineno) or m["circular_number"]
    if number and number != r.get("circular_number"):
        print(f"  {r['circular_number']} -> {number}", flush=True)
        r["circular_number"] = number
        r["issue_date"] = m["issue_date"]
        r["effective_date"] = m["effective_date"]
        changed += 1
```

State in the report what you put in each map and why. If you reject nothing,
leave `SKIP_LINES` empty and say so.

Note the knock-on for Task 4: with the override, line 397's new number is
`SEBI/HO/AFD/AFD-PoD-2/CIR/P/2023/148`. No golden row references line 397, so
Task 4's `MAPPING` is unaffected — but re-run the Task 4 exposure check after
this task and reconcile if that has changed.

- [ ] **Step 4: Apply the renumbering**

Run: `PYTHONPATH=src .venv/bin/python scripts/renumber.py`
Expected: one `old -> new` line per accepted change, then `updated N records. Next: make reindex`.

Run: `make validate-corpus`
Expected: `705 records, 0 violations`. Any remaining violation must be explained in the report, not suppressed.

- [ ] **Step 5: Commit**

```bash
git add scripts/analysis/renumber_audit.py scripts/renumber.py
git commit -m "fix(corpus): re-derive 17 stale circular numbers after parser improvements (audited)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: Update golden_v7 doc references and re-validate two row premises

Renumbering changes doc ids that 7 golden rows reference. Two of those rows are
lineage/repealed rows whose premise depends on which circular is which, so they
need re-checking, not just a string swap.

**Files:**
- Modify: `eval/golden/golden_v7.jsonl` (in the `.worktrees/golden-v7` worktree)
- Create: `scripts/golden_v7/remap_doc_ids.py`
- Test: `tests/test_golden_v7_remap.py` (create)

**Interfaces:**
- Consumes: `normalize_circular_number`, `sebi_rag.eval_harness.load_golden`, `sebi_rag.benchmark.validate_golden_v7`, `sebi_rag.benchmark.write_jsonl`.
- Produces: `remap(rows, mapping) -> tuple[list[dict], int]` (rewritten rows, ref count changed) — pure and importable.

**The 8 affected references** (7 rows; `v7-ls-029` has two):

| row | field | old | new |
|---|---|---|---|
| `v7-td-005` | relevant_circulars | `CIR/IMD/DF/5/2013` | `CIR/IMD/DF/14/2013` |
| `v7-bp-003` | relevant_circulars | `CIR/MRD/DP/41` | `CIR/MRD/DP/41/2010` |
| `v7-nt-014` | relevant_circulars | `CIR/IMD/DF/5/2013` | `CIR/IMD/DF/14/2013` |
| `v7-ls-029` | relevant_circulars | `CIR/4/51/2000` | `SEBI/IMD/MC No.3/10554/2012` |
| `v7-ls-029` | must_not_cite | `CIR/IMD/DF/5/2013` | `CIR/IMD/DF/14/2013` |
| `v7-rb-010` | relevant_circulars | `DOF3/P/CIR/2022/82` | *(unchanged — Task 2 restored its real text)* |
| `v7-rb-018` | relevant_circulars | `CIR/MRD/DP/13` | `CIR/MRD/DP/13/2013` |
| `v7-rb-020` | relevant_circulars | `SEBI/HO/IMD/DF2/CIR/P/2019/65` | `POD2/P/CIR/2023/48` |

- [ ] **Step 1: Write the failing test**

```python
# tests/test_golden_v7_remap.py
"""Doc-id remapping after the 2026-07-25 corpus renumbering (Task 4)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from golden_v7.remap_doc_ids import remap  # noqa: E402


def _row(**over):
    base = {"id": "v7-td-005", "relevant_circulars": ["CIR/IMD/DF/5/2013"],
            "must_not_cite": [], "relevant_chunks": [
                {"doc": "CIR/IMD/DF/5/2013", "quote": "x" * 50}]}
    base.update(over)
    return base


def test_remaps_relevant_circulars_and_span_docs():
    rows, n = remap([_row()], {"CIR/IMD/DF/5/2013": "CIR/IMD/DF/14/2013"})
    assert rows[0]["relevant_circulars"] == ["CIR/IMD/DF/14/2013"]
    assert rows[0]["relevant_chunks"][0]["doc"] == "CIR/IMD/DF/14/2013"
    assert n == 2


def test_remaps_must_not_cite():
    rows, n = remap([_row(must_not_cite=["CIR/IMD/DF/5/2013"],
                          relevant_circulars=["OTHER/1"], relevant_chunks=[])],
                    {"CIR/IMD/DF/5/2013": "CIR/IMD/DF/14/2013"})
    assert rows[0]["must_not_cite"] == ["CIR/IMD/DF/14/2013"]
    assert n == 1


def test_unmapped_rows_untouched():
    rows, n = remap([_row(relevant_circulars=["KEEP/1"], relevant_chunks=[])],
                    {"CIR/IMD/DF/5/2013": "CIR/IMD/DF/14/2013"})
    assert rows[0]["relevant_circulars"] == ["KEEP/1"] and n == 0


def test_matching_is_normalization_insensitive():
    rows, n = remap([_row(relevant_circulars=["SEBI/CIR/IMD/DF/5/2013"],
                          relevant_chunks=[])],
                    {"CIR/IMD/DF/5/2013": "CIR/IMD/DF/14/2013"})
    assert rows[0]["relevant_circulars"] == ["CIR/IMD/DF/14/2013"] and n == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest -q tests/test_golden_v7_remap.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'golden_v7.remap_doc_ids'`

- [ ] **Step 3: Implement `scripts/golden_v7/remap_doc_ids.py`**

```python
"""Rewrite golden_v7 doc references after the corpus renumbering
(2026-07-25 remediation Task 4).

Rewrites relevant_circulars, must_not_cite and every span's `doc`, matching
under normalize_circular_number so a differently-prefixed spelling still maps.
Span `quote` values are untouched — they resolve by text, not by id.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.benchmark import validate_golden_v7, write_jsonl  # noqa: E402
from sebi_rag.corpus import load_circulars  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402
from sebi_rag.ingest_pdf import normalize_circular_number as N  # noqa: E402

# old circular_number -> new, from the Task 3 renumber audit.
MAPPING = {
    "CIR/IMD/DF/5/2013": "CIR/IMD/DF/14/2013",
    "CIR/MRD/DP/41": "CIR/MRD/DP/41/2010",
    "CIR/4/51/2000": "SEBI/IMD/MC No.3/10554/2012",
    "CIR/MRD/DP/13": "CIR/MRD/DP/13/2013",
    "SEBI/HO/IMD/DF2/CIR/P/2019/65": "POD2/P/CIR/2023/48",
}


def remap(rows: list[dict], mapping: dict[str, str]) -> tuple[list[dict], int]:
    keyed = {N(k): v for k, v in mapping.items()}
    changed = 0
    out = []
    for row in rows:
        row = json.loads(json.dumps(row))  # deep copy, rows are plain JSON
        for field in ("relevant_circulars", "must_not_cite"):
            vals = row.get(field) or []
            new_vals = []
            for v in vals:
                nv = keyed.get(N(v))
                if nv:
                    changed += 1
                    new_vals.append(nv)
                else:
                    new_vals.append(v)
            if vals:
                row[field] = new_vals
        for span in row.get("relevant_chunks") or []:
            if isinstance(span, dict):
                nv = keyed.get(N(span.get("doc", "")))
                if nv:
                    changed += 1
                    span["doc"] = nv
        out.append(row)
    return out, changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", default=str(ROOT / "eval/golden/golden_v7.jsonl"))
    ap.add_argument("--corpus", default=str(ROOT / "data/corpus/circulars.jsonl"))
    args = ap.parse_args()
    rows = load_golden(args.golden)
    rows, n = remap(rows, MAPPING)
    issues = validate_golden_v7(rows, chunks=load_circulars(args.corpus))
    for i in issues:
        print(f"{i.item_id}: {i.message}", file=sys.stderr)
    if issues:
        print(f"{len(issues)} issues — NOT written", file=sys.stderr)
        return 1
    write_jsonl(args.golden, rows)
    print(f"remapped {n} references across {len(rows)} rows -> {args.golden}")
    return 0
```

- [ ] **Step 4: Run tests, then apply**

Run: `.venv/bin/python -m pytest -q tests/test_golden_v7_remap.py` → PASS (4 tests)

From the worktree:
```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG/.worktrees/golden-v7"
HF_HUB_DISABLE_XET=1 PYTHONPATH=src .venv/bin/python scripts/golden_v7/remap_doc_ids.py
```
Expected: `remapped 7 references across 260 rows`. If it exits 1 with issues, the span quotes no longer resolve — report the issues rather than editing the mapping.

- [ ] **Step 5: Re-validate the two premise-dependent rows by hand**

These two rows assert a relationship between specific circulars, and both of
their circulars were renumbered. Read each row's `query`, `rationale` and its
circulars' actual text in `data/corpus/circulars.jsonl`, then state a verdict in
the task report:

- **`v7-ls-029`** — a `lineage_supersession` row. Its gold doc is now
  `SEBI/IMD/MC No.3/10554/2012` (a 2012 MF master circular) and its
  `must_not_cite` is now `CIR/IMD/DF/14/2013` (a 2013 one). Confirm the
  supersession direction still holds: does the 2013 circular supersede the 2012
  one, and is the row's dated/undated treatment still correct? If the premise no
  longer holds, do NOT silently relabel — report it as a row needing redraft.
- **`v7-rb-020`** — its doc moved from a 2019 number to `POD2/P/CIR/2023/48`
  (2023). Confirm the record's `regulatory_basis_status` is still
  `repealed_basis` and the row's `must_contain: ["repealed", ...]` premise still
  applies to the correctly-numbered circular.

- [ ] **Step 6: Commit**

```bash
git add scripts/golden_v7/remap_doc_ids.py tests/test_golden_v7_remap.py eval/golden/golden_v7.jsonl
git commit -m "fix(golden-v7): remap doc references after corpus renumbering; re-validate ls-029/rb-020 premises

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: Reindex and re-validate every golden span

Repaired text and renumbered docs mean the persisted FAISS/BM25 index is stale.
This is the long real-model step.

**Files:**
- Modify: `data/index/*` (gitignored, regenerated)
- Modify: `data/corpus/circulars.jsonl` (re-annotated by `make annotate`)

- [ ] **Step 1: Record the pre-reindex baseline**

```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
.venv/bin/python -c "
import sys; sys.path.insert(0,'src')
from sebi_rag.corpus import load_circulars
print('chunks before:', len(load_circulars('data/corpus/circulars.jsonl')))"
```
Expected: a count near 77,859. Record it.

- [ ] **Step 2: Reindex**

Run: `make reindex`
Expected: annotate output, then index build. This is a long run (bge-m3 over
~78k chunks). Run it in the background and wait on completion rather than
polling. If it OOMs, report — do not silently reduce batch size.

- [ ] **Step 3: Re-validate all 260 golden rows against the new chunking**

```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG/.worktrees/golden-v7"
HF_HUB_DISABLE_XET=1 PYTHONPATH=src .venv/bin/python -c "
import sys; sys.path.insert(0, 'src')
from sebi_rag.eval_harness import load_golden
from sebi_rag.benchmark import validate_golden_v7
from sebi_rag.corpus import load_circulars
rows = load_golden('eval/golden/golden_v7.jsonl')
issues = validate_golden_v7(rows, chunks=load_circulars('data/corpus/circulars.jsonl'))
print(len(issues), 'issues')
[print(i.item_id, i.message) for i in issues]"
```
Expected: `0 issues`. Spans are quote-anchored specifically so they survive
re-chunking. **If any span fails to resolve**, that is the designed loud error:
report which rows, and whether the cause is the repaired text (expected only for
docs in Task 2's map) or an unrelated chunking change. Do not delete the span to
make the check pass.

- [ ] **Step 4: Full offline suite**

Run: `.venv/bin/python -m pytest -q -m "not integration"`
Expected: no regressions.

- [ ] **Step 5: Commit any corpus-annotation churn that is tracked**

`data/corpus/` and `data/index/` are gitignored, so there is likely nothing to
commit. Run `git status --short` and commit only tracked changes; state in the
report that the index was rebuilt and its chunk count.

---

### Task 6: Fix the `assemble_pool` cap-saturation defect

Step 1 of `assemble_pool` iterates chunks in document order and consumes the
whole `cap` whenever a `must_contain` literal is a common word, so the
reranked/dense/BM25 legs never run. Measured: 92/207 pools saturated, 24 of 25
escalations inside that set.

**Files:**
- Modify: `scripts/golden_v7/build_pool.py` (`assemble_pool`)
- Modify: `tests/test_golden_v7_pool.py` (add regression tests)

**Interfaces:**
- Produces: `assemble_pool(row, retriever, reranker, cap=20, gold_literal_cap=6)`. The new keyword bounds step 1; existing callers keep working.

- [ ] **Step 1: Write the failing regression test**

Append to `tests/test_golden_v7_pool.py`:

```python
def _saturating_retriever(n: int = 40):
    """One gold doc with `n` chunks that ALL contain the word "broker", so a
    must_contain of ["broker"] matches every chunk. Only the last chunk
    answers a query about requirement 39."""
    chunks = []
    for i in range(n):
        chunks += hierarchical_chunk(
            f"{i}. Clause {i}:\nThe stock broker shall observe requirement {i} "
            f"in full and without exception at all times whatsoever.",
            CircularMeta(circular_number="SEBI/GOLD/1", subject=f"S{i}"))
    return HybridRetriever.build(chunks, HashEmbedder()), chunks


def test_deep_relevant_chunk_is_reachable_despite_a_common_literal():
    """Regression (2026-07-25): a must_contain literal matching many gold-doc
    chunks filled the whole cap in DOCUMENT order, so the reranked / dense /
    BM25 legs contributed nothing and a provision late in the document was
    unreachable. 92 of 207 real pools were saturated this way.

    The chunk answering "requirement 39" is last in document order, so before
    the fix (cap consumed by chunks 0..19) it cannot be in the pool.
    """
    retr, chunks = _saturating_retriever(40)
    row = {"query": "requirement 39 stock broker",
           "relevant_circulars": ["SEBI/GOLD/1"],
           "must_contain": ["broker"], "abstain": False}
    pool = assemble_pool(row, retr, LexicalReranker(), cap=20)
    ids = {c.id for c in pool}
    assert len(ids) == len(pool), "pool must stay deduped"
    target = [c.id for c in chunks if "requirement 39 " in c.text]
    assert target, "fixture did not produce a requirement-39 chunk"
    assert target[0] in ids, (
        "the chunk that answers the query is missing — step 1 is still "
        "consuming the cap in document order")


def test_gold_literal_chunks_still_lead_the_pool_when_bounded():
    row = {"query": "upfront margin percentage",
           "relevant_circulars": ["SEBI/GOLD/1"],
           "must_contain": ["twenty per cent"], "abstain": False}
    pool = assemble_pool(row, _retriever(), LexicalReranker(), cap=5)
    assert pool and pool[0].doc_id == "SEBI/GOLD/1"
```

If `LexicalReranker` does not rank the requirement-39 chunk into the bounded
gold-literal slice, the ranked legs must still surface it — that is the
behaviour under test. If the test fails *after* the fix, the ranked legs are not
being reached at all; do not weaken the assertion to make it pass.

- [ ] **Step 2: Run to verify the first test fails**

Run: `.venv/bin/python -m pytest -q tests/test_golden_v7_pool.py`
Expected: FAIL on `test_common_literal_does_not_starve_the_ranked_legs` — the
assertion about ranked-leg contribution fails because step 1 filled the cap.

- [ ] **Step 3: Bound step 1 in `scripts/golden_v7/build_pool.py`**

Replace the signature and step-1 block:

```python
def assemble_pool(row, retriever, reranker, cap: int = 20,
                  gold_literal_cap: int = 6):
    """TREC-style pool: gold-doc literal matches lead, then round-robin over
    [reranked, dense, raw-BM25] top-15 legs until `cap`, deduped by chunk id.

    `gold_literal_cap` bounds the literal-match step. Without it a common
    must_contain literal ("broker") matches hundreds of chunks in a master
    circular and fills the entire cap in DOCUMENT order — preamble and
    table-of-contents stubs — starving the ranked legs entirely
    (2026-07-25: this happened on 92 of 207 pools).
    """
    gold_docs = set(row.get("relevant_circulars", []))
    literals = [_norm_ws(m) for m in row.get("must_contain", []) if m]
    q = row["query"]

    pool, seen = [], set()

    def add(c, limit=cap):
        if c.id not in seen and len(pool) < limit:
            seen.add(c.id)
            pool.append(c)
            return True
        return False

    literal_hits = [c for c in retriever.chunks
                    if c.doc_id in gold_docs and literals
                    and any(lit in _norm_ws(c.text) for lit in literals)]
    # Rank the literal matches by the reranker instead of taking document
    # order, so the ones that actually answer the query lead.
    if literal_hits:
        ranked = [c for c, _ in reranker.rerank(q, literal_hits)]
        for c in ranked:
            add(c, limit=min(gold_literal_cap, cap))

    rrf = retriever.retrieve(q, top_n=50)
    reranked = [c for c, _ in reranker.rerank(q, [c for c, _ in rrf])[:15]]
    dense = [retriever.chunks[i] for i, _ in retriever.dense.search(q, 15)]
    bm25 = [retriever.chunks[i] for i, _ in retriever.sparse.search(q, 15)]  # raw query: no expand_query
    legs = [reranked, dense, bm25]
    i = 0
    while len(pool) < cap and any(legs):
        leg = legs[i % 3]
        if leg:
            add(leg.pop(0))
        i += 1
    return pool
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest -q tests/test_golden_v7_pool.py`
Expected: PASS (4 tests — the 2 originals plus the 2 new).

- [ ] **Step 5: Full offline suite, then commit**

Run: `.venv/bin/python -m pytest -q -m "not integration"`
Expected: no regressions.

```bash
git add scripts/golden_v7/build_pool.py tests/test_golden_v7_pool.py
git commit -m "fix(golden-v7): bound and rank the gold-literal pool step so it stops starving the ranked legs

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 7: Deterministically backfill the 18 recoverable escalations

Each of these 18 rows has an `answer_contains` literal that matches exactly one
chunk in the Task-5 candidate files — the chunk its query was drafted from. That
is the gold chunk by construction, so no re-judgment is needed.

**Files:**
- Create: `scripts/golden_v7/backfill_escalations.py`
- Modify: `eval/golden/golden_v7.jsonl`, `eval/golden/v7_annotations/votes.jsonl`, `eval/golden/v7_annotations/label_escalations.txt`
- Test: `tests/test_golden_v7_backfill.py` (create)

**Interfaces:**
- Consumes: `eval/golden/v7_annotations/candidates/{body_paraphrase,numeric_table}.jsonl` (fields `chunk_id`, `doc`, `subject`, `text`), `validate_golden_v7`, `load_circulars`.
- Produces: `find_source_chunk(row, candidates) -> dict | None` (the unique candidate whose text contains the row's `answer_contains`, else None) and `quote_for(candidate, row, min_chars=40) -> str` (a verbatim body window containing the literal).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_golden_v7_backfill.py
"""Deterministic escalation backfill from Task-5 candidate chunks
(2026-07-25 remediation Task 7)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from golden_v7.backfill_escalations import find_source_chunk, quote_for  # noqa: E402

_CAND = {
    "chunk_id": "SEBI/X/1#1.8. Besides the above#326",
    "doc": "SEBI/X/1",
    "subject": "Oversight",
    "text": ("1. The criteria for selection of members for annual inspection "
             "are as follows: 1.8. Besides the above, the special purpose or "
             "limited inspections shall be carried out based on any triggers "
             "like patterns found during investor complaint resolution or "
             "arbitration, complaints on specific malpractices of a broker."),
}


def _row(**over):
    base = {"id": "v7-bp-008", "relevant_circulars": ["SEBI/X/1"],
            "answer_contains": "patterns found during investor complaint resolution"}
    base.update(over)
    return base


def test_finds_the_unique_source_chunk():
    assert find_source_chunk(_row(), [_CAND])["chunk_id"] == _CAND["chunk_id"]


def test_returns_none_when_ambiguous():
    assert find_source_chunk(_row(), [_CAND, dict(_CAND, chunk_id="other#9")]) is None


def test_returns_none_when_doc_does_not_match():
    assert find_source_chunk(_row(relevant_circulars=["OTHER/2"]), [_CAND]) is None


def test_quote_is_verbatim_contains_literal_and_long_enough():
    q = quote_for(_CAND, _row())
    assert q in _CAND["text"]
    assert _row()["answer_contains"] in q
    assert len(" ".join(q.split())) >= 40


def test_quote_never_returns_the_header_line():
    cand = dict(_CAND, text="SEBI/X/1 | Oversight | s\n" + _CAND["text"])
    q = quote_for(cand, _row())
    assert not q.startswith("SEBI/X/1 |")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest -q tests/test_golden_v7_backfill.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'golden_v7.backfill_escalations'`

- [ ] **Step 3: Implement `scripts/golden_v7/backfill_escalations.py`**

```python
"""Backfill escalated golden_v7 rows from their Task-5 source candidate
(2026-07-25 remediation Task 7).

An escalation means pooling never surfaced the governing chunk. For
body_paraphrase and numeric_table rows the drafting candidate file records the
exact chunk the query was written from, and `answer_contains` was taken from
that chunk's text — so the gold chunk is recoverable deterministically, with no
re-judgment and no retrieval.

Rows that do not resolve to exactly one candidate are left escalated.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.benchmark import validate_golden_v7, write_jsonl  # noqa: E402
from sebi_rag.corpus import load_circulars  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402

ANN = ROOT / "eval" / "golden" / "v7_annotations"
MIN_QUOTE_CHARS = 40


def _norm(s: str) -> str:
    return " ".join(s.split()).lower()


def _body(text: str) -> str:
    """Chunk text minus the leading "<doc> | <subject> | <section>" header."""
    first, sep, rest = text.partition("\n")
    return rest if sep and first.count(" | ") >= 2 else text


def find_source_chunk(row: dict, candidates: list[dict]) -> dict | None:
    lit = _norm(row.get("answer_contains", ""))
    if not lit:
        return None
    gold = set(row.get("relevant_circulars", []))
    hits = [c for c in candidates
            if c.get("doc") in gold and lit in _norm(c.get("text", ""))]
    return hits[0] if len(hits) == 1 else None


def quote_for(candidate: dict, row: dict, min_chars: int = MIN_QUOTE_CHARS) -> str:
    """Smallest verbatim body window that contains answer_contains and clears
    min_chars after whitespace normalization."""
    body = _body(candidate["text"])
    lit = row["answer_contains"]
    i = body.find(lit)
    if i < 0:  # differs only by whitespace — fall back to the whole body
        return body.strip()
    start, end = i, i + len(lit)
    # widen to sentence-ish boundaries until long enough
    while len(" ".join(body[start:end].split())) < min_chars:
        if start > 0:
            start = max(0, start - 40)
        elif end < len(body):
            end = min(len(body), end + 40)
        else:
            break
    return body[start:end].strip()


def _load_candidates() -> list[dict]:
    out = []
    for name in ("body_paraphrase", "numeric_table"):
        p = ANN / "candidates" / f"{name}.jsonl"
        out += [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()
                if l.strip()]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", default=str(ROOT / "eval/golden/golden_v7.jsonl"))
    ap.add_argument("--corpus", default=str(ROOT / "data/corpus/circulars.jsonl"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    esc_path = ANN / "label_escalations.txt"
    esc_lines = [l for l in esc_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    escalated = {l.split(":", 1)[0].strip(): l for l in esc_lines}

    rows = load_golden(args.golden)
    cands = _load_candidates()
    filled, left = {}, {}
    for row in rows:
        rid = row["id"]
        if rid not in escalated or (row.get("relevant_chunks") or []):
            continue
        cand = find_source_chunk(row, cands)
        if not cand:
            left[rid] = escalated[rid]
            continue
        quote = quote_for(cand, row)
        row["relevant_chunks"] = [{"doc": cand["doc"], "quote": quote}]
        filled[rid] = cand["chunk_id"]

    issues = validate_golden_v7(rows, chunks=load_circulars(args.corpus))
    for i in issues:
        print(f"{i.item_id}: {i.message}", file=sys.stderr)
    if issues:
        print(f"{len(issues)} issues — NOT written", file=sys.stderr)
        return 1

    print(f"backfilled {len(filled)} rows; {len(left)} remain escalated")
    for rid, cid in sorted(filled.items()):
        print(f"  {rid} <- {cid}")
    if args.dry_run:
        return 0

    write_jsonl(args.golden, rows)
    with (ANN / "votes.jsonl").open("a", encoding="utf-8") as f:
        for rid, cid in sorted(filled.items()):
            row = next(r for r in rows if r["id"] == rid)
            f.write(json.dumps({
                "id": rid, "annotator": "claude", "governing": [cid],
                "expected_literal": row.get("answer_contains", ""),
            }, ensure_ascii=False) + "\n")
    esc_path.write_text(
        "".join(f"{l}\n" for l in left.values()), encoding="utf-8")
    print(f"votes appended; {esc_path.name} now lists {len(left)} rows")
    return 0
```

Note: the pre-existing `claude` vote for a backfilled row recorded
`governing: []`. Appending a corrected vote leaves two records for that id.
Task 8 Step 4 reconciles `votes.jsonl` — do not hand-edit it here.

- [ ] **Step 4: Run tests, then a dry run, then apply**

Run: `.venv/bin/python -m pytest -q tests/test_golden_v7_backfill.py` → PASS (5 tests)

From the worktree:
```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG/.worktrees/golden-v7"
HF_HUB_DISABLE_XET=1 PYTHONPATH=src .venv/bin/python scripts/golden_v7/backfill_escalations.py --dry-run
```
Expected: `backfilled 18 rows; 7 remain escalated`, listing these 18 ids:
`v7-bp-002, v7-bp-003, v7-bp-008, v7-bp-009, v7-bp-014, v7-bp-019, v7-bp-021,
v7-bp-022, v7-bp-023, v7-bp-024, v7-bp-025, v7-bp-027, v7-bp-032, v7-bp-033,
v7-bp-039, v7-bp-041, v7-bp-042, v7-nt-021`.

If the count differs from 18, STOP and report which rows changed and why —
Task 5's reindex may have altered candidate resolution.

Then apply (drop `--dry-run`). Expected: `0 issues` and the votes/escalations
files updated.

- [ ] **Step 5: Spot-check 4 backfilled spans by hand**

For `v7-bp-008`, `v7-nt-021`, `v7-bp-033` and `v7-bp-041`, print the row's
`query`, `answer_contains` and new span quote, and confirm the quote genuinely
carries the provision the query asks about (not an adjacent clause). Record the
four verdicts in the task report.

- [ ] **Step 6: Commit**

```bash
git add scripts/golden_v7/backfill_escalations.py tests/test_golden_v7_backfill.py \
        eval/golden/golden_v7.jsonl eval/golden/v7_annotations/votes.jsonl \
        eval/golden/v7_annotations/label_escalations.txt
git commit -m "data(golden-v7): backfill 18 escalated rows from their drafting source chunks

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 8: Re-pool and relabel the 7 remaining escalations

**Files:**
- Modify: `eval/golden/v7_annotations/pools.jsonl`, `eval/golden/golden_v7.jsonl`, `eval/golden/v7_annotations/votes.jsonl`, `eval/golden/v7_annotations/label_escalations.txt`

The 7: `v7-bp-013` (two candidate matches — needs a judgment call),
`v7-ls-010`, `v7-mh-009`, `v7-mh-012`, `v7-mh-016`, `v7-mh-018` (no chunk-level
candidate file), `v7-rb-010` (was blocked on the corpus bug; Task 2 fixed it).

- [ ] **Step 1: Re-pool just these 7 rows with the fixed `assemble_pool`**

Add a `--only` filter to `scripts/golden_v7/build_pool.py`'s `main()` so a
re-pool does not rewrite all 207 records:

```python
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="",
                    help="comma-separated row ids to (re)pool; merges into pools.jsonl")
    args = ap.parse_args()
    only = {s.strip() for s in args.only.split(",") if s.strip()}
```

and when `only` is set, load the existing `pools.jsonl`, replace just those
records, and write the merged file back — preserving the order of untouched
records.

Run (needs the rebuilt index and MPS models; several minutes):
```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG/.worktrees/golden-v7"
$(printf '%s ' HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src) \
  .venv/bin/python scripts/golden_v7/build_pool.py \
  --only v7-bp-013,v7-ls-010,v7-mh-009,v7-mh-012,v7-mh-016,v7-mh-018,v7-rb-010
```
Expected: 7 lines of `<id> <n>` on stderr, `pools.jsonl` still 207 records.

- [ ] **Step 2: Judge the 7 re-pooled rows under the Task-8 rules**

Apply the original labeling rules verbatim: a chunk is governing only if its
text contains the provision that answers the query; quote a verbatim ≥40-char
BODY window (never the `"<doc> | subject | section"` header line); a
`must_not_cite` doc can never yield a span; `multi_hop` rows should get a span
from each of their two `relevant_circulars` where the pool supports it. If a row
still has no governing chunk, leave it escalated with an updated reason — a
genuine miss after the fix is a valid outcome and more useful than a forced
label.

- [ ] **Step 3: Validate**

```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG/.worktrees/golden-v7"
HF_HUB_DISABLE_XET=1 PYTHONPATH=src .venv/bin/python -c "
import sys; sys.path.insert(0, 'src')
from sebi_rag.eval_harness import load_golden
from sebi_rag.benchmark import validate_golden_v7
from sebi_rag.corpus import load_circulars
rows = load_golden('eval/golden/golden_v7.jsonl')
issues = validate_golden_v7(rows, chunks=load_circulars('data/corpus/circulars.jsonl'))
print(len(issues), 'issues')
[print(i.item_id, i.message) for i in issues]"
```
Expected: `0 issues`.

- [ ] **Step 4: Reconcile `votes.jsonl` to one record per row**

Task 7 appended corrected votes for rows that already had a `governing: []`
vote. Collapse duplicates so each `(id, annotator)` pair appears once, keeping
the LAST occurrence (the corrected one), and preserving file order otherwise:

```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG/.worktrees/golden-v7"
.venv/bin/python - <<'PY'
import json
from pathlib import Path
p = Path('eval/golden/v7_annotations/votes.jsonl')
rows = [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]
last = {}
for r in rows:
    last[(r['id'], r['annotator'])] = r
out, seen = [], set()
for r in rows:
    k = (r['id'], r['annotator'])
    if k in seen:
        continue
    seen.add(k)
    out.append(last[k])
p.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in out), encoding='utf-8')
print(f'{len(rows)} -> {len(out)} vote records')
PY
```
Expected: `225 -> 207 vote records` (207 answerable rows, one claude vote each).
Report the actual numbers; a total other than 207 means a row is missing a vote.

- [ ] **Step 5: Commit**

```bash
git add scripts/golden_v7/build_pool.py eval/golden/v7_annotations/pools.jsonl \
        eval/golden/golden_v7.jsonl eval/golden/v7_annotations/votes.jsonl \
        eval/golden/v7_annotations/label_escalations.txt
git commit -m "data(golden-v7): re-pool and relabel the 7 remaining escalations; reconcile votes

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 9: Wrap-up — docs, ledger, final census

**Files:**
- Modify: `CLAUDE.md` (Testing & Evaluation section), `docs/status.md` (append), `.superpowers/sdd/progress.md`

- [ ] **Step 1: CLAUDE.md** — in "Testing & Evaluation", add one line: `make validate-corpus` checks corpus integrity (duplicate body text, circular_number derivable from own text; `--deep` also re-extracts every PDF) and must pass after any ingest, backfill, or repair.

- [ ] **Step 2: docs/status.md** — dated entry recording: the two bug classes and their root causes (shared-text batch write; stale numbers predating parser improvements), 6 records repaired from local orphan PDFs, N records renumbered, the `assemble_pool` saturation defect (92/207 pools) and its fix, escalations reduced from 25 to the final count, and the reindexed chunk count.

- [ ] **Step 3: Final census + full suite**

```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
make validate-corpus
cd .worktrees/golden-v7 && .venv/bin/python -m pytest -q -m "not integration"
```
Expected: `705 records, 0 violations`; suite green.

- [ ] **Step 4: Append to the SDD ledger** one line per completed task, then commit.

```bash
git add -A && git commit -m "docs: record corpus + pooling remediation (root causes, repairs, final census)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

- [ ] **Step 5: Report to the user** — the final escalation count, records repaired/renumbered, any row whose premise Task 4 found invalid, and whether golden_v7 is ready for Tasks 9–14 of the expansion plan.

---

## Plan Self-Review (performed at write time)

- **Coverage:** A1 text corruption → Task 2; A2 stale numbers → Task 3; A3 missing guardrail → Task 1 (first, so it verifies the repairs); eval-set fallout → Task 4; index staleness → Task 5; pooling defect → Task 6; escalation recovery → Tasks 7–8; docs → Task 9.
- **Ordering hazards made explicit:** renumber-before-text-repair causes a 5-way collision (Task 3 Step 2 has a collision gate); re-pooling before reindex would read stale embeddings (Task 8 follows Task 5); `ingest(replace=True)` drops annotations, restored by Task 5's `annotate`.
- **Decisions deliberately left to the implementer with a required written verdict:** the two suspicious renumberings (lines 397, 417) in Task 3 Step 3; the `v7-ls-029` / `v7-rb-020` premises in Task 4 Step 5; the 7 relabels in Task 8 Step 2. Each says what to check and forbids silently loosening a check.
- **Type consistency:** `remap(rows, mapping) -> (rows, int)`, `find_source_chunk(row, candidates) -> dict|None`, `quote_for(candidate, row, min_chars)`, `assemble_pool(..., cap, gold_literal_cap)`, `validate(records)` / `validate_deep(records, raw_dir)` are used under those exact names in every later reference.
- **Known residual risk:** Task 5's re-chunking could fail to resolve a span written against pre-repair text. Task 5 Step 3 treats that as a loud error with a defined response (report, do not delete the span).
- **Verified at plan-write time (so the implementer does not hit them cold):** Task 1's test fixtures do derive `AFD/P/CIR/2022/125` and `DOF3/P/CIR/2022/82` from their own text, as those tests assume; line 397's rejoined spelling does NOT share a normalization key with the canonical one, so Task 3 carries a pre-filled `OVERRIDES` entry rather than a "check and decide" instruction.
- **Out of scope, recorded for later:** 22 further orphan PDFs in `data/raw/` belong to no corpus record (possible ingestion coverage gap, worth its own audit); `_rejoin_split`'s en-dash→slash healing mangles numbers whose own components contain en-dashes — worked around per-record here rather than fixed, because that regex is load-bearing for other records.
