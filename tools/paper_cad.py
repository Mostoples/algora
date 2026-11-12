"""Detailed dimensioned design drawing (DXF) -> LibreCAD dxf2pdf -> PNG for the paper.
python tools/paper_cad.py -> output/paper/Algora_Detail_Design.dxf / .pdf, fig_cad.png"""
import json, math, os, subprocess
import ezdxf
from ezdxf.enums import TextEntityAlignment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "output", "paper")
D = json.load(open(os.path.join(ROOT, "output", "cnc", "dims.json")))
FLAT, FLAT_IN, RF, TS, TR, TH, WY = D["FLAT"], D["FLAT_IN"], D["R_IN_FILLET"], D["T_SHEET"], D["T_RING"], D["THICK"], D["WATER_Y"]
R, R_IN = FLAT / math.sqrt(3), FLAT_IN / math.sqrt(3)
LC = "C:/Program Files/LibreCAD/librecad.exe"

doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM
for name, rgb, lt, lw in (("OUTLINE", (0, 0, 0), "CONTINUOUS", 50), ("HIDDEN", (90, 90, 90), "DASHED", 25),
                          ("CENTER", (110, 110, 110), "CENTER", 18), ("DIM", (0, 70, 200), "CONTINUOUS", 18),
                          ("TEXT", (0, 0, 0), "CONTINUOUS", 25), ("WATER", (0, 140, 60), "DASHED", 25)):
    ly = doc.layers.add(name, linetype=lt); ly.rgb = rgb; ly.dxf.lineweight = lw
msp = doc.modelspace()
OV = dict(dimtxt=7, dimasz=5, dimdec=1, dimexe=3, dimexo=3, dimgap=1.5, dimdsep=46, dimtad=1, dimclrd=256, dimclre=256, dimclrt=256)

def hexpts(flat, cx=0, cy=0):
    r = flat / math.sqrt(3)
    return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(0, 360, 60)]

def fillet(pts, r):
    out = []
    for i in range(len(pts)):
        V, A, B = pts[i], pts[i - 1], pts[(i + 1) % len(pts)]
        u1 = ((A[0] - V[0]), (A[1] - V[1])); l1 = math.hypot(*u1); u1 = (u1[0] / l1, u1[1] / l1)
        u2 = ((B[0] - V[0]), (B[1] - V[1])); l2 = math.hypot(*u2); u2 = (u2[0] / l2, u2[1] / l2)
        t = r / math.tan(math.radians(60)); out += [(V[0] + u1[0] * t, V[1] + u1[1] * t, 0, 0, math.tan(math.radians(15))), (V[0] + u2[0] * t, V[1] + u2[1] * t, 0, 0, 0)]
    return out

def text(s, x, y, h=7, layer="TEXT", align=TextEntityAlignment.MIDDLE_CENTER):
    msp.add_text(s, height=h, dxfattribs={"layer": layer}).set_placement((x, y), align=align)

def lin(p1, p2, base, angle=0):
    v = abs(p2[0] - p1[0]) if angle == 0 else abs(p2[1] - p1[1])
    lab = f"{v:.1f}".rstrip("0").rstrip(".")
    d = msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=angle, text=lab, override=OV, dxfattribs={"layer": "DIM"}); d.render()
    for e in d.dimension.explode():
        e.dxf.layer = "DIM"; e.dxf.color = 256

def centerlines(cx, cy, sx, sy):
    msp.add_line((cx - sx, cy), (cx + sx, cy), dxfattribs={"layer": "CENTER"}); msp.add_line((cx, cy - sy), (cx, cy + sy), dxfattribs={"layer": "CENTER"})

# --- view 1: front view, assembled (inner ring outline hidden) ---------------
cx = 0
msp.add_lwpolyline(hexpts(FLAT, cx), close=True, dxfattribs={"layer": "OUTLINE"})
msp.add_lwpolyline([(x + cx, y, s, e, b) for x, y, s, e, b in fillet(hexpts(FLAT_IN), RF)], format="xyseb", close=True, dxfattribs={"layer": "HIDDEN"})
msp.add_line((cx - R_IN + 25, WY), (cx + R_IN - 25 - (R_IN - 0.866 * 0 - R_IN), WY), dxfattribs={"layer": "WATER"})
centerlines(cx, 0, R + 15, FLAT / 2 + 15)
lin((cx - R, 0), (cx + R, 0), (0, -FLAT / 2 - 35))
lin((cx - R / 2, -FLAT / 2), (cx - R / 2, FLAT / 2), (cx - R - 30, 0), angle=90)
lin((cx - R / 2, FLAT / 2), (cx + R / 2, FLAT / 2), (0, FLAT / 2 + 25))
lin((cx, FLAT_IN / 2), (cx, FLAT / 2), (cx + 60, 0), angle=90)
text("water line +105", cx - 70, WY + 6, 5, "WATER")
text("FRONT VIEW (ASSEMBLED)", cx, -FLAT / 2 - 75, 9)
# --- view 2: back sheet B with holes -------------------------------------------
cx = 450
msp.add_lwpolyline(hexpts(FLAT, cx), close=True, dxfattribs={"layer": "OUTLINE"})
centerlines(cx, 0, R + 15, FLAT / 2 + 15)
for h in D["HOLES"]:
    msp.add_circle((cx + h["x"], h["y"]), h["d"] / 2, dxfattribs={"layer": "OUTLINE"})
    centerlines(cx + h["x"], h["y"], h["d"] * 0.8, h["d"] * 0.8)
    text(f"{h['code']}  D{h['d']:.1f}", cx + h["x"] + (0 if h["x"] == 0 else (28 if h["x"] > 0 else -28)), h["y"] + (16 if h["y"] > 0 else -16), 6)
lin((cx - 40, 125), (cx, 125), (0, 155))
lin((cx, 125), (cx + 40, 125), (0, 155))
lin((cx, 0), (cx, 125), (cx + 100, 0), angle=90)
lin((cx, -125), (cx, 0), (cx + 100, 0), angle=90)
lin((cx - 60, 125), (cx - 60, FLAT / 2), (cx - 120, 0), angle=90)
text("BACK SHEET B (5 mm frosted)", cx, -FLAT / 2 - 75, 9)
# --- view 3: section A-A ------------------------------------------------------
x0 = 760; S = 1.0
ys = [0, TS, TS + TR, TS + 2 * TR, TS + 3 * TR, TH]
for x in ys:
    msp.add_line((x0 + x, -FLAT / 2), (x0 + x, FLAT / 2), dxfattribs={"layer": "OUTLINE"})
for y in (-FLAT / 2, FLAT / 2):
    msp.add_line((x0, y), (x0 + TH, y), dxfattribs={"layer": "OUTLINE"})
for y in (-FLAT_IN / 2, FLAT_IN / 2):
    msp.add_line((x0 + TS, y), (x0 + TH - TS, y), dxfattribs={"layer": "OUTLINE"})
msp.add_line((x0 + TS, WY), (x0 + TH - TS, WY), dxfattribs={"layer": "WATER"})
for k in range(5):
    lin((x0 + ys[k], FLAT / 2), (x0 + ys[k + 1], FLAT / 2), (0, FLAT / 2 + (18 if k % 2 == 0 else 34)))
lin((x0, FLAT / 2), (x0 + TH, FLAT / 2), (0, FLAT / 2 + 55))
lin((x0 + TH, -FLAT / 2), (x0 + TH, FLAT / 2), (x0 + TH + 30, 0), angle=90)
lin((x0, FLAT_IN / 2), (x0, FLAT / 2), (x0 - 25, 0), angle=90)
lin((x0, WY), (x0, FLAT / 2), (x0 - 55, 0), angle=90)
text("front A", x0 - 4, -FLAT / 2 - 14, 5, align=TextEntityAlignment.MIDDLE_RIGHT); text("back B", x0 + TH + 4, -FLAT / 2 - 14, 5, align=TextEntityAlignment.MIDDLE_LEFT)
text("C1-C3", x0 + 20, -FLAT / 2 - 26, 5)
text("culture 30 mm", x0 + TH + 6, 0, 5, align=TextEntityAlignment.MIDDLE_LEFT)
text("SECTION A-A", x0 + 20, -FLAT / 2 - 75, 9)
text("ALGORA module - detailed design, all dimensions in mm (drawn as DXF, plotted with LibreCAD)", 390, -FLAT / 2 - 110, 8)

dxf = os.path.join(P, "Algora_Detail_Design.dxf"); doc.saveas(dxf)
pdf = os.path.join(P, "Algora_Detail_Design.pdf")
subprocess.run([LC, "dxf2pdf", "-a", "-p", "297x210", "-f", "8,8,8,8", "-o", pdf, dxf], capture_output=True)
import pypdfium2 as Pd
from PIL import Image, ImageOps
im = Pd.PdfDocument(pdf)[0].render(scale=4).to_pil().convert("RGB")
bbox = ImageOps.invert(im).getbbox(); im = im.crop((bbox[0] - 20, bbox[1] - 20, bbox[2] + 20, bbox[3] + 20))
im.save(os.path.join(P, "fig_cad.png")); print("ok", im.size)
