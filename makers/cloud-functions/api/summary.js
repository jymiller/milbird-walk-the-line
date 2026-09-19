import { getStore } from "@edgeone/pages-blob";

const cors = { "Access-Control-Allow-Origin": "*", "Cache-Control": "public, max-age=60" };

const UTILITY = {
  orange: "communications / fibre", red: "electric", yellow: "gas, oil, steam",
  green: "sewer, drain", blue: "potable water", pink: "temporary survey",
  purple: "reclaimed water",
};

export async function onRequestGet() {
  const store = getStore({ name: "locates", consistency: "strong" });
  const geo = await store.get("locates.geojson", { type: "json" });
  if (!geo) return Response.json({ error: "no capture in blob yet" }, { status: 404, headers: cors });

  const byColour = {}, byUtility = {};
  let first = Infinity, last = -Infinity;
  for (const f of geo.features || []) {
    const c = f.properties?.primary || "unknown";
    byColour[c] = (byColour[c] || 0) + 1;
    const u = UTILITY[c] || "unknown";
    byUtility[u] = (byUtility[u] || 0) + 1;
    const t = f.properties?.t;
    if (typeof t === "number") { first = Math.min(first, t); last = Math.max(last, t); }
  }
  const p0 = geo.features?.[0]?.properties || {};

  return Response.json({
    video: "IMG_2104.MOV",
    detections: (geo.features || []).length,
    first_s: Number.isFinite(first) ? first : null,
    last_s: Number.isFinite(last) ? last : null,
    by_colour: byColour,
    by_utility: byUtility,
    anchor: { lat: p0.anchor_lat, lon: p0.anchor_lon, accuracy_m: p0.anchor_accuracy_m },
    provenance: {
      timestamps: "MEASURED — frame index / fps",
      colours: "MEASURED — HSV threshold against the APWA colour code",
      coordinates: "DERIVED — interpolated along the street axis from one GPS anchor. Not surveyed.",
    },
    storage: "EdgeOne Makers Blob",
  }, { headers: cors });
}
