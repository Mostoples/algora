"""Komposit video gambar teknik 3D (PIL + FFmpeg).  python showreel/tech_compose.py [--test t1,t2,...]
Input : output/frames/tech/f_####.png + anchors.json (blender/tech_video.py)
Output: output/ALGORA_gambar_teknik_3D.mp4 (1920x1080, 30 fps)"""
import os, sys, json, math, subprocess, shutil
from multiprocessing import Pool
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brand import *

W, H, FPS, DUR = 1920, 1080, 30, 75.0
NF = int(DUR * FPS)
FR = os.environ.get("TECH_FR") or os.path.join(ROOT, "output", "frames", "tech")
B = os.path.join(ROOT, "showreel", "build", "tech"); os.makedirs(B, exist_ok=True)
DIMS = json.load(open(os.path.join(ROOT, "output", "cnc", "dims.json")))
ANCH = None
GREEN, RED, WHITE_, AMBER = (46, 160, 67), (229, 72, 77), (255, 255, 255), (230, 160, 40)
PART = {"A": ((207, 232, 250), "Lembar depan", "akrilik bening 5 mm"), "C1": ((150, 205, 235), "Cincin 1", "akrilik 10 mm"),
        "C2": ((150, 205, 235), "Cincin 2", "akrilik 10 mm, strip LED"), "C3": ((150, 205, 235), "Cincin 3", "akrilik 10 mm"),
        "B": ((215, 211, 240), "Lembar belakang", "akrilik buram 5 mm, 4 lubang")}

CAPS = [
    (5.0, 14.3, "1 · Putar 360°", "Kita putar hexagon Algora satu kali penuh,", "supaya terlihat dari semua sisi."),
    (15.6, 21.6, "2 · Tampak depan", "Lebar 300 mm diukur dari sisi datar ke sisi datar.", "Dari sudut ke sudut 346,4 mm, setiap sisi 173,2 mm."),
    (22.0, 30.6, "3 · Dibongkar (exploded)", "Hexagon terdiri dari 5 lapis akrilik.", "Air alga ada di tengah, dikelilingi 3 cincin."),
    (30.6, 40.0, "4 · Putar sekali lagi", "Urutannya dari depan: A, lalu cincin C1, C2, C3,", "dan B paling belakang."),
    (40.0, 43.6, "5 · Dirakit kembali", "Semua lapisan ditempel jadi satu", "dengan silikon akuarium."),
    (43.8, 49.4, "6 · Close-up: sudut R4", "Sudut DALAM cincin dibuat melengkung R4,", "karena mata pahat CNC berbentuk bulat."),
    (50.4, 54.6, "7 · Close-up: lubang belakang", "P1, P2, P3 ada di atas garis air:", "untuk isi air, selang udara, dan kabel sensor suhu."),
    (54.6, 57.6, "7 · Close-up: lubang belakang", "P4 ada di bawah,", "untuk menguras air dan panen alga."),
    (58.4, 64.3, "8 · Close-up: susunan lapisan", "Dari samping terlihat 5 lapisan:", "5 + 10 + 10 + 10 + 5 = 40 mm."),
    (64.5, 69.4, "9 · Close out", "Lampu LED di sisi cincin menyala,", "alga mendapat cahaya untuk berfotosintesis."),
]

def fade(t, a, b, d=0.45):
    if t < a or t > b: return 0.0
    return max(0.0, min(1.0, (t - a) / d, (b - t) / d))

def P(f, name):
    v = ANCH[str(f)].get(name)
    if not v or v[2] <= 0: return None
    return (v[0] * W, (1 - v[1]) * H)

def A_(c, a): return tuple(c[:3]) + (int(255 * a),)

def pill(d, xy, text, fnt, fg, a, bg=WHITE_, pad=(16, 8), anchor="mm"):
    x, y = xy; tw = d.textlength(text, font=fnt); th = fnt.size
    w, h = tw + 2 * pad[0], th + 2 * pad[1]
    x0 = x - w / 2 if anchor == "mm" else (x if anchor == "lm" else x - w)
    d.rounded_rectangle((x0, y - h / 2, x0 + w, y + h / 2), h / 2, fill=A_(bg, a), outline=A_(fg, a), width=3)
    d.text((x0 + w / 2, y + 1), text, font=fnt, fill=A_(fg, a), anchor="mm")
    return (x0, y - h / 2, x0 + w, y + h / 2)

def arrow(d, tip, ang, col, a, L=18, Wd=7):
    ca, sa = math.cos(ang), math.sin(ang)
    d.polygon([tip, (tip[0] - L * ca + Wd * sa, tip[1] - L * sa - Wd * ca), (tip[0] - L * ca - Wd * sa, tip[1] - L * sa + Wd * ca)], fill=A_(col, a))

def dimline(d, Pa, Pb, off, label, col, a, size=30, ext=True):
    dx, dy = Pb[0] - Pa[0], Pb[1] - Pa[1]; L = math.hypot(dx, dy) or 1; ux, uy = dx / L, dy / L; nx, ny = -uy, ux
    a2 = (Pa[0] + nx * off, Pa[1] + ny * off); b2 = (Pb[0] + nx * off, Pb[1] + ny * off)
    if ext and abs(off) > 2:
        sg = 1 if off > 0 else -1
        for p0, p1 in ((Pa, a2), (Pb, b2)):
            d.line((p0[0] + nx * sg * 6, p0[1] + ny * sg * 6, p1[0] + nx * sg * 12, p1[1] + ny * sg * 12), fill=A_(col, a * 0.7), width=2)
    d.line((a2, b2), fill=A_(col, a), width=4)
    ang = math.atan2(uy, ux); arrow(d, b2, ang, col, a); arrow(d, a2, ang + math.pi, col, a)
    pill(d, ((a2[0] + b2[0]) / 2, (a2[1] + b2[1]) / 2), label, font(size, 800), col, a)

def leader(d, Pa, Pb, col, a, dot=True):
    d.line((Pa, Pb), fill=A_(col, a), width=3)
    if dot: d.ellipse((Pa[0] - 7, Pa[1] - 7, Pa[0] + 7, Pa[1] + 7), fill=A_(col, a), outline=A_(WHITE_, a), width=2)

def caption(d, t):
    for t0, t1, chip, l1, l2 in CAPS:
        a = fade(t, t0, t1)
        if a <= 0: continue
        f1, f2, fc = font(40, 800), font(32, 600), font(28, 800)
        w = max(d.textlength(l1, font=f1), d.textlength(l2, font=f2)) + 90
        x0, y0 = (W - w) / 2, H - 190
        d.rounded_rectangle((x0, y0, x0 + w, y0 + 150), 28, fill=A_(WHITE_, a * 0.94), outline=A_((210, 220, 236), a), width=2)
        d.text((W / 2, y0 + 52), l1, font=f1, fill=A_(INK, a), anchor="mm")
        d.text((W / 2, y0 + 104), l2, font=f2, fill=A_(INK2, a), anchor="mm")
        tw = d.textlength(chip, font=fc) + 70
        d.rounded_rectangle((48, 44, 48 + tw, 104), 30, fill=A_(INK, a))
        d.ellipse((70, 66, 86, 82), fill=A_(BLUE, a)); d.text((98, 75), chip, font=fc, fill=A_(WHITE_, a), anchor="lm")

def intro(d, t):
    a = fade(t, 0.0, 4.8, 0.6)
    if a <= 0: return
    d.rounded_rectangle((330, 28, 1590, 178), 36, fill=A_(WHITE_, a * 0.92))
    d.text((W / 2, 86), "Hexagon Algora  ·  Gambar teknik 3D", font=font(64, 800), fill=A_(INK, a), anchor="mm")
    d.text((W / 2, 146), "Versi prototipe yang dipotong mesin CNC  ·  semua ukuran dalam mm", font=font(30, 600), fill=A_(BLUE, a), anchor="mm")

def outro(d, t):
    a = fade(t, 69.6, 75.5, 0.7)
    if a <= 0: return
    d.rounded_rectangle((0, 0, W, H), 0, fill=A_((233, 239, 247), a * 0.55))
    d.text((W / 2, 150), "Angka penting hexagon Algora", font=font(60, 800), fill=A_(INK, a), anchor="mm")
    tiles = [("300 mm", "lebar sisi datar"), ("40 mm", "tebal total"), ("1,7 L", "air alga"), ("5 potong", "akrilik CNC")]
    for i, (big, small) in enumerate(tiles):
        x = 180 + i * 400; y = 250
        d.rounded_rectangle((x, y, x + 360, y + 200), 30, fill=A_(WHITE_, a), outline=A_((210, 220, 236), a), width=2)
        d.text((x + 180, y + 85), big, font=font(64, 800), fill=A_(BLUE, a), anchor="mm")
        d.text((x + 180, y + 150), small, font=font(32, 600), fill=A_(INK2, a), anchor="mm")
    d.text((W / 2, H - 110), "Ukuran lengkap: lihat PDF gambar teknik Algora", font=font(36, 700), fill=A_(INK, a), anchor="mm")

def overlay(f):
    t = f / FPS
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # tampak depan: ukuran utama
    a = fade(t, 15.9, 21.4)
    if a > 0:
        l, r_, tl, tr, bl = (P(f, k) for k in ("d_l", "d_r", "d_tl", "d_tr", "d_bl"))
        if all((l, r_, tl, tr, bl)):
            dimline(d, l, r_, 0, "346,4  (sudut ke sudut)", BLUE, a, 30, ext=False)
            dimline(d, bl, tl, -(bl[0] - l[0]) - 70, "300", BLUE, a, 34)
            dimline(d, tl, tr, -50, "173,2", BLUE, a)
    # bongkar: label bagian
    a = fade(t, 25.6, 30.9)
    if a > 0:
        ys = [250, 360, 470, 580, 690]
        for (k, y) in zip(("A", "C1", "C2", "C3", "B"), ys):
            p = P(f, "lab_" + k)
            col, name, sub = PART[k]
            x0 = 1440
            if p: leader(d, p, (x0, y), INK, a)
            d.rounded_rectangle((x0, y - 44, x0 + 430, y + 44), 22, fill=A_(WHITE_, a), outline=A_((210, 220, 236), a), width=2)
            d.rounded_rectangle((x0 + 16, y - 28, x0 + 72, y + 28), 14, fill=A_(col, a), outline=A_(INK, a), width=2)
            d.text((x0 + 44, y + 1), k, font=font(28, 800), fill=A_(INK, a), anchor="mm")
            d.text((x0 + 88, y - 12), name, font=font(30, 800), fill=A_(INK, a), anchor="lm")
            d.text((x0 + 88, y + 20), sub, font=font(24, 500), fill=A_(INK2, a), anchor="lm")
    a = fade(t, 25.6, 39.6)
    if a > 0:
        p = P(f, "water")
        if p:
            q = (p[0] - 170, p[1] + 190); leader(d, p, q, GREEN, a); pill(d, (q[0], q[1] + 4), "air alga ±1,7 L", font(28, 800), GREEN, a, anchor="rm")
    a = fade(t, 30.9, 39.6)
    if a > 0:
        for k in ("A", "C1", "C2", "C3", "B"):
            p = P(f, "tag_" + k)
            if p:
                col = PART[k][0]
                d.ellipse((p[0] - 26, p[1] - 26, p[0] + 26, p[1] + 26), fill=A_(col, a), outline=A_(INK, a), width=3)
                d.text((p[0], p[1] + 1), k, font=font(24, 800), fill=A_(INK, a), anchor="mm")
    # close-up R4
    a = fade(t, 44.2, 49.2)
    if a > 0:
        p = P(f, "r4")
        if p:
            d.ellipse((p[0] - 85, p[1] - 75, p[0] + 55, p[1] + 65), outline=A_(RED, a), width=5)
            q = (p[0] - 420, p[1] - 250); leader(d, (p[0] - 50, p[1] - 35), q, RED, a, dot=False)
            pill(d, q, "R4 = sudut dalam melengkung", font(32, 800), RED, a, anchor="rm")
        wi, wo = P(f, "w_in"), P(f, "w_out")
        if wi and wo: dimline(d, wi, wo, 0, "dinding 11", BLUE, a, 30, ext=False)
        d.text((W - 80, 160), "sudut luar tetap tajam", font=font(30, 700), fill=A_(INK2, a), anchor="rm")
    # lubang belakang
    for t0, t1, codes in ((51.0, 54.4, ("P1", "P2", "P3")), (55.7, 57.4, ("P4",))):
        a = fade(t, t0, t1)
        if a <= 0: continue
        for h in DIMS["HOLES"]:
            if h["code"] not in codes: continue
            p = P(f, "hole_" + h["code"])
            if not p: continue
            # dilihat dari belakang, kiri-kanan layar terbalik terhadap x gambar
            dx = {"P1": 0, "P2": 260, "P3": -260, "P4": 300}[h["code"]]; dy = -230 if h["code"] != "P4" else -120
            q = (p[0] + dx, p[1] + dy)
            leader(d, p, q, RED, a)
            pill(d, q, f"{h['code']}  Ø{str(h['d']).replace('.', ',').replace(',0', '')} mm", font(32, 800), RED, a)
    # susunan lapisan
    a = fade(t, 59.2, 64.2)
    if a > 0:
        pts = [P(f, f"L{k}") for k in range(6)]
        if all(pts):
            for k, lab in enumerate(("5", "10", "10", "10", "5")):
                dimline(d, pts[k], pts[k + 1], -(90 if k % 2 == 0 else 170), lab, BLUE, a, 30)
            dimline(d, pts[0], pts[5], -260, "tebal total 40", BLUE, a, 32)
    a = fade(t, 65.0, 69.4)
    if a > 0:
        p = P(f, "led")
        if p:
            q = (p[0] + 260, p[1] - 140); leader(d, p, q, AMBER, a); pill(d, q, "strip LED menyala", font(30, 800), AMBER, a, anchor="lm")
    intro(d, t); caption(d, t); outro(d, t)
    return im

def frame(f):
    out = os.path.join(B, f"c_{f:04d}.jpg")
    if os.path.exists(out) and not TEST: return
    src = os.path.join(FR, f"f_{f:04d}.png")
    bg = Image.open(src).convert("RGBA").resize((W, H), Image.LANCZOS)
    Image.alpha_composite(bg, overlay(f)).convert("RGB").save(out, quality=94)

def init():
    global ANCH
    ANCH = json.load(open(os.path.join(FR, "anchors.json")))

TEST = False
if __name__ == "__main__":
    init()
    if len(sys.argv) > 2 and sys.argv[1] == "--test":
        TEST = True
        for t in sys.argv[2].split(","):
            frame(int(float(t) * FPS))
        print("TEST OK"); sys.exit()
    with Pool(8, initializer=init) as pool:
        pool.map(frame, range(NF), chunksize=20)
    from compose import music
    FF = shutil.which("ffmpeg") or ffmpeg()
    wav = os.path.join(B, "music.wav"); music(DUR, wav)
    out = os.path.join(ROOT, "output", "ALGORA_gambar_teknik_3D.mp4")
    subprocess.run([FF, "-y", "-v", "error", "-framerate", str(FPS), "-i", os.path.join(B, "c_%04d.jpg"), "-i", wav,
                    "-filter_complex", "[1:a]loudnorm=I=-18:TP=-1.5[a]", "-map", "0:v", "-map", "[a]",
                    "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-t", f"{DUR:.3f}", out], check=True)
    print("WROTE", out)
