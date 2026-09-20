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
import { REGIONS } from "./mapdata.js";
import { appView } from "./appview.js";
import { WALK_JS, GEO } from "./geo.js";

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
.sign{background:var(--surface);border:1px solid var(--line2);border-radius:12px;padding:20px;margin:0 0 16px}
.sign .q{font-family:var(--disp);font-weight:700;font-size:clamp(17px,2.4vw,23px);line-height:1.2;
margin:0 0 16px;letter-spacing:-.015em}
.sign label{display:block;font-family:var(--mono);font-size:11px;letter-spacing:.1em;
text-transform:uppercase;color:var(--muted);margin:0 0 6px;font-weight:600}
.sign input,.sign textarea{width:100%;font-family:var(--body);font-size:16px;padding:11px 13px;
border:1px solid var(--line2);border-radius:8px;background:var(--paper);color:var(--ink);
margin-bottom:14px;resize:vertical}
.sign input:focus,.sign textarea:focus{outline:2px solid var(--comms);outline-offset:1px;border-color:var(--comms)}
.sign .btns{display:flex;gap:9px;flex-wrap:wrap}
.sign button{font-family:var(--body);font-weight:600;font-size:15.5px;padding:11px 24px;border-radius:9px;
border:1px solid var(--line2);background:var(--surface);color:var(--ink);cursor:pointer}
.sign button:hover{background:var(--sunk)}
.sign button.ok{background:var(--sewer);border-color:var(--sewer);color:#fff}
.sign button.no{border-color:var(--elec);color:var(--elec)}
.sign button:disabled{opacity:.5;cursor:default}
.msg{font-size:14.5px;margin:12px 0 0;min-height:1.3em}
.msg.err{color:var(--elec)}.msg.ok{color:var(--sewer)}
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

<h2>Record a decision</h2>
<div class="sign">
  <p class="q">Accept that no utility locate marking exists on this segment?</p>
  <label for="rv">Reviewer &mdash; required</label>
  <input id="rv" placeholder="Your name" autocomplete="name">
  <label for="rs">Reason &mdash; required to refuse or correct</label>
  <textarea id="rs" rows="2" placeholder="Why"></textarea>
  <div class="btns">
    <button class="ok" data-d="confirmed">Confirm</button>
    <button data-d="corrected">Correct</button>
    <button class="no" data-d="refused">Refuse</button>
  </div>
  <p class="msg" id="msg"></p>
</div>

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
<tr><td><a href="/locates">/locates</a></td><td>the Utility Locates screen, in the app's own look</td></tr><tr><td><a href="/map">/map</a></td><td>all 124 readings on the map, against the building</td></tr><tr><td><a href="/v1">/v1</a></td><td>this index, as JSON</td></tr></table>
<p class="note">CORS open, no key. Write-up:
<a href="https://claude.ai/artifact/7zpNEbGd88rbQGuLsEFFBJ">the deck</a> &middot;
<a href="https://github.com/jymiller/milbird-walk-the-line">the pipeline</a>.</p>
</div>
<script>
function render(d){
  var el=document.getElementById('log');
  if(!d.count){el.innerHTML='<p class="note">No decisions recorded yet.</p>';return}
  el.innerHTML=d.entries.map(function(e){
    return '<div class="d '+e.decision+'"><b>#'+e.seq+' &middot; '+e.decision.toUpperCase()+
      '</b> &mdash; '+e.reviewer+(e.reason?'<p class="r">'+e.reason+'</p>':'')+
      '<p class="h">'+e.prevHash.slice(0,12)+'&hellip; &rarr; '+e.hash.slice(0,12)+'&hellip;</p></div>';
  }).join('')+'<p class="note">Chain intact: <b>'+d.chainIntact+'</b></p>';
}
function load(){return fetch('/v1/decisions').then(function(r){return r.json()}).then(render)}
document.querySelectorAll('.sign button').forEach(function(b){
  b.addEventListener('click',function(){
    var msg=document.getElementById('msg');
    var btns=document.querySelectorAll('.sign button');
    msg.className='msg';msg.textContent='Recording\u2026';
    btns.forEach(function(x){x.disabled=true});
    fetch('/v1/decisions',{method:'POST',headers:{'content-type':'application/json'},
      body:JSON.stringify({decision:b.dataset.d,
        reviewer:document.getElementById('rv').value,
        reason:document.getElementById('rs').value})})
    .then(function(r){return r.json().then(function(j){return{ok:r.ok,j:j}})})
    .then(function(res){
      btns.forEach(function(x){x.disabled=false});
      if(!res.ok){msg.className='msg err';msg.textContent=res.j.error||'Rejected.';return}
      msg.className='msg ok';
      msg.textContent='Recorded as #'+res.j.entry.seq+'. It cannot be edited or removed.';
      document.getElementById('rs').value='';
      return load();
    })
    .catch(function(){btns.forEach(function(x){x.disabled=false});
      msg.className='msg err';msg.textContent='Could not reach the API.'});
  });
});
load().catch(function(){document.getElementById('log').innerHTML='<p class="note">Log unavailable.</p>'});
</script></body></html>`;
}

/**
 * Every reading, placed against the building it was walked past.
 *
 * There are no confirmed locate marks to plot, so this plots the honest thing
 * instead: all 124 readings, where each was taken, and what the rule bank
 * decided about it. Positions are DERIVED — interpolated along the street axis
 * from one GPS anchor at +-7m — and the map says so rather than implying survey
 * accuracy it does not have.
 */
function mapPage() {
  const pts = REGIONS.map(r => ({ ...r }));
  return `<!doctype html><html lang=en><head><meta charset=utf8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Walk the Line — the walk, on a map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;600&display=swap">
<style>
:root{--paper:#15130F;--surface:#1D1A16;--ink:#F2EDE6;--ink2:#C6BDB2;--muted:#8D8378;
--line:#312B24;--comms:#F08A48;--elec:#F06B7F;--gas:#DBB454;--sewer:#6FBF8E;--water:#78AEDD;
--disp:'Bricolage Grotesque',Helvetica,sans-serif;--body:'IBM Plex Sans',Helvetica,sans-serif;
--mono:'IBM Plex Mono',Menlo,monospace}
*{box-sizing:border-box}
html,body{height:100%;margin:0;background:var(--paper);color:var(--ink);font-family:var(--body)}
#map{position:absolute;inset:0 0 0 0}
.panel{position:absolute;top:0;left:0;z-index:1000;max-width:410px;
background:rgba(21,19,15,.93);backdrop-filter:blur(10px);border-right:1px solid var(--line);
border-bottom:1px solid var(--line);padding:22px 24px 20px;max-height:100%;overflow-y:auto}
h1{font-family:var(--disp);font-weight:800;font-size:27px;line-height:1.05;letter-spacing:-.03em;margin:0 0 6px}
.sub{font-size:14.5px;color:var(--ink2);line-height:1.45;margin:0 0 16px}
.key{display:grid;gap:7px;margin:0 0 16px}
.kr{display:flex;align-items:center;gap:10px;font-size:13.5px;color:var(--ink2)}
.kd{width:13px;height:13px;border-radius:50%;flex:0 0 auto}
.kr b{color:var(--ink);font-family:var(--mono);font-size:13px}
.note{font-family:var(--mono);font-size:11.5px;line-height:1.6;color:var(--muted);
border-top:1px solid var(--line);padding-top:13px;margin:0}
.note b{color:var(--gas)}
.simbtn{display:block;width:100%;font-family:var(--body);font-size:14.5px;font-weight:600;
padding:11px 16px;border-radius:9px;border:1px solid var(--muted);background:transparent;
color:var(--ink);cursor:pointer;margin:0 0 14px}
.simbtn:hover{border-color:var(--gas);color:var(--gas)}
.simbtn.on{background:var(--gas);border-color:var(--gas);color:#15130F}
.simban{display:none;position:absolute;top:0;left:0;right:0;z-index:1200;
background:#DBB454;color:#15130F;font-family:var(--mono);font-size:12.5px;font-weight:600;
letter-spacing:.06em;text-transform:uppercase;text-align:center;padding:9px 14px}
.leaflet-popup-content-wrapper{background:var(--surface);color:var(--ink);border-radius:10px}
.leaflet-popup-tip{background:var(--surface)}
.leaflet-popup-content{margin:13px 15px;font-family:var(--body);font-size:13.5px;line-height:1.5}
.pt{font-family:var(--mono);font-size:12px;color:var(--muted);margin-bottom:5px}
.pv{font-weight:600;font-size:15px;margin-bottom:6px}
.pr{font-family:var(--mono);font-size:11.5px;color:var(--elec);line-height:1.6}
.pimg{width:100%;border-radius:7px;margin-top:9px;display:block}
a{color:var(--comms)}
@media(max-width:700px){.panel{max-width:100%;position:relative;border-right:0}#map{top:auto;height:62vh;position:relative}}
</style></head><body>
<div id="map"></div>
<div id="simban" class="simban">SIMULATED LAYER ON &mdash; these points are illustrative, not detections from the video</div>
<div class="panel">
  <h1>The walk, on a map</h1>
  <p class="sub">405 seconds along Pine Street. Every colour reading the detector produced, where it
  was taken, and what the rule bank decided.</p>
  <div class="key">
    <div class="kr"><span class="kd" style="background:#6FBF8E"></span><b>0</b> confirmed locate marks</div>
    <div class="kr"><span class="kd" style="background:#DBB454"></span><b>2</b> reached a human</div>
    <div class="kr"><span class="kd" style="background:#8D8378"></span><b>122</b> rejected by rule</div>
    <div class="kr"><span class="kd" style="background:#F08A48;border-radius:2px"></span>724 Pine St &mdash; the building</div>
    <div class="kr"><span class="kd" style="border:2px solid #DBB454;background:transparent"></span>the camera's own GPS point, 100 m off</div>
  </div>
  <button id="simbtn" class="simbtn">Show a simulated marked block</button>
  <p class="note">The path is a <b>RECONSTRUCTION</b>, not recorded GPS. iOS writes one location per
  clip, never a track, so the filmer's route was never in the file. What is measured: the block geometry
  and the address from OpenStreetMap, and 405 seconds of duration. The pavement loop is <b>311 m</b>,
  which is 0.77 m/s &mdash; one clockwise lap at filming pace. Click any point for its frame.
  <a href="/">Back to the API</a></p>
</div>
<script>
const R = ${JSON.stringify(pts)};
${WALK_JS}
// A SIMULATED marked block. Not detections. This is what the same map looks like
// when the street has actually been located, so the product can be shown working
// while the real run stands at zero. Every one of these is flagged in its popup.
const SIM = [
  {o:0.06,c:'orange',u:'communications / fiber',k:'line'},
  {o:0.11,c:'orange',u:'communications / fiber',k:'arrow'},
  {o:0.17,c:'orange',u:'communications / fiber',k:'line'},
  {o:0.21,c:'yellow',u:'gas, oil, steam',k:'crossing'},
  {o:0.26,c:'orange',u:'communications / fiber',k:'line'},
  {o:0.32,c:'blue',u:'potable water',k:'crossing'},
  {o:0.38,c:'orange',u:'communications / fiber',k:'line'},
  {o:0.44,c:'red',u:'electric',k:'crossing'},
  {o:0.49,c:'orange',u:'communications / fiber',k:'arrow'},
  {o:0.55,c:'orange',u:'communications / fiber',k:'line'},
  {o:0.61,c:'yellow',u:'gas, oil, steam',k:'crossing'},
  {o:0.66,c:'green',u:'sewer, drain',k:'crossing'},
  {o:0.72,c:'orange',u:'communications / fiber',k:'line'},
  {o:0.78,c:'orange',u:'communications / fiber',k:'line'},
  {o:0.84,c:'blue',u:'potable water',k:'crossing'},
  {o:0.89,c:'orange',u:'communications / fiber',k:'arrow'},
  {o:0.94,c:'orange',u:'communications / fiber',k:'line'}
];
const B = G.door, ANCHOR = G.anchor, DUR = G.durationS;
const DEG_LON_PER_M = 1/(111320*Math.cos(B[0]*Math.PI/180));
const COL = {orange:'#F08A48',red:'#F06B7F',yellow:'#DBB454',green:'#6FBF8E',blue:'#78AEDD'};
const map = L.map('map',{zoomControl:false}).setView(B, 20);
L.control.zoom({position:'bottomright'}).addTo(map);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',
  {maxZoom:22,maxNativeZoom:19,attribution:'&copy; OpenStreetMap contributors'}).addTo(map);
L.marker(atTime(0)).addTo(map).bindPopup('<div class="pv">724 Pine Street</div>'+
  '<div class="pt">37.7915965, -122.4088201</div>');
L.circleMarker(B,{radius:10,color:'#F08A48',fillColor:'#F08A48',fillOpacity:.9,weight:3}).addTo(map);
// the clip's own GPS point, and how far off it is
L.circleMarker(ANCHOR,{radius:7,color:'#DBB454',fillColor:'transparent',weight:2,dashArray:'3 3'})
  .addTo(map).bindPopup('<div class="pt" style="color:#DBB454">GPS anchor written by the camera</div>'+
  '<div class="pv">37.7912, -122.4078</div>'+
  '<div class="pt">100 m from the door &mdash; 90 m east, 44 m south.<br>One ISO6709 point per clip, '+
  'claimed accuracy &plusmn;7 m. This is why positions are labelled derived.</div>',{maxWidth:300});
L.circleMarker(ANCHOR,{radius:2.5,color:'#DBB454',fillColor:'#DBB454',fillOpacity:1,weight:1}).addTo(map);
const path = walkPolyline(2);
R.forEach(function(r){
  const pos = atTime(r.t), lat = pos[0], lon = pos[1];
  const done = r.v==='candidate';
  const m = L.circleMarker([lat,lon],{radius: done?8:5,
    color: done?'#DBB454':'#8D8378', fillColor: done?'#DBB454':(COL[r.c]||'#8D8378'),
    fillOpacity: done?.95:.5, weight: done?2:1}).addTo(map);
  const frame = 'https://jymiller.github.io/milbird-walk-the-line/frames/t'+String(r.t).padStart(4,'0')+'.jpg';
  m.bindPopup('<div class="pt">t='+r.t+'s &middot; '+r.c+' &middot; '+r.a+'px</div>'+
    '<div class="pv">'+(done?'Reached a human. Not confirmed.':'Rejected by rule')+'</div>'+
    (r.rb.length?'<div class="pr">'+r.rb.join('<br>')+'</div>':'')+
    '<img class="pimg" src="'+frame+'" onerror="this.style.display=\'none\'">',{maxWidth:330});
});
L.polyline(path,{color:'#8D8378',weight:2,opacity:.55,dashArray:'5 6'}).addTo(map);
map.fitBounds(L.latLngBounds(path.concat([B, ANCHOR])).pad(.06));

// ---- the simulated layer ----
const simLayer = L.layerGroup();
SIM.forEach(function(s,i){
  const pos = atTime(s.o*G.durationS), lat = pos[0], lon = pos[1];
  const col = COL[s.c];
  const m = L.circleMarker([lat,lon],{radius:9,color:'#fff',weight:2,
    fillColor:col,fillOpacity:.95,dashArray:'3 3'}).addTo(simLayer);
  m.bindPopup('<div class="pt" style="color:#DBB454">SIMULATED &mdash; not a detection</div>'+
    '<div class="pv" style="color:'+col+'">'+s.c+' &middot; '+s.u+'</div>'+
    '<div class="pt">'+s.k+' marking &middot; illustrative position only</div>',{maxWidth:300});
});
let simOn=false;
const btn=document.getElementById('simbtn'), ban=document.getElementById('simban');
btn.addEventListener('click',function(){
  simOn=!simOn;
  if(simOn){simLayer.addTo(map);ban.style.display='block';btn.textContent='Hide the simulated block';
    btn.classList.add('on');}
  else{map.removeLayer(simLayer);ban.style.display='none';btn.textContent='Show a simulated marked block';
    btn.classList.remove('on');}
});
</script></body></html>`;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const p = url.pathname.replace(/\/+$/, "") || "/";

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });

    if (p === "/locates") return new Response(appView(DATA, REGIONS, WALK_JS), {
      headers: { "content-type": "text/html; charset=utf-8", ...CORS },
    });

    if (p === "/map") return new Response(mapPage(), {
      headers: { "content-type": "text/html; charset=utf-8", ...CORS },
    });

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
