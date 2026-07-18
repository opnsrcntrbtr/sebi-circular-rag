# HyDE Third-Leg Retrieval (Part B) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the probes answer-level gate (4 → ≤ 3) by adding a HyDE hypothetical-statutory-passage embedding as an additive third RRF leg, opt-in for evaluation only.

**Architecture:** New `src/sebi_rag/hyde.py` turns a query into a hypothetical SEBI-circular-style passage via an injected generation callable (MLX enters only through a `load()` factory). `HybridRetriever.retrieve()` gains an optional `hyde_text` parameter that dense-searches the passage and fuses it as a third RRF leg — `None`/`""` is byte-identical to today. `scripts/bench_retrieval.py --hyde` wraps the retriever, generates per query, and audits every passage to `hyde.jsonl`.

**Tech Stack:** Python 3.12 (uv-managed venv), pytest, mlx-lm (already a dependency — `MLXGenerator`/`MLXJudge` use it), Qwen2.5-1.5B-Instruct-4bit (already cached locally), existing benchmark scripts.

**Spec:** `docs/superpowers/specs/2026-07-18-hyde-third-leg-design.md` (approved).

## Global Constraints

- Eval-only opt-in: the live API path (`src/sebi_rag/api.py`) is untouched; HyDE activates only via `retrieve(hyde_text=…)` and the bench `--hyde` flag.
- Silent failure contract: any generation exception or empty/whitespace output → `""`, treated as no-HyDE.
- Tests are fully offline: fake callables only, no `mlx_lm` import at test time.
- Never overwrite existing run dirs (`ft-*`, `iv-final-*`, `iv2-*`, `iv6-*`, `iv7-*`); new runs go to `eval/runs/iv8-probes/` and `eval/runs/iv8-golden/`.
- `make test` green after every task (265 currently passing; 271 after Tasks 1–2's six new tests).
- After modifying source code, run `graphify update .` before committing (project rule).
- All commands run from repo root: `/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG`. Use `uv run python …` or `.venv/bin/python …` — bare `python` lacks the project deps.

---

### Task 1: `HydeExpander` module (TDD)

**Files:**
- Create: `src/sebi_rag/hyde.py`
- Test: `tests/test_hyde.py` (new file)

**Interfaces:**
- Consumes: nothing from this codebase at test time; `mlx_lm.load`/`mlx_lm.generate` inside `load()` only (same pattern as `MLXGenerator`, `src/sebi_rag/generate.py:265`).
- Produces: `HydeExpander(generate: Callable[[str], str], max_chars: int = 1200)` with `hypothesize(query: str) -> str` and `HydeExpander.load(model: str = "mlx-community/Qwen2.5-1.5B-Instruct-4bit", max_tokens: int = 150) -> HydeExpander`. Tasks 2–3 rely on `hypothesize` returning `""` on failure.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_hyde.py`:

```python
"""HyDE expander (Part B): query -> hypothetical statutory passage.

Offline only — generation is an injected callable; mlx_lm never loads here.
"""
from __future__ import annotations

from sebi_rag.hyde import HydeExpander


def test_prompt_contains_query_and_style_cue():
    seen: dict[str, str] = {}

    def fake(prompt: str) -> str:
        seen["prompt"] = prompt
        return "  The CRA shall not take any new clients.  "

    out = HydeExpander(fake).hypothesize(
        "can companies pull their rating assignments?"
    )
    assert "can companies pull their rating assignments?" in seen["prompt"]
    assert "SEBI circular" in seen["prompt"]
    assert out == "The CRA shall not take any new clients."


def test_generation_error_returns_empty():
    def boom(prompt: str) -> str:
        raise RuntimeError("mlx exploded")

    assert HydeExpander(boom).hypothesize("any query") == ""


def test_whitespace_output_returns_empty():
    assert HydeExpander(lambda p: "   \n ").hypothesize("any query") == ""


def test_output_truncated_to_max_chars():
    ex = HydeExpander(lambda p: "x" * 5000, max_chars=1200)
    assert len(ex.hypothesize("any query")) == 1200
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_hyde.py -v`
Expected: all 4 FAIL at import (`ModuleNotFoundError: No module named 'sebi_rag.hyde'`).

- [ ] **Step 3: Implement `hyde.py`**

Create `src/sebi_rag/hyde.py`:

```python
"""HyDE (Hypothetical Document Embeddings): query -> statutory passage.

Part B of the semantic-gap resolution (probe-par-03). The passage is
dense-searched as an additive third RRF leg — see
HybridRetriever.retrieve(hyde_text=...). Failure is silent by design: any
generation error or empty output yields "", which callers treat as no-HyDE.
"""
from __future__ import annotations

from typing import Callable

_PROMPT = (
    "Write a short passage in the style of a SEBI circular provision that "
    "would answer this question. Use formal regulatory vocabulary. "
    "Question: {query}"
)


class HydeExpander:
    def __init__(
        self, generate: Callable[[str], str], max_chars: int = 1200
    ) -> None:
        self._generate = generate
        self.max_chars = max_chars

    def hypothesize(self, query: str) -> str:
        try:
            out = self._generate(_PROMPT.format(query=query))
        except Exception:  # noqa: BLE001 — silent-failure contract (spec)
            return ""
        return (out or "").strip()[: self.max_chars]

    @classmethod
    def load(
        cls,
        model: str = "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
        max_tokens: int = 150,
    ) -> "HydeExpander":
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
```

- [ ] **Step 4: Run the tests to verify green**

Run: `uv run pytest tests/test_hyde.py -v`
Expected: 4 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/hyde.py tests/test_hyde.py
git commit -m "feat: HydeExpander — query to hypothetical statutory passage (Part B)"
```

---

### Task 2: `hyde_text` third leg in `HybridRetriever.retrieve` (TDD)

**Files:**
- Modify: `src/sebi_rag/retrieve.py:165-173` (the `retrieve` method)
- Test: `tests/test_hyde.py` (append wiring section)

**Interfaces:**
- Consumes: existing `DenseIndex.search(query: str, k: int)`, `SparseIndex.search(query: str, k: int)`, `rrf_fuse(legs, top_n)`, `expand_query(str) -> str` — all already used inside `retrieve`.
- Produces: `HybridRetriever.retrieve(query: str, k_dense: int = 50, k_sparse: int = 50, top_n: int = 50, hyde_text: str | None = None) -> list[tuple[Chunk, float]]`. Task 3 passes `hyde_text=h or None`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_hyde.py`:

```python
# --- wiring: hyde_text as an additive third RRF leg --------------------------

from sebi_rag.embeddings import HashEmbedder  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402
from sebi_rag.segment import Chunk  # noqa: E402


def _chunk(i: int, text: str) -> Chunk:
    return Chunk(id=f"DOC/{i}#s#0", doc_id=f"DOC/{i}",
                 section=f"DOC/{i}/s/p0", text=text)


_CORPUS = [
    _chunk(1, "The CRA shall not take any new clients or fresh mandates "
              "upon surrender of certificate of registration."),
    _chunk(2, "Settlement of trades occurs on a T plus one cycle."),
    _chunk(3, "Margin requirements for derivatives are specified in "
              "Annexure A of this circular."),
]


def _rank(results: list, cid: str) -> int:
    ids = [c.id for c, _ in results]
    return ids.index(cid)


def test_hyde_leg_improves_paraphrase_gap_rank():
    r = HybridRetriever.build(_CORPUS, HashEmbedder(dim=64))
    # query matches DOC/2 and DOC/3 lexically, DOC/1 not at all
    q = "settlement margin requirements for trades"
    hyde = ("Upon surrender of certificate of registration the CRA shall "
            "not take any new clients or fresh mandates.")
    without = r.retrieve(q, top_n=3)
    with_h = r.retrieve(q, top_n=3, hyde_text=hyde)
    assert _rank(with_h, "DOC/1#s#0") < _rank(without, "DOC/1#s#0"), (
        "hyde leg did not improve the paraphrase-gap chunk's rank"
    )


def test_none_and_empty_hyde_are_identical_to_baseline():
    r = HybridRetriever.build(_CORPUS, HashEmbedder(dim=64))
    q = "settlement of trades"
    base = [(c.id, s) for c, s in r.retrieve(q)]
    none_ = [(c.id, s) for c, s in r.retrieve(q, hyde_text=None)]
    empty = [(c.id, s) for c, s in r.retrieve(q, hyde_text="")]
    assert base == none_ == empty
```

- [ ] **Step 2: Run the tests to verify the new wiring test fails**

Run: `uv run pytest tests/test_hyde.py -v`
Expected: `test_hyde_leg_improves_paraphrase_gap_rank` FAILS with `TypeError: retrieve() got an unexpected keyword argument 'hyde_text'`. (`test_none_and_empty_hyde_are_identical_to_baseline` also fails with the same TypeError.) The 4 Task-1 tests PASS.

- [ ] **Step 3: Add the parameter and third leg**

In `src/sebi_rag/retrieve.py`, replace the `retrieve` method (currently lines 165-173):

```python
    def retrieve(
        self,
        query: str,
        k_dense: int = 50,
        k_sparse: int = 50,
        top_n: int = 50,
        hyde_text: str | None = None,
    ) -> list[tuple[Chunk, float]]:
        dense = self.dense.search(query, k_dense)
        # intervention #2: statutory-synonym expansion, sparse leg only —
        # BM25 misses lay vocabulary; dense keeps the raw query.
        sparse = self.sparse.search(expand_query(query), k_sparse)
        legs = [dense, sparse]
        if hyde_text:
            # intervention #5 (HyDE, Part B): hypothetical statutory passage
            # as an additive third dense leg; raw legs stay untouched.
            legs.append(self.dense.search(hyde_text, k_dense))
        fused = rrf_fuse(legs, top_n=top_n)
        return [(self.chunks[i], score) for i, score in fused]
```

- [ ] **Step 4: Run the tests to verify green**

Run: `uv run pytest tests/test_hyde.py -v`
Expected: all 6 PASS.

- [ ] **Step 5: Full test suite**

Run: `make test`
Expected: 271 passed (265 previous + 6 new), 0 failures — in particular `tests/test_expand.py` wiring tests still green (default path unchanged).

- [ ] **Step 6: Update the knowledge graph and commit**

```bash
graphify update .
git add src/sebi_rag/retrieve.py tests/test_hyde.py graphify-out
git commit -m "feat: hyde_text as additive third RRF leg in HybridRetriever.retrieve"
```

---

### Task 3: `--hyde` benchmark flag, iv8 measurement, report §5.3

**Files:**
- Modify: `scripts/bench_retrieval.py:60-134` (`main`)
- Output: new run dirs `eval/runs/iv8-probes/`, `eval/runs/iv8-golden/` (each containing `hyde.jsonl`)
- Modify: `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md` (append §5.3 after §5.2)

**Interfaces:**
- Consumes: `HydeExpander(generate, max_chars=1200)` / `HydeExpander.load()` / `.hypothesize(query) -> str` (Task 1); `retrieve(..., hyde_text: str | None = None)` (Task 2); `run_retrieval_benchmark` calls `pipeline.retriever.retrieve(item["query"], top_n=top_n)` duck-typed (`src/sebi_rag/benchmark.py:305`), and `RAGPipeline` is a mutable dataclass, so a wrapper can be assigned to `pipeline.retriever`.
- Produces: the measured verdict against the spec's gates, recorded in report §5.3.

- [ ] **Step 1: Add the `--hyde` flag and retriever wrapper**

In `scripts/bench_retrieval.py`, add the argument after the `--smoke` line (line 65):

```python
    ap.add_argument("--hyde", action="store_true")
```

Immediately after the `if args.smoke: … else: …` block finishes assigning `pipeline`/`models` (after line 113), insert:

```python
    hyde_log: dict[str, str] = {}
    if args.hyde:
        from sebi_rag.hyde import HydeExpander

        # --smoke stays offline: stub passage instead of loading MLX.
        expander = (
            HydeExpander(lambda p: "nomination of beneficiary provision")
            if args.smoke
            else HydeExpander.load()
        )

        class _HydeRetriever:
            def __init__(self, inner):
                self.inner = inner

            def retrieve(self, query: str, top_n: int = 50):
                h = expander.hypothesize(query)
                hyde_log[query] = h
                return self.inner.retrieve(query, top_n=top_n,
                                           hyde_text=h or None)

        pipeline.retriever = _HydeRetriever(pipeline.retriever)
```

Record the flag in metadata: change the `params={"top_n": args.top_n, "smoke": args.smoke}` line to:

```python
        params={"top_n": args.top_n, "smoke": args.smoke, "hyde": args.hyde},
```

And write the audit file after the `results.json` write (before the final `print`):

```python
    if args.hyde:
        with (out / "hyde.jsonl").open("w", encoding="utf-8") as f:
            for item in golden:
                f.write(json.dumps({
                    "id": item["id"],
                    "query": item["query"],
                    "hyde": hyde_log.get(item["query"], ""),
                }, ensure_ascii=False) + "\n")
```

- [ ] **Step 2: Offline smoke verification of the wiring**

```bash
uv run python scripts/bench_retrieval.py --smoke --hyde \
  --out /private/tmp/claude-501/-Users-ianpinto-sebi-circular-sota-rag-SEBI-circular-RAG/f852e1f2-7ea4-40ff-b185-9166f6902277/scratchpad/hyde-smoke
cat "/private/tmp/claude-501/-Users-ianpinto-sebi-circular-sota-rag-SEBI-circular-RAG/f852e1f2-7ea4-40ff-b185-9166f6902277/scratchpad/hyde-smoke/hyde.jsonl"
```

Expected: benchmark completes with `recall_at_10: 1.0` (smoke item), and `hyde.jsonl` contains one row with `"hyde": "nomination of beneficiary provision"`. No MLX load (instant).

- [ ] **Step 3: Full test suite, then commit the script change**

Run: `make test`
Expected: 271 passed.

```bash
git add scripts/bench_retrieval.py
git commit -m "feat: --hyde flag on retrieval benchmark (per-query HyDE leg + audit log)"
```

- [ ] **Step 4: Run iv8 benchmarks and classify misses**

Background this — the non-smoke path loads bge-m3 + MLX and generates 25 + 56 passages (expect ~10–20 min):

```bash
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python scripts/bench_retrieval.py --hyde \
  --golden eval/probes/probes_v1.jsonl --out eval/runs/iv8-probes

HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python scripts/bench_retrieval.py --hyde \
  --golden eval/golden/golden_v6.jsonl --out eval/runs/iv8-golden

.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv8-probes/run.trec --golden eval/probes/probes_v1.jsonl \
  --out eval/runs/iv8-probes/failures.jsonl --source probes_v1

.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv8-golden/run.trec --golden eval/golden/golden_v6.jsonl \
  --out eval/runs/iv8-golden/failures.jsonl --source golden_v6
```

Expected gates (report actual numbers verbatim whether or not met):
- probes answer-level failures (`answer_candidate_miss + answer_ranked_low`) ≤ 3 (from 4) — probe-par-03 is the target;
- golden answer-level failures ≤ 3 and `recall_at_10` ≥ 0.956;
- no new failure IDs vs `eval/runs/iv7-*/failures.jsonl` on either set (RRF re-ranks everything — verify, don't assume; any new ID = stop and investigate before reporting).

Also spot-check `eval/runs/iv8-probes/hyde.jsonl` for the probe-par-03 row: the generated passage should use statutory vocabulary (surrender / cancellation / withdraw). Quote it in the report.

- [ ] **Step 5: Append §5.3 to the report**

Append to `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md`, directly after §5.2 (before `## Self-check vs spec success criteria`):

```markdown
### 5.3 HyDE third-leg retrieval (iv8, 2026-07-18)

Part B: hypothetical statutory passages (Qwen2.5-1.5B-4bit MLX, greedy,
150 tokens) dense-searched as an additive third RRF leg, eval-only
(`--hyde`; commits <sha-task1>, <sha-task2>, <sha-task3>). Index unchanged
from iv6. Spec: `docs/superpowers/specs/2026-07-18-hyde-third-leg-design.md`,
plan: `docs/superpowers/plans/2026-07-18-hyde-third-leg.md`.

| run | answerable | answer-level failures | doc recall@10 |
|---|---|---|---|
| probes prior (`iv7-probes`) | 25 | 4 | 1.0 |
| probes iv8 (`iv8-probes`) | 25 | <n> | <x> |
| golden prior (`iv7-golden`) | 45 | 2 | 0.956 |
| golden iv8 (`iv8-golden`) | 45 | <n> | <x> |

probe-par-03: candidate_miss → <new class, first_answer_rank>. Generated
passage (hyde.jsonl): "<first ~150 chars of the probe-par-03 passage>".
Regression check vs iv7: <none / list of new failure IDs>.
Gate verdict: <met / not met, which gates>. <If met: API/Settings wiring is
the designed follow-on. If not met: decision point per the spec — remaining
options are SPLADE and contextual headers (report §4); no silent iteration.>
```

Fill every `<…>` with measured values; keep only the applicable branch of the final sentence.

- [ ] **Step 6: Commit results**

```bash
git add docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md \
        eval/runs/iv8-probes eval/runs/iv8-golden
git commit -m "eval: HyDE third-leg results (iv8) + report update"
```

---

## Self-review notes

- Spec coverage: Component 1 → Task 1 (class, prompt, silent-failure, `load()` mirroring `MLXGenerator`'s `_gen(m, tok, prompt=…, max_tokens=…, verbose=False)` pattern); Component 2 → Task 2 (exact signature, empty-string-as-None, byte-identical default pinned); Component 3 → Task 3 Step 1 (flag, wrapper via mutable `RAGPipeline.retriever`, `hyde.jsonl`, params metadata); Testing § → Tasks 1–2 tests (prompt contract, error/empty/truncation, rescue-by-rank-improvement, None/"" pin); Measurement § → Task 3 Steps 4–6 (iv8 dirs, all gates incl. no-new-IDs vs iv7, §5.3 verbatim + decision-point sentence). Out-of-scope items have no tasks, as specified.
- Type consistency: `hypothesize(query: str) -> str` used in Task 3's wrapper; `hyde_text: str | None` matches `h or None`; `_HydeRetriever.retrieve(query, top_n=50)` matches the duck-typed call in `benchmark.py:305` (`retrieve(item["query"], top_n=top_n)`).
- The rescue test asserts rank *improvement* rather than absolute top-1 — robust to HashEmbedder's arbitrary dense ordering for non-matching queries.
