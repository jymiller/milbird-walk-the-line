# The Executable World — event repo

**Event key:** `the-executable-world-a-full-stack-ai-hackathon-m-19b2b4249d`
**When:** Saturday 19 September 2026, doors 08:30, **submission closes 15:30**
**Where:** 724 Pine St, San Francisco, CA 94108

**Prep notebook:** https://claude.ai/artifact/2MuMMnjtPFSoBEHPSgLe2G

## What this is

A general contractor building **FiberHoods** — neighbourhood-scale fiber builds — is paid a fixed
price per meter on thin margins, and orchestrates every other trade: design, permits, locating,
hydrovac, boring, trenching, conduit, splicing, testing, restoration, inspection. Eight stages run a
FiberHood. **Only the first reaches any system.** The other seven end the day as a paper ticket that
reaches the office between one day and three weeks later.

Walk the Line reads utility locate marks off sidewalk video and photographs, proposes them as
production records, and refuses to confirm anything without a named human signature.

## Live, and verified

Every URL below returned 200 at the time of writing.

| | |
|---|---|
| **The locates screen** — the work, on the real block | https://walk-the-line-api.john-2ea.workers.dev/locates |
| **The API** — with a decision log you can sign | https://walk-the-line-api.john-2ea.workers.dev |
| **The write-up** | https://claude.ai/artifact/7zpNEbGd88rbQGuLsEFFBJ |
| **Build assessment** | https://claude.ai/artifact/4KbJNxXMVjHeZCLPH9gQhp |
| **Static mirror + 49 frame images** | https://jymiller.github.io/milbird-walk-the-line/api/ |
| **Submitted demo** (now behind sign-in) | https://walkthelin3.replit.app/ |
| **App repo** | https://github.com/CloudCorpRecords/not_a_hacker_thing |

Worker endpoints: `/v1/checks` · `/v1/proposal` · `/v1/evidence` · `/v1/summary` · `/v1/rules` ·
`GET|POST /v1/decisions` · `/locates` · `/map`. CORS open, no key.
Static: `/api/summary.json` · `/api/evidence.json` · `/api/locates.json` · `/api/rules.json` ·
`/api/stage2.json`, published from `gh-pages`.

## What works

**Detection, end to end, offline.** 405 seconds of phone video → HSV threshold against the APWA
Uniform Color Code → seven named geometric classifiers → a proposed Stage 2 record. No model, no
network, no API key.

**Provenance on every field.** Times are MEASURED, coordinates DERIVED, verdicts HUMAN, coverage
stated as partial. Confidence is explicitly `null`: every verdict is a named rule plus the
measurement that triggered it, so a reviewer can argue with `194.9px inscribed radius against a
15.1px limit` in a way nobody can argue with `0.87`.

**A decision log that refuses.** `POST /v1/decisions` rejects an unsigned decision, requires a reason
to refuse, keeps refusals beside confirmations, and hash-chains every entry.

**Evidence linked to a proposal.** 49 exhibits, each carrying the proposal id, the frame image, the
rules that fired and the number behind each one — so an adjudication screen can show a reason
instead of a score.

## What we measured, and it is not flattering

The detector first reported **53 locate marks**. Before publishing, the four largest were opened by
eye: a red-painted doorstep, a USPS mailbox, fallen leaves, and a STOP sign. **All four wrong.** The
claim that orange dominance was "the signature of a fiber job" was withdrawn.

Seven classifiers were then written. They reject 122 of 124 regions; two reached a human; none was a
locate mark.

Later, 53 field photographs — **every one carrying a GPS fix** — were labelled twice over
independently, with a third pass reserved for disagreement. **25 contain genuine locate paint**
across six APWA colours. That is the first positive class this project has had.

Measured against it:

| | |
|---|---|
| **Recall** | **0 of 25.** Not low — zero. |
| Why | 17 positives produce no colour region at all; the other 8 are rejected |
| Root cause | **84% of real locate paint is faded.** `SAT_MEAN_MIN` carries the comment "locate paint is fluorescent". Worn pigment on grey concrete sits below that floor. |
| Worse | one *negative* — an indoor scene — survives as a clean candidate. The pipeline finds more paint indoors than on a marked sidewalk. |

## What does not work yet

- **The detector does not detect.** It is a rejector. Every threshold was fitted with no positive
  class; `STROKE_MAX_FRAC` sits on the population median of the set it was judging.
- **Nothing has been ingested into the app.** The integration is documented, not built. The deployed
  app fetches this API in the browser and renders a panel that cannot be adjudicated.
- **Not reproducible from a clean clone.** No dependency manifest; the interpreter and the source
  video are gitignored.
- **No false-positive rate.** Only 3 of the 28 paint-free photos are genuine clean pavement; the rest
  are indoors. Recall is measurable, precision is not.
- **`not_vegetation` was refusing every gas and sewer locate** on arithmetic — excess-green reads
  +1.045 on APWA green pigment against +0.065 for a dry leaf. Fixed in source: for those two colours
  the rule now escalates to human review rather than deciding. **Not yet published** — adding a third
  verdict is a change to a value consumers already read.
- **Memories.ai never ran** ($0 balance). **AgentX** authenticated and contributed nothing. **EdgeOne**
  is written and correct against the SDK, blocked on credits.

## How far this got

From an unverified claim to a **measured failure with a known cause**, in one day, in public.

The best thing here is the retraction. The detector was confidently wrong about its four largest
findings, and **not one wrong answer reached a production record** — because the architecture
proposes and never decides. That gate held under real failure, observably, which is a better
argument than a clean run would have been.

The honest summary: **we built the loop's skeleton and about a third of its substance.** Capture
runs. Organise is the strongest leg. Use is where the value is and where the work remains.

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
