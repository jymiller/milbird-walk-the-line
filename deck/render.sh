#!/bin/bash
# render.sh <fragment.svg|fragment.html> <out.png> [light|dark]
# Wraps a fragment in the deck's real tokens and screenshots it with headless Chrome.
set -e
FRAG="$1"; OUT="$2"; MODE="${3:-light}"; WIN="${4:-1400,900}"
D=$(dirname "$OUT"); mkdir -p "$D"
TOK_LIGHT='--paper:#E7E3D6;--surface:#F4F1E7;--sunk:#D8D3C2;--ink:#1E2318;--ink-2:#48513E;--muted:#7B8370;--line:#CCC6B4;--line-strong:#A9A491;--comms:#D2601C;--comms-soft:#F6E1CE;--elec:#AE2F39;--elec-soft:#F2DBDB;--gas:#BC8C1B;--gas-soft:#F3E7C7;--sewer:#4F7A3F;--sewer-soft:#DDE8D5;--water:#2F6480;--water-soft:#D9E4E9'
TOK_DARK='--paper:#13170F;--surface:#1C2117;--sunk:#242A1D;--ink:#EDF0E2;--ink-2:#BCC4AC;--muted:#828A75;--line:#2E3626;--line-strong:#454F39;--comms:#F0842F;--comms-soft:#33210F;--elec:#DF6068;--elec-soft:#331219;--gas:#DAAE3B;--gas-soft:#2E2510;--sewer:#6FBF8E;--sewer-soft:#1B2415;--water:#78AEDD;--water-soft:#14232B'
[ "$MODE" = dark ] && TOK="$TOK_DARK" || TOK="$TOK_LIGHT"
TMP=$(mktemp -t wtlart).html
{
cat <<EOF
<!doctype html><meta charset=utf8>
<link rel=stylesheet href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600&family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;600&display=swap">
<style>
:root{$TOK;--display:'Oswald',Arial,sans-serif;--mono:'IBM Plex Mono',monospace;--body:'IBM Plex Sans',Arial,sans-serif}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--body);padding:0}
.scene svg,svg{display:block;width:100%;height:auto;max-width:1320px;margin:0 auto}
</style>
EOF
cat "$FRAG"
} > "$TMP"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
  --virtual-time-budget=5000 --window-size=$WIN \
  --screenshot="$OUT" "file://$TMP" >/dev/null 2>&1
rm -f "$TMP"
echo "$OUT  $(du -h "$OUT" | cut -f1)"
