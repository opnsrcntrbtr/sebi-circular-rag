# Track A — Spaces UX Port Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring the proven Hugging Face Spaces demo UX (mode selector, as-of date, advisory draft, richer output surfacing) into the local Apple-Silicon pipeline, keeping the thin-client architecture.

**Architecture:** The local Gradio UI (`src/sebi_rag/ui.py`) stays a pure HTTP client that talks to the FastAPI `/query` endpoint (`src/sebi_rag/api.py`). The one backend change is a new `mode` field on `QueryRequest` plus a per-mode pipeline cache that swaps in `ExtractiveStubGenerator` for `retrieval_only` (mirroring `app.py:get_pipeline`). Everything else is presentation wired in the UI: as-of validation, the retrieval-only banner, the advisory draft, and an "Advanced outputs" accordion surfacing response fields the API already returns.

**Tech Stack:** Python 3.12, FastAPI + Pydantic v2, Gradio, httpx, pytest (`fastapi.testclient`), `uv` for deps, `make test` for the offline suite.

## Global Constraints

- **Two-parallel-paths rule:** edit ONLY local modules. This plan touches `src/sebi_rag/api.py`, `src/sebi_rag/ui.py`, `tests/test_api.py`, and a new `tests/test_ui.py`. Do NOT edit `app.py` or any `*_spaces.py`.
- **Thin client:** `ui.py` remains an HTTP client; no pipeline/model imports in it. All new logic routes through `/query`.
- **`QueryResponse` is unchanged** — it already returns `confidence`, `draft_answer`, `retrieved`.
- **Offline tests only for CI:** `make test` runs `pytest -q -m "not integration"`. New tests must not load real models (use `HashEmbedder`/`LexicalReranker`/`ExtractiveStubGenerator` fixtures or monkeypatched httpx).
- **Run commands via `make` or with env set:** the Makefile sets `PYTHONPATH=src` (+ `HF_HUB_DISABLE_XET=1`, `TOKENIZERS_PARALLELISM=false`, `OMP_NUM_THREADS=1`, `PYTORCH_ENABLE_MPS_FALLBACK=1`). For ad-hoc pytest use `PYTHONPATH=src pytest ...`.
- **Commit trailer:** end every commit message with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- **After code changes:** run `graphify update .` to keep the graph current (AST-only, no API cost).

---

## File Structure

| File | Responsibility |
|---|---|
| `src/sebi_rag/api.py` (modify) | Add `QueryRequest.mode`; per-mode pipeline cache; route `/query` by mode |
| `src/sebi_rag/ui.py` (modify) | `_parse_as_of` helper; `submit_query` rewrite (new inputs, banner, advisory, advanced outputs); `build_ui` layout regroup |
| `tests/test_api.py` (modify) | Distinct-generator fixture + mode routing / 422 / shared-retrieval tests |
| `tests/test_ui.py` (create) | Unit tests for `_parse_as_of` and `submit_query` (monkeypatched httpx) |

---

## Task 1: Backend — `mode` field + per-mode pipeline routing

**Files:**
- Modify: `src/sebi_rag/api.py` (`QueryRequest` ~L37-43; `create_app` internals ~L144-201)
- Test: `tests/test_api.py` (add fixture ~after L55; add tests ~after L90)

**Interfaces:**
- Consumes: `create_app(pipeline_factory)`; `RAGPipeline` (frozen dataclass); `ExtractiveStubGenerator` (in `sebi_rag.generate`, `.generate(query, contexts) -> str`, returns `contexts[0].text`).
- Produces: `QueryRequest.mode: Literal["rag", "retrieval_only"] = "rag"`; `/query` routes by `req.mode`; internal `pipe(mode: str) -> RAGPipeline` selecting a per-mode cached pipeline.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_api.py` (after `_slow_pipeline`, ~L55). This fixture uses a *distinct* generator (not the stub) so the `retrieval_only` swap is observable:

```python
class _CannedGenerator:
    def generate(self, query, contexts):
        return "CANNED-LLM-ANSWER"


def _distinct_pipeline() -> RAGPipeline:
    chunks = hierarchical_chunk("Nomination norms for demat accounts.",
                                CircularMeta(circular_number="SEBI/HO/Z/P/CIR/2024/7"))
    return RAGPipeline.build(
        chunks=chunks, embedder=HashEmbedder(128), reranker=LexicalReranker(),
        generator=_CannedGenerator(), abstain_threshold=0.05,
        lineage=build_lineage([{"circular_number": "SEBI/HO/Z/P/CIR/2024/7",
                                "text": "nomination norms"}]))


_distinct_client = TestClient(create_app(_distinct_pipeline))


def test_mode_defaults_to_rag():
    r = _distinct_client.post("/query", json={"question": "nomination norms"})
    assert r.status_code == 200
    assert r.json()["answer"] == "CANNED-LLM-ANSWER"


def test_mode_retrieval_only_swaps_generator():
    r = _distinct_client.post(
        "/query", json={"question": "nomination norms", "mode": "retrieval_only"})
    assert r.status_code == 200
    body = r.json()
    # ExtractiveStubGenerator returns the top context text, never the canned LLM string
    assert body["answer"] != "CANNED-LLM-ANSWER"
    assert "nomination" in body["answer"].lower()


def test_mode_invalid_rejected_422():
    r = _distinct_client.post(
        "/query", json={"question": "nomination norms", "mode": "bogus"})
    assert r.status_code == 422


def test_mode_retrieval_only_shares_retrieval():
    q = {"question": "nomination norms"}
    rag = _distinct_client.post("/query", json={**q, "mode": "rag"}).json()
    ret = _distinct_client.post("/query", json={**q, "mode": "retrieval_only"}).json()
    assert rag["citations"] == ret["citations"]  # same retriever/reranker/lineage
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=src pytest tests/test_api.py::test_mode_retrieval_only_swaps_generator tests/test_api.py::test_mode_invalid_rejected_422 -v`
Expected: FAIL — `test_mode_invalid_rejected_422` fails (extra field ignored, returns 200) and `test_mode_retrieval_only_swaps_generator` fails (returns "CANNED-LLM-ANSWER").

- [ ] **Step 3: Add the `mode` field to `QueryRequest`**

In `src/sebi_rag/api.py`, ensure `Literal` is imported (top of file, `from typing import ...`); if not present add it. Then modify `QueryRequest` (currently ends at `as_of`):

```python
class QueryRequest(BaseModel):
    question: str
    # ADR-002: top_k=0 previously slipped through and caused a silent
    # no-context abstention; degenerate values are now a 422.
    top_k: int | None = Field(default=None, ge=1, le=10)
    advisory: bool = False  # opt-in low-confidence draft on gate failure
    as_of: str | None = None  # date-scoped query: score against law as of date
    mode: Literal["rag", "retrieval_only"] = "rag"  # retrieval_only swaps in the stub generator
```

- [ ] **Step 4: Add per-mode routing in `create_app`**

In `create_app`, replace the single-pipeline `pipe()` helper (currently `def pipe() -> RAGPipeline: if "p" not in state: state["p"] = pipeline_factory(); return state["p"]`) with a mode-aware version that mirrors `app.py:get_pipeline`:

```python
    def pipe(mode: str = "rag") -> RAGPipeline:
        if "rag" not in state:
            state["rag"] = pipeline_factory()
        if mode == "retrieval_only" and "retrieval_only" not in state:
            import dataclasses

            from .generate import ExtractiveStubGenerator
            state["retrieval_only"] = dataclasses.replace(
                state["rag"], generator=ExtractiveStubGenerator())
        return state[mode if mode == "retrieval_only" else "rag"]
```

Update the two existing callers that used `pipe()` with no args:
- `/ready` handler: `pipe()` → unchanged (defaults to `"rag"`), and `return {"ready": "rag" in state}`.
- `/health` handler: `p = pipe()` → unchanged.
- `/query` handler: `p = pipe(req.mode)`.

The `state` dict type annotation stays `dict[str, RAGPipeline]`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `PYTHONPATH=src pytest tests/test_api.py -v`
Expected: PASS — all new mode tests plus existing tests (`test_health`, `test_query_grounded_with_metadata_and_latency`, `test_ready` etc.) green.

- [ ] **Step 6: Commit**

```bash
git add src/sebi_rag/api.py tests/test_api.py
git commit -m "$(cat <<'EOF'
feat(api): add mode=retrieval_only with per-mode pipeline routing

QueryRequest.mode swaps in ExtractiveStubGenerator via a cached
dataclasses.replace of the base pipeline, mirroring app.py:get_pipeline.
Shared retriever/reranker/lineage; invalid mode -> 422.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: UI logic — `_parse_as_of` + `submit_query` rewrite

**Files:**
- Modify: `src/sebi_rag/ui.py` (`submit_query` ~L6-63; add `_parse_as_of` above it)
- Test: `tests/test_ui.py` (create)

**Interfaces:**
- Consumes: `/query` JSON response fields — `answer`, `citations_meta` (list of `{circular, status, superseded_by}`), `latency_ms`, `faithfulness`, `certainty`, `abstained`, `abstention_reason`, `superseded`, `unsupported_citations`, `confidence`, `draft_answer`, `retrieved`.
- Produces: `_parse_as_of(raw: str) -> str | None`; `submit_query(question, api_url, api_key, top_k, mode, as_of_raw, advisory) -> tuple` of **10** values in this order: `(answer_md, citations_df, latency, faithfulness, certainty_str, superseded_json, unsupported, confidence_json, draft_md, retrieved_json)`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_ui.py`:

```python
"""Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)."""
from __future__ import annotations

import json

import pytest

from sebi_rag import ui


def test_parse_as_of_empty_is_none():
    assert ui._parse_as_of("") is None
    assert ui._parse_as_of("   ") is None


def test_parse_as_of_valid_iso():
    assert ui._parse_as_of("2025-01-10") == "2025-01-10"


def test_parse_as_of_malformed_raises_valueerror():
    with pytest.raises(ValueError):
        ui._parse_as_of("10-01-2025")


class _Resp:
    status_code = 200

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


_CANNED = {
    "answer": "The nomination norms are X.",
    "citations_meta": [{"circular": "SEBI/2025/9", "status": "in_force", "superseded_by": []}],
    "latency_ms": 12.5,
    "faithfulness": 0.91,
    "certainty": "high",
    "abstained": False,
    "abstention_reason": "",
    "superseded": {},
    "unsupported_citations": [],
    "confidence": {"score": 0.8},
    "draft_answer": "",
    "retrieved": ["SEBI/2025/9#0"],
}


def test_submit_query_malformed_as_of_short_circuits(monkeypatch):
    called = {"n": 0}

    def _boom(*a, **k):
        called["n"] += 1
        raise AssertionError("httpx.post must not be called on bad as_of")

    monkeypatch.setattr(ui.httpx, "post", _boom)
    out = ui.submit_query("q", "http://x/query", "", 3, "rag", "10-01-2025", False)
    assert out[0].startswith("**Error:**")
    assert called["n"] == 0
    assert len(out) == 10


def test_submit_query_sends_new_fields_and_returns_ten(monkeypatch):
    seen = {}

    def _fake_post(url, json, headers, timeout):  # noqa: A002 - mirror httpx kwarg
        seen.update(json)
        return _Resp(_CANNED)

    monkeypatch.setattr(ui.httpx, "post", _fake_post)
    out = ui.submit_query("q", "http://x/query", "", 5, "rag", "2025-01-10", True)
    assert seen["mode"] == "rag"
    assert seen["advisory"] is True
    assert seen["as_of"] == "2025-01-10"
    assert seen["top_k"] == 5
    assert len(out) == 10
    assert out[0] == "The nomination norms are X."  # no banner in rag mode


def test_submit_query_retrieval_only_prepends_banner(monkeypatch):
    monkeypatch.setattr(ui.httpx, "post", lambda *a, **k: _Resp(_CANNED))
    out = ui.submit_query("q", "http://x/query", "", 3, "retrieval_only", "", False)
    assert out[0].startswith("**Retrieval-only mode**")
    assert "The nomination norms are X." in out[0]


def test_submit_query_surfaces_confidence_and_retrieved(monkeypatch):
    monkeypatch.setattr(ui.httpx, "post", lambda *a, **k: _Resp(_CANNED))
    out = ui.submit_query("q", "http://x/query", "", 3, "rag", "", False)
    confidence_json, draft_md, retrieved_json = out[7], out[8], out[9]
    assert json.loads(confidence_json) == {"score": 0.8}
    assert draft_md == ""  # empty draft renders nothing
    assert json.loads(retrieved_json) == ["SEBI/2025/9#0"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=src pytest tests/test_ui.py -v`
Expected: FAIL — `AttributeError: module 'sebi_rag.ui' has no attribute '_parse_as_of'` and `submit_query` signature mismatch.

- [ ] **Step 3: Rewrite the logic layer of `ui.py`**

Replace the top of `src/sebi_rag/ui.py` (imports through the end of `submit_query`, i.e. lines 1-63) with:

```python
import json
from datetime import date

import gradio as gr
import httpx
import pandas as pd

_EMPTY_DF_COLS = ["Circular", "Status", "Superseded By"]
_RETRIEVAL_ONLY_BANNER = (
    "**Retrieval-only mode** — no LLM generation; the text below is the "
    "top retrieved excerpt. Evaluate the citations and metadata.\n\n"
)


def _empty_outputs(message: str) -> tuple:
    """Ten-slot output tuple for early returns (matches build_ui outputs order)."""
    return (message, pd.DataFrame(columns=_EMPTY_DF_COLS),
            "", "", "", "", "", "", "", "")


def _parse_as_of(raw: str) -> str | None:
    """Normalise the optional as-of field: empty -> None, else strict ISO
    YYYY-MM-DD. Raises ValueError for anything else (caller shows a message)."""
    raw = (raw or "").strip()
    if not raw:
        return None
    return date.fromisoformat(raw).isoformat()


def submit_query(question: str, api_url: str, api_key: str, top_k: float,
                 mode: str, as_of_raw: str, advisory: bool) -> tuple:
    if not question.strip():
        return _empty_outputs("Please enter a question.")

    try:
        as_of = _parse_as_of(as_of_raw)
    except ValueError:
        return _empty_outputs(
            "**Error:** 'As of date' must be YYYY-MM-DD (e.g. 2025-01-10).")

    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key

    payload = {"question": question, "top_k": int(top_k),
               "mode": mode, "advisory": bool(advisory), "as_of": as_of}

    try:
        resp = httpx.post(api_url, json=payload, headers=headers, timeout=120.0)
        if resp.status_code != 200:
            return _empty_outputs(
                f"**Error:** API returned status code {resp.status_code}\n\n{resp.text}")
        data = resp.json()
    except httpx.TimeoutException:
        return _empty_outputs("**Request Failed:** API timed out.")
    except Exception as e:  # noqa: BLE001 - surface, don't crash the UI
        return _empty_outputs(f"**Request Failed:** {str(e)}")

    df_rows = []
    for item in data.get("citations_meta", []):
        superseded_by = ", ".join(item.get("superseded_by", []))
        df_rows.append({
            "Circular": item.get("circular"),
            "Status": item.get("status"),
            "Superseded By": superseded_by if superseded_by else "-",
        })
    df = pd.DataFrame(df_rows) if df_rows else pd.DataFrame(columns=_EMPTY_DF_COLS)

    latency = f"{data.get('latency_ms', 0)} ms"
    faithfulness = f"{data.get('faithfulness', 0.0):.2f}"

    certainty_str = data.get("certainty", "unknown")
    abstained = data.get("abstained", False)
    if abstained:
        certainty_str += f" (Abstained: {data.get('abstention_reason', '')})"

    superseded = json.dumps(data.get("superseded", {}), indent=2)
    unsupported = ", ".join(data.get("unsupported_citations", [])) or "None"

    answer_text = data.get("answer", "")
    if mode == "retrieval_only" and not abstained:
        answer_text = _RETRIEVAL_ONLY_BANNER + answer_text

    confidence_json = json.dumps(data.get("confidence", {}), indent=2)
    draft = data.get("draft_answer", "") or ""
    draft_md = (f"**Advisory draft — not authoritative**\n\n{draft}" if draft else "")
    retrieved_json = json.dumps(data.get("retrieved", []), indent=2)

    return (answer_text, df, latency, faithfulness, certainty_str, superseded,
            unsupported, confidence_json, draft_md, retrieved_json)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=src pytest tests/test_ui.py -v`
Expected: PASS — all 8 tests green.

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/ui.py tests/test_ui.py
git commit -m "$(cat <<'EOF'
feat(ui): route mode/as_of/advisory + surface advanced outputs

submit_query now validates as_of client-side, sends mode/advisory/as_of
to /query, prepends the retrieval-only banner, renders the advisory draft,
and returns confidence/draft/retrieved. First test coverage for ui.py.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: UI presentation — new widgets + grouped-accordion layout

**Files:**
- Modify: `src/sebi_rag/ui.py` (`build_ui` ~L65-115)
- Test: import smoke check (`build_ui` constructs without error) + `make test`

**Interfaces:**
- Consumes: `submit_query(question, api_url, api_key, top_k, mode, as_of_raw, advisory)` returning the 10-tuple from Task 2.
- Produces: a `gr.Blocks` whose `submit_btn.click` inputs/outputs match `submit_query`'s signature and 10-value return exactly.

- [ ] **Step 1: Write the failing smoke test**

Add to `tests/test_ui.py`:

```python
def test_build_ui_constructs():
    demo = ui.build_ui()
    assert demo is not None
```

- [ ] **Step 2: Run it to confirm current state**

Run: `PYTHONPATH=src pytest tests/test_ui.py::test_build_ui_constructs -v`
Expected: PASS with the *old* `build_ui` (it still constructs) — this smoke test guards against wiring breakage while you rewrite. Proceed to rewrite; it must stay PASS.

- [ ] **Step 3: Rewrite `build_ui` with the grouped-accordion layout**

Replace `build_ui` (lines ~65-115) in `src/sebi_rag/ui.py` with:

```python
def build_ui():
    with gr.Blocks(title="SEBI Circular RAG", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# SEBI Circular RAG")
        gr.Markdown("Local-first, Apple-Silicon Retrieval-Augmented Generation "
                    "over Indian SEBI circulars.")

        with gr.Row():
            with gr.Column(scale=3):
                question_input = gr.Textbox(
                    label="Question",
                    placeholder="Ask a question about SEBI circulars (e.g. 'What are "
                                "the modified norms for nomination in demat accounts?')...",
                    lines=3,
                )
                submit_btn = gr.Button("Submit Query", variant="primary")
                answer_output = gr.Markdown(label="Answer")
                gr.Markdown("### Citations")
                citations_df = gr.Dataframe(
                    headers=["Circular", "Status", "Superseded By"],
                    interactive=False, wrap=True,
                )

            with gr.Column(scale=1):
                with gr.Accordion("Connection", open=True):
                    api_url = gr.Textbox(label="API Endpoint URL",
                                         value="http://127.0.0.1:8000/query")
                    api_key = gr.Textbox(label="API Key", type="password",
                                         placeholder="Required if server uses auth")

                with gr.Accordion("Query controls", open=True):
                    top_k = gr.Slider(minimum=1, maximum=10, value=3, step=1,
                                      label="Top K Citations")
                    mode = gr.Radio(
                        choices=["rag", "retrieval_only"], value="rag", label="Mode",
                        info="Full RAG answer, or retrieval-only academic benchmark "
                             "(citations + metadata, no LLM).",
                    )
                    as_of_input = gr.Textbox(
                        label="As of date (optional)",
                        placeholder="YYYY-MM-DD — answer per the law in force on this date",
                        max_lines=1,
                    )
                    advisory = gr.Checkbox(
                        label="Advisory draft on gate failure", value=False,
                        info="Opt-in low-confidence draft when the abstention gate trips.",
                    )

                with gr.Accordion("Metadata", open=True):
                    latency_out = gr.Textbox(label="Latency", interactive=False)
                    faithfulness_out = gr.Textbox(label="Faithfulness", interactive=False)
                    certainty_out = gr.Textbox(label="Certainty & Abstention",
                                               interactive=False)
                    superseded_out = gr.Code(label="Superseded Warnings",
                                             language="json", interactive=False)
                    unsupported_out = gr.Textbox(label="Unsupported Citations",
                                                 interactive=False)

                with gr.Accordion("Advanced outputs", open=False):
                    confidence_out = gr.Code(label="Confidence", language="json",
                                             interactive=False)
                    draft_out = gr.Markdown(label="Advisory Draft")
                    retrieved_out = gr.Code(label="Retrieved (doc ids)",
                                            language="json", interactive=False)

        submit_btn.click(
            fn=submit_query,
            inputs=[question_input, api_url, api_key, top_k, mode, as_of_input, advisory],
            outputs=[answer_output, citations_df, latency_out, faithfulness_out,
                     certainty_out, superseded_out, unsupported_out,
                     confidence_out, draft_out, retrieved_out],
        )

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(server_name="127.0.0.1", server_port=7860)
```

Note: the `inputs` list order (question, api_url, api_key, top_k, mode, as_of, advisory) and the `outputs` list order (10 items) MUST match `submit_query`'s parameter order and 10-value return exactly.

- [ ] **Step 4: Run the smoke test + full offline suite**

Run: `PYTHONPATH=src pytest tests/test_ui.py -v && make test`
Expected: PASS — `test_build_ui_constructs` still passes; full offline suite green.

- [ ] **Step 5: Manual verification (one-time, optional but recommended)**

In one terminal: `make serve` (needs `SEBI_RAG_API_KEY` if auth on). In another: `PYTHONPATH=src python -m sebi_rag.ui` → open http://127.0.0.1:7860. Confirm: as-of malformed date shows the friendly error without a request; `retrieval_only` shows the banner; Advanced outputs accordion is collapsed and populates on submit.

- [ ] **Step 6: Update the graph and commit**

```bash
graphify update .
git add src/sebi_rag/ui.py tests/test_ui.py
git commit -m "$(cat <<'EOF'
feat(ui): grouped-accordion layout with mode/as-of/advisory + advanced outputs

Regroups the sidebar into Connection / Query controls / Metadata /
Advanced outputs (collapsed) and wires the new inputs and outputs.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review (completed by plan author)

- **Spec coverage:** A1 backend mode routing → Task 1. A2 submit_query/banner/advisory/as_of validation → Task 2. A3 layout → Task 3. A5 tests → Tasks 1-3. A6 out-of-scope respected (no Spaces edits). ✅
- **Placeholders:** none — every step has concrete code/commands. ✅
- **Type consistency:** `submit_query` 7 params / 10-value return is defined identically in Task 2 (implementation), Task 2 tests, and Task 3 wiring; `pipe(mode)` and `QueryRequest.mode` consistent across Task 1. ✅

## Execution Handoff

Two execution options:
1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks.
2. **Inline Execution** — batch execution with checkpoints in this session.
