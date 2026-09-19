"""Ask Memories.ai to find the locates.

Uploads a video to the Video Datalake (API 2.0), waits for indexing, then runs
natural-language searches for utility locate paint and prints timestamped hits.

    export MEMORIES_API_KEY='sk-mai-...'        # console.memories.ai → API keys
    ../.venv-tts/bin/python memories_locates.py ~/Downloads/sidewalk.mov

Verified 19 Sep 2026 by three independent research agents that agreed, two of
them reading the vendor's own OpenAPI spec and SDK source:
  base   https://api.memories.ai/serve/datalake/v1   (docs.memories.ai/datalake/openapi.json)
  auth   Authorization: sk-mai-...   ← the RAW key, NO "Bearer" prefix
  key    sk-mai-   (sk-mavi- is the DEPRECATED API 1.0 — different product)

Writes memories_locates.json next to the video, shaped so bridge_to_api.py can
read it the same way it reads locates.geojson.
"""
import json, mimetypes, os, sys, time, uuid
import urllib.request

BASE = "https://api.memories.ai/serve/datalake/v1"

QUERIES = [
    "orange spray paint marking on the sidewalk pavement",
    "spray painted utility locate marks on the ground",
    "coloured paint lines and arrows on concrete",
    "utility markings indicating buried cables",
    "paint marks on the footpath surface",
    "coloured survey marks on the pavement",
]


def req(path, method="GET", body=None, files=None, key=None, timeout=90):
    url = BASE + path
    headers = {"Authorization": key, "X-Request-ID": "fig-" + uuid.uuid4().hex[:12]}
    data = None
    if files:
        boundary = "----fig" + uuid.uuid4().hex
        parts = []
        for name, value in (body or {}).items():
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n"
                         f"Content-Type: application/json\r\n\r\n{value}\r\n".encode())
        for name, path_ in files.items():
            fn = os.path.basename(path_)
            ctype = mimetypes.guess_type(fn)[0] or "video/mp4"
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"; "
                         f"filename=\"{fn}\"\r\nContent-Type: {ctype}\r\n\r\n".encode())
            parts.append(open(path_, "rb").read())
            parts.append(b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode())
        data = b"".join(parts)
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    elif body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"

    r = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"raw": raw[:500]}
    except Exception as e:
        return 0, {"error": str(e)}


def main():
    key = os.environ.get("MEMORIES_API_KEY", "").strip()
    if not key:
        sys.exit("set MEMORIES_API_KEY (get one at https://console.memories.ai → API keys)")
    if key.startswith("sk-mavi-"):
        print("!! that is an API 1.0 key (sk-mavi-). This script needs a Datalake 2.0 key (sk-mai-).")
    if len(sys.argv) < 2:
        sys.exit("usage: memories_locates.py <video>")
    video = os.path.abspath(sys.argv[1])
    if not os.path.exists(video):
        sys.exit(f"no such file: {video}")
    print(f"video: {os.path.basename(video)}  {os.path.getsize(video)/1e6:.1f} MB")

    # 1. collection -----------------------------------------------------------
    code, col = req("/collections", "POST", {"name": f"fig-locates-{uuid.uuid4().hex[:6]}"}, key=key)
    if code != 200 or not col.get("id"):
        sys.exit(f"collection failed ({code}): {json.dumps(col)[:400]}")
    cid = col["id"]
    print(f"collection {cid}")

    # 2. upload — multipart, json part + file part ----------------------------
    meta = {"collection_id": cid, "fps": 2.0,
            "metadata": {"title": os.path.basename(video), "tags": ["locates", "sidewalk"]}}
    print("uploading…")
    code, up = req("/videos", "POST", {"json": json.dumps(meta)}, files={"file": video}, key=key, timeout=600)
    if code not in (200, 202) or not up.get("video_id"):
        sys.exit(f"upload failed ({code}): {json.dumps(up)[:500]}")
    vid, op = up["video_id"], up.get("operation")
    print(f"video {vid}  operation {op}")

    # 3. poll — docs say trust `done` only ------------------------------------
    t0 = time.time()
    while op and time.time() - t0 < 600:
        time.sleep(5)
        code, o = req(f"/operations/{op}", key=key)
        if code != 200:
            print(f"  poll {code}: {json.dumps(o)[:200]}")
            continue
        pr = o.get("progress") or {}
        print(f"  {int(time.time()-t0):>3}s  done={o.get('done')}  {pr.get('percent', '?')}%  {pr}")
        if o.get("error"):
            sys.exit(f"ingest error: {json.dumps(o['error'])[:400]}")
        if o.get("done"):
            break
    else:
        print("  (no operation id or timed out — trying search anyway)")

    # 4. search ---------------------------------------------------------------
    hits, seen = [], set()
    for q in QUERIES:
        code, r = req("/search", "POST",
                      {"collection_id": cid, "query": q, "mode": "semantic",
                       "targets": ["caption", "frame"], "limit": 10}, key=key)
        if code != 200:
            print(f"  search {code} for {q!r}: {json.dumps(r)[:220]}")
            continue
        res = r.get("results") or []
        print(f"\n{q!r} → {len(res)} hit(s)")
        for h in res:
            ref, s, e = h.get("ref"), h.get("start"), h.get("end")
            print(f"   {str(s):>7}s–{str(e):<7}s  score={h.get('score')}  {str(h.get('snippet',''))[:88]}")
            if ref and ref not in seen:
                seen.add(ref)
                hits.append({"ref": ref, "start": s, "end": e, "score": h.get("score"),
                             "snippet": h.get("snippet"), "thumbnail": h.get("thumbnail"), "query": q})

    if not hits:
        print("\nNo hits. The model may not have the vocabulary for locate paint — "
              "that is a finding, not a failure. find_locates.py does it by colour.")

    # 5. one moment expanded, to show a frame ---------------------------------
    if hits:
        best = max(hits, key=lambda h: h.get("score") or 0)
        code, m = req(f"/moments/{best['ref']}?expand=caption,frame,clip", key=key)
        if code == 200:
            print(f"\nbest moment {best['ref']}:")
            print(json.dumps(m, indent=2)[:900])
            best["moment"] = m

    out = os.path.join(os.path.dirname(video), "memories_locates.json")
    json.dump({"collection": cid, "video": vid, "hits": hits}, open(out, "w"), indent=1)
    print(f"\n  {out}   ({len(hits)} distinct moments)")


if __name__ == "__main__":
    main()
