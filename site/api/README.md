# Locate API v2 — for the Walk the Line front end

Static JSON, CORS-open, served from GitHub Pages. No key, no auth, no rate limit.

**Base:** `https://jymiller.github.io/milbird-walk-the-line/api/`

## Breaking change from v1 — read this first

v1 published **53 detections as findings**. They were colour matches, not locate marks:
the four largest were a red-painted doorstep, a USPS mailbox, a drift of fallen leaves
and a STOP sign. v2 publishes the whole pipeline instead, and the honest count is **zero**.

| | v1 | v2 |
|---|---|---|
| `locates.json` features | 53, all treated as real | **124**, every colour region, kept or rejected |
| Reading a feature | every feature is a locate | check `properties.verdict` |
| `summary.json` | `detections: 53` | `pipeline: {colour_regions, rejected_by_classifiers, machine_candidates, human_confirmed}` |
| `stage2.json` | `quantity: 53` | `quantity: 0` |
| New | — | `rules.json` |

**Geometry is unchanged.** Every feature still carries a `Point` derived from the same
±7m GPS anchor, so an existing map layer keeps working. Filter before you plot.

## Endpoints

| Endpoint | Returns |
|---|---|
| `summary.json` | The funnel: 124 regions in → 122 rejected → 2 to human → 0 confirmed. Plus `rejections_by_rule` and `provenance`. |
| `rules.json` | The seven classifiers, their thresholds, and how many regions each rejected. |
| `locates.json` | GeoJSON FeatureCollection, 124 features — every region with its verdict and the seven measurements behind it. |
| `stage2.json` | The proposed Stage 2 (Utility Locates) record. `quantity: 0`, `requiresHumanDecision: true`. |
| `health.json` | Liveness and counts. |

## The one field that matters

```js
const { features } = await (await fetch(BASE + 'locates.json')).json();

features.filter(f => f.properties.verdict === 'candidate');  // 2 — reached a human
features.filter(f => f.properties.verdict === 'rejected');   // 122 — and why, below
```

`verdict` is `"candidate"` or `"rejected"`. **Nothing in this API is `confirmed`** —
no human confirmed any region as a locate mark, because none of them was one.

## Why a region was rejected

`properties.rejected_by` is an array of rule names, empty for a candidate. A region can
fire several. Every rule has a measured number beside it in the same properties object:

| Rule | Rejects | Read it against |
|---|---|---|
| `stroke_width` | Too thick to be a paint stroke | `stroke_px`, `stroke_frac` |
| `on_pavement` | Not surrounded by bare pavement | `pavement_surround` (0–1) |
| `not_vegetation` | Living foliage, not pigment | `exg` (excess-green index) |
| `ground_band` | Too high in frame to be on the ground | `centroid_y_frac` |
| `pigment_coherence` | Colour too mixed or too dull for marking paint | `hue_std`, `sat_mean` |
| `not_a_slab` | Large and solid — street furniture | `area_frac`, `extent` |
| `flat_film` | Shaded like a 3-D object, not a flat film | `value_cv` |

So a UI can say *"rejected: too thick — 195px against a 15px limit"* rather than showing
a confidence score nobody can argue with.

## Other properties

`t` (seconds into the clip), `colour`, `utility` (APWA class), `area` (px),
`bbox` `[x, y, w, h]` in the 1080×1920 frame, `position_provenance`.

## Suggested UI

1. Default to the **2 candidates**, with the 122 rejections behind a toggle.
2. On a rejected region, show `rejected_by` and the number that caused it.
3. Show the funnel from `summary.json` — it is the most honest thing on the page.
4. Surface `stage2.json`'s `note` verbatim. Absence of marking *is* the finding.

Regenerate: `python locates/build_api.py classified.json site/api locates.geojson`
