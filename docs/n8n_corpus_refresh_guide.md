# n8n Workflow Guide: SEBI RAG Corpus Refresh (Weekly)

## What this workflow does

Every Sunday at 2:00 AM, it:
1. Fetches new SEBI circulars (last 45 days, max 100)
2. Rebuilds the search index (only new/changed docs — ~82s)
3. Restarts the API so it serves the fresh index
4. Runs a quality check (recall, citation precision/recall, abstention, injection flags)
5. Sends you a notification if anything looks wrong

## Prerequisites (one-time setup)

| # | Step | Command / Action |
|---|------|------------------|
| 1 | Start the **ops server** (n8n's bridge to your scripts) | `make ops` (foreground) or install `deploy/com.sebi-rag-ops.plist` (background) |
| 2 | Verify it's running | `curl http://127.0.0.1:8765/ping` → `{"ok": true}` |
| 3 | Start the **RAG API** (the ops server calls it internally) | `make serve` (foreground) or install `deploy/com.sebi-rag.plist` (background) |
| 4 | Verify it's running | `curl http://127.0.0.1:8000/health` → `{"status":"ok","circulars":705,...}` |

> **Note:** The API must be running because the ops server's `/refresh` endpoint calls it internally. You don't need to call the API directly from n8n.

## Importing the workflow into n8n

1. Open **http://localhost:5678** in your browser
2. Click **Workflows** in the left sidebar
3. Click **Import from File** (top-right)
4. Select `automation/n8n/1_corpus_refresh.json`
5. The workflow appears with 4 nodes — click **Save**

## Understanding the 4 nodes

```
[Weekly Sun 02:00] → [POST /refresh] → [Parse metrics] → [Notify]
   (schedule)           (ops server)      (code logic)       (log + alert)
```

### Node 1: "Weekly Sun 02:00" (Schedule Trigger)
- **Type:** Schedule Trigger
- **What it does:** Fires automatically every Sunday at 2:00 AM (cron: `0 2 * * 0`)
- **You can change:** The schedule. Edit the node → "Cron Expression" → e.g., `0 3 * * 0` for 3 AM
- **Manual test:** Click "Execute Workflow" button (top-right) — it runs once immediately

### Node 2: "POST /refresh" (HTTP Request)
- **Type:** HTTP Request (POST)
- **URL:** `http://127.0.0.1:8765/refresh`
- **What it does:** Tells the ops server to run `scripts/refresh.sh`, which:
  - Runs `scripts/scrape_sebi.py --section circulars --from <45 days ago> --to today --max 100 --rate 3`
  - Runs `make reindex` (incremental — only encodes new/changed docs, ~82s)
  - Restarts the API via `launchctl kickstart -k gui/<uid>/com.sebi-rag`
  - Runs `scripts/eval_json.py` to generate quality metrics
  - Returns a JSON line with metrics like:
    ```json
    {"ts":"2026-07-28T18:33:09","circulars":705,"chunks":77841,"recall_at_10":0.98,
     "citation_precision":0.73,"citation_recall":0.91,"abstention_accuracy":0.875,
     "injection_flagged":10,"golden_file":"eval/golden/golden_v7.jsonl",
     "adjudicated_n":103,"gate":{"n":103,"recall_at_k":0.9126,...}}
    ```
- **Timeout:** 1,800,000 ms (30 minutes) — enough for scrape + reindex + eval
- **Error handling:** "Continue Regular Output" — if it fails, the workflow continues (Parse metrics will show the error)

### Node 3: "Parse metrics" (Code)
- **Type:** Code (JavaScript)
- **What it does:** Reads the JSON from Node 2, checks quality thresholds, and decides:
  - **Status = "OK"** if all metrics pass
  - **Status = "ALERT"** if any metric fails, listing which ones
- **Thresholds (from `docs/n8n_automation_plan.md` §6):**
  | Metric | Alert if below |
  |--------|---------------|
  | recall@10 | < 0.97 |
  | citation_recall | < 0.85 |
  | abstention_accuracy | < 0.82 |
  | injection_flagged | > 20 |
- **Output:** A single JSON object with `title` and `message` fields:
  - Success: `title: "SEBI RAG refresh OK"`, `message: "corpus 705 circulars 77841 chunks; recall 0.98 cit_prec 0.73 cit_recall 0.91 abst 0.875 inj 10"`
  - Failure: `title: "SEBI RAG refresh ALERT"`, `message: "...; REGRESSION recall,cit_recall"`

### Node 4: "Notify" (HTTP Request)
- **Type:** HTTP Request (POST)
- **URL:** `http://127.0.0.1:8765/notify?title=<title>&message=<message>`
- **What it does:**
  1. Appends a timestamped line to `logs/automation.log`
  2. Shows a macOS notification (via `osascript`)
- **When it fires:** Always (both OK and ALERT statuses)
- **If Node 2 failed:** Shows `title: "SEBI RAG refresh FAILED"`, `message: "refresh error <error details>"`

## Testing the workflow (manual execution)

1. Make sure the **ops server** and **API** are running (see Prerequisites above)
2. In n8n, click the **Execute Workflow** button (top-right, ▶️ icon)
3. Watch the execution:
   - Node 1: "Weekly Sun 02:00" — executes immediately (ignores schedule)
   - Node 2: "POST /refresh" — takes ~5–10 minutes (scrape + reindex + eval)
   - Node 3: "Parse metrics" — instant (just reads JSON)
   - Node 4: "Notify" — instant (writes log + shows notification)
4. Check results:
   - **macOS notification** (if permissions granted)
   - **`logs/automation.log`** — last line shows the result
   - **`logs/refresh.log`** — full details of the scrape + reindex

## Activating the schedule

1. Click the workflow title at the top
2. Toggle **Active** to ON (top-right)
3. It will now run automatically every Sunday at 2:00 AM

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ECONNREFUSED 127.0.0.1:8765` | Start the ops server: `make ops` |
| `ECONNREFUSED 127.0.0.1:8000` | Start the API: `make serve` |
| Workflow times out after 30 min | The refresh took too long (large delta). Check `logs/refresh.log` |
| No macOS notification | System Settings → Notifications → grant permission to n8n |
| "refresh FAILED" in log | Check `logs/refresh.log` for the actual error (scrape failure, index error, etc.) |
| High `injection_flagged` count | Run `scripts/ingest_pdf.py --scan` on the corpus to review flagged records |

## Can this workflow run independently?

**Yes.** This workflow is fully independent of the other 4 n8n workflows.

- It only depends on the **ops server** (port 8765) and the **RAG API** (port 8000)
- It does NOT require workflows 2–5 (Health Monitor, Eval Canary, New Circular Digest, Query Smoke Test) to be imported or active
- You can import, activate, and test this workflow alone

The other workflows have the same independence — each only needs the ops server and API running. They don't call each other.

## Quick reference

| Item | Value |
|------|-------|
| Workflow name | SEBI RAG - Corpus Refresh (weekly) |
| File | `automation/n8n/1_corpus_refresh.json` |
| Schedule | `0 2 * * 0` (Sunday 2:00 AM) |
| Ops server | `http://127.0.0.1:8765` |
| API | `http://127.0.0.1:8000` |
| Log file | `logs/automation.log` (summary), `logs/refresh.log` (details) |
| Expected runtime | ~5–10 minutes (scrape + incremental reindex + eval) |
| Thresholds | recall@10 ≥ 0.97, citation_recall ≥ 0.85, abstention ≥ 0.82, injection_flagged ≤ 20 |
