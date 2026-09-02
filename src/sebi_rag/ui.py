import concurrent.futures
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

MAX_PREVIEWS = 10  # matches the Top K Citations slider's maximum

# Runs the blocking httpx.post off the main generator thread so
# submit_query_stream can keep yielding cycling status messages while the
# request is in flight (a Python generator can only yield *between*
# statements, never during one).
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

# The API has no real stage callbacks — /query is one opaque blocking call
# (see src/sebi_rag/api.py) — so these cycle on a timer as a perceived-
# progress cue, not as a readout of actual backend state.
_QUERY_STAGE_MESSAGES = [
    "🔍 Retrieving relevant circulars…",
    "📊 Reranking candidates…",
    "🧭 Checking supersession & abstention gate…",
    "✍️ Drafting the answer…",
]


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


def _build_citations_markdown(rows: list[dict]) -> str:
    """Build a citations markdown table with superseded highlighting.

    Chunk-text previews render separately, one gr.Accordion per row (see
    _preview_updates) — Gradio markdown tables don't support nested HTML, so
    long free text inside a cell corrupts the table.
    """
    if not rows:
        return "*No citations retrieved.*"

    lines = [
        "| # | Circular | Status | Superseded By | Regulatory Basis |",
        "|---|----------|--------|----------------|------------------|",
    ]

    for i, row in enumerate(rows, 1):
        circular = row.get("Circular", "").replace("\\", "\\\\").replace("|", "\\|")
        status = row.get("Status", "")
        superseded_by = row.get("Superseded By", "-")
        basis = row.get("Regulatory Basis", "")

        # Highlight superseded rows
        is_superseded = "superseded" in status.lower() or "repealed" in status.lower()
        icon = "⚠️" if is_superseded else ""

        lines.append(f"| {i} | {circular} {icon} | {status} | {superseded_by} | {basis} |")

    return "\n".join(lines)


def _empty_citations_md() -> str:
    return "*No citations retrieved.*"


def _blank_previews() -> list:
    """Hide every preview accordion. Length must equal _preview_updates'."""
    updates: list = []
    for _ in range(MAX_PREVIEWS):
        updates.append(gr.update(visible=False))
        updates.append(gr.update(value=""))
    return updates


def _preview_updates(rows: list[dict]) -> list:
    """Build accordion(visible, label) + markdown(value) updates for up to
    MAX_PREVIEWS citation rows. Extra rows beyond MAX_PREVIEWS are silently
    dropped (the accordion pool is fixed-size); a row with no server-supplied
    preview text falls back to a placeholder instead of an empty box.

    Preview text comes straight off each row's own "Preview" field (set from
    citations_meta[i].preview server-side) — never from re-matching against a
    separately deduped list, which is the class of bug that misaligns rows by
    index once a query cites two chunks from the same circular.
    """
    updates: list = []
    for i in range(MAX_PREVIEWS):
        if i < len(rows):
            row = rows[i]
            circular = row.get("Circular", "")
            text = row.get("Preview") or "*Preview unavailable.*"
            updates.append(gr.update(visible=True, label=f"📄 [{i + 1}] {circular}"))
            updates.append(gr.update(value=text))
        else:
            updates.append(gr.update(visible=False))
            updates.append(gr.update(value=""))
    return updates


def _to_gradio5_history(history):
    """Normalize chat history to Gradio 5+/6+ message format.

    Gradio 5+ expects: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    Old format was: [[user_msg, bot_msg], ...] — Gradio 6 rejects that format
    outright (verified: gr.Chatbot().postprocess([["q","a"]]) raises).
    """
    if not history:
        return []
    result = []
    for entry in history:
        if isinstance(entry, dict) and "role" in entry and "content" in entry:
            result.append(entry)
        elif isinstance(entry, (list, tuple)) and len(entry) >= 2:
            if entry[0]:
                result.append({"role": "user", "content": entry[0]})
            if entry[1]:
                result.append({"role": "assistant", "content": entry[1]})
        elif isinstance(entry, dict):
            result.append(entry)
    return result


def _append_message(history, role, content):
    """Append a single message to history in Gradio 5+/6+ format."""
    return history + [{"role": role, "content": content}]


def _cycle_messages_until_done(future: "concurrent.futures.Future", messages: list[str], interval: float = 2.0):
    """Yield `messages` (cycling) roughly every `interval`s until `future`
    resolves. A cheap wait-with-heartbeat: future.result(timeout=interval)
    blocks for at most `interval`s, so this checks in periodically without a
    separate poll loop or sleep. Caller retrieves future.result() after the
    loop — it's guaranteed done by then.
    """
    i = 0
    while True:
        try:
            future.result(timeout=interval)
            return
        except concurrent.futures.TimeoutError:
            yield messages[i % len(messages)]
            i += 1


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


def submit_query_stream(
    question: str, api_url: str, api_key: str, top_k: float,
    mode: str, as_of_raw: str, advisory: bool, chat_history: list,
):
    """Generator that streams the answer while updating chat history."""
    empty_df = pd.DataFrame(columns=_EMPTY_DF_COLS)
    history = _to_gradio5_history(chat_history)

    if not question.strip():
        yield (
            _append_message(history, "assistant", "Please enter a question."),
            _empty_citations_md(), empty_df, "", "", "⚪ N/A", "", "", "", "",
            *_blank_previews(), *_hidden_meta(), "",
        )
        return

    current_history = _append_message(history, "user", question)

    try:
        as_of = _parse_as_of(as_of_raw)
    except ValueError:
        yield (
            _append_message(current_history, "assistant", "**Error:** 'As of date' must be YYYY-MM-DD."),
            _empty_citations_md(), empty_df, "", "", "⚪ Error", "", "", "", "",
            *_blank_previews(), *_hidden_meta(), "",
        )
        return

    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key

    payload = {"question": question, "top_k": int(top_k),
               "mode": mode, "advisory": bool(advisory), "as_of": as_of}

    try:
        _validate_api_url(api_url)

        query_future = _executor.submit(
            httpx.post, api_url, json=payload, headers=headers, timeout=120.0,
        )
        for msg in _cycle_messages_until_done(query_future, _QUERY_STAGE_MESSAGES):
            yield (
                current_history, _empty_citations_md(), empty_df, "", "", "⚪ Processing…", "", "", "", "",
                *_blank_previews(), *_loading_meta(msg), "",
            )
        resp = query_future.result()

        if resp.status_code != 200:
            error_msg = f"**Error:** API returned status code {resp.status_code}\n\n{resp.text}"
            yield (
                _append_message(current_history, "assistant", error_msg),
                _empty_citations_md(), empty_df, "", "", "⚪ Error", "", "", "", "",
                *_blank_previews(), *_hidden_meta(), "",
            )
            return
        data = resp.json()
    except httpx.TimeoutException:
        yield (
            _append_message(current_history, "assistant", "**Request Failed:** API timed out."),
            _empty_citations_md(), empty_df, "", "", "⚪ Error", "", "", "", "",
            *_blank_previews(), *_hidden_meta(), "",
        )
        return
    except Exception as e:  # noqa: BLE001 - surface, don't crash the UI
        yield (
            _append_message(current_history, "assistant", f"**Request Failed:** {e}"),
            _empty_citations_md(), empty_df, "", "", "⚪ Error", "", "", "", "",
            *_blank_previews(), *_hidden_meta(), "",
        )
        return

    # Build streaming chunks (typing effect)
    answer_text = data.get("answer", "")
    if mode == "retrieval_only" and not data.get("abstained", False):
        answer_text = _RETRIEVAL_ONLY_BANNER + answer_text

    chunk_size = 20
    for i in range(0, len(answer_text), chunk_size):
        partial = answer_text[: i + chunk_size]
        yield (
            _append_message(current_history, "assistant", partial),
            _empty_citations_md(), empty_df, "", "", "⚪ Processing…", "", "", "", "",
            *_blank_previews(), *_hidden_meta(), "",
        )

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
            "Preview": item.get("preview", ""),
        })
    df = pd.DataFrame(
        [{k: v for k, v in r.items() if k != "Preview"} for r in df_rows]
    ) if df_rows else empty_df

    latency_ms = data.get("latency_ms", 0)
    latency = f"{latency_ms} ms"
    faithfulness = data.get("faithfulness", 0.0)

    certainty_str = data.get("certainty", "unknown")
    abstained = data.get("abstained", False)
    certainty_display = certainty_str
    if abstained:
        certainty_display += f" (Abstained: {data.get('abstention_reason', '')})"

    superseded = json.dumps(data.get("superseded", {}), indent=2)
    unsupported = ", ".join(data.get("unsupported_citations", [])) or "None"
    confidence_json = json.dumps(data.get("confidence", {}), indent=2)
    draft = data.get("draft_answer", "") or ""
    draft_md = (f"**Advisory draft — not authoritative**\n\n{draft}" if draft else "")
    retrieved_json = json.dumps(data.get("retrieved", []), indent=2)

    answer_content = answer_text if not abstained else f"⚠️ *Abstained: {data.get('abstention_reason', '')}*"
    final_history = _append_message(current_history, "assistant", answer_content)

    citations_md = _build_citations_markdown(df_rows) if df_rows else _empty_citations_md()

    certainty_badge_str = (
        _certainty_badge(certainty_str) if not abstained else f"🔴 {certainty_display}"
    )

    yield (
        final_history, citations_md, df, latency, f"{faithfulness:.2f}", certainty_badge_str,
        superseded, unsupported, confidence_json, draft_md,
        *_preview_updates(df_rows),
        *_visible_meta(latency_ms, faithfulness, certainty_badge_str),
        retrieved_json,
    )


def build_ui():
    with gr.Blocks(title="SEBI Circular RAG") as demo:
        gr.Markdown(
            "Local-first, Apple-Silicon Retrieval-Augmented Generation over Indian SEBI circulars. "
            "Hybrid FAISS + BM25 retrieval with cross-encoder reranking, supersession-aware citations "
            "and an abstention gate."
        )

        # Chat history (multi-turn). height= gives it its own bounded,
        # internally-scrolling area — without one, Gradio's autoscroll
        # (default True) has no scroll container of its own to act on and
        # instead scrolls the WHOLE PAGE to document.scrollHeight on every
        # component update anywhere in the app. autoscroll=False turns that
        # off entirely now that a bounded height makes it unnecessary for
        # keeping messages in view.
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
                # Connection settings (local-only: HTTP client to a
                # separately-run FastAPI backend, unlike the in-process
                # Spaces demo)
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
                        minimum=1, maximum=MAX_PREVIEWS, value=5, step=1, label="Top K Citations"
                    )
                    mode = gr.Radio(
                        choices=["rag", "retrieval_only"], value="rag", label="Mode",
                        info="Full RAG answer, or retrieval-only academic benchmark "
                             "(citations + metadata, no LLM).",
                    )
                    # type="string" is required: DateTime's default type
                    # ("timestamp") returns a float, which _parse_as_of's
                    # date.fromisoformat() can't parse. include_time=False
                    # keeps it date-only (a time-of-day has no meaning for an
                    # as-of-date query). See tests/test_app_asof.py for the
                    # regression guard on this exact config (Spaces twin).
                    as_of_input = gr.DateTime(
                        label="As of date (optional)",
                        include_time=False,
                        type="string",
                        info="Pick a date to score retrieval against the law in "
                             "force then — leave blank to use current law. "
                             "(Typed YYYY-MM-DD also accepted.)",
                    )
                    advisory = gr.Checkbox(
                        label="Advisory draft on gate failure", value=False,
                        info="Opt-in low-confidence draft when the abstention gate trips.",
                    )

                # Metadata bar — placed inside Settings for detail, but the
                # loading/badge row directly below Submit (see below) is the
                # above-the-fold copy of the same signal.
                with gr.Accordion("Metadata", open=False):
                    with gr.Row():
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

        # Loading/status message + metadata badge row — placed immediately
        # below Submit so it's visible without scrolling.
        loading_text = gr.Markdown(value="", visible=False)
        with gr.Row():
            latency_badge = gr.Markdown(value="", visible=False)
            faithfulness_badge = gr.Markdown(value="", visible=False)
            certainty_badge = gr.Markdown(value="", visible=False)

        # Citations with superseded highlighting
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

        citations_df = gr.Dataframe(
            headers=_EMPTY_DF_COLS,
            interactive=False, wrap=True,
        )

        _submit_outputs = [
            chatbot,
            citations_md,
            citations_df,
            latency_out,
            faithfulness_out,
            certainty_out,
            superseded_out,
            unsupported_out,
            confidence_out,
            draft_out,
            *preview_components,
            loading_text, latency_badge, faithfulness_badge, certainty_badge,
            retrieved_out,
        ]

        # chatbot doubles as its own history state: each call's output value
        # becomes the next call's input, the standard Gradio chat pattern —
        # no separate gr.State needed (avoids a stale-history bug class: a
        # State that is read as input but never written as output would
        # reset every turn after the first).
        _submit_inputs = [question_input, api_url, api_key, top_k, mode, as_of_input,
                          advisory, chatbot]

        submit_btn.click(fn=submit_query_stream, inputs=_submit_inputs, outputs=_submit_outputs)
        # Enter key submits too
        question_input.submit(fn=submit_query_stream, inputs=_submit_inputs, outputs=_submit_outputs)

        # Clear conversation: reset chat, citations and metadata back to
        # their initial empty states without a page reload.
        clear_btn.click(
            fn=lambda: (
                [],
                _empty_citations_md(), pd.DataFrame(columns=_EMPTY_DF_COLS),
                "", "", "", "None", "None", "{}", "",
                *_blank_previews(), *_hidden_meta(), "[]",
            ),
            outputs=[
                chatbot, citations_md, citations_df,
                latency_out, faithfulness_out, certainty_out, superseded_out, unsupported_out,
                confidence_out, draft_out,
                *preview_components,
                loading_text, latency_badge, faithfulness_badge, certainty_badge,
                retrieved_out,
            ],
        )

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(server_name="127.0.0.1", server_port=7860)
