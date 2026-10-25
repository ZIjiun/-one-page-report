#!/usr/bin/env python3
"""Build a one-page report (HTML) from a report spec (JSON).

Usage:
  python3 build_report.py SPEC.json --out report.html [--style handdrawn|business|path/to/style.json] [--theme light|dark]

Standard library only. The HTML is self-contained: CSS, icons and only the font
pieces that the text needs are embedded, so the file opens anywhere offline.
See references/spec-format.md for the spec format.
"""
import argparse, base64, html, json, os, re, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diagrams

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")

# ---------------------------------------------------------------- helpers
def esc(s):
    return html.escape(str(s), quote=True)


def load_style(name, theme="light"):
    """Load a style file. theme="dark" applies the style's "dark" block (tokens/chart/status overrides);
    a style without one borrows the business dark block and keeps its own fonts."""
    path = name if os.path.isfile(name) else os.path.join(ASSETS, "styles", f"{name}.json")
    if not os.path.isfile(path):
        sys.exit(f"style not found: {name}")
    with open(path, encoding="utf-8") as f:
        st = json.load(f)
    st.setdefault("tokens", {}).setdefault("on-accent", "#ffffff")
    st["theme"] = "light"
    if theme == "dark":
        dark = st.get("dark")
        if not dark:
            with open(os.path.join(ASSETS, "styles", "business.json"), encoding="utf-8") as f:
                dark = json.load(f)["dark"]
            print(f"note: style '{st.get('name')}' has no dark block; using the default dark colours", file=sys.stderr)
        for k in ("tokens", "chart", "status"):
            st[k] = {**st.get(k, {}), **dark.get(k, {})}
        st["theme"] = "dark"
    return st


def image_uri(src, spec_dir="."):
    """Embed a user-provided local image (PNG/JPG/WebP/SVG). Remote URLs are refused: the page must open offline,
    and images come only from the user (or official sources the user approved), never generated."""
    if not src:
        return None
    if re.match(r"^https?://", str(src)):
        print(f"! image skipped (download it first and pass a local path): {src}", file=sys.stderr)
        return None
    path = src if os.path.isabs(src) else os.path.join(spec_dir, src)
    if not os.path.isfile(path):
        print(f"! image not found: {src}", file=sys.stderr)
        return None
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp", "svg": "image/svg+xml"}.get(ext, "image/png")
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


SPEC_DIR = "."


def image_size(src, spec_dir="."):
    """(width, height) of a local PNG or JPEG, standard library only; None if unknown."""
    import struct
    path = src if os.path.isabs(src) else os.path.join(spec_dir, src)
    try:
        with open(path, "rb") as f:
            head = f.read(26)
            if head[:8] == b"\x89PNG\r\n\x1a\n":
                return struct.unpack(">II", head[16:24])
            if head[:2] == b"\xff\xd8":
                f.seek(2)
                while True:
                    mk = f.read(2)
                    if len(mk) < 2 or mk[0] != 0xFF:
                        return None
                    ln = struct.unpack(">H", f.read(2))[0]
                    if 0xC0 <= mk[1] <= 0xCF and mk[1] not in (0xC4, 0xC8, 0xCC):
                        h, w = struct.unpack(">xHH", f.read(5))
                        return (w, h)
                    f.seek(ln - 2, 1)
    except OSError:
        return None
    return None


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
        # one line: rich() turns "\n" into <br>, which would cut a multi-shape icon short inside {{icon:...}}
        _icon_cache[name] = re.sub(r">\s+<", "><", body).strip() if body else body
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
        label_w = max([text_width(d["label"], 14) for d in data] + [40]) + 8
        vmax = max(d["value"] for d in data) or 1
        val_w = max(text_width(d.get("display", d["value"]), 18) for d in data) + 10
        bar_w = W - label_w - val_w - 6
        H = len(data) * (rowh + gap)
        out = [f'<svg class="chart" viewBox="0 0 {W} {H}" style="width:100%;max-width:{W}px;height:auto" data-chart="{esc(json.dumps(b, ensure_ascii=False))}">']
        for i, d in enumerate(data):
            y = i * (rowh + gap) + 3
            hl = d.get("highlight")
            w = max(2, bar_w * d["value"] / vmax)
            col = c["highlight"] if hl else c["context"]
            tc = c["strong"] if hl else c["text"]
            fw = ' font-weight="700"' if hl else ""
            out.append(f'<text x="{label_w-8:.0f}" y="{y+rowh*0.72:.0f}" text-anchor="end" font-size="14" fill="{tc}"{fw} {F}>{esc(d["label"])}</text>')
            out.append(f'<rect x="{label_w:.0f}" y="{y}" width="{w:.0f}" height="{rowh}" rx="4" fill="{col}"/>')
            out.append(f'<text x="{label_w+w+6:.0f}" y="{y+rowh*0.75:.0f}" font-size="{18 if hl else 14}" fill="{tc}" font-weight="700" {F}>{esc(d.get("display", d["value"]))}</text>')
        out.append(f'<path d="M{label_w:.0f} 0 v{H}" stroke="{c["axis"]}" stroke-width="1.5"/></svg>')
        return "".join(out)
    if kind == "column":
        has_ic = any(d.get("icon") for d in data)
        W, H, top, bottom = 380, (196 if has_ic else 170), 24, (62 if has_ic else 36)
        vmax = max(d["value"] for d in data) or 1
        n = len(data); slot = (W - 20) / n; bw = min(56, slot * 0.6)
        out = [f'<svg class="chart" viewBox="0 0 {W} {H}" style="width:100%;max-width:{W}px;height:auto" data-chart="{esc(json.dumps(b, ensure_ascii=False))}">']
        base = H - bottom
        for i, d in enumerate(data):
            cx = 10 + slot * (i + 0.5); h = (base - top) * d["value"] / vmax
            hl = d.get("highlight"); col = c["highlight"] if hl else c["context"]; tc = c["strong"] if hl else c["text"]
            out.append(f'<rect x="{cx-bw/2:.0f}" y="{base-h:.0f}" width="{bw:.0f}" height="{h:.0f}" rx="4" fill="{col}"/>')
            out.append(f'<text x="{cx:.0f}" y="{base-h-6:.0f}" text-anchor="middle" font-size="{18 if hl else 14}" font-weight="700" fill="{tc}" {F}>{esc(d.get("display", d["value"]))}</text>')
            if d.get("icon"):
                out.append(icon_nested(d["icon"], cx - 11, base + 8, 22, c["highlight"] if hl else c["text"]))
            out.append(f'<text x="{cx:.0f}" y="{base+(52 if has_ic else 19):.0f}" text-anchor="middle" font-size="14" fill="{tc}"{" font-weight=\"700\"" if hl else ""} {F}>{esc(d["label"])}</text>')

        out.append(f'<path d="M6 {base} H{W-6}" stroke="{c["axis"]}" stroke-width="1.5"/></svg>')
        note = f'<div class="chart-note">{rich(b["top_note"])}</div>' if b.get("top_note") else ""
        return note + "".join(out)
    if kind == "line":
        W, H = 560, 108
        L, R, T, B = 60, 80, 22, 22
        vals = [d["value"] for d in data]
        ref = b.get("reference")
        lo = b.get("y_min", min(vals + ([ref["value"]] if ref else [])) - 5)
        hi = b.get("y_max", max(vals + ([ref["value"]] if ref else [])) + 3)
        def X(i): return L + (W - L - R) * (i / max(1, len(data) - 1))
        def Y(v): return T + (H - T - B) * (1 - (v - lo) / ((hi - lo) or 1))
        out = [f'<svg class="chart" viewBox="0 0 {W} {H+6}" style="width:100%;max-width:{W}px;height:auto" data-chart="{esc(json.dumps(b, ensure_ascii=False))}">']
        out.append(f'<path d="M{L-10} {H-B+2} h{W-L-R+20}" stroke="{c["axis"]}" stroke-width="1.5"/>')
        if ref:
            ry = Y(ref["value"])
            out.append(f'<path d="M{L-10} {ry:.0f} h{W-L-R+20}" stroke="{c["reference"]}" stroke-width="1.2" stroke-dasharray="4 4"/>')
            out.append(f'<text x="{L-6}" y="{ry-5:.0f}" font-size="14" fill="{c["text"]}" {F}>{esc(ref.get("label",""))}</text>')
        pts = " ".join(f"{'M' if i==0 else 'L'}{X(i):.0f} {Y(v):.0f}" for i, v in enumerate(vals))
        out.append(f'<path d="{pts}" fill="none" stroke="{c["highlight"]}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>')
        for i, d in enumerate(data):
            last = i == len(data) - 1 or d.get("highlight")
            x, y = X(i), Y(d["value"])
            out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{6.5 if last else 5}" fill="{c["highlight"]}" stroke="{st["tokens"]["card"]}" stroke-width="2"/>')
            lab = esc(d.get("display", d["value"]))
            if last:
                out.append(f'<text x="{x+12:.0f}" y="{y+18:.0f}" font-size="18" font-weight="700" fill="{c["strong"]}" {F}>{lab}</text>')
            else:
                out.append(f'<text x="{x:.0f}" y="{y-10:.0f}" text-anchor="middle" font-size="14" fill="{c["text"]}" {F}>{lab}</text>')
            anchor = "middle"
            out.append(f'<text x="{x:.0f}" y="{H+4}" text-anchor="{anchor}" font-size="14" fill="{c["strong"] if last else c["text"]}" {F}>{esc(d["label"])}</text>')
        out.append("</svg>")
        return "".join(out)
    raise ValueError(f"unknown chart kind {kind}")


def timeline_svg(b, st):
    ev = b["events"]; c = st["chart"]; s = st["status"]
    W, H, L, R = 1820, 86, 70, 70
    n = len(ev)
    xs = [L + (W - L - R) * (i / max(1, n - 1)) for i in range(n)]
    out = [f'<svg class="timeline" viewBox="0 0 {W} {H}" style="width:100%;height:auto"><g font-family="inherit" text-anchor="middle" font-size="14">']
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
            out.append(f'<circle cx="{x:.0f}" cy="{y}" r="11" fill="{s["good"]}"/><text x="{x:.0f}" y="{y+5}" font-size="14" fill="{st["tokens"].get("on-accent", "#fff")}">✓</text>')
            dc = c["strong"]
        elif stt == "doing":
            out.append(f'<circle cx="{x:.0f}" cy="{y}" r="12" fill="{st["tokens"]["card"]}" stroke="{s["warning"]}" stroke-width="4"/><text x="{x:.0f}" y="{y+5}" font-size="14" font-weight="700" fill="{c["strong"]}">…</text>')
            dc = c["strong"]
        else:
            out.append(f'<circle cx="{x:.0f}" cy="{y}" r="9" fill="{st["tokens"]["card"]}" stroke="{c["reference"]}" stroke-width="3"/>')
            dc = c["reference"]
        out.append(f'<text x="{x:.0f}" y="{y-20}" font-weight="700" fill="{dc}">{esc(e.get("date",""))}</text>')
        lab = e.get("label", ""); size = 17; gap = 6
        w = text_width(lab, 14)
        total = (size + gap + w) if e.get("icon") else w
        sub_w = text_width(e.get("sub", ""), 14)
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
            out.append(f'<text x="{cx:.0f}" y="{y+47}" font-size="14" fill="{sc}">{esc(e["sub"])}</text>')
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
            if it.get("diagram"):
                h.append(block(it["diagram"], st, lang))
            if it.get("sub"):
                h.append(f'<div class="sub">{rich(it["sub"])}</div>')
            if it.get("photo"):
                ph = dict(it["photo"]); uri = image_uri(ph.get("src"), SPEC_DIR)
                if isinstance(ph.get("caption"), list):  # same list form as the photo block
                    ph["caption"] = "　".join(f'**{c.get("value","")}**{c.get("unit","")} {c.get("label","")}' if isinstance(c, dict) else str(c) for c in ph["caption"])
                if uri:
                    h.append(f'<div class="cardphoto" style="background-image:url({uri});background-position:{esc(ph.get("position", "center"))}">'
                             f'{"<span>"+rich(ph["caption"])+"</span>" if ph.get("caption") else ""}</div>')
                elif it.get("foot") is None and ph.get("caption"):
                    h.append(f'<div class="foot">{rich(ph["caption"])}</div>')
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
            lis.append(f'<li><span class="n">{i}</span>{icon(it.get("icon"))}{rich(it["title"])}{who}{sub}</li>')
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
    if t in diagrams.BLOCKS:
        head = f'<div class="btitle">{rich(b["title"])}</div>' if b.get("title") else ""
        return head + diagrams.BLOCKS[t](b, st, icon_names())
    if t == "photo":
        uri = image_uri(b.get("src"), SPEC_DIR)
        head = f'<div class="btitle">{rich(b["title"])}</div>' if b.get("title") else ""
        if not uri:
            return head
        cap = ""
        if b.get("caption"):
            cap = '<div class="cap">' + "".join(
                f'<span><b>{esc(c.get("value",""))}</b>{esc(c.get("unit",""))}<i>{esc(c.get("label",""))}</i></span>' if isinstance(c, dict)
                else f'<span>{rich(c)}</span>' for c in b["caption"]) + "</div>"
        hgt = f"height:{int(b['height'])}px;" if b.get("height") else ""
        if b.get("marks"):
            # screenshot with numbered marks: the whole image is shown (no crop), so x/y (% of width/height) land exactly
            pins, notes = [], []
            for i, mk in enumerate(b["marks"], 1):
                x, y = float(mk.get("x", 50)), float(mk.get("y", 50))
                if mk.get("w") and mk.get("h"):
                    pins.append(f'<span class="mbox" style="left:{x}%;top:{y}%;width:{float(mk["w"])}%;height:{float(mk["h"])}%"></span>')
                    px, py = x, y
                else:
                    px, py = x, y
                pins.append(f'<span class="mpin" style="left:{px}%;top:{py}%">{i}</span>')
                notes.append(f'<li><span class="mnum">{i}</span><span>{rich(mk.get("label", ""))}</span></li>')
            mh = f"max-height:{int(b['height'])}px;" if b.get("height") else ""
            return (f'{head}<figure class="shot"><div class="shotimg"><img src="{uri}" alt="{esc(b.get("alt", ""))}" style="{mh}">{"".join(pins)}</div>'
                    f'<ol class="marks">{"".join(notes)}</ol></figure>')
        return f'{head}<div class="photo" role="img" aria-label="{esc(b.get("alt", ""))}" style="{hgt}background-image:url({uri});background-position:{esc(b.get("position", "center"))}">{cap}</div>'
    if t == "speclines":
        rows = "".join(f'<div><span class="k">{icon(r.get("icon"))}{rich(r.get("label",""))}</span><span class="v">{rich(r.get("text",""))}</span></div>' for r in b["rows"])
        head = f'<div class="btitle">{rich(b["title"])}</div>' if b.get("title") else ""
        return f'{head}<div class="speclines">{rows}</div>'
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
    """Read one file from the bundled fonts (assets/fonts/<bundle>*.json; older copies used .zip)."""
    import glob
    for arc in sorted(glob.glob(os.path.join(ASSETS, "fonts", f"{bundle}*.json"))):
        with open(arc, encoding="utf-8") as f:
            entry = json.load(f).get("files", {}).get(name)
        if entry is not None:
            return entry["text"].encode("utf-8") if "text" in entry else base64.b64decode(entry["base64"])
    for arc in sorted(glob.glob(os.path.join(ASSETS, "fonts", f"{bundle}*.zip"))):
        with zipfile.ZipFile(arc) as z:
            if name in z.namelist():
                return z.read(name)
    raise FileNotFoundError(f"{name} not found in assets/fonts/{bundle}*.json")


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


LINKS_JS = """<script>
// Arrows between zones, drawn in the gap after layout and redrawn when the page is fitted or resized.
(function(){
  var NS = 'http://www.w3.org/2000/svg';
  function box(el){ return {x: el.offsetLeft, y: el.offsetTop, w: el.offsetWidth, h: el.offsetHeight}; }
  function draw(){
    var grid = document.querySelector('.grid'); if (!grid) return;
    grid.querySelectorAll('.link-arrow,.link-label').forEach(function(e){ e.remove(); });
    var paper = getComputedStyle(document.body).backgroundColor;
    (window.LINKS || []).forEach(function(l){
      var a = grid.querySelector('[data-zone="' + l.from + '"]'), b = grid.querySelector('[data-zone="' + l.to + '"]');
      if (!a || !b) return;
      var A = box(a), B = box(b), S = 34, cx, cy, rot, horiz;
      if (B.x >= A.x + A.w - 2 || A.x >= B.x + B.w - 2) {          // side by side
        horiz = true; rot = B.x > A.x ? 0 : 180;
        cx = (B.x > A.x ? (A.x + A.w + B.x) : (B.x + B.w + A.x)) / 2;
        var t = Math.max(A.y, B.y), btm = Math.min(A.y + A.h, B.y + B.h);
        cy = btm > t ? (t + btm) / 2 : (A.y + A.h / 2 + B.y + B.h / 2) / 2;
      } else {                                                        // stacked
        horiz = false; rot = B.y > A.y ? 90 : -90;
        cy = (B.y > A.y ? (A.y + A.h + B.y) : (B.y + B.h + A.y)) / 2;
        var lf = Math.max(A.x, B.x), rt = Math.min(A.x + A.w, B.x + B.w);
        cx = rt > lf ? (lf + rt) / 2 : (A.x + A.w / 2 + B.x + B.w / 2) / 2;
      }
      var col = getComputedStyle(a).getPropertyValue('--zc').trim() || 'currentColor';
      var svg = document.createElementNS(NS, 'svg');
      svg.setAttribute('class', 'ic link-arrow'); svg.setAttribute('viewBox', '0 0 24 24');
      svg.setAttribute('width', S); svg.setAttribute('height', S);
      svg.style.cssText = 'position:absolute;z-index:4;left:' + (cx - S / 2) + 'px;top:' + (cy - S / 2) + 'px;width:' + S + 'px;height:' + S + 'px;color:' + col;
      svg.innerHTML = '<circle cx="12" cy="12" r="11" fill="' + paper + '" stroke="currentColor" stroke-width="1.6"/>' +
        '<g transform="rotate(' + rot + ' 12 12)" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">' +
        '<path d="M6.5 12h10"/><path d="M12.5 8l4 4-4 4"/></g>';
      grid.appendChild(svg);
      if (l.label) {
        var lb = document.createElement('div'); lb.className = 'link-label'; lb.innerHTML = l.label;
        lb.style.color = col;
        if (!horiz) { lb.style.maxWidth = 'none'; lb.style.whiteSpace = 'nowrap'; lb.style.background = paper; lb.style.padding = '0 6px'; }
        grid.appendChild(lb);
        var w = lb.offsetWidth, h = lb.offsetHeight;
        lb.style.left = (horiz ? cx - w / 2 : cx + S / 2 + 6) + 'px';
        lb.style.top = (horiz ? cy + S / 2 + 4 : cy - h / 2) + 'px';
      }
    });
  }
  window.addEventListener('load', draw);
  if (document.fonts) document.fonts.ready.then(draw);
  if (window.ResizeObserver) new ResizeObserver(draw).observe(document.querySelector('.grid'));
  draw();
})();
</script>"""


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
    style["lang"] = lang
    font = style["fonts"][lang]
    tokens = "".join(f"--{k}:{v};" for k, v in style["tokens"].items())
    base = open(os.path.join(ASSETS, "styles", "base.css"), encoding="utf-8").read()
    used = all_text(spec) + "0123456789%+-.,:;()（）、，。：；「」？！…·→✓✗ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    fonts = font_css(font.get("bundled"), used)
    m = spec.get("meta", {})
    lay = spec["layout"]
    areas = " ".join(f"'{r}'" for r in lay["areas"])
    zones = []
    numbered = spec.get("zone_heading") == "number"
    for zi, z in enumerate(spec["zones"], 1):
        lead = f'<div class="lead">{rich(z["lead"])}</div>' if z.get("lead") else ""
        q = f'<i>{rich(z["question"])}</i>' if z.get("question") else ""
        blocks = "".join(block(b, style, lang) for b in z.get("blocks", []))
        pad = ' style="padding:22px 16px 6px"' if any(b["type"] == "timeline" for b in z.get("blocks", [])) else ""
        frame = z.get("frame", "solid")   # solid (default) | dashed (look here) | open (no frame, content on the page)
        if frame not in ("solid", "dashed", "open"):
            raise ValueError(f'zone {z["id"]}: frame must be solid, dashed or open (got {frame!r})')
        fcls = "" if frame == "solid" else f" f-{frame}"
        # when a zone is shorter than its row: stretch (default, content at the top), center, or end the frame at the content
        fit = z.get("fit", "stretch")
        if fit not in ("stretch", "center", "content"):
            raise ValueError(f'zone {z["id"]}: fit must be stretch, center or content (got {fit!r})')
        fcls += "" if fit == "stretch" else f" fit-{fit}"
        zones.append(f'<section class="zone c-{z.get("color","blue")}{fcls}" style="grid-area:{z["id"]}" data-zone="{esc(z["id"])}"{pad}>'
                     f'<div class="zhead"><div class="tab">{f"<span class=zn>{zi:02d}</span>" if numbered else icon(z.get("icon"))}{rich(z["label"])}{q}</div>{lead}</div><div class="blocks">{blocks}</div></section>')
    left = []
    if m.get("confidential"):
        left.append(f'<span class="conf">{rich(m["confidential"])}</span>')
    if m.get("sources"):
        left.append(rich(m["sources"]))
    right = " · ".join(rich(x) for x in [m.get("as_of"), m.get("version"), m.get("author")] if x)
    # ---- imagery (user-provided only): hero, product logo, backdrop. Credits go to the footer automatically.
    img = []; extra_css = []; cls_extra = []
    def themed(key):
        """Image settings for the current theme. In dark, a "dark" sub-object replaces fields
        (another image, another mode); "dark": null drops the image. src_dark is a shorthand."""
        v = spec.get(key)
        if not v or style.get("theme") != "dark" or "dark" not in v:
            return v
        if v["dark"] is None:
            return None
        return {**{k: x for k, x in v.items() if k != "dark"}, **v["dark"], "_dark": True}
    hero = themed("hero")
    if hero and style.get("theme") == "dark" and not hero.get("_dark"):
        if hero.get("src_dark"):
            hero = {**hero, "src": hero["src_dark"]}
        elif hero.get("mode") == "cutout":
            print("note: dark theme with a cut-out photo on a light background; edges faded as a stopgap. "
                  "Find an image that suits the dark page (night/dusk shot, dark key art) and pass it as hero.src_dark, or drop the hero", file=sys.stderr)
            hero = {**hero, "mode": "cutout faded"}
    if hero:
        uri = image_uri(hero.get("src"), SPEC_DIR)
        if uri:
            mode = hero.get("mode", "side")   # side (fades in from the right) | cutout (studio shot on a matching background) | band (full-width, behind the title)
            vars_ = "".join(f"--hero-{k}:{hero[k]}{'px' if isinstance(hero[k], (int, float)) and k != 'opacity' else ''};" for k in ("w", "h", "opacity") if k in hero)
            img.append(f'<div class="hero {esc(mode)}{" own-dark" if hero.get("_dark") else ""}" style="background-image:url({uri});{vars_}{"background-position:"+esc(hero["position"])+";" if hero.get("position") else ""}"></div>')
            if mode == "band":
                img.append('<div class="hero-shade"></div>')
            else:
                cls_extra.append("title-left")
                extra_css.append(f":root{{--title-pad:{int(hero.get('title_pad', (hero.get('w', 380) + 80) if mode == 'cutout' else 560))}px}}")
            cls_extra.append("has-hero")
    plogo = themed("logo")
    if plogo and style.get("theme") == "dark" and not plogo.get("_dark"):
        if plogo.get("src_dark"):
            plogo = {**plogo, "src": plogo["src_dark"]}
        else:
            print("note: dark theme with a logo made for light pages; pass logo.src_dark (the brand's version for dark backgrounds) or drop the logo", file=sys.stderr)
    if plogo:
        uri = image_uri(plogo.get("src"), SPEC_DIR)
        if uri:
            h_ = int(plogo.get("h", 104)); sz = image_size(plogo["src"], SPEC_DIR)
            lw = int(h_ * sz[0] / sz[1]) if sz else int(h_ * 1.8)
            img.append(f'<img class="page-logo" src="{uri}" alt="{esc(plogo.get("alt", "logo"))}" style="--logo-h:{h_}px">')
            cls_extra.append("has-logo")
            if "title-left" in cls_extra or hero is None or hero.get("mode") != "band":
                extra_css.append(f":root{{--logo-pad:{lw + 40}px}}")
    bd = themed("backdrop")
    if bd:
        uri = image_uri(bd.get("src"), SPEC_DIR)
        if uri:
            img.insert(0, f'<div class="backdrop" style="background-image:url({uri});--backdrop-opacity:{bd.get("opacity", .25)}"></div>')
            cls_extra.append("has-backdrop")
    if img and m.get("image_credit"):
        left.append(rich(m["image_credit"]))
    elif img:
        print("! images used but meta.image_credit is empty: add the source and rights holder", file=sys.stderr)
    body_cls = " ".join(x for x in ["rough" if style.get("rough") else "", "texture" if style.get("texture") else "",
                                    "faux-bold" if font.get("bundled") == "patrick-hand" else "",
                                    "dark" if style.get("theme") == "dark" else ""] + cls_extra if x)
    logo = ""
    if style.get("logo") and os.path.isfile(style["logo"]):
        ext = os.path.splitext(style["logo"])[1].lstrip(".").replace("jpg", "jpeg")
        data = base64.b64encode(open(style["logo"], "rb").read()).decode()
        logo = f'<img class="logo" src="data:image/{ext};base64,{data}" style="position:absolute;top:14px;right:36px;height:34px" alt="">'
    html_lang = "zh-Hant" if lang == "zh" else "en"
    ctx = f'<div class="context">{rich(spec["background"])}</div>\n' if spec.get("background") else ""
    # zone headings: "tab" (default, a label on the frame line) or "label" (an underlined heading above the content)
    heading = spec.get("zone_heading", "tab")
    if heading not in ("tab", "label", "ribbon", "number", "bar"):
        raise ValueError(f'zone_heading must be tab, label, ribbon, number or bar (got {heading!r})')
    if heading != "tab":
        body_cls = (body_cls + " h-" + heading).strip()
    # an aside: one short remark to the reader (a tip or an opinion, not evidence), in a speech bubble
    # beside the title. No frame of its own beyond the bubble, never over data. {"text", "icon"}
    aside = spec.get("aside")
    aside_html = (f'<div class="aside">{icon(aside.get("icon"))}<span>{rich(aside["text"])}</span></div>' if aside else "")
    # arrows between zones: [{"from": id, "to": id, "label": "..."}]; drawn after layout (LINKS_JS)
    ids = {z["id"] for z in spec["zones"]}
    links = []
    for ln in spec.get("links", []):
        if ln.get("from") not in ids or ln.get("to") not in ids:
            raise ValueError(f'links: unknown zone in {ln} (zones: {sorted(ids)})')
        links.append({"from": ln["from"], "to": ln["to"], "label": rich(ln.get("label", ""))})
    if links:
        body_cls = (body_cls + " has-links").strip()
    links_js = ("<script>window.LINKS=" + json.dumps(links, ensure_ascii=False).replace("</", "<\\/") + ";</script>" + LINKS_JS) if links else ""
    # a summary strip above the footer: {"icon", "text"} or {"icon", "lead", "items": [...], "result"}
    sm = spec.get("summary")
    summary = ""
    if sm:
        parts = [f'<span class="s-lead">{rich(sm.get("lead") or sm.get("text", ""))}</span>']
        parts += [f'<span class="s-item"><b class="s-ok">✓</b>{rich(x)}</span>' for x in sm.get("items", [])]
        if sm.get("result"):
            parts.append(f'<span class="s-eq">=</span><span class="s-res">{rich(sm["result"])}</span>')
        summary = f'<div class="summary c-{sm.get("color", "blue")}">{icon(sm.get("icon"))}{"".join(parts)}</div>\n'
    return f"""<!doctype html>
<html lang="{html_lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=1920">
<title>{esc(re.sub(r'[*=!^]', '', spec.get('doc_title') or spec['title'])[:80])}</title>
<style>{fonts}
:root{{{tokens}--font:{font['family']}}}
{base}{"".join(extra_css)}</style></head>
<body class="{body_cls}" data-style="{esc(style.get('name',''))}">
<svg width="0" height="0" style="position:absolute"><filter id="wobble"><feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="3"/><feDisplacementMap in="SourceGraphic" scale="3"/></filter></svg>
{logo}{"".join(img)}<div class="wrap">
<div class="kicker">{rich(m.get('kicker',''))}</div>
<div class="titlebox"><h1 class="title">{rich(spec['title'])}</h1>{aside_html}</div>
{ctx}<div class="grid" style="grid-template-columns:{lay['columns']};grid-template-areas:{areas}">
{''.join(zones)}
</div>
{summary}<div class="foot-meta"><span>{' '.join(left)}</span><span>{right}</span></div>
</div>
{TIMELINE_JS}{links_js}</body></html>"""


def main():
    global SPEC_DIR
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    ap.add_argument("--style", default=None, help="handdrawn | business | path to a style .json")
    ap.add_argument("--theme", default=None, choices=["light", "dark"], help="light (default) or dark; overrides the spec's \"theme\"")
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8"))
    SPEC_DIR = os.path.dirname(os.path.abspath(a.spec))
    style = load_style(a.style or spec.get("style", "handdrawn"), a.theme or spec.get("theme", "light"))
    try:
        html_out = build(spec, style)
    except ValueError as e:
        sys.exit(f"✗ {e}")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write(html_out)
    print(f"✓ {a.out}  ({len(html_out)//1024} KB, style={style.get('name')}, theme={style.get('theme')}, lang={spec.get('lang','zh')})")


if __name__ == "__main__":
    main()
