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
