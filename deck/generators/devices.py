"""Three surfaces, drawn from photographs of the real thing.

TestFlight, the native app in a worker's hand, and the control room on a laptop.

Both phone screens are traced from screenshots taken on John's own iPhone on
2026-09-20 at 22:21 — the TestFlight row reads "Walk the Line (ff65bf) · 1.0.0
(8) · 90 days", and the app's three tabs are Assignments, History and Account.
Nothing here is inferred from source: the native app was built by Rene in a
Replit workspace this repo has no access to, so the photographs ARE the evidence.

The laptop is the control room at walk-the-line.replit.app, which is a React SPA
and was read from its bundle.

iOS colours do not follow the deck palette: TestFlight is black whatever theme
the deck is in, and the app is light. Both are scoped on #devsvg.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1320, 584

TFX, TFY, PW = 46, 96, 196        # TestFlight phone
APX, APY = 344, 96                # the app phone
LX, LY, LW = 706, 150, 452        # laptop screen box
PH = round(PW * 2.05)             # 402


def _shell(x, y, w, h, r, cls=""):
    return (f'<rect class="case" x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/>'
            f'<rect class="screen {cls}" x="{x+7}" y="{y+7}" width="{w-14}" height="{h-14}" rx="{r-6}"/>'
            f'<rect class="island {cls}" x="{x+w/2-27}" y="{y+17}" width="54" height="15" rx="7.5"/>')


def app_icon(x, y, s=26):
    """The Walk the Line icon: cream tile, an orange arc and a green line on it."""
    k = s / 26
    return f'''<g class="appicon">
      <rect x="{x}" y="{y}" width="{s}" height="{s}" rx="{6*k}"/>
      <path class="o" d="M{x+5*k},{y+17*k} a{8*k},{8*k} 0 0 1 {16*k},0"/>
      <path class="g" d="M{x+13*k},{y+6*k} V{y+21*k}"/>
      <circle class="g d" cx="{x+13*k}" cy="{y+13*k}" r="{3*k}"/>
    </g>'''


def testflight(x=TFX, y=TFY, w=PW):
    """TestFlight, Apps tab, Walk the Line under Currently Testing."""
    h, r = PH, round(PW * 0.16)
    L, R = x + 18, x + w - 18
    row = y + 122
    return f'''<g class="dev tf">
    {_shell(x, y, w, h, r, "dark")}
    <text class="tf-t" x="{L}" y="{y+66}">Apps</text>
    <circle class="tf-av" cx="{R-11}" cy="{y+58}" r="11"/>
    <text class="tf-s" x="{L}" y="{y+94}">Currently Testing</text>

    <rect class="tf-card on" x="{L}" y="{row}" width="{R-L}" height="52" rx="10"/>
    {app_icon(L+10, row+13)}
    <text class="tf-n" x="{L+48}" y="{row+24}">Walk the Line</text>
    <text class="tf-m" x="{L+48}" y="{row+39}">1.0.0 (8) &middot; 90 days</text>
    <rect class="tf-pill" x="{R-44}" y="{row+17}" width="36" height="19" rx="9.5"/>
    <text class="tf-open" x="{R-26}" y="{row+30}" text-anchor="middle">Open</text>

    <rect class="tf-card" x="{L}" y="{row+62}" width="{R-L}" height="52" rx="10"/>
    <rect class="tf-ghost" x="{L+10}" y="{row+75}" width="26" height="26" rx="6"/>
    <path class="tf-gl" d="M{L+48},{row+84} h58 M{L+48},{row+98} h40"/>
    <rect class="tf-card" x="{L}" y="{row+124}" width="{R-L}" height="52" rx="10"/>
    <rect class="tf-ghost" x="{L+10}" y="{row+137}" width="26" height="26" rx="6"/>
    <path class="tf-gl" d="M{L+48},{row+146} h48 M{L+48},{row+160} h34"/>

    <rect class="tf-search" x="{L}" y="{y+h-56}" width="{R-L}" height="28" rx="14"/>
    <g class="tf-mag"><circle cx="{L+20}" cy="{y+h-42}" r="4.6"/>
      <path d="M{L+23.4},{y+h-38.6} l3.4,3.4"/></g>
    <text class="tf-ph" x="{L+34}" y="{y+h-38}">Search</text>
    <rect class="home dark" x="{x+w/2-38}" y="{y+h-20}" width="76" height="4" rx="2"/>
  </g>'''


def the_app(x=APX, y=APY, w=PW):
    """The app itself: Assignments, empty, with its three tabs."""
    h, r = PH, round(PW * 0.16)
    L, R = x + 18, x + w - 18
    mid, cy = x + w / 2, y + 196
    tb = y + h - 66
    return f'''<g class="dev ap">
    {_shell(x, y, w, h, r, "lite")}
    <text class="ap-h" x="{L}" y="{y+58}">Hello, Worker</text>
    <text class="ap-t" x="{L}" y="{y+86}">Assignments</text>
    <rect class="ap-btn" x="{R-30}" y="{y+56}" width="30" height="26" rx="7"/>
    <g class="ap-ref"><path d="M{R-22},{y+66} a5.5,5.5 0 0 1 9.5,-2.2"/>
      <path d="M{R-8},{y+72} a5.5,5.5 0 0 1 -9.5,2.2"/>
      <path d="M{R-13.5},{y+61.2} l1.4,3.2 -3.3,.7"/>
      <path d="M{R-16.5},{y+76.8} l-1.4,-3.2 3.3,-.7"/></g>

    <g class="ap-empty">
      <path class="ring" d="M{mid+17.41},{cy-11.74} A21,21 0 1 1 {mid-1.46},{cy-20.95}"/>
      <path class="tick" d="M{mid-9},{cy+1} l6.5,6.5 L{mid+11},{cy-8}"/>
    </g>
    <text class="ap-e1" x="{mid}" y="{cy+52}" text-anchor="middle">No assignments</text>
    <text class="ap-e2" x="{mid}" y="{cy+72}" text-anchor="middle">You&rsquo;re all caught up for today.</text>

    <rect class="ap-bar" x="{x+14}" y="{tb}" width="{w-28}" height="44" rx="22"/>
    <rect class="ap-sel" x="{x+w/6-27}" y="{tb+4}" width="54" height="36" rx="18"/>
    <g class="ap-ic on"><rect x="{x+w/6-7}" y="{tb+9}" width="14" height="16" rx="2.4"/>
      <path d="M{x+w/6-2.6},{tb+9} v-2.4 h5.2 v2.4"/>
      <path class="li" d="M{x+w/6-3.4},{tb+14} h6 M{x+w/6-3.4},{tb+18} h6 M{x+w/6-3.4},{tb+22} h4"/></g>
    <text class="ap-lb on" x="{x+w/6}" y="{tb+36}" text-anchor="middle">Assignments</text>
    <g class="ap-ic"><circle cx="{mid}" cy="{tb+17}" r="8.4"/>
      <path d="M{mid},{tb+11.5} v6 h4.2"/></g>
    <text class="ap-lb" x="{mid}" y="{tb+36}" text-anchor="middle">History</text>
    <g class="ap-ic"><circle cx="{x+5*w/6}" cy="{tb+13.5}" r="4.6"/>
      <path d="M{x+5*w/6-8},{tb+25} a8,8 0 0 1 16,0"/></g>
    <text class="ap-lb" x="{x+5*w/6}" y="{tb+36}" text-anchor="middle">Account</text>
    <rect class="home lite" x="{x+w/2-38}" y="{y+h-20}" width="76" height="4" rx="2"/>
  </g>'''


def laptop(x=LX, y=LY, w=LW):
    h = round(w * 0.625)
    sb = 108
    cx = x + w - 156
    return f'''<g class="dev">
    <path class="base" d="M{x-46},{y+h+8} h{w+92} l-22,15 h-{w+48} z"/>
    <path class="hinge" d="M{x+w/2-30},{y+h+8} h60"/>
    <rect class="case" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>
    <rect class="screen" x="{x+9}" y="{y+9}" width="{w-18}" height="{h-18}" rx="4"/>
    <rect class="pane" x="{x+9}" y="{y+9}" width="{sb}" height="{h-18}"/>
    <path class="rule" d="M{x+9+sb},{y+9} V{y+h-9}"/>
    <g class="ui">
      <rect class="mark" x="{x+22}" y="{y+24}" width="16" height="16" rx="4"/>
      <path class="hd" d="M{x+46},{y+32} h44"/>
      <path class="rule" d="M{x+22},{y+56} h82"/>
      <rect class="sel" x="{x+14}" y="{y+68}" width="96" height="22" rx="3"/>
      <path class="on" d="M{x+26},{y+80} h40"/>
      <path d="M{x+26},{y+106} h52 M{x+26},{y+128} h34"/>
      <path class="hd big" d="M{x+136},{y+38} h116"/>
      <path d="M{x+136},{y+58} h74"/>
      <path class="rule" d="M{x+136},{y+74} h{w-166}"/>
      <rect x="{x+136}" y="{y+88}" width="{cx-x-160}" height="28" rx="3"/>
      <rect x="{x+136}" y="{y+124}" width="{cx-x-160}" height="28" rx="3"/>
      <rect x="{x+136}" y="{y+160}" width="{cx-x-160}" height="28" rx="3"/>
      <path d="M{x+148},{y+100} h66 M{x+148},{y+136} h48 M{x+148},{y+172} h58"/>
    </g>
    <g class="card">
      <rect class="bg" x="{cx}" y="{y+88}" width="134" height="110" rx="4"/>
      <path class="hd" d="M{cx+14},{y+110} h68"/>
      <path class="thin" d="M{cx+14},{y+128} h100 M{cx+14},{y+140} h78"/>
      <rect class="field" x="{cx+14}" y="{y+150}" width="106" height="20" rx="3"/>
      <rect class="btn" x="{cx+14}" y="{y+176}" width="106" height="18" rx="3"/>
    </g>
  </g>'''


def build():
    tf_r, ap_l = TFX + PW, APX
    ap_r, l_l = APX + PW, LX
    lh = round(LW * 0.625)
    ay = APY + 150
    back = APY + PH + 48
    return f'''<figure class="devfig"><svg viewBox="0 0 {W} {H}" id="devsvg" role="img"
  aria-label="Three surfaces. An iPhone showing TestFlight, with Walk the Line version 1.0.0 build 8 listed under Currently Testing and an Open button. An arrow labelled install leads to a second iPhone running the app itself: Hello Worker, the Assignments screen, an empty state reading No assignments, You are all caught up for today, and three tabs, Assignments, History and Account. An arrow labelled the evidence leads to a laptop showing the control room. A return arrow labelled the work runs back from the laptop to the app.">

  {testflight()}
  {the_app()}
  {laptop()}

  <path class="hop" d="M{tf_r+14},{ay} H{ap_l-24}"/>
  <path class="hd" d="M{ap_l-6},{ay} l-20,-6.5 l1.5,14 z"/>
  <text class="flow" x="{(tf_r+ap_l)/2}" y="{ay-14}" text-anchor="middle">install</text>
  <text class="flows" x="{(tf_r+ap_l)/2}" y="{ay+24}" text-anchor="middle">once</text>

  <path class="hop back" d="M{ap_r+14},{ay} C{ap_r+90},{ay} {l_l-90},{ay+60} {l_l-24},{ay+60}"/>
  <path class="hd back" d="M{l_l-6},{ay+60} l-20,-6.5 l1.5,14 z"/>
  <text class="flow back" x="{(ap_r+l_l)/2+16}" y="{ay-14}" text-anchor="middle">the evidence</text>

  <path class="hop out" d="M{l_l+60},{LY+lh+46} C{l_l-60},{back+40} {ap_r+40},{back} {ap_r-70},{back}"/>
  <path class="hd out" d="M{ap_r-88},{back} l20,-6.5 l-1.5,14 z"/>
  <text class="flow out" x="{(ap_r+l_l)/2-30}" y="{back+26}" text-anchor="middle">the work</text>

  <text class="role" x="{TFX}" y="{APY-28}">INSTALL</text>
  <text class="roles" x="{TFX}" y="{APY-11}">TestFlight, on the worker&rsquo;s phone</text>
  <text class="role" x="{APX}" y="{APY-28}">FIELD</text>
  <text class="roles" x="{APX}" y="{APY-11}">the app, in hand</text>
  <text class="role" x="{LX}" y="{APY-28}">OFFICE</text>
  <text class="roles" x="{LX}" y="{APY-11}">a laptop, the control room</text>
</svg>
  <figcaption class="cap2">Both phone screens are traced from photographs of a real iPhone, taken
  2026&#8209;09&#8209;20. <b>The build is real: 1.0.0 (8), ninety days left to run.</b> The assignment
  list is empty because nobody has sent it any work yet &mdash; which is the one step of this loop
  still untested.</figcaption></figure>'''


CSS = '''
/* ---- the three surfaces ---- */
/* iOS does not follow the deck palette: TestFlight is black in either theme and
   the app is light. These are the platform's own colours, scoped here. */
#devsvg{--tf-bg:#000;--tf-card:#1C1C1E;--tf-ink:#FFF;--tf-mute:#8E8E93;--tf-blue:#0A84FF;
  --ap-bg:#F5F3F0;--ap-ink:#17191A;--ap-mute:#8A8A8E;--ap-blue:#007AFF;--ap-line:#E2DFD8}
.devfig{margin:clamp(10px,1.8vh,22px) 0 8px}
.devfig svg{display:block;width:100%;height:auto;max-width:1320px}

#devsvg .case{fill:var(--sunk);stroke:var(--ink-2);stroke-width:2.6}
#devsvg .screen{fill:var(--paper)}
#devsvg .screen.dark{fill:var(--tf-bg)}
#devsvg .screen.lite{fill:var(--ap-bg)}
#devsvg .island{fill:var(--ink)}
#devsvg .island.dark{fill:#2A2A2C}
#devsvg .island.lite{fill:#17191A}
#devsvg .home.dark{fill:#48484A}
#devsvg .home.lite{fill:#C9C5BD}

/* TestFlight */
#devsvg .tf-t{font-family:var(--body);font-size:22px;font-weight:700;fill:var(--tf-ink)}
#devsvg .tf-av{fill:#3A3A3C}
#devsvg .tf-s{font-family:var(--body);font-size:11px;font-weight:600;fill:var(--tf-mute)}
#devsvg .tf-card{fill:var(--tf-card)}
#devsvg .tf-n{font-family:var(--body);font-size:10px;font-weight:600;fill:var(--tf-ink)}
#devsvg .tf-m{font-family:var(--body);font-size:8.6px;fill:var(--tf-mute)}
#devsvg .tf-pill{fill:#2C2C2E}
#devsvg .tf-open{font-family:var(--body);font-size:9px;font-weight:600;fill:var(--tf-blue)}
#devsvg .tf-ghost{fill:#2C2C2E}
#devsvg .tf-gl{stroke:#3A3A3C;stroke-width:4;stroke-linecap:round;fill:none}
#devsvg .tf-search{fill:#1C1C1E}
#devsvg .tf-mag circle{fill:none;stroke:var(--tf-mute);stroke-width:1.5}
#devsvg .tf-mag path{stroke:var(--tf-mute);stroke-width:1.6;stroke-linecap:round;fill:none}
#devsvg .tf-ph{font-family:var(--body);font-size:10px;fill:var(--tf-mute)}
#devsvg .appicon rect{fill:#EFEADC}
#devsvg .appicon .o{fill:none;stroke:#D2601C;stroke-width:2.4;stroke-linecap:round}
#devsvg .appicon .g{fill:none;stroke:#3F7A43;stroke-width:2.4;stroke-linecap:round}
#devsvg .appicon .g.d{fill:#EFEADC}

/* the app */
#devsvg .ap-h{font-family:var(--body);font-size:11.5px;fill:var(--ap-mute)}
#devsvg .ap-t{font-family:var(--body);font-size:17.5px;font-weight:700;fill:var(--ap-ink)}
#devsvg .ap-btn{fill:none;stroke:var(--ap-line);stroke-width:1.4}
#devsvg .ap-ref path{fill:none;stroke:var(--ap-ink);stroke-width:1.5;stroke-linecap:round}
#devsvg .ap-empty .ring{fill:none;stroke:#9A9A9E;stroke-width:2.6;stroke-linecap:round}
#devsvg .ap-empty .tick{fill:none;stroke:#9A9A9E;stroke-width:2.8;
  stroke-linecap:round;stroke-linejoin:round}
#devsvg .ap-e1{font-family:var(--body);font-size:12.5px;font-weight:700;fill:var(--ap-ink)}
#devsvg .ap-e2{font-family:var(--body);font-size:10.5px;fill:var(--ap-mute)}
#devsvg .ap-bar{fill:#FFF;stroke:var(--ap-line);stroke-width:1.2}
#devsvg .ap-sel{fill:#EAE7E0}
#devsvg .ap-ic rect,#devsvg .ap-ic circle,#devsvg .ap-ic path{fill:none;stroke:var(--ap-ink);
  stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}
#devsvg .ap-ic.on rect,#devsvg .ap-ic.on path{stroke:var(--ap-blue)}
#devsvg .ap-ic .li{stroke-width:1.3}
#devsvg .ap-lb{font-family:var(--body);font-size:7.4px;fill:var(--ap-ink)}
#devsvg .ap-lb.on{fill:var(--ap-blue);font-weight:600}

/* laptop */
#devsvg .base{fill:var(--sunk);stroke:var(--ink-2);stroke-width:2.6;stroke-linejoin:round}
#devsvg .hinge{stroke:var(--ink-2);stroke-width:2.6;fill:none}
#devsvg .pane{fill:var(--surface)}
#devsvg .rule{stroke:var(--line);stroke-width:1.4;fill:none}
#devsvg .ui path{stroke:var(--line-strong);stroke-width:2.4;fill:none;stroke-linecap:round}
#devsvg .ui path.hd{stroke:var(--ink-2);stroke-width:4}
#devsvg .ui path.hd.big{stroke:var(--ink);stroke-width:6}
#devsvg .ui path.on{stroke:var(--comms);stroke-width:3}
#devsvg .ui rect{fill:none;stroke:var(--line);stroke-width:1.5}
#devsvg .ui rect.mark{fill:var(--comms);stroke:none}
#devsvg .ui rect.sel{fill:var(--comms-soft);stroke:var(--comms);stroke-width:1.4}
#devsvg .card rect{fill:none;stroke:var(--line-strong);stroke-width:1.6}
#devsvg .card rect.bg{fill:var(--surface);stroke:var(--ink-2)}
#devsvg .card rect.field{fill:var(--paper);stroke:var(--line)}
#devsvg .card rect.btn{fill:var(--sewer);stroke:none}
#devsvg .card path{stroke:var(--ink-2);stroke-width:3.6;fill:none;stroke-linecap:round}
#devsvg .card path.thin{stroke:var(--line-strong);stroke-width:1.8}

/* the flow */
#devsvg .hop{fill:none;stroke:var(--ink-2);stroke-width:2.6;stroke-dasharray:9 7}
#devsvg .hd{fill:var(--ink-2);stroke:none}
#devsvg .hop.back{stroke:var(--sewer)}
#devsvg .hd.back{fill:var(--sewer)}
#devsvg .hop.out{stroke:var(--comms)}
#devsvg .hd.out{fill:var(--comms)}
#devsvg .flow{font-family:var(--mono);font-size:14px;font-weight:600;fill:var(--ink-2);
  letter-spacing:.05em}
#devsvg .flow.back{fill:var(--sewer)}
#devsvg .flow.out{fill:var(--comms)}
#devsvg .flows{font-family:var(--mono);font-size:11px;fill:var(--muted)}
#devsvg .role{font-family:var(--mono);font-size:14px;font-weight:600;letter-spacing:.16em;
  fill:var(--ink)}
#devsvg .roles{font-family:var(--mono);font-size:11.5px;fill:var(--muted)}
@media (max-width:860px){.devfig svg{min-width:700px}}
'''

if __name__ == "__main__":
    open(f"{HERE}/devices.html", "w").write(build())
    open(f"{HERE}/devices.css", "w").write(CSS)
    print(f"devices.html {os.path.getsize(HERE+'/devices.html')} B")
