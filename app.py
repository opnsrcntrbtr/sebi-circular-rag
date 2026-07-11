"""Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).

Gradio SDK Spaces pick up the module-level `demo`. Unlike src/sebi_rag/ui.py
(a thin HTTP client for the local FastAPI server), this app calls the RAG
pipeline in-process: no API URL, no API key.

The pipeline is built lazily on the first query: it downloads the prebuilt
FAISS/BM25 index from [spaces].index_repo and the corpus from the published
HF dataset (see src/sebi_rag/api_spaces.py). Generation goes to the external
LLM Space if configured, else to the CPU fallback model. "retrieval_only"
mode swaps in the deterministic ExtractiveStubGenerator so no LLM runs —
citations, supersession lineage and abstention still behave exactly as in
the full system (academic retrieval-benchmark mode).
"""
from __future__ import annotations

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

# Add this dummy function anywhere before your build_ui() function
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


def run_query_spaces(question: str, top_k: float, mode: str):
    empty_df = pd.DataFrame(columns=["Circular", "Status", "Superseded By"])
    if not question.strip():
        return "Please enter a question.", empty_df, "", "", "", "", ""

    try:
        pipeline = get_pipeline(mode)
        t0 = time.perf_counter()
        ans, _retrieved = pipeline.query(question, top_k=int(top_k), advisory=False)
        latency = f"{(time.perf_counter() - t0) * 1000:.0f} ms"
    except Exception as exc:  # noqa: BLE001 — surface, don't crash the Space
        return f"**Error:** {exc}", empty_df, "", "", "", "", ""

    from sebi_rag.api import _citation_meta

    rows = [
        {
            "Circular": m.circular,
            "Status": m.status,
            "Superseded By": ", ".join(m.superseded_by) or "-",
        }
        for m in _citation_meta(ans.citations, pipeline.lineage)
    ]
    df = pd.DataFrame(rows) if rows else empty_df

    certainty_str = ans.certainty
    if ans.abstained:
        certainty_str += f" (Abstained: {ans.abstention_reason})"

    if mode == "retrieval_only" and not ans.abstained:
        answer_text = (
            "**Retrieval-only mode** — no LLM generation; the text below is the "
            "top retrieved excerpt. Evaluate the citations and metadata.\n\n"
            + ans.text
        )
    else:
        answer_text = ans.text

    return (
        answer_text,
        df,
        latency,
        f"{ans.faithfulness:.2f}",
        certainty_str,
        json.dumps(ans.superseded, indent=2),
        ", ".join(ans.unsupported_citations) or "None",
    )


def build_ui():
    # REMOVED theme=gr.themes.Soft() from here
    with gr.Blocks(title="SEBI Circular RAG (HF Spaces)") as demo:
        gr.Markdown("# SEBI Circular RAG (HF Spaces)")
        gr.Markdown(
            "Hybrid FAISS + BM25 retrieval with cross-encoder reranking, "
            "supersession-aware citations and an abstention gate over Indian "
            "SEBI circulars — corpus and prebuilt index loaded from the "
            f"[`{_settings.spaces.dataset_repo}`]"
            f"(https://huggingface.co/datasets/{_settings.spaces.dataset_repo}) "
            "dataset. CPU-only demo; the first query builds the pipeline and "
            "may take a few minutes."
        )

        with gr.Row():
            with gr.Column(scale=3):
                question_input = gr.Textbox(
                    label="Question",
                    placeholder=(
                        "Ask a question about SEBI circulars (e.g. 'What are the "
                        "modified norms for nomination in demat accounts?')..."
                    ),
                    lines=3,
                )
                submit_btn = gr.Button("Submit Query", variant="primary")

                answer_output = gr.Markdown(label="Answer")

                gr.Markdown("### Citations")
                citations_df = gr.Dataframe(
                    headers=["Circular", "Status", "Superseded By"],
                    interactive=False,
                    wrap=True,
                )

            with gr.Column(scale=1):
                with gr.Accordion("Settings", open=True):
                    top_k = gr.Slider(
                        minimum=1, maximum=10, value=_settings.spaces.top_k,
                        step=1, label="Top K Citations",
                    )
                    mode = gr.Radio(
                        choices=["rag", "retrieval_only"],
                        value="rag",
                        label="Mode",
                        info="Full RAG answer, or retrieval-only academic "
                             "benchmark (citations + metadata, no LLM).",
                    )

                with gr.Accordion("Metadata", open=True):
                    latency_out = gr.Textbox(label="Latency", interactive=False)
                    faithfulness_out = gr.Textbox(label="Faithfulness", interactive=False)
                    certainty_out = gr.Textbox(
                        label="Certainty & Abstention", interactive=False,
                    )
                    superseded_out = gr.Code(
                        label="Superseded Warnings", language="json",
                        interactive=False,
                    )
                    unsupported_out = gr.Textbox(
                        label="Unsupported Citations", interactive=False,
                    )

        submit_btn.click(
            fn=run_query_spaces,
            inputs=[question_input, top_k, mode],
            outputs=[
                answer_output,
                citations_df,
                latency_out,
                faithfulness_out,
                certainty_out,
                superseded_out,
                unsupported_out,
            ],
        )

    return demo


demo = build_ui()

if __name__ == "__main__":
    # ADDED theme configuration here for Gradio 6.0 compatibility
    demo.launch(theme=gr.themes.Soft())
