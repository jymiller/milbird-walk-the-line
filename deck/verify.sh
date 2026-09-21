#!/bin/bash
S=/private/tmp/claude-501/-Users-johnmiller-src-work-milbird-hackathons-fig/2e1b1d50-e541-46e3-9992-0d85355741e9/scratchpad
i=$1; fold=${2:-0}
python3 - "$S" "$i" "$fold" <<'PY'
import sys
S,i,fold=sys.argv[1],int(sys.argv[2]),int(sys.argv[3])
h=open(f"{S}/walk-the-line.html").read()
j=("""<script>setTimeout(function(){
 var t=document.getElementById('track');
 if(t){t.style.transition='none';t.style.transform='translateX(-%d%%)';}
 var s=document.querySelectorAll('.slide'); if(s[%d])s[%d].classList.add('live');
 document.body.classList.add('anim');
 %s
},700);</script>""" % (i*100, i, i,
 ("var f=document.querySelectorAll('.slide')[%d]; if(f) f.scrollTop=99999;"%i) if fold else ""))
open(f"{S}/_v.html","w").write(h.replace("</body>", j+"</body>",1))
PY
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --hide-scrollbars --force-device-scale-factor=2 --virtual-time-budget=8000 \
  --window-size=1000,531 --screenshot="$S/_v${i}_${fold}.png" "file://$S/_v.html" >/dev/null 2>&1
echo "$S/_v${i}_${fold}.png"
