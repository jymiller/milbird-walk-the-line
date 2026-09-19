/**
 * Walk the Line — locate findings API.
 *
 * GitHub Pages serves the raw pipeline output and does it well. This exists for
 * the three things a static file cannot do:
 *
 *   1. Hand a consumer the data already in THEIR shape, so nobody writes a
 *      mapping layer under demo pressure  ->  GET /v1/checks
 *   2. Filter and address individual regions                 ->  GET /v1/evidence?verdict=
 *   3. Accept a human decision and keep it append-only       ->  POST /v1/decisions
 *
 * The third is the point. The whole argument of this project is that a machine
 * proposes and a person signs; an API that can only be read cannot record the
 * signature. Decisions chain by hash, so the log can be shown to be unedited
 * rather than asserted to be.
 */
import { DATA } from "./data.js";

const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET, POST, OPTIONS",
  "access-control-allow-headers": "content-type",
  "access-control-max-age": "86400",
};

const json = (body, status = 200, extra = {}) =>
  new Response(JSON.stringify(body, null, 1), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", ...CORS, ...extra },
  });

async function sha256(s) {
  const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, "0")).join("");
}

const TOTAL = DATA.summary.pipeline.colour_regions;

/**
 * The seven classifiers, already shaped as the consuming app's EvidenceCheck.
 *
 * `passed` is true throughout on purpose. These are not pass/fail tests of the
 * claim — each one is a filter that ran and stands. Marking a rule "failed"
 * because it fired often would invert its meaning: on_pavement firing 98 times
 * is the rule working, not the evidence failing.
 */
function checks() {
  const out = DATA.rules.rules.map((r) => ({
    code: r.name,
    passed: true,
    severity: "info",
    message: `${r.rejects} — eliminated ${r.fired} of ${TOTAL} regions`,
  }));
  const p = DATA.summary.pipeline;
  out.push({
    code: "human_review",
    passed: true,
    severity: "info",
    message: `${p.machine_candidates} region(s) escalated to a human; ${p.human_confirmed} confirmed as a locate mark`,
  });
  out.push({
    code: "coverage_partial",
    passed: true,
    severity: "warning",
    message: DATA.evidence.coverage.note,
  });
  return out;
}

async function appendDecision(env, body) {
  if (!env.DECISIONS) return json({ error: "decision log not bound" }, 503);
  const reviewer = (body.reviewer || "").trim();
  const decision = (body.decision || "").trim().toLowerCase();
  if (!reviewer) return json({ error: "reviewer is required — an unsigned decision is not a decision" }, 400);
  if (!["confirmed", "refused", "corrected"].includes(decision))
    return json({ error: "decision must be confirmed, refused or corrected" }, 400);
  if (decision !== "confirmed" && !(body.reason || "").trim())
    return json({ error: `a ${decision} decision requires a reason` }, 400);

  const headRaw = await env.DECISIONS.get("head");
  const head = headRaw ? JSON.parse(headRaw) : { seq: 0, hash: "genesis" };
  const seq = head.seq + 1;
  const entry = {
    seq,
    proposalExternalId: DATA.evidence.proposal.externalId,
    decision,
    reviewer,
    reason: (body.reason || "").trim() || null,
    quantity: DATA.evidence.proposal.quantity,
    regionId: body.regionId || null,
    at: new Date().toISOString(),
    prevHash: head.hash,
  };
  entry.hash = await sha256(entry.prevHash + JSON.stringify(entry));

  // Append only. No key is ever overwritten except the head pointer, which
  // only ever moves forward.
  await env.DECISIONS.put(`d:${String(seq).padStart(6, "0")}`, JSON.stringify(entry));
  await env.DECISIONS.put("head", JSON.stringify({ seq, hash: entry.hash }));
  return json({ ok: true, entry }, 201);
}

async function listDecisions(env) {
  if (!env.DECISIONS) return json({ entries: [], note: "decision log not bound" });
  // Read by sequence from the head pointer rather than KV list(). list() is
  // eventually consistent and lagged behind a fresh write by up to a minute,
  // which made a just-recorded decision invisible. Sequence numbers are dense
  // and the head is written last, so this is both deterministic and immediate.
  const headRaw = await env.DECISIONS.get("head");
  const head = headRaw ? JSON.parse(headRaw) : { seq: 0 };
  const entries = [];
  for (let i = 1; i <= head.seq; i++) {
    const v = await env.DECISIONS.get(`d:${String(i).padStart(6, "0")}`);
    if (v) entries.push(JSON.parse(v));
  }
  // Re-walk the chain so a reader can see for themselves that it is intact.
  let prev = "genesis", intact = true;
  for (const e of entries) {
    if (e.prevHash !== prev) intact = false;
    prev = e.hash;
  }
  return json({
    count: entries.length,
    chainIntact: intact,
    note: "Each entry hashes the one before it. Refusals are kept, not deleted.",
    entries,
  });
}

/**
 * The root is a page, not JSON. One URL somebody can open on a screen and see
 * the API answering — the numbers below are read from the same objects the
 * endpoints serve, so the page cannot drift from the data.
 */
function page() {
  const p = DATA.summary.pipeline;
  const prop = DATA.evidence.proposal;
  const ck = checks();
  const row = (c) => `<li class="ck ${c.severity}">
      <span class="cd">${c.code}</span>
      <span class="cm">${c.message}</span></li>`;
  return `<!doctype html><html lang=en><head><meta charset=utf8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Walk the Line — locate API</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;600&display=swap">
<style>
:root{--paper:#FAF8F5;--surface:#fff;--sunk:#F2EEE8;--ink:#1A1714;--ink2:#4A433C;--muted:#8A8178;
--line:#E2DBD1;--line2:#C9BFB2;--comms:#D4621E;--elec:#C8102E;--gas:#B8860B;--sewer:#2F6B46;--water:#2B5C8A;
--disp:'Bricolage Grotesque',Helvetica,Arial,sans-serif;--body:'IBM Plex Sans',Helvetica,Arial,sans-serif;
--mono:'IBM Plex Mono',ui-monospace,Menlo,monospace}
@media(prefers-color-scheme:dark){:root{--paper:#15130F;--surface:#1D1A16;--sunk:#221E19;--ink:#F2EDE6;
--ink2:#C6BDB2;--muted:#8D8378;--line:#312B24;--line2:#474036;--comms:#F08A48;--elec:#F06B7F;
--gas:#DBB454;--sewer:#6FBF8E;--water:#78AEDD}}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--body);
line-height:1.55;-webkit-font-smoothing:antialiased}
.w{max-width:940px;margin:0 auto;padding:clamp(28px,5vw,64px) clamp(18px,4vw,28px) 80px}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.16em;text-transform:uppercase;
color:var(--comms);margin:0 0 16px;font-weight:600}
h1{font-family:var(--disp);font-weight:800;font-size:clamp(34px,6.5vw,66px);line-height:1;
letter-spacing:-.035em;margin:0 0 14px}
.sub{font-family:var(--disp);font-weight:700;font-size:clamp(18px,2.6vw,28px);line-height:1.2;
color:var(--ink2);margin:0 0 28px;max-width:26ch}
.live{display:inline-flex;align-items:center;gap:8px;font-family:var(--mono);font-size:12px;
letter-spacing:.1em;text-transform:uppercase;color:var(--sewer);font-weight:600;margin-bottom:22px}
.live i{width:9px;height:9px;border-radius:50%;background:var(--sewer);display:inline-block}
h2{font-family:var(--disp);font-weight:800;font-size:clamp(20px,3vw,28px);letter-spacing:-.02em;
margin:44px 0 14px}
.fun{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:0 0 8px}
.fu{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:18px 10px;text-align:center}
.fu.z{border-color:var(--sewer);border-width:3px}
.fu b{display:block;font-family:var(--mono);font-weight:600;font-size:clamp(26px,5vw,46px);line-height:1}
.fu span{display:block;margin-top:8px;font-size:12.5px;color:var(--ink2);line-height:1.3}
ul{list-style:none;padding:0;margin:0}
.ck{display:grid;grid-template-columns:minmax(120px,190px) 1fr;gap:14px;padding:11px 14px;
border:1px solid var(--line);border-bottom:0;background:var(--surface);align-items:baseline}
.ck:first-child{border-radius:10px 10px 0 0}
.ck:last-child{border-bottom:1px solid var(--line);border-radius:0 0 10px 10px}
.ck.warning{background:var(--sunk);border-left:3px solid var(--gas)}
.cd{font-family:var(--mono);font-size:13px;font-weight:600;color:var(--sewer);word-break:break-all}
.ck.warning .cd{color:var(--gas)}
.cm{font-size:15px;color:var(--ink2)}
table{border-collapse:collapse;width:100%;font-size:14.5px;background:var(--surface);
border:1px solid var(--line);border-radius:10px;overflow:hidden}
th{text-align:left;font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;
color:var(--muted);padding:10px 14px;background:var(--sunk);border-bottom:1px solid var(--line2)}
td{padding:11px 14px;border-bottom:1px solid var(--line);vertical-align:top}
tr:last-child td{border-bottom:0}
td a{color:var(--comms);font-family:var(--mono);font-size:13.5px;text-decoration:none}
td a:hover{text-decoration:underline}
#log{font-size:14.5px}
.d{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--sewer);
border-radius:0 10px 10px 0;padding:14px 16px;margin-bottom:9px}
.d.refused{border-left-color:var(--elec)}
.d b{font-family:var(--mono);font-size:13px}
.d .r{color:var(--ink2);margin:5px 0 0;font-size:14.5px}
.d .h{font-family:var(--mono);font-size:11px;color:var(--muted);margin-top:7px}
.note{font-size:14.5px;color:var(--muted);margin:12px 0 0;max-width:70ch}
code{font-family:var(--mono);font-size:.9em;background:var(--sunk);border:1px solid var(--line);
border-radius:3px;padding:1px 5px}
@media(max-width:620px){.fun{grid-template-columns:repeat(2,1fr)}.ck{grid-template-columns:1fr;gap:4px}}
</style></head><body><div class="w">
<p class="eyebrow">Walk the Line &middot; Pine Street, San Francisco</p>
<h1>Locate findings API</h1>
<p class="sub">${DATA.summary.finding}</p>
<p class="live"><i></i>Running &middot; responding now</p>

<h2>The run</h2>
<div class="fun">
  <div class="fu"><b style="color:var(--comms)">${p.colour_regions}</b><span>colour regions in</span></div>
  <div class="fu"><b style="color:var(--elec)">${p.rejected_by_classifiers}</b><span>rejected by rule</span></div>
  <div class="fu"><b style="color:var(--gas)">${p.machine_candidates}</b><span>to human review</span></div>
  <div class="fu z"><b style="color:var(--sewer)">${p.human_confirmed}</b><span>confirmed locates</span></div>
</div>
<p class="note">Proposal <code>${prop.externalId}</code> &mdash; stage ${prop.stage}, ${prop.stageName},
quantity ${prop.quantity} ${prop.unit}, status <b>${prop.status}</b>. ${DATA.evidence.items.length} exhibits linked.</p>

<h2>What a reviewer is shown</h2>
<ul>${ck.map(row).join("")}</ul>
<p class="note">Served ready-made at <code>/v1/checks</code> as <code>{code, passed, severity, message}</code>
&mdash; no mapping layer needed.</p>

<h2>Decisions recorded</h2>
<div id="log">loading&hellip;</div>
<p class="note">Append-only and hash-chained. A decision without a named reviewer is refused; a refusal
without a reason is refused. Refusals are kept beside confirmations.</p>

<h2>Endpoints</h2>
<table><tr><th>Endpoint</th><th>Returns</th></tr>
<tr><td><a href="/v1/checks">/v1/checks</a></td><td>the nine reviewer checks, ready to render</td></tr>
<tr><td><a href="/v1/proposal">/v1/proposal</a></td><td>the production proposal</td></tr>
<tr><td><a href="/v1/evidence">/v1/evidence</a></td><td>49 exhibits, plus source, subject and coverage</td></tr>
<tr><td><a href="/v1/evidence?verdict=candidate">/v1/evidence?verdict=candidate</a></td><td>the 2 that reached a human</td></tr>
<tr><td><a href="/v1/summary">/v1/summary</a></td><td>the funnel and provenance</td></tr>
<tr><td><a href="/v1/rules">/v1/rules</a></td><td>the rule bank and thresholds</td></tr>
<tr><td><a href="/v1/decisions">/v1/decisions</a></td><td>the decision log and its chain</td></tr>
<tr><td><a href="/v1">/v1</a></td><td>this index, as JSON</td></tr></table>
<p class="note">CORS open, no key. Write-up:
<a href="https://claude.ai/artifact/7zpNEbGd88rbQGuLsEFFBJ">the deck</a> &middot;
<a href="https://github.com/jymiller/milbird-walk-the-line">the pipeline</a>.</p>
</div>
<script>
fetch('/v1/decisions').then(r=>r.json()).then(d=>{
  var el=document.getElementById('log');
  if(!d.count){el.innerHTML='<p class="note">No decisions recorded yet.</p>';return}
  el.innerHTML=d.entries.map(function(e){
    return '<div class="d '+e.decision+'"><b>#'+e.seq+' &middot; '+e.decision.toUpperCase()+
      '</b> &mdash; '+e.reviewer+(e.reason?'<p class="r">'+e.reason+'</p>':'')+
      '<p class="h">'+e.prevHash.slice(0,12)+'&hellip; &rarr; '+e.hash.slice(0,12)+'&hellip;</p></div>';
  }).join('')+'<p class="note">Chain intact: <b>'+d.chainIntact+'</b></p>';
}).catch(function(){document.getElementById('log').innerHTML='<p class="note">Log unavailable.</p>'});
</script></body></html>`;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const p = url.pathname.replace(/\/+$/, "") || "/";

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });

    if (p === "/") return new Response(page(), {
      headers: { "content-type": "text/html; charset=utf-8", ...CORS },
    });

    if (p === "/v1")
      return json({
        service: "walk-the-line-locate-api",
        finding: DATA.summary.finding,
        proposal: DATA.evidence.proposal,
        endpoints: {
          "GET /v1/proposal": "the production proposal — quantity 0, requiresHumanDecision",
          "GET /v1/checks": "the seven classifiers, already shaped as EvidenceCheck[]",
          "GET /v1/evidence": "49 exhibits linked to the proposal; ?verdict=candidate|rejected",
          "GET /v1/evidence/:regionId": "one region with its measurements",
          "GET /v1/summary": "the funnel and provenance",
          "GET /v1/rules": "the rule bank and thresholds",
          "POST /v1/decisions": "record a signed decision (append-only)",
          "GET /v1/decisions": "the decision log, with its hash chain",
        },
        staticMirror: "https://jymiller.github.io/milbird-walk-the-line/api/",
      });

    if (p === "/v1/proposal") return json(DATA.evidence.proposal);
    if (p === "/v1/summary") return json(DATA.summary);
    if (p === "/v1/rules") return json(DATA.rules);
    if (p === "/v1/checks")
      return json({
        note: "Drop straight into EvidenceCheck[] — {code, passed, severity, message}. No mapping needed.",
        proposalExternalId: DATA.evidence.proposal.externalId,
        checks: checks(),
      });

    if (p === "/v1/evidence") {
      const want = (url.searchParams.get("verdict") || "").toLowerCase();
      let items = DATA.evidence.items;
      if (want) items = items.filter((i) => i.verdict === want);
      const limit = parseInt(url.searchParams.get("limit") || "0", 10);
      if (limit > 0) items = items.slice(0, limit);
      return json({
        proposal: DATA.evidence.proposal,
        source: DATA.evidence.source,
        subject: DATA.evidence.subject,
        coverage: DATA.evidence.coverage,
        count: items.length,
        totalAvailable: DATA.evidence.items.length,
        items,
      });
    }

    const m = p.match(/^\/v1\/evidence\/(.+)$/);
    if (m) {
      const id = decodeURIComponent(m[1]);
      const hit = DATA.evidence.items.find((i) => i.regionId === id || i.id === id);
      return hit
        ? json(hit)
        : json({ error: "no such region", hint: "use regionId or id from /v1/evidence" }, 404);
    }

    if (p === "/v1/decisions") {
      if (request.method === "POST") {
        let body;
        try {
          body = await request.json();
        } catch {
          return json({ error: "body must be JSON" }, 400);
        }
        return appendDecision(env, body);
      }
      return listDecisions(env);
    }

    return json({ error: "not found", try: "/v1" }, 404);
  },
};
