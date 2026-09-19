"""Locate API — serves the video's extracted facts to Rene's front end.

    ../.venv-tts/bin/python serve_locates.py ~/Downloads/locates.geojson [--port 8787]

Endpoints (all CORS-open, GET):
    /api/health                  liveness + counts
    /api/locates                 GeoJSON FeatureCollection, every detection
    /api/locates?color=orange    filter by APWA colour
    /api/locates?since=120       filter by video timestamp (seconds)
    /api/summary                 tallies by colour and utility class, plus provenance
    /api/stage2                  the proposed Stage 2 production record, ready to POST
    /api/frames/<t>.jpg          the marked frame at that second
    /                            the Leaflet map
"""
import json, os, sys, argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

STATE = {}

UTILITY = {
    "orange": "communications / fibre", "red": "electric", "yellow": "gas, oil, steam",
    "green": "sewer, drain", "blue": "potable water", "pink": "temporary survey",
    "purple": "reclaimed water",
}


class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *a):
        print(f"  {self.address_string()} {fmt % a}")

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, indent=1).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, b"")

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        feats = STATE["geo"]["features"]

        if u.path in ("/api/health", "/health"):
            return self._send(200, {
                "ok": True, "detections": len(feats),
                "video": STATE["video"], "duration_s": STATE["duration"],
                "anchor": STATE["anchor"],
                "endpoints": ["/api/locates", "/api/summary", "/api/stage2",
                              "/api/frames/<t>.jpg", "/"],
            })

        if u.path == "/api/locates":
            out = feats
            if "color" in q:
                want = {c.lower() for c in q["color"]}
                out = [f for f in out if (f["properties"].get("primary") or "").lower() in want]
            if "since" in q:
                try:
                    t0 = float(q["since"][0])
                    out = [f for f in out if (f["properties"].get("t") or 0) >= t0]
                except ValueError:
                    pass
            if "until" in q:
                try:
                    t1 = float(q["until"][0])
                    out = [f for f in out if (f["properties"].get("t") or 0) <= t1]
                except ValueError:
                    pass
            return self._send(200, {"type": "FeatureCollection", "features": out})

        if u.path == "/api/summary":
            by_colour, by_util = {}, {}
            for f in feats:
                c = f["properties"].get("primary", "unknown")
                by_colour[c] = by_colour.get(c, 0) + 1
                uti = UTILITY.get(c, "unknown")
                by_util[uti] = by_util.get(uti, 0) + 1
            ts = [f["properties"].get("t") for f in feats if f["properties"].get("t") is not None]
            return self._send(200, {
                "video": STATE["video"], "duration_s": STATE["duration"],
                "detections": len(feats),
                "by_colour": by_colour, "by_utility": by_util,
                "first_s": min(ts) if ts else None, "last_s": max(ts) if ts else None,
                "anchor": STATE["anchor"],
                "provenance": {
                    "timestamps": "MEASURED — frame index / fps",
                    "colours": "MEASURED — HSV threshold against the APWA colour code",
                    "coordinates": "DERIVED — interpolated along the street axis from one GPS "
                                   "anchor in the clip metadata. Not surveyed.",
                },
            })

        if u.path == "/api/stage2":
            by_colour = {}
            for f in feats:
                c = f["properties"].get("primary", "unknown")
                by_colour[c] = by_colour.get(c, 0) + 1
            parts = ", ".join(f"{n} {c}" for c, n in sorted(by_colour.items(), key=lambda x: -x[1]))
            return self._send(200, {
                "stage": 2, "stageName": "Utility Locates",
                "status": "proposed",
                "quantity": len(feats), "unit": "each",
                "note": f"Detected from sidewalk video: {len(feats)} locate marks, {parts}. "
                        "Machine-proposed from video evidence — not confirmed.",
                "evidence": {
                    "kind": "video",
                    "source": STATE["video"],
                    "frames_endpoint": "/api/frames/<t>.jpg",
                    "geojson_endpoint": "/api/locates",
                },
                "requiresHumanDecision": True,
            })

        if u.path.startswith("/api/frames/"):
            name = os.path.basename(u.path)
            t = name.split(".")[0].lstrip("t")
            try:
                fn = os.path.join(STATE["framedir"], f"t{int(float(t)):04d}.jpg")
            except ValueError:
                return self._send(400, {"error": "bad timestamp"})
            if not os.path.exists(fn):
                return self._send(404, {"error": "no frame at that second",
                                        "have": sorted(os.listdir(STATE["framedir"]))[:12]})
            return self._send(200, open(fn, "rb").read(), "image/jpeg")

        if u.path in ("/", "/map", "/index.html"):
            mp = STATE["map"]
            if os.path.exists(mp):
                return self._send(200, open(mp, "rb").read(), "text/html; charset=utf-8")

        return self._send(404, {"error": "not found", "try": "/api/health"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("geojson", nargs="?", default=os.path.expanduser("~/Downloads/locates.geojson"))
    ap.add_argument("--port", type=int, default=8787)
    a = ap.parse_args()

    geo = json.load(open(a.geojson))
    d = os.path.dirname(os.path.abspath(a.geojson))
    feats = geo["features"]
    p0 = feats[0]["properties"] if feats else {}
    STATE.update({
        "geo": geo, "framedir": os.path.join(d, "frames"),
        "map": os.path.join(d, "locates_map.html"),
        "video": p0.get("source", "IMG_2104.MOV"),
        "duration": max((f["properties"].get("t") or 0) for f in feats) if feats else 0,
        "anchor": {"lat": p0.get("anchor_lat"), "lon": p0.get("anchor_lon"),
                   "accuracy_m": p0.get("anchor_accuracy_m"),
                   "note": "single GPS point from clip metadata; per-mark coordinates are derived"},
    })

    srv = ThreadingHTTPServer(("0.0.0.0", a.port), H)
    print(f"locate API on http://localhost:{a.port}")
    print(f"  {len(feats)} detections from {STATE['video']}")
    for e in ("/api/health", "/api/locates", "/api/summary", "/api/stage2", "/api/frames/14.jpg", "/"):
        print(f"    http://localhost:{a.port}{e}")
    srv.serve_forever()


if __name__ == "__main__":
    main()
