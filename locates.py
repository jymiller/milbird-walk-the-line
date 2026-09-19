#!/usr/bin/env python3
# locates.py - upload a sidewalk video to Memories.ai, wait for indexing, hunt for
# spray-painted utility locates. Stdlib only, no pip install.
#   export MEMORIES_API_KEY='sk-mai-...'; python3 locates.py /abs/path/sidewalk.mp4
# Endpoint sources (nothing invented): OpenAPI docs.memories.ai/datalake/openapi.json
# (DataLake API 2.0, 2026-08) + official client Memories-ai-labs/Internet2EgoExo
# src/video_searching_agent/api/memories_datalake_client.py + docs.memories.ai/authentication
import json, os, sys, time, uuid, urllib.error, urllib.parse, urllib.request

BASE = os.environ.get("MEMORIES_BASE", "https://api.memories.ai/serve/datalake/v1").rstrip("/")
KEY = os.environ.get("MEMORIES_API_KEY", "").strip()
FPS = float(os.environ.get("MEMORIES_FPS", "2.0"))
BUDGET = int(os.environ.get("MEMORIES_TIMEOUT_S", "1200"))
OUT = os.path.abspath(os.environ.get("MEMORIES_OUT", "./locates_out"))
CRLF = bytes([13, 10])
# ONE AUTH SWITCH: docs + OpenAPI say RAW key; the live 401 text says Bearer.
# Try raw, auto-flip once on 401. MEMORIES_AUTH_STYLE=raw|bearer to force.
PFX = "Bearer " if os.environ.get("MEMORIES_AUTH_STYLE") == "bearer" else ""
FLIPPED = False
BOTH = ["caption", "frame_embedding"]  # frame_embedding bypasses caption vocabulary
QUERIES = [
    ("A any paint", "colored spray paint markings on the concrete sidewalk"),
    ("B ORANGE=fiber", "orange spray paint line on the sidewalk pavement"),
    ("C RED=electric", "red spray painted line crossing the sidewalk toward a building"),
    ("D YELLOW=gas", "yellow spray painted dashes on the pavement near the curb"),
    ("E BLUE=water", "blue paint line running along the sidewalk"),
    ("F WHITE=dig box", "white painted outline or rectangle on the sidewalk"),
    ("G arrows", "arrow spray painted on the pavement pointing sideways"),
    ("H handwriting", "handwritten letters or numbers spray painted on the ground"),
    ("I multi-color", "several different colors of spray paint in the same spot on the ground"),
    ("J flags", "small colored flags on wire stems stuck in the grass beside the sidewalk"),
]
WORDS = ["paint", "spray", "marking", "orange", "red", "yellow", "blue", "green",
         "pink", "purple", "white", "arrow", "stripe", "graffiti", "chalk"]
log = lambda m: print(m, flush=True)


def die(m):
    log("FATAL: " + m)
    sys.exit(1)


def send(req, tmo):
    try:
        with urllib.request.urlopen(req, timeout=tmo) as r:
            raw, st = r.read(), r.status
    except urllib.error.HTTPError as e:
        raw, st = e.read(), e.code
    except Exception as e:
        return 0, None, "TRANSPORT ERROR: %r" % (e,)
    txt = raw.decode("utf-8", "replace")
    try:
        return st, json.loads(txt), txt
    except ValueError:
        return st, None, txt


def api(m, path, body=None, params=None, tmo=120, retry=True):
    global PFX, FLIPPED
    url = BASE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    hd = {"Authorization": PFX + KEY, "X-Request-ID": "req_" + uuid.uuid4().hex[:24]}
    data = None
    if body is not None:
        data, hd["Content-Type"] = json.dumps(body).encode(), "application/json"
    st, p, txt = send(urllib.request.Request(url, data=data, headers=hd, method=m), tmo)
    if st in (429, 503) and retry:
        log("  throttled, sleeping 10s")
        time.sleep(10)
        return api(m, path, body, params, tmo, False)
    if st == 401 and retry and not FLIPPED and not PFX:
        FLIPPED, PFX = True, "Bearer "
        log("  [auth] 401 on raw key - retrying once with a Bearer prefix")
        return api(m, path, body, params, tmo, False)
    return st, p, txt


def show(label, st, p, txt, keys=None):
    """Defensive: print the raw body whenever the shape is not what we expect."""
    if not 200 <= st < 300:
        log("  !! %s -> HTTP %s raw: %s" % (label, st, txt[:600]))
        return False
    if p is None or (keys and isinstance(p, dict) and not any(k in p for k in keys)):
        log("  ?? %s -> HTTP %s unexpected shape, raw: %s" % (label, st, txt[:600]))
    return True


def upload(path, fields):
    """POST /videos multipart (OpenAPI: upload_video). Part shape from the official
    client: json part = JSON string with no filename, file part = octet-stream.
    We set the boundary ourselves; never send a bare multipart Content-Type."""
    b = "----mai" + uuid.uuid4().hex
    with open(path, "rb") as fh:
        blob = fh.read()
    body = b"".join([("--" + b).encode(), CRLF,
                     b'Content-Disposition: form-data; name="json"', CRLF,
                     b"Content-Type: application/json", CRLF, CRLF,
                     json.dumps(fields).encode(), CRLF, ("--" + b).encode(), CRLF,
                     ('Content-Disposition: form-data; name="file"; filename="%s"'
                      % os.path.basename(path)).encode(), CRLF,
                     b"Content-Type: application/octet-stream", CRLF, CRLF,
                     blob, CRLF, ("--" + b + "--").encode(), CRLF])
    hd = {"Authorization": PFX + KEY,
          "Content-Type": "multipart/form-data; boundary=" + b}
    return send(urllib.request.Request(BASE + "/videos", data=body, headers=hd,
                                       method="POST"), 900)


def main():
    if len(sys.argv) < 2:
        die("usage: python3 locates.py /abs/path/sidewalk.mp4")
    vp = os.path.abspath(sys.argv[1])
    if not os.path.isfile(vp):
        die("no such file: " + vp)
    if not KEY:
        die("MEMORIES_API_KEY not set")
    if not KEY.startswith("sk-mai-"):
        log("WARNING: key is not sk-mai-; sk-mavi- is the deprecated API 1.0")
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()

    # 0. GET /usage/balance (OpenAPI: get_balance). Free. Proves the key and
    #    settles raw-vs-Bearer before spending anything.
    log("[0] preflight")
    st, p, raw = api("GET", "/usage/balance")
    if st == 401:
        die("401 with BOTH header styles - bad/expired key. raw: " + raw[:300])
    show("balance", st, p, raw, ["balance_usd"])
    log("  balance=%s  auth=%s" % (json.dumps(p)[:120], "Bearer" if PFX else "raw"))
    if isinstance((p or {}).get("balance_usd"), (int, float)) and p["balance_usd"] <= 0:
        die("balance <= 0; top up at https://console.memories.ai/stripe")

    # 1. POST /collections (OpenAPI: create_collection). Free. No detectors, no
    #    face recognition - we are filming pavement on a public sidewalk.
    col = os.environ.get("MEMORIES_COLLECTION_ID", "").strip()
    if not col:
        st, p, raw = api("POST", "/collections", {"name": "sidewalk-locates"})
        if not show("create collection", st, p, raw, ["id"]):
            die("collection create failed")
        col = (p or {}).get("id")
        if not col:
            die("no collection id: " + raw[:300])
    log("[1] collection " + col)

    # 2. POST /videos multipart (OpenAPI: upload_video). $0.05/video-minute at
    #    fps 1.0, ~linear in fps: 3 min at fps 2.0 is about $0.30.
    mb = os.path.getsize(vp) / 1e6
    log("[2] uploading %s (%.1f MB, fps=%s)" % (os.path.basename(vp), mb, FPS))
    if mb > 100:
        log("  >100MB: if this stalls, ffmpeg -i IN.mp4 -vf scale=-2:1080 "
            "-c:v libx264 -crf 26 -an OUT.mp4 and rerun")
    st, p, raw = upload(vp, {"collection_id": col, "fps": FPS,
                             "metadata": {"title": os.path.basename(vp),
                                          "tags": ["locates", "sidewalk"]},
                             "idempotency_key": "locates-" + os.path.basename(vp)[:80]})
    # docs say 202, the OpenAPI example says 200: accept any 2xx, drive off the
    # returned operation handle rather than the status code.
    if not show("upload", st, p, raw, ["video_id"]):
        die("upload failed (402=no balance, 415=bad container, 413=too big)")
    vid, op = (p or {}).get("video_id"), (p or {}).get("operation")
    if not vid:
        die("no video_id: " + raw[:400])
    log("  video_id=%s operation=%s" % (vid, op))

    # 3. GET /operations/{id} (OpenAPI: get_operation). Free. Docs: "Only trust
    #    done." A non-null error is a failure even when done is true.
    log("[3] indexing, polling 5s, budget %ds" % BUDGET)
    end, done, last = time.time() + BUDGET, False, ""
    while time.time() < end:
        st, p, raw = api("GET", "/operations/" + op) if op else (0, None, "")
        if op and st == 200 and isinstance(p, dict):
            pr = p.get("progress") or {}
            line = "done=%s %s pct=%s" % (p.get("done"), pr.get("index"), pr.get("percent"))
            if line != last:
                log("  %4ds %s" % (time.time() - t0, line))
                last = line
            if p.get("error"):
                die("indexing FAILED: " + json.dumps(p["error"])[:400])
            if p.get("done") is True:
                done = True
                break
        else:
            if op:
                log("  ?? operation poll HTTP %s: %s" % (st, raw[:200]))
                op = None
            st, p, raw = api("GET", "/videos/" + vid)   # OpenAPI: get_video. Free.
            sv = (p or {}).get("status") if isinstance(p, dict) else None
            log("  %4ds video status=%s" % (time.time() - t0, sv))
            if sv == "ready":
                done = True
                break
            if sv == "failed":
                die("video failed: " + raw[:400])
        time.sleep(5)
    if not done:
        die("timed out. Nothing lost - resume with MEMORIES_COLLECTION_ID=%s and "
            "video %s" % (col, vid))
    log("  indexed in %ds" % (time.time() - t0))

    # 4. GET /videos/{id}/summary and /caption (OpenAPI: get_summary, get_caption).
    #    $0.001 each. THE reality check: if the captioner never says paint, no
    #    amount of query tuning on target=caption will help.
    for ep in ("summary", "caption"):
        st, p, raw = api("GET", "/videos/%s/%s" % (vid, ep), tmo=180)
        if st == 409:
            log("  409 not ready, waiting 20s")
            time.sleep(20)
            st, p, raw = api("GET", "/videos/%s/%s" % (vid, ep), tmo=180)
        show(ep, st, p, raw)
        if ep == "summary":
            log("[4] SUMMARY: " + raw[:1200])
        else:
            segs = (p or {}).get("segments") or [] if isinstance(p, dict) else []
            joined = " ".join(s.get("text", "") for s in segs if isinstance(s, dict))
            text = ((p or {}).get("aggregated") if isinstance(p, dict) else raw) or joined
            with open(os.path.join(OUT, "captions.txt"), "w") as f:
                f.write(text or raw)
            found = sorted(set(w for w in WORDS if w in (text or "").lower()))
            log("  captions: %d segments, %d chars -> %s/captions.txt"
                % (len(segs), len(text or ""), OUT))
            log("  VOCABULARY CHECK -> " + (", ".join(found) or "NOTHING relevant; "
                "caption search will be useless, rely on frame_embedding"))
            for s in segs:
                t = (s.get("text") or "") if isinstance(s, dict) else ""
                if any(w in t.lower() for w in ("paint", "spray", "marking", "chalk")):
                    log("    [%s-%s] %s" % (s.get("start"), s.get("end"), t[:180]))

    # 5. POST /search (OpenAPI: search). $0.008/call, 5 QPS. collection_id AND
    #    targets are BOTH required by the spec - always send targets explicitly.
    log("[5] %d searches at $0.008 each" % len(QUERIES))
    hits = []
    for label, q in QUERIES:
        st, p, raw = api("POST", "/search", {"collection_id": col, "query": q,
                                             "mode": "semantic", "targets": BOTH,
                                             "top_k": 25, "group_by": "moment"})
        log("  --- %s : %s" % (label, q))
        if not show("search", st, p, raw, ["results"]):
            time.sleep(0.3)
            continue
        res = (p or {}).get("results")
        if not isinstance(res, list):
            log("      ?? no results list, raw: " + raw[:300])
            time.sleep(0.3)
            continue
        if not res:
            log("      (no hits) hint=%r" % ((p or {}).get("hint"),))
        for r in res[:8]:
            if not isinstance(r, dict):
                log("      ?? odd item %r" % (r,))
                continue
            log("      %7.2fs-%7.2fs score=%s target=%s %s" % (
                float(r.get("start") or 0), float(r.get("end") or 0), r.get("score"),
                r.get("target"), (r.get("snippet") or "")[:80]))
            log("        ref=%s thumb=%s" % (r.get("ref"), (r.get("thumbnail_url") or "-")[:110]))
            hits.append(r)
        time.sleep(0.3)

    # 6. GET /videos/{id}/frame?t= (OpenAPI: get_frame). $0.001, 8x cheaper than
    #    /moments/{ref}. The API returns NO bounding boxes anywhere, so the actual
    #    color/shape call happens on these frames - by you or by a vision model.
    log("[6] frames for the top distinct moments - eyeball these")
    def sc(h):
        try:
            return -float(h.get("score") or 0)
        except (TypeError, ValueError):
            return 0.0
    seen, out = set(), []
    for h in sorted(hits, key=sc):
        t = round(float(h.get("start") or 0))
        if t in seen:
            continue
        seen.add(t)
        st, p, raw = api("GET", "/videos/%s/frame" % vid, {"t": t})
        u = (p or {}).get("url") if isinstance(p, dict) else None
        log("  t=%-6s %s" % (t, u or ("?? HTTP %s %s" % (st, raw[:150]))))
        if u:
            out.append({"t": t, "url": u})
        if len(out) >= 8:
            break
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"collection_id": col, "video_id": vid, "hits": hits,
                   "frames": out}, f, indent=2, default=str)
    log("DONE in %ds. video=%s collection=%s. Report: %s/report.json"
        % (time.time() - t0, vid, col, OUT))


if __name__ == "__main__":
    main()
