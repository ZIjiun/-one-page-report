#!/usr/bin/env python3
"""Render a one-page report HTML to PNG (16:9, 3840x2160) and PDF.

Usage:
  python3 render.py report.html [--png out.png] [--pdf out.pdf] [--no-fit]

Order of engines (no install needed when one exists):
  1. Python playwright with a Chromium it can find
  2. A Chrome / Edge / Chromium already on the computer (headless CLI)
  3. None: say so and keep the HTML (the user can open it and print to PDF)

The page is 1920 px wide. Unless --no-fit, the content is zoomed (0.75-1.15) so it
fills exactly one 1920x1080 page. A zoom below 0.8 means the page is too dense.
"""
import argparse, glob, json, os, shutil, subprocess, sys, tempfile

W, H = 1920, 1080
PAD_Y = 28          # body padding top + bottom in base.css
FIT_JS = """
() => {
  const wrap = document.querySelector('.wrap');
  wrap.style.zoom = 1; wrap.style.width = '1848px'; wrap.style.minHeight = '0px';
  const h = wrap.getBoundingClientRect().height;
  const avail = %d - %d;
  let z = Math.max(0.75, Math.min(1.15, avail / h));
  const apply = (v) => { wrap.style.zoom = v; wrap.style.width = (1848 / v) + 'px'; };
  apply(z);
  // The grid stretches to fill the page height (CSS); only shrink when it overflows.
  for (let i = 0; i < 25 && document.body.scrollHeight > %d && z > 0.75; i++) { z -= 0.01; apply(z); }
  wrap.style.minHeight = ((avail) / z) + 'px';   // then let rows grow to fill the page
  return {natural: h, zoom: z, final: document.body.scrollHeight};
}
""" % (H, PAD_Y, H)


def find_browser():
    names = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "msedge", "chrome"]
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    cands = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ] + glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome") + glob.glob(os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome"))
    for c in cands:
        if os.path.isfile(c):
            return c
    return None


def with_playwright(src, png, pdf, fit):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception:
            exe = find_browser()
            if not exe:
                raise
            b = p.chromium.launch(executable_path=exe)
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
        pg.goto("file://" + os.path.abspath(src))
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(400)
        info = pg.evaluate(FIT_JS) if fit else {"zoom": 1, "final": pg.evaluate("document.body.scrollHeight")}
        pg.wait_for_timeout(200)
        if png:
            pg.screenshot(path=png, clip={"x": 0, "y": 0, "width": W, "height": H})
        if pdf:
            pg.emulate_media(media="screen")
            pg.pdf(path=pdf, width=f"{W}px", height=f"{H}px", print_background=True, page_ranges="1")
        b.close()
        return info


def with_cli(exe, src, png, pdf):
    url = "file://" + os.path.abspath(src)
    common = [exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{H}"]
    if png:
        subprocess.run(common + ["--force-device-scale-factor=2", f"--screenshot={os.path.abspath(png)}", url], capture_output=True, timeout=120)
    if pdf:
        subprocess.run(common + ["--no-pdf-header-footer", f"--print-to-pdf={os.path.abspath(pdf)}", url], capture_output=True, timeout=120)
    return {"zoom": None, "final": None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--png")
    ap.add_argument("--pdf")
    ap.add_argument("--no-fit", action="store_true")
    a = ap.parse_args()
    if not (a.png or a.pdf):
        base = os.path.splitext(a.html)[0]
        a.png, a.pdf = base + ".png", base + ".pdf"
    engine, info = None, None
    try:
        info = with_playwright(a.html, a.png, a.pdf, not a.no_fit); engine = "playwright"
    except Exception as e:
        exe = find_browser()
        if exe:
            info = with_cli(exe, a.html, a.png, a.pdf); engine = "browser-cli"
        else:
            print(json.dumps({"engine": None, "error": f"no browser found ({e.__class__.__name__}). "
                              "Deliver the HTML; open it in Chrome/Edge and use Print > Save as PDF, or take a screenshot."}, ensure_ascii=False))
            sys.exit(2)
    out = {"engine": engine, "png": a.png if a.png and os.path.isfile(a.png) else None,
           "pdf": a.pdf if a.pdf and os.path.isfile(a.pdf) else None}
    if info and info.get("zoom"):
        out["zoom"] = round(info["zoom"], 3)
        if info["zoom"] < 0.8:
            out["warning"] = "Content is too dense for one page (zoom < 0.8). Cut content or split it."
        elif info["zoom"] >= 1.15 and info.get("natural", 0) < 760:
            out["warning"] = "Content is thin for one page: zones were stretched to fill it. Consider adding evidence or using fewer zones."
        if info.get("final") and info["final"] > H + 2:
            out["warning"] = f"Content overflows the page ({info['final']}px > {H}px). Cut content."
    if engine == "browser-cli":
        out["note"] = "Rendered with the browser command line: no auto-fit. Check the PNG for overflow."
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
