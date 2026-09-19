# Walk the Line API — Cloudflare Worker

**Live:** https://walk-the-line-api.john-2ea.workers.dev

GitHub Pages serves the raw pipeline output and does it well. This exists for the three
things a static file cannot do.

**1. Hand a consumer the data in their shape.** `GET /v1/checks` returns the seven
classifiers already formed as the consuming app's `EvidenceCheck {code, passed, severity,
message}`, so nobody writes a mapping layer under demo pressure.

**2. Filter and address individual regions.** `GET /v1/evidence?verdict=candidate`,
`GET /v1/evidence/:regionId`.

**3. Accept a decision and keep it.** `POST /v1/decisions`.

The third is the point. The argument of this project is that a machine proposes and a
person signs — and an API that can only be read cannot record the signature.

## Endpoints

| Method | Path | Returns |
|---|---|---|
| GET | `/v1` | service index |
| GET | `/v1/proposal` | the production proposal — `quantity: 0`, `requiresHumanDecision` |
| GET | `/v1/checks` | 9 `EvidenceCheck` entries: 7 rules + `human_review` + `coverage_partial` |
| GET | `/v1/evidence` | 49 exhibits, plus `source`, `subject`, `coverage` |
| GET | `/v1/evidence?verdict=` | `candidate` (2) or `rejected` (47) |
| GET | `/v1/evidence/:regionId` | one region with all seven measurements |
| GET | `/v1/summary` | the funnel and provenance |
| GET | `/v1/rules` | the rule bank and thresholds |
| POST | `/v1/decisions` | record a signed decision |
| GET | `/v1/decisions` | the log, with `chainIntact` |

## The decision log

Append-only. Each entry hashes the one before it, starting at `genesis`, and
`GET /v1/decisions` re-walks the chain so a reader can verify it rather than take it on
trust. Three rules are enforced at the edge:

- **A reviewer name is required.** An unsigned decision is not a decision.
- **A refusal or correction requires a reason.**
- **Refusals are kept beside confirmations.** Nothing is deleted, so the record shows
  judgement being exercised rather than data being entered.

```bash
curl -X POST https://walk-the-line-api.john-2ea.workers.dev/v1/decisions \
  -H 'content-type: application/json' \
  -d '{"decision":"refused","reviewer":"A Name","reason":"Why"}'
```

Reads walk the sequence from the `head` pointer rather than calling `KV.list()`. `list()` is
eventually consistent and lagged a fresh write by up to a minute, which made a
just-recorded decision invisible — the failure a demo would find for you.

## Build and deploy

`data.js` is generated from `site/api/*.json`, so the Worker carries its own copy and has
no runtime dependency on Pages:

```bash
python3 - <<'PY'
import json
out = {n: json.load(open(f'site/api/{n}.json')) for n in ('evidence','rules','stage2','summary')}
for it in out['evidence']['items']: it.pop('confidenceNote', None)
open('worker/data.js','w').write("export const DATA = " + json.dumps(out, separators=(',',':')) + ";\n")
PY

cd worker && npx wrangler deploy
```

Regenerate `data.js` and redeploy whenever the pipeline output changes, or the Worker will
serve a stale copy while Pages serves the new one.
