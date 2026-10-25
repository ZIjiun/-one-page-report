#!/usr/bin/env python3
"""Automatic part of the self-review (references/review-checklist.md).

Usage:
  python3 review.py SPEC.zh.json [SPEC.en.json] [--html A.html [B.html]] [--source notes.txt data.xlsx deck.pptx ...] [--out review.json]

Checks:
  numbers   every number in the spec, with where it appears (for tracing to the material);
            with --source, numbers not found in the source files are flagged. Sources may be
            .txt .md .csv .tsv .json .html, or .xlsx .pptx .docx (text read with the standard
            library). For .pdf, export the text first (pdftotext is used when it exists).
  derived   spec "derived": [{"value": "−60%", "formula": "(6.5-2.6)/6.5*100", "from": ["6.5","2.6"]}]
            numbers worked out from the material: the formula is recomputed and must match
            the value (to its shown precision); its inputs must be in the sources
  bilingual numbers/dates in the zh and en specs must match (as multisets)
  meta      data date and sources present (company mode, the default: also version, author)
  options   design-option limits: one dashed zone, open zones hold no evidence, 4–6 zones, summary not the title
  empty     with --html: zones whose content fills under 70% of them
  logic     title is not a bare topic; zones have leads; next steps have owners/dates or say so
  words     vague or "AI feel" phrases (zh and en lists)
  layout    with --html: renders in the browser and reports overlapping text and overflow
  icons     the same icon used for two different labels
  icon_gaps category rows (table first column, steps, timeline, issues, cards, chips, speclines)
            with no icon; mark a deliberate choice with "icons": false on the block
  repeats   the same number in more than one place (each number appears once; the title may
            restate one headline figure)
  holes     cells that say "not given" / 「未提供」「未公開」「待補」: ask the user or drop the row
  focus     a chart with more than one highlighted item (one highlight per chart)
  fonts     with --html: rendered text sizes outside 46 / 34 / 18 / 14 (diagrams scaled up or down)
  colours   contrast of the style colours on its page; custom styles also via check_colors.py
Prints a JSON report and a short text summary. Exit 0 always (it advises, it does not block).
"""
import argparse, collections, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
NUM = re.compile(r"(?<![\w.])(?:US\$|\$|NT\$)?\d[\d,]*(?:\.\d+)?\s*(?:%|萬|億|K|M|B|fps|p|元|人|則|套|個|分|天|週|年|月)?")
VAGUE = ["大幅", "顯著", "全面", "賦能", "打造", "優化了", "提升了", "持續努力", "相關", "一定程度",
         "significantly", "robust", "seamless", "leverage", "synergy", "cutting-edge", "world-class",
         "best-in-class", "various", "a number of", "going forward", "empower", "unlock"]
TOPIC_TITLES = ["報告", "說明", "概況", "簡介", "update", "report", "overview", "summary"]


# Layout and drawing settings are not facts: their numbers are not traced to the sources.
CONFIG_KEYS = {"scale", "opacity", "h", "w", "width", "height", "length_mm", "width_mm", "folded", "highlight",
               "title_pad", "zoom", "max", "min", "layout", "hero", "logo", "backdrop", "position", "theme", "style"}


def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in CONFIG_KEYS and not isinstance(v, str) or k in ("layout", "hero", "logo", "backdrop"):
                continue
            if k == "rows" and isinstance(v, list) and all(isinstance(x, (int, float)) for x in v):
                continue   # seat counts per row in a seatmap
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, f"{path}[{i}]")
    elif isinstance(o, str):
        yield path, o
    elif isinstance(o, (int, float)) and not isinstance(o, bool):
        yield path, str(o)


UNIT = {"萬": 1e4, "万": 1e4, "億": 1e8, "K": 1e3, "k": 1e3, "M": 1e6, "B": 1e9}
DATE = re.compile(r"(?<![\d.])(\d{1,2})/(\d{1,2})(?:[–-](\d{1,2})(?:/(\d{1,2}))?)?(?![\d.])")
VER = re.compile(r"(?<![\d.])\d+\.\d+\.\d+(?:\.\d+)?|(?<=[A-Za-z])\d+\.\d{2}(?![\d%])")


def base_value(s):
    """A number with its 萬/億/K/M/B unit applied, as the facts() keys are ("40 萬" -> "400000")."""
    m = re.search(r"(\d[\d,]*(?:\.\d+)?)\s*(萬|万|億|K|k|M|B)?", str(s).replace("US$", "").replace("NT$", "").replace("$", ""))
    if not m:
        return None
    return f"{float(m.group(1).replace(',', '')) * UNIT.get(m.group(2) or '', 1):g}"


def norm_num(s):
    s = s.replace(",", "").replace("US$", "").replace("NT$", "").replace("$", "")
    m = re.match(r"\d+(?:\.\d+)?", s)
    return m.group(0) if m else s


def source_text(path):
    """Plain text of one source file. Office files are zip archives of XML: read with the standard library."""
    import zipfile, html as _h, subprocess, shutil
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".pptx", ".docx"):
        out = []
        try:
            with zipfile.ZipFile(path) as z:
                for n in z.namelist():
                    if (ext == ".xlsx" and (n == "xl/sharedStrings.xml" or n.startswith("xl/worksheets/sheet"))) or \
                       (ext == ".pptx" and n.startswith("ppt/slides/slide") and n.endswith(".xml")) or \
                       (ext == ".docx" and n in ("word/document.xml",)):
                        x = z.read(n).decode("utf-8", "replace")
                        out.append(_h.unescape(re.sub(r"<[^>]+>", " ", x)))
        except zipfile.BadZipFile:
            print(f"! cannot read {path} (not a valid {ext} file)", file=sys.stderr)
        return " ".join(out)
    if ext == ".pdf":
        if shutil.which("pdftotext"):
            return subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True).stdout
        print(f"! {path}: PDF text not readable here; export it to .txt and pass that file", file=sys.stderr)
        return ""
    if ext in (".csv", ".tsv"):
        import csv as _csv
        with open(path, encoding="utf-8-sig", errors="replace", newline="") as f:
            return " ".join(" ".join(row) for row in _csv.reader(f, delimiter="\t" if ext == ".tsv" else ","))
    return open(path, encoding="utf-8", errors="replace").read()


def check_derived(spec, src_nums):
    """Recompute each derived number; report wrong results and inputs missing from the sources."""
    import ast, operator as op
    ops = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.USub: op.neg, ast.UAdd: op.pos}
    def ev(n):
        if isinstance(n, ast.Expression): return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)): return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in ops: return ops[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in ops: return ops[type(n.op)](ev(n.operand))
        raise ValueError("only numbers and + - * / ( ) are allowed")
    bad, missing = [], []
    for d in spec.get("derived", []):
        shown = str(d.get("value", "")).replace("−", "-").replace(",", "")
        m = re.search(r"-?\d+(?:\.\d+)?", shown)
        try:
            got = ev(ast.parse(str(d.get("formula", "")).replace("−", "-").replace("×", "*").replace("÷", "/"), mode="eval"))
        except Exception as e:
            bad.append({"value": d.get("value"), "problem": f"formula not readable: {e}"}); continue
        if not m:
            bad.append({"value": d.get("value"), "problem": "no number in value"}); continue
        want = float(m.group(0)); dec = len(m.group(0).split(".")[1]) if "." in m.group(0) else 0
        if abs(round(got, dec) - want) > 10 ** -dec / 2 + 1e-9 and abs(round(abs(got), dec) - abs(want)) > 10 ** -dec / 2 + 1e-9:
            bad.append({"value": d.get("value"), "formula": d.get("formula"), "computes": round(got, max(dec, 2))})
        if src_nums is not None:
            for x in d.get("from", []):
                k = norm_num(str(x)); kb = base_value(x)
                try:
                    plain = f"{float(k):g}"
                except (TypeError, ValueError):
                    continue
                if plain not in src_nums and kb not in src_nums:
                    missing.append({"value": d.get("value"), "input": x})
    return bad, missing


def derived_values(spec):
    vals = set()
    for d in spec.get("derived", []):
        m = re.search(r"\d[\d,]*(?:\.\d+)?", str(d.get("value", "")))
        if m:
            vals.add(f"{float(m.group(0).replace(',', '')):g}")
    return vals


def facts(spec):
    """Comparable facts: numbers in base units, dates, versions. Whole numbers below 10 (counts such as
    "3 steps") are skipped; decimals are always kept, because scores and times (4.3, 2.6 h) matter most."""
    nums, dates, vers = collections.Counter(), collections.Counter(), collections.Counter()
    for p, t in walk(spec):
        if p.endswith((".icon", ".color", ".id", ".kind", ".status", ".state", ".lang", ".style", ".report_type", ".formula", ".theme", ".position", ".src", ".src_dark")) or ".areas" in p or ".cols" in p or "layout" in p or p.startswith("derived") or ".from[" in p:
            continue
        if p.endswith((".value", "y_min", "y_max")) or p.startswith("meta.sources") or p.endswith(("doc_title", "kicker", "as_of", "version", "author")):
            continue
        t = re.sub(r"\{\{icon:[^}]+\}\}", "", t)
        for m in DATE.finditer(t):
            dates[m.group(0).replace("–", "-")] += 1
        t = DATE.sub(" ", t)
        for m in VER.finditer(t):
            vers[m.group(0)] += 1
        t = VER.sub(" ", t)
        t = re.sub(r"\d{1,2}\s*[–-]\s*\d{1,2}\s*月|\d{1,2}\s*月", " ", t)   # months: 10 月初, 11–12 月
        t = re.sub(r"(?i)\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s*[–-]?\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)?[a-z]*\b", " ", t)
        t = re.sub(r"(?<!\d)(19|20)\d{2}(?!\d)", " ", t)        # years appear in both anyway
        for m in re.finditer(r"(\d[\d,]*(?:\.\d+)?)\s*(萬|万|億|K|k|M|B)?(?![A-Za-z])", t):
            v = float(m.group(1).replace(",", "")) * UNIT.get(m.group(2) or "", 1)
            if v < 10 and not m.group(2) and "." not in m.group(1):
                continue
            nums[f"{v:g}"] += 1
    return nums, dates, vers


def bilingual(zh, en):
    out = []
    for kind, a, b in zip(("number", "date", "version"), facts(zh), facts(en)):
        for k in sorted(set(a) | set(b)):
            if (a[k] > 0) != (b[k] > 0):
                out.append({kind: k, "zh": a[k], "en": b[k]})
    return out


def numbers(spec):
    out = []
    for p, t in walk(spec):
        if p.endswith((".icon", ".color", ".id", ".kind", ".status", ".state", ".lang", ".style", ".report_type")) or ".areas" in p or ".cols" in p or "layout" in p:
            continue
        if p.endswith((".value", "y_min", "y_max")):
            continue
        for m in NUM.finditer(re.sub(r"\{\{icon:[^}]+\}\}", "", t)):
            out.append((norm_num(m.group(0)), m.group(0).strip(), p))
    return out


def layout_check(html):
    try:
        from playwright.sync_api import sync_playwright
        import render
    except Exception:
        return {"skipped": "no browser engine"}
    js = """() => {
      const boxes = [];
      document.querySelectorAll('.zone .blocks *').forEach(el => {
        if (el.children.length || !el.textContent.trim()) return;
        const r = el.getBoundingClientRect(); if (r.width < 2) return;
        boxes.push({t: el.textContent.trim().slice(0, 40), x: r.left, y: r.top, w: r.width, h: r.height, p: el.parentElement,
                    over: el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).overflow === 'hidden'});
      });
      const hits = [];
      for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
        const a = boxes[i], b = boxes[j];
        if (a.p === b.p && a.p.tagName.toLowerCase() === 'text') continue;   // two lines of one SVG label
        const ox = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x), oy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
        // line boxes of stacked labels touch by a few px; real overlap covers a good part of the text height
        if (ox > 3 && oy > Math.max(3, 0.35 * Math.min(a.h, b.h))) hits.push([a.t, b.t]);
      }
      const zones = [...document.querySelectorAll('.zone')].map(z => {
        const r = z.getBoundingClientRect(), inner = z.querySelector('.blocks');
        // how much of the zone the content fills (from the zone top to the bottom of its last element)
        let bottom = r.top;
        inner.querySelectorAll(':scope > *').forEach(c => { const b = c.getBoundingClientRect(); if (b.height > 0) bottom = Math.max(bottom, b.bottom); });
        return {zone: z.dataset.zone, overflow: inner.scrollHeight > inner.clientHeight + 4,
                fill: r.height > 0 ? (bottom - r.top) / r.height : 1, centered: z.classList.contains('fit-center') || z.classList.contains('fit-content')};
      });
      const leadsCut = [...document.querySelectorAll('.lead')].filter(e => e.scrollWidth > e.clientWidth + 1).map(e => e.closest('.zone').dataset.zone);
      // rendered text size in page px (the zoom that fits the page is taken out, so 14 means 14)
      const wrap = document.querySelector('.wrap');
      const z = parseFloat(wrap && wrap.style.zoom) || 1;
      const rectZoomed = wrap ? Math.abs(wrap.getBoundingClientRect().width - 1848) < 3 : true;
      // 14 and 18 (diagrams may scale down to 12), 30-48 for the title and big numbers
      const ok = px => (px >= 12 && px <= 15.2) || (px >= 16.5 && px <= 19.5) || (px >= 30 && px <= 48);
      const sizes = [];
      document.querySelectorAll('.wrap *').forEach(el => {
        if (!el.textContent.trim() || [...el.childNodes].every(n => n.nodeType !== 3 || !n.textContent.trim())) return;
        if (el.closest('.foot-meta')) return;
        let fs = parseFloat(getComputedStyle(el).fontSize);
        const svg = el.closest('svg');
        if (svg && svg.viewBox && svg.viewBox.baseVal && svg.viewBox.baseVal.width) {
          const sc = svg.getBoundingClientRect().width / svg.viewBox.baseVal.width;
          fs = fs * sc / (rectZoomed ? z : 1);
        }
        if (!ok(fs)) sizes.push({t: el.textContent.trim().slice(0, 30), px: Math.round(fs * 10) / 10,
          zone: (el.closest('.zone') || {dataset: {}}).dataset.zone || 'page'});
      });
      return {off_scale_text: sizes.slice(0, 15), off_scale_count: sizes.length, overlaps: hits.slice(0, 12), zones_overflowing: zones.filter(z => z.overflow).map(z => z.zone), leads_cut: leadsCut,
              zones_mostly_empty: zones.filter(z => !z.centered && z.fill < 0.7).map(z => z.zone + ' (' + Math.round(z.fill * 100) + '% filled)'),
              clipped: boxes.filter(b => b.over).map(b => b.t), page_height: document.body.scrollHeight};
    }"""
    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception:
            exe = render.find_browser()
            if not exe:
                return {"skipped": "no browser"}
            b = p.chromium.launch(executable_path=exe)
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        pg.goto("file://" + os.path.abspath(html)); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        pg.evaluate(render.FIT_JS); pg.wait_for_timeout(200)
        r = pg.evaluate(js); b.close()
    r["page_overflow"] = r["page_height"] > 1082
    return r


HAS_ICON = re.compile(r"\{\{icon:[^}]+\}\}")
HOLE_WORDS = ["素材未提供", "未提供", "未公開", "待補", "待提供", "資料不足", "不詳", "N/A", "n/a", "not given",
              "not provided", "not disclosed", "unknown", "TBC"]


def _blocks(o, zone=None):
    """Every block in the spec with the zone it sits in (columns and card diagrams included)."""
    if isinstance(o, dict):
        if "zones" in o:
            for z in o["zones"]:
                yield from _blocks(z.get("blocks", []), z.get("id"))
            return
        if "type" in o:
            yield zone, o
        for k, v in o.items():
            if k in ("children", "items", "blocks", "diagram", "chart") or isinstance(v, (list, dict)):
                yield from _blocks(v, zone)
    elif isinstance(o, list):
        for v in o:
            yield from _blocks(v, zone)


def icon_gaps(spec):
    """Category rows that a reader sorts at a glance but that carry no icon (references/icons.md, step 1).
    It flags what is missing, not what is wrong: a block can say "icons": false to record the choice."""
    out, seen = [], set()
    def first_cell(row):
        return str(row[0]) if isinstance(row, list) and row else ""
    for zone, b in _blocks(spec):
        if id(b) in seen or b.get("icons") is False:
            continue
        seen.add(id(b))
        t = b.get("type")
        rows = []
        if t == "table" and b.get("header"):
            rows = [(first_cell(r), False) for r in b.get("rows", []) if first_cell(r).strip()]
            rows = [(c, bool(HAS_ICON.search(c))) for c, _ in rows]
        elif t == "table":
            rows = [(r.get("key", ""), bool(r.get("icon") or HAS_ICON.search(str(r.get("key", ""))))) for r in b.get("rows", [])]
        elif t in ("steps", "issues", "cards"):
            key = {"steps": "title", "issues": "problem", "cards": "tag"}[t]
            rows = [(str(i.get(key) or i.get("title") or ""), bool(i.get("icon") or HAS_ICON.search(str(i.get(key, ""))))) for i in b.get("items", [])]
        elif t == "timeline":
            rows = [(str(e.get("label", "")), bool(e.get("icon"))) for e in b.get("events", [])]
        elif t in ("chips", "speclines"):
            rows = [(str(r.get("label", "")), bool(r.get("icon"))) for r in b.get("rows", [])]
        missing = [lab for lab, ok in rows if not ok]
        if len(rows) >= 2 and missing:
            out.append({"zone": zone, "block": t, "without_icon": [re.sub(r"[*=!^+]", "", m)[:20] for m in missing][:8],
                        "of": len(rows)})
    return out


def repeated_numbers(spec):
    """Each number appears once, next to the claim it proves (references/layout.md). The title may restate
    one headline figure, so title occurrences are counted apart. Chart data values are not counted."""
    where = collections.defaultdict(list)
    skip = (".icon", ".color", ".id", ".kind", ".status", ".state", ".lang", ".style", ".report_type", ".theme",
            ".value", ".values", "y_min", "y_max", ".formula", ".src", ".position")
    for p, t in walk(spec):
        if p.startswith(("meta", "derived", "doc_title", "layout", "links")) or ".from[" in p or ".values[" in p:
            continue
        if p.endswith(skip) or re.search(r"\.(value|values|before|after|actual|target|compare|max|delta_value)(\[\d+\])?$", p):
            continue
        n, _, _ = facts({"t": t})
        for k in n:
            m = re.match(r"zones\[(\d+)\]", p)
            where[k].append("title" if p == "title" else (spec["zones"][int(m.group(1))].get("id", m.group(1)) if m else p))
    cross, same = [], []
    for k, ps in where.items():
        zones = sorted({x for x in ps if x != "title"})
        if len(zones) > 1:
            cross.append({"number": k, "times": len(ps), "where": ps})
        elif len(ps) > 1 and len(zones) == 1 and ps.count(zones[0]) > 1:
            same.append({"number": k, "times": len(ps), "where": ps})
    return sorted(cross, key=lambda x: -x["times"]), sorted(same, key=lambda x: -x["times"])


def holes(spec):
    out = []
    for p, t in walk(spec):
        if p.startswith(("meta", "derived")):
            continue
        for w in HOLE_WORDS:
            if re.search(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])", t):
                out.append({"where": p, "text": t[:30]}); break
    return out


def focus(spec):
    """One highlight per chart (references/charts-and-color.md). Lists charts with more than one."""
    out = []
    for zone, b in _blocks(spec):
        for key in ("data", "items", "options"):
            items = b.get(key) if isinstance(b.get(key), list) else []
            hi = [str(it.get("label") or it.get("name") or "")[:12] for it in items
                  if isinstance(it, dict) and (it.get("highlight") or it.get("recommended"))]
            if len(hi) > 1:
                out.append({"zone": zone, "block": b.get("type"), "highlighted": hi})
    return out


def colour_check(spec, style=None):
    """Contrast of the style's colours on its own page, for the spec's theme: graphic colours (highlight,
    zone roles) >= 3:1 on the card, body text >= 4.5:1. A custom style (a company template, a brand look)
    also gets its highlight checked by check_colors.py. Built-in styles were checked when they were made."""
    import importlib
    style = style or spec.get("style", "handdrawn")
    theme = spec.get("theme", "light")
    builtin = style in ("business", "handdrawn")
    path = style if os.path.isfile(str(style)) else os.path.join(HERE, "..", "assets", "styles", f"{style}.json")
    try:
        st = json.load(open(path, encoding="utf-8"))
    except Exception:
        return {"skipped": f"style not found: {style}"}
    tok, ch = dict(st.get("tokens", {})), dict(st.get("chart", {}))
    if theme == "dark" and isinstance(st.get("dark"), dict):
        tok.update(st["dark"].get("tokens", {})); ch.update(st["dark"].get("chart", {}))
    surf = next((c for c in (tok.get("card"), tok.get("paper")) if str(c).startswith("#")), None)
    if not surf:
        return {"skipped": "no solid page colour in the style"}
    sys.path.insert(0, HERE)
    cc = importlib.import_module("check_colors")
    low = []
    for name, need in [("hi", 3), ("c-blue", 3), ("c-red", 3), ("c-green", 3), ("c-orange", 3), ("ink", 4.5), ("soft", 4.5)]:
        c = ch.get("highlight") if name == "hi" and ch.get("highlight") else tok.get(name)
        if c and str(c).startswith("#"):
            r = cc.contrast(c, surf)
            if r < need:
                low.append({"colour": name, "hex": c, "contrast": round(r, 2), "needs": need})
    out = {"style": st.get("name", style), "theme": theme, "surface": surf, "low_contrast": low, "pass": not low, "builtin": builtin}
    if not builtin and ch.get("highlight"):
        res = cc.check([ch["highlight"]], theme, surf)
        out["highlight_check"] = res
        out["pass"] = out["pass"] and res.get("ok", True)
    return out


def review(spec, other=None, html=None, sources=None):
    rep = {"lang": spec.get("lang")}
    meta = spec.get("meta", {})
    # home reports need only sources and the data date; company reports (the default) also version and author
    need = ("as_of", "sources") if str(meta.get("mode", "")).lower() == "home" else ("as_of", "version", "author", "sources")
    rep["meta_missing"] = [k for k in need if not meta.get(k)]
    title = re.sub(r"[*=!^+]", "", spec.get("title", ""))
    rep["title_is_topic"] = len(title) < 18 and any(w in title.lower() for w in TOPIC_TITLES)
    def width(t):
        t = re.sub(r"[*=!^+]", "", t)
        return sum(1 if ord(c) > 0x2E80 else 0.45 for c in t)
    rep["leads_too_long"] = [z["id"] for z in spec["zones"] if z.get("lead") and width(z["lead"]) > 40]  # rough; layout check measures
    rep["zones_without_lead"] = [z["id"] for z in spec["zones"] if not z.get("lead") and not any(b["type"] in ("steps", "timeline") for b in z.get("blocks", []))]
    steps_no_owner = []
    for p, t in walk(spec):
        pass
    for z in spec["zones"]:
        for b in z.get("blocks", []):
            if b["type"] == "steps":
                for it in b["items"]:
                    if not (it.get("owner") or it.get("due") or re.search(r"\d|未公布|TBA|TBD|未定|not set", json.dumps(it, ensure_ascii=False))):
                        steps_no_owner.append(it["title"])
    rep["steps_without_owner_or_date"] = steps_no_owner
    # design options (references/design-options.md): limits that keep them tools, not decoration
    opt = []
    if sum(1 for z in spec["zones"] if z.get("frame") == "dashed") > 1:
        opt.append("more than one dashed zone (keep it for the one zone the reader must act on)")
    for z in spec["zones"]:
        def kinds(o):   # block types anywhere inside a zone (columns, cards)
            if isinstance(o, dict):
                yield from ([o["type"]] if "type" in o else [])
                if o.get("chart"): yield "chart"
                for v in o.values(): yield from kinds(v)
            elif isinstance(o, list):
                for v in o: yield from kinds(v)
        evidence = {"chart", "bullet", "dumbbell", "slope", "waterfall", "variance", "stacked", "heatmap", "gauge", "stattile", "stat", "table"}
        if z.get("frame") == "open" and evidence & set(kinds(z.get("blocks", []))):
            opt.append(f"zone {z['id']} has no frame but holds evidence (charts or numbers); give it a frame")
    if len(spec.get("links", [])) > 3:
        opt.append("more than 3 arrows between zones")
    sm = spec.get("summary") or {}
    plain = lambda t: re.sub(r"[*=!^+\s，,。.;；：:]", "", t or "")
    if sm and plain(sm.get("lead") or sm.get("text")) and plain(sm.get("lead") or sm.get("text")) in plain(spec.get("title", "")):
        opt.append("the summary strip repeats the title")
    if spec.get("aside") and re.search(r"\d", spec["aside"].get("text", "")):
        opt.append("the aside holds a number: evidence belongs in a zone")
    if len(spec["zones"]) > 6 or len(spec["zones"]) < 4:
        opt.append(f"{len(spec['zones'])} zones (keep 4–6, background zone included)")
    rep["design_options"] = opt
    text = " ".join(t for _, t in walk(spec)).lower()
    rep["vague_words"] = sorted({w for w in VAGUE if w.lower() in text})
    icons = collections.defaultdict(set)
    def collect(o, label=None):
        if isinstance(o, dict):
            lab = o.get("label") or o.get("tag") or o.get("key") or o.get("problem") or label or (str(o.get("text") or o.get("lead") or "")[:16] or None)
            if o.get("icon"):
                icons[o["icon"]].add(re.sub(r"[*=!^+]", "", str(lab)))
            for v in o.values():
                collect(v, lab)
        elif isinstance(o, list):
            for v in o:
                collect(v, label)
    collect(spec)
    def same_topic(labels):
        def grams(l):
            l = l.lower()
            g = set(re.findall(r"[a-z0-9]{3,}", l))
            cjk = re.findall(r"[\u4e00-\u9fff]", l)
            g |= {cjk[i] + cjk[i + 1] for i in range(len(cjk) - 1)}   # overlapping bigrams
            return g
        words = [grams(l) for l in labels]
        return all(words[0] & w for w in words[1:])
    rep["icon_reuse"] = {k: sorted(v) for k, v in icons.items() if len(v) > 1 and not same_topic(sorted(v))}
    rep["icon_gaps"] = icon_gaps(spec)
    rep["repeated_numbers"], rep["repeated_in_one_zone"] = repeated_numbers(spec)
    rep["holes"] = holes(spec)
    rep["focus"] = focus(spec)
    rep["colours"] = colour_check(spec)
    nums = numbers(spec)
    rep["numbers"] = [{"value": raw, "where": p} for _, raw, p in nums]
    sn = None
    if sources:
        src_spec = {"text": " ".join(source_text(f) for f in sources)}
        sn, sd, sv = facts(src_spec)
        n, d, v = facts(spec)
        dv = derived_values(spec)
        rep["numbers_not_in_source"] = sorted([k for k in n if k not in sn and k not in dv and not any(abs(float(k) - float(x)) <= 1e-9 * max(1, float(x)) for x in sn)] +
                                              [k for k in d if k not in sd] + [k for k in v if k not in sv])
    if spec.get("derived"):
        rep["derived_wrong"], rep["derived_inputs_missing"] = check_derived(spec, sn)
    if other:
        rep["bilingual_mismatch"] = bilingual(spec, other)
    if html:
        rep["layout"] = layout_check(html)
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("specs", nargs="+")
    ap.add_argument("--html", nargs="*")
    ap.add_argument("--source", nargs="*")
    ap.add_argument("--out", help="write the JSON report here and print only the summary")
    a = ap.parse_args()
    specs = [json.load(open(f, encoding="utf-8")) for f in a.specs]
    htmls = a.html or []
    out = []
    for i, sp in enumerate(specs):
        other = specs[1 - i] if len(specs) == 2 else None
        out.append(review(sp, other, htmls[i] if i < len(htmls) else None, a.source))
    if a.out:
        json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    else:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    log = sys.stdout if a.out else sys.stderr
    print("\n--- summary ---", file=log)
    for r in out:
        flags = []
        if r["meta_missing"]: flags.append(f"meta missing {r['meta_missing']}")
        if r.get("design_options"): flags.append("design options: " + "; ".join(r["design_options"]))
        if r["title_is_topic"]: flags.append("title reads like a topic")
        if r["zones_without_lead"]: flags.append(f"zones without lead {r['zones_without_lead']}")
        if r.get("leads_too_long") and not r.get("layout"): flags.append(f"leads may be too long (run with --html to measure) {r['leads_too_long']}")
        if r["steps_without_owner_or_date"]: flags.append(f"{len(r['steps_without_owner_or_date'])} steps without owner/date")
        if r["vague_words"]: flags.append(f"vague words {r['vague_words']}")
        if r["icon_reuse"]: flags.append(f"icon reused for different things {r['icon_reuse']}")
        if r.get("bilingual_mismatch"): flags.append(f"zh/en number mismatch {r['bilingual_mismatch']}")
        if r.get("numbers_not_in_source"): flags.append(f"numbers not found in source {r['numbers_not_in_source']} (if worked out, record them under \"derived\")")
        if r.get("derived_wrong"): flags.append(f"derived numbers that do not recompute {r['derived_wrong']}")
        if r.get("derived_inputs_missing"): flags.append(f"derived-number inputs not in source {r['derived_inputs_missing']}")
        if r.get("icon_gaps"): flags.append("rows without icons " + "; ".join(f"{g['zone']}/{g['block']} {len(g['without_icon'])} of {g['of']}" for g in r["icon_gaps"]) + " (add icons where readers sort categories, or set \"icons\": false and say why)")
        if r.get("repeated_numbers"): flags.append("numbers shown more than once " + ", ".join(f"{x['number']}×{x['times']}" for x in r["repeated_numbers"][:6]))
        if r.get("holes"): flags.append(f"cells that read as holes {[h['text'] for h in r['holes']]} (ask the user or drop the row)")
        if r.get("focus"): flags.append(f"charts with more than one highlight {r['focus']} (one per chart; let the user pick which)")
        col = r.get("colours") or {}
        if col.get("pass") is False and not col.get("builtin"): flags.append(f"chart colours fail check_colors.py ({col.get('style')}, {col.get('theme')})")
        lay = r.get("layout") or {}
        if lay.get("overlaps"): flags.append(f"{len(lay['overlaps'])} text overlaps")
        if lay.get("zones_overflowing"): flags.append(f"zones overflowing {lay['zones_overflowing']}")
        if lay.get("zones_mostly_empty"): flags.append(f"zones with large empty space {lay['zones_mostly_empty']}: see references/design-options.md (never invent content)")
        if lay.get("page_overflow"): flags.append("page overflows 1080px")
        if lay.get("off_scale_count"): flags.append(f"{lay['off_scale_count']} text sizes off the 46/34/18/14 scale (scaled up, or squeezed under 12 px: give the zone more room), e.g. {lay['off_scale_text'][:3]}")
        if lay.get("leads_cut"): flags.append(f"leads cut with … {lay['leads_cut']}")
        print(f"[{r['lang']}] " + ("no automatic issues" if not flags else "; ".join(flags)), file=log)


if __name__ == "__main__":
    main()
