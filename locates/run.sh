#!/usr/bin/env bash
# One command: video in, evidence out, proposed record on Stage 2.
#   bash run.sh ~/Downloads/sidewalk.mov [--submit]
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(dirname "$HERE")"
PY="$ROOT/.venv-tts/bin/python"
VIDEO="${1:?usage: run.sh <video> [--submit]}"
SUBMIT="${2:-}"
[ -f "$ROOT/.env" ] && { set -a; . "$ROOT/.env"; set +a; }

echo "=============================================================="
echo " 1. LOCAL — colour detection, no vendor, no network"
echo "=============================================================="
"$PY" "$HERE/find_locates.py" "$VIDEO" || exit 1
GEO="$(dirname "$VIDEO")/locates.geojson"

echo
echo "=============================================================="
echo " 2. MEMORIES.AI — the second opinion, by description"
echo "=============================================================="
if [ -n "${MEMORIES_API_KEY:-}" ]; then
  "$PY" "$HERE/memories_locates.py" "$VIDEO" || echo "  (memories.ai leg failed — local detection still stands)"
else
  echo "  skipped: MEMORIES_API_KEY not set in $ROOT/.env"
fi

echo
echo "=============================================================="
echo " 3. AGREEMENT — where two independent detectors concur"
echo "=============================================================="
"$PY" "$HERE/compare.py" "$GEO" "$(dirname "$VIDEO")/memories_locates.json" 2>/dev/null \
  || echo "  (only one detector produced output)"

echo
echo "=============================================================="
echo " 4. PROPOSE — Stage 2, Utility Locates"
echo "=============================================================="
if [ "$SUBMIT" = "--submit" ]; then
  "$PY" "$HERE/bridge_to_api.py" "$GEO" --project 1
else
  "$PY" "$HERE/bridge_to_api.py" "$GEO" --project 1 --dry-run
  echo "  (dry run — add --submit to actually POST)"
fi

echo
echo "open: $(dirname "$VIDEO")/locates_map.html"
