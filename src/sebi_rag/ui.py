import json
import socket
from datetime import date
from urllib.parse import urlparse

import gradio as gr
import httpx
import pandas as pd

from sebi_rag.regulations import reg_display_name

_RETRIEVAL_ONLY_BANNER = (
    "**Retrieval-only mode** — no LLM generation; the text below is the "
    "top retrieved excerpt. Evaluate the citations and metadata.\n\n"
)

_EMPTY_DF_COLS = ["Circular", "Status", "Superseded By", "Regulatory Basis"]

def _certainty_badge(certainty: str) -> str:
    """Return a color-coded confidence badge string."""
    colors = {"high": "🟢", "medium": "🟡", "low": "🔴"}
    icon = colors.get(certainty, "⚪")
    return f"{icon} {certainty.capitalize()}"


def _build_citations_markdown(rows: list[dict]) -> str:
    """Build an expandable markdown table for citations with superseded highlighting."""
    if not rows:
        return "*No citations retrieved.*"

    lines = [
        "| # | Circular | Status | Superseded By | Regulatory Basis | Preview |",
        "|---|----------|--------|---------------|------------------|---------|",
    ]

    for i, row in enumerate(rows, 1):
        circular = row.get("Circular", "")
        status = row.get("Status", "")
        superseded_by = row.get("Superseded By", "-")
        basis = row.get("Regulatory Basis", "")

        # Highlight superseded rows
        is_superseded = "superseded" in status.lower() or "repealed" in status.lower()
        icon = "⚠️" if is_superseded else ""

        preview_text = f"[📄 Read text]($preview_{i})"

        lines.append(
            f"| {i} | {circular} {icon} | {status} | {superseded_by} | {basis} | {preview_text} |"
        )

    # Build expandable preview sections (placeholder — actual text from API)
    for i, row in enumerate(rows, 1):
        circular = row.get("Circular", "")
        lines.append(f"\n<details>")
        lines.append(f"<summary><b>{circular}</b></summary>")
        lines.append(f"\n*Preview: click 'Read text' above to expand.*\n")
        lines.append(f"</details>\n")

    return "\n".join(lines)

def _parse_as_of(raw: str) -> str | None:
    """Normalise the optional as-of field: empty -> None, else strict ISO
    YYYY-MM-DD. Raises ValueError for anything else (caller shows a message)."""
    raw = (raw or "").strip()
    if not raw:
        return None
    return date.fromisoformat(raw).isoformat()


def _validate_api_url(url: str) -> None:
    """SSRF guard: reject URLs pointing to private/internal/reserved addresses.

    Blocks cloud-metadata IPs, RFC-1918/private ranges, link-local,
    loopback (except 127.0.0.1), and non-http schemes.
    """
    parsed = urlparse(url)

    # Only allow http / https schemes
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"SSRF blocked: scheme '{parsed.scheme}' not allowed")

    host = parsed.hostname
    if not host:
        raise ValueError(f"SSRF blocked: could not resolve hostname from '{url}'")
    # Resolve to IP and check against private/reserved ranges
    try:
        addr_info = socket.getaddrinfo(host, None, socket.AF_INET)  # IPv4 only
    except socket.gaierror:
        return  # unresolvable hostname — let httpx handle the DNS error naturally

    ip = addr_info[0][4][0]  # first resolved IP address

    octets = list(map(int, ip.split(".")))
    first_octet = octets[0]
    second_octet = octets[1]

    # Block cloud metadata (AWS 169.254.169.254, GCP metadata, etc.)
    if first_octet == 169 and second_octet == 254:
        raise ValueError(f"SSRF blocked: metadata endpoint {ip}")

    # Block loopback (allow 127.0.0.1 explicitly — common for local dev)
    if first_octet == 127:
        return  # allow loopback

    # Block private ranges (RFC 1918)
    if first_octet == 10:
        raise ValueError(f"SSRF blocked: private network {ip}")
    if first_octet == 172 and 16 <= second_octet <= 31:
        raise ValueError(f"SSRF blocked: private network {ip}")
    if first_octet == 192 and second_octet == 168:
        raise ValueError(f"SSRF blocked: private network {ip}")

    # Block link-local (169.254.x.x already caught above, plus 0.0.0.0)
    if first_octet == 0:
        raise ValueError(f"SSRF blocked: zero address {ip}")

    # Block multicast (224.0.0.0/4) and reserved (240.0.0.0/4)
    if first_octet >= 224:
        raise ValueError(f"SSRF blocked: reserved/multicast address {ip}")

    # Block documentation/test ranges (198.18.0.0/15, 192.0.2.x)
    if first_octet == 198 and second_octet == 18:
        raise ValueError(f"SSRF blocked: benchmark range {ip}")
    if first_octet == 192 and second_octet == 0 and octets[2] == 2:
        raise ValueError(f"SSRF blocked: TEST-NET-1 {ip}")

    # Block documentation ranges (198.51.100.0/24, 203.0.113.0/24)
    if first_octet == 198 and second_octet == 51 and octets[2] == 100:
        raise ValueError(f"SSRF blocked: TEST-NET-2 {ip}")
    if first_octet == 203 and second_octet == 0 and octets[2] == 113:
        raise ValueError(f"SSRF blocked: TEST-NET-3 {ip}")

    # Block documentation range 100.64.0.0/10 (CGNAT)
    if first_octet == 100 and 64 <= second_octet <= 127:
        raise ValueError(f"SSRF blocked: CGNAT range {ip}")

    # Block IANA reserved / special-purpose
    if first_octet == 192 and second_octet == 88 and octets[2] == 99:
        raise ValueError(f"SSRF blocked: IANA reserved {ip}")

    # If we get here, the IP is public — allow it

def _empty_outputs_md() -> str:
    """Return empty markdown placeholder for streaming."""
    return ""

def submit_query_stream(
    question: str, api_url: str, api_key: str, top_k: float,
    mode: str, as_of_raw: str, advisory: bool, chat_history: list[list],
) -> tuple:
    """Generator that streams the answer while updating chat history."""
    empty_df = pd.DataFrame(columns=_EMPTY_DF_COLS)

    if not question.strip():
        yield (chat_history + [["You", "Please enter a question."]], "", _empty_outputs_md(),
               empty_df, "", "", "⚪ N/A", "", "", "", "", "")
        return

    current_history = chat_history + [[question, ""]]

    try:
        as_of = _parse_as_of(as_of_raw)
    except ValueError:
        yield (current_history + [["", "**Error:** 'As of date' must be YYYY-MM-DD."]],
               "", _empty_outputs_md(), empty_df, "", "", "⚪ Error", "", "", "", "", "")
        return

    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key

    payload = {"question": question, "top_k": int(top_k),
               "mode": mode, "advisory": bool(advisory), "as_of": as_of}

    _validate_api_url(api_url)

    try:
        resp = httpx.post(api_url, json=payload, headers=headers, timeout=120.0)
        if resp.status_code != 200:
            error_msg = f"**Error:** API returned status code {resp.status_code}\n\n{resp.text}"
            yield (current_history + [["", error_msg]], "", _empty_outputs_md(),
                   empty_df, "", "", "⚪ Error", "", "", "", "", "")
            return
        data = resp.json()
    except httpx.TimeoutException:
        yield (current_history + [["", "**Request Failed:** API timed out."]],
               "", _empty_outputs_md(), empty_df, "", "", "⚪ Error", "", "", "", "", "")
        return
    except Exception as e:  # noqa: BLE001 - surface, don't crash the UI
        yield (current_history + [["", f"**Request Failed:** {str(e)}"]],
               "", _empty_outputs_md(), empty_df, "", "", "⚪ Error", "", "", "", "", "")
        return

    # Build streaming chunks (typing effect)
    answer_text = data.get("answer", "")
    if mode == "retrieval_only" and not data.get("abstained", False):
        answer_text = _RETRIEVAL_ONLY_BANNER + answer_text

    # Yield streaming chunks for typing effect
    chunk_size = 20
    for i in range(0, len(answer_text), chunk_size):
        partial = answer_text[: i + chunk_size]
        yield (current_history, partial, _empty_outputs_md(), empty_df,
               "", "", "⚪ Processing…", "", "", "", "", "")

    # Final yield with all data
    df_rows = []
    for item in data.get("citations_meta", []):
        superseded_by = ", ".join(item.get("superseded_by", []))
        basis = item.get("regulatory_basis_status", "unknown")
        stale = [reg_display_name(r.get("short_name", r.get("reg_id", "?")),
                                  r.get("year"))
                 for r in item.get("regulations", [])
                 if r.get("status") != "in_force"]
        basis_cell = f"{basis} ({', '.join(stale)})" if stale else basis
        df_rows.append({
            "Circular": item.get("circular"),
            "Status": item.get("status"),
            "Superseded By": superseded_by if superseded_by else "-",
            "Regulatory Basis": basis_cell,
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
    confidence_json = json.dumps(data.get("confidence", {}), indent=2)
    draft = data.get("draft_answer", "") or ""
    draft_md = (f"**Advisory draft — not authoritative**\n\n{draft}" if draft else "")
    retrieved_json = json.dumps(data.get("retrieved", []), indent=2)

    # Update chat history with full answer
    final_history = current_history + [[answer_text if not abstained else f"⚠️ *Abstained: {data.get('abstention_reason', '')}*"]]

    citations_md = _build_citations_markdown(df_rows) if df_rows else "*No citations retrieved.*"

    yield (final_history, answer_text, citations_md, df, latency, faithfulness,
           _certainty_badge(certainty_str) if not abstained else f"🔴 {certainty_str}",
           superseded, unsupported, confidence_json, draft_md, retrieved_json)


def build_ui():
    with gr.Blocks(title="SEBI Circular RAG") as demo:
        gr.Markdown(
            "Local-first, Apple-Silicon Retrieval-Augmented Generation over Indian SEBI circulars. "
            "Hybrid FAISS + BM25 retrieval with cross-encoder reranking, supersession-aware citations "
            "and an abstention gate."
        )

        # Chat history (multi-turn)
        chatbot = gr.Chatbot(
            label="Conversation",
        )

        with gr.Row():
            with gr.Column(scale=3):
                question_input = gr.Textbox(
                    label="Question",
                    placeholder="Ask a question about SEBI circulars (e.g. 'What are the modified norms for nomination in demat accounts?')...",
                    lines=3,
                )

                # Example query chips
                gr.Markdown("**Try an example:**")
                with gr.Row():
                    for query in [
                        "Nomination norms in demat accounts",
                        "Maximum leverage for equity derivatives",
                        "Research analyst compliance requirements",
                        "Mutual fund expense ratio caps",
                        "SME IPO listing requirements",
                    ]:
                        gr.Button(query, size="sm", variant="secondary").click(
                            fn=lambda q=query: q, outputs=question_input,
                        )

                submit_btn = gr.Button("Submit Query", variant="primary")

            with gr.Column(scale=1):
                # Connection settings
                with gr.Accordion("Connection", open=True):
                    api_url = gr.Textbox(
                        label="API Endpoint URL", value="http://127.0.0.1:8000/query"
                    )
                    api_key = gr.Textbox(
                        label="API Key", type="password",
                        placeholder="Required if server uses auth"
                    )

                # Query controls
                with gr.Accordion("Query controls", open=True):
                    top_k = gr.Slider(
                        minimum=1, maximum=10, value=5, step=1, label="Top K Citations"
                    )
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

                # Metadata bar (always visible)
                with gr.Accordion("Metadata", open=False):
                    metadata_row = gr.Row()
                    with metadata_row:
                        latency_out = gr.Textbox(label="Latency", interactive=False)
                        faithfulness_out = gr.Textbox(label="Faithfulness", interactive=False)
                        certainty_out = gr.Markdown(label="Confidence Gauge")

                # Advanced outputs
                with gr.Accordion("Advanced outputs", open=False):
                    superseded_out = gr.Code(
                        label="Superseded Warnings", language="json", interactive=False
                    )
                    unsupported_out = gr.Textbox(
                        label="Unsupported Citations", interactive=False
                    )
                    confidence_out = gr.Code(
                        label="Confidence", language="json", interactive=False
                    )
                    draft_out = gr.Markdown(label="Advisory Draft")
                    retrieved_out = gr.Code(
                        label="Retrieved (doc ids)", language="json", interactive=False
                    )

        # Streaming answer output
        answer_output = gr.Markdown(label="Answer")

        # Citations with superseded highlighting
        gr.Markdown("### Citations")
        citations_md = gr.Markdown(label="Citations (click to expand)")
        citations_df = gr.Dataframe(
            headers=["Circular", "Status", "Superseded By", "Regulatory Basis"],
            interactive=False, wrap=True,
        )

        # Wire up streaming submit
        submit_btn.click(
            fn=submit_query_stream,
            inputs=[question_input, api_url, api_key, top_k, mode, as_of_input,
                    advisory, chatbot],
            outputs=[chatbot, answer_output, citations_md, citations_df, latency_out,
                     faithfulness_out, certainty_out, superseded_out, unsupported_out,
                     confidence_out, draft_out, retrieved_out],
        )

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(server_name="127.0.0.1", server_port=7860)
