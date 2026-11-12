"""Gambar teknik hexagon Algora versi siswa SMP (A4 landscape, berwarna).

python cnc/make_smp.py  ->  output/dokumen/Algora_Gambar_Teknik_Versi_SMP.pdf
Ukuran diambil dari cnc/make_cnc.py supaya selalu sama dengan file CNC.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_cnc import (FLAT, FLAT_IN, WALL, R, R_IN, R_IN_FILLET, T_SHEET, T_RING, N_RING, THICK, WATER_Y, HOLES,
                      N_HEX, hexpts, fillet_polyline, fmt, ROOT)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black

OUT = os.path.join(ROOT, "output", "dokumen", "Algora_Gambar_Teknik_Versi_SMP.pdf")
PW, PH = 297, 210
INK = HexColor("#16233F"); MUTED = HexColor("#5B6B86"); LINE = HexColor("#9AA7BD")
BLUE = HexColor("#1F6FEB"); RED = HexColor("#E5484D"); GREEN = HexColor("#2EA043")
C_A = HexColor("#CFE8FA"); C_B = HexColor("#DCDCEA"); C_C = HexColor("#BFE9E1"); C_W = HexColor("#BFE6A8"); C_AIR = HexColor("#EEF6FF")
PAPER = HexColor("#F6F8FC"); C_LED = HexColor("#F4B740")
PAGES = 7

# ------------------------------------------------------------------ helpers --
def T(c, x, y, s, size=10, color=INK, bold=False, anchor="start", ang=0):
    c.saveState(); c.translate(x * mm, y * mm); c.rotate(ang); c.setFillColor(color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    {"start": c.drawString, "middle": c.drawCentredString, "end": c.drawRightString}[anchor](0, 0, s); c.restoreState()

def para(c, x, y, lines, size=10, lh=5.2, color=INK, bold_first=False):
    for i, ln in enumerate(lines):
        T(c, x, y - i * lh, ln, size, color, bold=bold_first and i == 0)
    return y - len(lines) * lh

def poly(c, pts, fill=None, stroke=INK, w=0.8, dash=None):
    c.setLineWidth(w); c.setStrokeColor(stroke); c.setDash(*(dash or ([], 0)))
    if fill is not None: c.setFillColor(fill)
    p = c.beginPath(); p.moveTo(pts[0][0] * mm, pts[0][1] * mm)
    for x, y in pts[1:]: p.lineTo(x * mm, y * mm)
    p.close(); c.drawPath(p, stroke=1 if stroke is not None else 0, fill=1 if fill is not None else 0); c.setDash([], 0)

def ring_path(c, outer, inner, fill, stroke=INK, w=0.8):
    c.setLineWidth(w); c.setStrokeColor(stroke); c.setFillColor(fill)
    p = c.beginPath()
    for pts in (outer, inner[::-1]):
        p.moveTo(pts[0][0] * mm, pts[0][1] * mm)
        for x, y in pts[1:]: p.lineTo(x * mm, y * mm)
        p.close()
    c.drawPath(p, stroke=1, fill=1, fillMode=0)

def card(c, x, y, w, h, fill=white, stroke=LINE, r=3):
    c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(0.6); c.roundRect(x * mm, y * mm, w * mm, h * mm, r * mm, stroke=1, fill=1)

def pill(c, x, y, s, size=11, color=BLUE, bg=white):
    c.setFont("Helvetica-Bold", size); w = c.stringWidth(s, "Helvetica-Bold", size) / mm + 4; h = size * 0.3528 + 3
    c.setFillColor(bg); c.setStrokeColor(color); c.setLineWidth(0.8); c.roundRect((x - w / 2) * mm, (y - h / 2) * mm, w * mm, h * mm, h / 2 * mm, stroke=1, fill=1)
    T(c, x, y - size * 0.3528 * 0.36, s, size, color, bold=True, anchor="middle")

def arrowhead(c, x, y, ang, color=BLUE, L=3.0, W=1.2):
    c.setFillColor(color); ca, sa = math.cos(ang), math.sin(ang)
    p = c.beginPath(); p.moveTo(x * mm, y * mm)
    p.lineTo((x - L * ca + W * sa) * mm, (y - L * sa - W * ca) * mm); p.lineTo((x - L * ca - W * sa) * mm, (y - L * sa + W * ca) * mm); p.close()
    c.drawPath(p, stroke=0, fill=1)

def kdim(c, A, B, off, label, color=BLUE, size=11, ext=True):
    """Garis ukur ramah: panah di dua ujung, angka di dalam 'pil' di tengah garis."""
    dx, dy = B[0] - A[0], B[1] - A[1]; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; nx, ny = -uy, ux
    a2 = (A[0] + nx * off, A[1] + ny * off); b2 = (B[0] + nx * off, B[1] + ny * off)
    if ext and off:
        c.setStrokeColor(LINE); c.setLineWidth(0.4); sg = 1 if off > 0 else -1
        for P0, P1 in ((A, a2), (B, b2)):
            c.line((P0[0] + nx * sg) * mm, (P0[1] + ny * sg) * mm, (P1[0] + nx * sg * 2) * mm, (P1[1] + ny * sg * 2) * mm)
    c.setStrokeColor(color); c.setLineWidth(0.9); c.line(a2[0] * mm, a2[1] * mm, b2[0] * mm, b2[1] * mm)
    ang = math.atan2(uy, ux); arrowhead(c, b2[0], b2[1], ang, color); arrowhead(c, a2[0], a2[1], ang + math.pi, color)
    pill(c, (a2[0] + b2[0]) / 2, (a2[1] + b2[1]) / 2, label, size, color)

def callout(c, P, Q, label, color=INK, size=10, right=True, dot=True):
    c.setStrokeColor(color); c.setLineWidth(0.6); c.line(P[0] * mm, P[1] * mm, Q[0] * mm, Q[1] * mm)
    e = Q[0] + (6 if right else -6); c.line(Q[0] * mm, Q[1] * mm, e * mm, Q[1] * mm)
    if dot: c.setFillColor(color); c.circle(P[0] * mm, P[1] * mm, 0.8 * mm, stroke=0, fill=1)
    T(c, e + (1.5 if right else -1.5), Q[1] - 1.2, label, size, color, bold=True, anchor="start" if right else "end")

def page(c, no, title, subtitle=None):
    c.setFillColor(PAPER); c.rect(0, 0, PW * mm, PH * mm, stroke=0, fill=1)
    c.setFillColor(INK); c.rect(0, (PH - 22) * mm, PW * mm, 22 * mm, stroke=0, fill=1)
    T(c, 12, PH - 12, title, 18, white, bold=True)
    if subtitle: T(c, 12, PH - 18.5, subtitle, 10, HexColor("#C9D6EE"))
    T(c, PW - 12, PH - 12, f"{no} / {PAGES}", 12, white, bold=True, anchor="end")
    T(c, PW - 12, PH - 18.5, "Algora - gambar teknik versi siswa", 9, HexColor("#C9D6EE"), anchor="end")
    T(c, 12, 6, "Semua angka dalam milimeter (mm). 10 mm = 1 cm. Gambar diperkecil; angka di garis ukur adalah ukuran ASLI.", 8.5, MUTED)

def tag(c, x, y, letter, fill):
    c.setFillColor(fill); c.setStrokeColor(INK); c.setLineWidth(0.8); c.circle(x * mm, y * mm, 4 * mm, stroke=1, fill=1)
    T(c, x, y - 1.6, letter, 12, INK, bold=True, anchor="middle")

def view(ox, oy, s):
    return lambda x, y: (ox + x * s, oy + y * s)

def iso_hex(cx, cy, r, k=0.32):
    return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)) * k) for a in range(0, 360, 60)]

def iso_slab(c, cx, cy, r, t, fill, rin=None, k=0.32, inner_fill=None, holes=()):
    top = iso_hex(cx, cy, r, k); bot = iso_hex(cx, cy - t, r, k)
    side = [top[0], top[5], top[4], top[3], bot[3], bot[4], bot[5], bot[0]]
    shade = HexColor("#00000000")
    poly(c, side, fill, INK, 0.6)
    c.setFillColor(HexColor("#16233F")); c.setFillAlpha(0.12); pp = c.beginPath(); pp.moveTo(side[0][0] * mm, side[0][1] * mm)
    for x, y in side[1:]: pp.lineTo(x * mm, y * mm)
    pp.close(); c.drawPath(pp, stroke=0, fill=1); c.setFillAlpha(1)
    if rin:
        ring_path(c, top, iso_hex(cx, cy, rin, k), fill, INK, 0.6)
        poly(c, iso_hex(cx, cy, rin, k), inner_fill, INK, 0.4)
    else:
        poly(c, top, fill, INK, 0.6)
    for hx, hy, d in holes:
        c.setFillColor(white); c.setStrokeColor(RED); c.setLineWidth(0.8)
        c.ellipse((cx + hx - d / 2) * mm, (cy + hy * k - d / 2 * k) * mm, (cx + hx + d / 2) * mm, (cy + hy * k + d / 2 * k) * mm, stroke=1, fill=1)

# -------------------------------------------------------------------- pages --
def p1(c):
    page(c, 1, "Kenalan: hexagon Algora dibuat dari 5 lapis akrilik", "Seperti roti lapis: lembar - cincin - cincin - cincin - lembar")
    cx, s = 72, 0.27; r = R * s; rin = R_IN * s
    # ditumpuk dari bawah (belakang) ke atas (depan), dipisah supaya terlihat
    hole = [(x * s, y * s, max(d * s, 3.5)) for _, _, d, x, y, _ in HOLES]
    iso_slab(c, cx, 40, r, 2.2, C_B, holes=hole)
    for i, yy in enumerate((74, 98, 122)):
        iso_slab(c, cx, yy, r, 4, C_C, rin=rin, inner_fill=C_W if i == 1 else PAPER)
    iso_slab(c, cx, 150, r, 2.2, C_A)
    lx = cx + r + 8
    for yy, letter, fill, l1, l2 in ((150, "A", C_A, "Lembar depan", "akrilik bening, tebal 5 mm"),
                                     (122, "C", C_C, "Cincin rangka (3 buah)", "akrilik bening, tebal 10 mm"),
                                     (74, "C", C_C, "", ""),
                                     (40, "B", C_B, "Lembar belakang", "akrilik buram, tebal 5 mm, 4 lubang")):
        if not l1: continue
        c.setStrokeColor(LINE); c.setLineWidth(0.5); c.line((cx + r + 1) * mm, (yy - 1) * mm, (lx - 1) * mm, (yy - 1) * mm)
        tag(c, lx + 4, yy - 1, letter, fill)
        T(c, lx + 10, yy, l1, 11, bold=True); T(c, lx + 10, yy - 5, l2, 9, MUTED)
    c.setStrokeColor(LINE); c.setDash([1.5, 1.5], 0); c.line((cx + r + 1) * mm, 97 * mm, (lx + 4) * mm, 97 * mm); c.line((cx + r + 1) * mm, 73 * mm, (lx + 4) * mm, 73 * mm)
    c.line((lx + 4) * mm, 73 * mm, (lx + 4) * mm, 117 * mm); c.setDash([], 0)
    T(c, cx + 20, 22, "Lapisan dipisah supaya terlihat. Setelah dilem, semuanya rapat jadi satu.", 9, MUTED, anchor="middle")
    T(c, cx, 96.5, "air alga", 9, GREEN, bold=True, anchor="middle")
    # angka penting
    x0 = 200; T(c, x0, 177, "Angka penting", 13, bold=True)
    tiles = [("300 mm", "lebar dari sisi datar ke sisi datar", "kira-kira sepanjang penggaris 30 cm"),
             ("40 mm", "tebal setelah dirakit", "5 + 10 + 10 + 10 + 5"),
             ("1,7 liter", "air alga di dalamnya", "ruang air setebal 30 mm"),
             (f"{2 + N_RING} potong", "bagian yang dipotong CNC", "1 depan, 3 cincin, 1 belakang")]
    for i, (big, l1, l2) in enumerate(tiles):
        y = 143 - i * 33; card(c, x0, y, 85, 28)
        T(c, x0 + 5, y + 15, big, 20, BLUE, bold=True); T(c, x0 + 5, y + 8.5, l1, 9.5, bold=True); T(c, x0 + 5, y + 3.5, l2, 8.5, MUTED)

def p2(c):
    page(c, 2, "Cara membaca gambar teknik", "Pelajari 6 tanda ini dulu, nanti semua halaman jadi mudah dibaca")
    W, H = 86, 78; xs = (12, 105.5, 199); ys = (100, 16)
    def box(i, title, lines):
        x, y = xs[i % 3], ys[i // 3]; card(c, x, y, W, H, white)
        c.setFillColor(BLUE); c.circle((x + 8) * mm, (y + H - 8) * mm, 4.2 * mm, stroke=0, fill=1)
        T(c, x + 8, y + H - 9.6, str(i + 1), 11, white, bold=True, anchor="middle")
        T(c, x + 15, y + H - 9.6, title, 11.5, bold=True)
        para(c, x + 5, y + 16, lines, 9, 4.6, MUTED)
        return x, y
    x, y = box(0, "Garis ukur", ["Panah di kedua ujung menunjukkan dari mana", "sampai mana diukur. Angka = panjang asli."])
    c.setStrokeColor(INK); c.setLineWidth(1.2); c.rect((x + 18) * mm, (y + 30) * mm, 50 * mm, 14 * mm)
    kdim(c, (x + 18, y + 44), (x + 68, y + 44), 7, "50")
    x, y = box(1, "Satuan milimeter (mm)", ["Semua angka dalam mm. 10 mm = 1 cm.", "Jadi 300 mm = 30 cm."])
    c.setStrokeColor(INK); c.setLineWidth(0.8); c.line((x + 13) * mm, (y + 38) * mm, (x + 73) * mm, (y + 38) * mm)
    for k in range(61):
        h = 6 if k % 10 == 0 else (4 if k % 5 == 0 else 2.2)
        c.setLineWidth(0.6 if k % 10 == 0 else 0.3); c.line((x + 13 + k) * mm, (y + 38) * mm, (x + 13 + k) * mm, (y + 38 + h) * mm)
    for k in range(0, 7): T(c, x + 13 + k * 10, y + 32.5, str(k), 8, INK, anchor="middle")
    T(c, x + 43, y + 26, "angka = cm,  garis kecil = mm", 8.5, BLUE, bold=True, anchor="middle")
    x, y = box(2, "Ø = diameter", ["Ø artinya lebar lingkaran, diukur lewat", "titik tengahnya. Ø12,5 = lubang 12,5 mm."])
    c.setStrokeColor(RED); c.setLineWidth(1.2); c.setFillColor(white); c.circle((x + 43) * mm, (y + 40) * mm, 12 * mm, stroke=1, fill=1)
    kdim(c, (x + 31, y + 40), (x + 55, y + 40), 0, "Ø24", RED, 10, ext=False)
    x, y = box(3, "Garis titik-strip = garis tengah", ["Garis ini membelah benda tepat di tengah.", "Ukuran lubang diukur dari garis ini."])
    c.setStrokeColor(INK); c.setLineWidth(1.2); c.rect((x + 18) * mm, (y + 28) * mm, 50 * mm, 26 * mm)
    c.setStrokeColor(BLUE); c.setLineWidth(0.6); c.setDash([6, 2, 1, 2], 0)
    c.line((x + 12) * mm, (y + 41) * mm, (x + 74) * mm, (y + 41) * mm); c.line((x + 43) * mm, (y + 23) * mm, (x + 43) * mm, (y + 59) * mm); c.setDash([], 0)
    x, y = box(4, "Garis putus-putus = tersembunyi", ["Bagian yang ada di belakang atau di dalam,", "jadi tidak terlihat dari depan."])
    c.setStrokeColor(INK); c.setLineWidth(1.2); c.setFillColor(C_A); c.rect((x + 18) * mm, (y + 28) * mm, 50 * mm, 26 * mm, stroke=1, fill=1)
    c.setDash([2, 1.5], 0); c.setStrokeColor(RED); c.setFillColor(C_A); c.circle((x + 43) * mm, (y + 41) * mm, 7 * mm, stroke=1, fill=0); c.setDash([], 0)
    T(c, x + 43, y + 21.5, "lubang di lembar belakang", 8.5, RED, bold=True, anchor="middle")
    x, y = box(5, "R = sudut dibulatkan", ["R4 artinya sudut dibuat melengkung", "dengan jari-jari 4 mm (seperti seperempat", "lingkaran kecil)."])
    pts = [(x + 18, y + 54), (x + 18, y + 30), (x + 68, y + 30)]
    c.setStrokeColor(INK); c.setLineWidth(1.4); p = c.beginPath(); p.moveTo(pts[0][0] * mm, pts[0][1] * mm); p.lineTo(pts[0][0] * mm, (y + 40) * mm)
    p.arcTo((x + 18) * mm, (y + 30) * mm, (x + 38) * mm, (y + 50) * mm, startAng=180, extent=90); p.lineTo(pts[2][0] * mm, pts[2][1] * mm); c.drawPath(p)
    callout(c, (x + 21, y + 33), (x + 40, y + 48), "R10 di contoh ini", BLUE, 9)

def hex_dims(c, V, sc, color=BLUE):
    pts = hexpts(FLAT)
    kdim(c, V(-R, 0), V(R, 0), -(FLAT / 2) * sc - 12, f"{fmt(2 * R)}  (sudut ke sudut)", color, 10)
    kdim(c, V(-R / 2, -FLAT / 2), V(-R / 2, FLAT / 2), R / 2 * sc + 12, f"{fmt(FLAT)}", color, 11)
    a, b = V(*pts[2]), V(*pts[1]); kdim(c, a, b, 9, f"{fmt(R)}  (1 sisi)", color, 10)

def info(c, x, y, title, letter, fill, rows, checks):
    card(c, x, y - 2, 98, 150, white)
    tag(c, x + 9, y + 139, letter, fill); T(c, x + 16, y + 137, title, 13, bold=True)
    yy = y + 126
    for k, v in rows:
        T(c, x + 6, yy, k, 9, MUTED); T(c, x + 38, yy, v, 10, INK, bold=True); yy -= 7
    yy -= 3; T(c, x + 6, yy, "Cek setelah dipotong:", 10.5, GREEN, bold=True); yy -= 7
    for ln in checks:
        c.setStrokeColor(GREEN); c.setLineWidth(0.8); c.rect((x + 6) * mm, (yy - 0.8) * mm, 3.6 * mm, 3.6 * mm)
        T(c, x + 12, yy, ln, 9.5); yy -= 6.4
    return yy

def p3(c):
    page(c, 3, "Part A - Lembar depan", "Hexagon utuh dari akrilik bening. Ini sisi yang menghadap orang.")
    V = view(100, 106, 0.36)
    poly(c, [V(*p) for p in hexpts(FLAT)], C_A, INK, 1.2)
    hex_dims(c, V, 0.36)
    T(c, *V(0, 6), "6 sisi sama panjang", 10, INK, bold=True, anchor="middle"); T(c, *V(0, -12), "6 sudut sama besar: 120°", 10, INK, bold=True, anchor="middle")
    T(c, 95, 18, "Skala kira-kira 1 : 3 (gambar diperkecil). Pakai angka di garis ukur, jangan mengukur gambar.", 8.5, MUTED, anchor="middle")
    info(c, 188, 32, "Lembar depan", "A", C_A,
         [("Bahan", "akrilik bening"), ("Tebal", f"{fmt(T_SHEET)} mm"), ("Jumlah", f"{N_HEX} buah"), ("Lubang", "tidak ada")],
         [f"Sisi datar ke sisi datar = {fmt(FLAT)} mm", f"Sudut ke sudut = {fmt(2 * R)} mm", f"Tiap sisi = {fmt(R)} mm", "Tidak ada retak atau goresan dalam", "Kertas pelindung masih menempel"])

def p4(c):
    page(c, 4, f"Part C - Cincin rangka ({N_RING} buah, ditumpuk)", "Cincin membentuk dinding. Ruang di tengah nanti berisi air alga.")
    V = view(100, 106, 0.36)
    ring_path(c, [V(*p) for p in hexpts(FLAT)], [V(*p) for p in fillet_polyline(hexpts(FLAT_IN), R_IN_FILLET)], C_C, INK, 1.2)
    poly(c, [V(*p) for p in fillet_polyline(hexpts(FLAT_IN), R_IN_FILLET)], PAPER, INK, 1.0)
    hex_dims(c, V, 0.36)
    kdim(c, V(40, -FLAT_IN / 2), V(40, FLAT_IN / 2), 0, f"{fmt(FLAT_IN)} (dalam)", GREEN, 10, ext=False)
    callout(c, V(-60, (FLAT + FLAT_IN) / 4), (V(0, 0)[0] - 50, V(0, 0)[1] + 66), f"dinding {fmt(WALL)} mm", INK, 10, right=False)
    zx, zy, zs = 163, 148, 1.6
    c0 = ((R + R_IN) / 2, 0); corner = V(*c0)
    c.setStrokeColor(BLUE); c.setLineWidth(0.6); c.setDash([2, 1.5], 0)
    c.circle(corner[0] * mm, corner[1] * mm, 5 * mm, stroke=1, fill=0)
    c.line((corner[0] + 2) * mm, (corner[1] + 5) * mm, (zx - 10) * mm, (zy - 13) * mm); c.setDash([], 0)
    c.saveState(); cp = c.beginPath(); cp.circle(zx * mm, zy * mm, 17 * mm); c.setFillColor(white); c.drawPath(cp, stroke=0, fill=1); c.clipPath(cp, stroke=0, fill=0)
    Z = lambda x, y: (zx + (x - c0[0]) * zs, zy + (y - c0[1]) * zs)
    ring_path(c, [Z(*q) for q in hexpts(FLAT)], [Z(*q) for q in fillet_polyline(hexpts(FLAT_IN), R_IN_FILLET, 16)], C_C, INK, 1.2)
    c.restoreState(); c.setStrokeColor(BLUE); c.setLineWidth(0.9); c.circle(zx * mm, zy * mm, 17 * mm, stroke=1, fill=0)
    T(c, zx, zy + 24, "sudut dalam: melengkung R4", 9, BLUE, bold=True, anchor="middle"); T(c, zx, zy + 19.5, "sudut luar: tajam", 9, INK, bold=True, anchor="middle")
    T(c, 100, 18, "Mata pahat CNC berbentuk bulat, jadi 6 sudut DALAM dibuat melengkung R4 mm. Sudut luar tetap tajam.", 8.5, MUTED, anchor="middle")
    info(c, 188, 32, "Cincin rangka", "C", C_C,
         [("Bahan", "akrilik bening"), ("Tebal", f"{fmt(T_RING)} mm"), ("Jumlah", f"{N_RING * N_HEX} buah"), ("Dinding", f"{fmt(WALL)} mm")],
         [f"Luar: sisi datar = {fmt(FLAT)} mm", f"Dalam: sisi datar = {fmt(FLAT_IN)} mm", f"Dinding di 6 sisi = {fmt(WALL)} mm", "3 cincin ditumpuk pas, tidak geser", "Sudut dalam melengkung halus"])

def p5(c):
    page(c, 5, "Part B - Lembar belakang dan 4 lubang", "Akrilik buram. Lubang P1-P4 untuk selang, kabel, dan menguras air.")
    V = view(92, 98, 0.42)
    poly(c, [V(*p) for p in hexpts(FLAT)], C_B, INK, 1.2)
    poly(c, [V(*p) for p in fillet_polyline(hexpts(FLAT_IN), R_IN_FILLET)], None, MUTED, 0.5, ([2, 1.5], 0))
    c.setStrokeColor(BLUE); c.setLineWidth(0.5); c.setDash([6, 2, 1, 2], 0)
    a, b = V(-R - 6, 0), V(R + 6, 0); c.line(a[0] * mm, a[1] * mm, b[0] * mm, b[1] * mm)
    a, b = V(0, -FLAT / 2 - 6), V(0, FLAT / 2 + 6); c.line(a[0] * mm, a[1] * mm, b[0] * mm, b[1] * mm); c.setDash([], 0)
    a, b = V(-R_IN + 30, WATER_Y), V(R_IN - 30, WATER_Y); c.setStrokeColor(GREEN); c.setDash([3, 1.5], 0); c.line(a[0] * mm, a[1] * mm, (b[0] - 18) * mm, b[1] * mm); c.setDash([], 0)
    T(c, *V(R_IN - 75, WATER_Y - 9), "garis air", 8.5, GREEN, bold=True)
    for code, _, d, x, y, _ in HOLES:
        q = V(x, y); c.setFillColor(white); c.setStrokeColor(RED); c.setLineWidth(1.1); c.circle(q[0] * mm, q[1] * mm, d / 2 * 0.42 * mm + 0.3 * mm, stroke=1, fill=1)
    kdim(c, V(-40, 125), V(0, 125), 13, "40", BLUE, 9.5); kdim(c, V(0, 125), V(40, 125), 13, "40", BLUE, 9.5)
    kdim(c, V(0, 0), V(0, 125), -22, "125", BLUE, 10); kdim(c, V(0, -125), V(0, 0), -22, "125", BLUE, 10)
    kdim(c, V(-R, 0), V(R, 0), -(FLAT / 2) * 0.42 - 10, f"{fmt(2 * R)}", BLUE, 10)
    callout(c, V(-40, 125 + 7), (V(0, 0)[0] - 50, V(0, 0)[1] + 72), "P2", RED, 11, right=False)
    callout(c, V(0, 125 + 8), (V(0, 0)[0] - 8, V(0, 0)[1] + 74), "P1", RED, 11, right=False)
    callout(c, V(40, 125 + 7), (V(0, 0)[0] + 42, V(0, 0)[1] + 72), "P3", RED, 11)
    callout(c, V(6, -125), (V(0, 0)[0] + 30, V(0, 0)[1] - 62), "P4", RED, 11)
    T(c, 92, 14.5, "Ukuran lubang diukur dari GARIS TENGAH (titik-strip biru), bukan dari tepi.", 8.5, MUTED, anchor="middle")
    x0 = 180; card(c, x0, 22, 106, 160, white)
    tag(c, x0 + 9, 173, "B", C_B); T(c, x0 + 16, 171, "Lembar belakang", 13, bold=True)
    para(c, x0 + 6, 161, [f"Bahan: akrilik buram (frosted), tebal {fmt(T_SHEET)} mm", f"Jumlah: {N_HEX} buah"], 9.5, 5.2)
    yy = 146
    for code, fn, d, x, y, isi in HOLES:
        c.setFillColor(white); c.setStrokeColor(RED); c.setLineWidth(1); c.circle((x0 + 10) * mm, (yy + 1.2) * mm, 4 * mm, stroke=1, fill=1)
        T(c, x0 + 10, yy - 0.3, code, 9, RED, bold=True, anchor="middle")
        T(c, x0 + 18, yy + 2, f"{fn}", 10, bold=True); T(c, x0 + 18, yy - 3, f"Ø{fmt(d)} mm  -  {isi}", 8.5, MUTED); yy -= 15
    T(c, x0 + 6, yy + 2, "Cek setelah dipotong:", 10.5, GREEN, bold=True); yy -= 5
    for ln in ["P1 = 15,2 mm, P2-P4 = 12,5 mm", "Cable gland bisa diputar masuk", "P1-P3 berjarak 25 mm dari tepi atas", "Sisi buram menghadap ke dinding"]:
        c.setStrokeColor(GREEN); c.setLineWidth(0.8); c.rect((x0 + 6) * mm, (yy - 0.8) * mm, 3.6 * mm, 3.6 * mm); T(c, x0 + 12, yy, ln, 9.5); yy -= 6.2

def p6(c):
    page(c, 6, "Susunan lapisan (dilihat dari samping)", "Bayangkan hexagon dipotong tegak lewat lubang P1 dan P4, lalu dilihat dari samping.")
    xs = [0, T_SHEET, T_SHEET + T_RING, T_SHEET + 2 * T_RING, T_SHEET + 3 * T_RING, THICK]
    def section(P, ylo, yhi, bubbles=()):
        def rect(xa, ya, xb, yb_, fill, w=0.8):
            ya, yb_ = max(ya, ylo), min(yb_, yhi)
            if yb_ <= ya: return
            a, b = P(xa, ya), P(xb, yb_); poly(c, [a, (b[0], a[1]), b, (a[0], b[1])], fill, INK, w)
        rect(xs[1], WATER_Y, xs[4], FLAT_IN / 2, C_AIR, 0.4); rect(xs[1], -FLAT_IN / 2, xs[4], WATER_Y, C_W, 0.4)
        rect(xs[0], -FLAT / 2, xs[1], FLAT / 2, C_A); rect(xs[4], -FLAT / 2, xs[5], FLAT / 2, C_B)
        for k in range(1, 4):
            rect(xs[k], FLAT_IN / 2, xs[k + 1], FLAT / 2, C_C); rect(xs[k], -FLAT / 2, xs[k + 1], -FLAT_IN / 2, C_C)
        for code, _, d, x, y, _ in HOLES:
            if x == 0 and ylo < y < yhi:
                a, b = P(xs[4] - 0.2, y - d / 2), P(xs[5] + 0.2, y + d / 2)
                c.setFillColor(PAPER); c.rect(a[0] * mm, a[1] * mm, (b[0] - a[0]) * mm, (b[1] - a[1]) * mm, stroke=0, fill=1)
        for bx_, by_ in bubbles:
            q = P(bx_, by_); c.setFillColor(white); c.setStrokeColor(HexColor("#7FB86A")); c.setLineWidth(0.5); c.circle(q[0] * mm, q[1] * mm, 1.2 * mm, stroke=1, fill=1)
    # kiri: potongan utuh, kecil (lebar dibesarkan agar lapisan terlihat)
    s1 = 0.42; Pf = lambda x, y: (30 + x * s1 * 1.6, 103 + y * s1)
    section(Pf, -FLAT / 2, FLAT / 2)
    a, b = Pf(-3, 98), Pf(THICK + 3, FLAT / 2 + 3); c.setStrokeColor(RED); c.setLineWidth(0.8); c.setDash([2, 1.5], 0)
    c.rect(a[0] * mm, a[1] * mm, (b[0] - a[0]) * mm, (b[1] - a[1]) * mm); c.setDash([], 0)
    T(c, 44, 28, "Utuh (diperkecil)", 9, MUTED, bold=True, anchor="middle"); T(c, 44, 23.5, "tebalnya dilebarkan agar terlihat", 7.5, MUTED, anchor="middle")
    kdim(c, Pf(THICK, -FLAT / 2), Pf(THICK, FLAT / 2), -8, "300", BLUE, 9)
    # tengah: bagian atas diperbesar 2x
    s2 = 2.0; ylo = 98; Pz = lambda x, y: (100 + x * s2, 150 + (y - FLAT / 2) * s2)
    section(Pz, ylo, FLAT / 2, bubbles=((12, 101), (22, 103.2), (30, 100.5)))
    a, b = Pz(-3, ylo), Pz(THICK + 3, FLAT / 2 + 3); c.setStrokeColor(RED); c.setLineWidth(0.8); c.setDash([2, 1.5], 0)
    c.rect(a[0] * mm, a[1] * mm, (b[0] - a[0]) * mm, (b[1] - a[1]) * mm); c.setDash([], 0)
    c.setStrokeColor(RED); c.setLineWidth(0.5); c.setDash([2, 1.5], 0)
    za, zb = Pf(THICK + 3, FLAT / 2 + 3), Pz(-3, FLAT / 2 + 3); c.line(za[0] * mm, za[1] * mm, zb[0] * mm, zb[1] * mm)
    za, zb = Pf(THICK + 3, 98), Pz(-3, ylo); c.line(za[0] * mm, za[1] * mm, zb[0] * mm, zb[1] * mm); c.setDash([], 0)
    hy = 125; g0, g1 = Pz(THICK, hy - 11), Pz(THICK + 9, hy + 11)
    c.setFillColor(HexColor("#D0D4DC")); c.setStrokeColor(INK); c.setLineWidth(0.6); c.rect(g0[0] * mm, g0[1] * mm, (g1[0] - g0[0]) * mm, (g1[1] - g0[1]) * mm, stroke=1, fill=1)
    l0, l1 = Pz(xs[2], FLAT / 2), Pz(xs[3], FLAT / 2 + 2); c.setFillColor(C_LED); c.rect(l0[0] * mm, l0[1] * mm, (l1[0] - l0[0]) * mm, (l1[1] - l0[1]) * mm, stroke=1, fill=1)
    w0, w1 = Pz(xs[1], WATER_Y), Pz(xs[4], WATER_Y); c.setStrokeColor(GREEN); c.setLineWidth(1.2); c.setDash([3, 1.5], 0); c.line(w0[0] * mm, w0[1] * mm, w1[0] * mm, w1[1] * mm); c.setDash([], 0)
    top = FLAT / 2
    for k, lbl in enumerate(("5", "10", "10", "10", "5")):
        kdim(c, Pz(xs[k], top), Pz(xs[k + 1], top), 7 + (k % 2) * 8, lbl, BLUE, 9.5)
    kdim(c, Pz(0, top), Pz(THICK, top), 24, f"tebal total {fmt(THICK)}", BLUE, 10.5)
    kdim(c, Pz(0, FLAT_IN / 2), Pz(0, top), 7, fmt(WALL), BLUE, 9.5)
    kdim(c, Pz(0, WATER_Y), Pz(0, top), 20, "45", GREEN, 9.5)
    T(c, 140, 33, "Bagian atas, diperbesar 2 kali", 9, MUTED, bold=True, anchor="middle")
    # nomor + keterangan
    marks = [(Pz(2.5, 128), "Lembar depan A, bening 5 mm", C_A), (Pz(xs[2] + 5, 144.5), "3 cincin rangka C, masing-masing 10 mm", C_C),
             (Pz(xs[4] + 2.5, 110), "Lembar belakang B, buram 5 mm", C_B), (Pz(THICK + 4.5, 133), "Lubang P1, dipasang cable gland PG9", HexColor("#D0D4DC")),
             (Pz(20, top + 1), "Strip LED, menempel di luar cincin", C_LED), (Pz(20, 120), "Celah udara, gelembung pecah di sini", C_AIR),
             (Pz(20, 101.5), "Air + alga, garis hijau = permukaan air", C_W)]
    card(c, 196, 34, 90, 140, white)
    T(c, 201, 164, "Keterangan nomor", 12, bold=True)
    for i, ((px, py), txt, fill) in enumerate(marks):
        c.setFillColor(INK); c.circle(px * mm, py * mm, 2.6 * mm, stroke=0, fill=1); T(c, px, py - 1.1, str(i + 1), 8.5, white, bold=True, anchor="middle")
        y = 150 - i * 16.5; c.setFillColor(fill); c.setStrokeColor(INK); c.setLineWidth(0.5); c.roundRect(201 * mm, (y - 3.5) * mm, 8 * mm, 8 * mm, 1.5 * mm, stroke=1, fill=1)
        T(c, 205, y - 0.6, str(i + 1), 9.5, INK, bold=True, anchor="middle")
        head, tail = txt.split(", ", 1)
        T(c, 212, y + 1.4, head, 9.5, INK, bold=True); T(c, 212, y - 3.4, tail, 8.5, MUTED)
    T(c, 12, 14.5, "Semua lapisan direkatkan dengan silikon akuarium. Lubang P1-P3 ada di atas garis air, jadi tidak bocor.", 8.5, MUTED)

def p7(c):
    page(c, 7, "Merakit dan memeriksa", "Ikuti urutan ini. Kerjakan bersama guru, dan tunggu silikon kering sebelum lanjut.")
    steps = [("Cek ukuran", "Ukur semua part dengan penggaris\natau jangka sorong (tabel di kanan)."),
             ("Bersihkan", "Lepas kertas pelindung, lap dengan\nalkohol 70%. Jangan pegang tepinya."),
             ("Tumpuk cincin", "Silikon tipis di antara 3 cincin,\ntekan rata, jepit, tunggu 24 jam."),
             ("Lem ke belakang", "Rekatkan tumpukan cincin ke part B.\nPasang cable gland di P1-P4."),
             ("Tutup depan", "Rekatkan part A di atasnya.\nTunggu kering 24 jam lagi."),
             ("Uji bocor", "Isi air, berdirikan di atas tisu\n24 jam. Tisu harus tetap kering.")]
    for i, (t1, t2) in enumerate(steps):
        x, y = 12 + (i % 2) * 70, 136 - (i // 2) * 48
        card(c, x, y, 66, 42, white)
        c.setFillColor(BLUE); c.circle((x + 9) * mm, (y + 33) * mm, 5 * mm, stroke=0, fill=1); T(c, x + 9, y + 31.2, str(i + 1), 13, white, bold=True, anchor="middle")
        T(c, x + 17, y + 31.5, t1, 11.5, bold=True)
        para(c, x + 5, y + 18, t2.split("\n"), 8.8, 4.8, MUTED)
    x0 = 158; T(c, x0, 182, "Tabel cek ukuran (isi setelah dipotong)", 12, bold=True)
    rows = [("A", "Sisi datar ke sisi datar", "300"), ("A", "Sudut ke sudut", "346,4"), ("C1", "Luar, sisi datar", "300"), ("C1", "Dalam, sisi datar", "278"),
            ("C2", "Luar, sisi datar", "300"), ("C2", "Dalam, sisi datar", "278"), ("C3", "Luar, sisi datar", "300"), ("C3", "Dalam, sisi datar", "278"),
            ("B", "Sisi datar ke sisi datar", "300"), ("B", "Lubang P1", "Ø15,2"), ("B", "Lubang P2 / P3 / P4", "Ø12,5"), ("B", "P1 ke tepi atas", "25"),
            ("Rakit", "Tebal total", "40")]
    cols = [("Part", 14), ("Yang diukur", 50), ("Target (mm)", 22), ("Hasil ukur", 24), ("OK?", 16)]
    y = 175; rh = 10.4
    card(c, x0, y - rh * (len(rows) + 1) - 1, sum(w for _, w in cols), rh * (len(rows) + 1) + 1, white, LINE, 2)
    xx = x0
    for hd, w in cols: T(c, xx + 2, y - 6.6, hd, 9, INK, bold=True); xx += w
    for i, r_ in enumerate(rows):
        yy = y - rh * (i + 1); c.setStrokeColor(LINE); c.setLineWidth(0.35); c.line(x0 * mm, yy * mm, (x0 + 126) * mm, yy * mm)
        xx = x0
        for j, (hd, w) in enumerate(cols):
            if j < 3: T(c, xx + 2, yy - 6.6, r_[j], 9, INK, bold=(j == 2))
            elif j == 4: c.setStrokeColor(GREEN); c.setLineWidth(0.8); c.rect((xx + 5) * mm, (yy - 7.4) * mm, 4.5 * mm, 4.5 * mm)
            else: c.setStrokeColor(LINE); c.setLineWidth(0.4); c.line((xx + 2) * mm, (yy - 7.6) * mm, (xx + w - 2) * mm, (yy - 7.6) * mm)
            xx += w
    T(c, x0, 22, "Boleh selisih sampai +/- 0,5 mm. Jika lebih, beri tahu operator CNC sebelum dilem.", 9, MUTED)
    T(c, 12, 22, "Keselamatan: silikon dan lem dipakai di ruang terbuka. Jangan pegang tepi akrilik yang tajam.", 9, RED, bold=True)

if __name__ == "__main__":
    c = canvas.Canvas(OUT, pagesize=landscape(A4)); c.setTitle("Algora - Gambar Teknik Versi Siswa"); c.setAuthor("Tim Algora")
    for f in (p1, p2, p3, p4, p5, p6, p7):
        f(c); c.showPage()
    c.save(); print("PDF:", OUT)
