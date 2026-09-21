"""Measured, not made up.

One photograph, its own EXIF fix, and the same fix on the plan. The point is not
that the dot is pretty — it is that the dot came off the camera rather than out
of an estimate, and that the two sit in different columns for a reason.
"""
import base64, json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.dirname(HERE)

SUBJECT = "IMG_2118"          # yellow GAS lettering with a red arrow beside it

G = dict(pine=37.791201, california=37.792024, joice=-122.408310, stockton=-122.407585)
CLAT = (G["pine"] + G["california"]) / 2
CLON = (G["joice"] + G["stockton"]) / 2
MPD_LAT = 111320.0
MPD_LON = 111320.0 * math.cos(CLAT * math.pi / 180)

PW, PH = 420, 300              # the plan panel
VIEW_W, VIEW_H = 190.0, 136.0
LAT_N = CLAT + (VIEW_H / 2) / MPD_LAT
LON_W = CLON - (VIEW_W / 2) / MPD_LON
X = lambda lon: round((lon - LON_W) * MPD_LON * (PW / VIEW_W), 1)
Y = lambda lat: round((LAT_N - lat) * MPD_LAT * (PH / VIEW_H), 1)

TOK = {"orange": "--comms", "yellow": "--gas", "blue": "--water", "green": "--sewer",
       "red": "--elec", "white": "--ink"}


def build():
    truth = json.load(open(f"{S}/photos/truth.json"))
    pos = [r for r in truth if r["verdict"] == "locate"]
    subj = next(r for r in pos if r["id"] == SUBJECT)

    img = base64.b64encode(open(f"{S}/photos/small/{SUBJECT}.jpg", "rb").read()).decode()

    osm = json.load(open(f"{S}/map/osm.json"))["elements"]
    def vis(g):
        return any(-40 <= X(p["lon"]) <= PW + 40 and -40 <= Y(p["lat"]) <= PH + 40 for p in g)
    def path(g):
        return "M" + " L".join(f"{X(p['lon'])},{Y(p['lat'])}" for p in g) + "Z"
    blds = [path(e["geometry"]) for e in osm
            if "building" in e.get("tags", {}) and e.get("geometry") and vis(e["geometry"])]
    RW = {"secondary": 15.0, "tertiary": 13.0, "residential": 9.0, "service": 5.0}
    roads = sorted(
        ((RW[e["tags"]["highway"]] * (PW / VIEW_W),
          "M" + " L".join(f"{X(p['lon'])},{Y(p['lat'])}" for p in e["geometry"]))
         for e in osm
         if e.get("geometry") and e.get("tags", {}).get("highway") in RW and vis(e["geometry"])),
        key=lambda r: -r[0])

    others = "".join(
        f'<circle cx="{X(r["lon"])}" cy="{Y(r["lat"])}" r="4" '
        f'fill="var({TOK.get((r["colours"] or ["red"])[0], "--muted")})" opacity=".45"/>'
        for r in pos if r["id"] != SUBJECT)

    sx, sy = X(subj["lon"]), Y(subj["lat"])

    return f'''<figure class="pinfig">
  <div class="pinrow">

    <div class="pinshot">
      <img src="data:image/jpeg;base64,{img}" alt="{subj["note"]}">
      <span class="pinmark" aria-hidden="true"></span>
      <figcaption class="pincap"><b>{SUBJECT}</b> &middot; {subj["lat"]:.6f}, {subj["lon"]:.6f}
        <span class="tag meas">measured &mdash; EXIF, off the camera</span></figcaption>
    </div>

    <div class="pinlink" aria-hidden="true">
      <svg viewBox="0 0 90 60"><path d="M4,30 H72" class="ln"/><path d="M72,30 l-14,-8 v16 z" class="hd"/></svg>
    </div>

    <div class="pinplan">
      <svg viewBox="0 0 {PW} {PH}" role="img"
        aria-label="The same photograph's position on the plan of the block, with the other confirmed readings shown faintly.">
        <rect width="{PW}" height="{PH}" fill="var(--paper)"/>
        {"".join(f'<path d="{d}" stroke="var(--surface)" stroke-width="{w:.0f}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' for w, d in roads)}
        <g fill="var(--sunk)" stroke="var(--line)" stroke-width=".7" opacity=".7">
          {"".join(f'<path d="{d}"/>' for d in blds)}
        </g>
        {others}
        <circle cx="{sx}" cy="{sy}" r="13" class="halo"/>
        <circle cx="{sx}" cy="{sy}" r="6.5" fill="var(--gas)" stroke="var(--paper)" stroke-width="2"/>
      </svg>
      <figcaption class="pincap">the same fix, on the block
        <span class="tag meas">measured</span></figcaption>
    </div>

  </div>
  <figcaption class="cap2">The dot did not come from an estimate. It came off the camera.
  <b>Everything on the video layer is derived instead</b> &mdash; walked along the block at the filmed
  pace from a single anchor, good to about seven metres. Useful for finding your way back to a mark.
  <b>Not a survey, and never drawn as one.</b></figcaption>
</figure>'''


CSS = '''
/* ---- measured, not made up ---- */
.pinfig{margin:clamp(12px,2vh,22px) 0 6px}
.pinrow{display:grid;grid-template-columns:minmax(0,1fr) 74px minmax(0,1fr);
  gap:clamp(8px,1.4vw,20px);align-items:center}
.pinshot,.pinplan{position:relative;min-width:0}
.pinshot img{display:block;width:100%;aspect-ratio:4/3;object-fit:cover;
  border:1px solid var(--line-strong);background:var(--paper)}
.pinplan svg{display:block;width:100%;height:auto;aspect-ratio:4/3;
  border:1px solid var(--line-strong);background:var(--paper)}
.pinshot{position:relative}
.pinshot .pinmark{position:absolute;left:52%;top:64%;width:34px;height:34px;margin:-17px 0 0 -17px;
  border:2.4px solid var(--gas);border-radius:50%;pointer-events:none}
.pinshot .pinmark::before,.pinshot .pinmark::after{content:"";position:absolute;background:var(--gas)}
.pinshot .pinmark::before{left:50%;top:-13px;width:2px;height:60px;margin-left:-1px;opacity:.85}
.pinshot .pinmark::after{top:50%;left:-13px;height:2px;width:60px;margin-top:-1px;opacity:.85}
.pinplan .halo{fill:var(--gas);opacity:.22}
.pinlink svg{display:block;width:100%;height:auto}
.pinlink .ln{stroke:var(--ink-2);stroke-width:2.4;fill:none;stroke-dasharray:7 6}
.pinlink .hd{fill:var(--ink-2)}
.pincap{font-family:var(--mono);font-size:11px;line-height:1.5;color:var(--muted);
  margin-top:7px;display:flex;flex-wrap:wrap;gap:6px;align-items:baseline}
.pincap b{color:var(--ink-2)}
.pincap .tag{padding:2px 7px;border-radius:2px;font-size:10px;letter-spacing:.08em;
  text-transform:uppercase;font-weight:600;margin-left:0}
.pincap .tag.meas{background:var(--sewer-soft);color:var(--sewer)}
@media (max-width:820px){
  .pinrow{grid-template-columns:1fr;gap:14px}
  .pinlink{transform:rotate(90deg);width:74px;margin:0 auto}
}
'''

if __name__ == "__main__":
    open(f"{HERE}/pin.html", "w").write(build())
    open(f"{HERE}/pin.css", "w").write(CSS)
    print(f"pin.html {os.path.getsize(HERE+'/pin.html')/1024:.0f} KB · subject {SUBJECT}")
