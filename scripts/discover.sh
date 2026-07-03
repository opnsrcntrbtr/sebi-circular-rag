#!/usr/bin/env bash
# Daily new-circular discovery: emit JSON of circulars newer than the corpus.
set -uo pipefail
DIR="/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
cd "$DIR"; mkdir -p logs
export PYTHONPATH=src
.venv/bin/python scripts/discover_new.py 2>> logs/discover.log
