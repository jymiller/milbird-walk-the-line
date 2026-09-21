/**
 * The walk, reconstructed — now on the street grid that is actually there.
 *
 * The clip carries ONE GPS point — iOS writes a single ISO6709 location per
 * video, not a track — so the filmer's path was never in the file. What is
 * real: the block geometry (OSM), the address (OSM), and the 404-second
 * duration.
 *
 * The first version of this walked an axis-aligned rectangle in latitude and
 * longitude. San Francisco is not axis-aligned. Measured off 256 m of Pine
 * Street centreline in OSM, this grid runs at 9.11 degrees, so that rectangle
 * was rotated wrong by nine degrees and the walk never sat on the pavement.
 *
 * BLOCK below is the oriented bounding box of the sixteen buildings standing on
 * the block, pushed out 6.5 m to the middle of the walked pavement. 64.6 m by
 * 86.0 m, a 353 m perimeter, which over 404.1 s is 0.87 m/s — one lap at the
 * pace of somebody filming the ground.
 *
 * It is still a RECONSTRUCTION from measured geometry and measured time, not
 * recorded GPS, and every surface that draws it says so.
 */
export const GEO = {
  door:       [37.791388, -122.407837],   // 724 Pine St (OSM)
  anchor:     [37.7912,   -122.4078],     // the one point the camera wrote
  anchorAccM: 7.0,
  durationS:  404.1,
  gridDeg:    9.11,                       // measured, not assumed
  // Corners of the walked pavement, in order: SW, SE, NE, NW.
  corners: [
    [37.791216, -122.408231],
    [37.791326, -122.407360],
    [37.792205, -122.407538],
    [37.792094, -122.408410],
  ],
  perimeterM: 353,
  paceMS:     0.87,
};

/** Four legs around the block, in corner order. */
export function walkLegs(g) {
  const c = g.corners;
  return [0, 1, 2, 3].map(i => [c[i], c[(i + 1) % 4]]);
}

export const WALK_JS = `
const G = ${JSON.stringify(GEO)};
const MPD_LAT = 111320, MPD_LON = 111320*Math.cos(G.door[0]*Math.PI/180);
function legs(){const c=G.corners;return [0,1,2,3].map(i=>[c[i],c[(i+1)%4]]);}
function legLen(a,b){const dy=(b[0]-a[0])*MPD_LAT,dx=(b[1]-a[1])*MPD_LON;return Math.hypot(dx,dy);}
const LEGS=legs(), LENS=LEGS.map(l=>legLen(l[0],l[1]));
const PERIM=LENS.reduce((a,b)=>a+b,0);

/* The walk starts at the front door, so find where the door sits along the
   perimeter and offset every time by that much. */
function projectDoor(){
  let best={d:Infinity,s:0}, acc=0;
  for(let i=0;i<LEGS.length;i++){
    const [a,b]=LEGS[i];
    const ax=(a[1]-G.door[1])*MPD_LON, ay=(a[0]-G.door[0])*MPD_LAT;
    const bx=(b[1]-a[1])*MPD_LON,      by=(b[0]-a[0])*MPD_LAT;
    const L2=bx*bx+by*by;
    let t=L2?(-(ax*bx+ay*by)/L2):0; t=Math.max(0,Math.min(1,t));
    const dx=ax+t*bx, dy=ay+t*by, d=Math.hypot(dx,dy);
    if(d<best.d) best={d,s:acc+t*LENS[i]};
    acc+=LENS[i];
  }
  return best.s;
}
const S0=projectDoor();

/* Position at time t, with a small deterministic wobble so the readings do not
   sit on a mathematically perfect line — a person does not walk a ruler. */
function atTime(t){
  let s=(S0+(t/G.durationS)*PERIM)%PERIM, i=0;
  while(i<LENS.length-1 && s>LENS[i]){ s-=LENS[i]; i++; }
  const [a,b]=LEGS[i], k=Math.min(1,s/LENS[i]);
  const lat=a[0]+(b[0]-a[0])*k, lon=a[1]+(b[1]-a[1])*k;
  const w=Math.sin(t*0.21)*0.7 + Math.sin(t*0.083)*0.5;   // ~1.2 m, a pavement is narrow
  /* offset perpendicular to the leg, whatever direction the leg runs */
  const dy=(b[0]-a[0])*MPD_LAT, dx=(b[1]-a[1])*MPD_LON, L=Math.hypot(dx,dy)||1;
  return [lat + (w*(-dx/L))/MPD_LAT, lon + (w*(dy/L))/MPD_LON];
}
function walkPolyline(step){
  const pts=[]; for(let t=0;t<=G.durationS;t+=(step||3)) pts.push(atTime(t));
  pts.push(atTime(G.durationS)); return pts;
}
const PERIM_M = Math.round(PERIM);
`;
