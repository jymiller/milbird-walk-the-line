import { getStore } from "@edgeone/pages-blob";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Cache-Control": "public, max-age=60",
};

export function onRequestOptions() {
  return new Response(null, { status: 204, headers: cors });
}

export async function onRequestGet({ request }) {
  const store = getStore({ name: "locates", consistency: "strong" });
  const geo = await store.get("locates.geojson", { type: "json" });
  if (!geo) {
    return Response.json({ error: "no capture in blob yet" }, { status: 404, headers: cors });
  }
  const url = new URL(request.url);
  let features = geo.features || [];
  const colour = url.searchParams.get("color");
  if (colour) {
    const want = new Set(colour.toLowerCase().split(","));
    features = features.filter((f) => want.has((f.properties?.primary || "").toLowerCase()));
  }
  const since = parseFloat(url.searchParams.get("since"));
  if (!Number.isNaN(since)) features = features.filter((f) => (f.properties?.t ?? 0) >= since);
  const until = parseFloat(url.searchParams.get("until"));
  if (!Number.isNaN(until)) features = features.filter((f) => (f.properties?.t ?? 0) <= until);

  return Response.json({ type: "FeatureCollection", features }, { headers: cors });
}
