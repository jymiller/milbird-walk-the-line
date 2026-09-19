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

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const p = url.pathname.replace(/\/+$/, "") || "/";

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });

    if (p === "/" || p === "/v1")
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
