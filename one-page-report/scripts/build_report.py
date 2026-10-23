#!/usr/bin/env python3
"""Build a one-page report (HTML) from a report spec (JSON).

Usage:
  python3 build_report.py SPEC.json --out report.html [--style handdrawn|business|path/to/style.json]

Standard library only. The HTML is self-contained: CSS, icons and only the font
pieces that the text needs are embedded, so the file opens anywhere offline.
See references/spec-format.md for the spec format.
"""
import argparse, base64, html, json, os, re, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")

# ---------------------------------------------------------------- helpers
def esc(s):
    return html.escape(str(s), quote=True)


def load_style(name):
    path = name if os.path.isfile(name) else os.path.join(ASSETS, "styles", f"{name}.json")
    if not os.path.isfile(path):
        sys.exit(f"style not found: {name}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


_icon_cache = {}
_icon_set = None
def icon_names():
    """All bundled icon names (assets/icons.json, Lucide, ISC)."""
    global _icon_set
    if _icon_set is None:
        with open(os.path.join(ASSETS, "icons.json"), encoding="utf-8") as f:
            _icon_set = json.load(f)["icons"]
    return _icon_set


def icon(name, cls="ic"):
    if not name:
        return ""
    if name not in _icon_cache:
        body = icon_names().get(name)
        if body is None:
            print(f"! icon not found: {name} (skipped)", file=sys.stderr)
        _icon_cache[name] = body
    body = _icon_cache[name]
    if body is None:
        return ""
    return (f'<svg class="{cls}" data-icon="{esc(name)}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')


def icon_nested(name, x, y, size, color):
    if not name:
        return ""
    icon(name)
    body = _icon_cache.get(name)
    if not body:
        return ""
    return (f'<svg x="{x:.0f}" y="{y:.0f}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round" data-icon="{esc(name)}">{body}</svg>')


def rich(s):
    """Escape, then apply the small markup set: **bold** ==good== !!bad!! ^^marker^^ ++up++ {{icon:name}}."""
    if s is None:
        return ""
    t = esc(s)
    t = re.sub(r"\{\{icon:([a-z0-9-]+)\}\}", lambda m: icon(m.group(1)), t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"==(.+?)==", r'<span class="good">\1</span>', t)
    t = re.sub(r"!!(.+?)!!", r'<span class="bad">\1</span>', t)
    t = re.sub(r"\^\^(.+?)\^\^", r'<span class="hl">\1</span>', t)
    t = re.sub(r"\+\+(.+?)\+\+", r'<span class="up">\1</span>', t)
    t = t.replace("\n", "<br>")
    return t


def text_width(s, size):
    """Rough rendered width in px for SVG layout (CJK ~1em, latin ~0.56em)."""
    return sum(size * (1.0 if ord(c) > 0x2E80 else 0.56) for c in str(s))


# ---------------------------------------------------------------- charts (SVG)
def chart_svg(b, st):
    kind = b.get("kind", "bar")
    c = st["chart"]
    data = b.get("data", [])
    F = 'font-family="inherit"'
    if kind == "bar":  # horizontal bars, one highlighted
        W, rowh, gap = 380, 22, 9
        label_w = max([text_width(d["label"], 13.5) for d in data] + [40]) + 8
        vmax = max(d["value"] for d in data) or 1
        val_w = max(text_width(d.get("display", d["value"]), 15) for d in data) + 10
        bar_w = W - label_w - val_w - 6
        H = len(data) * (rowh + gap)
        out = [f'<svg class="chart" viewBox="0 0 {W} {H}" style="width:100%;height:auto;max-height:{len(data)*44}px" data-chart="{esc(json.dumps(b, ensure_ascii=False))}">']
        for i, d in enumerate(data):
            y = i * (rowh + gap) + 3
            hl = d.get("highlight")
            w = max(2, bar_w * d["value"] / vmax)
            col = c["highlight"] if hl else c["context"]
            tc = c["strong"] if hl else c["text"]
            fw = ' font-weight="700"' if hl else ""
            out.append(f'<text x="{label_w-8:.0f}" y="{y+rowh*0.72:.0f}" text-anchor="end" font-size="13.5" fill="{tc}"{fw} {F}>{esc(d["label"])}</text>')
            out.append(f'<rect x="{label_w:.0f}" y="{y}" width="{w:.0f}" height="{rowh}" rx="4" fill="{col}"/>')
            out.append(f'<text x="{label_w+w+6:.0f}" y="{y+rowh*0.75:.0f}" font-size="{16 if hl else 13.5}" fill="{tc}" font-weight="700" {F}>{esc(d.get("display", d["value"]))}</text>')
        out.append(f'<path d="M{label_w:.0f} 0 v{H}" stroke="{c["axis"]}" stroke-width="1.5"/></svg>')
        return "".join(out)
    if kind == "column":
        W, H, top, bottom = 380, 170, 24, 36
        vmax = max(d["value"] for d in data) or 1
        n = len(data); slot = (W - 20) / n; bw = min(56, slot * 0.6)
        out = [f'<svg class="chart" viewBox="0 0 {W} {H}" style="width:100%;height:auto;max-height:240px" data-chart="{esc(json.dumps(b, ensure_ascii=False))}">']
        base = H - bottom
        for i, d in enumerate(data):
            cx = 10 + slot * (i + 0.5); h = (base - top) * d["value"] / vmax
            hl = d.get("highlight"); col = c["highlight"] if hl else c["context"]; tc = c["strong"] if hl else c["text"]
            out.append(f'<rect x="{cx-bw/2:.0f}" y="{base-h:.0f}" width="{bw:.0f}" height="{h:.0f}" rx="4" fill="{col}"/>')
            out.append(f'<text x="{cx:.0f}" y="{base-h-6:.0f}" text-anchor="middle" font-size="{15 if hl else 13.5}" font-weight="700" fill="{tc}" {F}>{esc(d.get("display", d["value"]))}</text>')
            out.append(f'<text x="{cx:.0f}" y="{base+17:.0f}" text-anchor="middle" font-size="12.5" fill="{tc}" {F}>{esc(d["label"])}</text>')
        out.append(f'<path d="M6 {base} H{W-6}" stroke="{c["axis"]}" stroke-width="1.5"/></svg>')
        return "".join(out)
    if kind == "line":
        W, H = 560, 108
        L, R, T, B = 60, 80, 22, 22
        vals = [d["value"] for d in data]
        ref = b.get("reference")
        lo = b.get("y_min", min(vals + ([ref["value"]] if ref else [])) - 5)
        hi = b.get("y_max", max(vals + ([ref["value"]] if ref else [])) + 3)
        def X(i): return L + (W - L - R) * (i / max(1, len(data) - 1))
        def Y(v): return T + (H - T - B) * (1 - (v - lo) / ((hi - lo) or 1))
        out = [f'<svg class="chart" viewBox="0 0 {W} {H+6}" style="width:100%;height:auto" data-chart="{esc(json.dumps(b, ensure_ascii=False))}">']
        out.append(f'<path d="M{L-10} {H-B+2} h{W-L-R+20}" stroke="{c["axis"]}" stroke-width="1.5"/>')
        if ref:
            ry = Y(ref["value"])
            out.append(f'<path d="M{L-10} {ry:.0f} h{W-L-R+20}" stroke="{c["reference"]}" stroke-width="1.2" stroke-dasharray="4 4"/>')
            out.append(f'<text x="{L-6}" y="{ry-5:.0f}" font-size="12.5" fill="{c["text"]}" {F}>{esc(ref.get("label",""))}</text>')
        pts = " ".join(f"{'M' if i==0 else 'L'}{X(i):.0f} {Y(v):.0f}" for i, v in enumerate(vals))
        out.append(f'<path d="{pts}" fill="none" stroke="{c["highlight"]}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>')
        for i, d in enumerate(data):
            last = i == len(data) - 1 or d.get("highlight")
            x, y = X(i), Y(d["value"])
            out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{6.5 if last else 5}" fill="{c["highlight"]}" stroke="#fff" stroke-width="2"/>')
            lab = esc(d.get("display", d["value"]))
            if last:
                out.append(f'<text x="{x+12:.0f}" y="{y+18:.0f}" font-size="17" font-weight="700" fill="{c["strong"]}" {F}>{lab}</text>')
            else:
                out.append(f'<text x="{x:.0f}" y="{y-10:.0f}" text-anchor="middle" font-size="14.5" fill="{c["text"]}" {F}>{lab}</text>')
            anchor = "middle"
            out.append(f'<text x="{x:.0f}" y="{H+4}" text-anchor="{anchor}" font-size="13" fill="{c["strong"] if last else c["text"]}" {F}>{esc(d["label"])}</text>')
        out.append("</svg>")
        return "".join(out)
    raise ValueError(f"unknown chart kind {kind}")


def timeline_svg(b, st):
    ev = b["events"]; c = st["chart"]; s = st["status"]
    W, H, L, R = 1820, 82, 70, 70
    n = len(ev)
    xs = [L + (W - L - R) * (i / max(1, n - 1)) for i in range(n)]
    out = [f'<svg class="timeline" viewBox="0 0 {W} {H}" style="width:100%;height:auto"><g font-family="inherit" text-anchor="middle" font-size="14.5">']
    y = 32
    # solid up to the last "done" event, dashed after it (planned and in-progress lie ahead)
    last_done = max((i for i, e in enumerate(ev) if e.get("status", "done") == "done"), default=None)
    solid_end = xs[last_done] if last_done is not None else 30
    if last_done is not None:
        out.append(f'<path d="M30 {y} H{solid_end:.0f}" stroke="{c["strong"]}" stroke-width="2.4"/>')
    if last_done is None or last_done < len(ev) - 1:
        out.append(f'<path d="M{solid_end:.0f} {y} H{W-20}" stroke="{c["reference"]}" stroke-width="2.4" stroke-dasharray="7 6"/>')
    for x, e in zip(xs, ev):
        stt = e.get("status", "done")
        if stt == "done":
            out.append(f'<circle cx="{x:.0f}" cy="{y}" r="11" fill="{s["good"]}"/><text x="{x:.0f}" y="{y+5}" font-size="12" fill="#fff">✓</text>')
            dc = c["strong"]
        elif stt == "doing":
            out.append(f'<circle cx="{x:.0f}" cy="{y}" r="12" fill="#fff" stroke="{s["warning"]}" stroke-width="4"/><text x="{x:.0f}" y="{y+5}" font-size="12" font-weight="700" fill="{c["strong"]}">…</text>')
            dc = c["strong"]
        else:
            out.append(f'<circle cx="{x:.0f}" cy="{y}" r="9" fill="#fff" stroke="{c["reference"]}" stroke-width="3"/>')
            dc = c["reference"]
        out.append(f'<text x="{x:.0f}" y="{y-20}" font-weight="700" fill="{dc}">{esc(e.get("date",""))}</text>')
        lab = e.get("label", ""); size = 17; gap = 6
        w = text_width(lab, 14.5)
        total = (size + gap + w) if e.get("icon") else w
        sub_w = text_width(e.get("sub", ""), 12.5)
        half = max(total, sub_w) / 2
        cx = min(max(x, half + 6), W - half - 6)   # keep text inside the frame
        if e.get("icon"):
            left = cx - (size + gap + w) / 2
            out.append(icon_nested(e["icon"], left, y + 14, size, c["text"] if stt != "plan" else c["reference"]).replace("<svg ", '<svg class="tl-ic" ', 1))
            tx = left + size + gap + w / 2
        else:
            tx = cx
        lc = c["strong"] if stt != "plan" else c["text"]
        out.append(f'<text class="tl-lab" data-cx="{cx:.0f}" data-icon-size="{size if e.get("icon") else 0}" x="{tx:.0f}" y="{y+28}" fill="{lc}">{esc(lab)}</text>')
        if e.get("sub"):
            sc = st["tokens"]["bad-text"] if e.get("highlight") else c["text"]
            out.append(f'<text x="{cx:.0f}" y="{y+46}" font-size="12.5" fill="{sc}">{esc(e["sub"])}</text>')
    out.append("</g></svg>")
    return "".join(out)


# ---------------------------------------------------------------- blocks
def block(b, st, lang):
    t = b["type"]
    if t == "cards":
        items = b["items"]
        cols = b.get("cols", len(items))
        parts = [f'<div class="cards" style="grid-template-columns:repeat({cols},1fr)">']
        for it in items:
            h = ['<div class="card">']
            if it.get("tag") or it.get("icon"):
                h.append(f'<div class="tagline">{icon(it.get("icon"))}{rich(it.get("tag",""))}</div>')
            if it.get("title"):
                h.append(f'<div class="ctitle">{rich(it["title"])}</div>')
            if it.get("big"):
                h.append(f'<div class="big">{rich(it["big"])}<small>{rich(it.get("big_note",""))}</small></div>')
            if it.get("chart"):
                h.append(chart_svg(it["chart"], st))
            if it.get("sub"):
                h.append(f'<div class="sub">{rich(it["sub"])}</div>')
            if it.get("foot"):
                h.append(f'<div class="foot">{rich(it["foot"])}</div>')
            h.append("</div>")
            parts.append("".join(h))
        parts.append("</div>")
        return "".join(parts)
    if t == "chart":
        head = ""
        if b.get("title"):
            head = f'<div class="btitle">{rich(b["title"])}{" <small>"+rich(b["note"])+"</small>" if b.get("note") else ""}</div>'
        foot = f'<div class="note">{rich(b["caption"])}</div>' if b.get("caption") else ""
        return f'<div class="chartblock">{head}{chart_svg(b, st)}{foot}</div>'
    if t == "issues":
        rows = []
        for it in b["items"]:
            d = f' <span class="d">{rich(it["detail"])}</span>' if it.get("detail") else ""
            fx = f'<div class="f">{rich(it["fix"])}</div>' if it.get("fix") else ""
            rows.append(f'<div class="issue card"><span class="p">{icon(it.get("icon","triangle-alert"))}{rich(it["problem"])}</span>{d}{fx}</div>')
        head = f'<div class="btitle">{rich(b["title"])}</div>' if b.get("title") else ""
        return head + '<div class="issues">' + "".join(rows) + "</div>"
    if t == "chips":
        rows = []
        for r in b["rows"]:
            chips = "".join(f'<span class="chip hot">{rich(x[1:])}</span>' if x.startswith("*") else f'<span class="chip">{rich(x)}</span>' for x in r["items"])
            rows.append(f'<div class="cat"><div class="k">{icon(r.get("icon"))}{rich(r["label"])}</div><div class="chips">{chips}</div></div>')
        head = f'<div class="btitle">{rich(b.get("title",""))}{" <small>"+rich(b["note"])+"</small>" if b.get("note") else ""}</div>' if b.get("title") else ""
        return head + "".join(rows)
    if t == "table":
        head = f'<div class="btitle">{rich(b.get("title",""))}{" <small>"+rich(b["note"])+"</small>" if b.get("note") else ""}</div>' if b.get("title") else ""
        if "header" in b:
            rec = b.get("recommend")
            def cell(v, i, tag="td"):
                cls = ' class="rec"' if rec is not None and i == rec else ""
                v = str(v)
                m = re.match(r"^(ok|no|warn)\b\s*(.*)$", v)
                if m and tag == "td":
                    sym = {"ok": "✓", "no": "✗", "warn": "!"}[m.group(1)]
                    v2 = f'<span class="st-{m.group(1)}">{sym}</span> {rich(m.group(2))}'
                    return f"<{tag}{cls}>{v2}</{tag}>"
                return f"<{tag}{cls}>{rich(v)}</{tag}>"
            hh = "<tr>" + "".join(cell(h, i, "th") for i, h in enumerate(b["header"])) + "</tr>"
            body = "".join("<tr>" + "".join(cell(v, i) for i, v in enumerate(r)) + "</tr>" for r in b["rows"])
            return head + f"<table>{hh}{body}</table>"
        body = "".join(f'<tr><td>{icon(r.get("icon"))}{rich(r["key"])}</td><td>{rich(r["value"])}</td></tr>' for r in b["rows"])
        return head + f'<table class="kv">{body}</table>'
    if t == "steps":
        lis = []
        for i, it in enumerate(b["items"], 1):
            who = ""
            if it.get("owner") or it.get("due"):
                who = f'<span class="who">{rich(" · ".join(x for x in [it.get("owner"), it.get("due")] if x))}</span>'
            sub = f'<span>{rich(it["sub"])}</span>' if it.get("sub") else ""
            lis.append(f'<li><span class="n">{i}</span>{rich(it["title"])}{who}{sub}</li>')
        return '<ol class="steps">' + "".join(lis) + "</ol>"
    if t == "note":
        return f'<div class="callout">{icon(b.get("icon"))}{rich(b["text"])}</div>'
    if t == "timeline":
        return timeline_svg(b, st)
    if t == "status":
        s = st["status"]
        names = {"zh": {"good": "正常", "warning": "注意", "serious": "落後", "critical": "嚴重"},
                 "en": {"good": "On track", "warning": "Watch", "serious": "Behind", "critical": "Critical"}}[lang]
        icons = {"good": "circle-check", "warning": "circle-alert", "serious": "triangle-alert", "critical": "octagon-alert"}
        names.update(b.get("labels", {}))
        rows = []
        for it in b["items"]:
            k = it["state"]
            rows.append(f'<div class="st"><span class="lamp" style="color:{s[k]}">{icon(icons[k])}<span style="color:var(--ink)">{names[k]}</span></span>'
                        f'<span class="nm">{rich(it["name"])}</span><span class="nt">{rich(it.get("note",""))}</span></div>')
        return '<div class="status">' + "".join(rows) + "</div>"
    if t == "stat":
        return (f'<div class="stat card"><div class="v">{rich(b["value"])}<small>{rich(b.get("unit",""))}</small></div>'
                f'<div class="l">{rich(b["label"])}</div><div class="c">{rich(b.get("compare",""))}</div></div>')
    if t == "text":
        lines = b["md"].split("\n")
        out, inlist = [], False
        for ln in lines:
            if ln.startswith("- "):
                if not inlist:
                    out.append("<ul>"); inlist = True
                out.append(f"<li>{rich(ln[2:])}</li>")
            else:
                if inlist:
                    out.append("</ul>"); inlist = False
                if ln.strip():
                    out.append(f"<p>{rich(ln)}</p>")
        if inlist:
            out.append("</ul>")
        return '<div class="text">' + "".join(out) + "</div>"
    if t == "columns":
        cols = b.get("cols", " ".join(["1fr"] * len(b["children"])))
        inner = "".join('<div class="col">' + "".join(block(x, st, lang) for x in ch) + "</div>" for ch in b["children"])
        return f'<div class="cols" style="grid-template-columns:{cols}">{inner}</div>'
    raise ValueError(f"unknown block type: {t}")


# ---------------------------------------------------------------- fonts
def parse_ranges(css_rule):
    m = re.search(r"unicode-range:\s*([^;}]+)", css_rule)
    if not m:
        return None
    rs = []
    for part in m.group(1).split(","):
        part = part.strip().upper().replace("U+", "")
        if "-" in part:
            a, b = part.split("-"); rs.append((int(a, 16), int(b, 16)))
        else:
            rs.append((int(part, 16), int(part, 16)))
    return rs


def font_file(bundle, name):
    """Read one file from the bundled font archives (assets/fonts/<bundle>*.zip)."""
    import glob
    for arc in sorted(glob.glob(os.path.join(ASSETS, "fonts", f"{bundle}*.zip"))):
        with zipfile.ZipFile(arc) as z:
            if name in z.namelist():
                return z.read(name)
    raise FileNotFoundError(f"{name} not found in assets/fonts/{bundle}*.zip")


def subset_font(raw, codepoints):
    """Shrink a woff2 piece to the characters used. Needs fontTools + brotli; otherwise keep the piece."""
    try:
        import logging; logging.getLogger("fontTools").setLevel(logging.ERROR)
        from fontTools import subset as fts
        import brotli  # noqa: F401  (woff2 support)
        import io
        opts = fts.Options(); opts.flavor = "woff2"; opts.layout_features = ["*"]
        font = fts.load_font(io.BytesIO(raw), opts)
        sub = fts.Subsetter(opts); sub.populate(unicodes=codepoints); sub.subset(font)
        buf = io.BytesIO(); fts.save_font(font, buf, opts)
        return buf.getvalue()
    except Exception:
        return raw


def font_css(bundle, used_chars):
    """Embed only the font files whose unicode-range covers characters the report uses.
    A missing font archive is not an error: the style's fallback (system) fonts are used instead."""
    if not bundle:
        return ""
    try:
        return _font_css(bundle, used_chars)
    except FileNotFoundError as e:
        print(f"warning: bundled font '{bundle}' not found ({e}); using system fonts instead", file=sys.stderr)
        return ""


def _font_css(bundle, used_chars):
    if bundle == "lxgw-wenkai-tc":
        out = []
        cps = {ord(ch) for ch in used_chars}
        for f in ("regular.css", "bold.css"):
            css = font_file(bundle, f).decode("utf-8")
            for rule in re.findall(r"@font-face\s*\{[^}]*\}", css):
                rs = parse_ranges(rule)
                if rs and not any(a <= cp <= b for cp in cps for a, b in rs):
                    continue
                fn = re.search(r"url\('\./([^']+)'\)", rule).group(1)
                raw = subset_font(font_file(bundle, fn), {cp for cp in cps if rs is None or any(a <= cp <= b for a, b in rs)})
                data = base64.b64encode(raw).decode()
                out.append(re.sub(r"url\('\./[^']+'\)", f"url(data:font/woff2;base64,{data})", rule))
        return "\n".join(out)
    faces = {"inter": [("Inter", 400, "inter-latin-400-normal.woff2"), ("Inter", 600, "inter-latin-600-normal.woff2"), ("Inter", 700, "inter-latin-700-normal.woff2")],
             "patrick-hand": [("Patrick Hand", 400, "patrick-hand-latin-400-normal.woff2"), ("Patrick Hand", 700, "patrick-hand-latin-400-normal.woff2")]}[bundle]
    out = []
    for fam, w, fn in faces:
        data = base64.b64encode(font_file(bundle, fn)).decode()
        out.append(f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:normal;src:url(data:font/woff2;base64,{data}) format('woff2')}}")
    return "\n".join(out)


def all_text(o):
    if isinstance(o, dict):
        return "".join(all_text(v) for v in o.values())
    if isinstance(o, list):
        return "".join(all_text(v) for v in o)
    return str(o) if isinstance(o, str) else ""


TIMELINE_JS = """<script>
// Re-centre each timeline icon + label with the real text width (fonts differ by language and style).
(function(){
  function fix(){
    document.querySelectorAll('svg.timeline').forEach(function(svg){
      var labs = svg.querySelectorAll('text.tl-lab'), ics = svg.querySelectorAll('svg.tl-ic'), k = 0;
      labs.forEach(function(t){
        var size = +t.getAttribute('data-icon-size'), cx = +t.getAttribute('data-cx');
        var w = t.getComputedTextLength();
        if (!size) { t.setAttribute('x', cx); return; }
        var left = cx - (size + 6 + w) / 2, ic = ics[k++];
        if (ic) ic.setAttribute('x', left);
        t.setAttribute('x', left + size + 6 + w / 2);
      });
    });
  }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fix); else window.addEventListener('load', fix);
})();
</script>"""


# ---------------------------------------------------------------- page
def build(spec, style):
    lang = "zh" if spec.get("lang", "zh").lower().startswith("zh") else "en"
    font = style["fonts"][lang]
    tokens = "".join(f"--{k}:{v};" for k, v in style["tokens"].items())
    base = open(os.path.join(ASSETS, "styles", "base.css"), encoding="utf-8").read()
    used = all_text(spec) + "0123456789%+-.,:;()（）、，。：；「」？！…·→✓✗ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    fonts = font_css(font.get("bundled"), used)
    m = spec.get("meta", {})
    lay = spec["layout"]
    areas = " ".join(f"'{r}'" for r in lay["areas"])
    zones = []
    for z in spec["zones"]:
        lead = f'<div class="lead">{rich(z["lead"])}</div>' if z.get("lead") else ""
        q = f'<i>{rich(z["question"])}</i>' if z.get("question") else ""
        blocks = "".join(block(b, style, lang) for b in z.get("blocks", []))
        pad = ' style="padding:22px 16px 6px"' if any(b["type"] == "timeline" for b in z.get("blocks", [])) else ""
        zones.append(f'<section class="zone c-{z.get("color","blue")}" style="grid-area:{z["id"]}" data-zone="{esc(z["id"])}"{pad}>'
                     f'<div class="zhead"><div class="tab">{icon(z.get("icon"))}{rich(z["label"])}{q}</div>{lead}</div><div class="blocks">{blocks}</div></section>')
    left = []
    if m.get("confidential"):
        left.append(f'<span class="conf">{rich(m["confidential"])}</span>')
    if m.get("sources"):
        left.append(rich(m["sources"]))
    right = " · ".join(rich(x) for x in [m.get("as_of"), m.get("version"), m.get("author")] if x)
    body_cls = " ".join(x for x in ["rough" if style.get("rough") else "", "texture" if style.get("texture") else "",
                                    "faux-bold" if font.get("bundled") == "patrick-hand" else ""] if x)
    logo = ""
    if style.get("logo") and os.path.isfile(style["logo"]):
        ext = os.path.splitext(style["logo"])[1].lstrip(".").replace("jpg", "jpeg")
        data = base64.b64encode(open(style["logo"], "rb").read()).decode()
        logo = f'<img class="logo" src="data:image/{ext};base64,{data}" style="position:absolute;top:14px;right:36px;height:34px" alt="">'
    html_lang = "zh-Hant" if lang == "zh" else "en"
    return f"""<!doctype html>
<html lang="{html_lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=1920">
<title>{esc(re.sub(r'[*=!^]', '', spec.get('doc_title') or spec['title'])[:80])}</title>
<style>{fonts}
:root{{{tokens}--font:{font['family']}}}
{base}</style></head>
<body class="{body_cls}" data-style="{esc(style.get('name',''))}">
<svg width="0" height="0" style="position:absolute"><filter id="wobble"><feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="3"/><feDisplacementMap in="SourceGraphic" scale="3"/></filter></svg>
{logo}<div class="wrap">
<div class="kicker">{rich(m.get('kicker',''))}</div>
<h1 class="title">{rich(spec['title'])}</h1>
<div class="grid" style="grid-template-columns:{lay['columns']};grid-template-areas:{areas}">
{''.join(zones)}
</div>
<div class="foot-meta"><span>{' '.join(left)}</span><span>{right}</span></div>
</div>
{TIMELINE_JS}</body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    ap.add_argument("--style", default=None, help="handdrawn | business | path to a style .json")
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8"))
    style = load_style(a.style or spec.get("style", "handdrawn"))
    html_out = build(spec, style)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write(html_out)
    print(f"✓ {a.out}  ({len(html_out)//1024} KB, style={style.get('name')}, lang={spec.get('lang','zh')})")


if __name__ == "__main__":
    main()
