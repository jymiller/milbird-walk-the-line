# Walk the Line — the deck

Published at <https://claude.ai/artifact/7zpNEbGd88rbQGuLsEFFBJ>.

Four slides, each with a fold you reach with the down arrow:

| Slide | Above the fold | Below |
|---|---|---|
| **Cover** | the neighbourhood: a distribution point, a trunk, a drop to every house | the margin drain |
| **The system** | evidence in, a signed number out | the GC fan-in, the five-layer architecture, the deep dives |
| **Simulated FiberHood** | the block, 26 photographs at measured GPS, the sign-off | plan vs block, measured vs derived, the colour finding, the sieve |
| **Live Demo** | four cards: control room, invite a worker, locates, code | — |

## Building it

`src/head.html` + `src/body.html` concatenate into `walk-the-line.html`. That is the
whole build — there is no bundler.

The drawings are generated, not hand-written. Each generator emits an HTML
fragment and its CSS, which are then spliced into `src/`:

| Generator | Draws |
|---|---|
| `cover_scene.py` | the cover neighbourhood |
| `gc_fan.py` | eight trades converging on one signed record |
| `architecture.py` | the five layers, with a person in each |
| `measured_vs_derived.py` | one photograph, its EXIF fix, the same fix on the plan |
| `fiberhood_slide.py` | the block plan, both layers, the inspector |
| `photo_truth.py` | the by-eye verdict for all 53 photographs |

`render.sh <fragment> <out.png> [light|dark] [w,h]` renders any fragment against
the deck's real tokens. `verify.sh <slide-index> [fold]` shoots a slide inside the
assembled deck. Look at the PNG before believing anything.

## Two traps this repo has already fallen into

**The artifact host replaces the first `<style>` block in the head with its own
reset.** Anything appended there is destroyed on publish — it renders locally and
ships unstyled. All CSS must go in the block that carries `.deck{position:fixed`.
This is why the FiberHood slide once looked broken for a whole day.

**`class="door"` is not unique.** The block plan uses `<g class="door">` for the
724 Pine marker, so counting doors on the Live Demo slide has to be scoped to
that section.

## Geometry

The walk is fitted to the street grid that is actually there: 9.11 degrees,
measured off 256 m of Pine Street centreline in OSM, against the oriented
bounding box of the sixteen buildings on the block. 353 m at 0.87 m/s. See
`data/walk_rot.json` and `worker/geo.js`.

Photograph positions are measured (EXIF). Video reading positions are derived
from that walk. Every surface says which.
