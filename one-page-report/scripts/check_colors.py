#!/usr/bin/env python3
"""Check a categorical chart palette for colour-blind safety and contrast.

Usage:
  python3 check_colors.py "#2a78d6,#eb6834,#1baf7a" [--mode light|dark] [--surface #ffffff] [--pairs adjacent|all]

Written from public sources (no third-party code):
  - OKLab: Bjorn Ottosson, "A perceptual color space for image processing" (2020)
  - Colour-vision deficiency: Machado, Oliveira & Fernandes (2009), severity 1.0
  - Contrast: WCAG 2.x relative luminance ratio

Checks (thresholds follow common data-viz practice):
  band      OKLCH lightness inside the mode band (light 0.43-0.77, dark 0.48-0.67)
  chroma    OKLCH chroma >= 0.10, so a hue does not read as grey
  cvd       neighbour pairs under protanopia/deuteranopia: dE >= 8 target, 6-8 needs labels, < 6 fail
  normal    neighbour pairs with normal vision: dE >= 15 (hard)
  contrast  each colour vs surface >= 3:1, else labels or a table must carry the values
dE is Euclidean distance in OKLab x 100. Exit code 1 on any FAIL.
If the environment has the built-in `dataviz` skill, prefer its validator; this is the offline stand-in.
"""
import argparse, itertools, json, math, sys

BANDS = {"light": (0.43, 0.77), "dark": (0.48, 0.67)}
SURFACES = {"light": "#fcfcfb", "dark": "#1a1a19"}
MACHADO = {  # severity 1.0, applied to linear RGB
    "protan": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
    "deutan": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
}


def hex_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6 or any(c not in "0123456789abcdefABCDEF" for c in h):
        raise ValueError(f"not a hex colour: #{h}")
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin_rgb(h):
    return [to_lin(c) for c in hex_rgb(h)]


def oklab_lin(rgb):
    r, g, b = rgb
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return [0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s]


def oklch(h):
    L, a, b = oklab_lin(lin_rgb(h))
    return L, math.hypot(a, b)


def sim(h, kind):
    rgb = lin_rgb(h)
    if kind == "normal":
        return rgb
    M = MACHADO[kind]
    return [min(1, max(0, sum(M[i][j] * rgb[j] for j in range(3)))) for i in range(3)]


def dE(a, b, kind):
    A, B = oklab_lin(sim(a, kind)), oklab_lin(sim(b, kind))
    return 100 * math.dist(A, B)


def luminance(h):
    r, g, b = lin_rgb(h)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    hi, lo = sorted([luminance(a), luminance(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def check(palette, mode="light", surface=None, pairs="adjacent"):
    surface = surface or SURFACES[mode]
    lo, hi = BANDS[mode]
    res = []
    out_band = [(c, round(oklch(c)[0], 3)) for c in palette if not lo <= oklch(c)[0] <= hi]
    res.append(("band", "FAIL" if out_band else "PASS", out_band or f"all inside L {lo}-{hi}"))
    grey = [(c, round(oklch(c)[1], 3)) for c in palette if oklch(c)[1] < 0.10]
    res.append(("chroma", "FAIL" if grey else "PASS", grey or "all >= 0.10"))
    plist = list(zip(palette, palette[1:])) if pairs == "adjacent" else list(itertools.combinations(palette, 2))
    if plist:
        worst = min(((min(dE(a, b, "protan"), dE(a, b, "deutan")), a, b) for a, b in plist))
        st = "PASS" if worst[0] >= 8 else ("WARN" if worst[0] >= 6 else "FAIL")
        res.append(("cvd", st, f"worst {worst[1]}~{worst[2]} dE {worst[0]:.1f}" + (" (labels required)" if st == "WARN" else "")))
        wn = min(((dE(a, b, "normal"), a, b) for a, b in plist))
        res.append(("normal", "PASS" if wn[0] >= 15 else "FAIL", f"worst {wn[1]}~{wn[2]} dE {wn[0]:.1f}"))
    low = [(c, round(contrast(c, surface), 2)) for c in palette if contrast(c, surface) < 3]
    res.append(("contrast", "WARN" if low else "PASS", (low and f"{low} < 3:1 vs {surface}: show labels or a table") or f"all >= 3:1 vs {surface}"))
    ok = not any(s == "FAIL" for _, s, _ in res)
    return {"ok": ok, "mode": mode, "surface": surface, "pairs": pairs, "checks": [{"check": n, "status": s, "detail": d} for n, s, d in res]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("palette")
    ap.add_argument("--mode", default="light", choices=["light", "dark"])
    ap.add_argument("--surface")
    ap.add_argument("--pairs", default="adjacent", choices=["adjacent", "all"])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    pal = [p.strip() for p in a.palette.split(",") if p.strip()]
    r = check(pal, a.mode, a.surface, a.pairs)
    if a.json:
        print(json.dumps(r, ensure_ascii=False))
    else:
        print(f"Palette ({r['mode']}, surface {r['surface']}, {r['pairs']} pairs): {len(pal)} colours")
        for c in r["checks"]:
            print(f"  [{c['status']}] {c['check']:<9} {c['detail']}")
        print("  -> " + ("OK" if r["ok"] else "FAILED: fix the marked checks"))
    sys.exit(0 if r["ok"] else 1)


if __name__ == "__main__":
    main()
