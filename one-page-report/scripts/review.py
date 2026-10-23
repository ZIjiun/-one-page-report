#!/usr/bin/env python3
"""Automatic part of the self-review (references/review-checklist.md).

Usage:
  python3 review.py SPEC.zh.json [SPEC.en.json] [--html A.html [B.html]] [--source notes.txt ...] [--out review.json]

Checks:
  numbers   every number in the spec, with where it appears (for tracing to the material);
            with --source, numbers not found in the source files are flagged
  bilingual numbers/dates in the zh and en specs must match (as multisets)
  meta      data date, version, author, sources present
  logic     title is not a bare topic; zones have leads; next steps have owners/dates or say so
  words     vague or "AI feel" phrases (zh and en lists)
  layout    with --html: renders in the browser and reports overlapping text and overflow
  icons     the same icon used for two different labels
Prints a JSON report and a short text summary. Exit 0 always (it advises, it does not block).
"""
import argparse, collections, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
NUM = re.compile(r"(?<![\w.])(?:US\$|\$|NT\$)?\d[\d,]*(?:\.\d+)?\s*(?:%|萬|億|K|M|B|fps|p|元|人|則|套|個|分|天|週|年|月)?")
VAGUE = ["大幅", "顯著", "全面", "賦能", "打造", "優化了", "提升了", "持續努力", "相關", "一定程度",
         "significantly", "robust", "seamless", "leverage", "synergy", "cutting-edge", "world-class",
         "best-in-class", "various", "a number of", "going forward", "empower", "unlock"]
TOPIC_TITLES = ["報告", "說明", "概況", "簡介", "update", "report", "overview", "summary"]


def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
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
VER = re.compile(r"(?<![\d.])\d+\.\d+\.\d+(?:\.\d+)?|(?<=[A-Za-z ])\d+\.\d{2}(?![\d%])")


def norm_num(s):
    s = s.replace(",", "").replace("US$", "").replace("NT$", "").replace("$", "")
    m = re.match(r"\d+(?:\.\d+)?", s)
    return m.group(0) if m else s


def facts(spec):
    """Comparable facts: numbers in base units, dates, versions. Small counts (< 10) are skipped."""
    nums, dates, vers = collections.Counter(), collections.Counter(), collections.Counter()
    for p, t in walk(spec):
        if p.endswith((".icon", ".color", ".id", ".kind", ".status", ".state", ".lang", ".style", ".report_type")) or ".areas" in p or ".cols" in p or "layout" in p:
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
            if v < 10 and not m.group(2):
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
        boxes.push({t: el.textContent.trim().slice(0, 40), x: r.left, y: r.top, w: r.width, h: r.height,
                    over: el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).overflow === 'hidden'});
      });
      const hits = [];
      for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
        const a = boxes[i], b = boxes[j];
        const ox = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x), oy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
        if (ox > 3 && oy > 3) hits.push([a.t, b.t]);
      }
      const zones = [...document.querySelectorAll('.zone')].map(z => {
        const r = z.getBoundingClientRect(), inner = z.querySelector('.blocks');
        return {zone: z.dataset.zone, overflow: inner.scrollHeight > inner.clientHeight + 4};
      });
      const leadsCut = [...document.querySelectorAll('.lead')].filter(e => e.scrollWidth > e.clientWidth + 1).map(e => e.closest('.zone').dataset.zone);
      return {overlaps: hits.slice(0, 12), zones_overflowing: zones.filter(z => z.overflow).map(z => z.zone), leads_cut: leadsCut,
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


def review(spec, other=None, html=None, sources=None):
    rep = {"lang": spec.get("lang")}
    meta = spec.get("meta", {})
    rep["meta_missing"] = [k for k in ("as_of", "version", "author", "sources") if not meta.get(k)]
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
    text = " ".join(t for _, t in walk(spec)).lower()
    rep["vague_words"] = sorted({w for w in VAGUE if w.lower() in text})
    icons = collections.defaultdict(set)
    def collect(o, label=None):
        if isinstance(o, dict):
            lab = o.get("label") or o.get("tag") or o.get("key") or o.get("problem") or label
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
    nums = numbers(spec)
    rep["numbers"] = [{"value": raw, "where": p} for _, raw, p in nums]
    if sources:
        src_spec = {"text": " ".join(open(f, encoding="utf-8", errors="replace").read() for f in sources)}
        sn, sd, sv = facts(src_spec)
        n, d, v = facts(spec)
        rep["numbers_not_in_source"] = sorted([k for k in n if k not in sn and not any(abs(float(k) - float(x)) <= 1e-9 * max(1, float(x)) for x in sn)] +
                                              [k for k in d if k not in sd] + [k for k in v if k not in sv])
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
        if r["title_is_topic"]: flags.append("title reads like a topic")
        if r["zones_without_lead"]: flags.append(f"zones without lead {r['zones_without_lead']}")
        if r.get("leads_too_long") and not r.get("layout"): flags.append(f"leads may be too long (run with --html to measure) {r['leads_too_long']}")
        if r["steps_without_owner_or_date"]: flags.append(f"{len(r['steps_without_owner_or_date'])} steps without owner/date")
        if r["vague_words"]: flags.append(f"vague words {r['vague_words']}")
        if r["icon_reuse"]: flags.append(f"icon reused for different things {r['icon_reuse']}")
        if r.get("bilingual_mismatch"): flags.append(f"zh/en number mismatch {r['bilingual_mismatch']}")
        if r.get("numbers_not_in_source"): flags.append(f"numbers not found in source {r['numbers_not_in_source']}")
        lay = r.get("layout") or {}
        if lay.get("overlaps"): flags.append(f"{len(lay['overlaps'])} text overlaps")
        if lay.get("zones_overflowing"): flags.append(f"zones overflowing {lay['zones_overflowing']}")
        if lay.get("page_overflow"): flags.append("page overflows 1080px")
        if lay.get("leads_cut"): flags.append(f"leads cut with … {lay['leads_cut']}")
        print(f"[{r['lang']}] " + ("no automatic issues" if not flags else "; ".join(flags)), file=log)


if __name__ == "__main__":
    main()
