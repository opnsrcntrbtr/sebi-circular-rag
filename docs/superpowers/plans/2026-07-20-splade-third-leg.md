# SPLADE Learned-Sparse Third RRF Leg (iv11) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an opt-in, non-destructive SPLADE learned-sparse leg to hybrid retrieval, fused at RRF alongside dense+BM25, and A/B-measure it against the current 2-leg control.

**Architecture:** A new `SpladeIndex` (dependency-injected encoder, scipy-CSR doc matrix) mirrors `SparseIndex`'s `(idx, score)` interface and is fused as a third ranking by the existing `rrf_fuse`. It never touches `dense.faiss` or the BM25 index, so A (2-leg) is reproducible on demand by leaving the leg off — no snapshot/restore needed. The doc matrix is built once by a standalone script (~3.5h MPS encode, pilot-gated) and persisted as a separate artifact.

**Tech Stack:** `prithivida/Splade_PP_en_v1` (Apache-2.0 MLM), transformers 5.14.1, torch 2.13.0 (MPS), scipy 1.18.0 sparse — all already installed, no new dependency.

## Global Constraints

- Model: `prithivida/Splade_PP_en_v1`, **Apache-2.0** (verify in Task 1 Step 1 before any other work).
- **No new pip dependency** — scipy, transformers, torch are already in the lockfile.
- MPS encode always sets `PYTORCH_ENABLE_MPS_FALLBACK=1` (and the repo's usual `TOKENIZERS_PARALLELISM=false`, `HF_HUB_DISABLE_XET=1`).
- SPLADE doc matrix rows are positional and **must align 1:1 with `data/index/chunks.jsonl` order** — RRF fuses on integer `idx` and `self.chunks[i]` must line up across all three legs.
- Persisted doc count **must equal the dense index's `n=77859`**; a mismatch aborts the load rather than silently mis-fusing.
- SPLADE is **strictly opt-in and additive**: with the leg off/absent, `retrieve()` is byte-identical to today.
- SPLADE receives the **raw query** — no `expand_query` glossary (that stays BM25-only); SPLADE does its own learned expansion.
- **Eval-only this cycle** — no API/Settings/pipeline default wiring.
- All unit tests run **offline** (no MPS, no model download) via an injected fake encoder — same DI pattern as iv10's `HeaderGenerator(fake)` and iv8's `HydeExpander(lambda ...)`.
- SPLADE-leg failures (missing artifact, encode error, `n` mismatch) **raise loudly** — never a silent 2-leg fallback (the opposite of the header generator's silent-empty contract).

---

### Task 1: `SpladeIndex` core — CSR doc matrix, search, persistence, load guard

**Files:**
- Create: `src/sebi_rag/splade.py`
- Test: `tests/test_splade.py`

**Interfaces:**
- Consumes: nothing from earlier tasks; `scipy.sparse.csr_matrix`.
- Produces:
  - `SpladeIndex(encode: Callable[[list[str]], csr_matrix], vocab_size: int)`
  - `.build(texts: list[str]) -> None` — sets `self.matrix` (shape `(len(texts), vocab_size)`, CSR).
  - `.search(query: str, k: int) -> list[tuple[int, float]]` — top-k `(idx, score)`, score-descending.
  - `.save(path: str | Path, model: str) -> None` — writes `splade.npz` + `splade_meta.json`.
  - `SpladeIndex.load(path, encode, expected_n: int) -> SpladeIndex` — classmethod; raises `ValueError` if stored row count != `expected_n`.

- [ ] **Step 1: Verify the model license before building anything on it**

Run:
```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && \
.venv/bin/python -c "from huggingface_hub import model_info; print(model_info('prithivida/Splade_PP_en_v1').cardData.get('license'))"
```
Expected: prints `apache-2.0`. If it prints anything else, STOP and raise with the user — the spec's license decision is invalidated. (If offline and the call fails, note it and confirm the license from the model card manually before proceeding.)

- [ ] **Step 2: Write the failing test for `build` + `search` with an injected fake encoder**

```python
# tests/test_splade.py
from __future__ import annotations

import numpy as np
from scipy.sparse import csr_matrix

from sebi_rag.splade import SpladeIndex

VOCAB = 6


def _fake_encode(rows: dict[str, list[float]]):
    """Return an encode fn mapping known texts to known dense weight rows."""
    def encode(texts: list[str]) -> csr_matrix:
        dense = np.array([rows[t] for t in texts], dtype="float32")
        return csr_matrix(dense)
    return encode


def test_search_ranks_by_sparse_dot_product():
    # doc0 shares terms 0,1 with the query; doc1 shares term 5 only; doc2 none.
    docs = {
        "doc0": [2.0, 1.0, 0.0, 0.0, 0.0, 0.0],
        "doc1": [0.0, 0.0, 0.0, 0.0, 0.0, 3.0],
        "doc2": [0.0, 0.0, 4.0, 0.0, 0.0, 0.0],
    }
    query = {"q": [1.0, 1.0, 0.0, 0.0, 0.0, 1.0]}
    idx = SpladeIndex(_fake_encode({**docs, **query}), vocab_size=VOCAB)
    idx.build(["doc0", "doc1", "doc2"])
    out = idx.search("q", k=2)
    assert [i for i, _ in out] == [0, 1]           # doc0 score 3.0, doc1 score 3.0 -> tie broken by idx
    assert out[0][1] == 3.0 and out[1][1] == 3.0
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && PYTHONPATH=src .venv/bin/pytest tests/test_splade.py::test_search_ranks_by_sparse_dot_product -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sebi_rag.splade'`.

- [ ] **Step 4: Write the minimal `SpladeIndex` (build + search)**

```python
# src/sebi_rag/splade.py
"""SPLADE learned-sparse retrieval leg (iv11).

Non-destructive, opt-in third RRF leg. A dependency-injected encoder maps
texts to sparse term-weight vectors (scipy CSR over the model vocabulary);
search is a sparse dot-product returning the same (idx, score) tuple shape
that rrf_fuse already consumes for the dense and BM25 legs. The encoder is
injected so tests run offline with a fake; the real Splade_PP encoder is
built by SpladeEncoder.load() (see splade_encoder.py).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import numpy as np
from scipy.sparse import csr_matrix, load_npz, save_npz


class SpladeIndex:
    def __init__(
        self, encode: Callable[[list[str]], csr_matrix], vocab_size: int
    ) -> None:
        self._encode = encode
        self.vocab_size = vocab_size
        self.matrix: csr_matrix | None = None

    def build(self, texts: list[str]) -> None:
        self.matrix = self._encode(texts).tocsr()

    def search(self, query: str, k: int) -> list[tuple[int, float]]:
        if self.matrix is None:
            raise RuntimeError("SpladeIndex.search called before build/load")
        q = self._encode([query]).tocsr()          # (1, vocab)
        scores = np.asarray((self.matrix @ q.T).todense()).ravel()  # (n,)
        k = min(k, scores.shape[0])
        # top-k by score, descending; ties broken by ascending index
        top = np.argsort(-scores, kind="stable")[:k]
        return [(int(i), float(scores[i])) for i in top]
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && PYTHONPATH=src .venv/bin/pytest tests/test_splade.py::test_search_ranks_by_sparse_dot_product -v`
Expected: PASS.

- [ ] **Step 6: Write the failing test for save/load round-trip + the `expected_n` guard**

```python
# append to tests/test_splade.py
import pytest


def test_save_load_roundtrip_and_guard(tmp_path):
    docs = {
        "a": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "b": [0.0, 2.0, 0.0, 0.0, 0.0, 0.0],
    }
    idx = SpladeIndex(_fake_encode(docs), vocab_size=VOCAB)
    idx.build(["a", "b"])
    idx.save(tmp_path, model="fake/model")

    # meta records the true row count and vocab
    meta = json.loads((tmp_path / "splade_meta.json").read_text())
    assert meta["n"] == 2 and meta["vocab_size"] == VOCAB and meta["model"] == "fake/model"

    # load with matching expected_n succeeds and preserves scores
    reloaded = SpladeIndex.load(tmp_path, _fake_encode({**docs, "b": [0.0, 2.0, 0.0, 0.0, 0.0, 0.0]}), expected_n=2)
    assert reloaded.matrix.shape == (2, VOCAB)

    # load with wrong expected_n raises, not silently mis-fuses
    with pytest.raises(ValueError, match="row count 2 != expected 77859"):
        SpladeIndex.load(tmp_path, _fake_encode(docs), expected_n=77859)
```
(Add `import json` at the top of the test file alongside the existing imports.)

- [ ] **Step 7: Run the test to verify it fails**

Run: `cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && PYTHONPATH=src .venv/bin/pytest tests/test_splade.py::test_save_load_roundtrip_and_guard -v`
Expected: FAIL with `AttributeError: 'SpladeIndex' object has no attribute 'save'`.

- [ ] **Step 8: Implement `save` and `load`**

```python
# add these methods to SpladeIndex in src/sebi_rag/splade.py
    def save(self, path: str | Path, model: str) -> None:
        if self.matrix is None:
            raise RuntimeError("SpladeIndex.save called before build")
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)
        save_npz(str(d / "splade.npz"), self.matrix)
        (d / "splade_meta.json").write_text(
            json.dumps({"n": int(self.matrix.shape[0]),
                        "vocab_size": int(self.vocab_size),
                        "model": model}),
            encoding="utf-8",
        )

    @classmethod
    def load(
        cls,
        path: str | Path,
        encode: Callable[[list[str]], csr_matrix],
        expected_n: int,
    ) -> "SpladeIndex":
        d = Path(path)
        meta = json.loads((d / "splade_meta.json").read_text(encoding="utf-8"))
        matrix = load_npz(str(d / "splade.npz")).tocsr()
        if matrix.shape[0] != expected_n:
            raise ValueError(
                f"SPLADE row count {matrix.shape[0]} != expected {expected_n}"
            )
        obj = cls(encode, vocab_size=int(meta["vocab_size"]))
        obj.matrix = matrix
        return obj
```

- [ ] **Step 9: Run the full test file to verify both tests pass**

Run: `cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && PYTHONPATH=src .venv/bin/pytest tests/test_splade.py -v`
Expected: 2 passed.

- [ ] **Step 10: Commit**

```bash
git add src/sebi_rag/splade.py tests/test_splade.py
git commit -m "feat: SpladeIndex — CSR doc matrix, sparse-dot search, guarded persistence (iv11)"
```

---

### Task 2: Real Splade_PP encoder (max-pooled MLM logits → CSR)

**Files:**
- Create: `src/sebi_rag/splade_encoder.py`
- Test: `tests/test_splade_encoder.py`

**Interfaces:**
- Consumes: `SpladeIndex`'s encoder contract `Callable[[list[str]], csr_matrix]`.
- Produces:
  - `splade_pool(logits: np.ndarray, attention_mask: np.ndarray) -> np.ndarray` — pure function, the canonical SPLADE max-pool: `max over sequence of log(1 + relu(logits)) * mask`, returns `(batch, vocab)` dense weights. Unit-tested.
  - `SpladeEncoder.load(model: str = "prithivida/Splade_PP_en_v1", device: str = "mps", batch_size: int = 32) -> Callable[[list[str]], csr_matrix]` — factory returning an encode callable (thin, model-loading, not unit-tested — same as `HydeExpander.load`/`HeaderGenerator.load`).

- [ ] **Step 1: Write the failing test for the pooling math (pure, offline)**

```python
# tests/test_splade_encoder.py
from __future__ import annotations

import numpy as np

from sebi_rag.splade_encoder import splade_pool


def test_splade_pool_max_over_sequence_with_log_relu_and_mask():
    # batch=1, seq=2, vocab=3
    logits = np.array([[[0.0, 3.0, -5.0],
                        [2.0, 1.0,  0.0]]], dtype="float32")
    mask = np.array([[1, 1]], dtype="float32")
    out = splade_pool(logits, mask)
    # term0: max(log1p(relu(0)), log1p(relu(2))) = log1p(2)
    # term1: max(log1p(3), log1p(1)) = log1p(3)
    # term2: max(log1p(0), log1p(0)) = 0  (negative logits -> relu 0)
    expected = np.array([[np.log1p(2.0), np.log1p(3.0), 0.0]], dtype="float32")
    assert np.allclose(out, expected, atol=1e-6)


def test_splade_pool_masked_positions_excluded():
    logits = np.array([[[10.0, 0.0, 0.0],
                        [ 0.0, 9.0, 0.0]]], dtype="float32")
    mask = np.array([[1, 0]], dtype="float32")   # second token padding
    out = splade_pool(logits, mask)
    # only first token counts: term0 = log1p(10), others 0
    assert np.isclose(out[0, 0], np.log1p(10.0), atol=1e-6)
    assert out[0, 1] == 0.0 and out[0, 2] == 0.0
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && PYTHONPATH=src .venv/bin/pytest tests/test_splade_encoder.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sebi_rag.splade_encoder'`.

- [ ] **Step 3: Implement `splade_pool` and the `SpladeEncoder.load` factory**

```python
# src/sebi_rag/splade_encoder.py
"""Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.

splade_pool is the canonical SPLADE representation (Formal et al.):
    w_j = max_{i in seq}  log(1 + relu(logits_{i,j}))  * mask_i
kept as a pure function so the math is unit-tested without loading a model.
SpladeEncoder.load returns an encode callable for SpladeIndex; it is thin
model plumbing and follows the untested-factory pattern of HydeExpander.load.
"""
from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.sparse import csr_matrix


def splade_pool(logits: np.ndarray, attention_mask: np.ndarray) -> np.ndarray:
    """(batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights."""
    activated = np.log1p(np.maximum(logits, 0.0))           # log(1 + relu(x))
    masked = activated * attention_mask[:, :, None]         # zero padding rows
    return masked.max(axis=1)                               # max over sequence


class SpladeEncoder:
    @staticmethod
    def load(
        model: str = "prithivida/Splade_PP_en_v1",
        device: str = "mps",
        batch_size: int = 32,
    ) -> Callable[[list[str]], csr_matrix]:
        import torch
        from transformers import AutoModelForMaskedLM, AutoTokenizer

        tok = AutoTokenizer.from_pretrained(model)
        mdl = AutoModelForMaskedLM.from_pretrained(model).to(device).eval()

        def encode(texts: list[str]) -> csr_matrix:
            rows: list[csr_matrix] = []
            for start in range(0, len(texts), batch_size):
                batch = texts[start: start + batch_size]
                enc = tok(batch, padding=True, truncation=True,
                          max_length=512, return_tensors="pt").to(device)
                with torch.no_grad():
                    logits = mdl(**enc).logits            # (b, seq, vocab)
                weights = splade_pool(
                    logits.float().cpu().numpy(),
                    enc["attention_mask"].cpu().numpy().astype("float32"),
                )
                rows.append(csr_matrix(weights))
            from scipy.sparse import vstack
            return vstack(rows).tocsr() if rows else csr_matrix((0, mdl.config.vocab_size))

        return encode
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && PYTHONPATH=src .venv/bin/pytest tests/test_splade_encoder.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/splade_encoder.py tests/test_splade_encoder.py
git commit -m "feat: Splade_PP encoder — max-pool logits to CSR (iv11)"
```

---

### Task 3: Wire the SPLADE leg into `HybridRetriever.retrieve`

**Files:**
- Modify: `src/sebi_rag/retrieve.py` (the `HybridRetriever` dataclass and `retrieve`, around lines 86-183)
- Test: `tests/test_splade_leg.py`

**Interfaces:**
- Consumes: `SpladeIndex` (Task 1); existing `rrf_fuse(rankings, k_const=60, top_n=50)` and `DenseIndex`/`SparseIndex`.
- Produces: `HybridRetriever.splade: SpladeIndex | None` field (default `None`); `retrieve(..., use_splade: bool = False, k_splade: int = 50)`. With `use_splade=False` behavior is unchanged; with `use_splade=True` and `self.splade is None`, raises `RuntimeError`.

- [ ] **Step 1: Write the failing tests (3-leg fusion active + flag-off no-op + guard)**

```python
# tests/test_splade_leg.py
from __future__ import annotations

import numpy as np
import pytest
from scipy.sparse import csr_matrix

from sebi_rag.retrieve import HybridRetriever
from sebi_rag.segment import Chunk
from sebi_rag.splade import SpladeIndex


class _StubDense:
    """Returns a fixed dense ranking regardless of query."""
    def __init__(self, ranking): self._r = ranking
    def search(self, query, k): return self._r[:k]


class _StubSparse:
    def __init__(self, ranking): self._r = ranking
    def search(self, query, k): return self._r[:k]


def _chunks(n):
    return [Chunk(id=f"D/{i}#0", doc_id="D", section="0", text=f"t{i}",
                  meta={}) for i in range(n)]


def _fake_encode(rows):
    def encode(texts):
        return csr_matrix(np.array([rows[t] for t in texts], dtype="float32"))
    return encode


def test_splade_leg_changes_fused_order_when_on():
    chunks = _chunks(3)
    # dense likes doc2 then doc0; sparse likes doc2 then doc1.
    dense = _StubDense([(2, 0.9), (0, 0.8)])
    sparse = _StubSparse([(2, 5.0), (1, 4.0)])
    splade = SpladeIndex(_fake_encode({
        "t0": [1.0, 0.0], "t1": [0.0, 0.0], "t2": [0.0, 0.0], "q": [1.0, 0.0],
    }), vocab_size=2)
    splade.build(["t0", "t1", "t2"])
    r = HybridRetriever(chunks=chunks, dense=dense, sparse=sparse, splade=splade)

    off = [c.id for c, _ in r.retrieve("q", use_splade=False)]
    on = [c.id for c, _ in r.retrieve("q", use_splade=True)]
    # With splade on, doc0 gains a strong third-leg vote and must rank higher
    # than it does with splade off.
    assert on.index("D/0#0") < off.index("D/0#0")


def test_flag_off_is_unchanged_and_ignores_splade():
    chunks = _chunks(2)
    dense = _StubDense([(0, 0.9), (1, 0.8)])
    sparse = _StubSparse([(0, 5.0), (1, 4.0)])
    r = HybridRetriever(chunks=chunks, dense=dense, sparse=sparse, splade=None)
    out = [c.id for c, _ in r.retrieve("q", use_splade=False)]
    assert out == ["D/0#0", "D/1#0"]


def test_use_splade_without_index_raises():
    chunks = _chunks(1)
    r = HybridRetriever(chunks=chunks, dense=_StubDense([(0, 1.0)]),
                        sparse=_StubSparse([(0, 1.0)]), splade=None)
    with pytest.raises(RuntimeError, match="use_splade=True but no SPLADE index"):
        r.retrieve("q", use_splade=True)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && PYTHONPATH=src .venv/bin/pytest tests/test_splade_leg.py -v`
Expected: FAIL — `TypeError` on the unexpected `splade=` keyword to `HybridRetriever`.

- [ ] **Step 3: Add the `splade` field to the dataclass**

In `src/sebi_rag/retrieve.py`, add the import near the top (after the existing `from .segment import Chunk`):
```python
from .splade import SpladeIndex
```
Add the field to the `HybridRetriever` dataclass (after the `vecs` field at line ~91):
```python
    splade: SpladeIndex | None = field(default=None, repr=False)
```

- [ ] **Step 4: Add the leg to `retrieve`**

Replace the current `retrieve` signature and body (lines ~165-183) with:
```python
    def retrieve(
        self,
        query: str,
        k_dense: int = 50,
        k_sparse: int = 50,
        top_n: int = 50,
        hyde_text: str | None = None,
        use_splade: bool = False,
        k_splade: int = 50,
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
        if use_splade:
            # intervention iv11 (SPLADE): learned-sparse third leg on the RAW
            # query (SPLADE does its own expansion; glossary stays BM25-only).
            if self.splade is None:
                raise RuntimeError("use_splade=True but no SPLADE index attached")
            legs.append(self.splade.search(query, k_splade))
        fused = rrf_fuse(legs, top_n=top_n)
        return [(self.chunks[i], score) for i, score in fused]
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && PYTHONPATH=src .venv/bin/pytest tests/test_splade_leg.py -v`
Expected: 3 passed.

- [ ] **Step 6: Run the full suite to confirm no regression**

Run: `cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && make test`
Expected: 287 passed (282 prior + 2 Task 1 + 2 Task 2... note exact count may differ; the requirement is **all green, and the count increased by the new tests only**). If any prior test fails, STOP — the flag-off path is not byte-identical.

- [ ] **Step 7: Commit**

```bash
git add src/sebi_rag/retrieve.py tests/test_splade_leg.py
git commit -m "feat: wire opt-in SPLADE third leg into HybridRetriever.retrieve (iv11)"
```

---

### Task 4: Build script + pilot gate

**Files:**
- Create: `scripts/build_splade_index.py`
- Create: `scripts/splade_pilot.py`

**Interfaces:**
- Consumes: `SpladeEncoder.load` (Task 2), `SpladeIndex` (Task 1), `load_circulars` (`src/sebi_rag/corpus.py`).
- Produces: `data/index/splade.npz` + `data/index/splade_meta.json` (built once).

- [ ] **Step 1: Write the pilot-gate script (runs BEFORE the full encode)**

```python
# scripts/splade_pilot.py
"""Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the
residual paraphrase gaps BEFORE paying the ~3.5h full-corpus encode.

For each residual query + its known answer chunk text, encode both, and
print the top overlapping expansion terms (by min weight). A healthy signal
is a non-trivial shared statutory/lay term set (e.g. the AIF query and the
AIF answer chunk sharing 'fund'/'investment'/'alternative').

    PYTHONPATH=src .venv/bin/python scripts/splade_pilot.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
for k, v in {"TOKENIZERS_PARALLELISM": "false", "PYTORCH_ENABLE_MPS_FALLBACK": "1",
             "HF_HUB_DISABLE_XET": "1"}.items():
    os.environ.setdefault(k, v)

import numpy as np
from transformers import AutoTokenizer

from sebi_rag.splade_encoder import SpladeEncoder

# Residual failure queries (report §5.5) with a short lay description of the
# answer text to sanity-check bridging. Full answer chunks are large; a
# representative snippet is sufficient for a go/no-go term-overlap read.
PILOT = [
    ("Category II private pooled investment vehicle registration",
     "Alternative Investment Fund AIF registered with the Board under regulations"),
    ("winding down rating agency pull ongoing assignments",
     "credit rating agency surrender of certificate not take any new clients"),
    ("which appendix serial numbers withdrawn on issuance",
     "circulars listed at Sl. No. 68-74 in the Appendix shall stand rescinded"),
]


def main() -> None:
    encode = SpladeEncoder.load()
    tok = AutoTokenizer.from_pretrained("prithivida/Splade_PP_en_v1")
    inv = {v: k for k, v in tok.get_vocab().items()}
    for q, a in PILOT:
        mq = encode([q]).tocoo()
        ma = encode([a]).tocoo()
        wq = {int(j): float(v) for j, v in zip(mq.col, mq.data)}
        wa = {int(j): float(v) for j, v in zip(ma.col, ma.data)}
        shared = sorted(
            ((min(wq[j], wa[j]), inv[j]) for j in set(wq) & set(wa)),
            reverse=True,
        )[:12]
        print(f"\nQUERY: {q}\n  shared terms: {[t for _, t in shared]}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the pilot gate and record the go/no-go**

Run:
```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && \
PYTHONPATH=src .venv/bin/python scripts/splade_pilot.py
```
Expected: for each of the 3 residual queries, a non-empty `shared terms` list that includes topical statutory/lay tokens bridging the query and answer (e.g. `fund`, `investment`, `alternative` for AIF; `rating`, `surrender`, `clients` for CRA; `appendix`, `rescinded`, `withdrawn` for supersession). **GO** if at least 2 of 3 show a meaningful bridge. If fewer, STOP and report to the user — SPLADE is unlikely to help the residual and the 3.5h encode is not justified (record this as a negative pilot in the report, as iv9's 1.5B pilot was).

- [ ] **Step 3: Write the full-corpus build script**

```python
# scripts/build_splade_index.py
"""Build the SPLADE learned-sparse doc matrix once and persist it (iv11).

Standalone (kept out of build_index.py so the ~3.5h SPLADE encode never
entangles with routine dense/BM25 reindex). Chunk order is identical to the
dense index because both load data/corpus/circulars.jsonl via load_circulars.

    HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false PYTORCH_ENABLE_MPS_FALLBACK=1 \
    PYTHONPATH=src .venv/bin/python scripts/build_splade_index.py
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
for k, v in {"TOKENIZERS_PARALLELISM": "false", "PYTORCH_ENABLE_MPS_FALLBACK": "1",
             "HF_HUB_DISABLE_XET": "1", "OMP_NUM_THREADS": "1"}.items():
    os.environ.setdefault(k, v)

from sebi_rag.corpus import load_circulars
from sebi_rag.splade import SpladeIndex
from sebi_rag.splade_encoder import SpladeEncoder

MODEL = "prithivida/Splade_PP_en_v1"
CORPUS = ROOT / "data" / "corpus" / "circulars.jsonl"
INDEX = ROOT / "data" / "index"


def main() -> None:
    chunks = load_circulars(CORPUS)
    texts = [c.text for c in chunks]
    print(f"chunks={len(texts)}  loading {MODEL} ...", flush=True)
    encode = SpladeEncoder.load(MODEL)
    # infer vocab from a 1-row probe (avoids hardcoding 30522)
    vocab = encode(["probe"]).shape[1]
    idx = SpladeIndex(encode, vocab_size=vocab)
    t0 = time.time()
    idx.build(texts)
    nnz = idx.matrix.nnz
    print(f"encoded in {time.time() - t0:.0f}s  shape={idx.matrix.shape}  nnz={nnz}",
          flush=True)
    idx.save(INDEX, model=MODEL)
    print(f"saved -> {INDEX}/splade.npz + splade_meta.json", flush=True)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the full build (only if pilot was GO)**

Run:
```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && \
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false PYTORCH_ENABLE_MPS_FALLBACK=1 \
PYTHONPATH=src .venv/bin/python scripts/build_splade_index.py
```
Expected: `chunks=77859 ...` then, after up to ~3.5h, `encoded in <n>s shape=(77859, <vocab>) nnz=<large>` and `saved -> …/splade.npz`. Verify `data/index/splade_meta.json` shows `"n": 77859`.

- [ ] **Step 5: Commit the scripts (not the multi-hundred-MB artifact yet — that is force-added in Task 6 alongside the runs, matching the iv9/iv10 data/ exception pattern)**

```bash
git add scripts/build_splade_index.py scripts/splade_pilot.py
git commit -m "feat: SPLADE full-corpus build script + pilot gate (iv11)"
```

---

### Task 5: Bench `--splade` flag (mirrors the `--hyde` wrapper)

**Files:**
- Modify: `scripts/bench_retrieval.py` (the `main()` arg block ~60-67 and the wrapper section ~116-137)

**Interfaces:**
- Consumes: `SpladeIndex.load` (Task 1), `SpladeEncoder.load` (Task 2), the `use_splade` param on `retrieve` (Task 3).
- Produces: a `--splade` CLI flag that attaches a loaded `SpladeIndex` and routes retrieval through the third leg.

- [ ] **Step 1: Add the `--splade` argument**

In `scripts/bench_retrieval.py`, after the `--hyde` line (~66):
```python
    ap.add_argument("--splade", action="store_true")
```

- [ ] **Step 2: Attach the SPLADE index and wrap the retriever**

After the existing `--hyde` wrapper block (after line ~137, before `result = run_retrieval_benchmark(...)`), add:
```python
    if args.splade:
        from sebi_rag.splade import SpladeIndex
        from sebi_rag.splade_encoder import SpladeEncoder

        # --smoke stays offline: a trivial fake encoder over a tiny vocab.
        if args.smoke:
            import numpy as np
            from scipy.sparse import csr_matrix
            n = len(pipeline.retriever.chunks)
            fake_mat = csr_matrix(np.ones((n, 4), dtype="float32"))
            si = SpladeIndex(lambda ts: csr_matrix(np.ones((len(ts), 4), "float32")), 4)
            si.matrix = fake_mat
        else:
            enc = SpladeEncoder.load()
            si = SpladeIndex.load(index_dir, enc,
                                  expected_n=len(pipeline.retriever.chunks))
        pipeline.retriever.splade = si

        class _SpladeRetriever:
            def __init__(self, inner):
                self.inner = inner
                self.chunks = inner.chunks

            def retrieve(self, query: str, top_n: int = 50):
                return self.inner.retrieve(query, top_n=top_n, use_splade=True)

        pipeline.retriever = _SpladeRetriever(pipeline.retriever)
```

- [ ] **Step 3: Add `splade` to the recorded params**

Change the `params=` line (~151) from:
```python
        params={"top_n": args.top_n, "smoke": args.smoke, "hyde": args.hyde},
```
to:
```python
        params={"top_n": args.top_n, "smoke": args.smoke, "hyde": args.hyde,
                "splade": args.splade},
```

- [ ] **Step 4: Smoke-test the flag path offline**

Run:
```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && \
PYTHONPATH=src .venv/bin/python scripts/bench_retrieval.py --smoke --splade \
  --out /tmp/iv11-smoke
```
Expected: exits 0, prints a JSON block with `"out": "/tmp/iv11-smoke"` and a `recall_at_10` field (value not meaningful on the 1-item smoke corpus; this only proves the `--splade` wiring runs end-to-end without error).

- [ ] **Step 5: Commit**

```bash
git add scripts/bench_retrieval.py
git commit -m "feat: --splade bench flag routing retrieval through the third leg (iv11)"
```

---

### Task 6: A/B + 3-way runs, item-by-item diff, report §5.6

**Files:**
- Output: `eval/runs/iv11-a-{probes,golden}/`, `eval/runs/iv11-b-{probes,golden}/`, `eval/runs/iv11-splade-only-{probes,golden}/`
- Modify: `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md` (append §5.6 after §5.5)

**Interfaces:**
- Consumes: Task 5's `--splade` flag; the persisted `splade.npz` (Task 4); `scripts/analysis/extract_misses.py`.
- Produces: the six iv11 run directories and the recorded gate verdict.

- [ ] **Step 1: Benchmark A (2-leg control — no `--splade`)**

```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false PYTORCH_ENABLE_MPS_FALLBACK=1 \
.venv/bin/python scripts/bench_retrieval.py \
  --golden eval/probes/probes_v1.jsonl --out eval/runs/iv11-a-probes
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false PYTORCH_ENABLE_MPS_FALLBACK=1 \
.venv/bin/python scripts/bench_retrieval.py \
  --golden eval/golden/golden_v6.jsonl --out eval/runs/iv11-a-golden
.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv11-a-probes/run.trec --golden eval/probes/probes_v1.jsonl \
  --out eval/runs/iv11-a-probes/failures.jsonl --source probes_v1
.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv11-a-golden/run.trec --golden eval/golden/golden_v6.jsonl \
  --out eval/runs/iv11-a-golden/failures.jsonl --source golden_v6
```
Expected: probes recall@10 = 1.0, 4 answer-level failures; golden recall@10 = 0.9556, 2 answer-level failures (matches iv10-a — this is the same untouched index).

- [ ] **Step 2: Benchmark B (3-leg — add `--splade`)**

```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false PYTORCH_ENABLE_MPS_FALLBACK=1 \
.venv/bin/python scripts/bench_retrieval.py --splade \
  --golden eval/probes/probes_v1.jsonl --out eval/runs/iv11-b-probes
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false PYTORCH_ENABLE_MPS_FALLBACK=1 \
.venv/bin/python scripts/bench_retrieval.py --splade \
  --golden eval/golden/golden_v6.jsonl --out eval/runs/iv11-b-golden
.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv11-b-probes/run.trec --golden eval/probes/probes_v1.jsonl \
  --out eval/runs/iv11-b-probes/failures.jsonl --source probes_v1
.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv11-b-golden/run.trec --golden eval/golden/golden_v6.jsonl \
  --out eval/runs/iv11-b-golden/failures.jsonl --source golden_v6
```
Expected: both benchmarks complete; record the exact recall@10 and failure counts for the diff.

- [ ] **Step 3: 3-way diagnostic — SPLADE-only leg**

This needs a one-off SPLADE-only run. Temporarily bench with only the SPLADE leg by adding a throwaway `--splade-only` path is over-engineering; instead capture SPLADE's standalone reach directly:
```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false PYTORCH_ENABLE_MPS_FALLBACK=1 \
PYTHONPATH=src .venv/bin/python -c "
import json, os
from pathlib import Path
from sebi_rag.corpus import load_circulars
from sebi_rag.splade import SpladeIndex
from sebi_rag.splade_encoder import SpladeEncoder
ROOT = Path('.')
chunks = load_circulars(ROOT/'data/corpus/circulars.jsonl')
enc = SpladeEncoder.load()
si = SpladeIndex.load(ROOT/'data/index', enc, expected_n=len(chunks))
for name, gp in [('probes', 'eval/probes/probes_v1.jsonl'),
                 ('golden', 'eval/golden/golden_v6.jsonl')]:
    out = Path(f'eval/runs/iv11-splade-only-{name}'); out.mkdir(parents=True, exist_ok=True)
    with (out/'run.trec').open('w') as f:
        for l in open(gp):
            item = json.loads(l)
            hits = si.search(item['query'], 50)
            for rank, (i, s) in enumerate(hits):
                f.write(f\"{item['id']} Q0 {chunks[i].id} {rank+1} {s:.6f} splade-only\n\")
print('wrote splade-only runfiles')
"
.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv11-splade-only-probes/run.trec --golden eval/probes/probes_v1.jsonl \
  --out eval/runs/iv11-splade-only-probes/failures.jsonl --source probes_v1
.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv11-splade-only-golden/run.trec --golden eval/golden/golden_v6.jsonl \
  --out eval/runs/iv11-splade-only-golden/failures.jsonl --source golden_v6
```
Expected: two runfiles written; the `extract_misses` summaries show how many residual answer chunks SPLADE reaches on its own (diagnostic only — informs whether any B gain is from SPLADE reaching new chunks vs. pure rank reshuffling).

- [ ] **Step 4: Compute the item-by-item diff (A vs B)**

```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && python3 -c "
import json
def load(p): return {r['id']: r for r in (json.loads(l) for l in open(p))}
for kind in ('probes', 'golden'):
    a = load(f'eval/runs/iv11-a-{kind}/failures.jsonl')
    b = load(f'eval/runs/iv11-b-{kind}/failures.jsonl')
    af = {k for k, v in a.items() if v['answer_class'] != 'hit'}
    bf = {k for k, v in b.items() if v['answer_class'] != 'hit'}
    print(f'=== {kind} ===')
    print('A fail:', sorted(af)); print('B fail:', sorted(bf))
    print('resolved (A fail -> B hit):', sorted(af - bf))
    print('regressed (A hit -> B fail):', sorted(bf - af))
"
```
Expected: prints resolved/regressed sets. The **gate**: at least the resolved set is non-empty on some axis AND the regressed set is empty on both axes → SPLADE wins. Any non-empty regressed set → report as a localized negative (SPLADE reshuffled a passing item out), do not promote.

- [ ] **Step 5: Full test suite (unchanged — retrieval code paths are additive)**

Run: `cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && make test`
Expected: all green (same count as end of Task 3). SPLADE artifacts do not affect the offline suite.

- [ ] **Step 6: Write report §5.6 with the three verdict branches**

Append a `### 5.6 SPLADE learned-sparse third leg (iv11, 2026-07-20)` section to `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md` after §5.5, containing: the A/B/SPLADE-only table (answerable, answer-level failures, recall@10 for each), the pilot-gate outcome (shared-term bridges observed), the item-by-item resolved/regressed diff, and exactly one of these pre-written verdicts made concrete with the numbers:

- **Win:** "≥1 residual resolved, zero regressions — SPLADE third leg validated as a net recall improvement. Recommend a follow-on cycle to promote it to the default API/Settings path (currently eval-only)."
- **Insufficient:** "no residual resolved, zero regressions — SPLADE is safe but does not reach the current residual (which the SPLADE-only run confirms it does/does not independently retrieve). Close as a documented negative alongside iv9/iv10; the residual is now understood to require [answer-chunk-level fix / accept as residual]."
- **Regression:** "≥1 previously-passing item regressed — SPLADE's rank contribution displaces a correct chunk. Reject; do not promote. Stronger localized signal than a null result."

- [ ] **Step 7: Commit runs + report + the SPLADE artifact (force-add, per data/ gitignore exception)**

```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
git add eval/runs/iv11-a-probes eval/runs/iv11-a-golden \
        eval/runs/iv11-b-probes eval/runs/iv11-b-golden \
        eval/runs/iv11-splade-only-probes eval/runs/iv11-splade-only-golden \
        docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md
git add -f data/index/splade.npz data/index/splade_meta.json
git commit -m "eval: SPLADE third-leg A/B + 3-way runs, report §5.6 (iv11)"
```

---

## Self-Review

**Spec coverage:**
- Success criterion (general recall, no-regression) → Task 6 Step 4 gate + §5.6.
- Model/license (Splade_PP, Apache-2.0) → Task 1 Step 1 license assertion; Task 2/4 use the checkpoint.
- Non-destructive additive architecture → Task 3 (additive leg, flag-off byte-identical); no snapshot/restore anywhere (correct — nothing is mutated).
- `SpladeIndex` (CSR, search, save/load, guard) → Task 1.
- Full-corpus build, separate script, chunk-order alignment → Task 4 (both scripts load `circulars.jsonl` via `load_circulars`, same as dense).
- Pilot gate before 3.5h encode → Task 4 Steps 1-2.
- Raw query to SPLADE, glossary BM25-only → Task 3 Step 4 (`self.splade.search(query, ...)`, not `expand_query(query)`), stated in the code comment.
- `n=77859` load guard → Task 1 Step 8 + Task 5 (`expected_n=len(chunks)`).
- A/B + 3-way diagnostic → Task 6 Steps 1-3.
- Offline DI tests → Tasks 1-3 all use fake encoders.
- Loud-failure error handling → Task 3 (`RuntimeError` on `use_splade` without index), Task 1 (`ValueError` on `n` mismatch).
- Eval-only (no API/Settings) → no task touches `api.py`/`settings.py`/`pipeline.py`.

**Placeholder scan:** No TBD/TODO; every code step shows complete code; the report §5.6 step (Task 6 Step 6) specifies exact contents and three concrete verdict branches rather than "write the report".

**Type consistency:** `SpladeIndex(encode, vocab_size)` and `.search(query, k) -> list[tuple[int, float]]` are identical across Tasks 1, 3, 4, 5. `SpladeEncoder.load(...) -> Callable[[list[str]], csr_matrix]` matches the `encode` the index expects. `splade_pool(logits, attention_mask) -> np.ndarray` used only inside Task 2. `retrieve(..., use_splade=False, k_splade=50)` defined in Task 3 and called with `use_splade=True` in Task 5.

**Note on test count:** the plan states "287 passed" as illustrative in Task 3 Step 6; the real invariant is *all prior tests still pass and the total rises by exactly the newly-added tests*. An implementer should not treat 287 as a hard number.
