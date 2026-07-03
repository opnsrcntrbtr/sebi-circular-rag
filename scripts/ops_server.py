#!/usr/bin/env python3
"""Local ops HTTP server so n8n can drive the pipeline via HTTP (no Execute Command
node needed). Binds 127.0.0.1 only. Runs the repo wrapper scripts as subprocesses
and returns their JSON. Optional shared secret via SEBI_OPS_TOKEN (header X-Ops-Token).

Endpoints:
  GET  /ping                      -> {"ok": true}
  GET  /canary                    -> eval metrics JSON        (canary.sh, ~40s)
  GET  /discover                  -> new-circular JSON         (discover.sh, ~20s)
  GET  /smoketest                 -> live /query check (faithfulness==1, not abstained)
  POST /refresh                   -> refresh metrics JSON      (refresh.sh, up to ~30m)
  POST /notify?title=..&message=..-> log + macOS notification  -> {"ok": true}

The smoke test calls the running RAG API (SEBI_RAG_API_URL, default
http://127.0.0.1:8000) with the key from SEBI_RAG_API_KEY (set it in this server's
env too if the API requires a key). Override the question with SEBI_RAG_SMOKE_Q.

Run:  PYTHONPATH=src .venv/bin/python scripts/ops_server.py   (or: make ops)
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DIR = Path(__file__).resolve().parents[1]
SCRIPTS = DIR / "scripts"
TOKEN = os.environ.get("SEBI_OPS_TOKEN")
PORT = int(os.environ.get("SEBI_OPS_PORT", "8765"))


def run_script(name: str, timeout: int) -> dict:
    p = subprocess.run(["bash", str(SCRIPTS / name)], capture_output=True,
                       text=True, timeout=timeout)
    out = (p.stdout or "").strip().splitlines()
    for line in reversed(out):                      # last JSON line wins
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                break
    return {"error": "no JSON output", "returncode": p.returncode,
            "stderr_tail": (p.stderr or "")[-200:]}


def smoketest() -> dict:
    import urllib.request

    api = os.environ.get("SEBI_RAG_API_URL", "http://127.0.0.1:8000")
    key = os.environ.get("SEBI_RAG_API_KEY")
    question = os.environ.get(
        "SEBI_RAG_SMOKE_Q",
        "What are the modified norms for nomination in demat accounts and mutual fund folios?")
    headers = {"Content-Type": "application/json"}
    if key:
        headers["X-API-Key"] = key
    data = json.dumps({"question": question}).encode()
    try:
        req = urllib.request.Request(api + "/query", data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=180) as resp:
            body = json.loads(resp.read())
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:180]}
    ok = ((not body.get("abstained")) and body.get("faithfulness") == 1.0
          and bool(body.get("citations")))
    return {
        "ok": ok,
        "faithfulness": body.get("faithfulness"),
        "abstained": body.get("abstained"),
        "citations": len(body.get("citations", [])),
        "unsupported": body.get("unsupported_citations", []),
        "latency_ms": body.get("latency_ms"),
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, obj: dict) -> None:
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _authed(self) -> bool:
        return (not TOKEN) or self.headers.get("X-Ops-Token") == TOKEN

    def _route(self):
        return urlparse(self.path).path

    def do_GET(self):
        if not self._authed():
            return self._send(401, {"error": "unauthorized"})
        try:
            r = self._route()
            if r == "/ping":
                return self._send(200, {"ok": True})
            if r == "/canary":
                return self._send(200, run_script("canary.sh", 300))
            if r == "/discover":
                return self._send(200, run_script("discover.sh", 180))
            if r == "/smoketest":
                return self._send(200, smoketest())
            return self._send(404, {"error": "not found"})
        except Exception as e:  # noqa: BLE001
            return self._send(500, {"error": str(e)})

    def do_POST(self):
        if not self._authed():
            return self._send(401, {"error": "unauthorized"})
        try:
            r = self._route()
            if r == "/refresh":
                return self._send(200, run_script("refresh.sh", 1800))
            if r == "/notify":
                q = parse_qs(urlparse(self.path).query)
                title = (q.get("title") or ["SEBI RAG"])[0]
                msg = (q.get("message") or [""])[0]
                (DIR / "logs").mkdir(exist_ok=True)
                with (DIR / "logs" / "automation.log").open("a", encoding="utf-8") as f:
                    f.write(f"{dt.datetime.now():%F %T} [{title}] {msg}\n")
                subprocess.run(
                    ["/usr/bin/osascript", "-e",
                     f"display notification {json.dumps(msg)} with title {json.dumps(title)}"],
                    capture_output=True)
                return self._send(200, {"ok": True})
            return self._send(404, {"error": "not found"})
        except Exception as e:  # noqa: BLE001
            return self._send(500, {"error": str(e)})

    def log_message(self, *a):  # silence access logs
        pass


if __name__ == "__main__":
    with ThreadingHTTPServer(("127.0.0.1", PORT), Handler) as s:
        print(f"ops server on 127.0.0.1:{PORT}", flush=True)
        s.serve_forever()
