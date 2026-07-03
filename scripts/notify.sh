#!/usr/bin/env bash
# Local notification: append to logs/automation.log + macOS notification.
# Usage: notify.sh "<title>" "<message>"
set -uo pipefail
DIR="/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
mkdir -p "$DIR/logs"
TITLE="${1:-SEBI RAG}"
MSG="${2:-}"
printf '%s [%s] %s\n' "$(date '+%F %T')" "$TITLE" "$MSG" >> "$DIR/logs/automation.log"
/usr/bin/osascript -e "display notification \"${MSG//\"/ }\" with title \"${TITLE//\"/ }\"" >/dev/null 2>&1 || true
