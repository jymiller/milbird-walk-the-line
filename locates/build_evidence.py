"""Publish the evidence, linked to the proposal.

An adjudication screen needs two things a detector usually does not give it:
a production proposal to decide about, and evidence attached to that proposal.
Evidence with nothing to adjudicate is just a photo.

This pairs them. Every frame becomes an evidence item carrying the proposal's
externalId, the verdict, the rules that fired, and the measurement behind each
rule — so the explanation shown to a human is derived, not generated.

    ../.venv-tts/bin/python build_evidence.py ~/Downloads/classified.json \
        ~/Downloads/frames site

Writes:
    site/frames/tNNNN.jpg      the marked frames, downscaled for the web
    site/api/evidence.json     evidence items, each linked to the proposal
"""
import json, os, sys, shutil, subprocess, datetime, hashlib
from collections import defaultdict

BASE = "https://jymiller.github.io/milbird-walk-the-line"
FRAME_W = 720          # enough to see paint; small enough to ship 53 of them

# The clip this run is about. An adjudication screen asks four things of any
# evidence it is shown — what is it, when was it taken, has it been altered,
# and what does it cover — so answer all four rather than only the verdict.
SOURCE = {
    "file": "IMG_2104.MOV",
    "sha256": "6ef6297733a3b39056e248cf08dbf6c93962a683f40e1e5274086593a0a3debf",
    "capturedAt": "2026-09-19T20:56:56Z",
    "durationSeconds": 404.1,
    "frameSize": [1080, 1920],
}
# Where the finding applies. Without this an ingest has to hard-code the ids,
# and a reviewer cannot tell which stretch of street was actually walked.
SUBJECT = {
    "street": "Pine St, San Francisco",
    "segmentDescription": "one continuous walk, filmed east-west at walking pace",
    "gpsAnchor": {"lat": 37.7912, "lon": -122.4078, "accuracyMetres": 7.0},
    "stageName": "Utility Locates",
    "workTypeCode": "LOCATE",
    "unit": "each",
}
# What this run does and does not cover. An adjudicator refusing a claim on the
# strength of one clip needs to know it is one clip.
COVERAGE = {
    "kind": "partial",
    "basis": "a single 404-second walk sampled at 1 frame per second",
    "framesSampled": 405,
    "framesWithColourMatch": 49,
    "note": "This is one pass along one side of one street. It is evidence about "
            "what the camera saw, not a survey of the whole site.",
}

# The thresholds classify.py decided against, so an explanation can quote both
# the measured value and the limit it failed.
LIMITS = {
    "stroke_width":      ("stroke_px", 15.1, "px inscribed radius", "against a limit of"),
    "on_pavement":       ("pavement_surround", 0.45, "of the surround reads as pavement", "needs at least"),
    "not_vegetation":    ("exg", 0.06, "excess-green index", "vegetation above"),
    "ground_band":       ("centroid_y_frac", 0.62, "down the frame", "must be below"),
    "pigment_coherence": ("sat_mean", 110, "mean saturation", "marking paint is above"),
    "not_a_slab":        ("area_frac", 0.012, "of the frame, solidly filled", "furniture above"),
    "flat_film":         ("value_cv", 0.28, "brightness variation", "flat paint is below"),
}
PLAIN = {
    "stroke_width":      "too thick to be a paint stroke",
    "on_pavement":       "not surrounded by pavement",
    "not_vegetation":    "living foliage, not pigment",
    "ground_band":       "too high in frame to be on the ground",
    "pigment_coherence": "colour too dull or too mixed for marking paint",
    "not_a_slab":        "large and solid — street furniture",
    "flat_film":         "shaded like a 3-D object, not a flat film",
}


def explain(region):
    """A sentence a human can check, not a confidence score they cannot."""
    if region["verdict"] == "candidate":
        return ("Passed all seven classifiers and was escalated to human review. "
                "A person inspected it and did not confirm it as a locate mark.")
    parts = []
    for rule in region["rejected_by"]:
        key, limit, unit, rel = LIMITS.get(rule, (None, None, "", ""))
        val = region.get(key)
        if val is None:
            parts.append(PLAIN.get(rule, rule))
        else:
            parts.append(f"{PLAIN[rule]} ({val}{'' if unit.startswith(' ') else ' '}{unit}, {rel} {limit})")
    return "Rejected: " + "; ".join(parts) + "."


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Downloads/classified.json")
    framedir = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/Downloads/frames")
    site = sys.argv[3] if len(sys.argv) > 3 else "site"

    d = json.load(open(src))
    by_t = defaultdict(list)
    for r in d["regions"]:
        by_t[r["t"]].append(r)

    outframes = os.path.join(site, "frames")
    os.makedirs(outframes, exist_ok=True)

    items, shipped = [], 0
    for t in sorted(by_t):
        # Stage one named frames from int(t) on a float; stage two rounds. A
        # frame at 13.5s is t0013 there and t=14 here, so check the neighbours.
        fn, tf = None, t
        for cand in (t, t - 1, t + 1):
            c = os.path.join(framedir, f"t{cand:04d}.jpg")
            if os.path.exists(c):
                fn, tf = c, cand
                break
        url = None
        if fn:
            dest = os.path.join(outframes, f"t{tf:04d}.jpg")
            r = subprocess.run(["sips", "-Z", str(FRAME_W), "-s", "formatOptions", "72",
                                fn, "--out", dest], capture_output=True)
            if r.returncode != 0:                      # sips is macOS-only; fall back to a copy
                shutil.copy(fn, dest)
            url = f"{BASE}/frames/t{tf:04d}.jpg"
            shipped += 1

        regions = sorted(by_t[t], key=lambda x: -x["area"])
        best = regions[0]
        candidates = [r for r in regions if r["verdict"] == "candidate"]
        # A stable id per region, so a reviewer can cite one, a UI can key on
        # one, and a second run can be diffed against this one.
        bx = best.get("bbox") or [0, 0, 0, 0]
        region_id = f"wtl-r-{t:04d}-{bx[0]}-{bx[1]}-{best['colour']}"
        items.append({
            "id": f"wtl-ev-{t:04d}",
            "regionId": region_id,
            "kind": "image",
            "url": url,
            "linkedTo": "wtl-3167e83ea982483c",
            "linkedToStage": 2,
            "linkedToStageName": "Utility Locates",
            "videoOffsetSeconds": t,
            "source": SOURCE["file"],
            "sourceSha256": SOURCE["sha256"],
            "capturedAt": SOURCE["capturedAt"],
            "regionCount": len(regions),
            "verdict": "candidate" if candidates else "rejected",
            "extraction": {
                "method": "deterministic — HSV colour match against the APWA Uniform Color "
                          "Code, then seven geometric and statistical classifiers",
                "colour": best["colour"],
                "utilityClass": best["utility"],
                "areaPx": best["area"],
                "rulesFired": best["rejected_by"],
                "measurements": {k: best[k] for k in
                                 ("stroke_px", "extent", "pavement_surround", "hue_std",
                                  "sat_mean", "exg", "value_cv", "centroid_y_frac")
                                 if k in best},
            },
            "explanation": explain(best),
            "confidence": None,
            "confidenceNote": "No confidence score is published. Every verdict is a named rule "
                              "and the measurement that triggered it, which a human can check.",
        })

    n_cand = sum(1 for i in items if i["verdict"] == "candidate")
    out = {
        "api_version": "2.0",
        "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "source": SOURCE,
        "subject": SUBJECT,
        "coverage": COVERAGE,
        "proposal": {
            "externalId": "wtl-3167e83ea982483c",
            "stage": 2, "stageName": "Utility Locates",
            "status": "proposed", "quantity": 0, "unit": "each",
            "requiresHumanDecision": True,
            "endpoint": f"{BASE}/api/stage2.json",
        },
        "summary": {
            "evidenceItems": len(items), "framesPublished": shipped,
            "framesWithACandidate": n_cand, "humanConfirmed": 0,
        },
        "note": "Every item here is linked to the proposal above, so it is adjudicable rather "
                "than evidence-only. The finding is that this segment has not been marked; these "
                "frames are what that conclusion was drawn from.",
        "items": items,
    }
    p = os.path.join(site, "api", "evidence.json")
    json.dump(out, open(p, "w"), indent=1)
    print(f"  {p}  ({len(items)} items, {shipped} frames published)")


if __name__ == "__main__":
    main()
