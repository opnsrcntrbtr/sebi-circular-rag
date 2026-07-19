# Scoped Contextual Chunk Headers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the probes answer-level gate (4 → ≤ 3) by generating one-sentence lay+statutory contextual headers for ~18.2k deep sub-clause and annex chunks and merging them into chunk text at index build.

**Architecture:** A `HeaderGenerator` (injected callable, MLX only via `load()` — the proven `HydeExpander` pattern) writes one plain sentence per chunk into a committed sidecar `data/corpus/context_headers.jsonl`; a pure `apply_context_headers` merges sidecar rows into chunk text inside `scripts/build_index.py`. A pilot go/no-go on the known failure chunks runs before the ~5–8 h full generation. Retrieval code is untouched — enrichment is entirely index-side.

**Tech Stack:** Python 3.12 (uv-managed venv), pytest, mlx-lm (working since the transformers 5.14.1 fix, commit 8f997ad), Qwen2.5-1.5B-Instruct-4bit with a single escalation option to Qwen2.5-7B-Instruct-4bit.

**Spec:** `docs/superpowers/specs/2026-07-19-contextual-headers-design.md` (approved).

## Global Constraints

- Scope is exactly: section depth ≥ 3 (`^\d+(?:\.\d+){2,}`) OR section matching `annex|appendix|schedule` (case-insensitive) — ~17,601 + 595 chunks. No headers for shallow chunks; full-corpus generation declined.
- Header output contract: one plain sentence, ≤ 200 chars, no markdown/headings/dates/circular numbers; silent failure → `""`.
- The generation prompt sees only corpus text (subject, governing clause, chunk body) — never probe or golden wording.
- Pilot go/no-go gates the full run; at most one model escalation (1.5B → 7B); if still failing, stop and report no-go.
- Chunk count and IDs unchanged (77,859); tests fully offline (fake callables, no MLX).
- Never overwrite existing run dirs; new runs go to `eval/runs/iv9-probes/` and `eval/runs/iv9-golden/`; iv7 is the comparison baseline (HyDE stays off).
- `make test` green after every task (271 currently passing; 279 after Task 1's eight new tests).
- After modifying source code, run `graphify update .` before committing (project rule).
- All commands run from repo root: `/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG`. Use `uv run python …` or `.venv/bin/python …` — bare `python` lacks the project deps.

---

### Task 1: `context_headers` module (TDD)

**Files:**
- Create: `src/sebi_rag/context_headers.py`
- Test: `tests/test_context_headers.py` (new file)

**Interfaces:**
- Consumes: `Chunk` dataclass (`src/sebi_rag/segment.py:29` — fields `id, doc_id, section, text, meta`); `mlx_lm` inside `load()` only, mirroring `HydeExpander.load` (`src/sebi_rag/hyde.py:33`).
- Produces (used verbatim by Tasks 2–3):
  - `HeaderGenerator(generate: Callable[[str], str], max_chars: int = 200)` with `describe(subject: str, governing: str, chunk_text: str) -> str` and `HeaderGenerator.load(model: str = "mlx-community/Qwen2.5-1.5B-Instruct-4bit", max_tokens: int = 80) -> HeaderGenerator`.
  - `apply_context_headers(chunks: list[Chunk], headers: dict[str, str]) -> list[Chunk]`.
  - `in_scope(section: str) -> bool`.
  - `load_headers(path: str | Path) -> dict[str, str]` (missing file → `{}`).

- [ ] **Step 1: Write the failing tests**

Create `tests/test_context_headers.py`:

```python
"""Contextual chunk headers (iv9): one lay+statutory sentence per deep chunk.

Offline only — generation is an injected callable; mlx_lm never loads here.
"""
from __future__ import annotations

from sebi_rag.context_headers import (
    HeaderGenerator,
    apply_context_headers,
    in_scope,
    load_headers,
)
from sebi_rag.segment import Chunk


def test_describe_prompt_contains_inputs_and_constraints():
    seen: dict[str, str] = {}

    def fake(prompt: str) -> str:
        seen["p"] = prompt
        return " Governs winding down of a rating agency. "

    out = HeaderGenerator(fake).describe(
        "Master Circular for Credit Rating Agencies",
        "4.1.1. On and from the date of the Order",
        "not take any new clients or fresh mandates",
    )
    for frag in (
        "Master Circular for Credit Rating Agencies",
        "4.1.1. On and from the date of the Order",
        "not take any new clients or fresh mandates",
        "markdown",
    ):
        assert frag in seen["p"], f"prompt missing: {frag}"
    assert out == "Governs winding down of a rating agency."


def test_describe_cleans_markdown_and_newlines():
    g = HeaderGenerator(lambda p: "### Obligations\nof a CRA ceasing operations")
    assert g.describe("s", "g", "t") == "Obligations of a CRA ceasing operations"


def test_describe_error_or_empty_returns_empty():
    def boom(prompt: str) -> str:
        raise RuntimeError("mlx exploded")

    assert HeaderGenerator(boom).describe("s", "g", "t") == ""
    assert HeaderGenerator(lambda p: "  \n ").describe("s", "g", "t") == ""


def test_describe_truncates_to_max_chars():
    g = HeaderGenerator(lambda p: "y" * 999, max_chars=200)
    assert len(g.describe("s", "g", "t")) == 200


def _chunk(cid: str, text: str) -> Chunk:
    return Chunk(id=cid, doc_id=cid.split("#")[0], section="s", text=text)


def test_header_inserted_below_breadcrumb():
    cid = "DOC/1#4.1.1.2. not take any#0"
    c = _chunk(cid, "DOC/1 | subject | section\n4.1.1.2. body text")
    out = apply_context_headers([c], {cid: "Governs winding down."})
    assert out[0].text.splitlines() == [
        "DOC/1 | subject | section",
        "Governs winding down.",
        "4.1.1.2. body text",
    ]
    assert out[0].id == cid and len(out) == 1


def test_missing_or_empty_header_leaves_chunk_unchanged():
    c = _chunk("DOC/1#s#0", "a\nb")
    assert apply_context_headers([c], {})[0].text == "a\nb"
    assert apply_context_headers([c], {"DOC/1#s#0": "  "})[0].text == "a\nb"


def test_scope_predicate():
    assert in_scope("4.1.1. On and from the date")
    assert in_scope("12.5.2.1. rated such security")
    assert not in_scope("4.1. In order to facilitate")
    assert not in_scope("preamble")
    assert in_scope("Annexure 17")
    assert in_scope("Appendix A serial numbers")


def test_load_headers_missing_file_returns_empty(tmp_path):
    assert load_headers(tmp_path / "none.jsonl") == {}
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_context_headers.py -v`
Expected: collection error — `ModuleNotFoundError: No module named 'sebi_rag.context_headers'`.

- [ ] **Step 3: Implement the module**

Create `src/sebi_rag/context_headers.py`:

```python
"""Contextual chunk headers (iv9): one lay+statutory sentence per chunk.

Index-side enrichment for deep sub-clause and annex chunks whose statutory
text lacks the vocabulary users query with (probe-par-03 class). Headers
are generated once into data/corpus/context_headers.jsonl (committed) and
merged into chunk text at index build. Failure is silent by design: any
generation error or empty output yields "", which callers treat as
no-header.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable

from .segment import Chunk

_PROMPT = (
    "You are indexing Indian securities regulations. Read this provision "
    "from a SEBI circular and describe in ONE plain sentence what it "
    "governs, naming the topic both in everyday language and in the "
    "statute's own terms. Do not use markdown, headings, dates, or "
    "circular numbers. Reply with the sentence only.\n"
    "Circular subject: {subject}\n"
    "Governing clause: {governing}\n"
    "Provision: {chunk_text}"
)

_DEEP = re.compile(r"^\d+(?:\.\d+){2,}")
_ANNEX = re.compile(r"annex|appendix|schedule", re.I)


def in_scope(section: str) -> bool:
    """Spec scope: depth>=3 numbered sub-clauses plus annex-family headings."""
    return bool(_DEEP.match(section) or _ANNEX.search(section))


class HeaderGenerator:
    def __init__(
        self, generate: Callable[[str], str], max_chars: int = 200
    ) -> None:
        self._generate = generate
        self.max_chars = max_chars

    def describe(self, subject: str, governing: str, chunk_text: str) -> str:
        try:
            out = self._generate(_PROMPT.format(
                subject=subject, governing=governing, chunk_text=chunk_text
            ))
        except Exception:  # noqa: BLE001 — silent-failure contract (spec)
            return ""
        out = " ".join((out or "").split())
        return out.lstrip("#*>- ").strip()[: self.max_chars]

    @classmethod
    def load(
        cls,
        model: str = "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
        max_tokens: int = 80,
    ) -> "HeaderGenerator":
        from mlx_lm import generate as _gen
        from mlx_lm import load

        m, tok = load(model)

        def call(prompt: str) -> str:
            try:
                p = tok.apply_chat_template(
                    [{"role": "user", "content": prompt}],
                    add_generation_prompt=True, tokenize=False,
                )
            except Exception:  # noqa: BLE001
                p = prompt
            return _gen(m, tok, prompt=p, max_tokens=max_tokens, verbose=False)

        return cls(call)


def apply_context_headers(
    chunks: list[Chunk], headers: dict[str, str]
) -> list[Chunk]:
    """Insert each chunk's header as a line below its breadcrumb line.

    Pure and id-preserving: chunk count and IDs never change; chunks with
    no (or blank) header pass through untouched.
    """
    out: list[Chunk] = []
    for c in chunks:
        h = headers.get(c.id, "").strip()
        if not h:
            out.append(c)
            continue
        if "\n" in c.text:
            first, rest = c.text.split("\n", 1)
            text = f"{first}\n{h}\n{rest}"
        else:
            text = f"{c.text}\n{h}"
        out.append(Chunk(id=c.id, doc_id=c.doc_id, section=c.section,
                         text=text, meta=c.meta))
    return out


def load_headers(path: str | Path) -> dict[str, str]:
    p = Path(path)
    if not p.exists():
        return {}
    out: dict[str, str] = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["chunk_id"]] = r.get("header", "")
    return out
```

- [ ] **Step 4: Run the tests to verify green**

Run: `uv run pytest tests/test_context_headers.py -v`
Expected: 8 PASS.

- [ ] **Step 5: Full suite, graph, commit**

Run: `make test` — expected 279 passed (271 + 8).

```bash
graphify update .
git add src/sebi_rag/context_headers.py tests/test_context_headers.py graphify-out
git commit -m "feat: context-header module — generator, scope predicate, index merge (iv9)"
```

---

### Task 2: generation script + pilot go/no-go

**Files:**
- Create: `scripts/generate_context_headers.py`
- Output (pilot only, scratch — not committed): `<scratchpad>/iv9-pilot/`

**Interfaces:**
- Consumes: `load_circulars(path) -> list[Chunk]` (`src/sebi_rag/corpus.py:10`); `HeaderGenerator`, `in_scope`, `load_headers` from Task 1 (exact signatures in Task 1's Produces block).
- Produces: the script CLI — `--out` (default `data/corpus/context_headers.jsonl`), `--model` (default `mlx-community/Qwen2.5-1.5B-Instruct-4bit`), `--limit N`, `--ids <file of chunk ids, one per line>`. Rows: `{"chunk_id", "header", "model"}`. Resumable: chunk ids already in `--out` are skipped. Task 3 runs this script for the full scope.

- [ ] **Step 1: Write the script**

Create `scripts/generate_context_headers.py`:

```python
"""Generate contextual headers for deep sub-clause + annex chunks (iv9).

Resumable: chunk ids already present in --out are skipped, so an
interrupted multi-hour run continues where it stopped.

    PYTHONPATH=src .venv/bin/python scripts/generate_context_headers.py \
        [--out data/corpus/context_headers.jsonl] [--model ...] \
        [--limit N] [--ids ids.txt]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.context_headers import (  # noqa: E402
    HeaderGenerator, in_scope, load_headers,
)
from sebi_rag.corpus import load_circulars  # noqa: E402

_HEAD = re.compile(r"^\d+(?:\.\d+)*[.)]\s")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "data" / "corpus" / "context_headers.jsonl"))
    ap.add_argument("--model", default="mlx-community/Qwen2.5-1.5B-Instruct-4bit")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--ids", default="")
    args = ap.parse_args()

    chunks = load_circulars(ROOT / "data" / "corpus" / "circulars.jsonl")
    done = set(load_headers(args.out))
    targets = [
        c for c in chunks
        if in_scope(c.id.split("#")[1]) and c.id not in done
    ]
    if args.ids:
        keep = {l.strip() for l in Path(args.ids).read_text().splitlines() if l.strip()}
        targets = [c for c in targets if c.id in keep]
    if args.limit:
        targets = targets[: args.limit]
    print(f"targets={len(targets)} (skipped {len(done)} already done)", flush=True)

    gen = HeaderGenerator.load(model=args.model)
    t0 = time.time()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "a", encoding="utf-8") as f:
        for i, c in enumerate(targets, 1):
            body = c.text.split("\n", 1)[1] if "\n" in c.text else c.text
            lines = body.splitlines()
            governing = lines[0] if lines and _HEAD.match(lines[0]) else ""
            h = gen.describe(c.meta.get("subject", ""), governing, body)
            f.write(json.dumps(
                {"chunk_id": c.id, "header": h, "model": args.model},
                ensure_ascii=False,
            ) + "\n")
            f.flush()
            if i % 100 == 0:
                rate = i / (time.time() - t0)
                print(f"{i}/{len(targets)}  {rate:.1f}/s  "
                      f"eta {((len(targets) - i) / rate) / 60:.0f} min", flush=True)
    print(f"done: {len(targets)} headers in {(time.time() - t0) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Collect the pilot chunk ids**

```bash
uv run python - <<'EOF'
import json
probes = {}
for l in open('eval/probes/probes_v1.jsonl'):
    r = json.loads(l); probes[r['id']] = r
ids = set()
targets = ['probe-par-03', 'probe-sup-04', 'probe-tbl-05', 'probe-num-05']
for l in open('data/index/chunks.jsonl'):
    c = json.loads(l)
    for pid in targets:
        p = probes[pid]
        if c['doc_id'] in set(p['relevant_circulars']) and any(
            n.lower() in c['text'].lower() for n in p['must_contain']
        ):
            ids.add(c['id'])
    # all CRA 4.1.1.x siblings (probe-par-03 context)
    if c['doc_id'].endswith('CIR/2025/101') and c['id'].split('#')[1].startswith('4.1.1'):
        ids.add(c['id'])
out = '/private/tmp/claude-501/-Users-ianpinto-sebi-circular-sota-rag-SEBI-circular-RAG/f852e1f2-7ea4-40ff-b185-9166f6902277/scratchpad/iv9-pilot-ids.txt'
open(out, 'w').write('\n'.join(sorted(ids)))
print(len(ids), 'pilot ids ->', out)
EOF
```

Expected: roughly 5–20 ids printed. If 0, stop — the discovery filter is wrong; debug before generating.

- [ ] **Step 3: Run the pilot with the 1.5B model (scratch output, not the real sidecar)**

```bash
PYTHONPATH=src HF_HUB_DISABLE_XET=1 .venv/bin/python scripts/generate_context_headers.py \
  --ids "/private/tmp/claude-501/-Users-ianpinto-sebi-circular-sota-rag-SEBI-circular-RAG/f852e1f2-7ea4-40ff-b185-9166f6902277/scratchpad/iv9-pilot-ids.txt" \
  --out "/private/tmp/claude-501/-Users-ianpinto-sebi-circular-sota-rag-SEBI-circular-RAG/f852e1f2-7ea4-40ff-b185-9166f6902277/scratchpad/iv9-pilot/headers-1.5b.jsonl"
cat "/private/tmp/claude-501/-Users-ianpinto-sebi-circular-sota-rag-SEBI-circular-RAG/f852e1f2-7ea4-40ff-b185-9166f6902277/scratchpad/iv9-pilot/headers-1.5b.jsonl"
```

- [ ] **Step 4: Judge the pilot against the spec's go/no-go criteria**

Inspect every generated header:
- CRA `4.1.1.x` chunks: winding-down/ceasing-operations phrasing present alongside surrender/cancellation vocabulary?
- probe-sup-04 chunk: describes a list of circulars withdrawn/rescinded?
- Zero markdown/boilerplate artifacts (no `**`, `#`, "Circular No.", dates)?

If the 1.5B fails: rerun Step 3 once with `--model mlx-community/Qwen2.5-7B-Instruct-4bit --out …/iv9-pilot/headers-7b.jsonl` and re-judge. If the 7B also fails: **STOP — report no-go to the user with the generated headers quoted; do not proceed to Task 3.**

- [ ] **Step 5: Commit the script (record the pilot verdict and chosen model in the commit message)**

```bash
git add scripts/generate_context_headers.py
git commit -m "feat: resumable context-header generation script (iv9) — pilot go with <model>"
```

---

### Task 3: index-merge wiring + full scoped generation

**Files:**
- Modify: `scripts/build_index.py:24-34` (imports + merge after `load_circulars`)
- Output (committed): `data/corpus/context_headers.jsonl` (~18.2k rows)

**Interfaces:**
- Consumes: `apply_context_headers(chunks, headers) -> list[Chunk]` and `load_headers(path) -> dict[str, str]` from Task 1; the Task 2 script CLI.
- Produces: an index build that automatically merges the sidecar; the committed sidecar Task 4 reindexes with.

- [ ] **Step 1: Wire the merge into `build_index.py`**

Add to the imports block (after the `from sebi_rag.corpus import load_circulars` line):

```python
from sebi_rag.context_headers import apply_context_headers, load_headers  # noqa: E402
```

And change the chunk-loading line

```python
chunks = load_circulars(CORPUS)
```

to:

```python
chunks = load_circulars(CORPUS)
# iv9: merge contextual headers (no-op when the sidecar is absent)
chunks = apply_context_headers(
    chunks, load_headers(ROOT / "data" / "corpus" / "context_headers.jsonl")
)
```

- [ ] **Step 2: Verify the wiring is a no-op without the sidecar**

Run: `make test`
Expected: 279 passed (the sidecar does not exist yet; `load_headers` returns `{}` and every chunk passes through unchanged).

```bash
git add scripts/build_index.py
git commit -m "feat: merge context-header sidecar into chunks at index build (iv9)"
```

- [ ] **Step 3: Run the full scoped generation (background, ~5–8 h)**

```bash
PYTHONPATH=src HF_HUB_DISABLE_XET=1 .venv/bin/python scripts/generate_context_headers.py \
  --model <model chosen by the Task 2 pilot>
```

Run in the background; the script prints progress + ETA every 100 chunks and is resumable if interrupted. On completion, sanity-check coverage and quality:

```bash
uv run python - <<'EOF'
import json
rows = [json.loads(l) for l in open('data/corpus/context_headers.jsonl')]
empty = sum(1 for r in rows if not r['header'].strip())
bad = sum(1 for r in rows if '**' in r['header'] or r['header'].startswith('#'))
print(f"rows={len(rows)} empty={empty} markdown_artifacts={bad}")
EOF
```

Expected: rows ≈ 18,196 (17,601 + 595), empty and markdown_artifacts both a small fraction (< 5%). A large empty count means generation failures — investigate before reindexing.

- [ ] **Step 4: Commit the sidecar**

```bash
git add data/corpus/context_headers.jsonl
git commit -m "data: contextual headers for deep+annex chunks (iv9, ~18.2k rows)"
```

---

### Task 4: reindex, iv9 measurement, report §5.4

**Files:**
- Output: rebuilt `data/index/`, new run dirs `eval/runs/iv9-probes/`, `eval/runs/iv9-golden/`
- Modify: `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md` (append §5.4 after §5.3)

**Interfaces:**
- Consumes: Task 3's committed sidecar and wiring; `make reindex`; `scripts/bench_retrieval.py --golden <jsonl> --out <dir>` (NO `--hyde`); `scripts/analysis/extract_misses.py --run <trec> --golden <jsonl> --out <jsonl> --source <label>`.
- Produces: the measured verdict against the spec's gates, recorded in report §5.4.

- [ ] **Step 1: Rebuild the index**

Run: `make reindex` (background; enriched docs re-embed — expect ~1–3 h on MPS).
Expected: completes without error. **Gate:** chunk count printed by the build must be exactly 77,859 (headers add text inside existing chunks, never chunks). Any delta = merge bug: stop and debug.

- [ ] **Step 2: Run both benchmarks (no `--hyde`) and classify misses**

```bash
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python scripts/bench_retrieval.py \
  --golden eval/probes/probes_v1.jsonl --out eval/runs/iv9-probes

HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python scripts/bench_retrieval.py \
  --golden eval/golden/golden_v6.jsonl --out eval/runs/iv9-golden

.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv9-probes/run.trec --golden eval/probes/probes_v1.jsonl \
  --out eval/runs/iv9-probes/failures.jsonl --source probes_v1

.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv9-golden/run.trec --golden eval/golden/golden_v6.jsonl \
  --out eval/runs/iv9-golden/failures.jsonl --source golden_v6
```

Expected gates (report actual numbers verbatim whether or not met):
- probes answer-level failures ≤ 3 (from 4) — probe-par-03 and probe-sup-04 are the targets;
- golden answer-level failures ≤ 3 and `recall_at_10` ≥ 0.956;
- no new failure IDs vs `eval/runs/iv7-*/failures.jsonl` (any new ID = stop and investigate before reporting).

- [ ] **Step 3: Full test suite**

Run: `make test`
Expected: 279 passed.

- [ ] **Step 4: Append §5.4 to the report**

Append to `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md`, directly after §5.3 (before `## Self-check vs spec success criteria`):

```markdown
### 5.4 Scoped contextual chunk headers (iv9, <date>)

Index-side enrichment: one lay+statutory sentence per deep sub-clause and
annex chunk (<model>, greedy, 80 tokens; <n> sidecar rows; commits
<sha-task1>..<sha-task3>). Pilot verdict: <go with 1.5B / escalated to 7B>,
sample header for `…CIR/2025/101#4.1.1.2`: "<the header>". Spec:
`docs/superpowers/specs/2026-07-19-contextual-headers-design.md`, plan:
`docs/superpowers/plans/2026-07-19-contextual-headers.md`.

| run | answerable | answer-level failures | doc recall@10 |
|---|---|---|---|
| probes prior (`iv7-probes`) | 25 | 4 | 1.0 |
| probes iv9 (`iv9-probes`) | 25 | <n> | <x> |
| golden prior (`iv7-golden`) | 45 | 2 | 0.956 |
| golden iv9 (`iv9-golden`) | 45 | <n> | <x> |

probe-par-03: candidate_miss → <class, arank>. probe-sup-04:
candidate_miss → <class, arank>. Chunk count: 77,859 (unchanged).
Regression check vs iv7: <none / list>. Gate verdict: <met / not met,
which>. <If not met: decision point — no silent iteration.>
```

Fill every `<…>` with measured values; keep only the applicable branches.

- [ ] **Step 5: Commit results**

```bash
git add docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md \
        eval/runs/iv9-probes eval/runs/iv9-golden
git commit -m "eval: scoped contextual-header results (iv9) + report update"
```

---

## Self-review notes

- Spec coverage: Component 1 → Task 1 (signatures, prompt with anti-boilerplate constraints, post-processing, silent failure, `load()`); Component 2 → Task 2 (CLI, resumability, `--ids`/`--limit`/`--model`, governing-clause derivation via `_HEAD` regex exactly as the spec fixed it); Component 3 → Task 3 (pure merge in `build_index.py`, no-op without sidecar); Pilot § → Task 2 Steps 2–4 with the STOP rule; Testing § → Task 1's eight tests (prompt contract, cleanup, failure, truncation, insertion, no-op, scope predicate, missing file); Measurement § → Task 4 (chunk-count gate, iv9 dirs, all gates, §5.4). Out-of-scope items have no tasks.
- Type consistency: `describe(subject, governing, chunk_text) -> str` matches the Task 2 call `gen.describe(c.meta.get("subject",""), governing, body)` (`Chunk.meta` is a dict built by `asdict(meta)` in `segment.py:126`, so `meta["subject"]` exists); `in_scope(c.id.split("#")[1])` matches the id format `doc#section#idx`; `load_headers` used in both the script (resume) and `build_index.py` (merge).
- The pilot writes to scratch outputs so the real sidecar only ever contains the accepted model's headers; the resume mechanism therefore never mixes rejected pilot rows into production data.
