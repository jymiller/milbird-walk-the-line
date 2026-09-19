"""Reject the mailbox.

The colour detector in find_locates.py answers one question: are there pixels
here in an APWA locate colour? On a real San Francisco block the answer is yes
constantly, and almost always wrong. A red doorstep, a blue USPS mailbox, a
drift of autumn leaves and a STOP sign all pass a colour threshold cleanly.

This is the second stage. Every candidate region the colour pass produced is
put through five cheap, named, independent classifiers. Each one votes reject
with a reason and a measured number. Nothing here is learned, nothing calls a
model, nothing needs the network — they are geometry and statistics over the
pixels the first stage already found.

    ../.venv-tts/bin/python classify.py ~/Downloads/IMG_2104.MOV ~/Downloads/locates.geojson

Writes, next to the geojson:
    classified.geojson     every candidate, with verdict + per-rule measurements
    rejects/               the rejected frames, annotated with the rule that killed them
    survivors/             what is left
"""
import json, os, sys, math, argparse
from collections import Counter

import cv2
import numpy as np

# ---------------------------------------------------------------- colour pass
# Identical ranges to find_locates.py — stage two must see exactly what stage
# one saw, or the rejections are about a different picture.
APWA = [
    ("orange", "communications / fibre", [((5, 120, 120), (18, 255, 255))]),
    ("red",    "electric",               [((0, 120, 90), (4, 255, 255)), ((170, 120, 90), (179, 255, 255))]),
    ("yellow", "gas, oil, steam",        [((22, 110, 130), (32, 255, 255))]),
    ("green",  "sewer, drain",           [((40, 80, 70), (85, 255, 255))]),
    ("blue",   "potable water",          [((95, 90, 70), (125, 255, 255))]),
    ("pink",   "temporary survey",       [((145, 70, 130), (169, 255, 255))]),
    ("purple", "reclaimed water",        [((128, 70, 70), (148, 255, 255))]),
]
MIN_AREA_PX     = 900
GROUND_FRACTION = 0.45

# ------------------------------------------------------------------ thresholds
# Calibrated against a 1920x1080 phone clip held at chest height. Every one is
# expressed as a fraction of frame width so the numbers travel to other cameras.
STROKE_MAX_FRAC  = 0.014   # inscribed radius. A 4in paint stroke at sidewalk
                           # range is ~26px half-width on 1920. A mailbox is 90+.
SLAB_AREA_FRAC   = 0.012   # a region bigger than 1.2% of frame is furniture
SLAB_EXTENT      = 0.70    # ...and if it also fills its own bounding box, it is solid
PAVEMENT_MIN     = 0.45    # this much of the surrounding ring must read as bare pavement
PAVEMENT_SAT_MAX = 70      # concrete and asphalt are grey: low saturation
HUE_STD_MAX      = 7.0     # one pigment is narrow. Leaf litter is a gradient.
SAT_MEAN_MIN     = 110     # locate paint is fluorescent. Dead leaves are not.
GROUND_BAND      = 0.62    # centroid must sit below this fraction of frame height
EXG_MAX          = 0.06    # excess-green index. Living foliage is green in a way
                           # pigment is not: it reflects hard in G against R and B.
VALUE_CV_MAX     = 0.28    # paint is a flat film on a flat surface, so brightness
                           # across it barely varies. A curled leaf is a 3-D object
                           # with a lit face and a shadowed one.

RULES = ["stroke_width", "not_a_slab", "on_pavement", "pigment_coherence",
         "ground_band", "not_vegetation", "flat_film"]
WHY = {
    "stroke_width":      "too thick to be a paint stroke",
    "not_a_slab":        "large and solid — street furniture, not a marking",
    "on_pavement":       "not surrounded by pavement",
    "pigment_coherence": "colour too mixed or too dull for marking paint",
    "ground_band":       "too high in frame to be on the ground",
    "not_vegetation":    "living foliage, not pigment",
    "flat_film":         "shaded like a 3-D object, not a flat film on flat ground",
}


def regions(frame):
    """Re-run stage one, but keep the mask so stage two can measure it."""
    h, w = frame.shape[:2]
    y0 = int(h * (1 - GROUND_FRACTION))
    ground = frame[y0:, :]
    hsv = cv2.cvtColor(cv2.GaussianBlur(ground, (5, 5), 0), cv2.COLOR_BGR2HSV)
    out = []
    for name, utility, ranges in APWA:
        mask = None
        for lo, hi in ranges:
            m = cv2.inRange(hsv, np.array(lo, np.uint8), np.array(hi, np.uint8))
            mask = m if mask is None else cv2.bitwise_or(mask, m)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            a = cv2.contourArea(c)
            if a < MIN_AREA_PX:
                continue
            out.append((name, utility, float(a), c, y0, hsv))
    return out


def measure(frame, colour, area, contour, y0, hsv):
    """Five numbers. Each one is a physical claim about what paint looks like."""
    H, W = frame.shape[:2]
    gh, gw = hsv.shape[:2]

    blob = np.zeros((gh, gw), np.uint8)
    cv2.drawContours(blob, [contour], -1, 255, -1)

    # 1. stroke width — biggest circle that fits inside the region.
    #    Paint is a stroke; a mailbox is a slab.
    dist = cv2.distanceTransform(blob, cv2.DIST_L2, 5)
    stroke_px = float(dist.max())

    # 2. slab test — how much of its own bounding box does it fill?
    x, y, bw, bh = cv2.boundingRect(contour)
    extent = area / float(max(1, bw * bh))

    # 3. pavement surround — dilate, subtract, look at the ring.
    #    Bare concrete and asphalt are grey: low saturation, mid brightness.
    k = max(9, int(round(min(bw, bh) * 0.6)) | 1)
    ring = cv2.subtract(cv2.dilate(blob, np.ones((k, k), np.uint8)), blob)
    rpix = hsv[ring > 0]
    if len(rpix):
        grey = (rpix[:, 1] < PAVEMENT_SAT_MAX) & (rpix[:, 2] > 35) & (rpix[:, 2] < 235)
        pavement = float(grey.mean())
    else:
        pavement = 0.0

    # 4. pigment coherence — one can of paint is one hue, and a bright one.
    bpix = hsv[blob > 0]
    hues = bpix[:, 0].astype(np.float32)
    if colour == "red":                      # red wraps 179->0; unwrap before stdev
        hues = np.where(hues > 90, hues - 180, hues)
    hue_std = float(hues.std()) if len(hues) else 99.0
    sat_mean = float(bpix[:, 1].mean()) if len(bpix) else 0.0

    # 5. ground band — where the region actually sits in the full frame.
    cy_full = (y + bh / 2.0 + y0) / float(H)

    # 6. vegetation — excess-green index. A leaf is a chlorophyll reflectance
    #    curve; a can of marking paint is not.
    bgr = frame[y0:, :][blob > 0].astype(np.float32)
    if len(bgr):
        tot = bgr.sum(axis=1) + 1e-6
        exg = float(((2 * bgr[:, 1] - bgr[:, 2] - bgr[:, 0]) / tot).mean())
    else:
        exg = 0.0

    # 7. flat film — paint lies flat, so it is evenly lit. A curled leaf or any
    #    rounded object carries its own shading.
    v = bpix[:, 2].astype(np.float32) if len(bpix) else np.array([1.0], np.float32)
    value_cv = float(v.std() / max(1.0, v.mean()))

    return {
        "exg": round(exg, 4),
        "value_cv": round(value_cv, 3),
        "stroke_px": round(stroke_px, 1),
        "stroke_frac": round(stroke_px / W, 5),
        "extent": round(extent, 3),
        "area_frac": round(area / float(W * H), 5),
        "pavement_surround": round(pavement, 3),
        "hue_std": round(hue_std, 2),
        "sat_mean": round(sat_mean, 1),
        "centroid_y_frac": round(cy_full, 3),
        "bbox": [int(x), int(y + y0), int(bw), int(bh)],
    }


def vote(m):
    """Each rule rejects independently. Returns the list of rules that fired."""
    fired = []
    if m["stroke_frac"] > STROKE_MAX_FRAC:
        fired.append("stroke_width")
    if m["area_frac"] > SLAB_AREA_FRAC and m["extent"] > SLAB_EXTENT:
        fired.append("not_a_slab")
    if m["pavement_surround"] < PAVEMENT_MIN:
        fired.append("on_pavement")
    if m["hue_std"] > HUE_STD_MAX or m["sat_mean"] < SAT_MEAN_MIN:
        fired.append("pigment_coherence")
    if m["centroid_y_frac"] < GROUND_BAND:
        fired.append("ground_band")
    if m["exg"] > EXG_MAX:
        fired.append("not_vegetation")
    if m["value_cv"] > VALUE_CV_MAX:
        fired.append("flat_film")
    return fired


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("geojson", nargs="?", default=os.path.expanduser("~/Downloads/locates.geojson"))
    a = ap.parse_args()

    geo = json.load(open(a.geojson))
    feats = geo["features"]
    want = {int(round(f["properties"]["t"])): f for f in feats}
    outdir = os.path.dirname(os.path.abspath(a.geojson))
    for d in ("rejects", "survivors"):
        os.makedirs(os.path.join(outdir, d), exist_ok=True)

    cap = cv2.VideoCapture(a.video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    rows, n = [], 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        t = int(round(n / fps))
        if n % int(fps) or t not in want:
            n += 1
            continue
        for colour, utility, area, cnt, y0, hsv in regions(frame):
            m = measure(frame, colour, area, cnt, y0, hsv)
            fired = vote(m)
            rows.append({"t": t, "colour": colour, "utility": utility,
                         "area": int(area), "rejected_by": fired,
                         "verdict": "candidate" if not fired else "rejected", **m})
        n += 1
    cap.release()

    kept = [r for r in rows if r["verdict"] == "candidate"]
    rej = [r for r in rows if r["verdict"] == "rejected"]
    tally = Counter(x for r in rej for x in r["rejected_by"])

    print(f"colour pass      {len(rows):>4} regions across {len(want)} frames")
    print(f"after classifiers{len(kept):>4} candidates, {len(rej)} rejected\n")
    print("rejections by rule (a region can fire several):")
    for r in RULES:
        print(f"   {r:<20} {tally.get(r,0):>4}   {WHY[r]}")

    json.dump({"rules": RULES, "why": WHY,
               "thresholds": {"stroke_max_frac": STROKE_MAX_FRAC, "slab_area_frac": SLAB_AREA_FRAC,
                              "slab_extent": SLAB_EXTENT, "pavement_min": PAVEMENT_MIN,
                              "hue_std_max": HUE_STD_MAX, "sat_mean_min": SAT_MEAN_MIN,
                              "ground_band": GROUND_BAND, "exg_max": EXG_MAX,
                              "value_cv_max": VALUE_CV_MAX},
               "regions": rows},
              open(os.path.join(outdir, "classified.json"), "w"), indent=1)
    print(f"\n  {os.path.join(outdir, 'classified.json')}")


if __name__ == "__main__":
    main()
