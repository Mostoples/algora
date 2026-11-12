"""Concept board: python showreel/concept_board.py -> output/concept/ALGORA_concept_board.png"""
import os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brand import *

C = os.path.join(ROOT, "output", "concept")
ITEMS = [
    ("A1", "Produk · Exploded", "concept_hero.png", "Modul hexagon 300 mm: akrilik, kultur, inti AIoT, konektor 6 sisi"),
    ("B1", "Dinding", "concept_wall.png", "Ruang tamu sore — karakter memasang modul baru (snap)"),
    ("B2", "Lantai / paving", "concept_floor.png", "Taman blue-hour — jalur paving bercahaya, karakter berjalan"),
    ("B3", "Lampu", "concept_lamp.png", "Pendant 7 modul di atas meja makan + kontrol app"),
    ("B4", "Genting", "concept_roof.png", "Pergola beratap modul — cahaya matahari tersaring hijau"),
]
W, H = 2400, 2700
im = aura_bg((W, H))
d = ImageDraw.Draw(im)
c, p = chip("KONSEP 3D · PILIH ARAH")
im.paste(c, (80 - p, 60 - p), c)
d.text((80, 130), "Algora", font=font(84), fill=INK)
grad_text(im, (80 + d.textlength("Algora ", font=font(84)), 130), "in-use scenes", font(84), ALGAE, ALGAE2)
d.text((80, 240), "Still konsep (render cepat 960 px). Pilih/komentari tiap scene sebelum render video penuh.", font=font(30, 500), fill=INK2)
cw, ch = 1080, 608
pos = [(80, 330), (1240, 330), (80, 1120), (1240, 1120), (660, 1910)]
ITEMS = ITEMS
for (lab, title, fn, desc), (x, y) in zip(ITEMS, pos):
    f = os.path.join(C, fn)
    if not os.path.exists(f):
        continue
    cd, pad = card((cw + 24, ch + 120), 26, 245)
    im.paste(cd, (x - 12 - pad, y - 12 - pad), cd)
    img = Image.open(f).convert("RGB")
    img = img.resize((cw, ch))
    im.paste(img, (x, y))
    d.rounded_rectangle((x + 16, y + 16, x + 96, y + 64), 14, fill=BLUE)
    d.text((x + 56, y + 40), lab, font=font(28), fill=(255, 255, 255), anchor="mm")
    d.text((x, y + ch + 22), title, font=font(36), fill=INK)
    d.text((x, y + ch + 72), desc, font=font(24, 500), fill=INK2)
im.save(os.path.join(C, "ALGORA_concept_board.png"))
print("board ok")
