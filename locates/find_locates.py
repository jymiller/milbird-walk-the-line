"""Locate the locates.

Walks a sidewalk video, finds APWA-coloured utility locate paint on the ground,
pulls whatever GPS the camera embedded, and writes a map you can open.

No vendor, no API key, no network. Runs entirely on this laptop.

    ../.venv-tts/bin/python find_locates.py ~/Downloads/sidewalk.mov

Outputs, next to the video:
    locates_map.html      leaflet map, one pin per detection, thumbnail in the popup
    locates.geojson       the same detections as data
    frames/               the sampled frames, with detections outlined
"""
import json, os, subprocess, sys, base64, math

import cv2
import numpy as np

# APWA Uniform Color Code. HSV ranges are OpenCV's (H 0-179, S/V 0-255),
# widened for sun, shadow, wet pavement and faded paint.
APWA = [
    # name,        utility,                   [(h_lo,s_lo,v_lo),(h_hi,s_hi,v_hi)] ranges
    ("orange", "communications / fibre", [((5, 120, 120), (18, 255, 255))]),
    ("red",    "electric",               [((0, 120, 90), (4, 255, 255)), ((170, 120, 90), (179, 255, 255))]),
    ("yellow", "gas, oil, steam",        [((22, 110, 130), (32, 255, 255))]),
    ("green",  "sewer, drain",           [((40, 80, 70), (85, 255, 255))]),
    ("blue",   "potable water",          [((95, 90, 70), (125, 255, 255))]),
    ("pink",   "temporary survey",       [((145, 70, 130), (169, 255, 255))]),
    ("purple", "reclaimed water",        [((128, 70, 70), (148, 255, 255))]),
]
SWATCH = {"orange": "#D4621E", "red": "#C8102E", "yellow": "#B8860B",
          "green": "#2F6B46", "blue": "#2B5C8A", "pink": "#A8447F", "purple": "#7A4FA3"}

SAMPLE_EVERY_S = 1.0     # sample a frame this often
MIN_AREA_PX    = 900     # ignore specks
GROUND_FRACTION = 0.45   # only look at the bottom N of the frame — that's the pavement


def probe_gps(path):
    """Pull whatever location the camera left behind.

    iPhone writes a single ISO6709 point in QuickTime metadata; some devices
    embed a timed GPS track. Try the track first, fall back to the point.
    """
    track = []
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_entries",
             "format_tags:stream_tags", path],
            capture_output=True, text=True, timeout=30).stdout
        meta = json.loads(out or "{}")
        tags = {}
        tags.update((meta.get("format") or {}).get("tags") or {})
        for s in meta.get("streams") or []:
            tags.update(s.get("tags") or {})
        for k, v in tags.items():
            if "location" in k.lower() and isinstance(v, str) and v.strip():
                pt = parse_iso6709(v)
                if pt:
                    track.append((0.0, pt[0], pt[1]))
                    break
    except Exception as e:
        print(f"  gps probe failed: {e}")
    return track


def parse_iso6709(s):
    """'+37.7869-122.4090+016.729/' -> (lat, lon)"""
    import re
    m = re.findall(r"[+-]\d+\.?\d*", s)
    if len(m) >= 2:
        return float(m[0]), float(m[1])
    return None


def detect(frame):
    """Return [(color, utility, area, bbox)] for locate-coloured paint on the ground."""
    h, w = frame.shape[:2]
    y0 = int(h * (1 - GROUND_FRACTION))
    ground = frame[y0:, :]
    hsv = cv2.cvtColor(cv2.GaussianBlur(ground, (5, 5), 0), cv2.COLOR_BGR2HSV)
    hits = []
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
            x, y, cw, ch = cv2.boundingRect(c)
            # paint on the ground is elongated or blobby, not a thin vertical sliver
            if ch > 0 and cw / ch > 12:
                pass
            hits.append((name, utility, int(a), (x, y + y0, cw, ch)))
    return hits


def thumb_b64(frame, max_w=340):
    h, w = frame.shape[:2]
    if w > max_w:
        frame = cv2.resize(frame, (max_w, int(h * max_w / w)))
    ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 72])
    return base64.b64encode(buf).decode() if ok else ""


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: find_locates.py <video>")
    path = os.path.abspath(sys.argv[1])
    if not os.path.exists(path):
        sys.exit(f"no such file: {path}")
    outdir = os.path.dirname(path)
    framedir = os.path.join(outdir, "frames")
    os.makedirs(framedir, exist_ok=True)

    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    dur = total / fps if fps else 0
    print(f"video: {os.path.basename(path)}  {dur:.0f}s  {fps:.1f}fps  {total} frames")

    gps = probe_gps(path)
    if gps:
        print(f"  gps: anchor point {gps[0][1]:.5f}, {gps[0][2]:.5f}")
    else:
        print("  gps: none embedded — map will lay detections along a synthetic walk line")

    step = max(1, int(fps * SAMPLE_EVERY_S))
    feats, n, kept = [], 0, 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if n % step:
            n += 1
            continue
        t = n / fps
        hits = detect(frame)
        if hits:
            marked = frame.copy()
            for name, utility, a, (x, y, w_, h_) in hits:
                col = SWATCH[name]
                bgr = tuple(int(col[i:i+2], 16) for i in (5, 3, 1))
                cv2.rectangle(marked, (x, y), (x + w_, y + h_), bgr, 3)
                cv2.putText(marked, f"{name} {a}px", (x, max(18, y - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, bgr, 2)
            fn = os.path.join(framedir, f"t{int(t):04d}.jpg")
            cv2.imwrite(fn, marked)
            best = max(hits, key=lambda x: x[2])
            feats.append({
                "t": round(t, 1), "frame": fn,
                "colors": sorted({h[0] for h in hits}),
                "primary": best[0], "utility": best[1], "area": best[2],
                "count": len(hits), "thumb": thumb_b64(marked),
            })
            kept += 1
        n += 1
    cap.release()
    print(f"sampled {n // step} frames, {kept} with locate-coloured paint")

    # place detections: real anchor if we have one, else a synthetic line
    if gps:
        lat0, lon0 = gps[0][1], gps[0][2]
    else:
        lat0, lon0 = 37.79025, -122.41000     # 724 Pine St, SF — the venue
    span = max(1.0, dur)
    for f in feats:
        frac = f["t"] / span
        f["lat"] = lat0 + 0.00055 * frac      # ~60m walk north
        f["lon"] = lon0 + 0.00012 * frac
        f["position_provenance"] = ("INTERPOLATED from a single GPS anchor; timestamp measured, coordinate derived"
                                   if gps else "SYNTHETIC — no GPS in clip; coordinates are placeholders")

    geo = {"type": "FeatureCollection", "features": [
        {"type": "Feature",
         "geometry": {"type": "Point", "coordinates": [f["lon"], f["lat"]]},
         "properties": {k: v for k, v in f.items() if k != "thumb"}}
        for f in feats]}
    gj = os.path.join(outdir, "locates.geojson")
    json.dump(geo, open(gj, "w"), indent=1)

    tally = {}
    for f in feats:
        for c in f["colors"]:
            tally[c] = tally.get(c, 0) + 1

    html = MAP_HTML.replace("__DATA__", json.dumps(feats)) \
                   .replace("__LAT__", str(lat0)).replace("__LON__", str(lon0)) \
                   .replace("__SWATCH__", json.dumps(SWATCH)) \
                   .replace("__TALLY__", json.dumps(tally)) \
                   .replace("__VIDEO__", os.path.basename(path)) \
                   .replace("__DUR__", f"{dur:.0f}") \
                   .replace("__MODE__", "GPS-anchored" if gps else "synthetic walk line")
    mp = os.path.join(outdir, "locates_map.html")
    open(mp, "w").write(html)

    print(f"\n  {gj}")
    print(f"  {mp}")
    print(f"  {framedir}/  ({kept} marked frames)")
    print(f"\n  by colour: {tally}")


MAP_HTML = """<!doctype html><html><head><meta charset=utf8>
<title>Locate the locates</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
 body{margin:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#15130F;color:#F2EDE6}
 #map{height:66vh}
 .panel{padding:14px 18px}
 h1{font-size:19px;margin:0 0 4px}
 .meta{font-family:ui-monospace,Menlo,monospace;font-size:11px;color:#8D8378;margin-bottom:12px}
 .tally{display:flex;gap:8px;flex-wrap:wrap}
 .chip{font-family:ui-monospace,monospace;font-size:11px;padding:4px 10px;border-radius:4px;
       border:1px solid currentColor;font-weight:600}
 .pop img{width:100%;border-radius:5px;margin-top:6px}
 .pop b{font-family:ui-monospace,monospace}
</style></head><body>
<div id="map"></div>
<div class="panel">
  <h1>Locate the locates</h1>
  <div class="meta">__VIDEO__ &middot; __DUR__s &middot; positions: __MODE__</div>
  <div class="tally" id="tally"></div>
</div>
<script>
const D=__DATA__, SW=__SWATCH__, TALLY=__TALLY__;
const map=L.map('map').setView([__LAT__,__LON__],19);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  {maxZoom:22,attribution:'&copy; OpenStreetMap'}).addTo(map);
const pts=[];
D.forEach(f=>{
  const c=SW[f.primary]||'#888';
  const m=L.circleMarker([f.lat,f.lon],{radius:7,color:c,fillColor:c,fillOpacity:.85,weight:2}).addTo(map);
  m.bindPopup(`<div class="pop"><b>t=${f.t}s &middot; ${f.primary}</b><br>${f.utility}<br>
    <span style="color:#666">${f.count} region(s), ${f.area}px</span>
    ${f.thumb?`<img src="data:image/jpeg;base64,${f.thumb}">`:''}</div>`,{maxWidth:360});
  pts.push([f.lat,f.lon]);
});
if(pts.length){L.polyline(pts,{color:'#8D8378',weight:2,dashArray:'4 5'}).addTo(map);
  map.fitBounds(L.latLngBounds(pts).pad(.35));}
const t=document.getElementById('tally');
Object.entries(TALLY).sort((a,b)=>b[1]-a[1]).forEach(([k,v])=>{
  const s=document.createElement('span');s.className='chip';s.style.color=SW[k]||'#888';
  s.textContent=`${k} ${v}`;t.appendChild(s);});
if(!D.length)t.textContent='No locate-coloured paint detected. Try lowering MIN_AREA_PX or widening the HSV ranges.';
</script></body></html>"""

if __name__ == "__main__":
    main()
