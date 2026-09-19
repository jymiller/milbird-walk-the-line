# The Executable World — event repo

**Event key:** `the-executable-world-a-full-stack-ai-hackathon-m-19b2b4249d`
**When:** Saturday 19 September 2026, doors 08:30, **submission closes 15:30**
**Where:** 724 Pine St, San Francisco, CA 94108

**Prep notebook:** https://claude.ai/artifact/2MuMMnjtPFSoBEHPSgLe2G

## Live

| | |
|---|---|
| Locate inventory + API | https://jymiller.github.io/milbird-walk-the-line/ |
| Write-up | https://claude.ai/artifact/7zpNEbGd88rbQGuLsEFFBJ |
| Submitted demo | https://walkthelin3.replit.app/ |
| App repo | https://github.com/CloudCorpRecords/not_a_hacker_thing |

Endpoints: `/api/locates.json` · `/api/summary.json` · `/api/stage2.json`
Published from the `gh-pages` branch. The EdgeOne Makers implementation (Blob + Cloud
Functions) is in `makers/` — correct against their SDK, blocked on account credits.


Authority for this build, its trace, and its submission evidence. Campaign
strategy stays in `hackathon-prep`. Source of truth for rules is the organizers'
[Notion handbook](https://agentx-ai.notion.site/The-Executable-World-3ab03378208e80579131cc26b769a94f).

## The number that shapes everything

Build sprint is **10:30–15:15**. That is 285 minutes, not a day. Freeze at
**14:15** leaves 60 minutes for submission, package and rehearsal.

## Start of day

```bash
cd ~/src/work/milbird/hackathons/fig
.venv/bin/agentx-trace-eval -port 4700 &     # prints a fresh API key — paste into .env
set -a && . ./.env && set +a
bash scripts/preflight.sh                     # expect 21/21
.venv/bin/python scripts/smoke_agentx.py      # expect PASS
```

## What is already verified (2026-09-18)

| Thing | State | Evidence |
|---|---|---|
| AgentX SDK 0.8.28 + engine 0.3.31 | installed, venv py3.12 | `scripts/preflight.sh` |
| AgentX trace round-trip | **PASS** — span read back | `.hackathon/evidence/agentx-smoke.txt` |
| EdgeOne CLI 1.6.40 | installed repo-local | `npx edgeone makers --help` |
| edgeone-makers-tools skill | installed, **unreviewed** | `.agents/skills/` |
| 8 vendor endpoints | reachable | `.hackathon/evidence/preflight-2026-09-18.txt` |

## Gotchas already paid for

- AgentX auth header is **`X-API-Key`**, not `Authorization: Bearer`. Bearer returns 401.
- `traces.list()` returns `{"traces": [...], "hasNextPage", "nextCursor", "totalCount"}`.
  It is a dict — `len()` gives 4 (the key count), not the row count.
- The AgentX key is regenerated on every engine boot. Re-paste into `.env` each morning.
- EdgeOne CLI deploys need `--area overseas` (per the sponsor onboarding guide).
- Non-interactive EdgeOne auth is `EDGEONE_PAGES_API_TOKEN`.

## Approval gates (STRATEGY.md)

Not taken without John saying so: spending, registration, organizer/judge contact,
**submission**, **public publication or deployment**, **commit or push**.

## Layout

```
.hackathon/event.json              handoff descriptor, rubric, timing, prizes
.hackathon/env.requirements.json   values-free env contract
.hackathon/trace.jsonl             append-only, conforms to event-trace.schema.json
.hackathon/evidence/               receipts
scripts/preflight.sh               vendor + toolchain check, no secrets
scripts/smoke_agentx.py            independent trace round-trip check
```
