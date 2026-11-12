"""English diagrams for the full paper: system architecture + control flowchart (PIL)."""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output", "paper")
FONT = os.path.join(ROOT, "showreel", "fonts", "PlusJakartaSans.ttf")
INK, MUTED, EDGE, ACC, TUBE, TINT = (22, 35, 63), (91, 107, 134), (120, 130, 145), (31, 111, 235), (229, 110, 60), (240, 243, 248)
S = 2  # supersample

def f(sz, w=700):
    ft = ImageFont.truetype(FONT, sz * S)
    try: ft.set_variation_by_axes([w])
    except Exception: pass
    return ft

def box(d, x, y, w, h, t1, t2=None, main=False, round_=16):
    d.rounded_rectangle((x * S, y * S, (x + w) * S, (y + h) * S), round_ * S, fill=(225, 236, 252) if main else "white",
                        outline=ACC if main else EDGE, width=(3 if main else 2) * S)
    cy = y + h / 2
    if t2:
        d.text(((x + w / 2) * S, (cy - 9) * S), t1, font=f(17, 750), fill=INK, anchor="mm")
        d.text(((x + w / 2) * S, (cy + 12) * S), t2, font=f(14, 500), fill=MUTED, anchor="mm")
    else:
        d.text(((x + w / 2) * S, cy * S), t1, font=f(17, 650), fill=INK, anchor="mm")

def arrow(d, pts, col=EDGE, w=2):
    pts = [(x * S, y * S) for x, y in pts]
    d.line(pts, fill=col, width=w * S, joint="curve")
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    import math
    a = math.atan2(y1 - y0, x1 - x0); L, W = 12 * S, 6 * S
    d.polygon([(x1, y1), (x1 - L * math.cos(a) + W * math.sin(a), y1 - L * math.sin(a) - W * math.cos(a)),
               (x1 - L * math.cos(a) - W * math.sin(a), y1 - L * math.sin(a) + W * math.cos(a))], fill=col)

def label(d, x, y, t, anchor="mm"):
    d.text((x * S, y * S), t, font=f(13, 500), fill=MUTED, anchor=anchor)

def architecture():
    W, H = 1180, 560
    im = Image.new("RGB", (W * S, H * S), "white"); d = ImageDraw.Draw(im)
    for x, t in ((300, "Electronics box"), (900, "Hexagon module")):
        d.rounded_rectangle((x * S, 30 * S, (x + 250) * S, 440 * S), 18 * S, fill=TINT, outline=EDGE, width=2 * S)
        d.text(((x + 125) * S, 58 * S), t, font=f(19, 800), fill=INK, anchor="mm")
    box(d, 30, 90, 210, 66, "Adapter 12 V 3 A", "switch + 3 A fuse")
    box(d, 320, 90, 210, 66, "LM2596", "12 V to 5 V")
    box(d, 320, 180, 210, 66, "2 x MOSFET D4184", "pump switches")
    box(d, 320, 275, 210, 140, "ESP32 DevKit V1", "controller + Wi-Fi", main=True)
    d.text((425 * S, 375 * S), "BH1750 #1, MH-Z19B", font=f(14, 500), fill=MUTED, anchor="mm")
    box(d, 615, 90, 200, 66, "Air pump", "aeration 10/30 min")
    box(d, 615, 180, 200, 66, "Nutrient pump", "peristaltic")
    box(d, 920, 90, 210, 66, "Microalgae culture", "Chlorella, 1.7 L")
    box(d, 920, 180, 210, 66, "5-layer acrylic body", "40 mm thick")
    box(d, 920, 270, 210, 66, "LED strip", "31 x WS2812B")
    box(d, 920, 360, 210, 66, "Temp. probe + OD unit", "DS18B20, BH1750 #2")
    box(d, 320, 480, 210, 66, "Phone / laptop", "JSON over local Wi-Fi")
    arrow(d, [(240, 123), (320, 123)]); label(d, 280, 108, "12 V")
    arrow(d, [(530, 213), (615, 213)]); arrow(d, [(570, 213), (570, 123), (615, 123)])
    arrow(d, [(815, 123), (920, 123)], TUBE, 3); label(d, 868, 108, "P2")
    arrow(d, [(815, 213), (865, 213), (865, 140), (920, 140)], TUBE, 3); label(d, 845, 230, "P1")
    arrow(d, [(530, 303), (920, 303)]); label(d, 725, 290, "LED data (GPIO 13)")
    arrow(d, [(920, 393), (530, 393)]); label(d, 725, 380, "sensor data")
    arrow(d, [(425, 440), (425, 480)]); label(d, 450, 460, "Wi-Fi", "lm")
    d.line((30 * S, 500 * S, 70 * S, 500 * S), fill=EDGE, width=2 * S); label(d, 80, 500, "power / data", "lm")
    d.line((30 * S, 530 * S, 70 * S, 530 * S), fill=TUBE, width=3 * S); label(d, 80, 530, "air / nutrient tubing", "lm")
    im.resize((W, H), Image.LANCZOS).save(os.path.join(OUT, "fig_architecture_en.png"))

def flowchart():
    W, H = 900, 1010
    im = Image.new("RGB", (W * S, H * S), "white"); d = ImageDraw.Draw(im)
    cx, bw, bh = 330, 330, 58
    ys = dict(start=40, wifi=130, read=220, led=310, air=400, dose=500, check=640, data=780, wait=870)
    d.rounded_rectangle(((cx - 120) * S, ys["start"] * S, (cx + 120) * S, (ys["start"] + bh) * S), 29 * S, fill="white", outline=EDGE, width=2 * S)
    d.text((cx * S, (ys["start"] + bh / 2) * S), "Start (power on)", font=f(17, 750), fill=INK, anchor="mm")
    box(d, cx - bw / 2, ys["wifi"], bw, bh, "Connect Wi-Fi, sync NTP clock")
    box(d, cx - bw / 2, ys["read"], bw, bh, "Read sensors", "temperature, light, OD, CO2", main=True)
    box(d, cx - bw / 2, ys["led"], bw, bh, "Set LED by time and lux", "grow 06-18, room 18-22, off")
    box(d, cx - bw / 2, ys["air"], bw, bh, "Set air pump", "10 min on every 30 min")
    def diamond(y, t1, t2):
        pts = [((cx - 165) * S, (y + 50) * S), (cx * S, y * S), ((cx + 165) * S, (y + 50) * S), (cx * S, (y + 100) * S)]
        d.polygon(pts, fill="white", outline=EDGE); d.line(pts + [pts[0]], fill=EDGE, width=2 * S)
        d.text((cx * S, (y + 40) * S), t1, font=f(16, 600), fill=INK, anchor="mm"); d.text((cx * S, (y + 62) * S), t2, font=f(16, 600), fill=INK, anchor="mm")
    diamond(ys["dose"], "08:00 and not", "dosed yet?")
    diamond(ys["check"], "Temperature or OD", "out of range?")
    box(d, 600, ys["dose"] + 21, 260, bh, "Run nutrient pump")
    box(d, 600, ys["check"] + 21, 260, bh, "Warning / harvest flag")
    box(d, cx - bw / 2, ys["data"], bw, bh, "Update JSON data")
    box(d, cx - bw / 2, ys["wait"], bw, bh, "Wait 60 s")
    for a, b in (("start", "wifi"), ("wifi", "read"), ("read", "led"), ("led", "air")):
        arrow(d, [(cx, ys[a] + bh), (cx, ys[b])])
    arrow(d, [(cx, ys["air"] + bh), (cx, ys["dose"])])
    arrow(d, [(cx, ys["dose"] + 100), (cx, ys["check"])]); label(d, cx + 12, ys["dose"] + 118, "no", "lm")
    arrow(d, [(cx, ys["check"] + 100), (cx, ys["data"])]); label(d, cx + 12, ys["check"] + 118, "no", "lm")
    arrow(d, [(cx + 165, ys["dose"] + 50), (600, ys["dose"] + 50)]); label(d, 560, ys["dose"] + 36, "yes")
    arrow(d, [(cx + 165, ys["check"] + 50), (600, ys["check"] + 50)]); label(d, 560, ys["check"] + 36, "yes")
    arrow(d, [(730, ys["dose"] + 79), (730, ys["dose"] + 118), (cx + 4, ys["dose"] + 118)])
    arrow(d, [(730, ys["check"] + 79), (730, ys["check"] + 118), (cx + 4, ys["check"] + 118)])
    arrow(d, [(cx, ys["data"] + bh), (cx, ys["wait"])])
    arrow(d, [(cx - bw / 2, ys["wait"] + bh / 2), (60, ys["wait"] + bh / 2), (60, ys["read"] + bh / 2), (cx - bw / 2, ys["read"] + bh / 2)])
    label(d, 70, (ys["read"] + ys["wait"]) / 2, "repeat", "lm")
    im.resize((W, H), Image.LANCZOS).save(os.path.join(OUT, "fig_flowchart_en.png"))

if __name__ == "__main__":
    architecture(); flowchart(); print("ok")
