"""The seam: locate detections become a PROPOSED production record.

Takes locates.geojson from find_locates.py and submits it to the fiber
operations API as a capture against Stage 2 — Utility Locates.

The machine proposes. A human confirms or refuses. Nothing here auto-commits.

    ../.venv-tts/bin/python bridge_to_api.py locates.geojson --project 1
    ../.venv-tts/bin/python bridge_to_api.py locates.geojson --project 1 --dry-run

Routes used (read from Rene's artifacts/api-server/src/routes/operations.ts):
    GET  /projects/:projectId/field-context   → resolve site, crew and work-type ids
    POST /projects/:projectId/captures        → submit the capture
    GET  /projects/:projectId/proposals       → read back what is awaiting review
"""
import argparse, hashlib, json, os, sys, urllib.request, urllib.error
from datetime import datetime, timezone

STAGE_UTILITY_LOCATES = 2

# APWA colour → what a locate of that colour actually asserts is under the ground.
UTILITY = {
    "orange": "communications / fibre", "red": "electric", "yellow": "gas, oil, steam",
    "green": "sewer, drain", "blue": "potable water", "pink": "temporary survey",
    "purple": "reclaimed water",
}


def call(base, path, method="GET", body=None, timeout=25):
    url = base.rstrip("/") + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw.strip() else None)
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"raw": raw[:600]}
    except Exception as e:
        return 0, {"error": str(e)}


def pick(rows, *names):
    """Find an id field on whatever shape field-context returns."""
    if not isinstance(rows, list) or not rows:
        return None
    r = rows[0]
    if isinstance(r, dict):
        for n in names:
            if n in r:
                return r[n]
        return r.get("id")
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("geojson")
    ap.add_argument("--api", default=os.environ.get("FIBER_API", "http://localhost:3000"))
    ap.add_argument("--project", type=int, default=1)
    ap.add_argument("--site", type=int)
    ap.add_argument("--crew", type=int)
    ap.add_argument("--work-type", type=int)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    geo = json.load(open(a.geojson))
    feats = geo.get("features", [])
    if not feats:
        sys.exit("no detections in that geojson — nothing to propose")

    # ---- what the video actually asserts -------------------------------------
    by_colour, positions = {}, []
    for f in feats:
        p = f.get("properties", {})
        c = p.get("primary", "unknown")
        by_colour[c] = by_colour.get(c, 0) + 1
        lon, lat = f.get("geometry", {}).get("coordinates", [None, None])
        if lat is not None:
            positions.append((round(lat, 6), round(lon, 6), p.get("t")))
    span = (min(p[2] for p in positions if p[2] is not None),
            max(p[2] for p in positions if p[2] is not None)) if positions else (0, 0)

    print(f"video evidence: {len(feats)} detections over {span[0]:.0f}–{span[1]:.0f}s")
    for c, n in sorted(by_colour.items(), key=lambda x: -x[1]):
        print(f"   {c:<8} {n:>3}  ({UTILITY.get(c, '?')})")

    # ---- resolve ids ---------------------------------------------------------
    site, crew, wt = a.site, a.crew, a.work_type
    if not all([site, crew, wt]):
        code, ctx = call(a.api, f"/projects/{a.project}/field-context")
        if code == 200 and isinstance(ctx, dict):
            site = site or pick(ctx.get("sites"), "id", "siteId")
            crew = crew or pick(ctx.get("crews"), "id", "crewId")
            for w in (ctx.get("workTypes") or []):
                if isinstance(w, dict) and w.get("stageNumber") == STAGE_UTILITY_LOCATES:
                    wt = wt or w.get("id")
                    print(f"   work type: stage {STAGE_UTILITY_LOCATES} → "
                          f"{w.get('name')} (id {w.get('id')}, unit {w.get('unit')}, "
                          f"max/crew-day {w.get('maxPerCrewDay')})")
            wt = wt or pick(ctx.get("workTypes"), "id")
            print(f"   resolved: site={site} crew={crew} workType={wt}")
        else:
            print(f"   field-context unavailable ({code}) — pass --site --crew --work-type")
            print(f"   {json.dumps(ctx)[:300]}")

    if not all([site, crew, wt]):
        sys.exit("could not resolve site/crew/workType; pass them explicitly")

    # ---- build the capture ---------------------------------------------------
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    work_date = now[:10]
    ext = "locate-video-" + hashlib.sha256(
        json.dumps(sorted(by_colour.items())).encode() + work_date.encode()
    ).hexdigest()[:12]

    note = (f"Detected from sidewalk video: {len(feats)} locate marks, "
            + ", ".join(f"{n} {c}" for c, n in sorted(by_colour.items(), key=lambda x: -x[1]))
            + f". Positions {span[0]:.0f}–{span[1]:.0f}s. "
            "Machine-proposed from video evidence — not confirmed.")

    body = {
        "siteId": site, "crewId": crew,
        "workDate": work_date, "capturedAt": now,
        "items": [{
            "externalId": ext,
            "workTypeId": wt,
            "quantity": f"{len(feats)}.00",
            "unit": "each",
            "note": note[:500],
        }],
    }

    print("\ncapture payload:")
    print(json.dumps(body, indent=2))

    if a.dry_run:
        print("\n[dry run] not submitted")
        return

    code, resp = call(a.api, f"/projects/{a.project}/captures", "POST", body)
    print(f"\nPOST /projects/{a.project}/captures → {code}")
    print(json.dumps(resp, indent=2)[:1400] if resp else "(no body)")

    if code in (200, 201):
        c2, props = call(a.api, f"/projects/{a.project}/proposals")
        if c2 == 200:
            items = props if isinstance(props, list) else (props or {}).get("items", [])
            print(f"\nawaiting review: {len(items)} proposal(s)")
            for p in items[:5]:
                if isinstance(p, dict):
                    print(f"   #{p.get('id')}  {p.get('status')}  qty={p.get('quantity')}  "
                          f"{str(p.get('note',''))[:70]}")
        print("\nThe record is PROPOSED. A human confirms or refuses it.")
        print("Then try to UPDATE the audit row and watch Postgres refuse:")
        print("   UPDATE fiber_production_audit_events SET decision='confirmed' WHERE id=1;")
        print("   ERROR: fiber production audit events are append-only")


if __name__ == "__main__":
    main()
