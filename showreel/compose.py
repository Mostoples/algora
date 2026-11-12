"""ALGORA showreel composer (PIL + FFmpeg).  python showreel/compose.py [id|en]
Inputs : output/frames/<shot>/f_####.png (Blender), showreel/build/rec_<lang>/rec.mp4 + marks.json (app)
Output : output/ALGORA_showreel_<lang>.mp4  (1920x1080, 30 fps)"""
import os, sys, json, math, subprocess, shutil, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brand import *

LANG = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("APP_LANG", "id")
W, H, FPS = 1920, 1080, 30
B = os.path.join(ROOT, "showreel", "build", "reel_" + LANG)
FR = os.path.join(ROOT, "output", "frames")
REC = os.path.join(ROOT, "showreel", "build", "rec_" + LANG)
FF = shutil.which("ffmpeg") or ffmpeg()
os.makedirs(B, exist_ok=True)

TEXT = {
 "id": dict(
  tagline="Fotobioreaktor mikroalga modular · lampu hidup · AIoT rawat-mandiri",
  hero=("01 · PRODUK", "Satu hexagon,", "ekosistem hidup.", "Akrilik 300 mm berisi mikroalga — menyerap CO₂, menghasilkan O₂, menyala sebagai lampu.", ["Snap 6 sisi", "Inti AIoT", "Akrilik daur ulang"]),
  labels=dict(top="Akrilik bening 5 mm", core="Inti AIoT · sensor + LED", culture="Kultur mikroalga", bottom="Akrilik frosted / difuser", connector="Konektor magnet pogo + fluida", led="LED tepi"),
  wall=("02 · DINDING", "Dinding yang", "bernapas.", "Tempel, kunci magnet, langsung sinkron — tambah modul kapan saja.", ["Snap & play", "Seni + udara bersih"]),
  floor=("03 · LANTAI / PAVING", "Jalan setapak", "yang bercahaya.", "Akrilik tebal anti-slip — taman jadi penyerap karbon & lampu malam.", ["Anti-slip", "Glow malam"]),
  lamp=("04 · LAMPU", "Cahaya ruangan,", "energi alga.", "LED tepi menerangi meja sekaligus memberi cahaya fotosintesis.", ["2700–6500 K", "Ritme sirkadian"]),
  roof=("05 · GENTING", "Atap peneduh", "yang tumbuh.", "Sinar matahari tersaring hijau — teduh, sejuk, dan menghasilkan biomassa.", ["Peneduh", "Panen biomassa"]),
  app=[("06 · APP · BERANDA", "Semua modul,", "satu dashboard.", "CO₂ terserap, O₂, skor bio & 4 mode pemasangan secara langsung.", ["Live", "4 mode"], "home"),
       ("07 · MODUL", "Sambung,", "langsung terdeteksi.", "Peta honeycomb real-time — setiap modul punya sensor sendiri.", ["Auto-detect", "6 sensor"], "hive"),
       ("08 · CAHAYA", "Suasana", "sesuai waktu.", "Suhu warna, kecerahan & fotoperiode alga dalam satu dial.", ["Scene", "Fotoperiode"], "light"),
       ("09 · RAWAT MANDIRI", "Merawat", "dirinya sendiri.", "Nutrien, aerasi, self-cleaning & panen otomatis lewat base station.", ["Auto-dosing", "UV-C clean"], "care"),
       ("10 · AI INSIGHT", "Tahu kapan", "harus panen.", "Prediksi pertumbuhan, deteksi anomali & rekomendasi per modul.", ["Prediksi", "Anomali"], "ai")],
  outro="Modular · Hidup · Rawat-mandiri",
 ),
 "en": dict(
  tagline="Modular microalgae photobioreactor · living light · self-maintaining AIoT",
  hero=("01 · PRODUCT", "One hexagon,", "a living ecosystem.", "300 mm acrylic cell of microalgae — captures CO₂, releases O₂, glows as a lamp.", ["6-side snap", "AIoT core", "Recycled acrylic"]),
  labels=dict(top="5 mm clear acrylic", core="AIoT core · sensors + LED", culture="Microalgae culture", bottom="Frosted acrylic diffuser", connector="Magnetic pogo + fluid port", led="Edge LED"),
  wall=("02 · WALL", "A wall that", "breathes.", "Snap, magnet-lock, instantly synced — add modules any time.", ["Snap & play", "Art + clean air"]),
  floor=("03 · FLOOR / PAVING", "A path that", "glows.", "Thick anti-slip acrylic — the garden becomes a carbon sink & night light.", ["Anti-slip", "Night glow"]),
  lamp=("04 · LAMP", "Room light,", "algae energy.", "Edge LEDs light the table and feed photosynthesis at once.", ["2700–6500 K", "Circadian"]),
  roof=("05 · ROOF TILE", "A canopy", "that grows.", "Sunlight filtered green — shade, cooling and harvestable biomass.", ["Shade", "Biomass harvest"]),
  app=[("06 · APP · HOME", "Every module,", "one dashboard.", "CO₂ captured, O₂, bio score & 4 install modes — live.", ["Live", "4 modes"], "home"),
       ("07 · MODULES", "Snap in,", "detected instantly.", "Real-time honeycomb map — every module has its own sensors.", ["Auto-detect", "6 sensors"], "hive"),
       ("08 · LIGHT", "Light that", "fits the hour.", "Colour temperature, brightness & algae photoperiod in one dial.", ["Scenes", "Photoperiod"], "light"),
       ("09 · SELF-CARE", "Looks after", "itself.", "Nutrients, aeration, self-cleaning & harvest run automatically.", ["Auto-dosing", "UV-C clean"], "care"),
       ("10 · AI INSIGHT", "Knows when", "to harvest.", "Growth forecast, anomaly detection & per-module advice.", ["Forecast", "Anomalies"], "ai")],
  outro="Modular · Alive · Self-maintaining",
 ),
}[LANG]

def run(args):
    subprocess.run([FF, "-y", "-loglevel", "error"] + args, check=True)

def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3

# --------------------------------------------------------------- text card --
def caption_card(chip_t, l1, l2, desc, pills, width=820, green=False):
    """Returns RGBA card image (chip + 2-colour title + desc + pills)."""
    f1, fd, fp = font(64), font(28, 500), font(24, 700)
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    lines = []
    words, cur = desc.split(), ""
    for w_ in words:
        if tmp.textlength(cur + " " + w_, font=fd) > width - 80:
            lines.append(cur); cur = w_
        else:
            cur = (cur + " " + w_).strip()
    lines.append(cur)
    h = 70 + 80 + 78 + 30 + len(lines) * 40 + 30 + 56 + 40
    cd, pad = card((width, h), 32, 238, aura=True)
    d = ImageDraw.Draw(cd)
    x, y = pad + 40, pad + 36
    ch, cp = chip(chip_t)
    cd.paste(ch, (x - cp, y - cp), ch)
    y += 70
    d.text((x, y), l1, font=f1, fill=INK)
    y += 76
    grad_text(cd, (x, y), l2, f1, *((ALGAE, ALGAE2) if green else (BLUE, DEEP)))
    y += 96
    for ln in lines:
        d.text((x, y), ln, font=fd, fill=INK2); y += 40
    y += 24
    for p_ in pills:
        pw = int(d.textlength(p_, font=fp)) + 56
        pc, ppad = card((pw, 48), 24, 250, shadow=True)
        dd = ImageDraw.Draw(pc)
        dd.ellipse((ppad + 18, ppad + 19, ppad + 28, ppad + 29), fill=ALGAE)
        dd.text((ppad + 36, ppad + 24), p_, font=fp, fill=INK2, anchor="lm")
        cd.paste(pc, (x - ppad, y - ppad), pc)
        x += pw + 16
    return cd

def overlay_png(img, path, xy):
    full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    full.paste(img, xy, img)
    full.save(path)
    return path

def logo_mark(size=120):
    p = os.path.join(ROOT, "app", "assets", "img", "icon512.png")
    im = Image.open(p).convert("RGBA")
    im.thumbnail((size, size))
    return im

# ------------------------------------------------------------ PIL segments --
def seg_intro(dur=3.6, name="s00_intro.mp4", outro=False):
    d_ = os.path.join(B, "intro" if not outro else "outro"); os.makedirs(d_, exist_ok=True)
    bg = aura_bg((W, H))
    hero = Image.open(os.path.join(ROOT, "app", "assets", "img", "hero_cluster.png")).convert("RGBA")
    hero.thumbnail((620, 620))
    n = int(dur * FPS)
    for i in range(n):
        t = i / FPS
        im = bg.copy().convert("RGBA")
        k = ease(t / 1.2)
        hs = hero.resize((int(hero.width * (0.85 + 0.15 * k)), int(hero.height * (0.85 + 0.15 * k))))
        a = hs.split()[3].point(lambda v: int(v * k))
        hs.putalpha(a)
        cx = 560 if not outro else W // 2
        im.paste(hs, (cx - hs.width // 2, H // 2 - hs.height // 2 - (0 if not outro else 90) + int(18 * math.sin(t * 1.6))), hs)
        d = ImageDraw.Draw(im)
        kt = ease((t - 0.5) / 0.9)
        f = font(150)
        if not outro:
            x0, y0 = 980, 380 + int(30 * (1 - kt))
        else:
            x0 = W // 2 - int(d.textlength("Algora", font=f)) // 2; y0 = 640 + int(30 * (1 - kt))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.text((x0, y0), "Algo", font=f, fill=INK)
        grad_text(layer, (x0 + ld.textlength("Algo", font=f), y0), "ra", f, ALGAE, ALGAE2)
        sub = TEXT["tagline"] if not outro else TEXT["outro"]
        fs = font(34, 600)
        sx = x0 + 6 if not outro else W // 2 - int(ld.textlength(sub, font=fs)) // 2
        maxw = (W - sx - 90) if not outro else W - 200
        words, lines_, cur = sub.split(" "), [], ""
        for w_ in words:
            if ld.textlength((cur + " " + w_).strip(), font=fs) > maxw:
                lines_.append(cur); cur = w_
            else:
                cur = (cur + " " + w_).strip()
        lines_.append(cur)
        for j, ln in enumerate(lines_):
            lx = sx if not outro else W // 2 - int(ld.textlength(ln, font=fs)) // 2
            ld.text((lx, y0 + 190 + j * 46), ln, font=fs, fill=INK2)
        if outro:
            ld.text((W // 2, H - 70), "3D assets: Sketchfab CC-BY — 3dimentionalben, Giora, AllQuad, OliverMatheGames, scailman, Elasta Kristya  ·  Characters: MakeHuman CC0 + Blender Rigify", font=font(20, 600), fill=MUTED, anchor="mt")
        layer.putalpha(layer.split()[3].point(lambda v: int(v * kt)))
        im = Image.alpha_composite(im, layer)
        fade = min(1, t / 0.4, (dur - t) / 0.4) if outro else min(1, (dur - t) / 0.5 + 0.0) if False else 1
        im.convert("RGB").save(os.path.join(d_, f"f_{i:04d}.png"))
    out = os.path.join(B, name)
    run(["-framerate", str(FPS), "-i", os.path.join(d_, "f_%04d.png"), "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", out])
    return out

# ----------------------------------------------------------- 3D segments ---
def frames_of(shot):
    d_ = os.path.join(FR, shot)
    return sorted(f for f in os.listdir(d_) if f.startswith("f_") and f.endswith(".png")) if os.path.isdir(d_) else []

def seg_3d(shot, cap, name, green=False, labels=None, cap_at=0.6):
    fs = frames_of(shot)
    if not fs:
        print("no frames for", shot); return None
    n = len(fs); dur = n / FPS
    card_img = caption_card(*cap, green=green)
    card_img = card_img.resize((int(card_img.width * 0.78), int(card_img.height * 0.78)))
    cpath = overlay_png(card_img, os.path.join(B, f"{shot}_card.png"), (40, H - card_img.height - 10))
    logo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lm = logo_mark(64); logo.paste(lm, (W - 260, 34), lm)
    ImageDraw.Draw(logo).text((W - 186, 66), "Algora", font=font(38), fill=(255, 255, 255) if shot in ("floor",) else INK, anchor="lm")
    lpath = os.path.join(B, f"{shot}_logo.png"); logo.save(lpath)
    src = os.path.join(FR, shot, "f_%04d.png")
    A, Bt = cap_at, dur - 0.5
    inputs = ["-framerate", str(FPS), "-i", src, "-loop", "1", "-i", cpath, "-loop", "1", "-i", lpath]
    fc = (f"[0]scale={W}:{H}:flags=lanczos,format=rgba[v];"
          f"[1]format=rgba,fade=in:st={A}:d=0.5:alpha=1,fade=out:st={Bt}:d=0.4:alpha=1[ci];"
          f"[v][ci]overlay=x='-60*(1-min(max((t-{A})/0.6,0),1))':y=0:enable='between(t,{A},{Bt + 0.4})'[v2];"
          f"[2]format=rgba[lg];[v2][lg]overlay=0:0[v3]")
    last = "v3"
    if labels:
        ldir = os.path.join(B, f"{shot}_labels"); os.makedirs(ldir, exist_ok=True)
        for i in range(n):
            labels(i).save(os.path.join(ldir, f"l_{i:04d}.png"))
        inputs += ["-framerate", str(FPS), "-i", os.path.join(ldir, "l_%04d.png")]
        fc += f";[3]format=rgba[lb];[v3][lb]overlay=0:0[v4]"
        last = "v4"
    out = os.path.join(B, name)
    run(inputs + ["-filter_complex", fc, "-map", f"[{last}]", "-t", f"{dur:.3f}", "-r", str(FPS), "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", out])
    return out

def hero_labels():
    ap = os.path.join(FR, "hero", "anchors.json")
    A = json.load(open(ap)) if os.path.exists(ap) else {}
    order = ["core", "top", "culture", "connector", "bottom"]
    side = {"core": 1, "top": -1, "culture": -1, "connector": 1, "bottom": 1}
    dy = {"core": 0, "top": -30, "culture": 30, "connector": 40, "bottom": 40}
    f = font(26, 700)
    def make(i):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        t = i / FPS
        k = ease((t - 2.9) / 0.6) * (1 - ease((t - 4.9) / 0.4))
        a = A.get(str(i))
        if not a or k <= 0.01:
            return im
        d = ImageDraw.Draw(im)
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
        for j, key in enumerate(order):
            if key not in a:
                continue
            kj = ease((t - 2.9 - j * 0.12) / 0.5) * (1 - ease((t - 4.9) / 0.4))
            if kj <= 0.01:
                continue
            px, py = a[key][0] * W, (1 - a[key][1]) * H
            sx = side[key]
            label = TEXT["labels"][key]
            tw = d.textlength(label, font=f)
            ex = px + sx * 220
            ex = min(ex, W - 40 - tw - 40) if sx > 0 else max(ex, 40 + tw + 40)
            ly = py + dy[key]
            bx = ex if sx > 0 else ex - tw - 40
            al = int(255 * kj)
            pts = [(px, py), (px + (ex - px) * 0.35, ly), (ex, ly)]
            gd.line(pts, fill=(47, 123, 255, int(140 * kj)), width=8)
            d.line(pts, fill=(47, 123, 255, al), width=3)
            py_box = ly
            d.ellipse((px - 9, py - 9, px + 9, py + 9), fill=(255, 255, 255, al), outline=(47, 123, 255, al), width=4)
            d.rounded_rectangle((bx, py_box - 26, bx + tw + 40, py_box + 26), 26, fill=(250, 252, 255, int(235 * kj)), outline=(255, 255, 255, al), width=2)
            d.text((bx + 20, py_box), label, font=f, fill=INK[:3] + (al,), anchor="lm")
        glow = glow.filter(ImageFilter.GaussianBlur(6))
        return Image.alpha_composite(glow, im)
    return make

# ----------------------------------------------------------- app segments --
def phone_assets(scale=0.98):
    """Phone bezel + screen mask (screen 780x1688 scaled)."""
    sw, sh = int(390 * 2 * 0.5 * scale * 1.1), int(844 * 2 * 0.5 * scale * 1.1)
    bez = 22
    pw, ph = sw + bez * 2, sh + bez * 2
    im = Image.new("RGBA", (pw + 160, ph + 160), (0, 0, 0, 0))
    sh_ = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh_).rounded_rectangle((80, 96, 80 + pw, 96 + ph), 70, fill=(40, 90, 200, 110))
    im = Image.alpha_composite(im, sh_.filter(ImageFilter.GaussianBlur(34)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((80, 80, 80 + pw, 80 + ph), 70, fill=(28, 34, 48, 255))
    d.rounded_rectangle((84, 84, 76 + pw, 76 + ph), 66, outline=(90, 100, 120, 255), width=2)
    # cut the screen out
    hole = Image.new("L", im.size, 0)
    ImageDraw.Draw(hole).rounded_rectangle((80 + bez, 80 + bez, 80 + bez + sw, 80 + bez + sh), 50, fill=255)
    a = np.array(im.split()[3]); a[np.array(hole) > 0] = 0
    im.putalpha(Image.fromarray(a))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((80 + pw // 2 - 60, 80 + bez + 12, 80 + pw // 2 + 60, 80 + bez + 42), 15, fill=(10, 12, 18, 255))
    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, sw - 1, sh - 1), 50, fill=255)
    return im, mask, (sw, sh), 80 + bez

def seg_app(i, item, marks, name):
    chip_t, l1, l2, desc, pills, key = item
    a, b = marks[key]
    dur = min(max(4.6, b - a), 6.2)
    bg = aura_bg((W, H), ((0.78, 0.3, 700, (140, 198, 255)), (0.2, 0.85, 600, (125, 230, 170))))
    bez, mask, (sw, sh), off = phone_assets()
    px = 1240 - bez.width // 2 + 120
    py = (H - bez.height) // 2 + 10
    bg.save(os.path.join(B, f"app{i}_bg.png"))
    full_bez = Image.new("RGBA", (W, H), (0, 0, 0, 0)); full_bez.paste(bez, (px, py), bez)
    full_bez.save(os.path.join(B, f"app{i}_bez.png"))
    mask.save(os.path.join(B, f"app{i}_mask.png"))
    cd = caption_card(chip_t, l1, l2, desc, pills, width=760, green=key in ("care",))
    cpath = overlay_png(cd, os.path.join(B, f"app{i}_card.png"), (70, (H - cd.height) // 2))
    out = os.path.join(B, name)
    fc = (f"[1]trim=start={a + 0.2}:duration={dur},setpts=PTS-STARTPTS,scale={sw}:{sh}:flags=lanczos,format=rgba[sc];"
          f"[3]format=gray,scale={sw}:{sh}[mk];[sc][mk]alphamerge[scm];"
          f"[0]format=rgba[bg];[bg][scm]overlay={px + off}:{py + off}[v1];"
          f"[2]format=rgba[bz];[v1][bz]overlay=0:0[v2];"
          f"[4]format=rgba,fade=in:st=0.3:d=0.5:alpha=1[ci];[v2][ci]overlay=x='-80*(1-min(max((t-0.3)/0.6,0),1))':y=0[v3]")
    run(["-loop", "1", "-i", os.path.join(B, f"app{i}_bg.png"), "-i", os.path.join(REC, "rec.mp4"),
         "-loop", "1", "-i", os.path.join(B, f"app{i}_bez.png"), "-loop", "1", "-i", os.path.join(B, f"app{i}_mask.png"),
         "-loop", "1", "-i", cpath, "-filter_complex", fc, "-map", "[v3]", "-t", f"{dur:.3f}", "-r", str(FPS),
         "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", out])
    return out

# ------------------------------------------------------------------ music --
def music(dur, path):
    sr = 48000
    t = np.arange(int(dur * sr)) / sr
    chords = [[57, 60, 64, 69], [53, 57, 60, 65], [55, 59, 62, 67], [52, 55, 59, 64]]  # Am F G Em
    bar = 4.0
    y = np.zeros_like(t)
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    for k in range(int(dur / bar) + 1):
        c = chords[k % 4]
        s0 = int(k * bar * sr); s1 = min(len(t), int((k + 1) * bar * sr + sr))
        tt = t[s0:s1] - k * bar
        env = np.minimum(1, tt / 0.8) * np.exp(-np.maximum(0, tt - bar) * 3)
        for m in c:
            y[s0:s1] += 0.06 * env * (np.sin(2 * np.pi * hz(m) * tt) + 0.3 * np.sin(2 * np.pi * hz(m) * 2.003 * tt))
        for j in range(8):  # pluck arpeggio
            st = j * bar / 8
            m = c[[0, 2, 1, 3, 2, 3, 1, 2][j]] + 12
            p0 = s0 + int(st * sr); p1 = min(len(t), p0 + int(0.9 * sr))
            if p0 >= len(t):
                break
            tp = t[p0:p1] - t[p0]
            y[p0:p1] += 0.05 * np.exp(-tp * 5) * np.sin(2 * np.pi * hz(m) * tp)
        p0 = s0; p1 = min(len(t), s0 + int(0.5 * sr))  # soft kick
        tp = t[p0:p1] - t[p0]
        y[p0:p1] += 0.18 * np.exp(-tp * 9) * np.sin(2 * np.pi * (50 + 60 * np.exp(-tp * 30)) * tp)
    fade = np.minimum(1, np.minimum(t / 1.5, (dur - t) / 2.5))
    y = y * fade
    st = np.stack([y, np.roll(y, int(0.012 * sr))], 1)
    st = (st / (np.abs(st).max() + 1e-9) * 0.8 * 32767).astype(np.int16)
    with wave.open(path, "wb") as w_:
        w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(sr); w_.writeframes(st.tobytes())

# ------------------------------------------------------------------- main --
if __name__ == "__main__":
    segs = [seg_intro()]
    segs.append(seg_3d("hero", TEXT["hero"], "s01_hero.mp4", green=True, labels=hero_labels(), cap_at=0.5))
    for k, shot in enumerate(["wall", "floor", "lamp", "roof"]):
        segs.append(seg_3d(shot, TEXT[shot], f"s{k + 2:02d}_{shot}.mp4", green=shot in ("roof", "floor")))
    marks = json.load(open(os.path.join(REC, "marks.json")))
    for i, item in enumerate(TEXT["app"]):
        segs.append(seg_app(i, item, marks, f"s{i + 6:02d}_app.mp4"))
    segs.append(seg_intro(4.2, "s99_outro.mp4", outro=True))
    segs = [s for s in segs if s]
    # xfade chain
    durs = [float(subprocess.run([FF.replace("ffmpeg.exe", "ffprobe.exe") if FF.endswith(".exe") else "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", s],
                                 capture_output=True, text=True).stdout.strip()) for s in segs]
    X = 0.6
    inputs, fc, prev, acc = [], "", "0:v", durs[0]
    for s in segs:
        inputs += ["-i", s]
    trans = ["fade", "smoothleft", "fade", "fade", "fade", "circleopen", "smoothleft", "smoothleft", "smoothleft", "smoothleft", "fade"]
    for i in range(1, len(segs)):
        off = acc - X
        tr = trans[(i - 1) % len(trans)]
        fc += f"[{prev}][{i}:v]xfade=transition={tr}:duration={X}:offset={off:.3f}[x{i}];"
        prev = f"x{i}"; acc = off + durs[i]
    total = acc
    wav = os.path.join(B, "music.wav"); music(total, wav)
    out = os.path.join(ROOT, "output", f"ALGORA_showreel_{LANG}.mp4")
    run(inputs + ["-i", wav, "-filter_complex", fc.rstrip(";") + f";[{len(segs)}:a]loudnorm=I=-17:TP=-1.5[a]",
                  "-map", f"[{prev}]", "-map", "[a]", "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
                  "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{total:.3f}", out])
    print("WROTE", out, f"{total:.1f}s")
