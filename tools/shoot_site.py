"""Screenshot the landing page at key scroll positions + report console errors.
python tools/shoot_site.py [url] [desktop|mobile] -> %TEMP%/claude/shots/*.png"""
import os, sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765/"
MODE = sys.argv[2] if len(sys.argv) > 2 else "desktop"
OUT = os.path.join(os.environ["TEMP"], "claude", "shots"); os.makedirs(OUT, exist_ok=True)
VP = dict(width=1440, height=900) if MODE == "desktop" else dict(width=390, height=844)
STOPS = [("hero", "#top", 0), ("problem", "#masalah", 0.2), ("explode0", ".explode", 0.02), ("explode50", ".explode", 0.3),
         ("explode100", ".explode", 0.62), ("builder", "#builder", 0.15), ("cycle", "#siklus", 0.1), ("app", "#aplikasi", 0.1),
         ("specs", "#spesifikasi", 0.1), ("gallery", "#galeri", 0.15), ("video", "#video", 0.1), ("cta", "#unduh", 0.0)]

with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport=VP); errs = []
    pg.on("console", lambda m: errs.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
    pg.on("pageerror", lambda e: errs.append(f"pageerror: {e}"))
    pg.goto(URL, wait_until="networkidle", timeout=90000); pg.wait_for_timeout(5000)
    for name, sel, frac in STOPS:
        y = pg.evaluate(f"""(()=>{{const e=document.querySelector('{sel}');const r=e.getBoundingClientRect();return r.top+scrollY+r.height*{frac};}})()""")
        pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(1800)
        pg.screenshot(path=os.path.join(OUT, f"{MODE}_{name}.png"))
    print("scrollWidth", pg.evaluate("document.documentElement.scrollWidth"), "viewport", VP["width"])
    print("\n".join(errs[:20]) or "no console errors")
    b.close()
