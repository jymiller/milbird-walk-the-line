/**
 * A Utility Locates screen, drawn in the consuming app's own visual language.
 *
 * The work exists — 124 readings, seven classifiers, two escalations, a signed
 * log — but none of it is wired into that app yet. Rather than describe what it
 * would look like, this is the screen: the same cream ground, serif headings and
 * mono labels, with our readings on the real block.
 */
export function appView(DATA, REGIONS, WALK_JS) {
  const p = DATA.summary.pipeline;
  const cand = REGIONS.filter(r => r.verdict === 'candidate' || r.v === 'candidate');
  const rows = REGIONS.slice().sort((a, b) => a.t - b.t);
  return `<!doctype html><html lang=en><head><meta charset=utf8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Utility Locates — FiberOps Control Room</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
:root{
  --paper:#FAF8F5; --panel:#FFFFFF; --sunk:#F2EEE8; --rail:#F5F2ED;
  --ink:#1F1D1A; --ink2:#5A544C; --muted:#948C81; --line:#E5DFD6; --line2:#CFC7BA;
  --green:#2F6B46; --amber:#B8860B; --red:#B23A48; --orange:#D4621E; --blue:#2B5C8A;
  --serif:'Newsreader',Georgia,serif; --sans:'IBM Plex Sans',Helvetica,sans-serif;
  --mono:'IBM Plex Mono',Menlo,monospace;
}
*{box-sizing:border-box}
html,body{margin:0;height:100%;background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:15px}
.shell{display:grid;grid-template-columns:232px 1fr;min-height:100%}
.rail{background:var(--rail);border-right:1px solid var(--line);padding:18px 0}
.brand{display:flex;gap:11px;align-items:center;padding:0 18px 22px}
.logo{width:34px;height:34px;border-radius:8px;background:var(--green);display:flex;
  align-items:center;justify-content:center;flex:0 0 auto}
.logo svg{width:19px;height:19px;fill:none;stroke:#fff;stroke-width:1.9}
.brand b{font-family:var(--serif);font-weight:500;font-size:17px;display:block;line-height:1.1}
.brand span{font-family:var(--mono);font-size:9px;letter-spacing:.16em;color:var(--muted);text-transform:uppercase}
.navlab{font-family:var(--mono);font-size:9.5px;letter-spacing:.16em;color:var(--muted);
  text-transform:uppercase;padding:0 18px 9px}
.rail a{display:flex;gap:11px;align-items:center;padding:9px 18px;color:var(--ink2);
  text-decoration:none;font-size:14.5px}
.rail a.on{background:var(--sunk);color:var(--ink);font-weight:500;
  box-shadow:inset 2px 0 0 var(--green)}
.main{min-width:0}
.top{padding:22px 30px 18px;border-bottom:1px solid var(--line);display:flex;
  justify-content:space-between;align-items:flex-start;gap:20px;flex-wrap:wrap}
.back{font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--muted);text-decoration:none;display:block;margin-bottom:7px}
h1{font-family:var(--serif);font-weight:500;font-size:31px;letter-spacing:-.01em;margin:0 0 5px}
.crumb{font-family:var(--mono);font-size:12px;color:var(--muted);letter-spacing:.03em}
.acts{display:flex;gap:9px}
.btn{font-family:var(--mono);font-size:10.5px;letter-spacing:.11em;text-transform:uppercase;
  padding:9px 15px;border:1px solid var(--line2);border-radius:6px;background:var(--panel);
  color:var(--ink2);text-decoration:none;cursor:pointer}
.btn.pri{background:var(--sunk);border-color:var(--line2);color:var(--ink)}
.btn:hover{border-color:var(--green);color:var(--green)}
.body{padding:24px 30px 40px;display:grid;grid-template-columns:1fr 400px;gap:22px;align-items:start}
@media(max-width:1080px){.body{grid-template-columns:1fr}.shell{grid-template-columns:1fr}.rail{display:none}}
h2{font-family:var(--serif);font-weight:500;font-size:22px;margin:0 0 14px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden}
#map{height:clamp(360px,54vh,620px);width:100%}
.mapfoot{padding:11px 15px;border-top:1px solid var(--line);background:var(--sunk);
  font-family:var(--mono);font-size:11px;color:var(--muted);line-height:1.6}
.mapfoot b{color:var(--amber)}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:0;border:1px solid var(--line);
  border-radius:10px;overflow:hidden;background:var(--panel);margin:0 0 20px}
.st{padding:14px 12px;border-right:1px solid var(--line);text-align:center}
.st:last-child{border-right:0}
.st b{display:block;font-family:var(--mono);font-size:25px;font-weight:600;line-height:1}
.st span{display:block;font-family:var(--mono);font-size:9px;letter-spacing:.11em;
  text-transform:uppercase;color:var(--muted);margin-top:7px}
.qh{padding:13px 16px;border-bottom:1px solid var(--line);background:var(--sunk);
  font-family:var(--mono);font-size:10px;letter-spacing:.13em;text-transform:uppercase;color:var(--muted);
  display:flex;justify-content:space-between}
.q{max-height:540px;overflow-y:auto}
.qi{padding:12px 16px;border-bottom:1px solid var(--line);cursor:pointer;display:grid;
  grid-template-columns:1fr auto;gap:10px;align-items:start}
.qi:last-child{border-bottom:0}
.qi:hover{background:var(--sunk)}
.qi b{font-family:var(--serif);font-weight:500;font-size:16px;display:block;line-height:1.2}
.qi .m{font-family:var(--mono);font-size:10.5px;color:var(--muted);margin-top:3px;display:block}
.pill{font-family:var(--mono);font-size:8.5px;letter-spacing:.1em;text-transform:uppercase;
  padding:3px 8px;border-radius:999px;white-space:nowrap;font-weight:600;align-self:center}
.pill.rev{background:#FAF2DE;color:var(--amber)}
.pill.rej{background:var(--sunk);color:var(--muted)}
.pill.sim{background:#EAF2EC;color:var(--green)}
.leaflet-popup-content-wrapper{border-radius:9px}
.leaflet-popup-content{margin:12px 14px;font-family:var(--sans);font-size:13px;line-height:1.5}
.pt{font-family:var(--mono);font-size:10.5px;color:var(--muted);margin-bottom:4px}
.pv{font-family:var(--serif);font-size:16px;margin-bottom:5px}
.pr{font-family:var(--mono);font-size:10.5px;color:var(--red);line-height:1.6}
.pimg{width:100%;border-radius:6px;margin-top:8px;display:block}
.simban{display:none;background:#FAF2DE;border:1px solid var(--amber);color:#6B4E08;
  font-family:var(--mono);font-size:11px;letter-spacing:.06em;padding:10px 14px;border-radius:8px;
  margin:0 0 16px;text-transform:uppercase}
.prov{font-size:12.5px;color:var(--ink2);line-height:1.55;padding:14px 16px;border-top:1px solid var(--line)}
.prov b{color:var(--ink)}
</style></head><body>
<div class="shell">
  <nav class="rail">
    <div class="brand"><span class="logo"><svg viewBox="0 0 24 24"><path d="M4 17h16M6 17a6 6 0 0 1 12 0"/></svg></span>
      <span><b>Walk the Line</b><span>Control Room</span></span></div>
    <p class="navlab">Navigation</p>
    <a href="#">Overview</a>
    <a href="#" class="on">Utility Locates</a>
    <a href="#">Assignments</a>
  </nav>
  <div class="main">
    <div class="top">
      <div>
        <a class="back" href="/">&larr; Back to the API</a>
        <h1>Utility Locates</h1>
        <p class="crumb">Pine St, San Francisco &middot; Stage 2 &middot; proposed, awaiting sign-off</p>
      </div>
      <div class="acts">
        <span class="btn" id="simbtn">Show a marked block</span>
        <a class="btn pri" href="/v1/evidence">Export evidence</a>
      </div>
    </div>
    <div class="body">
      <div>
        <div class="simban" id="simban">Simulated layer on &mdash; illustrative positions, not detections from this video</div>
        <div class="stats">
          <div class="st"><b style="color:var(--orange)">${p.colour_regions}</b><span>readings</span></div>
          <div class="st"><b style="color:var(--red)">${p.rejected_by_classifiers}</b><span>rejected by rule</span></div>
          <div class="st"><b style="color:var(--amber)">${p.machine_candidates}</b><span>to review</span></div>
          <div class="st"><b style="color:var(--green)">${p.human_confirmed}</b><span>confirmed</span></div>
        </div>
        <div class="card">
          <div id="map"></div>
          <div class="mapfoot">Route <b>RECONSTRUCTED</b>, not recorded. iOS writes one location per clip,
            never a track. Measured: the block geometry and address (OpenStreetMap) and 405 s of footage.
            The pavement loop is <b>311 m</b> &mdash; 0.77 m/s, one clockwise lap at filming pace.</div>
        </div>
      </div>
      <div>
        <h2>Review queue</h2>
        <div class="card">
          <div class="qh"><span>${rows.length} readings</span><span>Stage 2</span></div>
          <div class="q" id="q"></div>
          <p class="prov"><b>Nothing here is confirmed.</b> Every reading landed as proposed. Two reached a
            person; neither was a locate mark. A named reviewer signs or refuses, and a refusal keeps its reason.</p>
        </div>
      </div>
    </div>
  </div>
</div>
<script>
const R = ${JSON.stringify(REGIONS)};
${WALK_JS}
const SIM = [{o:.06,c:'orange',u:'communications / fiber',k:'line'},{o:.11,c:'orange',u:'communications / fiber',k:'arrow'},
{o:.17,c:'orange',u:'communications / fiber',k:'line'},{o:.21,c:'yellow',u:'gas, oil, steam',k:'crossing'},
{o:.26,c:'orange',u:'communications / fiber',k:'line'},{o:.32,c:'blue',u:'potable water',k:'crossing'},
{o:.38,c:'orange',u:'communications / fiber',k:'line'},{o:.44,c:'red',u:'electric',k:'crossing'},
{o:.49,c:'orange',u:'communications / fiber',k:'arrow'},{o:.55,c:'orange',u:'communications / fiber',k:'line'},
{o:.61,c:'yellow',u:'gas, oil, steam',k:'crossing'},{o:.66,c:'green',u:'sewer, drain',k:'crossing'},
{o:.72,c:'orange',u:'communications / fiber',k:'line'},{o:.78,c:'orange',u:'communications / fiber',k:'line'},
{o:.84,c:'blue',u:'potable water',k:'crossing'},{o:.89,c:'orange',u:'communications / fiber',k:'arrow'}];
const B=G.door, ANCHOR=G.anchor, DUR=G.durationS;
const COL={orange:'#D4621E',red:'#B23A48',yellow:'#B8860B',green:'#2F6B46',blue:'#2B5C8A'};
const map=L.map('map',{zoomControl:false}).setView(B,20);
L.control.zoom({position:'bottomright'}).addTo(map);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',
 {maxZoom:22,maxNativeZoom:19,attribution:'&copy; OpenStreetMap contributors'}).addTo(map);
L.marker(atTime(0)).addTo(map).bindPopup('<div class="pv">724 Pine Street</div>'+
 '<div class="pt">37.791388, -122.407837 &middot; the walk starts and ends here</div>');
L.circleMarker(ANCHOR,{radius:7,color:'#B8860B',fill:false,weight:2,dashArray:'3 3'}).addTo(map)
 .bindPopup('<div class="pt">Camera GPS anchor</div><div class="pv">100 m from the door</div>'+
 '<div class="pt">90 m east, 44 m south. One ISO6709 point, claimed &plusmn;7 m.</div>');
const path=walkPolyline(2), marks={};
R.forEach(function(r,i){
  const pos=atTime(r.t), lat=pos[0], lon=pos[1], done=r.v==='candidate';
  const m=L.circleMarker([lat,lon],{radius:done?8:4.5,color:done?'#B8860B':'#948C81',
    fillColor:done?'#B8860B':(COL[r.c]||'#948C81'),fillOpacity:done?.95:.45,weight:done?2:1}).addTo(map);
  const frame='https://jymiller.github.io/milbird-walk-the-line/frames/t'+String(r.t).padStart(4,'0')+'.jpg';
  m.bindPopup('<div class="pt">t='+r.t+'s &middot; '+r.c+' &middot; '+r.a+'px</div><div class="pv">'+
    (done?'Reached a person. Not confirmed.':'Rejected by rule')+'</div>'+
    (r.rb.length?'<div class="pr">'+r.rb.join('<br>')+'</div>':'')+
    '<img class="pimg" src="'+frame+'" onerror="this.style.display=\\'none\\'">',{maxWidth:320});
  marks[i]=m;
});
L.polyline(path,{color:'#948C81',weight:2,opacity:.5,dashArray:'4 6'}).addTo(map);
map.fitBounds(L.latLngBounds(path.concat([B,ANCHOR])).pad(.05));
const q=document.getElementById('q');
q.innerHTML=R.map(function(r,i){
  const done=r.v==='candidate';
  return '<div class="qi" data-i="'+i+'"><span><b>'+r.c.charAt(0).toUpperCase()+r.c.slice(1)+
   ' &mdash; '+r.u+'</b><span class="m">t='+r.t+'s &middot; '+r.a+'px'+
   (r.rb.length?' &middot; '+r.rb.join(', '):'')+'</span></span>'+
   '<span class="pill '+(done?'rev':'rej')+'">'+(done?'To review':'Rejected')+'</span></div>';
}).join('');
q.addEventListener('click',function(e){
  const el=e.target.closest('.qi'); if(!el)return;
  const m=marks[el.dataset.i]; if(m){map.setView(m.getLatLng(),19);m.openPopup();}
});
const simLayer=L.layerGroup();
SIM.forEach(function(s){
  const pos=atTime(s.o*G.durationS), lat=pos[0], lon=pos[1];
  L.circleMarker([lat,lon],{radius:9,color:'#fff',weight:2,fillColor:COL[s.c],fillOpacity:.95})
   .addTo(simLayer).bindPopup('<div class="pt" style="color:#B8860B">Simulated &mdash; not a detection</div>'+
   '<div class="pv" style="color:'+COL[s.c]+'">'+s.c+' &middot; '+s.u+'</div>'+
   '<div class="pt">'+s.k+' marking, illustrative position</div>');
});
let on=false; const b=document.getElementById('simbtn'), ban=document.getElementById('simban');
b.addEventListener('click',function(){
  on=!on;
  if(on){simLayer.addTo(map);ban.style.display='block';b.textContent='Hide marked block';}
  else{map.removeLayer(simLayer);ban.style.display='none';b.textContent='Show a marked block';}
});
</script></body></html>`;
}
