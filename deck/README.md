# Walk the Line — the deck

Published at <https://claude.ai/artifact/7zpNEbGd88rbQGuLsEFFBJ>.

Four slides, each with a fold you reach with the down arrow:

| Slide | Above the fold | Below |
|---|---|---|
| **Cover** | the neighbourhood: a distribution point, a trunk, a drop to every house | the margin drain |
| **The system** | evidence in, a signed number out | the GC fan-in, the five-layer architecture, the deep dives |
| **Simulated FiberHood** | the block, 26 photographs at measured GPS, the sign-off | plan vs block, measured vs derived, the colour finding, the sieve |
| **Live Demo** | four cards: control room, invite a worker, locates, code | the two devices, and a run-through you can follow |

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
| `devices.py` | TestFlight, the app and the laptop, on the Live Demo fold |

`render.sh <fragment> <out.png> [light|dark] [w,h]` renders any fragment against
the deck's real tokens. `verify.sh <slide-index> [fold]` shoots a slide inside the
assembled deck. Look at the PNG before believing anything.

## Two traps this repo has already fallen into

**The artifact host replaces the first `<style>` block in the head with its own
reset.** Anything appended there is destroyed on publish — it renders locally and
ships unstyled. All CSS must go in the block that carries `.deck{position:fixed`.
This is why the FiberHood slide once looked broken for a whole day.

**There IS a TestFlight build — do not conclude otherwise from the web bundle.**
An earlier pass grepped `walk-the-line.replit.app`'s JS bundle, found zero hits for
`TestFlight` / `itms-services` / `apps.apple.com` / Capacitor / React Native, and
published "there is no App Store build". That was wrong. The native app is a
**separate codebase**, built by Rene in a Replit workspace that is not this
repository and not on this machine — no `.xcodeproj` anywhere under
`~/src/work/milbird`, and no mobile repo under the `jymiller` GitHub account.
Absence from the web bundle says nothing about it.

What is actually known, from photographs of a real iPhone taken 2026-09-20:
TestFlight lists **Walk the Line, 1.0.0 (8), 90 days**; the app has three tabs,
**Assignments / History / Account**; Assignments was empty
("You're all caught up for today."); Account offers Sign out, so it authenticates.
`devices.py` draws exactly that and nothing more.

**Probing this API proves nothing about routes.** Everything under `/api` returns
`401` — including `/api/banana` — because an auth middleware sits in front of the
router. Every non-`/api` path returns `200`, including `/nonsense-xyz123`, because
the SPA serves index.html as a fallback. Route claims must come from the bundle,
which is real evidence; "I probed it and it answered" is not.

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

## iOS does not follow the deck palette

`#devsvg` scopes its own `--tf-*` and `--ap-*` tokens. TestFlight is black and the
app is light whichever theme the deck is in, because those are photographs of a
platform, not deck surfaces. Bound to `--ink`/`--paper` they invert in dark mode
and the content disappears. Shoot both themes before believing a device drawing.

SVG geometry belongs in the path, not in a CSS `transform`. The empty-state ring
was a `<circle>` rotated with `transform-origin:center`, which resolved against
the wrong box and threw it across the phone. It is now an explicit arc.
