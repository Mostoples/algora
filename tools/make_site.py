"""Build the public site: landing page at /, demo app at /app/.
python tools/make_site.py  ->  site/   (then: firebase deploy --only hosting)"""
import os, re, shutil, subprocess
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, OUT, FR = os.path.join(ROOT, "site_src"), os.path.join(ROOT, "site"), os.path.join(ROOT, "output", "frames")
MEDIA = os.path.join(OUT, "media")
import sys
sys.path.insert(0, os.path.join(ROOT, "showreel"))
from brand import ffmpeg as _find_ffmpeg
FF = shutil.which("ffmpeg") or _find_ffmpeg()

def img(src, dst, crop_ratio=None, width=1600, q=82):
    im = Image.open(src).convert("RGB")
    if crop_ratio:
        w, h = im.size
        if w / h > crop_ratio: nw = int(h * crop_ratio); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else: nh = int(w / crop_ratio); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    if im.width > width: im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    im.save(os.path.join(MEDIA, dst), quality=q, method=6) if dst.endswith(".webp") else im.save(os.path.join(MEDIA, dst), quality=88)

def video(src, dst, poster_t=8):
    out = os.path.join(MEDIA, dst)
    subprocess.run([FF, "-y", "-v", "error", "-i", src, "-vf", "scale=1280:-2", "-c:v", "libx264", "-crf", "27", "-preset", "slow",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", out], check=True)
    subprocess.run([FF, "-y", "-v", "error", "-ss", str(poster_t), "-i", src, "-frames:v", "1", "-vf", "scale=1280:-2",
                    os.path.join(MEDIA, dst.replace(".mp4", ".jpg"))], check=True)

if __name__ == "__main__":
    if os.path.exists(OUT): shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT); os.makedirs(MEDIA)
    shutil.copytree(os.path.join(ROOT, "app"), os.path.join(OUT, "app"))
    swp = os.path.join(OUT, "app", "sw.js"); s = open(swp, encoding="utf-8").read()
    open(swp, "w", encoding="utf-8").write(re.sub(r'VERSION = "algora-v\d+"', 'VERSION = "algora-v2"', s))
    # root service worker that removes the old cache-first worker registered when the app lived at "/"
    open(os.path.join(OUT, "sw.js"), "w").write(
        'self.addEventListener("install",()=>self.skipWaiting());\n'
        'self.addEventListener("activate",e=>e.waitUntil(caches.keys().then(ks=>Promise.all(ks.map(k=>caches.delete(k))))'
        '.then(()=>self.registration.unregister()).then(()=>self.clients.matchAll()).then(cs=>cs.forEach(c=>c.navigate(c.url)))));\n')
    img(os.path.join(FR, "hero", "f_0250.png"), "hero.webp", 1.0, 1400)
    img(os.path.join(FR, "hero", "f_0250.png"), "og.jpg", 1.91, 1200)
    for shot, f in (("wall", 100), ("floor", 80), ("lamp", 90), ("roof", 80)):
        img(os.path.join(FR, shot, f"f_{f:04d}.png"), f"{shot}.webp", 3 / 4, 900)
    img(os.path.join(FR, "tech", "f_0810.png"), "exploded.webp", 4 / 3, 1400)
    img(os.path.join(ROOT, "output", "paper", "fig_cad.png"), "cad.webp", None, 2000)
    for k in ("home", "hive", "care"):
        img(os.path.join(ROOT, "output", "app", f"id_{k}.png"), f"app_{k}.webp", None, 600)
    for name, f in (("proto", 2050), ("r4", 1395), ("holes", 1560)):
        img(os.path.join(FR, "tech", f"f_{f:04d}.png"), f"{name}.webp", 4 / 3, 1400)
    import pypdfium2 as pdfium
    gt = pdfium.PdfDocument(os.path.join(ROOT, "output", "dokumen", "Algora_Gambar_Teknik_Hexagon.pdf"))
    for i in range(len(gt)):
        tmp = os.path.join(MEDIA, f"_gt{i + 1}.png"); gt[i].render(scale=2.2).to_pil().save(tmp)
        img(tmp, f"gt{i + 1}.webp", None, 1800); os.remove(tmp)
    dl = os.path.join(OUT, "downloads"); os.makedirs(dl)
    shutil.copy(os.path.join(ROOT, "output", "dokumen", "Algora_Gambar_Teknik_Hexagon.pdf"), os.path.join(dl, "Algora_Gambar_Teknik.pdf"))
    shutil.copy(os.path.join(ROOT, "output", "dokumen", "Dokumen_Teknis_Algora.pdf"), os.path.join(dl, "Algora_Dokumen_Teknis.pdf"))
    video(os.path.join(ROOT, "output", "ALGORA_showreel_id.mp4"), "showreel.mp4", 9)
    video(os.path.join(ROOT, "output", "ALGORA_gambar_teknik_3D.mp4"), "tech.mp4", 27)
    total = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(OUT) for f in fs)
    print("site built", round(total / 1e6, 1), "MB")
