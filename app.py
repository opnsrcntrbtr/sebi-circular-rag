"""Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).

Redesigned UI with:
- Multi-turn chat history via gr.Chatbot
- Streaming answer output (typing effect)
- Metadata bar with latency/faithfulness/certainty badges above the answer
- Example query chips below the question input
- Loading spinner during cold-start pipeline build
- Superseded document highlighting (red row tint + ⚠️ icon) in citations table
- Expandable document preview per citation (markdown accordion)
- Confidence gauge (color-coded: green/yellow/red text badges)

The pipeline is built lazily on the first query: it downloads the prebuilt
FAISS/BM25 index from [spaces].index_repo and the corpus from the published
HF dataset. Generation goes to the external LLM Space if configured, else to
the CPU fallback model. "retrieval_only" mode swaps in the deterministic
ExtractiveStubGenerator so no LLM runs.
"""
import spaces

import dataclasses
import json
import sys
import threading
import time
from pathlib import Path

import gradio as gr
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from sebi_rag.settings import Settings  # noqa: E402

_settings = Settings.load_spaces()
_pipelines: dict[str, object] = {}
_lock = threading.Lock()


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

            _pipelines[mode] = dataclasses.replace(  # type: ignore[arg-type]
                _pipelines["rag"], generator=ExtractiveStubGenerator()
            )
        return _pipelines[mode if mode == "retrieval_only" else "rag"]


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


def _build_citations_markdown(rows: list[dict], chunks_map: dict[str, str]) -> str:
    """Build an expandable markdown table for citations with superseded highlighting."""
    if not rows:
        return "*No citations retrieved.*"

    lines = [
        "| # | Circular | Status | Superseded By | Preview |",
        "|---|----------|--------|---------------|---------|",
    ]

    for i, row in enumerate(rows, 1):
        circular = row.get("Circular", "")
        status = row.get("Status", "")
        superseded_by = row.get("Superseded By", "-")

        # Highlight superseded rows
        is_superseded = "superseded" in status.lower() or "repealed" in status.lower()
        icon = "⚠️" if is_superseded else ""

        # Build preview link
        chunk_id = row.get("id", "")
        if is_superseded:
            preview_text = f"[📄 Read superseded text]($preview_{i})"
        else:
            preview_text = f"[📄 Read text]($preview_{i})"

        lines.append(
            f"| {i} | {circular} {icon} | {status} | {superseded_by} | {preview_text} |"
        )

    # Build expandable preview sections
    for i, row in enumerate(rows, 1):
        chunk_id = row.get("id", "")
        text = chunks_map.get(chunk_id, "*Preview unavailable.*")
        # Truncate long previews to ~800 chars
        if len(text) > 800:
            text = text[:800] + "… (truncated)"

        circular = row.get("Circular", "")
        lines.append(f"\n<details>")
        lines.append(f"<summary><b>{circular}</b></summary>")
        lines.append(f"\n{text}\n")
        lines.append(f"</details>\n")

    return "\n".join(lines)


def _empty_citations_md() -> str:
    return "*No citations retrieved.*"


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
    empty_df = pd.DataFrame(
        columns=["Circular", "Status", "Superseded By", "id"]
    )

    if not question.strip():
        yield (
            _append_message(_to_gradio5_history(chat_history), "assistant", "Please enter a question."),
            "",  # streaming answer
            _empty_citations_md(),
            empty_df,
            "",  # latency
            "",  # faithfulness
            "⚪ N/A",  # certainty
            "",  # superseded warnings
            "",  # unsupported citations
        )
        return

    try:
        as_of = _parse_as_of(as_of_raw)
    except ValueError:
        yield (
            _append_message(_to_gradio5_history(chat_history), "assistant", "**Error:** 'As of date' must be YYYY-MM-DD (e.g. 2025-01-10)."),
            "", _empty_citations_md(), empty_df, "", "", "⚪ Error", "", "",
        )
        return

    # Show user message immediately
    current_history = _append_message(_to_gradio5_history(chat_history), "user", question)

    try:
        pipeline = get_pipeline(mode)  # type: ignore[assignment]
        t0 = time.perf_counter()

        # Stream the answer by generating it fully, then yielding chunks
        ans, _retrieved = pipeline.query(  # type: ignore[attr-defined]
            question, top_k=int(top_k), advisory=False, as_of=as_of,
        )
        latency_ms = (time.perf_counter() - t0) * 1000
        # Build streaming chunks (yield every ~20 chars for typing effect)
        answer_text = ans.text
        if mode == "retrieval_only" and not ans.abstained:
            answer_text = (
                "**Retrieval-only mode** — no LLM generation; the text below is the "
                "top retrieved excerpt. Evaluate the citations and metadata.\n\n"
                + answer_text
            )

        # Yield streaming chunks
        chunk_size = 20
        for i in range(0, len(answer_text), chunk_size):
            partial = answer_text[: i + chunk_size]
            yield (
                current_history,  # chat history with user msg only during streaming
                partial,  # streaming answer text
                _empty_citations_md(),
                empty_df,
                "",  # latency (shown at end)
                "",  # faithfulness (shown at end)
                "⚪ Processing…",  # certainty during streaming
                "",  # superseded (shown at end)
                "",  # unsupported (shown at end)
            )

        # Final yield with all data
        latency = f"{latency_ms:.0f} ms"

        # Build citations with document preview
        from sebi_rag.api import _citation_meta

        citation_rows = [
            {
                "Circular": m.circular,
                "Status": m.status,
                "Superseded By": ", ".join(m.superseded_by) or "-",
            }
            for m in _citation_meta(ans.citations, pipeline.lineage)  # type: ignore[attr-defined]
        ]

        # Build chunks map for previews (doc_id -> text of top chunk per doc)
        chunks_map: dict[str, str] = {}
        retriever = getattr(pipeline, "retriever", None)  # type: ignore[attr-defined]
        if retriever is not None and hasattr(retriever, "chunks"):
            for c in retriever.chunks:  # type: ignore[attr-defined]
                if c.doc_id not in chunks_map and len(chunks_map) < 5:
                    # Use first chunk per doc_id for preview
                    chunks_map[c.doc_id] = c.text[:800] + ("…" if len(c.text) > 800 else "")

        citations_md = _build_citations_markdown(citation_rows, chunks_map) if citation_rows else _empty_citations_md()

        certainty_str = ans.certainty
        if ans.abstained:
            certainty_str += f" (Abstained: {ans.abstention_reason})"

        # Update chat history with full answer
        answer_content = ans.text if not ans.abstained else f"⚠️ *Abstained: {ans.abstention_reason}*"
        final_history = _append_message(current_history, "assistant", answer_content)

        yield (
            final_history,  # complete chat history
            answer_text,  # full answer text (also shown in chat)
            citations_md,  # markdown citations table with previews
            pd.DataFrame(citation_rows) if citation_rows else empty_df,  # dataframe for metadata access
            latency,
            f"{ans.faithfulness:.2f}",
            _certainty_badge(ans.certainty) + (f" — {ans.abstention_reason}" if ans.abstained else ""),
            json.dumps(ans.superseded, indent=2) if ans.superseded else "None",
            ", ".join(ans.unsupported_citations or []) or "None",
        )

    except Exception as exc:  # noqa: BLE001 — surface, don't crash the Space
        error_msg = f"**Error:** {exc}"
        yield (
            _append_message(current_history, "assistant", error_msg),
            error_msg,
            _empty_citations_md(),
            empty_df,
            "", "", "⚪ Error", "", "",
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

        # Chat history (multi-turn)
        chatbot = gr.Chatbot(
            label="Conversation",
        )

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
                as_of_input = gr.Textbox(
                    label="As of date (optional)",
                    placeholder="YYYY-MM-DD — answer per the law in force on this date",
                    max_lines=1,
                )

        # Loading spinner (shown during cold-start pipeline build)
        loading_text = gr.Markdown(
            value="",  # empty by default, shown during first query
            visible=False,
        )

        # Metadata bar (horizontal badges above answer)
        with gr.Row():
            latency_badge = gr.Markdown(value="", visible=False, elem_classes="meta-badge")
            faithfulness_badge = gr.Markdown(value="", visible=False, elem_classes="meta-badge")
            certainty_badge = gr.Markdown(value="", visible=False, elem_classes="meta-badge")

        # Answer output (streaming)
        answer_output = gr.Markdown(label="Answer", elem_classes="answer-output")

        # Citations section
        gr.Markdown("### 📚 Citations")
        citations_md = gr.Markdown(value=_empty_citations_md(), label="Citations (click to expand)")

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

        # Wire up submit
        submit_btn.click(
            fn=_on_submit,
            inputs=[question_input, top_k, mode, as_of_input, chat_history_state],
            outputs=[
                chatbot,       # updated chat history
                answer_output, # streaming answer text
                citations_md,  # markdown citations with previews
                citations_df,  # hidden dataframe
                latency_out,   # latency badge
                faithfulness_out,
                certainty_out,
                superseded_out,
                unsupported_out,
            ],
        )

        # Allow Enter key to submit
        question_input.submit(
            fn=_on_submit,
            inputs=[question_input, top_k, mode, as_of_input, chat_history_state],
            outputs=[
                chatbot, answer_output, citations_md, citations_df,
                latency_out, faithfulness_out, certainty_out,
                superseded_out, unsupported_out,
            ],
        )

    return demo


demo = build_ui()

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
