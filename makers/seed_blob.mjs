// Seed EdgeOne Makers Blob from this laptop — the "outside Functions" mode.
//   EDGEONE_PROJECT_ID=makers-xxx EDGEONE_PAGES_API_TOKEN=xxx node seed_blob.mjs
import { getStore } from "@edgeone/pages-blob";
import { readFileSync, readdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const projectId = process.env.EDGEONE_PROJECT_ID;
const token = process.env.EDGEONE_PAGES_API_TOKEN;
if (!projectId || !token) {
  console.error("set EDGEONE_PROJECT_ID and EDGEONE_PAGES_API_TOKEN");
  process.exit(1);
}

const store = getStore({ name: "locates", projectId, token, consistency: "strong" });

const geo = JSON.parse(readFileSync(join(process.env.HOME, "Downloads/locates.geojson"), "utf8"));
await store.setJSON("locates.geojson", geo);
console.log(`locates.geojson -> blob  (${geo.features.length} features)`);

const frameDir = process.env.FRAME_DIR || join(process.env.HOME, "Downloads/frames");
const frames = readdirSync(frameDir).filter((f) => f.endsWith(".jpg")).sort();
let n = 0;
for (const f of frames) {
  await store.set(`frames/${f}`, readFileSync(join(frameDir, f)));
  n++;
  if (n % 10 === 0) console.log(`  ${n}/${frames.length} frames`);
}
console.log(`${n} frames -> blob`);

const keys = await store.list();
console.log(`blob now holds ${(keys.blobs || keys).length ?? "?"} objects`);
