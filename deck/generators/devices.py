"""Two devices, drawn as they actually are.

A laptop in an office and an iPhone outdoors. The phone is running Safari on the
live URL — there is no App Store build and no TestFlight, so the drawing does not
invent one. What a field worker really does is tap a link.

Both screens show the app's own routes, read out of its bundle, not imagined.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1320, 516
HOST = "walk-the-line.replit.app"

LX, LY, LW = 62, 78, 548          # laptop screen box
PX, PY, PW = 1046, 48, 214        # phone body


def laptop(x=LX, y=LY, w=LW):
    """Control room: sidebar, the people list, the invite card with its button."""
    h = round(w * 0.625)
    sb = 128
    cx = x + w - 182                                   # invite card left
    return f'''<g class="dev">
    <path class="base" d="M{x-54},{y+h+8} h{w+108} l-26,17 h-{w+56} z"/>
    <path class="hinge" d="M{x+w/2-36},{y+h+8} h72"/>
    <rect class="case" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>
    <rect class="screen" x="{x+9}" y="{y+9}" width="{w-18}" height="{h-18}" rx="4"/>

    <rect class="pane" x="{x+9}" y="{y+9}" width="{sb}" height="{h-18}"/>
    <path class="rule" d="M{x+9+sb},{y+9} V{y+h-9}"/>
    <g class="ui">
      <rect class="mark" x="{x+24}" y="{y+26}" width="18" height="18" rx="4"/>
      <path class="hd" d="M{x+50},{y+35} h56"/>
      <path class="rule" d="M{x+24},{y+62} h100"/>
      <rect class="sel" x="{x+16}" y="{y+76}" width="114" height="24" rx="3"/>
      <path class="on" d="M{x+28},{y+89} h46"/>
      <path d="M{x+28},{y+118} h62 M{x+28},{y+142} h40"/>
    </g>

    <g class="ui">
      <path class="hd big" d="M{x+160},{y+40} h132"/>
      <path d="M{x+160},{y+62} h86"/>
      <path class="rule" d="M{x+160},{y+80} h{w-196}"/>
      <rect x="{x+160}" y="{y+96}" width="{cx-x-184}" height="32" rx="3"/>
      <rect x="{x+160}" y="{y+138}" width="{cx-x-184}" height="32" rx="3"/>
      <rect x="{x+160}" y="{y+180}" width="{cx-x-184}" height="32" rx="3"/>
      <path d="M{x+174},{y+110} h78 M{x+174},{y+152} h58 M{x+174},{y+194} h68"/>
    </g>

    <g class="card">
      <rect class="bg" x="{cx}" y="{y+96}" width="156" height="126" rx="4"/>
      <path class="hd" d="M{cx+16},{y+120} h80"/>
      <path class="thin" d="M{cx+16},{y+140} h118 M{cx+16},{y+153} h92"/>
      <rect class="field" x="{cx+16}" y="{y+164}" width="124" height="22" rx="3"/>
      <rect class="btn" x="{cx+16}" y="{y+194}" width="124" height="20" rx="3"/>
    </g>
  </g>'''


def iphone(x=PX, y=PY, w=PW):
    """Safari on the live URL, sitting on the capture screen."""
    h = round(w * 2.05)
    r = round(w * 0.16)
    top = y + 44                       # Safari chrome top
    vt = top + 46                      # viewfinder top
    vb = y + h - 78                    # viewfinder bottom (above bottom bar)
    return f'''<g class="dev phone">
    <rect class="case" x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/>
    <rect class="screen" x="{x+7}" y="{y+7}" width="{w-14}" height="{h-14}" rx="{r-6}"/>
    <rect class="island" x="{x+w/2-29}" y="{y+18}" width="58" height="16" rx="8"/>

    <rect class="chrome" x="{x+7}" y="{top}" width="{w-14}" height="46"/>
    <rect class="urlbar" x="{x+18}" y="{top+12}" width="{w-36}" height="23" rx="11.5"/>
    <g class="lock"><rect x="{x+29}" y="{top+22}" width="8" height="6.4" rx="1.3"/>
      <path d="M{x+30.6},{top+22} v-3.4 a2.4,2.4 0 0 1 4.8,0 v3.4"/></g>
    <text class="url" x="{x+44}" y="{top+28.5}">{HOST}</text>

    <rect class="feed" x="{x+7}" y="{vt}" width="{w-14}" height="{vb-vt}"/>
    <g class="vf">
      <path d="M{x+26},{vt+34} v-16 h18 M{x+w-26},{vt+34} v-16 h-18
               M{x+26},{vb-52} v16 h18 M{x+w-26},{vb-52} v16 h-18"/>
      <circle cx="{x+w/2}" cy="{(vt+vb)/2-14}" r="27"/>
      <circle cx="{x+w/2}" cy="{(vt+vb)/2-14}" r="9"/>
    </g>
    <g class="chip">
      <rect x="{x+20}" y="{vb-42}" width="{w-40}" height="26" rx="13"/>
      <circle cx="{x+38}" cy="{vb-29}" r="5.4"/><circle class="dot" cx="{x+38}" cy="{vb-29}" r="1.8"/>
      <text class="fix" x="{x+52}" y="{vb-25}">37.7914, &minus;122.4078</text>
    </g>

    <rect class="bottom" x="{x+7}" y="{vb}" width="{w-14}" height="{y+h-7-vb}"/>
    <circle class="shut out" cx="{x+w/2}" cy="{vb+34}" r="21"/>
    <circle class="shut in"  cx="{x+w/2}" cy="{vb+34}" r="16"/>
    <rect class="home" x="{x+w/2-42}" y="{y+h-22}" width="84" height="4.5" rx="2.2"/>
  </g>'''


def build():
    lh = round(LW * 0.625)
    lr = LX + LW                                # laptop right edge
    pl = PX                                     # phone left edge
    ph = round(PW * 2.05)
    join_y0, join_y1 = LY + 118, PY + 92        # out of the laptop, into the URL bar
    ev_y0,   ev_y1   = PY + ph - 150, LY + 258  # out of the phone, back to the list
    return f'''<figure class="devfig"><svg viewBox="0 0 {W} {H}" id="devsvg" role="img"
  aria-label="A laptop showing the control room, with a sidebar, a list of people and an invite card with its button. An orange dashed arrow labelled the join link crosses to an iPhone running Safari on walk-the-line.replit.app, showing the capture screen: a camera viewfinder, a chip carrying a position, and a shutter button. A green dashed arrow labelled the evidence crosses back to the laptop.">

  {laptop()}
  {iphone()}

  <path class="hop" d="M{lr+16},{join_y0} C{lr+130},{join_y0} {pl-130},{join_y1} {pl-24},{join_y1}"/>
  <path class="hd" d="M{pl-6},{join_y1} l-20,-6.5 l1.5,14 z"/>
  <text class="flow" x="{(lr+pl)/2}" y="{(join_y0+join_y1)/2-18}" text-anchor="middle">the join link</text>

  <path class="hop back" d="M{pl-16},{ev_y0} C{pl-130},{ev_y0} {lr+130},{ev_y1} {lr+24},{ev_y1}"/>
  <path class="hd back" d="M{lr+6},{ev_y1} l20,-6.5 l-1.5,14 z"/>
  <text class="flow back" x="{(lr+pl)/2}" y="{(ev_y0+ev_y1)/2+34}" text-anchor="middle">the evidence</text>

  <text class="role" x="{LX+2}" y="{LY-24}">OFFICE</text>
  <text class="roles" x="{LX+2}" y="{LY-7}">a laptop, the control room</text>
  <text class="role" x="{PX}" y="{PY-24}">FIELD</text>
  <text class="roles" x="{PX}" y="{PY-7}">a phone, outdoors</text>
</svg>
  <figcaption class="cap2">No App Store build, no TestFlight. <b>A field worker opens a link in Safari
  &mdash; that is the whole install.</b> Depending on who you are talking to, that is either the best
  thing about it or the first thing to fix.</figcaption></figure>'''


CSS = '''
/* ---- the two devices, drawn as they are ---- */
.devfig{margin:clamp(10px,1.8vh,22px) 0 8px}
.devfig svg{display:block;width:100%;height:auto;max-width:1320px}
#devsvg .case{fill:var(--sunk);stroke:var(--ink-2);stroke-width:2.6}
#devsvg .screen{fill:var(--paper)}
#devsvg .base{fill:var(--sunk);stroke:var(--ink-2);stroke-width:2.6;stroke-linejoin:round}
#devsvg .hinge{stroke:var(--ink-2);stroke-width:2.6;fill:none}
#devsvg .pane{fill:var(--surface)}
#devsvg .rule{stroke:var(--line);stroke-width:1.4;fill:none}
#devsvg .ui path{stroke:var(--line-strong);stroke-width:2.6;fill:none;stroke-linecap:round}
#devsvg .ui path.hd{stroke:var(--ink-2);stroke-width:4.5}
#devsvg .ui path.hd.big{stroke:var(--ink);stroke-width:6.5}
#devsvg .ui path.on{stroke:var(--comms);stroke-width:3}
#devsvg .ui rect{fill:none;stroke:var(--line);stroke-width:1.5}
#devsvg .ui rect.mark{fill:var(--comms);stroke:none}
#devsvg .ui rect.sel{fill:var(--comms-soft);stroke:var(--comms);stroke-width:1.4}
#devsvg .card rect{fill:none;stroke:var(--line-strong);stroke-width:1.6}
#devsvg .card rect.bg{fill:var(--surface);stroke:var(--ink-2)}
#devsvg .card rect.field{fill:var(--paper);stroke:var(--line)}
#devsvg .card rect.btn{fill:var(--sewer);stroke:none}
#devsvg .card path{stroke:var(--ink-2);stroke-width:4;fill:none;stroke-linecap:round}
#devsvg .card path.thin{stroke:var(--line-strong);stroke-width:1.8}

#devsvg .island{fill:var(--ink)}
#devsvg .chrome{fill:var(--surface)}
#devsvg .urlbar{fill:var(--sunk);stroke:var(--line);stroke-width:1.2}
#devsvg .lock rect{fill:var(--muted)}
#devsvg .lock path{fill:none;stroke:var(--muted);stroke-width:1.4}
#devsvg .url{font-family:var(--mono);font-size:10.5px;fill:var(--ink-2)}
/* a camera feed is a photograph, not a UI surface — it stays dark in both themes,
   so these two do not follow the palette */
#devsvg{--cam:#171C12;--cam-ink:#E9EDE0}
#devsvg .feed{fill:var(--cam)}
#devsvg .bottom{fill:var(--surface)}
#devsvg .vf path{stroke:var(--cam-ink);stroke-width:3;fill:none;stroke-linecap:round;
  stroke-linejoin:round;opacity:.85}
#devsvg .vf circle{fill:none;stroke:var(--cam-ink);stroke-width:2.2;opacity:.55}
#devsvg .chip rect{fill:var(--sewer);stroke:none}
#devsvg .chip circle{fill:none;stroke:var(--cam-ink);stroke-width:1.8}
#devsvg .chip circle.dot{fill:var(--cam-ink);stroke:none}
#devsvg .fix{font-family:var(--mono);font-size:10px;fill:var(--cam-ink);font-weight:600}
#devsvg .shut.out{fill:none;stroke:var(--line-strong);stroke-width:2.4}
#devsvg .shut.in{fill:var(--ink-2)}
#devsvg .home{fill:var(--line-strong)}

#devsvg .hop{fill:none;stroke:var(--comms);stroke-width:2.8;stroke-dasharray:9 7}
#devsvg .hd{fill:var(--comms);stroke:none}
#devsvg .hop.back{stroke:var(--sewer)}
#devsvg .hd.back{fill:var(--sewer)}
#devsvg .flow{font-family:var(--mono);font-size:14px;font-weight:600;fill:var(--comms);
  letter-spacing:.05em}
#devsvg .flow.back{fill:var(--sewer)}
#devsvg .role{font-family:var(--mono);font-size:14px;font-weight:600;letter-spacing:.16em;
  fill:var(--ink)}
#devsvg .roles{font-family:var(--mono);font-size:11.5px;fill:var(--muted)}
@media (max-width:820px){.devfig svg{min-width:660px}}
'''

if __name__ == "__main__":
    open(f"{HERE}/devices.html", "w").write(build())
    open(f"{HERE}/devices.css", "w").write(CSS)
    print(f"devices.html {os.path.getsize(HERE+'/devices.html')} B · host {HOST}")
