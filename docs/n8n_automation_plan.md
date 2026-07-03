# n8n Automation Plan — SEBI Circular RAG

Automates the repetitive operational sections of `docs/USAGE.md` using the
self-hosted n8n at `http://localhost:5678`. Alerts go to a **local log file + macOS
notification** (no external credentials).

> **Note (Execute Command unavailable):** this n8n build (npm, nvm node v24) does not
> load the `n8n-nodes-base.executeCommand` node ("Unrecognized node type"), so the
> workflows use **HTTP + Code nodes only**. A tiny local **ops HTTP server**
> (`scripts/ops_server.py`, port 8765, localhost-only) runs the repo scripts and
> returns their JSON; n8n calls it over HTTP. This sidesteps the blocked node and
> keeps all logic in the repo.

## 1. What is automated (and why it suits n8n)

| Workflow | USAGE section | Cadence | Repetitive task automated |
|----------|---------------|---------|---------------------------|
| 1. Corpus refresh | §4 pipeline + §8 eval | weekly | scrape new circulars → reindex → restart API → report metrics |
| 2. Health monitor | §7 operations | every 5 min | poll `/health`; alert if the API is down/degraded |
| 3. Eval canary | §8 evaluation | daily | run the golden-set metrics; alert on regression |
| 4. New-circular digest | §4.1 scraping | daily | detect newly published circulars; digest the titles |
| 5. Query smoke test | §5 API | every 6h | live `/query`; alert if `faithfulness != 1`, abstained, or no citations |

n8n is a good fit: these are **scheduled, multi-step, conditional-alert** jobs.
The heavy work (models, scraping) stays in the repo scripts; n8n only schedules,
parses the JSON they print, applies thresholds, and notifies.

## 2. Architecture

```
n8n Schedule Trigger ─▶ HTTP Request (ops server)  ─▶ Code (parse JSON + decide)
                        │  returns metrics/status JSON   │ returns [] (OK) or [{title,message}]
   health: HTTP GET localhost:8000/health (the RAG API) ▼
                                       HTTP POST localhost:8765/notify?title=..&message=..
                                       (runs only if Code returned an item)  ├─ append logs/automation.log
                                                                             └─ macOS notification
```

Ops server endpoints (all 127.0.0.1:8765): `GET /ping`, `GET /canary`,
`GET /discover`, `GET /smoketest`, `POST /refresh`, `POST /notify`. The Code node returns an **empty
array when everything is OK**, so the Notify node only fires on an alert (n8n skips
downstream nodes when a node yields 0 items). The weekly refresh always emits a
one-line summary.

## 3. Repo pieces added (already created & tested)

Wrapper scripts (each prints a single JSON line to stdout; noise → `logs/*.log`):

- `scripts/refresh.sh` — scrape (last 45 days, ≤100) → `make reindex` → restart the
  launchd API → `eval_json.py`. Emits corpus + metric JSON.
- `scripts/canary.sh` — `eval_json.py` only (retrieval/citation/abstention metrics
  over `golden_v4`, no LLM). ~40 s.
- `scripts/discover.sh` — `discover_new.py`: circulars newer than a seen-ids state
  file (`data/seen_circular_ids.txt`), seeded on first run. No downloads.
- `scripts/notify.sh "<title>" "<message>"` — append log + macOS notification.
- Helpers: `scripts/eval_json.py`, `scripts/discover_new.py`.
- **Ops HTTP server:** `scripts/ops_server.py` (+ `run_ops.sh`, `make ops`,
  `deploy/com.sebi-rag-ops.plist`) — localhost:8765; n8n calls it over HTTP.

Verified outputs on this machine:
`canary.sh` → `{"circulars":124,"chunks":22273,"recall_at_10":1.0,"citation_precision":0.728,"citation_recall":1.0,"abstention_accuracy":1.0}`;
`discover.sh` (first run) → `{"seeded":true,"new_count":0}`.

Importable workflows: `automation/n8n/1_corpus_refresh.json` … `4_new_circular_digest.json`.

## 4. Prerequisites

1. **Ops server running** (n8n calls it): `make ops` (foreground) or the launchd
   agent `deploy/com.sebi-rag-ops.plist` (persistent). Listens on `127.0.0.1:8765`.
   Verify: `curl http://127.0.0.1:8765/ping` → `{"ok":true}`.
2. **API running** (for the health monitor): `make serve` or `deploy/com.sebi-rag.plist`.
   Health checks `http://localhost:8000/health`; change the port in workflow 2 if
   you serve elsewhere.
3. **Paths** — the ops server and wrapper scripts use the absolute repo path
   `/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG`. If you move the repo,
   update the scripts' `DIR` and the plist paths (the workflows only reference
   `localhost:8765` / `localhost:8000`, so they don't need path edits).
4. **launchd label** — `refresh.sh` restarts the API via
   `launchctl kickstart -k gui/<uid>/com.sebi-rag`; harmless if the agent isn't
   installed (guarded with `|| true`). Install the API plist to enable auto-reload.
5. **Optional auth** — set `SEBI_OPS_TOKEN` for the ops server and add an
   `X-Ops-Token` header to the n8n HTTP nodes (localhost-only, so usually not needed).

## 5. Setup steps (n8n UI)

1. Open `http://localhost:5678`.
2. Start the ops server: `make ops` (or install `deploy/com.sebi-rag-ops.plist`).
   Confirm `curl http://127.0.0.1:8765/ping` returns `{"ok":true}`.
3. For each file in `automation/n8n/`: **Workflows → Import from File** → select the
   JSON. Four workflows appear. They reference `localhost:8765` (ops) and
   `localhost:8000` (health) — no path edits needed.
4. **Seed the digest state** once so it doesn't alert on the existing backlog:
   `curl http://127.0.0.1:8765/discover` (or execute workflow 4 manually once) —
   first run writes `data/seen_circular_ids.txt` and reports 0 new.
5. **Test each** with n8n's *Execute Workflow* button; check `logs/automation.log`
   and the macOS notification. (For the refresh test, expect ~10 min.)
6. **Activate** each workflow (toggle top-right) to enable the schedule.

Schedules (cron): refresh `0 2 * * 0` (Sun 02:00), health `*/5 * * * *`,
canary `0 6 * * *`, digest `0 7 * * *`.

## 6. Alert thresholds (Code nodes) — updated 2026-07-02 for golden_v5 + gate

`eval_json.py` now evaluates **golden_v5** (held-out paraphrases + hard
negatives; env `SEBI_RAG_GOLDEN` to override) and models the **production
abstention** (score floor 0.05 + subject-sim gate 0.42, mirroring api.py). It
also emits `injection_flagged` (F4 live scan; known-benign baseline = 1, the
broker master's password-policy text).

Baselines @ 207 circulars: recall_at_10 0.98, citation_precision ~0.73,
citation_recall ~0.91, abstention_accuracy ~0.875 (gate-modeled).

- **Canary alert** if `recall_at_10 < 0.97` OR `citation_recall < 0.85` OR
  `abstention_accuracy < 0.82` OR `citation_precision < 0.60` OR
  `injection_flagged > 1` (possible injected PDF — review flags before trusting).
- **Refresh** always notifies a summary (now incl. abstention + injection count);
  marks `ALERT` on the same rules.
- **Health alert** if `/health` is unreachable or `status != "ok"`.
- **Digest** notifies when `new_count > 0` and not the seed run; discovery now
  checks BOTH sections (circulars + master-circulars — masters drive supersession).

Tune the numbers in each workflow's Code node. Re-tighten after each corpus
growth + recalibration. NOTE: refresh is much faster since F3 — `make reindex`
is incremental (encodes only new/changed docs; ~82s for an 83-doc delta vs
8+ min full).

## 7. Security & safety

- Everything is **localhost**; nothing is exposed externally. The health check needs
  no API key (that endpoint is unauthenticated); if you later require it, add an
  `X-API-Key` header node.
- Execute Command runs as **your macOS user** — the scripts use absolute paths and
  set their own env; review them before enabling.
- Secrets stay in the environment (`SEBI_RAG_API_KEY`), never in n8n or the repo.
- The scraper inside `refresh.sh` keeps the polite defaults (rate limit, dedupe,
  provenance) from `docs/scraping_plan.md`.

## 8. Operational notes & troubleshooting

- **MPS contention:** `make reindex` and the API both use the GPU. Refresh runs at
  02:00 and restarts the API afterward so it serves the fresh index; keep heavy jobs
  off-hours. The canary loads models briefly (~40 s) — fine daily.
- **Long refresh run:** ensure n8n has no short `EXECUTIONS_TIMEOUT`; the refresh
  can take ~10 min (scrape + 5-min index build).
- **`ECONNREFUSED ::1:8765` (or :8000):** n8n resolved `localhost` to IPv6 `::1`,
  but the servers bind IPv4 `127.0.0.1`. The workflow URLs use `127.0.0.1` to avoid
  this — if you typed a URL yourself, use `127.0.0.1`, not `localhost`.
- **`Unrecognized node type: executeCommand`:** already handled — the workflows use
  HTTP + Code only and call the ops server. Ensure the ops server is running
  (`curl http://127.0.0.1:8765/ping`).
- **`make`/`launchctl` not found:** the ops server subprocess (esp. under launchd)
  may have a minimal PATH. `make` is `/usr/bin/make`, `launchctl` `/bin/launchctl`
  on macOS; if not found, prepend `PATH=/usr/bin:/bin:$PATH` in the wrapper script.
- **No macOS notification appears:** grant notification/automation permission to the
  process running n8n (System Settings → Notifications / Privacy → Automation). The
  log line in `logs/automation.log` is written regardless.
- **n8n node-version differences:** these workflows target recent n8n
  (scheduleTrigger 1.2, httpRequest 4.2, code 2, executeCommand 1). If import warns
  about a node version, open the node and re-save; logic is unchanged.
- **Pagination drift:** if SEBI changes the AJAX pager, `refresh.sh`/`discover.sh`
  degrade gracefully (page-0 results) — see `docs/scraping_plan.md`.

## 9. Extending

- Swap notifications to Slack/email by replacing the final Notify HTTP node with
  n8n's Slack/Email Send node (map `{{ $json.title }}` / `{{ $json.message }}`).
- **Query smoke test — added** (workflow 5 + `GET /smoketest`): the ops server calls
  the RAG API `/query` with the key from its env and asserts `faithfulness == 1.0`,
  not abstained, and citations present. Set `SEBI_RAG_API_KEY` in the ops server's
  env (matching the API's) and ensure the API is running; override the question with
  `SEBI_RAG_SMOKE_Q`. Restart the ops server after updating it to load `/smoketest`.
- Add **backup**: a `/backup` endpoint to `ops_server.py` that `tar`s `data/corpus`
  + `data/index` to a dated archive; call it via HTTP after a successful refresh.
