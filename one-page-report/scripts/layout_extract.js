// Runs inside the rendered report page. Returns every visible piece with its real
// position, so build_pptx.py can place native PowerPoint objects exactly where the
// browser put them. Coordinates are CSS px on the 1920x1080 page (zoom included).
() => {
  const out = [];
  const px = (v) => parseFloat(v) || 0;
  const color = (c) => {
    const m = c && c.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(',').map((x) => parseFloat(x));
    if (p.length === 4 && p[3] < 0.05) return null;
    return '#' + p.slice(0, 3).map((x) => Math.round(x).toString(16).padStart(2, '0')).join('');
  };
  const rect = (el) => { const r = el.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; };
  const zoomOf = (el) => { let z = 1, e = el; while (e && e.nodeType === 1) { const v = parseFloat(getComputedStyle(e).zoom); if (v) z *= v; e = e.parentElement; } return z; };

  // 1. boxes: zones, cards, tabs, chips, issues, steps, notes, table cells
  const boxSel = '.zone, .card, .tab, .chip, .cat .k, .callout, .steps li, .steps li .n, .st';
  document.querySelectorAll(boxSel).forEach((el) => {
    const cs = getComputedStyle(el), r = rect(el);
    if (r.w < 2 || r.h < 2) return;
    let fill = color(cs.backgroundColor), line = null, lw = 0;
    const ring = cs.boxShadow && cs.boxShadow.match(/rgba?\([^)]+\)/);
    if (cs.borderTopStyle !== 'none' && px(cs.borderTopWidth) > 0) { line = color(cs.borderTopColor); lw = px(cs.borderTopWidth); }
    else if (ring) { line = color(ring[0]); lw = 1.5; }
    if (el.classList.contains('zone')) {
      const b = getComputedStyle(el, '::before'); line = color(b.borderTopColor); lw = px(b.borderTopWidth) * zoomOf(el);
    }
    let accent = null;
    if (px(cs.borderLeftWidth) >= 3 && cs.borderLeftStyle !== 'none') accent = color(cs.borderLeftColor);
    const round = px(cs.borderTopLeftRadius) > 0 || el.classList.contains('zone');
    out.push({ kind: 'box', cls: el.className.toString().split(' ')[0], ...r, fill, line, lw, round, accent,
               circle: el.classList.contains('n') });
  });

  // 2. text: collect styled fragments per text node and visual line, then merge fragments
  //    that sit on the same line inside the same block into one line with several runs.
  const skip = (el) => el.closest('svg');
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
    acceptNode: (n) => (n.nodeValue.trim() && !skip(n.parentElement)) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT,
  });
  let n; const frags = [];
  while ((n = walker.nextNode())) {
    const el = n.parentElement, cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    const range = document.createRange(), text = n.nodeValue;
    // split into visual lines
    let start = 0, lineTop = null, buf = '', lineRect = null;
    const block = el.closest('.ctitle,.tagline,.sub,.foot,.btitle,.issue .p,.issue .f,.issue,.chip,.cat .k,td,th,.steps li,.callout,.tab,.lead,.kicker,h1,.foot-meta>span,.big,.stat .v,.stat .l,.stat .c,.st,.text p,.text li,.note,div,span') || el;
    const flush = () => {
      if (buf.replace(/\s+/g, '') && lineRect) frags.push({ text: buf.replace(/[ \t\n\r]+/g, ' '), x: lineRect.left, y: lineRect.top, w: lineRect.right - lineRect.left, h: lineRect.bottom - lineRect.top,
        size: px(cs.fontSize) * zoomOf(el), bold: (parseInt(cs.fontWeight) || 400) >= 600, color: color(cs.color), block });
      buf = ''; lineRect = null;
    };
    for (let i = 0; i < text.length; i++) {
      range.setStart(n, i); range.setEnd(n, i + 1);
      const rs = range.getClientRects(); if (!rs.length) { buf += text[i]; continue; }
      const r = rs[0];
      if (lineTop !== null && Math.abs(r.top - lineTop) > r.height * 0.5) flush();
      lineTop = r.top; buf += text[i];
      lineRect = lineRect ? { left: Math.min(lineRect.left, r.left), right: Math.max(lineRect.right, r.right), top: Math.min(lineRect.top, r.top), bottom: Math.max(lineRect.bottom, r.bottom) }
                          : { left: r.left, right: r.right, top: r.top, bottom: r.bottom };
    }
    flush();
  }

  // merge fragments: same visual line (centre within half a line) and touching horizontally
  frags.sort((a, b) => (a.y - b.y) || (a.x - b.x));
  const lines = [];
  frags.forEach((f) => {
    const cy = f.y + f.h / 2;
    const L = lines.find((l) => Math.abs(l.cy - cy) < Math.max(l.h, f.h) * 0.45 && f.x >= l.x + l.w - 2 && f.x - (l.x + l.w) < f.size * 1.2);
    if (L) { L.runs.push({ text: ((f.x - (L.x + L.w) > f.size * 0.15 && !/\s$/.test(L.runs[L.runs.length-1].text) && !/^\s/.test(f.text)) ? ' ' : '') + f.text, bold: f.bold, color: f.color, size: f.size }); L.w = f.x + f.w - L.x; L.h = Math.max(L.h, f.h); }
    else lines.push({ kind: 'text', x: f.x, y: f.y, w: f.w, h: f.h, cy, size: f.size, runs: [{ text: f.text, bold: f.bold, color: f.color, size: f.size }] });
  });
  lines.forEach((l) => { l.runs[0].text = l.runs[0].text.replace(/^\s+/, ''); const z = l.runs[l.runs.length - 1]; z.text = z.text.replace(/\s+$/, ''); out.push(l); });

  // 3. html icons and SVG charts / timelines: export as images (except charts, rebuilt natively)
  document.querySelectorAll('svg.ic, svg.chart, svg.timeline').forEach((svg) => {
    const r = rect(svg); if (r.w < 2) return;
    const clone = svg.cloneNode(true);
    const c = getComputedStyle(svg).color;
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    clone.setAttribute('width', r.w); clone.setAttribute('height', r.h);
    let s = new XMLSerializer().serializeToString(clone).replace(/currentColor/g, c);
    s = s.replace(/font-family="inherit"/g, 'font-family="' + getComputedStyle(document.body).fontFamily.replace(/"/g, "'") + '"');
    const item = { kind: svg.classList.contains('ic') ? 'icon' : (svg.classList.contains('chart') ? 'chart' : 'timeline'), ...r, svg: s };
    if (item.kind === 'chart') item.data = svg.getAttribute('data-chart');
    out.push(item);
  });
  return { page: { w: 1920, h: 1080, bg: color(getComputedStyle(document.body).backgroundColor) || '#ffffff' }, items: out };
}
