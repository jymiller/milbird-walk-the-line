/**
 * The walk, reconstructed.
 *
 * The clip carries ONE GPS point — iOS writes a single ISO6709 location per
 * video, not a track — so the filmer's path was never in the file. What is
 * real: the block geometry (OSM), the address (OSM), and the 405-second
 * duration. The pavement loop is ~311 m, which at 405 s is 0.77 m/s: one
 * clockwise lap at the pace of somebody filming the pavement.
 *
 * So the path below is a RECONSTRUCTION from measured geometry and measured
 * time, not recorded GPS, and every surface that draws it says so.
 */
export const GEO = {
  door:       [37.791388, -122.407837],   // 724 Pine St (OSM)
  anchor:     [37.7912,   -122.4078],     // the one point the camera wrote
  anchorAccM: 7.0,
  // Street centrelines from OSM, inset to the pavement: Pine, California and
  // Stockton are arterials (~11 m centreline to sidewalk), Joice is an alley (~5.5 m).
  pine:       37.791201,                  // south pavement
  california: 37.792024,                  // north pavement
  joice:      -122.408310,                // west pavement
  stockton:   -122.407585,                // east pavement
  durationS:  404.1,
};

/** Clockwise from the front door: west on Pine, north on Joice, east on
 *  California, south on Stockton, west back to the door. */
export function walkLegs(g) {
  const d = g.door;
  return [
    [[g.pine, d[1]],            [g.pine, g.joice]],
    [[g.pine, g.joice],         [g.california, g.joice]],
    [[g.california, g.joice],   [g.california, g.stockton]],
    [[g.california, g.stockton],[g.pine, g.stockton]],
    [[g.pine, g.stockton],      [g.pine, d[1]]],
  ];
}

export const WALK_JS = `
const G = ${JSON.stringify(GEO)};
const MPD_LAT = 111320, MPD_LON = 111320*Math.cos(G.door[0]*Math.PI/180);
function legs(){const d=G.door;return [
  [[G.pine,d[1]],[G.pine,G.joice]],[[G.pine,G.joice],[G.california,G.joice]],
  [[G.california,G.joice],[G.california,G.stockton]],
  [[G.california,G.stockton],[G.pine,G.stockton]],
  [[G.pine,G.stockton],[G.pine,d[1]]]];}
function legLen(a,b){const dy=(b[0]-a[0])*MPD_LAT,dx=(b[1]-a[1])*MPD_LON;return Math.hypot(dx,dy);}
const LEGS=legs(), LENS=LEGS.map(l=>legLen(l[0],l[1]));
const PERIM=LENS.reduce((a,b)=>a+b,0);
/* Position at time t, with a small deterministic wobble so 124 points do not
   sit on a mathematically perfect line — a person does not walk a ruler. */
function atTime(t){
  let s=(t/G.durationS)*PERIM, i=0;
  while(i<LENS.length-1 && s>LENS[i]){ s-=LENS[i]; i++; }
  const [a,b]=LEGS[i], k=Math.min(1,s/LENS[i]);
  const lat=a[0]+(b[0]-a[0])*k, lon=a[1]+(b[1]-a[1])*k;
  const w=Math.sin(t*0.21)*0.7 + Math.sin(t*0.083)*0.5;   // ~1.2 m, a pavement is narrow
  const horiz=Math.abs(b[0]-a[0])<Math.abs(b[1]-a[1]);
  return horiz ? [lat + w/MPD_LAT, lon] : [lat, lon + w/MPD_LON];
}
function walkPolyline(step){
  const pts=[]; for(let t=0;t<=G.durationS;t+=(step||3)) pts.push(atTime(t));
  pts.push(atTime(G.durationS)); return pts;
}
const PERIM_M = Math.round(PERIM);
`;
