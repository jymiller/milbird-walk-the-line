"""Independent check: does an AgentX trace actually land in the engine?

Not "the SDK imported" — emits a span, flushes, then reads it back through the
SDK's own read API. Exit 0 only if that exact span comes back.

Response envelope (verified 2026-09-18, engine v0.3.31, SDK 0.8.28):
  {"traces": [...], "hasNextPage": bool, "nextCursor": str|None, "totalCount": int}
Each row: _id, name, input, output, latencyMs, sessionId, spanId, spanKind,
startedAt, source, createdAt, inputTokens, outputTokens, judgeScores.
"""
import json, sys, time, uuid

from agentx import AgentX

NAME = f"preflight-{uuid.uuid4().hex[:8]}"

client = AgentX.from_env()
print(f"engine: {client.base_url}  ping={client.ping()}")


@client.tracer.trace(NAME)
def answer(query: str) -> str:
    return f"echo::{query}"


answer("does the executable world trace path work?")
client.tracer.flush(timeout=15)

for attempt in range(1, 11):
    time.sleep(1.5)
    rows = client.traces.list(limit=50)["traces"]
    hit = [r for r in rows if r.get("name") == NAME]
    if hit:
        print(f"PASS: span '{NAME}' read back after {attempt} poll(s).")
        print(json.dumps(hit[0], default=str, indent=2))
        sys.exit(0)
    print(f"  poll {attempt}: {len(rows)} trace(s), none matching yet")

print(f"FAIL: '{NAME}' never appeared")
sys.exit(1)
