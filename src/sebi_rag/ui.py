import json
import socket
from datetime import date
from urllib.parse import urlparse

import gradio as gr
import httpx
import pandas as pd

from sebi_rag.regulations import reg_display_name

_EMPTY_DF_COLS = ["Circular", "Status", "Superseded By", "Regulatory Basis"]
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

    # --- SSRF guard: validate api_url before making the request ---
    _validate_api_url(api_url)

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
