"""Screenshot every app screen: python tools/app_shots.py [lang] -> output/app/<lang>_<screen>.png"""
import sys, os, pathlib, asyncio
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
lang = sys.argv[1] if len(sys.argv) > 1 else "id"
out = ROOT / "output" / "app"; out.mkdir(parents=True, exist_ok=True)
url = (ROOT / "app" / "index.html").as_uri() + f"?demo&nosplash&lang={lang}"
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 400, "height": 860}, device_scale_factor=2)
    errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(url); pg.wait_for_timeout(1500)
    for s in ["home", "hive", "light", "care", "ai"]:
        pg.evaluate(f"APP.go('{s}')"); pg.wait_for_timeout(1300)
        pg.screenshot(path=str(out / f"{lang}_{s}.png"))
    pg.evaluate("APP.go('hive')"); pg.wait_for_timeout(600); pg.evaluate("APP.openSheet(2)"); pg.wait_for_timeout(900)
    pg.screenshot(path=str(out / f"{lang}_sheet.png"))
    print("ERRORS", errs)
    b.close()
