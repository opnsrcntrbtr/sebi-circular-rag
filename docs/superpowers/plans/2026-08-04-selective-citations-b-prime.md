# Selective Citations B′ Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cite only the contexts an answer rests on, by scoring each context's answer-relevance with the pipeline's existing cross-encoder and keeping those within a margin of the top (always ≥1), so eval and production measure the same citation behavior.

**Architecture:** A pure `select_citations()` reuses the `Reranker` protocol (`scorer.rerank(answer_text, contexts)`) to score answer-relevance. `answer_with_abstention()` gains an optional `citation_scorer`; when set it filters citations, replacing the inert Option A bracket-parse. `RAGPipeline` passes its own reranker when `selective_citations` is on (off by default, env-gated). The gate re-arm adds a `citation_precision` floor.

**Tech Stack:** Python 3.12, pytest, sentence-transformers CrossEncoder (bge-reranker-v2-m3), existing `LexicalReranker` for deterministic tests.

## Global Constraints

- NEVER add fields to `CircularMeta` (`segment.py`) — additive metadata goes on corpus JSONL only.
- NEVER edit `*_spaces.py` / root `app.py` (CPU-only HF demo path).
- Reuse the existing cross-encoder — no new model or dependency.
- Offline suite (`pytest -q -m "not integration"`, currently 654 passed) must stay green.
- Citation margin is on the **sigmoid 0–1 score scale** (same as `abstain_threshold` 0.4 / `score_floor` 0.05), NOT raw logits.
- Env guards for any script touching models: `TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 PYTORCH_ENABLE_MPS_FALLBACK=1 HF_HUB_DISABLE_XET=1 PYTHONPATH=src`.
- Feature ships OFF by default (`selective_citations=False`); enabled in eval/prod only after the gate re-arms.

---

## Task 1: `select_citations()` pure function

**Files:**
- Modify: `src/sebi_rag/generate.py` (add near `faithfulness`, ~line 71)
- Test: `tests/test_selective_citations.py` (create)

**Interfaces:**
- Consumes: `Reranker` protocol (`rerank(query, candidates) -> list[tuple[Chunk, float]]`, sorted desc), `Chunk(id, doc_id, section, text, meta)`.
- Produces: `_CITATION_MARGIN_DEFAULT: float = 0.15`; `select_citations(answer_text: str, contexts: list[Chunk], scorer: Reranker, margin: float = _CITATION_MARGIN_DEFAULT) -> list[str]`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_selective_citations.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sebi_rag.segment import Chunk  # noqa: E402
from sebi_rag.generate import select_citations, _CITATION_MARGIN_DEFAULT  # noqa: E402


def _chunk(cid: str, text: str = "x") -> Chunk:
    return Chunk(id=cid, doc_id=cid.split("#")[0], section="s", text=text)


class _FakeReranker:
    """Deterministic scorer: returns preset answer-relevance scores, sorted desc."""
    def __init__(self, scores: dict[str, float]):
        self._scores = scores

    def rerank(self, query, candidates):
        paired = [(c, self._scores[c.id]) for c in candidates]
        paired.sort(key=lambda cs: -cs[1])
        return paired


def test_keeps_only_contexts_within_margin_of_top():
    ctx = [_chunk("A"), _chunk("B"), _chunk("C")]
    scorer = _FakeReranker({"A": 0.90, "B": 0.80, "C": 0.40})
    # margin 0.15: keep >= 0.75 -> A, B; drop C
    assert select_citations("ans", ctx, scorer, margin=0.15) == ["A", "B"]


def test_always_keeps_at_least_one_when_all_below_margin():
    ctx = [_chunk("A"), _chunk("B")]
    scorer = _FakeReranker({"A": 0.90, "B": 0.10})
    # margin 0.05: only A within margin of itself -> exactly the top
    assert select_citations("ans", ctx, scorer, margin=0.05) == ["A"]


def test_empty_contexts_returns_empty():
    assert select_citations("ans", [], _FakeReranker({}), margin=0.15) == []


def test_returns_ids_in_original_context_order_not_score_order():
    ctx = [_chunk("A"), _chunk("B"), _chunk("C")]
    scorer = _FakeReranker({"A": 0.80, "B": 0.95, "C": 0.85})  # score order B,C,A
    # all within 0.15 of top (0.95): keep all, but in context order A,B,C
    assert select_citations("ans", ctx, scorer, margin=0.15) == ["A", "B", "C"]


def test_default_margin_is_sigmoid_scale():
    assert 0.0 < _CITATION_MARGIN_DEFAULT < 1.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=src python -m pytest tests/test_selective_citations.py -q`
Expected: FAIL — `ImportError: cannot import name 'select_citations'`.

- [ ] **Step 3: Write minimal implementation**

Add to `src/sebi_rag/generate.py` (after `faithfulness`, before `@dataclass class Answer`):

```python
# Sigmoid-scale margin (same scale as abstain_threshold 0.4 / score_floor 0.05),
# NOT raw logits. Provisional; finalized by scripts/calibrate.py sweep.
_CITATION_MARGIN_DEFAULT = 0.15


def select_citations(answer_text: str, contexts: list["Chunk"],
                     scorer: "Reranker",
                     margin: float = _CITATION_MARGIN_DEFAULT) -> list[str]:
    """Context ids the answer rests on. Scores each context's answer-relevance
    via `scorer.rerank(answer_text, contexts)` (sigmoid 0-1), keeps those within
    `margin` of the top score, always keeps >=1 (the top) so a grounded answer
    never emits zero citations. Ids returned in the contexts' original order."""
    if not contexts:
        return []
    scored = scorer.rerank(answer_text, contexts)
    if not scored:
        return []
    top = scored[0][1]
    kept = [c for c, s in scored if s >= top - margin] or [scored[0][0]]
    order = {c.id: i for i, c in enumerate(contexts)}
    return sorted((c.id for c in kept), key=order.get)
```

`Reranker` and `Chunk` are already imported/defined in `generate.py` (Chunk at top import; Reranker is defined in `rerank.py` — import it: add `from .rerank import Reranker` is circular-risk, so annotate as a string/`Protocol` structural type. Use `"Reranker"` string annotation and do NOT import, since only `.rerank` is called duck-typed).

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=src python -m pytest tests/test_selective_citations.py -q`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/generate.py tests/test_selective_citations.py
git commit -m "feat(generate): select_citations post-hoc answer-relevance filter"
```

---

## Task 2: Integrate filter into `answer_with_abstention` (replace Option A)

**Files:**
- Modify: `src/sebi_rag/generate.py` — `answer_with_abstention` signature + the block at `generate.py:446-455`
- Test: `tests/test_selective_citations.py`

**Interfaces:**
- Consumes: `select_citations` (Task 1).
- Produces: `answer_with_abstention(query, reranked, generator, threshold, top_k=5, judge=None, advisory=False, citation_scorer=None, citation_margin=_CITATION_MARGIN_DEFAULT)`. When `citation_scorer` is None → `citations = [c.id for c in contexts]` (unchanged). When set → `citations = select_citations(text, contexts, citation_scorer, citation_margin)`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_selective_citations.py`:

```python
from sebi_rag.generate import answer_with_abstention, ExtractiveStubGenerator  # noqa: E402


def _reranked(chunks):
    return [(c, 0.9) for c in chunks]  # all above abstain threshold


def test_answer_with_scorer_filters_citations():
    ctx = [_chunk("A", "alpha text"), _chunk("B", "beta text"), _chunk("C", "gamma")]
    scorer = _FakeReranker({"A": 0.95, "B": 0.90, "C": 0.30})
    ans = answer_with_abstention(
        "q", _reranked(ctx), ExtractiveStubGenerator(), threshold=0.05, top_k=10,
        citation_scorer=scorer, citation_margin=0.15)
    assert ans.citations == ["A", "B"]           # C dropped (below margin)


def test_answer_without_scorer_cites_all_contexts_backward_compat():
    ctx = [_chunk("A"), _chunk("B"), _chunk("C")]
    ans = answer_with_abstention(
        "q", _reranked(ctx), ExtractiveStubGenerator(), threshold=0.05, top_k=10)
    assert set(ans.citations) == {"A", "B", "C"}  # unchanged default
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=src python -m pytest tests/test_selective_citations.py -q -k answer`
Expected: FAIL — `TypeError: answer_with_abstention() got an unexpected keyword argument 'citation_scorer'`.

- [ ] **Step 3: Write minimal implementation**

In `src/sebi_rag/generate.py`, update the signature (add two params at the end):

```python
def answer_with_abstention(
    query: str,
    reranked: list[tuple[Chunk, float]],
    generator: Generator,
    threshold: float,
    top_k: int = 5,
    judge: Judge | None = None,
    advisory: bool = False,
    citation_scorer: "Reranker | None" = None,
    citation_margin: float = _CITATION_MARGIN_DEFAULT,
) -> Answer:
```

Replace the Option A block (currently `generate.py:446-455`, from `# Parse LLM bracket citations...` through the `citations = sorted(...)` line) with:

```python
    if citation_scorer is not None:
        citations = select_citations(text, contexts, citation_scorer, citation_margin)
    else:
        citations = [c.id for c in contexts]
```

(The `_BRACKET`/`llm_cited`/`id_to_idx` lines are deleted — Option A is gone.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=src python -m pytest tests/test_selective_citations.py -q`
Expected: PASS (7 passed).

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/generate.py tests/test_selective_citations.py
git commit -m "feat(generate): wire citation filter into answer_with_abstention; drop inert Option A"
```

---

## Task 3: Revert `ExtractiveStubGenerator` to plain text

**Files:**
- Modify: `src/sebi_rag/generate.py:96-102` (`ExtractiveStubGenerator.generate`)
- Test: `tests/test_selective_citations.py`; fix any existing test asserting the bracketed stub output.

**Interfaces:**
- Produces: `ExtractiveStubGenerator.generate(query, contexts) -> contexts[0].text` (no brackets).

- [ ] **Step 1: Write the failing test**

Append to `tests/test_selective_citations.py`:

```python
def test_stub_generator_returns_plain_top_context_text():
    ctx = [_chunk("A", "alpha body"), _chunk("B", "beta body")]
    out = ExtractiveStubGenerator().generate("q", ctx)
    assert out == "alpha body"
    assert "[" not in out                      # no bracket citations
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/test_selective_citations.py::test_stub_generator_returns_plain_top_context_text -q`
Expected: FAIL — output is `"[A] [B] alpha body"`, assertion fails.

- [ ] **Step 3: Write minimal implementation**

Replace `ExtractiveStubGenerator.generate` body (`generate.py:96-102`) with:

```python
    def generate(self, query: str, contexts: list[Chunk]) -> str:
        if not contexts:
            return ABSTAIN
        return contexts[0].text
```

- [ ] **Step 4: Run the test, then find/fix any other test asserting the old bracketed stub**

Run: `PYTHONPATH=src python -m pytest tests/test_selective_citations.py -q` → PASS.
Then: `grep -rn "\[A\]\|\] \[\|f\"\[{c.id}\]\"" tests/` and `PYTHONPATH=src python -m pytest -q -m "not integration"`.
Any failure asserting stub text contained `[id]` brackets: update the expected string to the plain top-context text. Citation-count assertions are unaffected (Task 2 keeps all-contexts default when no scorer).
Expected: full suite green.

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/generate.py tests/
git commit -m "refactor(generate): stub returns plain top-context text (Option A removed)"
```

---

## Task 4: Wire filter into `RAGPipeline`

**Files:**
- Modify: `src/sebi_rag/pipeline.py` (dataclass fields + `query` at `pipeline.py:75`)
- Test: `tests/test_selective_citations.py`

**Interfaces:**
- Consumes: `answer_with_abstention(..., citation_scorer, citation_margin)` (Task 2).
- Produces: `RAGPipeline` fields `selective_citations: bool = False`, `citation_margin: float = _CITATION_MARGIN_DEFAULT`; `query` passes `citation_scorer=self.reranker if self.selective_citations else None, citation_margin=self.citation_margin`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_selective_citations.py`:

```python
from sebi_rag.pipeline import RAGPipeline  # noqa: E402


class _PassThroughRetriever:
    def __init__(self, chunks): self._chunks = chunks
    def retrieve(self, question, top_n=50): return [(c, 0.9) for c in self._chunks]


def test_pipeline_selective_citations_filters_end_to_end():
    ctx = [_chunk("A", "alpha"), _chunk("B", "beta"), _chunk("C", "gamma")]
    scorer = _FakeReranker({"A": 0.95, "B": 0.90, "C": 0.20})
    pipe = RAGPipeline(
        retriever=_PassThroughRetriever(ctx), reranker=scorer,
        generator=ExtractiveStubGenerator(), abstain_threshold=0.05,
        selective_citations=True, citation_margin=0.15)
    ans, _ = pipe.query("q", top_k=10)
    assert ans.citations == ["A", "B"]           # C dropped


def test_pipeline_default_cites_all_contexts():
    ctx = [_chunk("A", "alpha"), _chunk("B", "beta")]
    scorer = _FakeReranker({"A": 0.95, "B": 0.90})
    pipe = RAGPipeline(retriever=_PassThroughRetriever(ctx), reranker=scorer,
                       generator=ExtractiveStubGenerator(), abstain_threshold=0.05)
    ans, _ = pipe.query("q", top_k=10)
    assert set(ans.citations) == {"A", "B"}
```

Note: `_FakeReranker` here doubles as the pipeline reranker (its `rerank` is called both for retrieval reranking and, when selective, for answer-scoring — both duck-typed on `.rerank`). Scores are constant per id, so both uses are consistent.

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/test_selective_citations.py -q -k pipeline`
Expected: FAIL — `TypeError: __init__() got an unexpected keyword argument 'selective_citations'`.

- [ ] **Step 3: Write minimal implementation**

In `src/sebi_rag/pipeline.py`, add fields to the `RAGPipeline` dataclass (after `regulatory_index`):

```python
    selective_citations: bool = False   # B′: cite only answer-relevant contexts
    citation_margin: float = _CITATION_MARGIN_DEFAULT
```

Add the import at top: `from .generate import Answer, Generator, Judge, _BRACKET, _CITATION_MARGIN_DEFAULT, answer_with_abstention`.

In `query`, change the `answer_with_abstention(...)` call (`pipeline.py:75`) to:

```python
        ans = answer_with_abstention(
            question, reranked, self.generator, self.abstain_threshold, top_k,
            judge=self.judge, advisory=advisory,
            citation_scorer=self.reranker if self.selective_citations else None,
            citation_margin=self.citation_margin,
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=src python -m pytest tests/test_selective_citations.py -q`
Expected: PASS. Then full suite: `PYTHONPATH=src python -m pytest -q -m "not integration"` → green.

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/pipeline.py tests/test_selective_citations.py
git commit -m "feat(pipeline): selective_citations flag wires reranker as citation scorer"
```

---

## Task 5: Settings + `build_default_pipeline` env wiring

**Files:**
- Modify: `src/sebi_rag/settings.py` (`Settings` dataclass + `load`)
- Modify: `src/sebi_rag/api.py` (`build_default_pipeline`, RAGPipeline construction ~`api.py:143`)
- Test: `tests/test_settings.py` (create or append if it exists)

**Interfaces:**
- Produces: `Settings.selective_citations: bool = False`, `Settings.citation_margin: float = 0.15`, parsed from `SEBI_RAG_SELECTIVE_CITATIONS` / `SEBI_RAG_CITATION_MARGIN`. `build_default_pipeline` passes both to `RAGPipeline`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_settings.py` (or append):

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sebi_rag.settings import Settings  # noqa: E402


def test_selective_citations_defaults_off(monkeypatch, tmp_path):
    monkeypatch.delenv("SEBI_RAG_SELECTIVE_CITATIONS", raising=False)
    monkeypatch.setenv("SEBI_RAG_CONFIG", str(tmp_path / "none.toml"))
    s = Settings.load()
    assert s.selective_citations is False
    assert 0.0 < s.citation_margin < 1.0


def test_selective_citations_env_on(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBI_RAG_CONFIG", str(tmp_path / "none.toml"))
    monkeypatch.setenv("SEBI_RAG_SELECTIVE_CITATIONS", "1")
    monkeypatch.setenv("SEBI_RAG_CITATION_MARGIN", "0.2")
    s = Settings.load()
    assert s.selective_citations is True
    assert s.citation_margin == 0.2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/test_settings.py -q`
Expected: FAIL — `AttributeError: 'Settings' object has no attribute 'selective_citations'`.

- [ ] **Step 3: Write minimal implementation**

In `src/sebi_rag/settings.py`, add fields to the `Settings` dataclass (after `rerank_backend`):

```python
    selective_citations: bool = False  # B′ post-hoc citation filter (off by default)
    citation_margin: float = 0.15      # sigmoid-scale keep-within-margin-of-top
```

In `Settings.load(...)`, add to the `cls(...)` call:

```python
            selective_citations=_as_bool(_get("selective_citations", False, "SEBI_RAG_", svc)),
            citation_margin=float(_get("citation_margin", 0.15, "SEBI_RAG_", svc)),
```

In `src/sebi_rag/api.py`, `build_default_pipeline` RAGPipeline construction (`api.py:143`), add:

```python
        selective_citations=s.selective_citations,
        citation_margin=s.citation_margin,
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=src python -m pytest tests/test_settings.py -q` → PASS.
Then: `PYTHONPATH=src python -m pytest -q -m "not integration"` → green.

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/settings.py src/sebi_rag/api.py tests/test_settings.py
git commit -m "feat(settings): SEBI_RAG_SELECTIVE_CITATIONS + SEBI_RAG_CITATION_MARGIN env wiring"
```

---

## Task 6: Gate — add `citation_precision` floor + enable selective in eval scripts

**Files:**
- Modify: `scripts/golden_v7/derive_thresholds.py` (`_GATED_METRICS`, `_FLOOR_NAMES`, pipeline construction)
- Modify: `scripts/eval_json.py` (pipeline construction)
- Test: `tests/test_golden_v7_gate.py` (append; create if absent)

**Interfaces:**
- Consumes: `derive_floors(per_query)` (`derive_thresholds.py:52`), `score.vectors` keys (`recall, citation_precision, citation_recall, abstention`).
- Produces: `_GATED_METRICS` includes `"citation_precision"`; `_FLOOR_NAMES["citation_precision"] = "citation_precision"`. Eval pipelines built with `selective_citations=True`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_golden_v7_gate.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from golden_v7.derive_thresholds import derive_floors  # noqa: E402


def test_derive_floors_gates_citation_precision():
    per_query = {
        "recall": [1.0, 1.0, 0.9],
        "citation_precision": [0.8, 0.9, 0.7],
        "citation_recall": [0.7, 0.8, 0.6],
        "abstention": [1.0, 1.0, 1.0],
    }
    floors = derive_floors(per_query)
    assert "citation_precision" in floors
    assert 0.0 <= floors["citation_precision"] <= 0.7  # bootstrap lower bound - cushion
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/test_golden_v7_gate.py::test_derive_floors_gates_citation_precision -q`
Expected: FAIL — `"citation_precision" not in floors`.

- [ ] **Step 3: Write minimal implementation**

In `scripts/golden_v7/derive_thresholds.py`:

```python
_GATED_METRICS = ("recall", "citation_precision", "citation_recall", "abstention")
_FLOOR_NAMES = {"recall": "recall_at_k", "citation_precision": "citation_precision",
                "citation_recall": "citation_recall", "abstention": "abstention_accuracy"}
```

Update the comment above `_GATED_METRICS` (currently says citation_precision is NOT floored) to: precision is now floored because B′ makes it a real, non-trivial signal; recall keeps its floor so the precision/recall rebalance stays bounded.

In `derive_thresholds.py` `main()`, set the eval pipeline to selective (after building `pipeline`, or in the constructor):

```python
    pipeline = RAGPipeline(
        retriever=retr, reranker=rer, generator=ExtractiveStubGenerator(),
        abstain_threshold=s.abstain_threshold, lineage=lin, judge=judge,
        selective_citations=s.selective_citations, citation_margin=s.citation_margin)
```

Do the identical change in `scripts/eval_json.py`'s `RAGPipeline(...)` construction so measurement and floor-derivation stay on the same semantics (`score.py` shared path already guarantees the rest).

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=src python -m pytest tests/test_golden_v7_gate.py -q` → PASS.
Then: `PYTHONPATH=src python -m pytest -q -m "not integration"` → green.

- [ ] **Step 5: Commit**

```bash
git add scripts/golden_v7/derive_thresholds.py scripts/eval_json.py tests/test_golden_v7_gate.py
git commit -m "feat(gate): floor citation_precision; run eval pipelines with selective citations"
```

---

## Task 7: Calibrate margin + re-arm gate (scripted verification — needs MPS + index)

**Files:**
- Modify: `scripts/calibrate.py` (add a citation-margin sweep mode) — OR run the ad-hoc sweep below
- Modify: `eval/golden/gate_v7.json` (regenerated by `make golden-v7-gate`)
- Modify: `docs/status.md` (record new floors + operating point)

This task is NOT an offline unit test — it runs the real cross-encoder over the golden set. Execute it deliberately, capture outputs, and STOP if citation_recall floor drops below a usable band (decide the band with the user before committing the re-armed gate).

- [ ] **Step 1: Sweep the margin on the golden set**

Enable B′ and sweep margins, measuring citation_precision/recall via the shared `score.py` path. Ad-hoc runner (scratchpad), reusing `eval_json`'s construction with `selective_citations=True` and varying `SEBI_RAG_CITATION_MARGIN` over e.g. `{0.05, 0.10, 0.15, 0.20, 0.30}`. Record per-margin `citation_precision` (mean) and `citation_recall` (mean) on the adjudicated subset.

Run (example):
```bash
for m in 0.05 0.10 0.15 0.20 0.30; do
  SEBI_RAG_SELECTIVE_CITATIONS=1 SEBI_RAG_CITATION_MARGIN=$m \
  TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 PYTORCH_ENABLE_MPS_FALLBACK=1 \
  HF_HUB_DISABLE_XET=1 PYTHONPATH=src .venv/bin/python scripts/eval_json.py; done
```
Expected: JSON lines with rising `citation_precision` and falling `citation_recall` as margin shrinks. Pick the margin that maximizes precision while keeping `citation_recall` in the agreed band. Update `_CITATION_MARGIN_DEFAULT` (generate.py) and `Settings.citation_margin` default to the chosen value; commit that one-line change with the sweep numbers in the message.

- [ ] **Step 2: Re-derive and re-arm the gate**

Run:
```bash
SEBI_RAG_SELECTIVE_CITATIONS=1 make golden-v7-gate
```
Expected: `eval/golden/gate_v7.json` gains a `citation_precision` floor; `citation_recall` floor drops but stays > 0; `recall_at_k`/`abstention_accuracy` ~unchanged. STOP and consult if `citation_recall` floor collapses.

- [ ] **Step 3: Verify the armed gate passes**

Run:
```bash
SEBI_RAG_SELECTIVE_CITATIONS=1 PYTHONPATH=src .venv/bin/python scripts/eval_json.py
```
Expected: `gate.floors_ok == true` with the new floors (including citation_precision). Also run `make eval-asof` (13/13) as a regression sanity check.

- [ ] **Step 4: Flip the default on + record**

Set `selective_citations = True` default in `config.toml [service]` (NOT the dataclass default — keep code off-by-default; config turns it on for this deployment). Update `docs/status.md` with: new floors, chosen margin, before/after citation_precision & citation_recall, and a note that Option A was removed and superseded by B′.

- [ ] **Step 5: Commit**

```bash
git add eval/golden/gate_v7.json config.toml docs/status.md
git commit -m "chore(gate): re-arm gate_v7 under selective citations; enable in service config"
```

---

## Self-Review

**Spec coverage:** select_citations (T1) ✓; answer_with_abstention integration + Option A removal (T2) ✓; stub revert (T3) ✓; RAGPipeline wiring (T4) ✓; Settings/api env (T5) ✓; citation_precision floor + eval-parity enable (T6) ✓; margin calibration + gate re-arm + docs (T7) ✓. `pipeline.py:_BRACKET.sub` deferred per spec — not a task (documented follow-up). Latency: no code, covered by design risk note.

**Placeholder scan:** none — every step has concrete code or exact commands.

**Type consistency:** `select_citations(answer_text, contexts, scorer, margin)` and `_CITATION_MARGIN_DEFAULT` used identically in T1/T2/T4/T5; `citation_scorer`/`citation_margin` param names consistent across generate.py and pipeline.py; `selective_citations`/`citation_margin` field names consistent across pipeline/Settings/api/derive_thresholds.

**Open dependency note:** `_BRACKET` import stays in `pipeline.py` for the (deferred) supersession text-scan; T4's import line keeps it. If a later cleanup removes the text-scan, drop `_BRACKET` then.
