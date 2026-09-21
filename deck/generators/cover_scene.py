"""The cover scene: one line that becomes a neighbourhood.

A FiberHood is not a linear run. It is a distribution point and a drop to every
house on the street. The trunk draws itself in first, left to right — that is the
walk — and then the drops rise to each door, which is the thing actually being
sold. Grass, trees, a sidewalk to walk, and the road it all runs beside.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

W, H = 1320, 330
HOUSE_X = [250, 540, 830, 1120]
TREE_X = [400, 690, 980]

# bands, top to bottom
LAWN_Y, LAWN_H = 182, 34
WALK_Y, WALK_H = 216, 22
VERGE_Y, VERGE_H = 238, 40
ROAD_Y = 278
TRUNK_Y = 259            # the fiber, in the verge
CAB_X = 62               # the distribution point


def house(cx, w=168, h=104, base=182):
    """A flat, drawn house: body, roof, door, two windows."""
    x0, y0 = cx - w / 2, base - h
    roof = h * 0.40
    body_y = y0 + roof
    dw, dh = 26, 40
    return f'''<g class="ho">
    <path d="M{x0-10},{body_y} L{cx},{y0} L{x0+w+10},{body_y}"/>
    <path d="M{x0},{body_y} h{w} v{h-roof} h-{w} z"/>
    <path d="M{cx-dw/2},{base} v-{dh} h{dw} v{dh}"/>
    <path d="M{x0+22},{body_y+18} h30 v26 h-30 z"/>
    <path d="M{x0+w-52},{body_y+18} h30 v26 h-30 z"/>
  </g>'''


def tree(cx, base=182):
    return f'''<g class="tr">
    <path d="M{cx},{base} v-34"/>
    <path d="M{cx},{base-30} c-13,-8 -18,-21 -11,-32 M{cx},{base-30} c13,-8 18,-21 11,-32"/>
    <path d="M{cx-30},{base-70} c7,-28 53,-28 60,0 c18,5 18,28 -5,30 h-50 c-23,-2 -23,-25 -5,-30 z"/>
  </g>'''


def build():
    houses = "\n  ".join(house(x) for x in HOUSE_X)
    trees = "\n  ".join(tree(x) for x in TREE_X)

    # the drop to each door: up out of the verge, under the walk, into the house
    drops = "\n    ".join(
        f'<path class="dr" d="M{x},{TRUNK_Y} V{LAWN_Y - 14}"/>' for x in HOUSE_X)
    # a small tap where each drop leaves the trunk
    taps = "".join(f'<circle class="tap" cx="{x}" cy="{TRUNK_Y}" r="6"/>' for x in HOUSE_X)

    # one length of verge cut open, so the trunk is visible in the ground
    TR_X0, TR_X1 = 896, 1022

    # grass tufts along the verge
    tufts = " ".join(
        f"M{x},{VERGE_Y + VERGE_H} v-{9 + (i % 3) * 4}"
        for i, x in enumerate(range(30, W, 46)))

    return f'''<div class="scene netscene"><svg viewBox="0 0 {W} {H}" role="img"
  aria-label="A neighbourhood street: four houses behind lawns and trees, a sidewalk, a grass verge and the road. One orange fiber trunk runs along the verge from a distribution cabinet, with a drop rising to every house, and one length of the verge cut open so the trunk can be seen in the ground.">

  <!-- the ground it all sits on -->
  <rect class="lawn" x="0" y="{LAWN_Y}" width="{W}" height="{LAWN_H}"/>
  <rect class="walk" x="0" y="{WALK_Y}" width="{W}" height="{WALK_H}"/>
  <rect class="verge" x="0" y="{VERGE_Y}" width="{W}" height="{VERGE_H}"/>
  <rect class="road" x="0" y="{ROAD_Y}" width="{W}" height="{H - ROAD_Y}"/>
  <path class="edge" d="M0,{WALK_Y} H{W} M0,{VERGE_Y} H{W} M0,{ROAD_Y} H{W}"/>
  <path class="joint" d="{' '.join(f'M{x},{WALK_Y} v{WALK_H}' for x in range(110, W, 110))}"/>
  <path class="centre" d="M0,{ROAD_Y + 44} H{W}"/>
  <path class="tuft" d="{tufts}"/>

  <!-- the street -->
  {houses}
  {trees}

  <!-- the distribution point the whole FiberHood hangs off -->
  <g class="cab">
    <path d="M{CAB_X - 26},{TRUNK_Y - 4} v-54 h52 v54"/>
    <path d="M{CAB_X - 14},{TRUNK_Y - 40} h28 M{CAB_X - 14},{TRUNK_Y - 28} h28"/>
  </g>

  <!-- the verge, cut open -->
  <g class="cut">
    <path class="void" d="M{TR_X0},{VERGE_Y} v{VERGE_H + 14} h{TR_X1 - TR_X0} v-{VERGE_H + 14}"/>
    <path class="rib" d="M{TR_X0 + 16},{VERGE_Y + 10} v{VERGE_H} M{TR_X1 - 16},{VERGE_Y + 10} v{VERGE_H}"/>
    <path class="spoil" d="M{TR_X1 + 4},{VERGE_Y} q22,-18 44,0 z"/>
  </g>

  <!-- THE LINE, and the drops that are the actual product -->
  <path class="trunk" d="M{CAB_X},{TRUNK_Y} H{W - 24}"/>
  <g class="drops">
    {drops}
    {taps}
  </g>
</svg></div>'''


CSS = '''
/* ---- the cover scene: a line that becomes a neighbourhood ---- */
.netscene{margin:clamp(14px,2.6vh,34px) 0 0}
.netscene svg{display:block;width:100%;height:auto;max-width:1320px}
.netscene .lawn,.netscene .verge{fill:var(--sewer-soft)}
.netscene .walk{fill:var(--sunk)}
.netscene .road{fill:var(--surface)}
.netscene .edge{stroke:var(--line-strong);stroke-width:1.6;fill:none;opacity:.8}
.netscene .joint{stroke:var(--line-strong);stroke-width:1.2;fill:none;opacity:.55}
.netscene .centre{stroke:var(--line-strong);stroke-width:2.4;fill:none;
  stroke-dasharray:26 22;opacity:.65}
.netscene .tuft{stroke:var(--sewer);stroke-width:2;fill:none;opacity:.6;stroke-linecap:round}
.netscene .ho path,.netscene .tr path,.netscene .cab path{fill:none;stroke:var(--ink-2);
  stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
.netscene .cut .void{fill:var(--paper);stroke:var(--ink-2);stroke-width:2.4;
  stroke-linejoin:round}
.netscene .cut .spoil{fill:var(--ink-2);opacity:.25;stroke:none}
.netscene .cut .rib{fill:none;stroke:var(--ink-2);stroke-width:2;opacity:.5}
.netscene .trunk{stroke:var(--comms);stroke-width:7;fill:none;stroke-linecap:round}
.netscene .dr{stroke:var(--comms);stroke-width:4.5;fill:none;stroke-linecap:round}
.netscene .tap{fill:var(--comms)}

/* the walk first, then the drops — linear becomes network */
body.anim .slide.live .netscene > *{animation:none}
body.anim .slide.live .netscene .trunk{animation:wipe 1.15s cubic-bezier(.3,.8,.3,1) both;
  animation-delay:.25s}
body.anim .slide.live .netscene .drops{animation:fadein .6s ease both;animation-delay:1.25s}
body.anim .slide.live .netscene .ho{animation:fadein .5s ease backwards}
body.anim .slide.live .netscene .ho:nth-of-type(1){animation-delay:.10s}
body.anim .slide.live .netscene .ho:nth-of-type(2){animation-delay:.16s}
body.anim .slide.live .netscene .ho:nth-of-type(3){animation-delay:.22s}
body.anim .slide.live .netscene .ho:nth-of-type(4){animation-delay:.28s}

/* ---- the scroll cue: a mark, not a sentence ---- */
.down{display:flex;justify-content:center;align-items:center;margin:clamp(14px,2.2vh,28px) 0 0;
  cursor:pointer;color:var(--muted);border:0;background:none;padding:6px;width:100%}
.down::after{content:none}
.down svg{width:26px;height:15px;display:block;overflow:visible}
.down path{fill:none;stroke:currentColor;stroke-width:2.4;stroke-linecap:round;
  stroke-linejoin:round}
.down:hover{color:var(--comms)}
body.anim .slide.live .down{animation:cuein .5s ease both;animation-delay:1.7s}
@keyframes cuein{from{opacity:0}to{opacity:.55}}
.down{opacity:.55}
body.anim .slide.live .down svg{animation:bob 2.4s ease-in-out 2.2s infinite}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(5px)}}
@media (prefers-reduced-motion:reduce){
  body.anim .slide.live .down svg{animation:none}
}
'''

CUE = ('<p class="down" role="button" tabindex="0" aria-label="More detail below">'
       '<svg viewBox="0 0 26 15" aria-hidden="true"><path d="M3,3 L13,12 L23,3"/></svg></p>')

if __name__ == "__main__":
    open(f"{HERE}/scene.html", "w").write(build())
    open(f"{HERE}/scene.css", "w").write(CSS)
    open(f"{HERE}/cue.html", "w").write(CUE)
    print(f"scene {os.path.getsize(HERE+'/scene.html')} B  css {len(CSS)} B")
    print(f"houses {len(HOUSE_X)}  trees {len(TREE_X)}  trunk y={TRUNK_Y}  viewBox {W}x{H}")
