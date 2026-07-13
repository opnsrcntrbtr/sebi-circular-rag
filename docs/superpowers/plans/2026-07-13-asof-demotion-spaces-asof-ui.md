# As-of/Demotion Fix + Spaces As-of UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make date-scoped ("as per circular dated …") questions answerable: fix the as-of/demotion double-penalty in `RAGPipeline.query`, make the supersession note per-citation-honest, expose an "As of date" field in the Spaces demo, and redeploy the stale Space.

**Architecture:** Two surgical changes to `src/sebi_rag/pipeline.py` (mutually-exclusive as-of vs. global demotion; note text filtered to circulars actually referenced in the answer), one UI pass-through in `app.py`, then a real-index validation gate and a scripted redeploy of `opnsrcntrbtrian/sebi-circular-rag-demo` (whose deployed `pipeline.py` is a stale revision missing the entire as-of branch).

**Tech Stack:** Python 3.12 via `uv`, pytest, Gradio, huggingface_hub, gradio_client.

## Global Constraints

- Run all Python through `uv run` (or `make` targets); never bare `python`.
- Offline test suite must stay green: `make test` (excludes integration tests).
- Heavy/real-index commands need env: `HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false PYTORCH_ENABLE_MPS_FALLBACK=1 OMP_NUM_THREADS=1` (the Makefile sets these for its targets).
- Do NOT touch `api_spaces.py`, `corpus_spaces.py`, `generate_spaces.py` — none of the fixes live there. `pipeline.py` and `app.py` are shared/Spaces-entry files and are in scope.
- Do NOT rebuild or re-upload the index/dataset repos (`sebi-circulars-index`, `sebi-circulars`) — the index is already correct (34,883 chunks, post-chunker-fix); only Space *code* is stale.
- Commit after each task; conventional-commit style (`fix:`, `feat:`, `docs:`); end commit bodies with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Working branch: `spaces` (current branch; do not branch off main).
- After code changes, run `graphify update .` once at the end (AST-only) to keep the knowledge graph current.

## Background (evidence from the 2026-07-13 debug session)

Question: *"What is the maximum number of nominations accepted for a mutual fund folio as per circular data January 10, 2025?"* Correct answer: **10** per `SEBI/HO/OIAE/OIAE_IAD-3/P/ON/2025/01650` §3.2 (superseded today; "3" per `SEBI/HO/OIAE/OIAE_IAD-3/P/CIR/2026/12676` is current law).

Measured on the real index: reranker puts 01650 at rank 2 (score 0.617); `demote_superseded` (penalty 0.3) drops it to rank 8 (0.185). `pipeline.query(..., as_of="2025-01-10")` **abstains** because the as-of branch runs on *already-demoted* scores: 01650 survives the date filter as the governing circular but at 0.185 < 0.40 abstention floor. Separately, `answer_with_abstention` sets `citations = [c.id for c in contexts]`, so at top_k ≥ 8 the demoted 01650 chunks re-enter as citations and the supersession note fires naming a circular the answer text never used.

---

### Task 1: as-of queries must score against undemoted reranker scores

**Files:**
- Modify: `src/sebi_rag/pipeline.py:46-61` (the demotion + as_of block in `query`)
- Test: `tests/test_pipeline.py` (append)

**Interfaces:**
- Consumes: `demote_superseded(reranked, lineage, penalty)` and `Lineage.governing_on(cn, as_of, issue_dates)` from `src/sebi_rag/lineage.py` (unchanged).
- Produces: `RAGPipeline.query(question, pool=50, top_k=3, advisory=False, as_of=None)` — signature unchanged; behavior change only: when `as_of` is set, global supersession demotion is skipped and as-of governance is applied to the raw reranked scores.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_pipeline.py` (it already imports `RAGPipeline`, `ExtractiveStubGenerator`, `HashEmbedder`, `CircularMeta`, `hierarchical_chunk`, `build_lineage`):

```python
class _FixedReranker:
    """Deterministic reranker: score by doc_id lookup (test-only)."""

    def __init__(self, scores):
        self.scores = scores

    def rerank(self, query, chunks):
        out = [(c, self.scores.get(c.doc_id, 0.0)) for c in chunks]
        out.sort(key=lambda cs: -cs[1])
        return out


def test_as_of_query_not_demoted_below_abstention_floor():
    """A circular that governed on the as-of date must keep its raw rerank
    score. Bug: global demote_superseded ran first, so the then-governing
    (now-superseded) circular arrived at the as-of branch already at
    score*0.3 and fell under the abstention threshold (score_floor)."""
    OLD = "SEBI/HO/MRD/2020/010"
    NEW = "SEBI/HO/MRD/2023/050"
    old_text = ("Margin rules for the equity derivatives segment. Margin "
                "collection shall be on a T plus one basis.")
    new_text = (f"CIRCULAR {NEW}. This circular supersedes {OLD}. In "
                f"supersession of {OLD}, margin collection on a T plus zero "
                "basis.")
    chunks = hierarchical_chunk(
        old_text, CircularMeta(circular_number=OLD, issue_date="2020-01-01"))
    chunks += hierarchical_chunk(
        new_text, CircularMeta(circular_number=NEW, issue_date="2023-01-01"))
    lineage = build_lineage([
        {"circular_number": OLD, "issue_date": "2020-01-01", "text": old_text},
        {"circular_number": NEW, "issue_date": "2023-01-01", "text": new_text},
    ])
    pipe = RAGPipeline.build(
        chunks=chunks, embedder=HashEmbedder(256),
        reranker=_FixedReranker({OLD: 0.6, NEW: 0.9}),
        generator=ExtractiveStubGenerator(),
        abstain_threshold=0.40,  # production floor — this is the point
        lineage=lineage,
    )
    # On 2021-06-01, NEW does not exist yet and OLD governs: raw score 0.6
    # must survive (demoted 0.6*0.3=0.18 would abstain via score_floor).
    ans, _ = pipe.query("margin rules equity derivatives", as_of="2021-06-01")
    assert not ans.abstained, f"abstained: {ans.abstention_reason}"
    assert ans.citations and ans.citations[0].startswith(OLD)
    # Present-day query is untouched: demotion still prefers NEW.
    ans_now, _ = pipe.query("margin rules equity derivatives")
    assert not ans_now.abstained
    assert ans_now.citations[0].startswith(NEW)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_pipeline.py::test_as_of_query_not_demoted_below_abstention_floor -v`
Expected: FAIL on `assert not ans.abstained` with `abstained: score_floor`.

- [ ] **Step 3: Reorder demotion vs. as-of in `pipeline.query`**

In `src/sebi_rag/pipeline.py`, replace lines 48-61 (from `if self.lineage is not None:` through `reranked = kept or reranked`) with:

```python
        if as_of and self.lineage is not None:
            # As-of queries score against the law as it stood on `as_of`.
            # The global demotion below encodes *today's* in-force status
            # and would double-penalise the then-governing circular, so
            # as-of governance is applied to the raw reranked scores.
            dates = {c.doc_id: (c.meta.get("issue_date") or "")
                     for c, _ in reranked}
            kept = []
            for c, s in reranked:
                d = dates.get(c.doc_id, "")
                if d and d > as_of:
                    continue  # circular did not exist on the as-of date
                gov = self.lineage.governing_on(c.doc_id, as_of, dates)
                kept.append((c, s if gov == c.doc_id else s * self.superseded_penalty))
            kept.sort(key=lambda cs: -cs[1])
            reranked = kept or reranked
        elif self.lineage is not None:
            reranked = demote_superseded(reranked, self.lineage, self.superseded_penalty)
```

(Net change: the two blocks swap into an if/elif — demotion no longer runs before the as-of branch.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_pipeline.py -v`
Expected: all PASS, including the pre-existing `test_query_as_of_prefers_governing_circular` and `test_answer_flags_superseded_citation`.

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/pipeline.py tests/test_pipeline.py
git commit -m "fix(pipeline): as-of queries use undemoted rerank scores

demote_superseded encodes today's in-force status; running it before the
as-of branch double-penalised the circular that governed on the as-of date,
pushing it under the abstention floor (verified on the real index:
ON/2025/01650 at 0.617 raw -> 0.185 demoted < 0.40 threshold -> abstain).

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: supersession note only for circulars the answer actually references

**Files:**
- Modify: `src/sebi_rag/pipeline.py:66-78` (the note block in `query`; line numbers pre-Task-1 — locate by the `superseded_citations` call)
- Test: `tests/test_pipeline.py` (append)

**Interfaces:**
- Consumes: `superseded_citations(citations, lineage) -> dict[str, list[str]]` from `lineage.py` (unchanged); `Answer.text` / `Answer.superseded` from `generate.py`; the `_FixedReranker` test helper added to `tests/test_pipeline.py` by Task 1 (if Task 1 has not run yet, copy its class definition from Task 1 Step 1).
- Produces: `ans.superseded` still carries **all** flagged context circulars (UI table metadata unchanged); the appended "no longer in force" note names only circulars whose number appears in `ans.text`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_pipeline.py`. Add `Lineage` to the existing `from sebi_rag.lineage import build_lineage` import line (`from sebi_rag.lineage import Lineage, build_lineage`).

```python
def test_supersession_note_only_for_circulars_cited_in_answer_text():
    """citations = all top_k contexts, so a demoted superseded chunk deep in
    the context window used to trigger a note contradicting the in-force
    circular the answer text actually came from (Space bug at top_k >= 8)."""
    OLD = "SEBI/HO/X/2020/01"
    NEW = "SEBI/HO/X/2024/09"
    # NEW's text must NOT mention OLD, so lineage is built directly.
    lineage = Lineage(supersedes={NEW: [OLD]}, superseded_by={OLD: [NEW]})
    chunks = hierarchical_chunk(
        "Margin rules prescribe collection on a T plus one basis.",
        CircularMeta(circular_number=OLD, issue_date="2020-01-01"))
    chunks += hierarchical_chunk(
        "Revised margin rules prescribe collection on a T plus zero basis.",
        CircularMeta(circular_number=NEW, issue_date="2024-01-01"))
    pipe = RAGPipeline.build(
        chunks=chunks, embedder=HashEmbedder(256),
        reranker=_FixedReranker({NEW: 0.9, OLD: 0.8}),
        generator=ExtractiveStubGenerator(), abstain_threshold=0.05,
        lineage=lineage,
    )
    ans, _ = pipe.query("margin rules", top_k=2)
    assert not ans.abstained
    # OLD is in the context window -> metadata still flags it...
    assert ans.superseded == {OLD: [NEW]}
    # ...but the answer text (NEW's chunk) never references OLD, so no note.
    assert "no longer in force" not in ans.text


def test_supersession_note_kept_when_answer_text_cites_superseded():
    OLD = "SEBI/HO/X/2020/01"
    NEW = "SEBI/HO/X/2024/09"
    lineage = Lineage(supersedes={NEW: [OLD]}, superseded_by={OLD: [NEW]})
    chunks = hierarchical_chunk(
        "Margin rules prescribe collection on a T plus one basis.",
        CircularMeta(circular_number=OLD, issue_date="2020-01-01"))

    class _CitesOld:
        def generate(self, query, contexts):
            return f"Per {OLD}, margin collection is on a T plus one basis."

    pipe = RAGPipeline.build(
        chunks=chunks, embedder=HashEmbedder(256),
        reranker=_FixedReranker({OLD: 0.8}),
        generator=_CitesOld(), abstain_threshold=0.05, lineage=lineage,
    )
    ans, _ = pipe.query("margin rules", top_k=1)
    assert not ans.abstained
    assert ans.superseded == {OLD: [NEW]}
    assert "no longer in force" in ans.text and NEW in ans.text
```

- [ ] **Step 2: Run tests to verify the first fails**

Run: `uv run pytest tests/test_pipeline.py -k supersession_note -v`
Expected: `test_supersession_note_only_for_circulars_cited_in_answer_text` FAILS on `"no longer in force" not in ans.text`; the `_kept_` test PASSES already (guards against over-fixing).

- [ ] **Step 3: Filter the note to circulars present in the answer text**

In `src/sebi_rag/pipeline.py`, replace the note block:

```python
        if self.lineage is not None and not ans.abstained and ans.citations:
            flagged = superseded_citations(ans.citations, self.lineage)
            if flagged:
                ans.superseded = flagged  # full metadata: every flagged context
                cited_in_text = {old: new for old, new in flagged.items()
                                 if old in ans.text}
                if cited_in_text:
                    notes = "; ".join(
                        f"{old} has been superseded by {', '.join(new)}"
                        for old, new in cited_in_text.items()
                    )
                    ans.text += (
                        f"\n\nNote: this answer cites circular(s) that are no longer in "
                        f"force — {notes}. Refer to the superseding circular(s) for "
                        "current requirements."
                    )
```

- [ ] **Step 4: Run the full offline suite**

Run: `make test`
Expected: all PASS (in particular `test_answer_flags_superseded_citation` still passes — its extractive answer text contains the superseded number).

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/pipeline.py tests/test_pipeline.py
git commit -m "fix(pipeline): supersession note only names circulars in answer text

citations include every top_k context, so at top_k>=8 a demoted superseded
chunk triggered a note contradicting the in-force circular the answer came
from. ans.superseded keeps full context metadata for the UI table.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: "As of date" field in the Spaces UI

**Files:**
- Modify: `app.py` (`run_query_spaces`, `build_ui`)
- Test: Create `tests/test_app_asof.py`

**Interfaces:**
- Consumes: `RAGPipeline.query(..., as_of: str | None)` from Task 1.
- Produces: module-level `app._parse_as_of(raw: str) -> str | None` (raises `ValueError` on non-ISO input); `run_query_spaces(question, top_k, mode, as_of_raw="")` — new trailing arg, wired to a `gr.Textbox` in the Settings accordion.

- [ ] **Step 1: Write the failing test**

Create `tests/test_app_asof.py`, reusing the `spaces`-stub import pattern from `tests/test_app_zerogpu.py` (that file injects a fake `spaces` module into `sys.modules` before importing `app`; copy its `stub_spaces_module` fixture verbatim or import the module the same way):

```python
"""As-of date plumbing in the Spaces UI (app.py)."""
from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def app_module(monkeypatch):
    fake = types.ModuleType("spaces")
    fake.GPU = lambda fn: fn
    monkeypatch.setitem(sys.modules, "spaces", fake)
    monkeypatch.syspath_prepend(str(ROOT))
    sys.modules.pop("app", None)
    return importlib.import_module("app")


def test_parse_as_of_accepts_iso_and_empty(app_module):
    assert app_module._parse_as_of("2025-01-10") == "2025-01-10"
    assert app_module._parse_as_of("  2025-01-10  ") == "2025-01-10"
    assert app_module._parse_as_of("") is None
    assert app_module._parse_as_of("   ") is None


def test_parse_as_of_rejects_garbage(app_module):
    with pytest.raises(ValueError):
        app_module._parse_as_of("January 10, 2025")
    with pytest.raises(ValueError):
        app_module._parse_as_of("2025-13-45")


def test_run_query_rejects_bad_as_of_before_building_pipeline(app_module):
    # Must error out on the date BEFORE get_pipeline() (no index download).
    out = app_module.run_query_spaces("what are the norms?", 3, "rag", "not-a-date")
    assert out[0].startswith("**Error:**") and "YYYY-MM-DD" in out[0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_app_asof.py -v`
Expected: FAIL with `AttributeError: module 'app' has no attribute '_parse_as_of'`.

- [ ] **Step 3: Implement in `app.py`**

Add after the `get_pipeline` function:

```python
def _parse_as_of(raw: str) -> str | None:
    """Normalise the optional as-of date field: empty -> None, else strict
    ISO YYYY-MM-DD (ValueError propagates for anything else)."""
    raw = (raw or "").strip()
    if not raw:
        return None
    from datetime import date

    return date.fromisoformat(raw).isoformat()
```

Change `run_query_spaces` — new signature and the date check placed before `get_pipeline` so bad input never triggers the multi-minute pipeline build:

```python
def run_query_spaces(question: str, top_k: float, mode: str, as_of_raw: str = ""):
    empty_df = pd.DataFrame(columns=["Circular", "Status", "Superseded By"])
    if not question.strip():
        return "Please enter a question.", empty_df, "", "", "", "", ""
    try:
        as_of = _parse_as_of(as_of_raw)
    except ValueError:
        return (
            "**Error:** 'As of date' must be YYYY-MM-DD (e.g. 2025-01-10).",
            empty_df, "", "", "", "", "",
        )

    try:
        pipeline = get_pipeline(mode)
        t0 = time.perf_counter()
        ans, _retrieved = pipeline.query(
            question, top_k=int(top_k), advisory=False, as_of=as_of,
        )
        latency = f"{(time.perf_counter() - t0) * 1000:.0f} ms"
    except Exception as exc:  # noqa: BLE001 — surface, don't crash the Space
        return f"**Error:** {exc}", empty_df, "", "", "", "", ""
```

(The rest of the function body is unchanged.)

In `build_ui`, inside the Settings accordion after the `mode` radio, add:

```python
                    as_of_input = gr.Textbox(
                        label="As of date (optional)",
                        placeholder="YYYY-MM-DD — answer per the law in force on this date",
                        max_lines=1,
                    )
```

and extend the click wiring: `inputs=[question_input, top_k, mode, as_of_input],`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_app_asof.py tests/test_app_zerogpu.py -v`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_app_asof.py
git commit -m "feat(spaces): optional 'As of date' field for date-scoped questions

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: real-index validation gate (no code changes)

**Files:**
- None modified. Uses `data/index/` (34,883 chunks) and the golden as-of eval.

**Interfaces:**
- Consumes: Task 1's pipeline behavior; the persisted index at `data/index`.
- Produces: go/no-go evidence for the deploy in Task 5. If any check fails, STOP and report — do not deploy.

- [ ] **Step 1: Full offline suite**

Run: `make test`
Expected: all tests pass.

- [ ] **Step 2: Golden as-of eval**

Run: `make eval-asof`
Expected: all cases pass (13/13 as of the 2026-07-13 chunker-fix session). Selector cases must be unchanged; pipeline cases may only improve. Any regression vs. 13/13 = STOP.

- [ ] **Step 3: End-to-end nominee scenario against the real index**

Run (takes a few minutes; loads BGE-M3 + cross-encoder):

```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && \
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false PYTORCH_ENABLE_MPS_FALLBACK=1 \
OMP_NUM_THREADS=1 KMP_DUPLICATE_LIB_OK=TRUE uv run python - <<'EOF'
import faiss
faiss.omp_set_num_threads(1)
import sys
sys.path.insert(0, "src")
from sebi_rag.retrieve import HybridRetriever
from sebi_rag.embeddings import BGEM3Embedder
from sebi_rag.rerank import CrossEncoderReranker
from sebi_rag.lineage import Lineage
from sebi_rag.pipeline import RAGPipeline
from sebi_rag.generate import ExtractiveStubGenerator

q = ("What is the maximum number of nominations accepted for a mutual fund "
     "folio as per circular data January 10, 2025?")
pipe = RAGPipeline(
    retriever=HybridRetriever.load("data/index", BGEM3Embedder()),
    reranker=CrossEncoderReranker(),
    generator=ExtractiveStubGenerator(),
    lineage=Lineage.load("data/index/lineage.json"),
)

ans, _ = pipe.query(q, top_k=8, as_of="2025-01-10")
assert not ans.abstained, f"FAIL: abstained ({ans.abstention_reason})"
assert "up to 10" in ans.text, f"FAIL: expected 10-nominee text, got: {ans.text[:200]}"
assert any(c.startswith("SEBI/HO/OIAE/OIAE_IAD-3/P/ON/2025/01650") for c in ans.citations)
print("PASS as-of: 01650 / up to 10 persons")

ans2, _ = pipe.query(q, top_k=8)
assert not ans2.abstained
assert "up to 3 nominees" in ans2.text, f"FAIL: {ans2.text[:200]}"
assert "SEBI/HO/OIAE/OIAE_IAD-3/P/ON/2025/01650" in ans2.superseded  # metadata kept
assert "no longer in force" not in ans2.text, "note should not fire: answer text is 12676's"
print("PASS current-law: 12676 / up to 3 nominees, no misleading note")
EOF
```

Expected output: both `PASS` lines. (Baseline measured 2026-07-13 pre-fix: the as-of call abstains and the top_k=8 call appends the misleading 01650 note — both asserts flip with Tasks 1-2.)

- [ ] **Step 4: Record results**

Append a short "Validation" section (commands + pass/fail) to this plan file under a `## Validation Log` heading and commit:

```bash
git add docs/superpowers/plans/2026-07-13-asof-demotion-spaces-asof-ui.md
git commit -m "docs: record real-index validation results for as-of fixes

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: redeploy the Space and validate live

**Files:**
- Modify: `README-spaces.md` (document the As-of field in the "UI modes" section)
- Uses: `scripts/deploy_space.py` (unchanged)

**Interfaces:**
- Consumes: Tasks 1-4 complete and committed; HF auth for `opnsrcntrbtrian` (already logged in via huggingface_hub).
- Produces: live Space at `https://huggingface.co/spaces/opnsrcntrbtrian/sebi-circular-rag-demo` running current `pipeline.py`/`app.py`.

- [ ] **Step 1: Document the new field**

In `README-spaces.md`, in the "UI modes" section, append after the retrieval_only bullet:

```markdown
- **As of date (optional)** — YYYY-MM-DD; scores retrieval against the law
  in force on that date (circulars issued later are excluded; the circular
  governing on that date is not demoted for being superseded today).
```

Commit:

```bash
git add README-spaces.md
git commit -m "docs(spaces): document the As-of date field

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

- [ ] **Step 2: Deploy**

Run: `uv run python scripts/deploy_space.py --repo opnsrcntrbtrian/sebi-circular-rag-demo`
Expected: `deployed -> https://huggingface.co/spaces/opnsrcntrbtrian/sebi-circular-rag-demo`. A "could not set hardware" note is normal (ZeroGPU downgrade needs PRO; see README-spaces.md).

- [ ] **Step 3: Verify deployed files match local**

```bash
uv run python - <<'EOF'
from huggingface_hub import hf_hub_download
import pathlib
for f in ["app.py", "src/sebi_rag/pipeline.py"]:
    p = hf_hub_download("opnsrcntrbtrian/sebi-circular-rag-demo", f,
                        repo_type="space", force_download=True)
    same = pathlib.Path(p).read_text() == pathlib.Path(f).read_text()
    print(f, "IDENTICAL" if same else "DIFFERS -- STOP")
EOF
```

Expected: both `IDENTICAL`. (Pre-fix state: deployed `pipeline.py` was a stale revision with no as-of branch at all.)

- [ ] **Step 4: Live smoke test (wait for Space rebuild, then query)**

The Space rebuilds for a few minutes after the push; the first query then builds the pipeline in-process (several more minutes). Poll `runtime.stage` until RUNNING, then query with a generous timeout:

```bash
uv run python - <<'EOF'
import time
from huggingface_hub import HfApi
api = HfApi()
for _ in range(60):
    stage = api.get_space_runtime("opnsrcntrbtrian/sebi-circular-rag-demo").stage
    print("stage:", stage)
    if stage == "RUNNING":
        break
    time.sleep(30)

from gradio_client import Client
c = Client("opnsrcntrbtrian/sebi-circular-rag-demo")
q = ("What is the maximum number of nominations accepted for a mutual fund "
     "folio as per circular data January 10, 2025?")
out = c.predict(q, 8, "retrieval_only", "2025-01-10", api_name=None)
answer = out[0]
print(answer[:400])
assert "up to 10" in answer, "FAIL: live as-of answer wrong"
out2 = c.predict(q, 8, "retrieval_only", "", api_name=None)
assert "up to 3 nominees" in out2[0], "FAIL: live current-law answer wrong"
assert "no longer in force" not in out2[0], "FAIL: misleading note still fires"
print("LIVE SMOKE TEST PASSED")
EOF
```

Expected: `LIVE SMOKE TEST PASSED`. Note: if `api_name=None` fails, run `Client(...).view_api()` and use the listed endpoint name for the submit button's function. If the first predict times out because the pipeline is still building, retry after 5 minutes before declaring failure.

- [ ] **Step 5: Rollback plan (only on live failure)**

If the smoke test fails for a code reason (not a cold-start timeout), the pre-push Space revision can be restored: `HfApi().list_repo_commits("opnsrcntrbtrian/sebi-circular-rag-demo", repo_type="space")`, then re-upload the prior revision's files. Report the failure rather than iterating blind fixes on the live Space.

- [ ] **Step 6: Final bookkeeping**

Run `graphify update .` and commit any graph changes:

```bash
graphify update . && git add graphify-out && git commit -m "chore: graphify update after as-of fixes

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" || true
```
