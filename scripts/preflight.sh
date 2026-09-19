#!/usr/bin/env bash
# Vendor preflight. Read-only, no secrets sent. Tells you which vendors are
# reachable and which local tools are installed BEFORE you depend on one.
# Usage: bash scripts/preflight.sh
set -u
pass=0; fail=0
ok(){ printf "  \033[32mPASS\033[0m %s\n" "$1"; pass=$((pass+1)); }
no(){ printf "  \033[31mFAIL\033[0m %s\n" "$1"; fail=$((fail+1)); }
warn(){ printf "  \033[33mWARN\033[0m %s\n" "$1"; }

http(){ curl -s -o /dev/null -w "%{http_code}" --max-time 12 "$1" 2>/dev/null || echo 000; }

echo "== local toolchain =="
for t in node npm python3 uv docker git gh; do
  command -v "$t" >/dev/null && ok "$t $($t --version 2>&1 | head -1 | tr -d '\n')" || no "$t missing"
done
[ -x .venv/bin/python ] && ok "venv $(.venv/bin/python -V)" || no "no .venv"
[ -x .venv/bin/agentx-trace-eval ] && ok "agentx launcher present" || no "agentx launcher missing"
npx --no-install edgeone --version >/dev/null 2>&1 && ok "edgeone CLI present" || no "edgeone CLI missing"
[ -d .agents/skills/edgeone-makers-tools ] && ok "edgeone-makers-tools skill installed" || no "edgeone skill missing"

echo; echo "== agentx engine (load-bearing for Track 2) =="
c=$(http http://localhost:4700/healthz)
if [ "$c" = 200 ]; then
  ok "engine healthy on :4700"
  if [ -n "${AGENTX_API_KEY:-}" ]; then
    a=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 -H "X-API-Key: $AGENTX_API_KEY" http://localhost:4700/api/v1/projects)
    [ "$a" = 200 ] && ok "API key accepted (X-API-Key)" || no "API key rejected ($a)"
  else
    warn "AGENTX_API_KEY unset — run: set -a && . ./.env && set +a"
  fi
else
  no "engine not up ($c). Start: .venv/bin/agentx-trace-eval -port 4700"
fi

echo; echo "== vendor endpoints (reachability only) =="
check(){ c=$(http "$2"); case "$c" in 2*|3*|401|403) ok "$1 reachable ($c)";; 000) no "$1 unreachable (timeout/DNS)";; *) warn "$1 returned $c";; esac; }
check "EdgeOne Makers docs" https://pages.edgeone.ai/document/product-introduction
check "EdgeOne register"    https://edgeone.ai/register
check "Memories.ai docs"    https://docs.memories.ai/home/overview
check "Memories.ai API"     https://api.memories.ai/serve/api/v1
check "AgentX docs"         https://developers.agentx.so/introduction
check "VeloDB"              https://www.velodb.io/cloud
check "Submission platform" https://figstudio-hackathon-production.up.railway.app/e/executable-world-2026
check "Handbook"            https://agentx-ai.notion.site/The-Executable-World-3ab03378208e80579131cc26b769a94f

echo; echo "== summary: $pass pass, $fail fail =="
[ "$fail" -eq 0 ] || exit 1
