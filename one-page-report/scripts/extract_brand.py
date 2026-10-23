#!/usr/bin/env python3
"""Make a style file from a company PowerPoint (.pptx or .potx). Standard library only.

Usage:
  python3 extract_brand.py company.pptx --out my-company.json [--logo-out my-company-logo.png]

Reads the theme colours and fonts, the master background and the largest picture on the
slide master / first layout (candidate logo). Writes a style based on
assets/styles/brand-template.json. Paid fonts are referenced by name only, never copied.
"""
import argparse, colorsys, json, os, re, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_colors as cc  # noqa: E402

TEMPLATE = os.path.join(os.path.dirname(HERE), "assets", "styles", "brand-template.json")


def hexs(h):
    return "#" + h.lower()


def hue_of(h):
    r, g, b = cc.hex_rgb(h)
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    return hh * 360, ll, ss


def tint(h, amount=0.94):
    r, g, b = cc.hex_rgb(h)
    return "#" + "".join(f"{int(round((c + (1 - c) * amount) * 255)):02x}" for c in (r, g, b))


def darken_for_text(h, surface="#ffffff"):
    """Darken until contrast >= 4.5 for text."""
    r, g, b = cc.hex_rgb(h)
    for k in range(0, 30):
        f = 1 - k * 0.03
        c = "#" + "".join(f"{int(round(x * f * 255)):02x}" for x in (r, g, b))
        if cc.contrast(c, surface) >= 4.5:
            return c
    return "#16191f"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx"); ap.add_argument("--out", required=True); ap.add_argument("--logo-out")
    a = ap.parse_args()
    z = zipfile.ZipFile(a.pptx)
    names = z.namelist()
    theme = next((n for n in sorted(names) if re.match(r"ppt/theme/theme\d+\.xml", n)), None)
    if not theme:
        sys.exit("no theme found in the file")
    t = z.read(theme).decode("utf-8", "replace")
    colors = {}
    for slot in ("dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6"):
        m = re.search(rf"<a:{slot}>.*?(?:srgbClr val=\"([0-9A-Fa-f]{{6}})\"|lastClr=\"([0-9A-Fa-f]{{6}})\").*?</a:{slot}>", t, re.S)
        if m:
            colors[slot] = hexs(m.group(1) or m.group(2))
    fonts = {}
    for part, key in (("majorFont", "major"), ("minorFont", "minor")):
        m = re.search(rf"<a:{part}>(.*?)</a:{part}>", t, re.S)
        if m:
            lat = re.search(r'<a:latin typeface="([^"]*)"', m.group(1))
            ea = re.search(r'<a:ea typeface="([^"]*)"', m.group(1))
            hant = re.search(r'<a:font script="Hant" typeface="([^"]*)"', m.group(1))
            fonts[key] = {"latin": lat.group(1) if lat else "", "ea": (hant.group(1) if hant else (ea.group(1) if ea else ""))}
    # background of the first master
    bg = None
    master = next((n for n in sorted(names) if re.match(r"ppt/slideMasters/slideMaster\d+\.xml", n)), None)
    if master:
        mx = z.read(master).decode("utf-8", "replace")
        m = re.search(r"<p:bg>.*?srgbClr val=\"([0-9A-Fa-f]{6})\"", mx, re.S)
        if m:
            bg = hexs(m.group(1))
    # candidate logo: largest image referenced by master or first layout
    logo = None
    cands = []
    for rel in [n for n in names if re.match(r"ppt/(slideMasters|slideLayouts)/_rels/.*\.rels", n)]:
        for tgt in re.findall(r'Target="\.\./media/([^"]+)"', z.read(rel).decode("utf-8", "replace")):
            p = "ppt/media/" + tgt
            if p in names and os.path.splitext(p)[1].lower() in (".png", ".jpg", ".jpeg", ".svg"):
                cands.append((z.getinfo(p).file_size, p))
    if cands and a.logo_out:
        _, p = max(cands)
        out = a.logo_out if os.path.splitext(a.logo_out)[1] else a.logo_out + os.path.splitext(p)[1]
        open(out, "wb").write(z.read(p)); logo = os.path.abspath(out)

    style = json.load(open(TEMPLATE, encoding="utf-8"))
    style["name"] = os.path.splitext(os.path.basename(a.out))[0]
    style["description"] = f"Extracted from {os.path.basename(a.pptx)}"
    tk = style["tokens"]; notes = []
    surface = bg or colors.get("lt1", "#ffffff")
    if cc.luminance(surface) < 0.5:
        notes.append(f"template background {surface} is dark; report keeps a light page for print")
        surface = "#ffffff"
    tk["paper"] = surface
    if colors.get("dk1"):
        tk["ink"] = colors["dk1"] if cc.contrast(colors["dk1"], surface) >= 7 else tk["ink"]
    accents = [colors[k] for k in ("accent1", "accent2", "accent3", "accent4", "accent5", "accent6") if k in colors]
    if accents:
        main = accents[0]
        tk["c-blue"] = darken_for_text(main, surface); tk["bg-blue"] = tint(main)
        used = {0}
        def take(pred, role):
            for i, c in enumerate(accents):
                if i in used:
                    continue
                h, l, s_ = hue_of(c)
                if s_ > 0.25 and pred(h):
                    used.add(i); tk[f"c-{role}"] = darken_for_text(c, surface); tk[f"bg-{role}"] = tint(c); return True
            return False
        take(lambda h: h < 20 or h > 340, "red")
        take(lambda h: 85 < h < 170, "green")
        take(lambda h: 20 <= h < 55, "orange")
        take(lambda h: 250 < h < 300, "purple")
        take(lambda h: 160 <= h < 200, "teal")
        hl = accents[0]
        res = cc.check([hl, style["chart"]["context"]], "light", surface)
        cvd = next(c for c in res["checks"] if c["check"] == "cvd")
        if cc.contrast(hl, surface) >= 3 and cvd["status"] != "FAIL":
            style["chart"]["highlight"] = hl; tk["hi"] = hl; tk["hi-bg"] = tint(hl, 0.9); tk["hi-text"] = darken_for_text(hl, surface)
        else:
            notes.append(f"accent1 {hl} kept out of charts (contrast {cc.contrast(hl, surface):.2f}:1, cvd {cvd['status']}); default blue used")
    f = fonts.get("minor") or fonts.get("major") or {}
    if f.get("latin"):
        style["fonts"]["en"]["family"] = f'"{f["latin"]}", "Segoe UI", Helvetica, Arial, sans-serif'
    if f.get("ea") or f.get("latin"):
        zh = f.get("ea") or f.get("latin")
        style["fonts"]["zh"]["family"] = f'"{zh}", "Microsoft JhengHei", "PingFang TC", "Noto Sans CJK TC", sans-serif'
    style["logo"] = logo
    style["extracted"] = {"theme_colors": colors, "fonts": fonts, "background": bg, "notes": notes}
    json.dump(style, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({"style": a.out, "colors": colors, "fonts": fonts, "logo": logo, "notes": notes}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
