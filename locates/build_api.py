"""Emit the static API from the classified regions.

The first version of this API published 53 detections as findings. They were
not findings, they were colour matches, and inspection showed the largest of
them to be a doorstep, a mailbox, a drift of leaves and a STOP sign. This
version publishes the whole pipeline instead: what colour found, what each
classifier rejected and why, and what survived to a human.

    ../.venv-tts/bin/python build_api.py ~/Downloads/classified.json site/api
"""
import json, os, sys, hashlib, datetime
from collections import Counter

VERSION = "2.0"

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Downloads/classified.json")
    out = sys.argv[2] if len(sys.argv) > 2 else "site/api"
    geo_src = sys.argv[3] if len(sys.argv) > 3 else os.path.expanduser("~/Downloads/locates.geojson")
    os.makedirs(out, exist_ok=True)

    # Coordinates come from stage one, which derived them from the single GPS
    # anchor. Carry them through so a map client keeps working across the
    # v1 -> v2 change; the verdict is what changed, not where the camera was.
    coords = {}
    if os.path.exists(geo_src):
        for f in json.load(open(geo_src))["features"]:
            t = int(round(f["properties"]["t"]))
            coords[t] = f["geometry"]["coordinates"]

    d = json.load(open(src))
    R = d["regions"]
    kept = [r for r in R if r["verdict"] == "candidate"]
    rej = [r for r in R if r["verdict"] == "rejected"]
    tally = Counter(x for r in rej for x in r["rejected_by"])
    frames = sorted({r["t"] for r in R})

    # Every machine candidate was looked at by a human. None was a locate mark.
    confirmed = []

    prov = {
        "timestamps": "MEASURED — frame index / fps",
        "colours": "MEASURED — HSV threshold against the APWA Uniform Color Code",
        "classifiers": "MEASURED — seven geometric and statistical rules over the same pixels",
        "coordinates": "DERIVED — interpolated along the street axis from a single GPS "
                       "anchor in the clip metadata (+-7.0m). Not surveyed.",
        "verdicts": "HUMAN — every surviving candidate was inspected by eye",
    }

    def w(name, obj):
        obj["api_version"] = VERSION
        obj["generated"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
        json.dump(obj, open(os.path.join(out, name), "w"), indent=1)
        print(f"  {out}/{name}")

    w("health.json", {
        "ok": True, "video": "IMG_2104.MOV", "duration_s": 404.1,
        "colour_regions": len(R), "frames_with_colour": len(frames),
        "machine_candidates": len(kept), "human_confirmed": len(confirmed),
        "endpoints": ["/api/health.json", "/api/locates.json", "/api/summary.json",
                      "/api/rules.json", "/api/stage2.json"],
        "note": "api_version 1 reported 53 detections. Those were colour matches, not "
                "locate marks. This version reports the full pipeline.",
    })

    w("rules.json", {
        "rules": [{"name": n, "rejects": d["why"][n], "fired": tally.get(n, 0)} for n in d["rules"]],
        "thresholds": d["thresholds"],
        "note": "Each rule votes to reject independently, with a measured number. "
                "A region can be rejected by several. Nothing here is learned and "
                "nothing calls a model — it is geometry and statistics over pixels.",
    })

    w("summary.json", {
        "video": "IMG_2104.MOV", "duration_s": 404.1,
        "pipeline": {
            "colour_regions": len(R),
            "rejected_by_classifiers": len(rej),
            "machine_candidates": len(kept),
            "human_confirmed": len(confirmed),
        },
        "rejections_by_rule": dict(tally),
        "colour_regions_by_colour": dict(Counter(r["colour"] for r in R)),
        "finding": "No utility locate marking was found on this segment of Pine Street.",
        "provenance": prov,
    })

    w("locates.json", {
        "type": "FeatureCollection",
        "note": "Every colour region, kept or rejected, with the measurements behind the verdict.",
        "features": [{
            "type": "Feature",
            "geometry": ({"type": "Point", "coordinates": coords[r["t"]]}
                         if r["t"] in coords else None),
            "properties": {**r,
                           "position_provenance": "DERIVED — interpolated along the street "
                                                  "axis from one +-7m GPS anchor. Not surveyed."},
        } for r in sorted(R, key=lambda x: x["t"])],
    })

    note = ("Video reviewed for utility locate marking: no marks found. "
            f"{len(R)} colour-matched regions across {len(frames)} frames were "
            f"examined; {len(rej)} were rejected by classifier, {len(kept)} reached "
            "human review, and none was a locate mark. Absence of marking is itself "
            "the finding: this segment has not been marked.")
    w("stage2.json", {
        "stage": 2, "stageName": "Utility Locates", "status": "proposed",
        "quantity": 0, "unit": "each",
        "note": note,
        "evidence": {"kind": "video", "source": "IMG_2104.MOV",
                     "regions_endpoint": "/api/locates.json",
                     "rules_endpoint": "/api/rules.json"},
        "requiresHumanDecision": True,
        "externalId": "wtl-" + hashlib.sha256(note.encode()).hexdigest()[:16],
    })


if __name__ == "__main__":
    main()
