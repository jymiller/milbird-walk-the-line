"""The architecture, with people in it.

Five layers. The top one is the actual street — the same neighbourhood the cover
draws — because every fact in this system starts as something that happened
outdoors. Then the phone that captures it, the console where an operator looks at
it, the edge where it is signed, and the pay application it finally has to defend.

Somebody is standing in every layer except the first. That is the point: nothing
here decides on its own.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1320, 470
LX = 196                      # label gutter
BANDS = [
    ("the ground",          "", 70),
    ("the phone",           "", 76),
    ("operations console",  "", 84),
    ("the edge",            "", 88),
    ("the pay application", "", 78),
]
FILLS = ["--sewer-soft", None, None, None, None]


def person(x, y, s=1.0, arm=None):
    """A person, drawn the way the rest of the deck draws things."""
    h = 30 * s
    return (f'<g class="pp">'
            f'<circle cx="{x}" cy="{y-h}" r="{6.5*s}"/>'
            f'<path d="M{x-9*s},{y-h*0.52} c0,{-9*s} {4*s},{-13*s} {9*s},{-13*s} '
            f'c{5*s},0 {9*s},{4*s} {9*s},{13*s}"/>'
            f'<path d="M{x},{y-h*0.52} V{y-h*0.30}"/>'
            f'<path d="M{x},{y-h*0.30} l{-6*s},{h*0.30} M{x},{y-h*0.30} l{6*s},{h*0.30}"/>'
            + (arm or '')
            + '</g>')


def build():
    ys, y = [], 0
    for _, _, hh in BANDS:
        ys.append((y, hh)); y += hh
    total = y

    out = [f'<svg viewBox="0 0 {W} {total}" id="archsvg" role="img" '
           'aria-label="Five layers. The street itself at the top, then the phone that captures it, '
           'an operations console where a person reviews, the edge where a proposal is signed and '
           'hash-linked, and the pay application the record has to defend. A person stands in every '
           'layer below the first.">']

    # bands
    for i, ((by, bh), (name, sub, _)) in enumerate(zip(ys, BANDS)):
        fill = FILLS[i]
        if fill:
            out.append(f'<rect x="0" y="{by}" width="{W}" height="{bh}" fill="var({fill})"/>')
        out.append(f'<path class="bl" d="M0,{by} H{W}"/>')
        out.append(f'<text class="bn" x="24" y="{by+bh/2+5}">{name.upper()}</text>')
    out.append(f'<path class="bl" d="M0,{total} H{W}"/>')
    out.append(f'<path class="gut" d="M{LX},0 V{total}"/>')

    # ---- 1 the ground: the same street the cover draws
    y0, h0 = ys[0]
    g = y0 + h0 - 14
    out.append(f'<g class="wl">')
    for hx in (300, 470, 640):
        out.append(f'<path d="M{hx-30},{g-20} L{hx},{g-38} L{hx+30},{g-20}"/>'
                   f'<path d="M{hx-24},{g-20} h48 v20 h-48 z"/>')
    out.append(f'<path d="M780,{g} v-24 M780,{g-22} c-9,-6 -12,-15 -7,-23 M780,{g-22} c9,-6 12,-15 7,-23"/>'
               f'<path d="M760,{g-46} c5,-19 35,-19 40,0 c12,3 12,19 -3,20 h-34 c-15,-1 -15,-17 -3,-20 z"/>')
    out.append('</g>')
    out.append(f'<path class="ln" d="M{LX+40},{g} H{W-40}"/>')
    out.append(f'<g class="tk">' + "".join(
        f'<path d="M{x},{g-9} v18"/>' for x in (360, 560, 900, 1120)) + '</g>')

    # ---- 2 the phone
    y1, h1 = ys[1]
    cy = y1 + h1 - 20
    out.append(person(LX + 70, cy, 1.0))
    out.append(f'<g class="ob"><rect x="{LX+92}" y="{cy-40}" width="22" height="36" rx="2"/>'
               f'<path d="M{LX+98},{cy-12} h10"/></g>')
    out.append(f'<g class="ob"><rect x="{LX+170}" y="{cy-34}" width="120" height="30"/>'
               + "".join(f'<path d="M{LX+180+i*22},{cy-34} v30"/>' for i in range(5)) + '</g>')
    out.append(f'<g class="ob">' + "".join(
        f'<rect x="{LX+330+i*26}" y="{cy-36+i*3}" width="34" height="26"/>' for i in range(4)) + '</g>')

    # ---- 3 operations console
    y2, h2 = ys[2]
    cy = y2 + h2 - 22
    out.append(person(LX + 70, cy, 1.0))
    out.append(f'<g class="ob"><path d="M{LX+104},{cy-8} h96 l10,10 h-116 z"/>'
               f'<rect x="{LX+114}" y="{cy-44}" width="76" height="36"/></g>')
    out.append(f'<g class="ob"><rect x="{LX+250}" y="{cy-44}" width="150" height="40"/>'
               f'<path d="M{LX+250},{cy-22} h150 M{LX+300},{cy-44} v40 M{LX+350},{cy-44} v40"/></g>')
    out.append('<g class="rl">' + "".join(
        f'<path d="M{LX+470+i*22},{cy-44} v34"/>' for i in range(7)) + '</g>')


    # ---- 4 the edge
    y3, h3 = ys[3]
    cy = y3 + h3 - 22
    out.append(person(LX + 70, cy, 1.0))
    out.append(f'<path class="sg" d="M{LX+120},{cy-16} c14,-18 24,4 38,-8 c12,-10 20,10 34,-4"/>')
    out.append(f'<path class="sgl" d="M{LX+112},{cy-6} h108"/>')
    out.append('<g class="ch">' + "".join(
        f'<rect x="{LX+270+i*74}" y="{cy-44}" width="60" height="38"/>'
        + (f'<path d="M{LX+270+i*74},{cy-25} h-14"/>' if i else '')
        for i in range(4)) + '</g>')
    out.append(f'<g class="ob"><rect x="{LX+620}" y="{cy-44}" width="130" height="38"/>'
               f'<path d="M{LX+632},{cy-30} h60 M{LX+632},{cy-20} h40"/></g>')
    out.append(f'<g class="gate"><path d="M{LX+880},{cy-44} v38"/>'
               f'<path class="bar" d="M{LX+860},{cy-26} h40"/></g>')

    # ---- 5 the pay application
    y4, h4 = ys[4]
    cy = y4 + h4 - 20
    out.append(person(LX + 70, cy, 1.0))
    out.append(f'<g class="ob"><path d="M{LX+112},{cy-42} h84 v52 h-84 z"/>'
               f'<path d="M{LX+124},{cy-28} h58 M{LX+124},{cy-16} h58 M{LX+124},{cy-4} h36"/></g>')

    # the line that threads the whole stack
    out.append(f'<path class="thread" d="M{LX+70},{ys[0][0]+ys[0][1]-14} '
               f'V{ys[4][0]+ys[4][1]-52}"/>')

    out.append('</svg>')
    return '<div class="scene archscene">' + "\n  ".join(out) + '</div>'


CSS = '''
/* ---- architecture: five layers, with people in them ---- */
.archscene{margin:clamp(8px,1.6vh,20px) 0 0}
.archscene svg{display:block;width:100%;height:auto;max-width:1320px}
#archsvg .bl{stroke:var(--line-strong);stroke-width:1.4;fill:none;opacity:.75}
#archsvg .gut{stroke:var(--line);stroke-width:1.2;fill:none;opacity:.7}
#archsvg .bn{font-family:var(--mono);font-size:14px;font-weight:600;letter-spacing:.13em;
  fill:var(--ink)}
#archsvg .bs{font-family:var(--mono);font-size:11.5px;fill:var(--muted)}
#archsvg .on{font-family:var(--mono);font-size:11.5px;fill:var(--muted)}
#archsvg .on.gy{fill:var(--elec)}
#archsvg .q{font-family:var(--mono);font-size:12.5px;fill:var(--ink-2);font-style:italic}
#archsvg .pp circle,#archsvg .pp path{fill:none;stroke:var(--comms);stroke-width:2.6;
  stroke-linecap:round;stroke-linejoin:round}
#archsvg .ob rect,#archsvg .ob path{fill:none;stroke:var(--ink-2);stroke-width:2.2;
  stroke-linejoin:round;stroke-linecap:round}
#archsvg .wl path{fill:none;stroke:var(--ink-2);stroke-width:2.2;stroke-linejoin:round;
  stroke-linecap:round}
#archsvg .ln{stroke:var(--comms);stroke-width:6;fill:none;stroke-linecap:round}
#archsvg .tk path{stroke:var(--comms);stroke-width:3.4;fill:none;stroke-linecap:round}
#archsvg .rl path{stroke:var(--ink-2);stroke-width:2.6;fill:none;stroke-linecap:round;opacity:.8}
#archsvg .ch rect{fill:none;stroke:var(--ink-2);stroke-width:2.2}
#archsvg .ch path{stroke:var(--ink-2);stroke-width:2;fill:none}
#archsvg .sg{fill:none;stroke:var(--comms);stroke-width:3.4;stroke-linecap:round}
#archsvg .sgl{stroke:var(--ink-2);stroke-width:1.8;fill:none;opacity:.7}
#archsvg .nn path{fill:none;stroke:var(--sewer);stroke-width:2;stroke-dasharray:6 5}
#archsvg .nt{font-family:var(--mono);font-size:11px;letter-spacing:.11em;fill:var(--sewer);
  font-weight:600}
#archsvg .gate path{stroke:var(--ink-2);stroke-width:2.2;fill:none}
#archsvg .gate .bar{stroke:var(--elec);stroke-width:5;stroke-linecap:round}
#archsvg .thread{stroke:var(--comms);stroke-width:2;fill:none;stroke-dasharray:5 7;opacity:.5}
'''

if __name__ == "__main__":
    open(f"{HERE}/arch.html", "w").write(build())
    open(f"{HERE}/arch.css", "w").write(CSS)
    print(f"arch.html {os.path.getsize(HERE+'/arch.html')} B · {len(BANDS)} layers")
