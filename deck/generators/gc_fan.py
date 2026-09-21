"""The general contractor, below the line on "The system".

Eight stages, eight different crews, eight different ways of proving what was
done. One party is accountable for all of them, against a contract that has been
simplified to a single number. The drawing is a fan-in: many hands at the top,
one signed record at the bottom, and above it the one number everything is
measured by.

Stage names and quantities are the seeded demo data from the control room. They are
illustrative, not measured, and nothing here claims otherwise.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

W, H = 1320, 320
STAGES = [
    ("Drawings",    "1 / 12 ea"),
    ("Locates",     "2.50 / 74 ea"),
    ("Hydrovac",    "0 / 27 ea"),
    ("Trenching",   "25 / 4,118 m"),
    ("Conduit",     "0 / 3,724 m"),
    ("Jetting",     "0 / 3,724 m"),
    ("Splicing",    "0 / 186 ea"),
    ("Restoration", "0 / 882 m"),
]
COL = W / len(STAGES)
TOP, GLYPH_H = 58, 46
JOIN_Y, REC_Y = 218, 240
CX = W / 2


def glyph(i, cx, y):
    """Each trade proves itself differently. Eight silhouettes, not eight boxes."""
    g = [
        # drawings — a rolled sheet
        f'<path d="M{cx-26},{y} h44 l8,8 v30 h-52 z"/><path d="M{cx-18},{y+14} h30 M{cx-18},{y+24} h22"/>',
        # locates — paint marks on ground
        f'<path d="M{cx-26},{y+30} h52"/><path d="M{cx-14},{y+30} v-14 M{cx+2},{y+30} v-20 M{cx+14},{y+30} v-10"/>',
        # hydrovac — a truck hose over a hole
        f'<path d="M{cx-26},{y+16} h30 v16 h-30 z"/><path d="M{cx+4},{y+22} h18 v10 h-18"/>'
        f'<path d="M{cx-6},{y+32} v6 h16 v-6"/>',
        # trenching — a cut in the ground
        f'<path d="M{cx-28},{y+18} h14 v20 h24 v-20 h14"/>',
        # conduit — stacked ducts
        f'<circle cx="{cx-12}" cy="{y+28}" r="8"/><circle cx="{cx+4}" cy="{y+28}" r="8"/>'
        f'<circle cx="{cx-4}" cy="{y+14}" r="8"/>',
        # jetting — a spool
        f'<circle cx="{cx}" cy="{y+24}" r="16"/><circle cx="{cx}" cy="{y+24}" r="5"/>',
        # splicing — a closure with fibres
        f'<path d="M{cx-18},{y+14} h36 v22 h-36 z"/><path d="M{cx-28},{y+25} h10 M{cx+18},{y+25} h10"/>',
        # restoration — a slab relaid
        f'<path d="M{cx-28},{y+20} h56 v18 h-56 z"/><path d="M{cx-10},{y+20} v18 M{cx+8},{y+20} v18"/>',
    ][i]
    return f'<g class="gy">{g}</g>'


def build():
    cols, feeds, labels = [], [], []
    for i, (name, qty) in enumerate(STAGES):
        cx = COL * (i + 0.5)
        cols.append(glyph(i, cx, TOP))
        # every trade's evidence falls to the same place
        feeds.append(f'<path class="fd" d="M{cx},{TOP+GLYPH_H+46} V{JOIN_Y-22} '
                     f'Q{cx},{JOIN_Y} {CX + (cx-CX)*0.06},{JOIN_Y}"/>')
        labels.append(
            f'<text class="sn" x="{cx}" y="{TOP+GLYPH_H+16}" text-anchor="middle">{name}</text>'
            f'<text class="sq" x="{cx}" y="{TOP+GLYPH_H+34}" text-anchor="middle">{qty}</text>')

    return f'''<figure class="gcfan"><svg viewBox="0 0 {W} {H}" role="img"
  aria-label="Eight build stages across the top, each drawn as the thing that trade produces, each with its actual against its planned quantity. A line falls from every one of them and converges into a single signed record at the bottom. Above them all runs one contract rule, measured in dollars per meter.">

  <!-- the one number the whole job is judged by -->
  <path class="rule" d="M40,26 H{W-40}"/>
  <text class="cn" x="{W-40}" y="18" text-anchor="end">THE CONTRACT &mdash; $ PER METER</text>
  <g class="ticks">{"".join(f'<path d="M{COL*(i+0.5)},26 v8"/>' for i in range(len(STAGES)))}</g>

  <g class="gys">{"".join(cols)}</g>
  <g class="lbl">{"".join(labels)}</g>
  <g class="feeds">{"".join(feeds)}</g>

  <!-- one party is accountable for all of it -->
  <g class="rec">
    <path class="box" d="M{CX-240},{REC_Y} h480 v62 h-480 z"/>
    <path class="sig" d="M{CX-206},{REC_Y+36} c16,-20 27,5 41,-9 c13,-13 21,13 38,-2 c12,-11 23,9 38,-5"/>
    <path class="sigline" d="M{CX-214},{REC_Y+46} h186"/>
    <text class="rl" x="{CX+6}" y="{REC_Y+30}" text-anchor="start">ONE RECORD</text>
    <text class="rl2" x="{CX+6}" y="{REC_Y+50}" text-anchor="start">ONE NAME ON IT</text>
  </g>
</svg>
  <figcaption class="cap2">Eight stages, eight crews, eight different ways of proving what was done.
  <b>The general contractor is the only party accountable for all of them</b> &mdash; and for a contract
  that has been simplified to one number.</figcaption></figure>'''


CSS = '''
/* ---- the GC fan-in, below the line on The system ---- */
.gcfan{margin:clamp(14px,2.4vh,28px) 0 6px}
.gcfan svg{display:block;width:100%;height:auto;max-width:1320px}
.gcfan .rule{stroke:var(--ink-2);stroke-width:2.5;fill:none}
.gcfan .ticks path{stroke:var(--ink-2);stroke-width:1.6;fill:none;opacity:.55}
.gcfan .cn{font-family:var(--mono);font-size:13px;letter-spacing:.14em;fill:var(--muted)}
.gcfan .gy path,.gcfan .gy circle{fill:none;stroke:var(--ink-2);stroke-width:2.4;
  stroke-linecap:round;stroke-linejoin:round}
.gcfan .sn{font-family:var(--mono);font-size:13px;letter-spacing:.06em;fill:var(--ink-2)}
.gcfan .sq{font-family:var(--mono);font-size:12px;fill:var(--muted)}
.gcfan .fd{fill:none;stroke:var(--comms);stroke-width:2.6;opacity:.75;stroke-linecap:round}
.gcfan .rec .box{fill:var(--surface);stroke:var(--ink-2);stroke-width:2.6;stroke-linejoin:round}
.gcfan .rec .sig{fill:none;stroke:var(--comms);stroke-width:4;stroke-linecap:round}
.gcfan .rec .sigline{stroke:var(--ink-2);stroke-width:2;fill:none;opacity:.7}
.gcfan .rl{font-family:var(--display);font-size:19px;font-weight:600;fill:var(--ink);
  letter-spacing:.02em}
.gcfan .rl2{font-family:var(--mono);font-size:12px;letter-spacing:.1em;fill:var(--muted)}
'''

if __name__ == "__main__":
    open(f"{HERE}/gc.html", "w").write(build())
    open(f"{HERE}/gc.css", "w").write(CSS)
    print(f"gc.html {os.path.getsize(HERE+'/gc.html')} B · css {len(CSS)} B · {len(STAGES)} stages")
