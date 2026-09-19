<!-- Paste into the top of README.md in CloudCorpRecords/not_a_hacker_thing -->

# Walk the Line

**The work happens outside. The systems are inside. Nothing connects them.**

A fibre contractor runs eight build stages across hundreds of sites. Seven of the eight
reach no system at all — they happen on paper, and the office finds out weeks later.
We captured one of them with a phone, on Pine Street, during the sprint.

Built at **The Executable World**, San Francisco, 19 September 2026 — Track 2,
Production-ready AI Agent.

| | |
|---|---|
| **Live app** | https://walkthelin3.replit.app/ |
| **Write-up** | ARTIFACT_LINK_HERE |
| **Capture pipeline** | https://github.com/jymiller/milbird-walk-the-line |

## What ran

A 405-second walk, filmed on an iPhone, sampled a frame a second and thresholded in HSV
against the APWA Uniform Color Code:

```
405s walked · 419 frames sampled · 53 locate marks found

communications / fibre   25   ████████████████████
gas, oil, steam          14   ███████████
potable water             6   █████
sewer, drain              4   ███
electric                  4   ███
```

Orange dominating is what a fibre job *should* look like. We did not tune for that —
it fell out of the colour code, which is why it is evidence rather than decoration.

## The architecture

**Capture → Propose → Decide → Enforce.**

Detections land as `proposed` against Stage 2, Utility Locates — never `confirmed`.
Status moves `captured` → `proposed` → `needs_review` → `confirmed` | `refused`.
A per-crew-day plausibility ceiling routes implausible quantities to review automatically.

Enforcement lives on the deterministic side of the boundary. The audit trail is
append-only *in the database*, not in a prompt:

```sql
UPDATE fiber_production_audit_events SET decision='confirmed' WHERE id=1;
-- ERROR:  fiber production audit events are append-only
```

That is not a policy an agent was asked to respect. It is a guarantee no agent, and no
transport reaching that table, can route around.

## Provenance

Every record states which of its own fields are evidence and which are inference.

| Field | Status | How |
|---|---|---|
| Timestamp | **measured** | frame index ÷ frame rate |
| Colour & utility class | **measured** | HSV threshold against the APWA colour code |
| Region count & area | **measured** | contour detection in the ground plane |
| Coordinates | **derived** | interpolated along the street axis from one ±7m GPS anchor. **Not surveyed.** |
| Confirmation | **absent** | no human has confirmed these; the record knows it |

## What didn't work

The design calls for **two independent detectors** — colour detection locally, and a
Memories.ai Video Datalake integration finding marks by semantic description instead.
Where two independent methods agree, the mark is evidence. Where they disagree, a human
looks. That disagreement *is* the review queue.

The integration is built and tested against the live API. It did not run: the account
balance was `$0` and every billed call returns `quota_exceeded`. So today's 53 marks are
**uncorroborated**. We would rather say that than claim a vendor we did not get working.

## Stack

React · Vite · TanStack Query · Wouter · Leaflet — Express · Drizzle ORM · Postgres with
an append-only audit trigger — Python · OpenCV — deployed on Replit, also deployed to
Tencent EdgeOne Makers during the sprint.
