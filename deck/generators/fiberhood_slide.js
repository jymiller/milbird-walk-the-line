/* The FiberHood: two layers over one block.
   Photographs carry measured EXIF GPS. Video readings are reconstructed along the walk. */
(function () {
  var svg = document.getElementById('fhsvg');
  var pane = document.getElementById('inspd');
  if (!svg || !pane || !window.FHDATA) return;

  var D = window.FHDATA, FR = window.FHFRAMES, RULE = window.FHRULE, UTIL = window.FHUTIL;
  var P = window.FHPHOTOS || [], PIMG = window.FHPIMG || {};
  var TOK = { orange: '--comms', yellow: '--gas', blue: '--water', green: '--sewer',
              red: '--elec', pink: '--elec', purple: '--water', white: '--ink' };
  var byId = {}, byPhoto = {};
  D.forEach(function (r) { byId[r.i] = r; });
  P.forEach(function (r) { byPhoto[r.id] = r; });

  var home = pane.innerHTML;
  var colours = [], rules = [], layer = 'photo';

  var MLABEL = { stroke_px: 'stroke', pavement_surround: 'pavement around it',
                 extent: 'extent', hue_std: 'hue spread', sat_mean: 'saturation',
                 exg: 'excess green', value_cv: 'brightness variation',
                 centroid_y_frac: 'height in frame' };

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function clearSel() {
    [].forEach.call(svg.querySelectorAll('.mk,.pk'), function (g) {
      g.classList.remove('sel'); });
  }

  /* ---- a photograph: measured position, human verdict ---- */
  function showPhoto(id) {
    var r = byPhoto[id]; if (!r) return;
    var img = PIMG[id] ? '<img class="ishot" alt="' + esc(r.note) + '" src="data:image/jpeg;base64,' + PIMG[id] + '">' : '';
    var chips = (r.cs || []).map(function (c) {
      return '<span class="icl" style="--c:var(' + (TOK[c] || '--muted') + ')">' + esc(c) + '</span>';
    }).join(' ');
    pane.innerHTML =
      '<button class="iback" type="button">&larr; all 26 photographs</button>' +
      '<div class="iscroll">' + img +
      '<div class="ihd"><span class="itm">' + esc(id.replace('IMG_', '')) + '</span>' + chips +
      '<span class="ivd">locate paint</span></div>' +
      '<p class="pgps">' + r.lat + ', ' + r.lon + ' &middot; EXIF, measured</p>' +
      '<p class="iwhy">' + esc(r.note) + '</p>' +
      '<p class="fl">Judged</p><p class="imeas">' +
      '<b>by eye</b> &mdash; a person opened this photograph and looked at it.<br>' +
      'Taken ' + esc(r.at) + '</p></div>';
    pane.querySelector('.iback').addEventListener('click', reset);
    clearSel();
    var g = svg.querySelector('.pk[data-p="' + id + '"]');
    if (g) g.classList.add('sel');
  }

  /* ---- a video reading: reconstructed position, machine verdict ---- */
  function showReading(id) {
    var r = byId[id]; if (!r) return;
    var tok = TOK[r.c] || '--muted';
    var img = FR[r.f] ? '<img class="ishot" alt="Frame at ' + r.t + ' seconds" src="data:image/jpeg;base64,' + FR[r.f] + '">' : '';
    var fired = (r.r || []).map(function (code) {
      return '<b>' + esc(code) + '</b> &mdash; ' + esc(RULE[code] || '');
    }).join('<br>') || '<b>none</b> &mdash; survived every rule';
    var meas = Object.keys(r.m || {}).map(function (k) {
      return esc(MLABEL[k] || k) + ' <b>' + r.m[k] + '</b>'; }).join(' &middot; ');
    pane.innerHTML =
      '<button class="iback" type="button">&larr; all 49 readings</button>' +
      '<div class="iscroll" style="--c:var(' + tok + ')">' + img +
      '<div class="ihd"><span class="itm">' + r.t + 's</span>' +
      '<span class="icl" style="--c:var(' + tok + ')">' + esc(r.c) + '</span>' +
      '<span class="ivd">' + esc(r.v) + '</span></div>' +
      '<p class="ihint" style="margin-bottom:8px">' + esc(UTIL[r.c] || '') + ' &middot; ' + r.a + '&thinsp;px</p>' +
      '<p class="iwhy">' + esc(r.w) + '</p>' +
      '<p class="fl">Rules that fired</p><p class="imeas">' + fired + '</p>' +
      '<p class="fl" style="margin-top:10px">Measured</p><p class="imeas">' + meas + '</p></div>';
    pane.querySelector('.iback').addEventListener('click', reset);
    clearSel();
    var g = svg.querySelector('.mk[data-i="' + id + '"]');
    if (g) g.classList.add('sel');
  }

  function reset() {
    pane.innerHTML = home;
    fillStrip();
    wire();
    applyFilter();
    clearSel();
  }

  function applyFilter() {
    var on = colours.length || rules.length;
    svg.classList.toggle('filtering', !!on);
    [].forEach.call(svg.querySelectorAll('.mk'), function (g) {
      var okC = !colours.length || colours.indexOf(g.dataset.c) > -1;
      var fired = (g.dataset.r || '').split('|');
      var okR = !rules.length || rules.some(function (x) { return fired.indexOf(x) > -1; });
      g.classList.toggle('hit-f', okC && okR);
    });
    [].forEach.call(svg.querySelectorAll('.pk'), function (g) {
      g.classList.toggle('hit-f', !colours.length || colours.indexOf(g.dataset.c) > -1); });
    [].forEach.call(pane.querySelectorAll('.cc'), function (b) {
      b.classList.toggle('on', colours.indexOf(b.dataset.c) > -1); });
    [].forEach.call(pane.querySelectorAll('.rc'), function (b) {
      b.classList.toggle('on', rules.indexOf(b.dataset.r) > -1); });
  }

  function toggle(a, v) { var i = a.indexOf(v); if (i > -1) a.splice(i, 1); else a.push(v); }

  function fillStrip() {
    var el = document.getElementById('strip');
    if (!el) return;
    el.innerHTML = '';
    var src = layer === 'photo' ? P : D;
    src.forEach(function (r) {
      var id = layer === 'photo' ? r.id : r.i;
      var img = layer === 'photo' ? PIMG[r.id] : FR[r.f];
      var tok = TOK[layer === 'photo' ? r.c : r.c] || '--muted';
      var b = document.createElement('button');
      b.type = 'button';
      b.style.setProperty('--c', 'var(' + tok + ')');
      b.title = layer === 'photo' ? (r.id + ' — ' + r.note) : (r.t + 's — ' + r.c);
      b.innerHTML = img ? '<img alt="" src="data:image/jpeg;base64,' + img + '">' : '';
      b.addEventListener('click', function () {
        layer === 'photo' ? showPhoto(id) : showReading(id); });
      b.addEventListener('mouseenter', function () {
        var g = svg.querySelector(layer === 'photo'
          ? '.pk[data-p="' + id + '"]' : '.mk[data-i="' + id + '"]');
        if (g) g.classList.add('sel'); });
      b.addEventListener('mouseleave', clearSel);
      el.appendChild(b);
    });
  }

  function wire() {
    [].forEach.call(pane.querySelectorAll('.cc'), function (b) {
      b.addEventListener('click', function () { toggle(colours, b.dataset.c); applyFilter(); }); });
    [].forEach.call(pane.querySelectorAll('.rc'), function (b) {
      b.addEventListener('click', function () { toggle(rules, b.dataset.r); applyFilter(); }); });
    var no = pane.querySelector('.sb.no'), ok = pane.querySelector('.sb.ok'), sn = pane.querySelector('#sn');
    if (no && sn) no.addEventListener('click', function () {
      sn.textContent = 'A refusal needs a name and a reason. Neither is set, so nothing was written.';
      sn.classList.add('warn'); });
    if (ok && sn) ok.addEventListener('click', function () {
      sn.textContent = 'A confirmation needs a signer. Nothing was written — sign it on the live API instead.';
      sn.classList.add('warn'); });
  }

  function setLayer(l) {
    layer = l;
    svg.classList.toggle('lay-photo', l === 'photo');
    svg.classList.toggle('lay-video', l === 'video');
    var box = svg.closest('.fh') || document.body;
    box.classList.toggle('lay-photo-pane', l === 'photo');
    [].forEach.call(document.querySelectorAll('.ly'), function (b) {
      b.classList.toggle('on', b.dataset.l === l); });
    reset();
  }

  [].forEach.call(svg.querySelectorAll('.mk'), function (g) {
    g.addEventListener('click', function () { showReading(g.dataset.i); }); });
  [].forEach.call(svg.querySelectorAll('.pk'), function (g) {
    g.addEventListener('click', function () { showPhoto(g.dataset.p); }); });
  [].forEach.call(document.querySelectorAll('.ly'), function (b) {
    b.addEventListener('click', function () { setLayer(b.dataset.l); }); });

  setLayer('photo');
})();
