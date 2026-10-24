"""Diagram blocks for one-page-report: pictures that carry the logic, text as support.

Each function takes the block dict and the style, and returns one self-contained <svg class="diagram">.
Layout is computed from the content (text widths, item counts), so the same block works for any report.
Fonts use the page's 4-size scale only: 46 (big number), 18 (heading / key value), 14 (everything else).
Colours come from the style tokens, so light/dark themes and every style work without changes.

Blocks (see references/diagrams.md for when to use each):
  route     A -> B (and back): distance, start/end level, optional comparison bars
  formula   value x value = result, optional scale of points (e.g. price by time of day)
  progress  current vs target on one track, optional "A -> B" mini flow under it
  gauge     one score on a half ring + an optional badge (rank, award)
  compare   2-3 options side by side, one recommended, reached from one question
  decision  yes / no question with the two outcomes
  transform before -> after (two boxes and an arrow)
  flowsteps numbered steps with icons, joined by a line
Report charts (form rules from the dataviz skill and the IBCS reporting standard, in our own words):
  stattile  big number + change vs a comparison + sparkline
  bullet    actual vs target per row, with a comparison mark and optional good/poor ranges
  dumbbell  before -> after for several items (one row each)
  slope     two points in time for 1-6 items; the one that matters highlighted
  waterfall start -> contributions (+/-) -> end (bridge)
  variance  each item's gap to target / plan / last year, right = better
  stacked   parts of a whole per row (absolute or 100%)
  heatmap   two dimensions crossed; one hue light -> dark, the worst/best cell outlined
Standard library only.
"""
import html, math, re

SIZES = (14, 18, 46)

def esc(s):
    return html.escape(str(s), quote=True)

def tw(s, size):
    """Rough rendered width in px (CJK ~1em, latin ~0.56em)."""
    s = re.sub(r"<[^>]+>", "", str(s))
    return sum(size * (1.0 if ord(c) > 0x2E80 else 0.62) for c in s)

def fit(s, size, maxw):
    """One line, cut with an ellipsis if it would overflow."""
    return wrap(s, size, maxw, 1)[0]

def fit_size(s, maxw, sizes=(46, 34, 18, 14)):
    """Largest size from the page scale at which s fits in maxw."""
    for z in sizes:
        if tw(s, z) <= maxw:
            return z
    return sizes[-1]

def wrap(s, size, maxw, max_lines=2):
    """Greedy wrap by characters (CJK) and words (latin). Last line gets an ellipsis if it overflows."""
    s = str(s); lines, cur = [], ""
    tokens = re.findall(r"[A-Za-z0-9.,%+\-/()$€£¥:]+|\s+|.", s)
    for t in tokens:
        if tw(cur + t, size) <= maxw or not cur:
            cur += t
        else:
            lines.append(cur.strip()); cur = t.lstrip()
    if cur.strip():
        lines.append(cur.strip())
    if len(lines) > max_lines:
        last = lines[max_lines - 1]
        while last and tw(last + "…", size) > maxw:
            last = last[:-1]
        lines = lines[:max_lines - 1] + [last + "…"]
    return lines or [""]

_HALO = ["#fff"]

LABELS = {
    "zh": {"before": "之前", "after": "之後", "flat": "（持平）", "worse": "較差", "better": "較好", "left": "前", "right": "後",
           "low": "低", "high": "高", "pick": "★ 建議", "yes": "是", "no": "否", "other": "其他／未分類", "sum": "合計"},
    "en": {"before": "Before", "after": "After", "flat": " (flat)", "worse": "Worse", "better": "Better", "left": "Before", "right": "After",
           "low": "Low", "high": "High", "pick": "★ Our pick", "yes": "Yes", "no": "No", "other": "Other / unknown", "sum": "Total"},
}

def L(st, key):
    lang = "zh" if str(st.get("lang", "zh")).lower().startswith("zh") else "en"
    return LABELS[lang][key]

class Pal:
    """Colours for diagrams, read from the style (works for light and dark themes)."""
    def __init__(self, st):
        t = st["tokens"]; c = st["chart"]; s = st["status"]
        self.ink, self.soft, self.mute = t["ink"], t["soft"], t["mute"]
        self.rule, self.card, self.ring = t["rule"], t["card"], t["card-ring"]
        self.hi, self.hi_bg, self.hi_text = c["highlight"], t["hi-bg"], t["hi-text"]
        self.context, self.strong = c["context"], c["strong"]
        self.good, self.warn, self.bad = t["good-text"], s["warning"], t["critical"]
        self.green, self.orange, self.paper = t["c-green"], t["c-orange"], t["paper"]
        self.on_accent = t.get("on-accent", "#fff")
        self.rough = bool(st.get("rough"))
        _HALO[0] = self.card

_uid = [0]
def _id():
    _uid[0] += 1
    return f"d{_uid[0]}"

def T(x, y, s, size=14, fill=None, anchor="start", weight=400, cls=""):
    c = f' class="{cls}"' if cls else ""
    if cls == "big":   # a halo in the card colour keeps big numbers clear of lines behind them
        c += f' paint-order="stroke" stroke="{_HALO[0]}" stroke-width="6" stroke-linejoin="round"' 
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}"{c}>{s}</text>')

def box(x, y, w, h, stroke, fill, sw=1.5, r=8, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'

def marker(mid, color):
    return (f'<marker id="{mid}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            f'<path d="M1 1 L9 5 L1 9" fill="none" stroke="{color}" stroke-width="1.8"/></marker>')

def svg(W, H, body, defs="", label=""):
    a = f' aria-label="{esc(label)}" role="img"' if label else ""
    return (f'<svg class="diagram" viewBox="0 0 {W:.0f} {H:.0f}" style="max-width:{W:.0f}px;overflow:visible"{a}>'
            f'{"<defs>"+defs+"</defs>" if defs else ""}{body}</svg>')

def icon_svg(icons, name, x, y, size, color, sw=2):
    body = icons.get(name) if name else None
    if not body:
        return ""
    return (f'<svg x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" data-icon="{esc(name)}">{body}</svg>')

def rough(p):
    return ' filter="url(#wobble)"' if p.rough else ""

def battery(x, y, pct, color, p, w=50):
    return (box(x, y, w, 20, p.ink, p.card, 1.8, 4) + f'<rect x="{x+w:.1f}" y="{y+6:.1f}" width="4" height="8" rx="1" fill="{p.ink}"/>'
            + f'<rect x="{x+3:.1f}" y="{y+3:.1f}" width="{max(2,(w-6)*pct/100):.1f}" height="14" rx="2" fill="{color}"/>')

# ---------------------------------------------------------------- route
def route(b, st, icons):
    """{"from":"台北","to":"嘉義","value":"465.6","unit":"公里","round_trip":true,"icon":"car",
        "start":{"pct":100,"label":"出發 100%"},"end":{"pct":10,"label":"回來剩 10%"},
        "bars":[{"label":"官方 WLTP","value":603,"display":"603"},{"label":"高速實測","value":517,"display":"517（85%）","highlight":true}]}"""
    p = Pal(st); W = 320; m = _id()
    o = [f'<g{rough(p)}>',
         f'<path d="M40 58 C100 10 220 10 280 58" fill="none" stroke="{p.hi}" stroke-width="2.6" marker-end="url(#{m})"/>']
    if b.get("round_trip", True):
        o.append(f'<path d="M280 72 C220 120 100 120 40 72" fill="none" stroke="{p.hi}" stroke-width="2.6" stroke-dasharray="7 5" marker-end="url(#{m})"/>')
    o.append("</g>")
    o += [f'<circle cx="33" cy="65" r="8" fill="{p.hi}"/><circle cx="287" cy="65" r="8" fill="{p.card}" stroke="{p.hi}" stroke-width="3"/>',
          T(4, 104, esc(fit(b.get("from", ""), 14, 120)), 14, p.ink, "start", 700), T(316, 104, esc(fit(b.get("to", ""), 14, 120)), 14, p.ink, "end", 700),
          icon_svg(icons, b.get("icon", "car"), 142, 2, 36, p.ink, 1.8)]
    vz = fit_size(str(b.get("value", "")), 190, (46, 34, 18))
    o.append(T(160, 84 if vz == 46 else 78, f'{esc(b.get("value",""))}<tspan font-size="14" font-weight="700"> {esc(b.get("unit",""))}</tspan>', vz, p.hi, "middle", 700, "big"))
    y = 118
    if b.get("start") or b.get("end"):
        s, e = b.get("start", {}), b.get("end", {})
        endc = p.orange if e.get("pct", 100) <= 20 else p.green
        o += [battery(8, y, s.get("pct", 100), p.green, p), T(8, y + 40, esc(fit(s.get("label", ""), 14, 148)), 14, p.soft),
              battery(258, y, e.get("pct", 100), endc, p), T(312, y + 40, esc(fit(e.get("label", ""), 14, 148)), 14, endc, "end", 700)]
        y += 58
    bars = b.get("bars", [])
    if bars:
        lw = min(110, max(tw(d["label"], 14) for d in bars) + 8); vmax = max(d["value"] for d in bars) or 1
        dw = max(tw(d.get("display", d["value"]), 14) for d in bars) + 8; bw = W - lw - dw - 8
        for d in bars:
            hl = d.get("highlight"); w = max(2, bw * d["value"] / vmax)
            o += [T(lw - 6, y + 13, esc(fit(d["label"], 14, lw - 8)), 14, p.ink if hl else p.soft, "end", 700 if hl else 400),
                  f'<rect x="{lw:.1f}" y="{y+1:.1f}" width="{w:.1f}" height="15" rx="3" fill="{p.hi if hl else p.context}"/>',
                  T(lw + w + 6, y + 13, esc(d.get("display", d["value"])), 14, p.ink if hl else p.soft, "start", 700 if hl else 400)]
            y += 27
    return svg(W, y + 4, "".join(o), marker(m, p.hi), b.get("label", ""))

# ---------------------------------------------------------------- formula
def formula(b, st, icons):
    """{"terms":[{"icon":"battery-charging","value":"75.5","label":"度・充一次"},{"icon":"tag","value":"7 元","label":"每度・平日"}],
        "ops":["×"],"result":{"icon":"wallet","value":"≈530","label":"元・來回"},
        "aside":{"icon":"utensils","text":"≈ 一頓晚餐"},
        "scale":{"title":"每度電價看時段","min":5,"max":14,"points":[{"value":6,"label":"離峰 6","kind":"good"},{"value":7,"label":"平日 7","kind":"hi"},{"value":13,"label":"尖峰 13 元","kind":"bad"}]}}"""
    p = Pal(st); terms = b["terms"] + [b["result"]]; n = len(terms); W = 320
    opw = 22; tile = (W - opw * (n - 1)) / n; tile = min(tile, 110); total = tile * n + opw * (n - 1); x0 = (W - total) / 2
    ops = b.get("ops", ["×"] * (n - 2)) + ["="]
    o = []; x = x0
    for i, t in enumerate(terms):
        res = i == n - 1; c = p.hi if res else p.soft; bg = p.hi_bg if res else p.card
        o.append(box(x, 4, tile, 100, c if res else p.ring, bg, 2 if res else 1.5, 10))
        o.append(icon_svg(icons, t.get("icon"), x + tile / 2 - 14, 12, 28, c))
        val = str(t.get("value", "")); vs = fit_size(val, tile - 8, (18, 14))
        o.append(T(x + tile / 2, 70, esc(fit(val, vs, tile - 6)), vs, p.hi if res else p.ink, "middle", 700))
        for k, ln in enumerate(wrap(t.get("label", ""), 14, tile - 8, 1)):
            o.append(T(x + tile / 2, 92 + k * 16, esc(ln), 14, p.soft, "middle"))
        x += tile
        if i < n - 1:
            o.append(T(x + opw / 2, 62, esc(ops[i] if i < len(ops) else "×"), 18, p.soft, "middle")); x += opw
    y = 112
    if b.get("aside"):
        a = b["aside"]; aw = tw(a.get("text", ""), 14) + 26
        o += [icon_svg(icons, a.get("icon"), W - aw, y + 2, 20, p.hi), T(W, y + 17, esc(a.get("text", "")), 14, p.hi, "end", 700)]
        y += 32
    sc = b.get("scale")
    if sc:
        lo, hi_ = sc.get("min"), sc.get("max"); pts = sc["points"]
        lo = lo if lo is not None else min(q["value"] for q in pts) - 1
        hi_ = hi_ if hi_ is not None else max(q["value"] for q in pts) + 1
        two_rows = len(pts) > 1 and min(abs(a["value"] - b_["value"]) for a, b_ in zip(pts, pts[1:])) / ((hi_ - lo) or 1) * (W - 24) < 70
        o.append(T(2, y + 14, esc(fit(sc.get("title", ""), 14, W - 4)), 14, p.soft)); y += 34 + (22 if two_rows else 0)
        o.append(f'<line x1="12" y1="{y}" x2="{W-12}" y2="{y}" stroke="{p.context}" stroke-width="6" stroke-linecap="round"/>')
        xs = [12 + (q["value"] - lo) / ((hi_ - lo) or 1) * (W - 24) for q in pts]
        # place labels on two rows (below, then above) so neighbours never overlap
        placed = {0: [], 1: []}; rows_used = 0
        for q, xq in zip(pts, xs):
            col = {"good": p.good, "bad": p.bad, "hi": p.hi}.get(q.get("kind"), p.soft)
            lab = fit(q.get("label", ""), 14, W / 2); w_ = tw(lab, 14)
            lx = min(max(xq, w_ / 2 + 2), W - w_ / 2 - 2)
            row = next((r for r in (0, 1) if all(abs(lx - px) > (w_ + pw) / 2 + 6 for px, pw in placed[r])), None)
            if row is None:   # both rows taken here: push right of the last label on the bottom row
                row = 0; lx = min(max(px + (pw + w_) / 2 + 6 for px, pw in placed[0]), W - w_ / 2 - 2)
            placed[row].append((lx, w_)); rows_used = max(rows_used, row)
            ly = y + 26 if row == 0 else y - 14
            o.append(f'<circle cx="{xq:.1f}" cy="{y}" r="7" fill="{col}"/>' + T(lx, ly, esc(lab), 14, col, "middle", 700))
        if rows_used:
            o = [x.replace(f'y="{y - 14:.1f}"', f'y="{y - 14:.1f}"') for x in o]
        y += 34
    return svg(W, y + 2, "".join(o), "", b.get("label", ""))

# ---------------------------------------------------------------- progress
def progress(b, st, icons):
    """{"current":115,"target":125,"current_label":"現在","unit":"站","target_label":"2026 年底目標 125 站","sub":"700 支超充電座",
        "then":{"from_icon":"timer","from_label":"充 5 分鐘","to_icon":"route","value":"120","unit":"公里","prefix":"多跑","sub":"高速路上補電很快"}}"""
    p = Pal(st); W = 320; L, R = 12, W - 12
    frac = max(0, min(1, b["current"] / (b.get("target") or b["current"] or 1))); x1 = L + (R - L) * frac
    o = [T(R, 16, esc(b.get("target_label", "")), 14, p.mute, "end"),
         f'<line x1="{L}" y1="38" x2="{R}" y2="38" stroke="{p.context}" stroke-width="14" stroke-linecap="round" stroke-dasharray="2 6"/>',
         f'<line x1="{L}" y1="38" x2="{x1:.1f}" y2="38" stroke="{p.hi}" stroke-width="14" stroke-linecap="round"/>',
         f'<circle cx="{x1:.1f}" cy="38" r="10" fill="{p.card}" stroke="{p.hi}" stroke-width="4"/>']
    val = f'{esc(b.get("current_label",""))} <tspan font-size="46" font-weight="700" fill="{p.hi}" class="big">{esc(b.get("current_display", b["current"]))}</tspan> {esc(b.get("unit",""))}'
    vx = min(max(x1 + 10, tw(re.sub(r"<[^>]+>", "", val), 14) + 60), R)
    o.append(T(vx, 98, val, 14, p.ink, "end"))
    y = 104
    if b.get("sub"):
        o.append(T(vx, 126, esc(b["sub"]), 14, p.soft, "end")); y = 132
    th = b.get("then")
    if th:
        y += 8; m = _id()
        o += [box(2, y, W - 4, 92, p.ring, p.card, 1.5, 10),
              icon_svg(icons, th.get("from_icon"), 16, y + 12, 36, p.green), T(34, y + 76, esc(th.get("from_label", "")), 14, p.green, "middle", 700),
              f'<line x1="62" y1="{y+30}" x2="112" y2="{y+30}" stroke="{p.green}" stroke-width="2.4" marker-end="url(#{m})"/>',
              icon_svg(icons, th.get("to_icon"), 120, y + 12, 36, p.green),
              T(166, y + 38, f'{esc(th.get("prefix",""))} <tspan font-size="18" font-weight="700">{esc(th.get("value",""))}</tspan> {esc(th.get("unit",""))}', 14, p.green, "start", 700)]
        if th.get("sub"):
            for k, ln in enumerate(wrap(th["sub"], 14, W - 176, 2)):
                o.append(T(166, y + 62 + k * 18, esc(ln), 14, p.soft))
        y += 92
        return svg(W, y + 4, "".join(o), marker(m, p.green), b.get("label", ""))
    return svg(W, y + 4, "".join(o), "", b.get("label", ""))

# ---------------------------------------------------------------- gauge
def gauge(b, st, icons):
    """{"value":94,"max":100,"label":"Metacritic 媒體評分","badge":{"icon":"crown","title":"第 1 名","sub":"2026 年所有新作（上線時）"}}"""
    p = Pal(st); W = 360; cx, cy, r = 108, 112, 82
    frac = max(0, min(1, b["value"] / (b.get("max") or 100)))
    def arc(a0, a1):
        P = lambda a: (cx + r * math.cos(math.radians(a)), cy - r * math.sin(math.radians(a)))
        (x0, y0), (x1, y1) = P(a0), P(a1)
        return f'M{x0:.1f} {y0:.1f} A{r} {r} 0 {1 if abs(a1 - a0) > 180 else 0} 1 {x1:.1f} {y1:.1f}'
    o = [f'<path d="{arc(200, -20)}" fill="none" stroke="{p.context}" stroke-width="15" stroke-linecap="round"/>',
         f'<path d="{arc(200, 200 - 220 * frac)}" fill="none" stroke="{p.hi}" stroke-width="15" stroke-linecap="round"/>',
         T(cx, cy + 10, esc(b.get("display", b["value"])), 46, p.hi, "middle", 700, "big"),
         T(cx, cy + 40, f'/ {esc(b.get("max", 100))}', 14, p.mute, "middle")]
    for k, ln in enumerate(wrap(b.get("label", ""), 14, 200, 2)):
        o.append(T(cx, 214 + k * 18, esc(ln), 14, p.soft, "middle"))
    bd = b.get("badge")
    if bd:
        sub = wrap(bd.get("sub", ""), 14, 118, 3); bh = 112 + 18 * len(sub)
        o += [box(222, 36, 134, bh, p.hi, p.hi_bg, 1.5, 8), icon_svg(icons, bd.get("icon", "award"), 271, 50, 36, p.hi),
              T(289, 118, esc(bd.get("title", "")), 18, p.hi, "middle", 700)]
        for k, ln in enumerate(sub):
            o.append(T(289, 142 + k * 18, esc(ln), 14, p.soft, "middle"))
    return svg(W, 236, "".join(o), "", b.get("aria", ""))

# ---------------------------------------------------------------- compare
def compare(b, st, icons):
    """{"question":"你最常怎麼開？","badge":"★ 最推","options":[
          {"name":"後驅","price":"189.99 萬","why":"市區通勤・預算優先","specs":[{"icon":"map","text":"534 公里"},{"icon":"gauge","text":"0–100 5.9 秒"}]},
          {"name":"長續航","price":"229.99 萬","why":"常跑長途・全家出遊","specs":[...],"recommended":true}, ...]}"""
    p = Pal(st); opts = b["options"]; n = len(opts); W = 560 if n == 3 else 420
    gap = 16; ow = (W - gap * (n - 1)) / n; mk, mkh = _id(), _id()
    q = b.get("question", ""); ql = wrap(q, 14, W - 60, 2); qw = max(180, max(tw(x, 14) for x in ql) + 40); qh = 18 + 18 * len(ql)
    o = []; top = 0
    if q:
        o.append(box(W / 2 - qw / 2, 2, qw, qh, p.ink, p.card, 1.8, min(18, qh / 2)))
        for k, ln in enumerate(ql):
            o.append(T(W / 2, 2 + qh / 2 + 5 - 9 * (len(ql) - 1) + k * 18, esc(ln), 14, p.ink, "middle", 700))
        top = qh + 2
    oy = top + 56
    whyl = max(len(wrap(x.get("why", ""), 14, ow - 16, 2)) for x in opts)
    nspec = max(len(x.get("specs", [])) for x in opts)
    oh = 26 + whyl * 18 + 12 + 26 + 24 + nspec * 22 + 10
    for i, x in enumerate(opts):
        ox = i * (ow + gap); cxo = ox + ow / 2; hl = x.get("recommended"); c = p.hi if hl else p.soft
        if q:
            o.append(f'<path d="M{W/2:.1f} {top} C{W/2:.1f} {top+26} {cxo:.1f} {top+18} {cxo:.1f} {oy-8}" fill="none" stroke="{c}" '
                     f'stroke-width="{2.4 if hl else 1.6}" marker-end="url(#{mkh if hl else mk})"/>')
        o.append(box(ox, oy, ow, oh, p.hi if hl else p.ring, p.hi_bg if hl else p.card, 2.4 if hl else 1.5, 10))
        yy = oy + 28
        for ln in wrap(x.get("why", ""), 14, ow - 16, 2):
            o.append(T(cxo, yy, esc(ln), 14, p.soft, "middle")); yy += 18
        o.append(f'<line x1="{ox+12:.1f}" y1="{yy-4:.1f}" x2="{ox+ow-12:.1f}" y2="{yy-4:.1f}" stroke="{p.rule}" stroke-width="1"/>')
        yy += 22
        nz = fit_size(x.get("name", ""), ow - 16, (18, 14))
        o.append(T(cxo, yy, esc(fit(x.get("name", ""), nz, ow - 12)), nz, p.hi if hl else p.ink, "middle", 700)); yy += 24
        o.append(T(cxo, yy, esc(x.get("price", "")), 14, p.ink, "middle", 700)); yy += 22
        for sp in x.get("specs", []):
            txt = fit(sp.get("text", ""), 14, ow - 16 - (20 if sp.get("icon") else 0))
            sw_ = tw(txt, 14) + (20 if sp.get("icon") else 0); sx = cxo - sw_ / 2
            o.append(icon_svg(icons, sp.get("icon"), sx, yy - 13, 15, p.soft) + T(sx + (20 if sp.get("icon") else 0), yy, esc(txt), 14, p.soft))
            yy += 22
        if hl and b.get("badge", L(st, "pick")):
            bt = b.get("badge", L(st, "pick")); bw = tw(bt, 14) + 22
            o.append(box(cxo - bw / 2, oy - 11, bw, 22, p.hi, p.hi, 0, 11) + T(cxo, oy + 5, esc(bt), 14, p.on_accent, "middle", 700))
    defs = marker(mk, p.soft) + marker(mkh, p.hi)
    return svg(W, oy + oh + 4, "".join(o), defs, b.get("label", ""))

# ---------------------------------------------------------------- decision
def decision(b, st, icons):
    """{"icon":"house","question":["家裡或公司","能裝充電樁嗎？"],"yes":{"label":"能","text":"✓ 可以買，後驅就夠"},
        "no":{"label":"不能","text":"先問管委會；不能裝，就查附近超充站再決定"}}"""
    p = Pal(st); W = 420; myes, mno = _id(), _id()
    ql = [fit(x, 14, 150) for x in b["question"]] if isinstance(b["question"], list) else wrap(b["question"], 14, 140, 2)
    yes, no = b.get("yes", {}), b.get("no", {})
    yl = wrap(yes.get("text", ""), 14, 112, 2)
    o = [f'<g{rough(p)}><path d="M140 4 L250 40 L140 76 L30 40 Z" fill="{p.card}" stroke="{p.ink}" stroke-width="2"/></g>',
         icon_svg(icons, b.get("icon"), 0, 27, 24, p.ink)]
    for k, ln in enumerate(ql[:2]):
        o.append(T(140, 36 + k * 18 - (9 if len(ql) == 1 else 0), esc(ln), 14, p.ink, "middle", 700))
    o += [f'<line x1="250" y1="40" x2="282" y2="40" stroke="{p.good}" stroke-width="2" marker-end="url(#{myes})"/>',
          T(266, 30, esc(yes.get("label", L(st, "yes"))), 14, p.good, "middle", 700),
          box(288, 40 - (13 + 9 * len(yl)), 130, 26 + 18 * len(yl), p.good, p.card, 1.4, 8)]
    for k, ln in enumerate(yl):
        o.append(T(353, 40 - 9 * (len(yl) - 1) + k * 18 + 5, esc(ln), 14, p.good, "middle", 700))
    nl = wrap(no.get("text", ""), 14, 380, 2); nh = 22 + 18 * len(nl)
    o += [f'<line x1="140" y1="76" x2="140" y2="102" stroke="{p.orange}" stroke-width="2" marker-end="url(#{mno})"/>',
          T(152, 94, esc(no.get("label", L(st, "no"))), 14, p.orange, "start", 700),
          box(16, 106, 400, nh, p.orange, p.card, 1.4, 8)]
    for k, ln in enumerate(nl):
        o.append(T(216, 106 + 26 + k * 18, esc(ln), 14, p.ink, "middle", 700))
    return svg(W, 106 + nh + 4, "".join(o), marker(myes, p.good) + marker(mno, p.orange), b.get("label", ""))

# ---------------------------------------------------------------- transform
def transform(b, st, icons):
    """{"from":{"icon":"users","value":"6,500 萬套","label":"累計銷量的玩家","sub":"帶著原本模組"},"arrow":"直接升級",
        "to":{"icon":"puzzle","value":"450+","label":"個模組首日相容","sub":"重製版"},"note":"玩家不用在新畫面和舊模組之間二選一"}"""
    p = Pal(st); W = 360; m = _id(); f, t_ = b["from"], b["to"]; bw = 144
    nl = max(len(wrap(d.get("label", ""), 14, bw - 12, 2)) for d in (f, t_)); bh = 154 + 18 * (nl - 1)
    def card_(x, d, hl):
        c = p.hi if hl else p.soft
        r = [box(x, 6, bw, bh, p.hi if hl else p.ring, p.hi_bg if hl else p.card, 1.8 if hl else 1.5, 8),
             icon_svg(icons, d.get("icon"), x + bw / 2 - 20, 18, 40, c)]
        val = str(d.get("value", "")); big = hl and tw(val, 46) < bw - 10
        r.append(T(x + bw / 2, 98 if big else 92, esc(val), 46 if big else 18, p.hi if hl else p.ink, "middle", 700, "big" if big else ""))
        lines = wrap(d.get("label", ""), 14, bw - 12, 2)
        for k, ln in enumerate(lines):
            r.append(T(x + bw / 2, 128 + k * 18, esc(ln), 14, p.soft, "middle"))
        if d.get("sub"):
            r.append(T(x + bw / 2, 128 + 18 * nl, esc(d["sub"]), 14, p.mute, "middle"))
        return "".join(r)
    o = [card_(2, f, False), card_(W - bw - 2, t_, True),
         f'<line x1="{bw+10}" y1="82" x2="{W-bw-10}" y2="82" stroke="{p.hi}" stroke-width="2.4" marker-end="url(#{m})"/>',
         T(W / 2, 70, esc(b.get("arrow", "")), 14, p.hi, "middle", 700)]
    y = bh + 12
    if b.get("note"):
        for k, ln in enumerate(wrap(b["note"], 14, W - 8, 2)):
            o.append(T(W / 2, bh + 36 + k * 18, esc(ln), 14, p.soft, "middle")); y = bh + 42 + k * 18
    return svg(W, y + 4, "".join(o), marker(m, p.hi), b.get("label", ""))

# ---------------------------------------------------------------- flowsteps
def flowsteps(b, st, icons):
    """{"items":[{"icon":"calendar","title":"到官網預約試駕","sub":"親自坐坐後座、打開後車廂"}, ...]}"""
    items = b["items"]
    need = max([tw(it.get("title", ""), 18) + 96 + (tw(it.get("owner", ""), 14) + 12 if it.get("owner") else 0) for it in items] + [420])
    p = Pal(st); W = int(b.get("width") or min(560, need)); o = []; y = 6; rows = []   # widen (up to 560) before wrapping titles
    for it in items:
        sub = wrap(it.get("sub", ""), 14, W - 96, 2) if it.get("sub") else []
        ow_ = tw(it.get("owner", ""), 14) + 12 if it.get("owner") else 0
        nt = len(wrap(it.get("title", ""), 18, W - 92 - ow_, 2))
        rows.append((it, sub, 30 + 20 * len(sub) + 22 + 22 * (nt - 1)))
    total = sum(r[2] for r in rows)
    o.append(f'<line x1="22" y1="30" x2="22" y2="{total-rows[-1][2]+30:.1f}" stroke="{p.rule}" stroke-width="2"/>')
    for i, (it, sub, h) in enumerate(rows):
        o.append(f'<circle cx="22" cy="{y+20:.1f}" r="14" fill="{p.green}"/>' + T(22, y + 25, str(i + 1), 14, p.on_accent, "middle", 700))
        o.append(icon_svg(icons, it.get("icon"), 52, y + 8, 24, p.green))
        ow_ = tw(it.get("owner", ""), 14) + 12 if it.get("owner") else 0
        tl = wrap(it.get("title", ""), 18, W - 92 - ow_, 2)
        for k, ln in enumerate(tl):
            o.append(T(88, y + 26 + k * 22, esc(ln), 18, p.ink, "start", 700))
        y += 22 * (len(tl) - 1)
        for k, ln in enumerate(sub):
            o.append(T(88, y + 48 + k * 20, esc(ln), 14, p.soft))
        if it.get("owner"):
            o.append(T(W - 4, y + 26, esc(it["owner"]), 14, p.green, "end", 700))
        y += h
        if i < len(rows) - 1:
            o.append(f'<line x1="52" y1="{y-8:.1f}" x2="{W-4}" y2="{y-8:.1f}" stroke="{p.rule}" stroke-width="1"/>')
    return svg(W, y, "".join(o), "", b.get("label", ""))


# ---------------------------------------------------------------- report charts
def _mix(a, b, t):
    """Blend two #rrggbb colours (t=0 -> a, t=1 -> b)."""
    a = a.lstrip("#")[:6]; b = b.lstrip("#")[:6]
    if len(a) != 6 or len(b) != 6:
        return "#" + b if len(b) == 6 else "#888888"
    ca = [int(a[i:i+2], 16) for i in (0, 2, 4)]; cb = [int(b[i:i+2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))

def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0

def _fmt(v, d=None):
    if d is not None:
        return str(d)
    v = float(v)
    if v == int(v) or abs(v) >= 100:
        return f"{v:,.0f}"
    if abs(v) >= 1:
        return f"{v:,.1f}"
    return f"{v:.2g}"

def _better(delta, higher_is_better=True):
    return (delta >= 0) == bool(higher_is_better)

def stattile(b, st, icons):
    """{"value":"92%","label":"Steam 近期好評率","delta":"+24 pt","vs":"vs 首日 68%","good":true,
        "spark":[68,66,65,70,78,85,92],"spark_label":["9/29","10/20"]}"""
    p = Pal(st); W = 320
    val = str(b.get("value", "")); vz = fit_size(val, 190, (46, 34, 18))
    good = b.get("good", True); dc = p.good if good else p.bad; arrow = "▲" if good == (not b.get("down", False)) else "▼"
    if "arrow" in b:
        arrow = b["arrow"]
    o = [T(2, 46 if vz == 46 else 38, esc(val), vz, p.hi, "start", 700, "big")]
    o.append(T(2, 74, esc(fit(b.get("label", ""), 14, 200)), 14, p.soft))
    if b.get("delta"):
        o.append(T(2, 100, f'<tspan fill="{dc}" font-weight="700">{arrow} {esc(b["delta"])}</tspan> {esc(fit(b.get("vs", ""), 14, 150))}', 14, p.soft))
    sp = [_num(x) for x in b.get("spark", [])]
    if len(sp) >= 2:
        x0, x1, y0, y1 = 212, W - 6, 14, 70
        lo, hi = min(sp), max(sp); rng = (hi - lo) or 1
        pts = [(x0 + (x1 - x0) * i / (len(sp) - 1), y1 - (v - lo) / rng * (y1 - y0)) for i, v in enumerate(sp)]
        d = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f} {y:.1f}" for i, (x, y) in enumerate(pts))
        area = d + f" L{pts[-1][0]:.1f} {y1} L{pts[0][0]:.1f} {y1} Z"
        o += [f'<path d="{area}" fill="{p.hi}" fill-opacity=".12"/>',
              f'<path d="{d}" fill="none" stroke="{p.hi}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>',
              f'<circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="4" fill="{p.hi}" stroke="{p.card}" stroke-width="2"/>']
        lab = b.get("spark_label") or []
        if len(lab) == 2:
            o += [T(x0, y1 + 18, esc(lab[0]), 14, p.mute, "start"), T(x1, y1 + 18, esc(lab[1]), 14, p.mute, "end")]
    return svg(W, 108, "".join(o), "", b.get("aria", ""))

def bullet(b, st, icons):
    """{"rows":[{"label":"首次回覆","actual":2.6,"target":3,"compare":6.5,"unit":"小時","display":"2.6 小時",
        "ranges":[3,5,8]}], "higher_is_better":false, "max":8, "legend":["實際","目標","改善前"]}"""
    p = Pal(st); rows = b["rows"]; W = 380
    lw = min(120, max(tw(r.get("label", ""), 14) for r in rows) + 10)
    dw = max(tw(r.get("display", _fmt(r.get("actual", 0))), 18) for r in rows) + 34
    bw = W - lw - dw - 6; hb = b.get("higher_is_better", True)
    o = []; y = 6
    for r in rows:
        mx = _num(b.get("max", r.get("max"))) or max(_num(r.get("actual")), _num(r.get("target")), _num(r.get("compare")), *[_num(x) for x in r.get("ranges", [])]) * 1.08 or 1
        X = lambda v: lw + bw * max(0, min(1, _num(v) / mx))
        rg = r.get("ranges", [])
        if rg:
            prev = lw; steps = [0.16, 0.10, 0.05] if hb else [0.05, 0.10, 0.16]
            for i, v in enumerate(rg[:3]):
                o.append(f'<rect x="{prev:.1f}" y="{y}" width="{max(0, X(v) - prev):.1f}" height="24" fill="{p.ink}" fill-opacity="{steps[i] if i < 3 else .05}"/>')
                prev = X(v)
        else:
            o.append(f'<rect x="{lw}" y="{y}" width="{bw:.1f}" height="24" fill="{p.context}" fill-opacity=".35"/>')
        if r.get("target") is None:
            ok = True
        else:
            a_, t_ = _num(r.get("actual", 0)), _num(r.get("target"))
            ok = a_ >= t_ if hb else a_ <= t_
        o.append(f'<rect x="{lw}" y="{y+7}" width="{max(2, X(r.get("actual", 0)) - lw):.1f}" height="10" fill="{p.hi}"/>')
        if r.get("compare") is not None:
            cx = X(r["compare"]); o.append(f'<circle cx="{cx:.1f}" cy="{y+12}" r="4.5" fill="{p.card}" stroke="{p.soft}" stroke-width="2"/>')
        if r.get("target") is not None:
            tx = X(r["target"]); o.append(f'<line x1="{tx:.1f}" y1="{y+1}" x2="{tx:.1f}" y2="{y+23}" stroke="{p.ink}" stroke-width="3"/>')
        o.append(T(lw - 8, y + 17, esc(fit(r.get("label", ""), 14, lw - 10)), 14, p.ink, "end", 700))
        mark = "✓ " if ok else "! "
        o.append(T(W - dw + 8, y + 18, f'<tspan fill="{p.good if ok else p.bad}">{mark}</tspan>{esc(r.get("display", _fmt(r.get("actual", 0))))}', 18 if len(rows) <= 3 else 14, p.ink, "start", 700))
        if r.get("note"):
            o.append(T(lw, y + 40, esc(fit(r["note"], 14, bw)), 14, p.mute)); y += 18
        y += 38
    lg = b.get("legend")
    if lg:
        x = lw
        items = [("bar", lg[0])] + ([("tick", lg[1])] if len(lg) > 1 else []) + ([("dot", lg[2])] if len(lg) > 2 else [])
        for kind, txt in items:
            if kind == "bar": o.append(f'<rect x="{x}" y="{y+2}" width="16" height="8" fill="{p.hi}"/>')
            elif kind == "tick": o.append(f'<line x1="{x+8}" y1="{y-1}" x2="{x+8}" y2="{y+13}" stroke="{p.ink}" stroke-width="3"/>')
            else: o.append(f'<circle cx="{x+8}" cy="{y+6}" r="4.5" fill="{p.card}" stroke="{p.soft}" stroke-width="2"/>')
            o.append(T(x + 22, y + 11, esc(txt), 14, p.soft)); x += 30 + tw(txt, 14) + 14
        y += 22
    return svg(W, y + 2, "".join(o), "", b.get("aria", ""))

def dumbbell(b, st, icons):
    """{"rows":[{"label":"首次回覆","before":6.5,"after":2.6,"before_display":"6.5","after_display":"2.6 小時"}],
        "higher_is_better":false, "legend":["改善前","改善後"]}"""
    p = Pal(st); rows = b["rows"]; W = 380; hb = b.get("higher_is_better", True)
    lw = min(132, max(tw(r.get("label", ""), 14) for r in rows) + 10)
    vals = [_num(v) for r in rows for v in (r.get("before"), r.get("after"))]
    lo = min(0, min(vals)) if b.get("zero", True) else min(vals); hi = max(vals) or 1
    pad = 70; x0, x1 = lw + 8, W - pad
    X = lambda v: x0 + (x1 - x0) * (_num(v) - lo) / ((hi - lo) or 1)
    o = []; y = 22
    lg = b.get("legend", [L(st, "before"), L(st, "after")])
    o += [f'<circle cx="{x0+6}" cy="8" r="5" fill="{p.card}" stroke="{p.soft}" stroke-width="2"/>', T(x0 + 16, 13, esc(lg[0]), 14, p.soft),
          f'<circle cx="{x0+36+tw(lg[0],14)}" cy="8" r="6" fill="{p.hi}"/>', T(x0 + 46 + tw(lg[0], 14), 13, esc(lg[1]), 14, p.soft)]
    y = 34
    for r in rows:
        bx, ax = X(r.get("before")), X(r.get("after"))
        good = _better(_num(r.get("after")) - _num(r.get("before")), hb)
        lc = p.hi if good else p.bad
        o.append(f'<line x1="{lw}" y1="{y}" x2="{W-4}" y2="{y}" stroke="{p.rule}" stroke-width="1"/>')
        o.append(f'<line x1="{bx:.1f}" y1="{y}" x2="{ax:.1f}" y2="{y}" stroke="{lc}" stroke-width="4" stroke-opacity=".45" stroke-linecap="round"/>')
        o.append(f'<circle cx="{bx:.1f}" cy="{y}" r="6" fill="{p.card}" stroke="{p.soft}" stroke-width="2"/>')
        o.append(f'<circle cx="{ax:.1f}" cy="{y}" r="7" fill="{lc}" stroke="{p.card}" stroke-width="2"/>')
        o.append(T(lw - 8, y + 5, esc(fit(r.get("label", ""), 14, lw - 10)), 14, p.ink, "end", 700))
        bd = r.get("before_display", _fmt(r.get("before"))); ad = r.get("after_display", _fmt(r.get("after")))
        left, right = (bx, ax) if bx <= ax else (ax, bx)
        lt, rt = (bd, ad) if bx <= ax else (ad, bd)
        if abs(ax - bx) < 4:
            o.append(T(ax + 11, y + 5, esc(ad) + f'<tspan fill="{p.mute}" font-weight="400" font-size="14">{L(st, "flat")}</tspan>', 18, p.ink, "start", 700))
        else:
            o.append(T(left - 11, y + 5, esc(lt), 14, p.soft if lt == bd else p.ink, "end", 400 if lt == bd else 700))
            o.append(T(right + 11, y + 5, esc(rt), 14 if rt == bd else 18, p.soft if rt == bd else lc, "start", 400 if rt == bd else 700))
        y += 36
    return svg(W, y - 12, "".join(o), "", b.get("aria", ""))

def slope(b, st, icons):
    """{"left":"改善前","right":"改善後","items":[{"label":"首次回覆","before":6.5,"after":2.6,"unit":"小時","highlight":true}],
        "higher_is_better":false}"""
    p = Pal(st); W = 380; items = b["items"][:6]; hb = b.get("higher_is_better", True)
    vals = [_num(v) for it in items for v in (it.get("before"), it.get("after"))]
    lo, hi = min(vals), max(vals); rng = (hi - lo) or 1
    xl, xr, yt, yb = 130, W - 110, 34, 34 + max(110, 34 * len(items))
    Y = lambda v: yb - (_num(v) - lo) / rng * (yb - yt)
    o = [T(xl, 16, esc(b.get("left", L(st, "left"))), 14, p.mute, "middle", 700), T(xr, 16, esc(b.get("right", L(st, "right"))), 14, p.mute, "middle", 700),
         f'<line x1="{xl}" y1="{yt-8}" x2="{xl}" y2="{yb+8}" stroke="{p.rule}"/>', f'<line x1="{xr}" y1="{yt-8}" x2="{xr}" y2="{yb+8}" stroke="{p.rule}"/>']
    # spread labels that would collide
    def spread(ys, gap=18):
        order = sorted(range(len(ys)), key=lambda i: ys[i]); out = list(ys)
        for k in range(1, len(order)):
            a, c = order[k - 1], order[k]
            if out[c] - out[a] < gap: out[c] = out[a] + gap
        return out
    ly = spread([Y(it.get("before")) for it in items]); ry = spread([Y(it.get("after")) for it in items], 22)
    for i, it in enumerate(items):
        hl = it.get("highlight") or len(items) == 1
        good = _better(_num(it.get("after")) - _num(it.get("before")), hb)
        c = (p.hi if good else p.bad) if hl else p.context
        y1, y2 = Y(it.get("before")), Y(it.get("after"))
        o.append(f'<line x1="{xl}" y1="{y1:.1f}" x2="{xr}" y2="{y2:.1f}" stroke="{c}" stroke-width="{3 if hl else 2}"/>')
        o += [f'<circle cx="{xl}" cy="{y1:.1f}" r="5" fill="{c}"/>', f'<circle cx="{xr}" cy="{y2:.1f}" r="{6 if hl else 5}" fill="{c}"/>']
        u = it.get("unit", "")
        dec = max([len(str(v).split(".")[1]) if "." in str(v) else 0 for x in items for v in (x.get("before"), x.get("after"))] + [0])
        fmt = lambda v: f"{_num(v):,.{min(dec,2)}f}"
        it = {**it, "before_display": it.get("before_display", fmt(it.get("before"))), "after_display": it.get("after_display", fmt(it.get("after")))}
        o.append(T(xl - 10, ly[i] + 5, f'{esc(fit(it.get("label",""),14,82))} <tspan font-weight="700">{esc(it.get("before_display", _fmt(it.get("before"))))}</tspan>', 14, p.ink if hl else p.soft, "end"))
        o.append(T(xr + 10, ry[i] + 6, f'{esc(it.get("after_display", _fmt(it.get("after"))))}{esc(u)}', 18 if hl else 14, c if hl else p.soft, "start", 700))
    return svg(W, max(yb, max(ly + ry)) + 14, "".join(o), "", b.get("aria", ""))

def waterfall(b, st, icons):
    """{"start":{"label":"改善前","value":6.5},"steps":[{"label":"AI 草稿","value":-2.4},{"label":"分流","value":-1.0},
        {"label":"旺季量","value":+0.5}],"end":{"label":"改善後"},"unit":"小時","higher_is_better":false}"""
    p = Pal(st); W = int(b.get("width") or max(400, 74 * (len(b.get("steps", [])) + 2))); hb = b.get("higher_is_better", True)
    steps = b.get("steps", []); start = b["start"]; end = b.get("end", {"label": "結果"})
    cum = [_num(start["value"])]
    for s_ in steps: cum.append(cum[-1] + _num(s_["value"]))
    endv = _num(end["value"]) if end.get("value") is not None else cum[-1]
    if end.get("value") is not None:
        dec = max([len(str(x).split(".")[1]) if "." in str(x) else 0 for x in [start["value"], end["value"]] + [s_["value"] for s_ in steps]] + [0])
        if abs(cum[-1] - endv) > 10 ** -dec / 2 + 1e-9:
            raise ValueError(f"waterfall '{start.get('label','')}': start {start['value']} plus the steps = {round(cum[-1], dec + 1)}, "
                             f"but end is {end['value']}. Fix the numbers, or add the missing step (for example \"other\": {round(endv - cum[-1], dec)})")
    bars = [("total", start.get("label", ""), 0, cum[0], start.get("display"))]
    for i, s_ in enumerate(steps):
        bars.append(("step", s_.get("label", ""), cum[i], cum[i + 1], s_.get("display")))
    bars.append(("total", end.get("label", ""), 0, endv, end.get("display")))
    allv = [0] + cum + [endv]; lo, hi = min(allv), max(allv); rng = (hi - lo) or 1
    dec = max([len(str(x).split(".")[1]) if "." in str(x) else 0 for x in [start["value"]] + [s_["value"] for s_ in steps]] + [0])
    f_ = lambda v: f"{v:,.{dec}f}"
    n = len(bars); top, bot = 30, 168; slot = (W - 8) / n; bw = min(52, slot * 0.62)
    if lo < 0:
        bot -= 18   # room for labels under bars that go below zero
    Y = lambda v: bot - (v - lo) / rng * (bot - top)
    u = b.get("unit", "")
    o = [f'<line x1="4" y1="{Y(0):.1f}" x2="{W-4}" y2="{Y(0):.1f}" stroke="{p.rule}" stroke-width="1.5"/>']
    for i, (kind, lab, a, z, disp) in enumerate(bars):
        cx = 4 + slot * (i + .5); x = cx - bw / 2
        y1, y2 = Y(max(a, z)), Y(min(a, z))
        if kind == "total":
            last = i == n - 1; c = p.hi if last else p.context
            o.append(f'<rect x="{x:.1f}" y="{y1:.1f}" width="{bw:.1f}" height="{max(2, y2-y1):.1f}" rx="3" fill="{c}"/>')
            txt = disp or f_(z) + u
            ty = y1 - 7 if z >= 0 else y2 + 18
            o.append(T(cx, ty, esc(txt), 18 if last else 14, p.hi if last else p.ink, "middle", 700))
        else:
            d = z - a; good = _better(d, hb); c = p.good if good else p.bad
            o.append(f'<rect x="{x:.1f}" y="{y1:.1f}" width="{bw:.1f}" height="{max(2, y2-y1):.1f}" rx="2" fill="{c}" fill-opacity=".85"/>')
            txt = disp or (("+" if d > 0 else "−") + f_(abs(d)))
            ty = y1 - 7 if (d >= 0 or y1 - 7 > top - 4) else y2 + 18
            o.append(T(cx, ty, esc(txt), 14, c, "middle", 700))
        if i < n - 1:
            nxt = z if kind == "step" or i == 0 else z
            o.append(f'<line x1="{x+bw:.1f}" y1="{Y(z):.1f}" x2="{x+slot:.1f}" y2="{Y(z):.1f}" stroke="{p.mute}" stroke-width="1" stroke-dasharray="3 3"/>')
        for k, ln in enumerate(wrap(lab, 14, slot - 4, 2)):
            o.append(T(cx, bot + (38 if lo < 0 else 20) + k * 17, esc(ln), 14, p.ink if kind == "total" else p.soft, "middle", 700 if kind == "total" else 400))
    return svg(W, bot + 56, "".join(o), "", b.get("aria", ""))

def variance(b, st, icons):
    """{"title_left":"差距（相對目標）","rows":[{"label":"首次回覆","delta":-0.4,"display":"−0.4 小時"}],
        "higher_is_better":false}  right side = better, always"""
    p = Pal(st); rows = b["rows"]; W = 380; hb = b.get("higher_is_better", True)
    lw = min(120, max(tw(r.get("label", ""), 14) for r in rows) + 10)
    mx = max(abs(_num(r.get("delta"))) for r in rows) or 1
    dw = max(tw(r.get("display", _fmt(r.get("delta"))), 14) for r in rows) + 10
    half = (W - lw - 2 * dw) / 2; cx = lw + dw + half
    o = [T(cx - 6, 12, "← " + esc(b.get("worse", L(st, "worse"))), 14, p.mute, "end"), T(cx + 6, 12, esc(b.get("better", L(st, "better"))) + " →", 14, p.mute, "start")]
    y = 24
    for r in rows:
        d = _num(r.get("delta")); score = d if hb else -d; good = score >= 0
        w = half * abs(score) / mx; c = p.good if good else p.bad
        x = cx if good else cx - w
        o.append(f'<rect x="{x:.1f}" y="{y}" width="{max(2, w):.1f}" height="20" rx="3" fill="{c}" fill-opacity=".85"/>')
        disp = r.get("display", ("+" if d > 0 else "") + _fmt(d) if d != 0 else "0")
        o.append(T(cx + w + 6 if good else cx - w - 6, y + 15, esc(disp), 14, c, "start" if good else "end", 700))
        o.append(T(lw - 8, y + 15, esc(fit(r.get("label", ""), 14, lw - 10)), 14, p.ink, "end", 700))
        y += 30
    o.append(f'<line x1="{cx:.1f}" y1="20" x2="{cx:.1f}" y2="{y-6}" stroke="{p.ink}" stroke-width="1.5"/>')
    if b.get("baseline"):
        o.append(T(cx, y + 10, esc(b["baseline"]), 14, p.mute, "middle"))
        y += 18
    return svg(W, y, "".join(o), "", b.get("aria", ""))

def stacked(b, st, icons):
    """{"series":["AI 處理","真人處理"],"highlight":0,"percent":true,
        "rows":[{"label":"改善前","values":[0,100]},{"label":"改善後","values":[46,54]}]}"""
    p = Pal(st); W = 380; rows = b["rows"]; ser = b.get("series", []); hl = b.get("highlight", 0); pct = b.get("percent", True)
    lw = min(90, max(tw(r.get("label", ""), 14) for r in rows) + 10)
    tot_max = max(sum(_num(v) for v in r["values"]) for r in rows) or 1
    shades = [p.hi] + [_mix(p.context, p.card, k) for k in (0, .35, .6, .8)]
    def col(i):
        return p.hi if i == hl else shades[1 + (sorted([j for j in range(len(ser)) if j != hl]).index(i) % 4 if ser else 1)]
    o = []; x = 4
    for i, sname in enumerate(ser):
        nm = fit(sname, 14, (W - 8) / max(1, len(ser)) - 30)
        o.append(f'<rect x="{x}" y="2" width="12" height="12" rx="2" fill="{col(i)}"/>' + T(x + 18, 13, esc(nm), 14, p.soft))
        x += 34 + tw(nm, 14)
    y = 26; bw = W - lw - 4
    for r in rows:
        vals = [_num(v) for v in r["values"]]; tot = sum(vals) or 1
        gap = 0
        if pct and vals and sum(vals) and abs(sum(vals) - 100) > 0.5:
            import sys as _sys
            print(f"note: stacked row '{r.get('label','')}' adds up to {sum(vals):g}, not 100; drawn on a 100 scale with the rest shown as '{L(st, 'other')}'", file=_sys.stderr)
            gap = max(0, 100 - sum(vals)); tot = 100 if sum(vals) < 100 else sum(vals)
        scale = bw / (tot if pct else tot_max); xx = lw
        for i, v in enumerate(vals):
            w = v * scale
            if w <= 0: continue
            o.append(f'<rect x="{xx:.1f}" y="{y}" width="{max(0, w-2):.1f}" height="24" rx="3" fill="{col(i)}"/>')
            share = v / tot * 100
            lab = (f"{share:.0f}%" if not gap else f"{v:g}%") if pct else _fmt(v)
            if w > tw(lab, 14) + 10:
                o.append(T(xx + w / 2 - 1, y + 17, lab, 14, p.on_accent if i == hl else p.ink, "middle", 700 if i == hl else 400))
            xx += w
        if gap:
            w = gap * scale
            o.append(f'<rect x="{xx:.1f}" y="{y}" width="{max(0, w-2):.1f}" height="24" rx="3" fill="none" stroke="{p.mute}" stroke-dasharray="3 3"/>')
            if w > 40:
                o.append(T(xx + w / 2, y + 17, f"{gap:g}%", 14, p.mute, "middle"))
        o.append(T(lw - 8, y + 17, esc(fit(r.get("label", ""), 14, lw - 10)), 14, p.ink, "end", 700))
        y += 34
    return svg(W, y - 4, "".join(o), "", b.get("aria", ""))

def heatmap(b, st, icons):
    """{"cols":["週一",...],"rows":[{"label":"上午","values":[..]}],"unit":"件","higher_is_worse":true,
        "mark":"max","legend":["少","多"]}"""
    p = Pal(st); cols = b["cols"]; rows = b["rows"]
    lw = min(90, max(tw(r.get("label", ""), 14) for r in rows) + 10)
    if len(cols) > 9 or len(rows) > 6:
        import sys as _sys
        print(f"note: heatmap with {len(rows)}×{len(cols)} cells is dense for one page; consider grouping (≤ 6 rows × 9 columns)", file=_sys.stderr)
    W = max(320, lw + 44 * len(cols)); cw = (W - lw) / len(cols); ch = 30
    allv = [_num(v) for r in rows for v in r["values"]]; lo, hi = min(allv), max(allv); rng = (hi - lo) or 1
    o = []
    for j, c in enumerate(cols):
        o.append(T(lw + cw * (j + .5), 14, esc(fit(c, 14, cw - 4)), 14, p.mute, "middle"))
    mark = b.get("mark", "max"); mv = hi if mark == "max" else lo if mark == "min" else None
    y = 22; marked = False
    for r in rows:
        o.append(T(lw - 8, y + 20, esc(fit(r.get("label", ""), 14, lw - 10)), 14, p.ink, "end", 700))
        for j, v in enumerate(r["values"]):
            t = (_num(v) - lo) / rng
            fill = _mix(p.card, p.hi, .08 + .82 * t)
            x = lw + cw * j
            o.append(f'<rect x="{x+1:.1f}" y="{y+1}" width="{cw-2:.1f}" height="{ch-2}" rx="3" fill="{fill}"/>')
            if b.get("show_values", True):
                o.append(T(x + cw / 2, y + 20, esc(_fmt(v)), 14, p.on_accent if t > .55 else p.ink, "middle", 700 if t > .55 else 400))
            if mv is not None and not marked and _num(v) == mv:
                o.append(f'<rect x="{x+1:.1f}" y="{y+1}" width="{cw-2:.1f}" height="{ch-2}" rx="3" fill="none" stroke="{p.bad if b.get("higher_is_worse", True) == (mark == "max") else p.good}" stroke-width="2.5"/>')
                marked = True
        y += ch
    lg = b.get("legend", [L(st, "low"), L(st, "high")])
    gid = _id()
    o.append(f'<defs><linearGradient id="{gid}"><stop offset="0" stop-color="{_mix(p.card, p.hi, .08)}"/><stop offset="1" stop-color="{_mix(p.card, p.hi, .9)}"/></linearGradient></defs>')
    o += [T(lw, y + 22, esc(lg[0]), 14, p.mute), f'<rect x="{lw+tw(lg[0],14)+8:.1f}" y="{y+11}" width="90" height="12" rx="3" fill="url(#{gid})"/>',
          T(lw + tw(lg[0], 14) + 106, y + 22, esc(lg[1]) + ((f"（{esc(b['unit'])}）" if L(st, "low") == "低" else f" ({esc(b['unit'])})") if b.get("unit") else ""), 14, p.mute)]
    extra = 0
    lg_end = lw + tw(lg[0], 14) + 106 + tw(lg[1] + (f"（{b['unit']}）" if b.get("unit") else ""), 14)
    if b.get("mark_label"):
        ml = b["mark_label"]; mc = p.bad if b.get("higher_is_worse", True) else p.good
        if lg_end + 16 + tw(ml, 14) <= W:
            o.append(T(W - 2, y + 22, esc(ml), 14, mc, "end", 700))
        else:
            o.append(T(lw, y + 44, esc(ml), 14, mc, "start", 700)); extra = 22
    return svg(W, y + 30 + extra, "".join(o), "", b.get("aria", ""))

def seatmap(b, st, icons):
    """Top view of a vehicle: seats per row and where the luggage goes, drawn to scale.
    {"length_mm":4956,"width_mm":2073,"rows":[2,3,2],"folded":[2],"body":"suv",
     "cargo":{"value":"1,137","unit":"L","label":"5 人坐時"},"front":{"value":"","label":"前車廂"},
     "dims":"長 4.96 m・寬 2.07 m"}"""
    p = Pal(st); k = b.get("scale", 0.07)
    Lp = b.get("length_mm", 4700) * k; Wp = b.get("width_mm", 1900) * k
    rows = b.get("rows", [2, 3]); folded = set(b.get("folded", [])); n = len(rows)
    x0, y0 = 4, 4; W = Lp + 8; r = Wp * (0.2 if b.get("body", "suv") == "suv" else 0.34)
    o = [f'<rect x="{x0}" y="{y0}" width="{Lp:.1f}" height="{Wp:.1f}" rx="{r:.1f}" fill="{p.card}" stroke="{p.soft}" stroke-width="2"/>']
    ws = x0 + Lp * 0.70   # windscreen line
    o.append(f'<path d="M{ws:.1f} {y0+Wp*0.12:.1f} Q{ws+Lp*0.05:.1f} {y0+Wp/2:.1f} {ws:.1f} {y0+Wp*0.88:.1f}" fill="none" stroke="{p.mute}" stroke-width="1.5"/>')
    c0, c1 = x0 + Lp * 0.22, x0 + Lp * 0.68   # cabin, rear to front
    pitch = (c1 - c0) / n
    first_fold = min(folded) if folded else n
    cargo_end = c0 + pitch * (n - first_fold) if folded else c0
    cx0 = x0 + Lp * 0.05
    o.append(f'<rect x="{cx0:.1f}" y="{y0+Wp*0.14:.1f}" width="{cargo_end-cx0-4:.1f}" height="{Wp*0.72:.1f}" rx="6" fill="{p.hi_bg}" stroke="{p.hi}" stroke-width="1.5"/>')
    for i, cnt in enumerate(rows):   # row 0 = front
        rx = c1 - pitch * (i + 1); sz = min(pitch * 0.66, Wp * 0.72 / max(rows) * 0.9)
        for j in range(cnt):
            sy = y0 + Wp * 0.14 + (Wp * 0.72) * (j + .5) / cnt - sz / 2; sx = rx + (pitch - sz) / 2
            if i in folded:
                o.append(f'<rect x="{sx:.1f}" y="{sy:.1f}" width="{sz:.1f}" height="{sz:.1f}" rx="4" fill="none" stroke="{p.hi}" stroke-opacity=".45" stroke-width="1.2" stroke-dasharray="3 3"/>')
            else:
                o.append(f'<rect x="{sx:.1f}" y="{sy:.1f}" width="{sz:.1f}" height="{sz:.1f}" rx="4" fill="{p.context}"/>')
    cg = b.get("cargo")
    if cg:
        mx = (cx0 + cargo_end - 4) / 2; avail = cargo_end - cx0 - 10
        v = esc(str(cg.get("value", ""))) + (f'<tspan font-size="14"> {esc(cg.get("unit",""))}</tspan>' if cg.get("unit") else "")
        o.append(T(mx, y0 + Wp / 2 + 2, v, 18, p.hi_text, "middle", 700))
        if cg.get("label"):
            o.append(T(mx, y0 + Wp / 2 + 20, esc(fit(cg["label"], 14, avail)), 14, p.soft, "middle"))
    fr = b.get("front")
    if fr:
        fx0, fx1 = x0 + Lp * 0.78, x0 + Lp * 0.95
        o.append(f'<rect x="{fx0:.1f}" y="{y0+Wp*0.22:.1f}" width="{fx1-fx0:.1f}" height="{Wp*0.56:.1f}" rx="6" fill="{p.hi_bg}" stroke="{p.hi}" stroke-width="1.2" stroke-dasharray="4 3"/>')
        if fr.get("label"):
            o.append(T((fx0 + fx1) / 2, y0 + Wp / 2 + 5, esc(fit(fr["label"], 14, fx1 - fx0 + 20)), 14, p.soft, "middle"))
    H = y0 + Wp + 6
    if b.get("dims"):
        o.append(T(x0 + Lp / 2, H + 14, esc(b["dims"]), 14, p.mute, "middle")); H += 20
    return svg(W, H, "".join(o), "", b.get("aria", ""))


BLOCKS = {"route": route, "formula": formula, "progress": progress, "gauge": gauge, "compare": compare,
          "decision": decision, "transform": transform, "flowsteps": flowsteps,
          "stattile": stattile, "bullet": bullet, "dumbbell": dumbbell, "slope": slope, "waterfall": waterfall,
          "variance": variance, "stacked": stacked, "heatmap": heatmap, "seatmap": seatmap}
