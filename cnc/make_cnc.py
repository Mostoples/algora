"""Algora hexagon: file potong CNC (DXF + SVG, 1:1 mm) dan gambar teknik PDF (A3).

python cnc/make_cnc.py   ->  output/cnc/*.dxf|*.svg  +  output/dokumen/Algora_Gambar_Teknik_Hexagon.pdf
Semua ukuran berasal dari konstanta di bawah; ubah di sini lalu jalankan ulang.
"""
import math, os
import ezdxf
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output", "cnc"); os.makedirs(OUT, exist_ok=True)
PDF = os.path.join(ROOT, "output", "dokumen", "Algora_Gambar_Teknik_Hexagon.pdf")

# ------------------------------------------------------------- dimensi (mm) --
FLAT = 300.0                 # sisi datar ke sisi datar (luar)
WALL = 11.0                  # lebar dinding cincin
FLAT_IN = FLAT - 2 * WALL    # 278
R_IN_FILLET = 4.0            # radius sudut dalam cincin (pahat CNC <= 8 mm)
T_SHEET, T_RING, N_RING = 5.0, 10.0, 3
THICK = 2 * T_SHEET + N_RING * T_RING   # 40
WATER_Y = 105.0              # garis air dari titik tengah
GAP = 15.0                   # jarak antar-part saat nesting
SHEET_W, SHEET_H = 1220.0, 2440.0
N_HEX = 1                    # jumlah hexagon yang dipotong (tahap 1: hexagon induk saja)
HOLES = [  # kode, fungsi, diameter, x, y (dari titik tengah), isi
    ("P1", "Isi air + ventilasi", 15.2, 0.0, 125.0, "Cable gland PG9"),
    ("P2", "Selang udara masuk", 12.5, -40.0, 125.0, "Cable gland PG7"),
    ("P3", "Kabel sensor suhu", 12.5, 40.0, 125.0, "Cable gland PG7"),
    ("P4", "Kuras / panen", 12.5, 0.0, -125.0, "Cable gland PG7 + selang + klem"),
]
R = FLAT / math.sqrt(3)          # 173.205 = panjang sisi = jari-jari sudut
R_IN = FLAT_IN / math.sqrt(3)    # 160.503

def hexpts(flat, cx=0.0, cy=0.0):
    r = flat / math.sqrt(3)
    return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(0, 360, 60)]

def fillet(pts, r):
    """Sudut poligon CCW dibulatkan: list (T1, T2, center) per sudut."""
    out, n = [], len(pts)
    for i in range(n):
        V, P, N = pts[i], pts[i - 1], pts[(i + 1) % n]
        u1 = _unit(P[0] - V[0], P[1] - V[1]); u2 = _unit(N[0] - V[0], N[1] - V[1])
        th = math.acos(u1[0] * u2[0] + u1[1] * u2[1])
        t = r / math.tan(th / 2); d = r / math.sin(th / 2)
        b = _unit(u1[0] + u2[0], u1[1] + u2[1])
        out.append(((V[0] + u1[0] * t, V[1] + u1[1] * t), (V[0] + u2[0] * t, V[1] + u2[1] * t), (V[0] + b[0] * d, V[1] + b[1] * d)))
    return out

def _unit(x, y):
    l = math.hypot(x, y); return (x / l, y / l)

def fillet_polyline(pts, r, seg=10):
    """Titik-titik (untuk PDF) dari poligon bersudut bulat."""
    res = []
    for T1, T2, C in fillet(pts, r):
        a1 = math.atan2(T1[1] - C[1], T1[0] - C[0]); a2 = math.atan2(T2[1] - C[1], T2[0] - C[0])
        while a2 < a1: a2 += 2 * math.pi
        for k in range(seg + 1):
            a = a1 + (a2 - a1) * k / seg
            res.append((C[0] + r * math.cos(a), C[1] + r * math.sin(a)))
    return res

# ------------------------------------------------------------------ parts --
# tiap part: list of ("poly", pts, layer) | ("fpoly", pts, r, layer) | ("circle", cx, cy, d, layer)
def part_A(cx=0, cy=0):
    return [("poly", hexpts(FLAT, cx, cy), "POTONG_LUAR")]

def part_B(cx=0, cy=0):
    g = [("poly", hexpts(FLAT, cx, cy), "POTONG_LUAR")]
    for code, _, d, x, y, _ in HOLES:
        g.append(("circle", cx + x, cy + y, d, "POTONG_DALAM"))
    return g

def part_C(cx=0, cy=0):
    return [("poly", hexpts(FLAT, cx, cy), "POTONG_LUAR"), ("fpoly", hexpts(FLAT_IN, cx, cy), R_IN_FILLET, "POTONG_DALAM")]

PARTS = {
    "A": dict(name="Lembar depan", mat="Akrilik bening", t=T_SHEET, per=1, fn=part_A),
    "B": dict(name="Lembar belakang", mat="Akrilik frosted (buram)", t=T_SHEET, per=1, fn=part_B),
    "C": dict(name="Cincin rangka", mat="Akrilik bening", t=T_RING, per=N_RING, fn=part_C),
}

def honeycomb(n, cols):
    """Pusat-pusat hexagon flat-top tersusun sarang lebah dengan celah GAP antar-sisi."""
    rp = R * (FLAT + GAP) / FLAT
    pos = []
    for i in range(n):
        c, rrow = i % cols, i // cols
        pos.append((c * 1.5 * rp, rrow * (FLAT + GAP) + (c % 2) * (FLAT + GAP) / 2))
    xs = [p[0] for p in pos]; ys = [p[1] for p in pos]
    x0, y0 = min(xs) - R, min(ys) - FLAT / 2
    pos = [(x - x0, y - y0) for x, y in pos]
    return pos, max(xs) - min(xs) + 2 * R, max(ys) - min(ys) + FLAT

# ------------------------------------------------------------- DXF / SVG --
def write_dxf(path, geoms, notes):
    doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM; doc.header["$INSUNITS"] = 4
    doc.layers.add("POTONG_LUAR", color=1); doc.layers.add("POTONG_DALAM", color=5); doc.layers.add("KETERANGAN_JANGAN_DIPOTONG", color=8)
    msp = doc.modelspace()
    bulge = math.tan(math.radians(60) / 4)
    for g in geoms:
        if g[0] == "poly":
            msp.add_lwpolyline(g[1], close=True, dxfattribs={"layer": g[2]})
        elif g[0] == "fpoly":
            pts = []
            for T1, T2, _ in fillet(g[1], g[2]):
                pts += [(T1[0], T1[1], 0, 0, bulge), (T2[0], T2[1], 0, 0, 0)]
            msp.add_lwpolyline(pts, format="xyseb", close=True, dxfattribs={"layer": g[3]})
        elif g[0] == "circle":
            msp.add_circle((g[1], g[2]), g[3] / 2, dxfattribs={"layer": g[4]})
    for x, y, txt in notes:
        msp.add_text(txt, height=8, dxfattribs={"layer": "KETERANGAN_JANGAN_DIPOTONG"}).set_placement((x, y))
    doc.saveas(path)

def write_svg(path, geoms, w, h, notes):
    f = lambda x, y: f"{x:.3f},{h - y:.3f}"
    el = []
    col = {"POTONG_LUAR": "#ff0000", "POTONG_DALAM": "#0000ff"}
    for g in geoms:
        if g[0] == "poly":
            el.append(f'<polygon points="{" ".join(f(*p) for p in g[1])}" fill="none" stroke="{col[g[2]]}" stroke-width="0.1"/>')
        elif g[0] == "fpoly":
            fl = fillet(g[1], g[2]); d = f"M{f(*fl[0][1])}"
            for T1, T2, _ in fl[1:] + fl[:1]:
                d += f" L{f(*T1)} A{g[2]},{g[2]} 0 0 1 {f(*T2)}"
            el.append(f'<path d="{d} Z" fill="none" stroke="{col[g[3]]}" stroke-width="0.1"/>')
        elif g[0] == "circle":
            el.append(f'<circle cx="{g[1]:.3f}" cy="{h - g[2]:.3f}" r="{g[3] / 2:.3f}" fill="none" stroke="{col[g[4]]}" stroke-width="0.1"/>')
    txt = "".join(f'<text x="{x:.1f}" y="{h - y:.1f}" font-family="Arial" font-size="8" fill="#888888">{t}</text>' for x, y, t in notes)
    open(path, "w", encoding="utf-8").write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="{w:.3f}mm" height="{h:.3f}mm" viewBox="0 0 {w:.3f} {h:.3f}">\n'
        f'<g id="POTONG">{"".join(el)}</g>\n<g id="KETERANGAN_JANGAN_DIPOTONG">{txt}</g>\n</svg>\n')

def export_cut_files():
    files = []
    for old in os.listdir(OUT):
        if old.startswith("Algora_") and old.endswith((".dxf", ".svg")): os.remove(os.path.join(OUT, old))
    for key, p in PARTS.items():
        tag = f"Algora_{key}_{p['name'].replace(' ', '_')}_{p['t']:.0f}mm"
        # satu buah
        g = p["fn"](R, FLAT / 2)
        note = [(5, -14, f"{key} {p['name']} - {p['mat']} {p['t']:.0f} mm - 1:1 mm")]
        write_dxf(os.path.join(OUT, tag + "_1buah.dxf"), g, note)
        write_svg(os.path.join(OUT, tag + "_1buah.svg"), g, 2 * R, FLAT, [])
        # nesting untuk N_HEX hexagon
        n = p["per"] * N_HEX; cols = 3
        pos, w, h = honeycomb(n, cols)
        if n == 1:
            files.append((key, n, w, h, pos, tag + "_1buah")); continue
        g = [e for cx, cy in pos for e in p["fn"](cx, cy)]
        note = [(5, -14, f"{key} {p['name']} x{n} - {p['mat']} {p['t']:.0f} mm - area {w:.0f} x {h:.0f} mm - 1:1 mm")]
        write_dxf(os.path.join(OUT, tag + f"_{n}buah_nesting.dxf"), g, note)
        write_svg(os.path.join(OUT, tag + f"_{n}buah_nesting.svg"), g, w, h, [])
        files.append((key, n, w, h, pos, tag + f"_{n}buah_nesting"))
    return files

# --------------------------------------------------------------- PDF tools --
INK, THIN, MID = 0.0, 0.25, 0.5
class V:  # view: titik part (mm) -> halaman (pt)
    def __init__(s, c, ox, oy, sc): s.c, s.ox, s.oy, s.sc = c, ox, oy, sc
    def P(s, x, y): return ((s.ox + x * s.sc) * mm, (s.oy + y * s.sc) * mm)
    def pm(s, x, y): return (s.ox + x * s.sc, s.oy + y * s.sc)   # halaman dalam mm
    def poly(s, pts, w=MID, dash=None, close=True):
        c = s.c; c.setLineWidth(w); c.setDash(*(dash or ([], 0)))
        p = c.beginPath(); p.moveTo(*s.P(*pts[0]))
        for q in pts[1:]: p.lineTo(*s.P(*q))
        if close: p.close()
        c.drawPath(p, stroke=1, fill=0); c.setDash([], 0)
    def line(s, a, b, w=THIN, dash=None): s.poly([a, b], w, dash, close=False)
    def circle(s, x, y, d, w=MID, dash=None):
        c = s.c; c.setLineWidth(w); c.setDash(*(dash or ([], 0))); c.circle(*s.P(x, y), d / 2 * s.sc * mm, stroke=1, fill=0); c.setDash([], 0)
    def center(s, x, y, size, sy=None):
        sy = size if sy is None else sy
        s.line((x - size, y), (x + size, y), 0.18, ([6, 2, 1, 2], 0)); s.line((x, y - sy), (x, y + sy), 0.18, ([6, 2, 1, 2], 0))

def arrow(c, x, y, ang):
    L, W = 2.6, 0.9
    ca, sa = math.cos(ang), math.sin(ang)
    p = c.beginPath(); p.moveTo(x * mm, y * mm)
    p.lineTo((x - L * ca + W * sa) * mm, (y - L * sa - W * ca) * mm); p.lineTo((x - L * ca - W * sa) * mm, (y - L * sa + W * ca) * mm); p.close()
    c.drawPath(p, stroke=0, fill=1)

def text(c, x, y, s, size=8, ang=0, anchor="middle", bold=False):
    c.saveState(); c.translate(x * mm, y * mm); c.rotate(ang)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    {"middle": c.drawCentredString, "start": c.drawString, "end": c.drawRightString}[anchor](0, 0, s)
    c.restoreState()

def dim(c, A, B, off, label, size=8):
    """Ukuran sejajar antara titik halaman A dan B (mm), digeser off mm ke kiri arah A->B."""
    dx, dy = B[0] - A[0], B[1] - A[1]; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; nx, ny = -uy, ux
    sg = 1 if off >= 0 else -1
    a2 = (A[0] + nx * off, A[1] + ny * off); b2 = (B[0] + nx * off, B[1] + ny * off)
    c.setLineWidth(THIN); c.setDash([], 0)
    for P0, P1 in ((A, a2), (B, b2)):
        c.line((P0[0] + nx * sg * 1.2) * mm, (P0[1] + ny * sg * 1.2) * mm, (P1[0] + nx * sg * 1.8) * mm, (P1[1] + ny * sg * 1.8) * mm)
    c.line(a2[0] * mm, a2[1] * mm, b2[0] * mm, b2[1] * mm)
    ang = math.atan2(uy, ux); arrow(c, b2[0], b2[1], ang); arrow(c, a2[0], a2[1], ang + math.pi)
    deg = math.degrees(ang)
    if deg > 90.1 or deg < -89.9: deg += 180
    tx, ty = (a2[0] + b2[0]) / 2, (a2[1] + b2[1]) / 2
    ux2, uy2 = -math.sin(math.radians(deg)), math.cos(math.radians(deg))
    text(c, tx + ux2 * 1.1, ty + uy2 * 1.1, label, size, deg)

def leader(c, P, Q, label, size=8, right=True):
    c.setLineWidth(THIN); c.line(P[0] * mm, P[1] * mm, Q[0] * mm, Q[1] * mm)
    arrow(c, P[0], P[1], math.atan2(P[1] - Q[1], P[0] - Q[0]))
    e = Q[0] + (10 if right else -10); c.line(Q[0] * mm, Q[1] * mm, e * mm, Q[1] * mm)
    text(c, e + (1 if right else -1), Q[1] - 1, label, size, anchor="start" if right else "end")

def fmt(v): return f"{v:.1f}".replace(".", ",").replace(",0", "") if abs(v - round(v)) < 0.05 else f"{v:.1f}".replace(".", ",")

PW, PH = 420, 297
def frame(c, no, total, title, scale):
    c.setLineWidth(0.7); c.rect(10 * mm, 10 * mm, (PW - 20) * mm, (PH - 20) * mm)
    x0, y0, w, h = PW - 10 - 190, 10, 190, 34
    c.setLineWidth(0.5); c.rect(x0 * mm, y0 * mm, w * mm, h * mm)
    for yy in (y0 + 22, y0 + 11): c.line(x0 * mm, yy * mm, (x0 + w) * mm, yy * mm)
    for xx in (x0 + 120, x0 + 155): c.line(xx * mm, y0 * mm, xx * mm, (y0 + 22) * mm)
    text(c, x0 + 3, y0 + 26, "ALGORA - Hexagon fotobioreaktor (prototipe sekolah)", 10, anchor="start", bold=True)
    text(c, x0 + 3, y0 + 14.5, title, 9, anchor="start", bold=True)
    text(c, x0 + 3, y0 + 3.5, "Satuan: mm  |  Toleransi umum: +/-0,2  |  Proyeksi: sudut pertama", 7, anchor="start")
    text(c, x0 + 122, y0 + 14.5, "Skala", 7, anchor="start"); text(c, x0 + 122, y0 + 3.5, scale, 9, anchor="start", bold=True)
    text(c, x0 + 157, y0 + 14.5, "Lembar", 7, anchor="start"); text(c, x0 + 157, y0 + 3.5, f"{no} / {total}", 9, anchor="start", bold=True)
    text(c, 14, 13, "Tanggal: 2026-10-13  |  Digambar: tim Algora  |  Dibuat dari cnc/make_cnc.py", 7, anchor="start")

def table(c, x, y, cols, rows, size=7.5, rowh=6.2, head=True):
    """cols: list (judul, lebar mm). y = tepi atas."""
    W = sum(w for _, w in cols); n = len(rows) + 1
    c.setLineWidth(0.4); c.rect(x * mm, (y - n * rowh) * mm, W * mm, n * rowh * mm)
    for i in range(1, n): c.setLineWidth(0.25 if i > 1 else 0.4); c.line(x * mm, (y - i * rowh) * mm, (x + W) * mm, (y - i * rowh) * mm)
    xx = x
    for j, (hd, w) in enumerate(cols):
        if j: c.setLineWidth(0.25); c.line(xx * mm, y * mm, xx * mm, (y - n * rowh) * mm)
        text(c, xx + 1.5, y - rowh + 1.9, hd, size, anchor="start", bold=True)
        for i, r in enumerate(rows):
            text(c, xx + 1.5, y - (i + 2) * rowh + 1.9, str(r[j]), size, anchor="start")
        xx += w
    return y - n * rowh

def notes(c, x, y, lines, size=8, lh=4.6, title=None):
    if title: text(c, x, y, title, 9, anchor="start", bold=True); y -= lh + 1
    for ln in lines:
        text(c, x, y, ln, size, anchor="start"); y -= lh
    return y

def hatch_rect(c, x0, y0, x1, y1, step=1.6):
    c.saveState(); p = c.beginPath(); p.rect(x0 * mm, y0 * mm, (x1 - x0) * mm, (y1 - y0) * mm); c.clipPath(p, stroke=0, fill=0)
    c.setLineWidth(0.18); k = x0 - (y1 - y0)
    while k < x1:
        c.line(k * mm, y0 * mm, (k + (y1 - y0)) * mm, y1 * mm); k += step
    c.restoreState()
    c.setLineWidth(MID); c.rect(x0 * mm, y0 * mm, (x1 - x0) * mm, (y1 - y0) * mm)

# ------------------------------------------------------------- PDF sheets --
TOTAL = 5
def sheet1(c):
    frame(c, 1, TOTAL, "Rakitan dan daftar bagian", "1 : 2")
    text(c, 20, 278, "1. Rakitan hexagon Algora (dilihat dari depan dan samping)", 12, anchor="start", bold=True)
    v = V(c, 115, 150, 0.5)
    v.poly(hexpts(FLAT), 0.7); v.poly(fillet_polyline(hexpts(FLAT_IN), R_IN_FILLET), 0.35)
    for _, _, d, x, y, _ in HOLES: v.circle(x, y, d, 0.3, ([2, 1.5], 0))
    v.line((-90, WATER_Y), (90, WATER_Y), 0.3, ([4, 2], 0)); text(c, *v.pm(-60, WATER_Y + 3), "garis air", 7)
    v.center(0, 0, 185, 158)
    pts = hexpts(FLAT)
    dim(c, v.pm(-R, 0), v.pm(R, 0), -82, f"{fmt(2 * R)} (sudut ke sudut)")
    dim(c, v.pm(-R / 2, -FLAT / 2), v.pm(-R / 2, FLAT / 2), 50, f"{fmt(FLAT)} (sisi datar ke sisi datar)")
    dim(c, v.pm(*pts[2]), v.pm(*pts[1]), 8, f"{fmt(R)} (panjang sisi)")
    text(c, 115, 60, "Tampak depan  (lubang P1-P4 di lembar belakang digambar putus-putus)", 8)
    # tampak samping
    sx = 212; vs = V(c, sx, 150, 0.5)
    layers = [T_SHEET] + [T_RING] * N_RING + [T_SHEET]; xx = 0
    for t in layers:
        vs.poly([(xx, -FLAT / 2), (xx + t, -FLAT / 2), (xx + t, FLAT / 2), (xx, FLAT / 2)], 0.5); xx += t
    dim(c, vs.pm(0, FLAT / 2), vs.pm(THICK, FLAT / 2), 8, f"{fmt(THICK)}")
    dim(c, vs.pm(THICK, -FLAT / 2), vs.pm(THICK, FLAT / 2), -10, f"{fmt(FLAT)}")
    text(c, sx + 10, 60, "Tampak samping", 8)
    text(c, sx - 3, 158, "depan", 7, ang=90); text(c, sx + 25, 158, "belakang", 7, ang=90)
    # daftar bagian
    rows = [
        ("A", "Lembar depan", "Akrilik bening", "5", "1", str(1 * N_HEX), "CNC, lembar 2"),
        ("B", "Lembar belakang + 4 lubang", "Akrilik frosted", "5", "1", str(1 * N_HEX), "CNC, lembar 3"),
        ("C", "Cincin rangka", "Akrilik bening", "10", str(N_RING), str(N_RING * N_HEX), "CNC, lembar 2"),
        ("D", "Strip LED WS2812B 30 LED/m", "-", "-", f"{fmt(6 * R)} mm", str(N_HEX), "31 LED"),
        ("E", "Cable gland PG9 / PG7", "Nilon", "-", "1 / 3", f"{N_HEX} / {3 * N_HEX}", "lubang P1-P4"),
        ("F", "Magnet neodymium", "Ø10 x 3", "-", "2 per sisi", "nanti", "saat disambung"),
    ]
    yb = table(c, 258, 262, [("Kode", 9), ("Nama", 44), ("Bahan", 24), ("Tebal", 10), ("Jml / hex", 20), ("Total", 16), ("Ket.", 27)], rows)
    text(c, 258, 266, "Daftar bagian", 10, anchor="start", bold=True)
    notes(c, 258, yb - 8, [
        f"Tebal total = {fmt(T_SHEET)} + {N_RING} x {fmt(T_RING)} + {fmt(T_SHEET)} = {fmt(THICK)} mm.",
        f"Ruang air: hexagon {fmt(FLAT_IN)} mm x tinggi {fmt(N_RING * T_RING)} mm = +/-2,0 L (diisi +/-1,7 L).",
        "Semua lapisan direkatkan dengan silikon akuarium 100%.",
        "Hexagon dipasang tegak, sisi datar di atas; P1-P3 di atas garis air.",
        "Sudut dalam cincin R4 karena dipotong dengan pahat CNC bulat.",
        "Versi produk (konsep) setebal 42 mm; gambar ini versi prototipe.",
    ], title="Catatan")

def sheet2(c):
    frame(c, 2, TOTAL, "Part A (lembar depan) dan Part C (cincin rangka)", "1 : 2")
    text(c, 20, 278, "2. Part A - Lembar depan   dan   Part C - Cincin rangka", 12, anchor="start", bold=True)
    va = V(c, 110, 160, 0.5); pts = hexpts(FLAT)
    va.poly(pts, 0.7); va.center(0, 0, 182, 158)
    dim(c, va.pm(-R, 0), va.pm(R, 0), -85, fmt(2 * R)); dim(c, va.pm(-R / 2, -FLAT / 2), va.pm(-R / 2, FLAT / 2), 50, fmt(FLAT))
    dim(c, va.pm(*pts[2]), va.pm(*pts[1]), 8, fmt(R))
    notes(c, 30, 62, ["Part A - Lembar depan", f"Akrilik BENING tebal {fmt(T_SHEET)} mm", f"Jumlah: {N_HEX} buah (1 per hexagon)", "Semua sudut 120°, tajam (potong luar)"], lh=4.8)
    vc = V(c, 300, 160, 0.5)
    vc.poly(pts, 0.7); vc.poly(fillet_polyline(hexpts(FLAT_IN), R_IN_FILLET), 0.7); vc.center(0, 0, 182, 158)
    pin = hexpts(FLAT_IN)
    dim(c, vc.pm(-R, 0), vc.pm(R, 0), -85, fmt(2 * R)); dim(c, vc.pm(-R / 2, -FLAT / 2), vc.pm(-R / 2, FLAT / 2), 50, fmt(FLAT))
    dim(c, vc.pm(-R_IN, 0), vc.pm(R_IN, 0), -30, f"{fmt(2 * R_IN)} (dalam, sudut maya)")
    dim(c, vc.pm(-40, -FLAT_IN / 2), vc.pm(-40, FLAT_IN / 2), 0, f"{fmt(FLAT_IN)} (dalam)")
    leader(c, vc.pm(40, (FLAT + FLAT_IN) / 4), (vc.pm(0, 0)[0] + 45, vc.pm(0, 0)[1] + 100), f"dinding {fmt(WALL)}")
    leader(c, vc.pm(pin[1][0] - 3, pin[1][1] - 3), (vc.pm(0, 0)[0] + 50, vc.pm(0, 0)[1] + 92), f"R{fmt(R_IN_FILLET)} (6 sudut dalam)")
    notes(c, 225, 62, ["Part C - Cincin rangka", f"Akrilik BENING tebal {fmt(T_RING)} mm", f"Jumlah: {N_RING * N_HEX} buah ({N_RING} per hexagon, ditumpuk)", f"Dinding {fmt(WALL)} mm; sisi dalam {fmt(R_IN)} mm"], lh=4.8)

def sheet3(c):
    frame(c, 3, TOTAL, "Part B - Lembar belakang dengan lubang", "1 : 2")
    text(c, 20, 278, "3. Part B - Lembar belakang (dilihat dari belakang)", 12, anchor="start", bold=True)
    v = V(c, 120, 150, 0.5); pts = hexpts(FLAT)
    v.poly(pts, 0.7); v.center(0, 0, 182, 158)
    v.poly(fillet_polyline(hexpts(FLAT_IN), R_IN_FILLET), 0.25, ([2, 1.5], 0))
    for code, _, d, x, y, _ in HOLES:
        v.circle(x, y, d, 0.6); v.center(x, y, d * 0.9)
    dim(c, v.pm(-R, 0), v.pm(R, 0), -85, fmt(2 * R)); dim(c, v.pm(-R / 2, -FLAT / 2), v.pm(-R / 2, FLAT / 2), 50, fmt(FLAT))
    dim(c, v.pm(-40, 125), v.pm(0, 125), 14, "40"); dim(c, v.pm(0, 125), v.pm(40, 125), 14, "40")
    dim(c, v.pm(60, 0), v.pm(60, 125), -16, "125"); dim(c, v.pm(60, -125), v.pm(60, 0), -16, "125")
    dim(c, v.pm(-75, 125), v.pm(-75, FLAT / 2), 10, "25")
    leader(c, v.pm(0 + 5.4, 125 + 5.4), (v.pm(0, 0)[0] + 15, v.pm(0, 0)[1] + 94), "P1  Ø15,2")
    leader(c, v.pm(-40 - 4.4, 125 + 4.4), (v.pm(0, 0)[0] - 40, v.pm(0, 0)[1] + 94), "P2  Ø12,5", right=False)
    leader(c, v.pm(40 + 4.4, 125 + 4.4), (v.pm(0, 0)[0] + 60, v.pm(0, 0)[1] + 94), "P3  Ø12,5")
    leader(c, v.pm(4.4, -125 - 4.4), (v.pm(0, 0)[0] + 25, v.pm(0, 0)[1] - 80), "P4  Ø12,5")
    text(c, 120, 52, "Garis putus-putus = posisi sisi dalam cincin (bukan garis potong)", 7.5)
    rows = [(code, fn, fmt(d), fmt(x), fmt(y), fmt(x + R), fmt(y + FLAT / 2), isi) for code, fn, d, x, y, isi in HOLES]
    yb = table(c, 225, 262, [("Kode", 11), ("Fungsi", 34), ("Ø", 11), ("X tgh", 13), ("Y tgh", 13), ("X kiri", 14), ("Y bawah", 15), ("Isi lubang", 70)], rows)
    text(c, 225, 266, "Tabel lubang (mm)", 10, anchor="start", bold=True)
    notes(c, 225, yb - 8, [
        "X tgh / Y tgh  = dari titik tengah hexagon.",
        f"X kiri / Y bawah = dari pojok kiri bawah kotak batas ({fmt(2 * R)} x {fmt(FLAT)}).",
        f"Akrilik FROSTED tebal {fmt(T_SHEET)} mm, jumlah {N_HEX} buah.",
        "Sisi buram menghadap keluar (ke dinding) agar bagian dalam licin.",
        "PG7: ulir Ø12,5 mm, kabel/selang 3-6,5 mm. PG9: ulir Ø15,2 mm.",
        "Cocokkan dulu dengan cable gland asli; lebih aman lubang dibuat",
        "0,2 mm lebih kecil lalu diperbesar dengan amplas gulung.",
        "P1-P3 berada di atas garis air (y = +105); hanya P4 yang terendam.",
    ], title="Catatan")

def sheet4(c):
    frame(c, 4, TOTAL, "Potongan A-A dan detail lapisan", "1 : 2 / detail 2 : 1")
    text(c, 20, 278, "4. Potongan A-A (dipotong tegak lewat P1 dan P4)", 12, anchor="start", bold=True)
    v = V(c, 50, 140, 0.5)   # x = arah tebal (0 = depan), y = tinggi
    xs = [0, T_SHEET, T_SHEET + T_RING, T_SHEET + 2 * T_RING, T_SHEET + 3 * T_RING, THICK]
    def sect(view, step):
        # lembar depan & belakang (penuh), dinding cincin atas & bawah
        for x0, x1 in ((xs[0], xs[1]), (xs[4], xs[5])):
            for y0, y1 in ((-FLAT / 2, FLAT / 2),):
                a = view.pm(x0, y0); b = view.pm(x1, y1); hatch_rect(c, a[0], a[1], b[0], b[1], step)
        for k in range(1, 4):
            for y0, y1 in ((FLAT_IN / 2, FLAT / 2), (-FLAT / 2, -FLAT_IN / 2)):
                a = view.pm(xs[k], y0); b = view.pm(xs[k + 1], y1); hatch_rect(c, a[0], a[1], b[0], b[1], step)
    sect(v, 1.2)
    # lubang di lembar belakang (dipotong): kosongkan dengan kotak putih
    for code, _, d, x, y, _ in HOLES:
        if x == 0:
            a = v.pm(xs[4] - 0.3, y - d / 2); b = v.pm(THICK + 0.3, y + d / 2)
            c.setFillGray(1); c.rect(a[0] * mm, a[1] * mm, (b[0] - a[0]) * mm, (b[1] - a[1]) * mm, stroke=0, fill=1); c.setFillGray(0)
    v.line((xs[1], WATER_Y), (xs[4], WATER_Y), 0.4, ([3, 1.5], 0))
    dim(c, v.pm(THICK, -FLAT / 2), v.pm(THICK, FLAT / 2), -16, fmt(FLAT))
    dim(c, v.pm(0, -FLAT / 2), v.pm(THICK, -FLAT / 2), -8, fmt(THICK))
    text(c, 60, 52, "Potongan A-A  1 : 2", 8, bold=True)
    text(c, 46, 140, "depan", 7, ang=90); text(c, 75, 140, "belakang", 7, ang=90)
    # detail X (atas) 2:1
    dd = V(c, 125, 240 - 2.0 * 150, 2.0)
    def clip_view(view, y0, y1, step):
        for x0, x1 in ((xs[0], xs[1]), (xs[4], xs[5])):
            a = view.pm(x0, y0); b = view.pm(x1, y1); hatch_rect(c, a[0], a[1], b[0], b[1], step)
        for k in range(1, 4):
            lo, hi = (FLAT_IN / 2, FLAT / 2) if y1 > 0 else (-FLAT / 2, -FLAT_IN / 2)
            a = view.pm(xs[k], lo); b = view.pm(xs[k + 1], hi); hatch_rect(c, a[0], a[1], b[0], b[1], step)
    clip_view(dd, 95, FLAT / 2, 2.0)
    for code, _, dia, x, y, _ in HOLES:
        if code == "P1":
            a = dd.pm(xs[4] - 0.2, y - dia / 2); b = dd.pm(THICK + 0.2, y + dia / 2)
            c.setFillGray(1); c.rect(a[0] * mm, a[1] * mm, (b[0] - a[0]) * mm, (b[1] - a[1]) * mm, stroke=0, fill=1); c.setFillGray(0)
            c.setLineWidth(0.4); c.line(a[0] * mm, a[1] * mm, b[0] * mm, a[1] * mm); c.line(a[0] * mm, b[1] * mm, b[0] * mm, b[1] * mm)
            # cable gland (skematis)
            g0 = dd.pm(THICK, y - 12); g1 = dd.pm(THICK + 14, y + 12); c.setLineWidth(0.4); c.setDash([2, 1], 0)
            c.rect(g0[0] * mm, g0[1] * mm, (g1[0] - g0[0]) * mm, (g1[1] - g0[1]) * mm); c.setDash([], 0)
            text(c, g1[0] + 2, (g0[1] + g1[1]) / 2, "cable gland PG9", 7, anchor="start")
    dd.line((xs[1], WATER_Y), (xs[4], WATER_Y), 0.4, ([3, 1.5], 0)); text(c, *dd.pm(xs[1] + 1, WATER_Y + 2), "garis air (y = +105)", 7, anchor="start")
    led0 = dd.pm(xs[2], FLAT / 2); led1 = dd.pm(xs[3], FLAT / 2 + 2)
    c.setFillGray(0.35); c.rect(led0[0] * mm, led0[1] * mm, (led1[0] - led0[0]) * mm, (led1[1] - led0[1]) * mm, stroke=1, fill=1); c.setFillGray(0)
    leader(c, ((led0[0] + led1[0]) / 2, led1[1]), (dd.pm(THICK, 0)[0] + 8, led1[1] + 5), "strip LED (lebar 10)")
    top = FLAT / 2
    for k in range(5):
        dim(c, dd.pm(xs[k], top), dd.pm(xs[k + 1], top), 14 if k % 2 == 0 else 22, fmt(xs[k + 1] - xs[k]), 7.5)
    dim(c, dd.pm(0, top), dd.pm(THICK, top), 32, fmt(THICK))
    dim(c, dd.pm(0, FLAT_IN / 2), dd.pm(0, top), 8, fmt(WALL))
    dim(c, dd.pm(0, 125), dd.pm(0, top), 22, "25")
    dim(c, dd.pm(0, WATER_Y), dd.pm(0, top), 36, "45")
    text(c, 165, 112, "Detail X (bagian atas)  2 : 1", 8, bold=True)
    # detail Y (bawah) 2:1
    dy = V(c, 270, 120 + 2.0 * 150, 2.0)
    clip_view(dy, -FLAT / 2, -110, 2.0)
    for code, _, dia, x, y, _ in HOLES:
        if code == "P4":
            a = dy.pm(xs[4] - 0.2, y - dia / 2); b = dy.pm(THICK + 0.2, y + dia / 2)
            c.setFillGray(1); c.rect(a[0] * mm, a[1] * mm, (b[0] - a[0]) * mm, (b[1] - a[1]) * mm, stroke=0, fill=1); c.setFillGray(0)
            c.setLineWidth(0.4); c.line(a[0] * mm, a[1] * mm, b[0] * mm, a[1] * mm); c.line(a[0] * mm, b[1] * mm, b[0] * mm, b[1] * mm)
            g0 = dy.pm(THICK, y - 10); g1 = dy.pm(THICK + 12, y + 10); c.setLineWidth(0.4); c.setDash([2, 1], 0)
            c.rect(g0[0] * mm, g0[1] * mm, (g1[0] - g0[0]) * mm, (g1[1] - g0[1]) * mm); c.setDash([], 0)
            text(c, g0[0], g0[1] - 4, "gland PG7 + selang kuras", 7, anchor="start")
    stone = dy.pm(THICK / 2, -FLAT_IN / 2 + 6); c.setLineWidth(0.4); c.setDash([1.5, 1], 0); c.circle(stone[0] * mm, stone[1] * mm, 2 * 10 * mm / 2 * 0.6); c.setDash([], 0)
    leader(c, (stone[0], stone[1] + 6), (stone[0] + 4, 210), "batu aerator")
    bot = -FLAT / 2
    dim(c, dy.pm(0, bot), dy.pm(0, -FLAT_IN / 2), 8, fmt(WALL))
    dim(c, dy.pm(THICK, bot), dy.pm(THICK, -125), -34, "25")
    text(c, 300, 100, "Detail Y (bagian bawah)  2 : 1", 8, bold=True)

def sheet5(c, files):
    frame(c, 5, TOTAL, "Tata letak potong CNC dan petunjuk operator", "1 : 10")
    text(c, 20, 278, "5. Tata letak potong (nesting) dan petunjuk untuk operator CNC", 12, anchor="start", bold=True)
    x = 25
    for key, n, w, h, pos, _ in files:
        p = PARTS[key]; v = V(c, x, 270 - h * 0.1 - 18, 0.1)
        for cx, cy in pos:
            for g in p["fn"](cx, cy):
                if g[0] == "poly": v.poly(g[1], 0.3)
                elif g[0] == "fpoly": v.poly(fillet_polyline(g[1], g[2], 3), 0.3)
                elif g[0] == "circle": v.circle(g[1], g[2], max(g[3], 8), 0.25)
        dim(c, v.pm(0, 0), v.pm(w, 0), -6, fmt(round(w)), 7); dim(c, v.pm(0, 0), v.pm(0, h), 6, fmt(round(h)), 7)
        text(c, x, 262, f"Part {key}: {p['name']} x{n}", 9, anchor="start", bold=True)
        text(c, x, 257, f"{p['mat']} {fmt(p['t'])} mm", 8, anchor="start")
        x += max(w * 0.1, 60) + 28
    yb = notes(c, 25, 180, [
        "1.  File DXF dan SVG berskala 1 : 1 dalam milimeter. Garis = ukuran JADI, bukan jalur pahat.",
        "2.  Layer POTONG_LUAR (merah): kompensasi pahat di LUAR garis (outside profile).",
        "     Layer POTONG_DALAM (biru): lubang P1-P4 dan sisi dalam cincin, kompensasi di DALAM garis (inside).",
        "     Layer KETERANGAN_JANGAN_DIPOTONG: tulisan saja, jangan dibuat jalur pahat.",
        "3.  Pahat: end mill 1 flute (O-flute) khusus akrilik, Ø3-6 mm. Sudut dalam cincin R4 => pahat maksimal Ø8 mm.",
        "4.  Urutan: potong bagian dalam dulu (lubang, sisi dalam cincin), baru sisi luar.",
        "5.  Tahan benda kerja dengan meja vakum atau tab/jembatan kecil, lalu rapikan bekas tab dengan kikir.",
        "6.  Biarkan kertas/plastik pelindung akrilik menempel selama dipotong; lepas saat akan dilem.",
        "7.  Kecepatan dan kedalaman per pass mengikuti setelan operator untuk akrilik (hindari panas berlebih agar tidak meleleh).",
        f"8.  Celah antar-part = {fmt(GAP)} mm. Ukuran bahan minimal = area tata letak + 20 mm tiap sisi (lihat tabel di bawah).",
        "9.  Cek ukuran setelah potong: sisi datar luar 300 +/-0,3; lubang P1 Ø15,2 dan P2-P4 Ø12,5.",
        "10. File CDR: buka DXF atau SVG di CorelDRAW (File > Import, satuan mm, skala 1 : 1), lalu File > Save As > .cdr.",
    ], size=8, lh=5.2, title="Petunjuk operator CNC")
    rows = [(f"{PARTS[k]['mat']} {fmt(PARTS[k]['t'])} mm", f"Part {k} x{n}", f"{fmt(round(w + 40))} x {fmt(round(h + 40))} mm", fn + ".dxf / .svg") for k, n, w, h, _, fn in files]
    text(c, 25, yb - 4, f"Bahan dan file untuk {N_HEX} hexagon (folder output/cnc)", 9, anchor="start", bold=True)
    table(c, 25, yb - 8, [("Bahan", 50), ("Part", 22), ("Bahan minimal", 34), ("File", 92)], rows)

def build_pdf(files):
    c = canvas.Canvas(PDF, pagesize=landscape(A3)); c.setTitle("Algora - Gambar Teknik Hexagon"); c.setAuthor("Tim Algora")
    for f in (sheet1, sheet2, sheet3, sheet4):
        f(c); c.showPage()
    sheet5(c, files); c.showPage(); c.save()

def export_dims():
    import json
    json.dump(dict(FLAT=FLAT, FLAT_IN=FLAT_IN, WALL=WALL, R_IN_FILLET=R_IN_FILLET, T_SHEET=T_SHEET, T_RING=T_RING, N_RING=N_RING,
                   THICK=THICK, WATER_Y=WATER_Y, HOLES=[dict(code=h[0], fn=h[1], d=h[2], x=h[3], y=h[4], isi=h[5]) for h in HOLES]),
              open(os.path.join(OUT, "dims.json"), "w"), indent=1)

if __name__ == "__main__":
    export_dims()
    files = export_cut_files()
    build_pdf(files)
    for key, n, w, h, _, _ in files:
        print(f"{key}: {n} buah, area nesting {w:.1f} x {h:.1f} mm")
    print("PDF:", PDF)
