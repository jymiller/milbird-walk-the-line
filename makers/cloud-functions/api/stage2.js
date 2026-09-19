import { getStore } from "@edgeone/pages-blob";

const cors = { "Access-Control-Allow-Origin": "*" };

export async function onRequestGet() {
  const store = getStore({ name: "locates", consistency: "strong" });
  const geo = await store.get("locates.geojson", { type: "json" });
  if (!geo) return Response.json({ error: "no capture in blob yet" }, { status: 404, headers: cors });

  const tally = {};
  for (const f of geo.features || []) {
    const c = f.properties?.primary || "unknown";
    tally[c] = (tally[c] || 0) + 1;
  }
  const parts = Object.entries(tally).sort((a, b) => b[1] - a[1])
    .map(([c, n]) => `${n} ${c}`).join(", ");
  const n = (geo.features || []).length;

  return Response.json({
    stage: 2,
    stageName: "Utility Locates",
    status: "proposed",
    quantity: n,
    unit: "each",
    note: `Detected from sidewalk video: ${n} locate marks, ${parts}. `
        + "Machine-proposed from video evidence — not confirmed.",
    evidence: { kind: "video", source: "IMG_2104.MOV", frames: "/api/frames/<t>" },
    requiresHumanDecision: true,
  }, { headers: cors });
}
