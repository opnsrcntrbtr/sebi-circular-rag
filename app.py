"""Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).

Redesigned UI with:
- Multi-turn chat history via gr.Chatbot; the answer streams directly into
  the chat bubble (single answer surface — no separate duplicate block)
- Metadata bar with latency/faithfulness/certainty badges above the answer,
  populated after each query (hidden otherwise)
- Example query chips below the question input
- Loading message shown while the pipeline builds on a cold start
- Superseded document highlighting (⚠️ icon) in the citations table
- Expandable document preview per citation (markdown accordion)
- Confidence gauge (color-coded: 🟢/🟡/🔴 certainty badge)
- "Clear conversation" resets chat, citations and metadata in one click

The pipeline is built lazily on the first query: it downloads the prebuilt
FAISS/BM25 index from [spaces].index_repo and the corpus from the published
HF dataset. Generation goes to the external LLM Space if configured, else to
the CPU fallback model. "retrieval_only" mode swaps in the deterministic
ExtractiveStubGenerator so no LLM runs.
"""
import spaces

import concurrent.futures
import dataclasses
import json
import sys
import threading
import time
from pathlib import Path

import gradio as gr
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from sebi_rag.pipeline import RAGPipeline  # noqa: E402
from sebi_rag.settings import Settings  # noqa: E402

_settings = Settings.load_spaces()
_pipelines: dict[str, RAGPipeline] = {}
_chunk_text: dict[str, str] = {}  # chunk_id -> full text; built once, shared across modes
_lock = threading.Lock()

MAX_PREVIEWS = 10  # matches the Top K Citations slider's maximum

_EMPTY_CITATIONS_COLUMNS = ["Circular", "Status", "Superseded By", "id"]

# Runs get_pipeline()/pipeline.query() off the main generator thread so
# run_query_stream can keep yielding cycling status messages while either
# blocking call is in flight (a Python generator can only yield *between*
# statements, never during one). Module-level and reused across requests.
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

# Neither get_pipeline() nor pipeline.query() exposes real stage callbacks
# (both are single opaque blocking calls — see src/sebi_rag/pipeline.py),
# so these cycle on a timer as a perceived-progress cue, not as a readout of
# actual backend state. Real instrumentation would mean threading a callback
# through pipeline.query()'s retrieve/rerank/generate stages — out of scope
# here; this is app.py-only.
_BUILD_STAGE_MESSAGES = [
    "⏳ Downloading the prebuilt index (first query only)…",
    "⏳ Loading embedding & reranker models…",
    "⏳ Almost ready — finishing pipeline setup…",
]
_QUERY_STAGE_MESSAGES = [
    "🔍 Retrieving relevant circulars…",
    "📊 Reranking candidates…",
    "🧭 Checking supersession & abstention gate…",
    "✍️ Drafting the answer…",
]


@spaces.GPU
def warm_up_gpu():
    pass


def get_pipeline(mode: str):
    """Cache one pipeline per mode; both share retriever/reranker/lineage."""
    with _lock:
        if "rag" not in _pipelines:
            from sebi_rag.api_spaces import build_spaces_pipeline

            _pipelines["rag"] = build_spaces_pipeline()
        if mode == "retrieval_only" and mode not in _pipelines:
            from sebi_rag.generate import ExtractiveStubGenerator

            _pipelines[mode] = dataclasses.replace(
                _pipelines["rag"], generator=ExtractiveStubGenerator()
            )
        return _pipelines[mode if mode == "retrieval_only" else "rag"]


def _get_chunk_text(pipeline) -> dict[str, str]:
    """Build {chunk_id: text} once from retriever.chunks (~78.5k rows) and cache it.

    Previously this map was rebuilt from scratch on every query; both modes
    share the same retriever (see get_pipeline), so one process-wide cache is
    correct and avoids the O(corpus) scan per request.
    """
    global _chunk_text
    with _lock:
        if not _chunk_text:
            retriever = getattr(pipeline, "retriever", None)
            for c in getattr(retriever, "chunks", ()) or ():
                _chunk_text.setdefault(c.id, c.text)
        return _chunk_text


def _parse_as_of(raw: str) -> str | None:
    """Normalise the optional as-of date field: empty -> None, else strict
    ISO YYYY-MM-DD (ValueError propagates for anything else)."""
    raw = (raw or "").strip()
    if not raw:
        return None
    from datetime import date

    return date.fromisoformat(raw).isoformat()


def _certainty_badge(certainty: str) -> str:
    """Return a color-coded confidence badge string."""
    colors = {"high": "🟢", "medium": "🟡", "low": "🔴"}
    icon = colors.get(certainty, "⚪")
    return f"{icon} {certainty.capitalize()}"


def _format_latency(ms: float) -> str:
    """Human-readable latency: '850ms' or '1.2s', not a raw millisecond count."""
    return f"{ms:.0f}ms" if ms < 1000 else f"{ms / 1000:.1f}s"


def _faithfulness_badge(faithfulness: float) -> str:
    icon = "✅" if faithfulness >= 0.9 else "⚠️" if faithfulness >= 0.7 else "❌"
    return f"{icon} Faithfulness: {faithfulness:.2f}"


def _hidden_meta() -> tuple:
    """loading_text, latency_badge, faithfulness_badge, certainty_badge — all hidden.

    Length/order must match _loading_meta and _visible_meta — this is the same
    arity-parity bug class _blank_previews/_preview_updates guards against.
    """
    hidden = gr.update(visible=False)
    return hidden, hidden, hidden, hidden


def _loading_meta(message: str) -> tuple:
    """Cold-start/processing message visible; badges stay hidden until real data exists."""
    hidden = gr.update(visible=False)
    return gr.update(visible=True, value=message), hidden, hidden, hidden


def _visible_meta(latency_ms: float, faithfulness: float, certainty_str: str) -> tuple:
    hidden = gr.update(visible=False)
    return (
        hidden,  # loading_text — done loading
        gr.update(visible=True, value=f"⏱️ {_format_latency(latency_ms)}"),
        gr.update(visible=True, value=_faithfulness_badge(faithfulness)),
        gr.update(visible=True, value=certainty_str),
    )


def _cycle_messages_until_done(future: "concurrent.futures.Future", messages: list[str], interval: float = 2.0):
    """Yield `messages` (cycling) roughly every `interval`s until `future`
    resolves. A cheap wait-with-heartbeat: future.result(timeout=interval)
    blocks for at most `interval`s, so this checks in periodically without
    a separate poll loop or sleep. Caller retrieves future.result() after
    the loop — it's guaranteed done by then.
    """
    i = 0
    while True:
        try:
            future.result(timeout=interval)
            return
        except concurrent.futures.TimeoutError:
            yield messages[i % len(messages)]
            i += 1


def _build_citations_markdown(rows: list[dict]) -> str:
    """Build a citations markdown table (Circular / Status / Superseded By).

    Chunk-text previews render separately, one gr.Accordion per row (see
    _preview_updates) — Gradio markdown tables don't support nested HTML, so
    <details> accordions or long free text inside a cell corrupts the table.
    """
    if not rows:
        return "*No citations retrieved.*"

    lines = [
        "| # | Circular | Status | Superseded By |",
        "|---|----------|--------|----------------|",
    ]

    for i, row in enumerate(rows, 1):
        circular = row.get("Circular", "").replace("\\", "\\\\").replace("|", "\\|")
        status = row.get("Status", "")
        superseded_by = row.get("Superseded By", "-")

        # Highlight superseded rows
        is_superseded = "superseded" in status.lower() or "repealed" in status.lower()
        icon = "⚠️" if is_superseded else ""

        lines.append(f"| {i} | {circular} {icon} | {status} | {superseded_by} |")

    return "\n".join(lines)


def _empty_citations_md() -> str:
    return "*No citations retrieved.*"


def _truncate_preview(text: str, limit: int = 800) -> str:
    """Truncate chunk text for display; append an ellipsis if cut."""
    if len(text) > limit:
        return text[:limit] + "…"
    return text


def _blank_previews() -> list:
    """Hide every preview accordion. Length must equal _preview_updates'."""
    updates: list = []
    for _ in range(MAX_PREVIEWS):
        updates.append(gr.update(visible=False))
        updates.append(gr.update(value=""))
    return updates


def _preview_updates(rows: list[dict], chunk_text: dict[str, str]) -> list:
    """Build accordion(visible, label) + markdown(value) updates for up to
    MAX_PREVIEWS citation rows. Extra rows beyond MAX_PREVIEWS are silently
    dropped (the accordion pool is fixed-size); missing chunk IDs fall back
    to a placeholder instead of raising.
    """
    updates: list = []
    for i in range(MAX_PREVIEWS):
        if i < len(rows):
            row = rows[i]
            circular = row.get("Circular", "")
            text = chunk_text.get(row.get("id", ""), "*Preview unavailable.*")
            if text != "*Preview unavailable.*":
                text = _truncate_preview(text)
            updates.append(gr.update(visible=True, label=f"📄 [{i + 1}] {circular}"))
            updates.append(gr.update(value=text))
        else:
            updates.append(gr.update(visible=False))
            updates.append(gr.update(value=""))
    return updates


def _to_gradio5_history(history):
    """Normalize chat history to Gradio 5+ message format.

    Gradio 5+ expects: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    Old format was: [[user_msg, bot_msg], ...]
    Handles both; returns new-format list.
    """
    if not history:
        return []
    result = []
    for entry in history:
        if isinstance(entry, dict) and "role" in entry and "content" in entry:
            # Already Gradio 5+ format
            result.append(entry)
        elif isinstance(entry, (list, tuple)) and len(entry) >= 2:
            # Old [[user, bot], ...] format — convert
            if entry[0]:  # user message present
                result.append({"role": "user", "content": entry[0]})
            if entry[1]:  # bot message present
                result.append({"role": "assistant", "content": entry[1]})
        elif isinstance(entry, dict):
            # Already a single message dict
            result.append(entry)
    return result

def _append_message(history, role, content):
    """Append a single message to history in Gradio 5+ format."""
    return history + [{"role": role, "content": content}]
def run_query_stream(
    question: str,
    top_k: int,
    mode: str,
    as_of_raw: str,
    chat_history: list | None,
):
    """Generator that streams the answer while updating chat history."""
    empty_df = pd.DataFrame(columns=_EMPTY_CITATIONS_COLUMNS)

    if not question.strip():
        yield (
            _append_message(_to_gradio5_history(chat_history), "assistant", "Please enter a question."),
            _empty_citations_md(),
            empty_df,
            "",  # latency
            "",  # faithfulness
            "⚪ N/A",  # certainty
            "",  # superseded warnings
            "",  # unsupported citations
            *_blank_previews(),
            *_hidden_meta(),
        )
        return

    try:
        as_of = _parse_as_of(as_of_raw)
    except ValueError:
        yield (
            _append_message(_to_gradio5_history(chat_history), "assistant", "**Error:** 'As of date' must be YYYY-MM-DD (e.g. 2025-01-10)."),
            _empty_citations_md(), empty_df, "", "", "⚪ Error", "", "",
            *_blank_previews(),
            *_hidden_meta(),
        )
        return

    # Show user message immediately
    current_history = _append_message(_to_gradio5_history(chat_history), "user", question)

    try:
        # get_pipeline()/pipeline.query() are single blocking calls with no
        # internal progress callback (see _BUILD_STAGE_MESSAGES/
        # _QUERY_STAGE_MESSAGES docstring above), so both run on a worker
        # thread while this generator keeps yielding cycling status
        # messages — a generator can only yield *between* statements, never
        # during a blocking one. On a warm cache, get_pipeline() typically
        # resolves before the first cycle check, so nothing cycles for
        # already-fast requests.
        pipeline_future = _executor.submit(get_pipeline, mode)
        for msg in _cycle_messages_until_done(pipeline_future, _BUILD_STAGE_MESSAGES):
            yield (
                current_history,
                _empty_citations_md(), empty_df, "", "", "⚪ Processing…", "", "",
                *_blank_previews(),
                *_loading_meta(msg),
            )
        pipeline = pipeline_future.result()  # type: ignore[assignment]
        chunk_text = _get_chunk_text(pipeline)

        t0 = time.perf_counter()
        query_future = _executor.submit(
            pipeline.query, question, top_k=int(top_k), advisory=False, as_of=as_of,  # type: ignore[attr-defined]
        )
        for msg in _cycle_messages_until_done(query_future, _QUERY_STAGE_MESSAGES):
            yield (
                current_history,
                _empty_citations_md(), empty_df, "", "", "⚪ Processing…", "", "",
                *_blank_previews(),
                *_loading_meta(msg),
            )
        ans, _retrieved = query_future.result()
        latency_ms = (time.perf_counter() - t0) * 1000
        # Build streaming chunks (yield every ~20 chars for typing effect)
        answer_text = ans.text
        if mode == "retrieval_only" and not ans.abstained:
            answer_text = (
                "**Retrieval-only mode** — no LLM generation; the text below is the "
                "top retrieved excerpt. Evaluate the citations and metadata.\n\n"
                + answer_text
            )

        # Yield streaming chunks straight into the chat bubble itself — this
        # is the only answer surface now, so the typing effect has to live
        # here rather than in a separate (now-removed) answer_output block.
        chunk_size = 20
        for i in range(0, len(answer_text), chunk_size):
            partial = answer_text[: i + chunk_size]
            yield (
                _append_message(current_history, "assistant", partial),
                _empty_citations_md(),
                empty_df,
                "",  # latency (shown at end)
                "",  # faithfulness (shown at end)
                "⚪ Processing…",  # certainty during streaming
                "",  # superseded (shown at end)
                "",  # unsupported (shown at end)
                *_blank_previews(),
                *_hidden_meta(),
            )

        # Final yield with all data
        latency = f"{latency_ms:.0f} ms"

        # Build citations with document preview
        from sebi_rag.api import _citation_meta

        seen_circulars: set[str] = set()
        # Build citation rows
        citation_rows = []
        for cit_id, m in zip(ans.citations, _citation_meta(ans.citations, pipeline.lineage)):  # type: ignore[attr-defined]
            if m.circular not in seen_circulars:
                seen_circulars.add(m.circular)
                citation_rows.append({
                    "id": cit_id,
                    "Circular": m.circular,
                    "Status": m.status,
                    "Superseded By": ", ".join(m.superseded_by) or "-",
                })

        citations_md = _build_citations_markdown(citation_rows) if citation_rows else _empty_citations_md()

        certainty_str = ans.certainty
        if ans.abstained:
            certainty_str += f" (Abstained: {ans.abstention_reason})"

        # Update chat history with full answer
        answer_content = ans.text if not ans.abstained else f"⚠️ *Abstained: {ans.abstention_reason}*"
        final_history = _append_message(current_history, "assistant", answer_content)

        certainty_badge_str = _certainty_badge(ans.certainty) + (
            f" — {ans.abstention_reason}" if ans.abstained else ""
        )

        yield (
            final_history,  # complete chat history
            citations_md,  # markdown citations table
            pd.DataFrame(citation_rows) if citation_rows else empty_df,  # dataframe for metadata access
            latency,
            f"{ans.faithfulness:.2f}",
            certainty_badge_str,
            json.dumps(ans.superseded, indent=2) if ans.superseded else "None",
            ", ".join(ans.unsupported_citations or []) or "None",
            *_preview_updates(citation_rows, chunk_text),
            *_visible_meta(latency_ms, ans.faithfulness, certainty_badge_str),
        )

    except Exception as exc:  # noqa: BLE001 — surface, don't crash the Space
        error_msg = f"**Error:** {exc}"
        yield (
            _append_message(current_history, "assistant", error_msg),
            _empty_citations_md(),
            empty_df,
            "", "", "⚪ Error", "", "",
            *_blank_previews(),
            *_hidden_meta(),
        )


def _on_submit(question, top_k, mode, as_of, chat_history):
    """Handle submit: yield streaming updates."""
    yield from run_query_stream(question, top_k, mode, as_of, chat_history or [])

def build_ui():
    # Guard against None settings (shouldn't happen in production)
    dataset_repo = _settings.spaces.dataset_repo if _settings.spaces else "sebi-circulars/rag-corpus"
    top_k_default = _settings.spaces.top_k if _settings.spaces else 10

    with gr.Blocks(title="SEBI Circular RAG") as demo:
        # Header
        gr.Markdown(
            f"# SEBI Circular RAG\n\n"
            "Hybrid FAISS + BM25 retrieval with cross-encoder reranking, "
            "supersession-aware citations and an abstention gate over Indian "
            "SEBI circulars — corpus and prebuilt index loaded from the "
            f"[`{dataset_repo}`]"
            f"(https://huggingface.co/datasets/{dataset_repo}) "
            "CPU-only demo; the first query builds the pipeline and may take a few minutes."
        )

        # Chat history (multi-turn). height= gives it its own bounded,
        # internally-scrolling area — without one, Gradio's autoscroll
        # (default True) has no scroll container of its own to act on and
        # instead scrolls the WHOLE PAGE to document.scrollHeight on every
        # component update anywhere in the app (confirmed live: expanding
        # an unrelated citation-preview accordion mid-page still jumped
        # scroll to the page's bottom edge, not to the accordion itself).
        # autoscroll=False turns that off entirely now that a bounded
        # height makes it unnecessary for keeping messages in view.
        chatbot = gr.Chatbot(
            label="Conversation",
            placeholder=(
                "### 👋 Ask a question about SEBI circulars\n"
                "Or click one of the examples below to get started."
            ),
            height=450,
            autoscroll=False,
        )
        clear_btn = gr.Button("🗑️ Clear conversation", size="sm", variant="secondary")

        # Question input + example queries
        with gr.Row():
            with gr.Column(scale=4):
                question_input = gr.Textbox(
                    label="Question",
                    placeholder=(
                        "Ask about SEBI circulars (e.g. 'What are the modified norms "
                        "for nomination in demat accounts?')..."
                    ),
                    lines=3,
                    scale=4,
                )
            with gr.Column(scale=1):
                submit_btn = gr.Button("Submit Query", variant="primary", scale=1)

        # Loading/status message + metadata badge row — placed immediately
        # below Submit so it's visible without scrolling (previously sat
        # below Settings + example chips, off-screen until manually
        # scrolled to). Hidden by default; see _hidden_meta/_loading_meta/
        # _visible_meta.
        loading_text = gr.Markdown(value="", visible=False)
        with gr.Row():
            latency_badge = gr.Markdown(value="", visible=False)
            faithfulness_badge = gr.Markdown(value="", visible=False)
            certainty_badge = gr.Markdown(value="", visible=False)

        # Example queries (clickable chips)
        gr.Markdown("### Try an example:")
        with gr.Row():
            for query in [
                "Nomination norms in demat accounts",
                "Maximum leverage for equity derivatives",
                "Research analyst compliance requirements",
                "Mutual fund expense ratio caps",
                "SME IPO listing requirements",
            ]:
                gr.Button(query, size="sm", variant="secondary").click(
                    fn=lambda q=query: q,
                    outputs=question_input,
                )

        # Settings accordion (right column)
        with gr.Accordion("⚙️ Settings", open=False):
            with gr.Row():
                top_k = gr.Slider(
                    minimum=1, maximum=10, value=top_k_default,
                    step=1, label="Top K Citations",
                )
                mode = gr.Radio(
                    choices=["rag", "retrieval_only"],
                    value="rag",
                    label="Mode",
                    info="Full RAG answer, or retrieval-only academic benchmark "
                         "(citations + metadata, no LLM).",
                )
            with gr.Row():
                # type="string" is required: DateTime's default type ("timestamp")
                # returns a float, which _parse_as_of's date.fromisoformat() can't
                # parse. include_time=False keeps it date-only (a time-of-day has
                # no meaning for an as-of-date query). See tests/test_app_asof.py
                # for the regression guard on this exact config.
                as_of_input = gr.DateTime(
                    label="As of date (optional)",
                    include_time=False,
                    type="string",
                    info="Pick a date to score retrieval against the law in "
                         "force then — leave blank to use current law. "
                         "(Typed YYYY-MM-DD also accepted.)",
                )

        # The Chatbot above is the single answer surface — no separate
        # duplicate block. (Previously a second answer_output Markdown here
        # rendered the identical text a second time with no visual
        # distinction from the chat bubble.)

        # Citations section
        gr.Markdown("### 📚 Citations")
        citations_md = gr.Markdown(value=_empty_citations_md(), label="Citations")

        # Fixed pool of preview accordions, one per possible citation row (up
        # to MAX_PREVIEWS). Gradio components are declared once at UI-build
        # time, not per-request, so unused rows are hidden via visible=False
        # rather than the pool being resized.
        preview_components: list = []
        for _ in range(MAX_PREVIEWS):
            with gr.Accordion(visible=False, open=False) as acc:
                md = gr.Markdown()
            preview_components.append(acc)
            preview_components.append(md)

        # Hidden dataframe for programmatic access
        citations_df = gr.Dataframe(
            headers=["Circular", "Status", "Superseded By", "id"],
            interactive=False,
            visible=False,  # hidden; we use markdown table instead
        )

        # Metadata outputs (detailed)
        with gr.Accordion("📊 Detailed Metadata", open=False):
            with gr.Row():
                latency_out = gr.Textbox(label="Latency", interactive=False)
                faithfulness_out = gr.Textbox(label="Faithfulness Score", interactive=False)
            with gr.Row():
                certainty_out = gr.Textbox(label="Certainty & Abstention", interactive=False)
            with gr.Row():
                superseded_out = gr.Code(label="Superseded Warnings", language="json", interactive=False)
            with gr.Row():
                unsupported_out = gr.Textbox(label="Unsupported Citations", interactive=False)

        # Chat history state
        chat_history_state = gr.State(value=[])

        _submit_outputs = [
            chatbot,       # updated chat history (answer streams in here)
            citations_md,  # markdown citations table
            citations_df,  # hidden dataframe
            latency_out,   # latency (Detailed Metadata)
            faithfulness_out,
            certainty_out,
            superseded_out,
            unsupported_out,
            *preview_components,  # per-citation preview accordions
            loading_text, latency_badge, faithfulness_badge, certainty_badge,
        ]

        # Wire up submit
        submit_btn.click(
            fn=_on_submit,
            inputs=[question_input, top_k, mode, as_of_input, chat_history_state],
            outputs=_submit_outputs,
        )

        # Allow Enter key to submit
        question_input.submit(
            fn=_on_submit,
            inputs=[question_input, top_k, mode, as_of_input, chat_history_state],
            outputs=_submit_outputs,
        )

        # Clear conversation: reset chat, citations and metadata back to
        # their initial empty states without a page reload.
        clear_btn.click(
            fn=lambda: (
                [], [],  # chatbot, chat_history_state
                _empty_citations_md(), pd.DataFrame(columns=_EMPTY_CITATIONS_COLUMNS),
                "", "", "", "None", "None",
                *_blank_previews(), *_hidden_meta(),
            ),
            outputs=[
                chatbot, chat_history_state, citations_md, citations_df,
                latency_out, faithfulness_out, certainty_out, superseded_out, unsupported_out,
                *preview_components,
                loading_text, latency_badge, faithfulness_badge, certainty_badge,
            ],
        )

    return demo


demo = build_ui()

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
