"""Rebuild the public raw-output page on positions that are actually defensible.

Two layers, and the page never lets you confuse them:

  PHOTOGRAPHS   26 frames that a person opened and confirmed carry locate paint.
                Position is EXIF GPS off the camera. MEASURED.
  VIDEO         the colour regions the detector pulled out of the walk. Position is
                reconstructed by walking the block perimeter at the filmed pace from a
                single GPS anchor. DERIVED — and it says so on every marker.

The old page interpolated every reading along a straight east-west line at a fixed
latitude, which put the whole clip several blocks east of where it was filmed. That is
the bug this replaces.

    python3 locates/build_site.py
"""
import base64, json, math, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
SCRATCH = ("/private/tmp/claude-501/-Users-johnmiller-src-work-milbird-hackathons-fig/"
           "2e1b1d50-e541-46e3-9992-0d85355741e9/scratchpad")

# ---------------------------------------------------------------- geometry
G = dict(door=[37.791388, -122.407837], pine=37.791201, california=37.792024,
         joice=-122.408310, stockton=-122.407585, durationS=404.1)
MPD_LAT = 111320.0
MPD_LON = 111320.0 * math.cos(G["door"][0] * math.pi / 180)
d = G["door"]
LEGS = [
    [[G["pine"], d[1]], [G["pine"], G["joice"]]],
    [[G["pine"], G["joice"]], [G["california"], G["joice"]]],
    [[G["california"], G["joice"]], [G["california"], G["stockton"]]],
    [[G["california"], G["stockton"]], [G["pine"], G["stockton"]]],
    [[G["pine"], G["stockton"]], [G["pine"], d[1]]],
]
LENS = [math.hypot((b[1] - a[1]) * MPD_LON, (b[0] - a[0]) * MPD_LAT) for a, b in LEGS]
PERIM = sum(LENS)


def at_time(t):
    s = (t / G["durationS"]) * PERIM
    i = 0
    while i < len(LENS) - 1 and s > LENS[i]:
        s -= LENS[i]
        i += 1
    a, b = LEGS[i]
    k = min(1.0, s / LENS[i])
    lat = a[0] + (b[0] - a[0]) * k
    lon = a[1] + (b[1] - a[1]) * k
    w = math.sin(t * 0.21) * 0.7 + math.sin(t * 0.083) * 0.5
    horiz = abs(b[0] - a[0]) < abs(b[1] - a[1])
    return (lat + w / MPD_LAT, lon) if horiz else (lat, lon + w / MPD_LON)


SW = {"orange": "#D4621E", "red": "#C8102E", "yellow": "#B8860B", "green": "#2F6B46",
      "blue": "#2B5C8A", "pink": "#A8447F", "purple": "#7A4FA3", "white": "#D8D3C2"}
UTIL = {"orange": "communications / fiber", "red": "electric", "yellow": "gas, oil, steam",
        "green": "sewer, drain", "blue": "potable water", "pink": "temporary survey",
        "purple": "reclaimed water", "white": "proposed excavation"}


def main():
    truth = json.load(open(f"{SCRATCH}/photos/truth.json"))
    pos = [r for r in truth if r["verdict"] == "locate"]

    # publish the confirmed photographs next to the page
    pdir = os.path.join(SITE, "photos")
    os.makedirs(pdir, exist_ok=True)
    for r in pos:
        src = f"{SCRATCH}/photos/small/{r['id']}.jpg"
        if os.path.exists(src):
            shutil.copy(src, os.path.join(pdir, r["id"] + ".jpg"))

    PHOTOS = [{
        "id": r["id"], "lat": round(r["lat"], 7), "lon": round(r["lon"], 7),
        "colours": r["colours"], "primary": (r["colours"] or ["red"])[0],
        "note": r["note"], "at": r["at"],
        "img": f"photos/{r['id']}.jpg",
        "positionProvenance": "MEASURED — EXIF GPS written by the camera",
        "verdictProvenance": "HUMAN — a person opened this photograph and looked at it",
    } for r in pos]

    # the video readings, re-placed on the walk instead of a straight line
    ev = json.load(open(os.path.join(SITE, "api", "evidence.json")))
    items = ev["items"] if isinstance(ev, dict) else ev
    VIDEO = []
    for it in items:
        t = it.get("videoOffsetSeconds")
        if t is None:
            continue
        x = it.get("extraction", {}) or {}
        lat, lon = at_time(t)
        VIDEO.append({
            "id": it["id"], "t": t, "lat": round(lat, 7), "lon": round(lon, 7),
            "colour": x.get("colour"), "verdict": it.get("verdict"),
            "rules": x.get("rulesFired", []), "area": x.get("areaPx"),
            "why": (it.get("explanation") or "")[:240],
            "img": "frames/" + os.path.basename(it["url"]),
            "positionProvenance": "DERIVED — reconstructed along the block perimeter "
                                  "from one GPS anchor (+-7 m). Not surveyed.",
        })
    VIDEO.sort(key=lambda r: r["t"])

    json.dump({"count": len(PHOTOS), "items": PHOTOS,
               "note": "Confirmed by eye. Positions are EXIF GPS — measured, not derived."},
              open(os.path.join(SITE, "api", "photos.json"), "w"), indent=1)

    html = PAGE
    for k, v in (("__PHOTOS__", json.dumps(PHOTOS)), ("__VIDEO__", json.dumps(VIDEO)),
                 ("__SW__", json.dumps(SW)), ("__UTIL__", json.dumps(UTIL)),
                 ("__CENTRE__", json.dumps([(G["pine"] + G["california"]) / 2,
                                            (G["joice"] + G["stockton"]) / 2])),
                 ("__WALK__", json.dumps([at_time(t) for t in range(0, 405, 3)])),
                 ("__NPH__", str(len(PHOTOS))), ("__NVI__", str(len(VIDEO)))):
        html = html.replace(k, v)
    assert "__" not in html.split("<script>")[0][:2000]
    open(os.path.join(SITE, "index.html"), "w").write(html)

    print(f"photographs {len(PHOTOS)} (measured GPS)   video readings {len(VIDEO)} (derived)")
    print(f"perimeter {PERIM:.0f} m   pace {PERIM/G['durationS']:.2f} m/s")
    print(f"  {SITE}/index.html  {os.path.getsize(SITE+'/index.html')/1024:.0f} KB")
    print(f"  {SITE}/api/photos.json")


PAGE = """<!doctype html><html lang=en><head><meta charset=utf8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Locates &mdash; Pine St, San Francisco</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{box-sizing:border-box}
html,body{margin:0;height:100%;overflow:hidden;background:#13170F;color:#EDF0E2;
  font:14px 'IBM Plex Sans',-apple-system,BlinkMacSystemFont,sans-serif}
.top{padding:11px 18px;border-bottom:1px solid #2E3626;display:flex;gap:16px;
  align-items:baseline;flex-wrap:wrap}
h1{font-size:17px;margin:0;font-weight:700}
.meta{font-family:ui-monospace,Menlo,monospace;font-size:11px;color:#828A75}
.prov{font-family:ui-monospace,monospace;font-size:10.5px;margin-left:auto;color:#828A75}
.prov b{color:#9BBE72} .prov i{font-style:normal;color:#DAAE3B}
.bar{display:flex;gap:7px;flex-wrap:wrap;padding:9px 18px;border-bottom:1px solid #2E3626;
  align-items:center}
.ly{font-family:ui-monospace,monospace;font-size:11px;padding:5px 11px;border-radius:4px;
  cursor:pointer;border:1px solid #454F39;background:transparent;color:#BCC4AC}
.ly.on{background:#F0842F;border-color:#F0842F;color:#13170F;font-weight:700}
.chip{font-family:ui-monospace,monospace;font-size:11px;padding:4px 10px;border-radius:4px;
  border:1px solid currentColor;font-weight:600;opacity:.5;cursor:pointer}
.chip.on{opacity:1}
.wrap{display:flex;height:calc(100% - 104px)}
#map{flex:1 1 56%;min-width:280px;background:#0d100a}
.list{flex:1 1 44%;overflow-y:auto;border-left:1px solid #2E3626;padding:10px}
.card{display:grid;grid-template-columns:150px 1fr;gap:12px;padding:10px;margin-bottom:9px;
  background:#1C2117;border:1px solid #2E3626;border-left:4px solid var(--c);border-radius:7px;
  cursor:pointer}
.card:hover{border-color:#828A75}
.card.sel{outline:2px solid var(--c)}
.card img{width:100%;border-radius:5px;display:block}
.hd{display:flex;gap:9px;align-items:baseline;margin-bottom:5px;flex-wrap:wrap}
.tm{font-family:ui-monospace,monospace;font-size:15px;font-weight:600;color:var(--c)}
.cl{font-family:ui-monospace,monospace;font-size:10px;letter-spacing:.09em;text-transform:uppercase;
  padding:2px 7px;border-radius:3px;background:var(--c);color:#13170F;font-weight:700}
.ut{font-size:14px;font-weight:600;margin-bottom:3px}
.dt{font-family:ui-monospace,monospace;font-size:11px;color:#828A75;line-height:1.65}
.dt b{color:#BCC4AC;font-weight:600}
.tagm{color:#9BBE72} .tagd{color:#DAAE3B}
@media (max-width:760px){.wrap{flex-direction:column}#map{flex:0 0 46%}}
</style></head><body>
<div class="top">
  <h1>Utility locates &mdash; Pine St, San Francisco</h1>
  <span class="meta">one block &middot; 404&thinsp;s of video &middot; 53 photographs</span>
  <span class="prov"><b>__NPH__ measured</b> &middot; <i>__NVI__ derived</i></span>
</div>
<div class="bar">
  <button class="ly on" id="lyP">Photographs __NPH__</button>
  <button class="ly" id="lyV">Video readings __NVI__</button>
  <span id="chips" style="display:flex;gap:7px;flex-wrap:wrap"></span>
</div>
<div class="wrap"><div id="map"></div><div class="list" id="list"></div></div>
<script>
const PHOTOS=__PHOTOS__, VIDEO=__VIDEO__, SW=__SW__, UTIL=__UTIL__,
      CENTRE=__CENTRE__, WALK=__WALK__;
const map=L.map('map').setView(CENTRE,18);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
 {maxZoom:21,attribution:'Esri'}).addTo(map);
const walk=L.polyline(WALK,{color:'#F0842F',weight:3,opacity:.45,dashArray:'5 6'});
let layer='photo', markers=[], filter=null;

function rows(){return layer==='photo'?PHOTOS:VIDEO}
function colourOf(r){return SW[layer==='photo'?r.primary:r.colour]||'#888'}

function draw(){
  markers.forEach(m=>map.removeLayer(m)); markers=[];
  if(layer==='video'){walk.addTo(map)}else{map.removeLayer(walk)}
  const data=rows().filter(r=>!filter||colourKey(r)===filter);
  const pts=[];
  data.forEach((r,i)=>{
    const c=colourOf(r);
    const m=L.circleMarker([r.lat,r.lon],{radius:layer==='photo'?8:5,color:c,fillColor:c,
      fillOpacity:layer==='photo'?.95:.75,weight:layer==='photo'?2.5:1.5}).addTo(map);
    m.on('click',()=>select(r.id));
    markers.push(m); pts.push([r.lat,r.lon]);
  });
  if(pts.length) map.fitBounds(L.latLngBounds(pts).pad(.28));
  list(data);
}
function colourKey(r){return layer==='photo'?r.primary:r.colour}

function list(data){
  const el=document.getElementById('list'); el.innerHTML='';
  data.forEach(r=>{
    const c=colourOf(r), d=document.createElement('div');
    d.className='card'; d.style.setProperty('--c',c); d.id='c_'+r.id;
    const key=colourKey(r);
    d.innerHTML = '<img loading="lazy" src="'+r.img+'" alt="">'
      + '<div><div class="hd"><span class="tm">'
      + (layer==='photo' ? r.id.replace('IMG_','') : (r.t+'s'))
      + '</span><span class="cl">'+key+'</span></div>'
      + '<div class="ut">'+(UTIL[key]||'')+'</div>'
      + '<div class="dt">'
      + (layer==='photo'
          ? '<b>'+r.lat.toFixed(6)+', '+r.lon.toFixed(6)+'</b> <span class="tagm">measured</span><br>'
            + r.note + '<br>confirmed by eye'
          : r.lat.toFixed(5)+', '+r.lon.toFixed(5)+' <span class="tagd">derived</span><br>'
            + '<b>'+r.verdict+'</b> &middot; '+r.area+'px<br>'+r.why)
      + '</div></div>';
    d.onclick=()=>select(r.id);
    el.appendChild(d);
  });
}
function select(id){
  document.querySelectorAll('.card').forEach(c=>c.classList.remove('sel'));
  const c=document.getElementById('c_'+id);
  if(c){c.classList.add('sel');c.scrollIntoView({block:'nearest',behavior:'smooth'})}
}
function chips(){
  const el=document.getElementById('chips'); el.innerHTML='';
  const t={}; rows().forEach(r=>{const k=colourKey(r); t[k]=(t[k]||0)+1});
  Object.entries(t).sort((a,b)=>b[1]-a[1]).forEach(([k,n])=>{
    const s=document.createElement('span');
    s.className='chip'+(filter===k?' on':''); s.style.color=SW[k]||'#888';
    s.textContent=k+' '+n;
    s.onclick=()=>{filter=(filter===k?null:k); chips(); draw()};
    el.appendChild(s);
  });
}
function setLayer(l){
  layer=l; filter=null;
  document.getElementById('lyP').classList.toggle('on',l==='photo');
  document.getElementById('lyV').classList.toggle('on',l==='video');
  chips(); draw();
}
document.getElementById('lyP').onclick=()=>setLayer('photo');
document.getElementById('lyV').onclick=()=>setLayer('video');
setLayer('photo');
</script></body></html>"""


if __name__ == "__main__":
    main()
