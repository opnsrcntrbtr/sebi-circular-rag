# Track B — Apple-Silicon Compute Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Sequencing:** Execute AFTER Track A (`2026-07-22-track-a-spaces-ux-port.md`). Tracks are independent; this ordering is a review convenience, not a code dependency.

**Goal:** Harden the local Apple-Silicon compute path to mid-2026 best practice — centralized device auto-detect, an fp16 policy (bf16 avoided on MPS), unified-memory OOM hygiene, batch-size config — and scope the optional MLX-native embeddings/reranker backend via a spike. ANE/NPU is declined and recorded as an ADR.

**Architecture:** A new `src/sebi_rag/device.py` centralizes the `mps`/`cpu` decision (removing hardcoded `"mps"`) and the fp16 policy. `Settings` gains compute knobs resolved through the existing env>toml>default chain. `BGEM3Embedder`/`CrossEncoderReranker` accept `device`/`use_fp16`/`batch_size`; `build_default_pipeline` passes them via a small pure `_compute_kwargs(settings)` helper. The fp16 default is flipped on only after an A/B recall-parity gate. The MLX-native backend is de-risked with a spike (findings doc), with concrete implementation deferred to a follow-up plan.

**Tech Stack:** Python 3.12, PyTorch MPS, FlagEmbedding (BGE-M3), sentence-transformers CrossEncoder, MLX (generation already; embeddings/reranker under evaluation), pytest, `uv`, `make`.

## Global Constraints

- **Two-parallel-paths rule:** edit ONLY local modules — `src/sebi_rag/device.py` (new), `settings.py`, `embeddings.py`, `rerank.py`, `api.py`, `config.toml`, `Makefile`, plus new docs/tests. Do NOT edit `app.py` or any `*_spaces.py`.
- **Measurement-first / no silent regression:** any change that can move retrieval quality (fp16, MLX backend) ships **disabled by default** and is enabled ONLY after an A/B recall-parity gate (`make bench-retrieval` / `make eval-asof`) shows no golden/probe regression. Record results under `reports/`.
- **bf16 is never selected on MPS** (poor kernel support as of mid-2026 — see the design spec's Sources).
- **Offline suite stays green & model-free:** `make test` runs `pytest -q -m "not integration"`. Real-weight behavior goes under the existing `integration` marker.
- **Env for ad-hoc runs:** Makefile sets `PYTHONPATH=src` (+ HF/threads/MPS-fallback vars). For ad-hoc pytest: `PYTHONPATH=src pytest ...`.
- **Commit trailer:** end every commit message with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- **After code changes:** run `graphify update .` (AST-only, no API cost).
- **Python floor:** `requires-python >=3.12,<3.13`. Dependency version floors already in `pyproject.toml`.

---

## File Structure

| File | Responsibility |
|---|---|
| `src/sebi_rag/device.py` (create) | `pick_device` (mps→cpu auto-detect), `should_use_fp16` (fp16 policy, no bf16) |
| `src/sebi_rag/settings.py` (modify) | New fields: `device`, `use_fp16`, `encode_batch_size`, `embed_backend`, `rerank_backend`; `_as_bool` helper |
| `config.toml` (modify) | Document the new `[service]` compute keys |
| `src/sebi_rag/embeddings.py` (modify) | `BGEM3Embedder` accepts `device`/`use_fp16`/`batch_size` |
| `src/sebi_rag/rerank.py` (modify) | `CrossEncoderReranker` accepts `device`/`use_fp16`/`batch_size` |
| `src/sebi_rag/api.py` (modify) | `_compute_kwargs(settings)`; wire into `build_default_pipeline` |
| `Makefile` (modify) | Add `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0` to `ENV` |
| `docs/adr-003-ane-declined.md` (create) | ANE decision record |
| `docs/superpowers/specs/2026-07-22-mlx-backend-spike-findings.md` (create, Task 6) | MLX library + API + parity findings; go/no-go |
| `tests/test_device.py` (create) | `pick_device`/`should_use_fp16` matrices |
| `tests/test_settings.py` (modify) | Round-trip for new compute fields |
| `tests/test_api.py` (modify) | `_compute_kwargs` behavior + embedder/reranker signature guard |

---

## Task 1: `device.py` — device + fp16 policy

**Files:**
- Create: `src/sebi_rag/device.py`
- Test: `tests/test_device.py` (create)

**Interfaces:**
- Produces: `pick_device(pref: str | None = None, is_mps_available: Callable[[], bool] | None = None) -> str`; `should_use_fp16(device: str, use_fp16: bool) -> bool`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_device.py`:

```python
"""Device + fp16 policy selection (no real torch/mps required)."""
from __future__ import annotations

from sebi_rag.device import pick_device, should_use_fp16


def test_pick_device_honors_explicit_pref():
    assert pick_device("cpu", is_mps_available=lambda: True) == "cpu"
    assert pick_device("cuda", is_mps_available=lambda: False) == "cuda"


def test_pick_device_auto_mps_when_available():
    assert pick_device(None, is_mps_available=lambda: True) == "mps"


def test_pick_device_auto_cpu_when_no_mps():
    assert pick_device(None, is_mps_available=lambda: False) == "cpu"


def test_pick_device_empty_pref_is_auto():
    assert pick_device("", is_mps_available=lambda: False) == "cpu"


def test_should_use_fp16_matrix():
    assert should_use_fp16("mps", True) is True
    assert should_use_fp16("cuda", True) is True
    assert should_use_fp16("cpu", True) is False   # never fp16 on cpu
    assert should_use_fp16("mps", False) is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=src pytest tests/test_device.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sebi_rag.device'`.

- [ ] **Step 3: Create `src/sebi_rag/device.py`**

```python
"""Device + precision selection for Apple-Silicon inference.

Centralizes the mps/cpu decision (previously hardcoded "mps") and the fp16
policy. bfloat16 is deliberately never selected: as of mid-2026 the MPS backend
lacks optimized bf16 kernels and is far slower than fp16/fp32 for inference.
See docs/superpowers/specs/2026-07-22-spaces-ux-and-apple-silicon-compute-design.md
(Sources).
"""
from __future__ import annotations

from typing import Callable


def _mps_available() -> bool:
    try:
        import torch
        return bool(torch.backends.mps.is_available())
    except Exception:  # noqa: BLE001 - torch missing or probe failed -> treat as no mps
        return False


def pick_device(pref: str | None = None,
                is_mps_available: Callable[[], bool] | None = None) -> str:
    """Resolve the compute device.

    A truthy explicit `pref` ("mps"/"cpu"/"cuda") wins. Otherwise prefer "mps"
    when available, else "cpu". `is_mps_available` is injectable for tests.
    """
    if pref:
        return pref
    check = is_mps_available or _mps_available
    return "mps" if check() else "cpu"


def should_use_fp16(device: str, use_fp16: bool) -> bool:
    """fp16 only on GPU-class devices; never on cpu. bf16 is never returned
    here by design (poor MPS support)."""
    return bool(use_fp16) and device in ("mps", "cuda")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=src pytest tests/test_device.py -v`
Expected: PASS — all 5 tests green.

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/device.py tests/test_device.py
git commit -m "$(cat <<'EOF'
feat(device): centralize mps/cpu auto-detect + fp16 policy

pick_device removes the hardcoded "mps" (cpu fallback for CI/Linux);
should_use_fp16 enforces fp16-on-gpu-only and never bf16 on MPS.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Settings compute fields + config.toml

**Files:**
- Modify: `src/sebi_rag/settings.py` (`Settings` dataclass ~L51-62; `load` ~L64-81; add `_as_bool` near `_get` ~L20)
- Modify: `config.toml` (`[service]` block)
- Test: `tests/test_settings.py`

**Interfaces:**
- Produces: `Settings.device: str | None = None`, `Settings.use_fp16: bool = False`, `Settings.encode_batch_size: int = 32`, `Settings.embed_backend: str = "torch"`, `Settings.rerank_backend: str = "torch"`.

> **Note on the `use_fp16` default:** the design spec lists `use_fp16 = True`, but per the measurement-first constraint we ship the field default **`False`** (preserving today's fp32 behavior) and flip it to `True` only after the Task 5 A/B parity gate. This realizes the spec's "default value is set by the A/B result."

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_settings.py`. First extend `ENV_KEYS` (L6-7) to include the new keys:

```python
ENV_KEYS = ["SEBI_RAG_GENERATOR", "SEBI_RAG_TOP_K", "SEBI_RAG_RATE_PER_MIN",
            "SEBI_RAG_TIMEOUT_S", "SEBI_RAG_MLX_MODEL",
            "SEBI_RAG_DEVICE", "SEBI_RAG_USE_FP16", "SEBI_RAG_ENCODE_BATCH_SIZE",
            "SEBI_RAG_EMBED_BACKEND", "SEBI_RAG_RERANK_BACKEND"]
```

Then add these tests:

```python
def test_compute_defaults(monkeypatch, tmp_path):
    _clear(monkeypatch)
    monkeypatch.setenv("SEBI_RAG_CONFIG", str(tmp_path / "none.toml"))
    s = Settings.load()
    assert s.device is None                 # auto-detect
    assert s.use_fp16 is False              # fp32 until the eval gate flips it
    assert s.encode_batch_size == 32
    assert s.embed_backend == "torch" and s.rerank_backend == "torch"


def test_compute_from_file(monkeypatch, tmp_path):
    _clear(monkeypatch)
    cfg = tmp_path / "c.toml"
    cfg.write_text(
        "[service]\ndevice = \"cpu\"\nuse_fp16 = true\n"
        "encode_batch_size = 64\nembed_backend = \"mlx\"\n",
        encoding="utf-8")
    monkeypatch.setenv("SEBI_RAG_CONFIG", str(cfg))
    s = Settings.load()
    assert s.device == "cpu" and s.use_fp16 is True
    assert s.encode_batch_size == 64 and s.embed_backend == "mlx"


def test_compute_env_overrides(monkeypatch, tmp_path):
    _clear(monkeypatch)
    monkeypatch.setenv("SEBI_RAG_CONFIG", str(tmp_path / "none.toml"))
    monkeypatch.setenv("SEBI_RAG_USE_FP16", "true")
    monkeypatch.setenv("SEBI_RAG_DEVICE", "mps")
    monkeypatch.setenv("SEBI_RAG_ENCODE_BATCH_SIZE", "16")
    s = Settings.load()
    assert s.use_fp16 is True and s.device == "mps" and s.encode_batch_size == 16
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=src pytest tests/test_settings.py::test_compute_defaults -v`
Expected: FAIL — `AttributeError: 'Settings' object has no attribute 'device'`.

- [ ] **Step 3: Add the `_as_bool` helper**

In `src/sebi_rag/settings.py`, just below `_get` (after ~L22), add:

```python
def _as_bool(v: object) -> bool:
    """Coerce a config/env value to bool. Env vars arrive as strings; toml/default
    may already be bool."""
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ("1", "true", "yes", "on")
```

- [ ] **Step 4: Add the fields to the `Settings` dataclass**

In `Settings` (frozen dataclass), add after `timeout_s` and before `spaces`:

```python
    device: str | None = None          # None = auto-detect (mps else cpu)
    use_fp16: bool = False             # fp16 on mps/cuda; flipped True by eval gate
    encode_batch_size: int = 32        # embed/rerank batch size
    embed_backend: str = "torch"       # torch | mlx (mlx = eval-gated, Phase 2)
    rerank_backend: str = "torch"      # torch | mlx (mlx = eval-gated, Phase 2)
```

- [ ] **Step 5: Resolve the fields in `Settings.load`**

In `load`, just before `return cls(`, add locals:

```python
        dev = _get("device", None, "SEBI_RAG_", svc)
        device = str(dev) if dev else None
```

Then add to the `cls(...)` call (after `timeout_s=...`):

```python
            device=device,
            use_fp16=_as_bool(_get("use_fp16", False, "SEBI_RAG_", svc)),
            encode_batch_size=int(_get("encode_batch_size", 32, "SEBI_RAG_", svc)),
            embed_backend=str(_get("embed_backend", "torch", "SEBI_RAG_", svc)),
            rerank_backend=str(_get("rerank_backend", "torch", "SEBI_RAG_", svc)),
```

- [ ] **Step 6: Document the keys in `config.toml`**

In `config.toml`, add to the `[service]` block (after `timeout_s = 30`):

```toml
# Apple-Silicon compute (Track B). Omit `device` to auto-detect (mps else cpu).
# device = "mps"                                       # force: mps | cpu | cuda
use_fp16 = false                                       # fp16 on mps/cuda (never bf16); flipped by eval gate
encode_batch_size = 32                                 # embed/rerank batch size (MPS prefers larger)
embed_backend = "torch"                                # torch | mlx  (mlx = eval-gated, Phase 2)
rerank_backend = "torch"                               # torch | mlx  (mlx = eval-gated, Phase 2)
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `PYTHONPATH=src pytest tests/test_settings.py -v`
Expected: PASS — new compute tests plus existing precedence tests green.

- [ ] **Step 8: Commit**

```bash
git add src/sebi_rag/settings.py config.toml tests/test_settings.py
git commit -m "$(cat <<'EOF'
feat(settings): add device/use_fp16/batch/backend compute knobs

Resolved via the existing env>toml>default chain; use_fp16 ships False
(fp32) until the eval gate proves parity. Documented in config.toml.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Wire compute knobs into embedder, reranker, and pipeline build

**Files:**
- Modify: `src/sebi_rag/embeddings.py` (`BGEM3Embedder.__init__` L54-65; `encode` L67-72)
- Modify: `src/sebi_rag/rerank.py` (`CrossEncoderReranker.__init__` L121-126; `rerank` L128-134)
- Modify: `src/sebi_rag/api.py` (add `_compute_kwargs`; `build_default_pipeline` L88 & L111)
- Test: `tests/test_api.py`

**Interfaces:**
- Consumes: `pick_device`, `should_use_fp16` (Task 1); `Settings.device/use_fp16/encode_batch_size` (Task 2).
- Produces: `_compute_kwargs(s: Settings) -> dict` returning `{"device": str, "use_fp16": bool, "batch_size": int}`; `BGEM3Embedder(model_path, device, use_fp16, batch_size)` and `CrossEncoderReranker(model, device, use_fp16, batch_size)`.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_api.py`:

```python
def test_compute_kwargs_cpu_disables_fp16():
    from sebi_rag.api import _compute_kwargs
    from sebi_rag.settings import Settings
    s = Settings(corpus_path="c", index_dir="i",
                 device="cpu", use_fp16=True, encode_batch_size=16)
    assert _compute_kwargs(s) == {"device": "cpu", "use_fp16": False, "batch_size": 16}


def test_compute_kwargs_mps_keeps_fp16():
    from sebi_rag.api import _compute_kwargs
    from sebi_rag.settings import Settings
    s = Settings(corpus_path="c", index_dir="i",
                 device="mps", use_fp16=True, encode_batch_size=8)
    assert _compute_kwargs(s) == {"device": "mps", "use_fp16": True, "batch_size": 8}


def test_embedder_reranker_accept_compute_kwargs():
    import inspect
    from sebi_rag.embeddings import BGEM3Embedder
    from sebi_rag.rerank import CrossEncoderReranker
    for cls in (BGEM3Embedder, CrossEncoderReranker):
        params = set(inspect.signature(cls.__init__).parameters)
        assert {"device", "use_fp16", "batch_size"} <= params
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=src pytest tests/test_api.py::test_compute_kwargs_cpu_disables_fp16 tests/test_api.py::test_embedder_reranker_accept_compute_kwargs -v`
Expected: FAIL — `ImportError: cannot import name '_compute_kwargs'` and signature guard fails.

- [ ] **Step 3: Update `BGEM3Embedder`**

In `src/sebi_rag/embeddings.py`, change `BGEM3Embedder.__init__` signature and the model construction:

```python
    def __init__(self, model_path: str = "BAAI/bge-m3", device: str = "mps",
                 use_fp16: bool = False, batch_size: int = 32) -> None:
        from FlagEmbedding import BGEM3FlagModel
        from huggingface_hub import snapshot_download

        # Pre-fetch without the 2.3 GB onnx variant we never use (Step 10).
        if "/" in model_path and not model_path.startswith(("/", ".", "~")):
            model_path = snapshot_download(
                model_path,
                ignore_patterns=["onnx/*", "imgs/*", "*.onnx", "*.onnx_data"],
            )
        self._m = BGEM3FlagModel(model_path, use_fp16=use_fp16, devices=device)
        self._batch_size = batch_size
        self.dim = 1024
```

And thread the batch size through `encode`:

```python
    def encode(self, texts: list[str]) -> np.ndarray:
        out = self._m.encode(texts, return_dense=True,
                             batch_size=self._batch_size)["dense_vecs"]
        v = np.asarray(out, dtype="float32")
        norms = np.linalg.norm(v, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return v / norms
```

- [ ] **Step 4: Update `CrossEncoderReranker`**

In `src/sebi_rag/rerank.py`:

```python
    def __init__(
        self, model: str = "BAAI/bge-reranker-v2-m3", device: str = "mps",
        use_fp16: bool = False, batch_size: int = 32
    ) -> None:
        from sentence_transformers import CrossEncoder

        model_kwargs = {"torch_dtype": "float16"} if use_fp16 else {}
        self._ce = CrossEncoder(model, device=device, model_kwargs=model_kwargs)
        self._batch_size = batch_size

    def rerank(self, query: str, candidates: list[Chunk]) -> list[tuple[Chunk, float]]:
        if not candidates:
            return []
        scores = self._ce.predict([[query, c.text] for c in candidates],
                                  batch_size=self._batch_size)
        paired = list(zip(candidates, (float(s) for s in scores)))
        paired.sort(key=lambda cs: -cs[1])
        return paired
```

- [ ] **Step 5: Add `_compute_kwargs` and wire `build_default_pipeline`**

In `src/sebi_rag/api.py`, add above `build_default_pipeline`:

```python
def _compute_kwargs(s: Settings) -> dict:
    """Resolve device/fp16/batch for the torch embedder + reranker."""
    from .device import pick_device, should_use_fp16
    device = pick_device(s.device)
    return {"device": device,
            "use_fp16": should_use_fp16(device, s.use_fp16),
            "batch_size": s.encode_batch_size}
```

In `build_default_pipeline`, replace the hardcoded constructions:
- `embedder = BGEM3Embedder(device="mps")` → 
  ```python
      ck = _compute_kwargs(s)
      embedder = BGEM3Embedder(**ck)
  ```
- `reranker=CrossEncoderReranker(device="mps"),` → `reranker=CrossEncoderReranker(**ck),`

(`ck` is computed once, after `s = Settings.load()`, and reused for both.)

- [ ] **Step 6: Run tests to verify they pass**

Run: `PYTHONPATH=src pytest tests/test_api.py -v && make test`
Expected: PASS — new `_compute_kwargs`/signature tests green; full offline suite green (offline tests use HashEmbedder/LexicalReranker, never these classes).

- [ ] **Step 7: (Optional) Integration smoke — real fp16 encode**

Add under the `integration` marker in `tests/test_api.py` (only run with `pytest -m integration`, needs weights):

```python
import pytest


@pytest.mark.integration
def test_bge_fp16_encode_is_normalized():
    from sebi_rag.embeddings import BGEM3Embedder
    emb = BGEM3Embedder(device="mps", use_fp16=True, batch_size=4)
    v = emb.encode(["nomination norms for demat accounts", "unrelated text"])
    assert v.shape == (2, 1024)
    import numpy as np
    assert np.allclose(np.linalg.norm(v, axis=1), 1.0, atol=1e-3)
```

Run (manual, on Apple Silicon): `PYTHONPATH=src pytest -m integration tests/test_api.py::test_bge_fp16_encode_is_normalized -v`
Expected: PASS.

- [ ] **Step 8: Update the graph and commit**

```bash
graphify update .
git add src/sebi_rag/embeddings.py src/sebi_rag/rerank.py src/sebi_rag/api.py tests/test_api.py
git commit -m "$(cat <<'EOF'
feat(compute): wire device/fp16/batch into embedder, reranker, build

_compute_kwargs resolves device via device.pick_device and fp16 via
should_use_fp16; build_default_pipeline passes them instead of "mps".
Behavior-preserving (use_fp16 defaults False until the eval gate).

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: MPS unified-memory OOM hygiene (Makefile)

**Files:**
- Modify: `Makefile` (`ENV` line, L3)

**Interfaces:** none (environment only).

- [ ] **Step 1: Add the watermark ratio to `ENV`**

In `Makefile`, change line 3 from:

```make
ENV  := HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src
```

to:

```make
ENV  := HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 PYTORCH_ENABLE_MPS_FALLBACK=1 PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0 PYTHONPATH=src
```

`PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0` disables the upper allocation watermark — the documented guard against unified-memory OOM kernel panics during large encodes (a full-corpus encode previously OOM'd).

- [ ] **Step 2: Verify**

Run: `grep -n "PYTORCH_MPS_HIGH_WATERMARK_RATIO" Makefile && make test`
Expected: the grep prints line 3; `make test` stays green.

- [ ] **Step 3: Commit**

```bash
git add Makefile
git commit -m "$(cat <<'EOF'
chore(make): set PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0 (OOM guard)

Prevents unified-memory OOM kernel panics on large MPS encodes.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: fp16 A/B eval gate (sets the `use_fp16` default)

**Files:**
- Modify (conditional): `src/sebi_rag/settings.py`, `config.toml` (flip default to `True` only if parity holds)
- Create: `reports/2026-07-22-fp16-mps-ab.md` (results)

**Interfaces:** none — an evaluation gate that decides a default value.

> This is an evaluation task on real weights/corpus (Apple Silicon). It has no unit test; the deliverable is a recorded A/B result and the resulting default decision.

- [ ] **Step 1: Baseline (fp32) retrieval run**

Ensure `use_fp16` is effectively False (default). Run:

```bash
make bench-retrieval
```

Record the recall/nDCG summary and the TREC runfile path it prints. Copy the metrics into `reports/2026-07-22-fp16-mps-ab.md` under a "Baseline fp32" heading.

- [ ] **Step 2: Candidate (fp16) retrieval run**

Rebuild/encode with fp16 via env override and re-run:

```bash
SEBI_RAG_USE_FP16=true make reindex
SEBI_RAG_USE_FP16=true make bench-retrieval
SEBI_RAG_USE_FP16=true make eval-asof ASOF_OUT=fp16
```

Record recall/nDCG + the as-of golden pass rate under a "Candidate fp16" heading in the same report.

- [ ] **Step 3: Decision**

Apply the project's promotion rule (no golden regression; recall within CI/noise of baseline):
- **If parity holds:** flip the default — set `Settings.use_fp16` default to `True` (settings.py) and `use_fp16 = true` in `config.toml`. Note the speed delta in the report.
- **If regression:** keep `use_fp16 = false`; document that fp16 stays opt-in via `SEBI_RAG_USE_FP16=true`.

Restore the index to the chosen default afterward (`make reindex` with the final setting) so `data/index` matches the shipped default.

- [ ] **Step 4: Commit**

```bash
git add reports/2026-07-22-fp16-mps-ab.md src/sebi_rag/settings.py config.toml
git commit -m "$(cat <<'EOF'
eval(compute): fp16-on-MPS A/B gate + default decision

Records fp32 vs fp16 retrieval recall/nDCG + as-of golden; sets the
use_fp16 default per the parity outcome.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: MLX-native backend spike (implementation deferred)

**Files:**
- Create: `docs/superpowers/specs/2026-07-22-mlx-backend-spike-findings.md`
- Scratch only: use the session scratchpad for throwaway spike code; do NOT add production modules or deps in this task.

**Interfaces:** none — the deliverable is a findings doc that pins the library + exact API + parity numbers, enabling a concrete follow-up plan.

> The MLX-native embeddings/reranker backend (design B5) cannot be written placeholder-free until a specific library and its call signatures are verified. This task de-risks it; the concrete `embeddings_mlx.py` / `rerank_mlx.py` implementation gets its own follow-up plan.

- [ ] **Step 1: Pick and install a candidate embedder library (scratch env)**

Candidates from research: `mlx-embeddings` (PyPI), BGE-M3-mlx port, `embed-rerank`. In a scratch venv or `uv pip install --python .venv`, install one candidate, e.g.:

```bash
uv pip install mlx-embeddings
```

- [ ] **Step 2: Smoke-encode and capture the exact API**

Write a throwaway script in the scratchpad that loads BGE-M3 (or nearest MLX port), encodes two SEBI-style strings, and prints: the load call, the encode call, output shape, and whether output is L2-normalized. Confirm it can produce a **1024-dim dense** vector matching `Embedder`'s contract (`dim`, `encode(texts) -> (n, 1024)` L2-normalized).

- [ ] **Step 3: Repeat for a reranker candidate**

Install/load a bge-reranker-v2-m3 MLX port (e.g. from `MemTensor/mlx-memos`) or `embed-rerank`. Capture the exact predict/score call producing per-pair relevance scores compatible with `.rerank(query, candidates) -> list[tuple[Chunk, float]]`.

- [ ] **Step 4: Mini parity check vs torch**

On the probe queries in `eval/probes/`, compare top-k retrieval overlap / reranker ordering between the torch backend and the MLX candidate. Record whether recall/ordering is at parity.

- [ ] **Step 5: Write the findings doc**

Create `docs/superpowers/specs/2026-07-22-mlx-backend-spike-findings.md` capturing:
- Chosen embedder + reranker library names and pinned versions.
- The exact load + encode/score API calls (copy-paste-ready).
- Whether outputs meet the `Embedder` protocol / `.rerank()` contract (dim, normalization).
- Parity results vs torch on the probe set.
- **Go / no-go** recommendation and any blockers.

- [ ] **Step 6: Commit**

```bash
git add docs/superpowers/specs/2026-07-22-mlx-backend-spike-findings.md
git commit -m "$(cat <<'EOF'
spike(mlx): pin MLX embedder/reranker API + torch parity findings

Findings doc for the deferred MLX-native backend; concrete impl gets a
follow-up plan. No production deps/modules added.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: ADR — ANE/NPU declined

**Files:**
- Create: `docs/adr-003-ane-declined.md`

**Interfaces:** none — decision record.

- [ ] **Step 1: Write the ADR**

Create `docs/adr-003-ane-declined.md`:

```markdown
# ADR-003: Apple Neural Engine (ANE/NPU) declined for the local RAG pipeline

**Date:** 2026-07-22
**Status:** Accepted

## Context
The local pipeline runs on Apple Silicon. Beyond the GPU (MPS/MLX) already in
use, the Apple Neural Engine (ANE) is available as a third compute engine. We
evaluated whether to target it for the embedder/reranker (and generation).

## Decision
We do NOT target the ANE. The pipeline stays on MLX (generation) and MPS/MLX
(embeddings/reranker).

## Rationale (as of 22 July 2026)
- ANE is an **energy-efficiency** engine (~2 W vs ~20 W GPU), not a throughput
  engine. For raw speed on a plugged-in Mac, MLX on the GPU wins (published
  comparisons: ~93+ tok/s vs ~9 tok/s on an 8B model).
- ANE access requires **Core ML conversion** (apple/ml-ane-transformers) with
  finicky operator support and significant engineering cost.
- This is a **server RAG on plugged-in Apple Silicon** — throughput-oriented,
  not battery/thermal/always-on constrained. ANE does not win the metric that
  matters here.

## Consequences
- No Core ML conversion pipeline to maintain.
- Revisit ONLY if battery life, thermal envelope, or always-on background
  inference becomes an explicit goal.

## References
See docs/superpowers/specs/2026-07-22-spaces-ux-and-apple-silicon-compute-design.md
(Sources — ANE/NPU) for the underlying research.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr-003-ane-declined.md
git commit -m "$(cat <<'EOF'
docs(adr): ADR-003 decline ANE/NPU for the local RAG pipeline

Energy play, not throughput; Core ML conversion cost unjustified for a
plugged-in server RAG. Revisit only if battery/always-on becomes a goal.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review (completed by plan author)

- **Spec coverage:** B1 → Task 1; B2 → Task 2; B3 wiring → Task 3; B3 fp16 gate → Task 5; B4 → Task 4; B5 (spike) → Task 6 (impl deferred per user decision); B6 → Task 7; B7 tests → Tasks 1-3 (+ integration smoke). ✅
- **Placeholders:** none — every code step shows concrete code; Task 5/6 are evaluation/spike tasks whose deliverables (reports/findings) are legitimately produced at execution, with exact commands. ✅
- **Type consistency:** `_compute_kwargs -> {"device","use_fp16","batch_size"}` matches the `BGEM3Embedder`/`CrossEncoderReranker` kwargs added in Task 3; `pick_device`/`should_use_fp16` signatures identical across Task 1 def, Task 1 tests, and Task 3 usage; new `Settings` field names identical across Task 2 dataclass, `load`, config.toml, and Task 3 consumption. ✅
- **Deviation noted:** `use_fp16` field default ships `False` (not spec's `True`) to preserve behavior until the Task 5 gate — reconciled with the spec's "default set by the A/B result." ✅

## Execution Handoff

Two execution options:
1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks.
2. **Inline Execution** — batch execution with checkpoints in this session.
