"""Video gambar teknik 3D hexagon Algora (prototipe CNC) untuk siswa SMP.
blender -b -P blender/tech_video.py -- [start end]        (ALG_ANCHORS=1 -> hanya tulis anchors.json, tanpa render)
Frames -> output/frames/tech/f_0000.png ; anchors -> output/frames/tech/anchors.json
Semua ukuran dibaca dari output/cnc/dims.json (ditulis cnc/make_cnc.py)."""
import sys, os, math, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from lib import _set
import bmesh
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

D = json.load(open(os.path.join(ROOT, "output", "cnc", "dims.json")))
FPS, DUR = 30, 75.0
NF = int(DUR * FPS)
RES = (int(os.environ.get("ALG_W", "1920")), int(os.environ.get("ALG_H", "1080")))
SPP = int(os.environ.get("ALG_SPP", "32"))
OUT = os.path.join(ROOT, "output", "frames", "tech")
U = 0.001
FLAT, FLAT_IN, RF = D["FLAT"], D["FLAT_IN"], D["R_IN_FILLET"]
R, R_IN = FLAT / math.sqrt(3), FLAT_IN / math.sqrt(3)
TS, TR, TH, WY = D["T_SHEET"], D["T_RING"], D["THICK"], D["WATER_Y"]
Y0 = -TH / 2
LAY = [("A", Y0, Y0 + TS), ("C1", Y0 + TS, Y0 + TS + TR), ("C2", Y0 + TS + TR, Y0 + TS + 2 * TR),
       ("C3", Y0 + TS + 2 * TR, Y0 + TS + 3 * TR), ("B", TH / 2 - TS, TH / 2)]
EXPL = dict(A=-160, C1=-80, C2=0, C3=80, B=160)   # mm geser saat dibongkar

# ------------------------------------------------------------------ waktu --
def ss(a, b, t):
    t = max(0.0, min(1.0, (t - a) / (b - a)))
    return t * t * (3 - 2 * t)

# t, az, el, jarak (m), target (mm), lensa
KEYS = [
    (0.0, 28, 12, 1.30, (0, 0, 0), 50), (5.0, 22, 10, 1.12, (0, 0, 0), 50),
    (14.0, 22, 10, 1.12, (0, 0, 0), 50), (15.8, 0, 0, 1.22, (0, 0, -8), 50), (19.5, 0, 0, 1.22, (0, 0, -8), 50),
    (22.0, 38, 18, 1.75, (0, 0, 0), 50), (40.0, 38, 18, 1.75, (0, 0, 0), 50),
    (42.5, 0, 0, 0.95, (0, 0, 0), 50), (44.0, 0, 0, 0.075, (R_IN - 6, -20, 3), 50), (49.0, 0, 0, 0.075, (R_IN - 6, -20, 3), 50),
    (51.0, 180, 8, 0.42, (0, 20, 100), 50), (54.0, 180, 8, 0.42, (0, 20, 100), 50),
    (55.5, 180, 8, 0.30, (0, 20, -105), 50), (57.0, 180, 8, 0.30, (0, 20, -105), 50),
    (59.0, 68, 34, 0.15, (R / 2 - 4, 0, 147), 50), (64.0, 68, 34, 0.15, (R / 2 - 4, 0, 147), 50),
    (69.0, 30, 12, 1.25, (0, 0, 0), 50), (75.0, 24, 10, 1.12, (0, 0, 0), 50),
]

def cam_at(t):
    for i in range(len(KEYS) - 1):
        a, b = KEYS[i], KEYS[i + 1]
        if a[0] <= t <= b[0]:
            u = ss(a[0], b[0], t)
            return [a[k] + (b[k] - a[k]) * u if k != 4 else tuple(a[4][j] + (b[4][j] - a[4][j]) * u for j in range(3)) for k in range(6)]
    return list(KEYS[-1])

def explode(t): return ss(22.5, 25.5, t) * (1 - ss(40.0, 42.5, t))
def spin(t): return 360 * ss(5, 14, t) + 360 * ss(30, 40, t)
def glow(t): return ss(63, 67, t)

# --------------------------------------------------------------- geometri --
def hexpts(flat):
    r = flat / math.sqrt(3)
    return [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in range(0, 360, 60)]

def fillet_pts(pts, r, seg=8):
    res, n = [], len(pts)
    for i in range(n):
        V, P, N = Vector(pts[i]), Vector(pts[i - 1]), Vector(pts[(i + 1) % n])
        u1, u2 = (P - V).normalized(), (N - V).normalized()
        th = math.acos(max(-1, min(1, u1.dot(u2))))
        t, dd = r / math.tan(th / 2), r / math.sin(th / 2)
        C = V + (u1 + u2).normalized() * dd
        T1, T2 = V + u1 * t, V + u2 * t
        a1, a2 = math.atan2(T1.y - C.y, T1.x - C.x), math.atan2(T2.y - C.y, T2.x - C.x)
        while a2 < a1: a2 += 2 * math.pi
        for k in range(seg + 1):
            a = a1 + (a2 - a1) * k / seg
            res.append((C.x + r * math.cos(a), C.y + r * math.sin(a)))
    return res

def circle(r, n=40, cx=0, cz=0):
    return [(cx + r * math.cos(2 * math.pi * k / n), cz + r * math.sin(2 * math.pi * k / n)) for k in range(n)]

def clip_below(pts, zmax):
    out = []
    for i in range(len(pts)):
        P, Q = pts[i - 1], pts[i]
        pin, qin = P[1] <= zmax, Q[1] <= zmax
        if qin:
            if not pin: out.append((P[0] + (Q[0] - P[0]) * (zmax - P[1]) / (Q[1] - P[1]), zmax))
            out.append(Q)
        elif pin:
            out.append((P[0] + (Q[0] - P[0]) * (zmax - P[1]) / (Q[1] - P[1]), zmax))
    return out

def prism(name, pts, y0, y1, m, parent=None):
    """Poligon (x, z) mm diekstrusi sepanjang Y dari y0 ke y1 (mm)."""
    bm = bmesh.new()
    b = [bm.verts.new((x * U, y0 * U, z * U)) for x, z in pts]
    t = [bm.verts.new((x * U, y1 * U, z * U)) for x, z in pts]
    bm.faces.new(b); bm.faces.new(t[::-1])
    n = len(pts)
    for i in range(n):
        bm.faces.new((b[i], t[i], t[(i + 1) % n], b[(i + 1) % n]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mk(bm, name, m, parent)

def vcyl(name, r, z0, z1, x, y, m, parent=None, seg=24):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r * U, radius2=r * U, depth=(z1 - z0) * U)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(x * U, y * U, (z0 + z1) / 2 * U))
    return mk(bm, name, m, parent, smooth=True)

def cut(ob, cutter):
    md = ob.modifiers.new("cut", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = cutter
    try: md.solver = "EXACT"
    except Exception: pass
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    ob.modifiers.remove(md); old = ob.data; ob.data = me; bpy.data.meshes.remove(old)
    bpy.data.objects.remove(cutter)

def tube(name, pts, r, m, parent=None):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = r * U; cu.bevel_resolution = 4
    sp = cu.splines.new("BEZIER"); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = Vector(p) * U; bp.handle_left_type = bp.handle_right_type = "AUTO"
    ob = bpy.data.objects.new(name, cu); link(ob); cu.materials.append(m)
    if parent: ob.parent = parent
    return ob

def anchor(name, p_mm, parent):
    return empty("an_" + name, tuple(v * U for v in p_mm), parent=parent)

# -------------------------------------------------------------- material --
def acrylic(name, tint, k_diff, gloss):
    m = bpy.data.materials.new(name); nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL": nt.nodes.remove(n)
    out = nt.nodes.get("Material Output")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); tr.inputs[0].default_value = lin(tint)
    df = nt.nodes.new("ShaderNodeBsdfDiffuse"); df.inputs[0].default_value = lin(tint)
    m1 = nt.nodes.new("ShaderNodeMixShader"); m1.inputs[0].default_value = k_diff
    nt.links.new(tr.outputs[0], m1.inputs[1]); nt.links.new(df.outputs[0], m1.inputs[2])
    gl = nt.nodes.new("ShaderNodeBsdfGlossy"); gl.inputs["Roughness"].default_value = gloss
    fr = nt.nodes.new("ShaderNodeFresnel"); fr.inputs["IOR"].default_value = 1.49
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    nt.links.new(geo.outputs["Backfacing"], inv.inputs[1])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    nt.links.new(fr.outputs[0], mul.inputs[0]); nt.links.new(inv.outputs[0], mul.inputs[1])
    m2 = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mul.outputs[0], m2.inputs[0]); nt.links.new(m1.outputs[0], m2.inputs[1]); nt.links.new(gl.outputs[0], m2.inputs[2])
    nt.links.new(m2.outputs[0], out.inputs["Surface"])
    return m

# ------------------------------------------------------------------ build --
def build():
    sc = setup(RES, SPP, exposure=0.0)
    world_color("#DCE5F2", 0.45)
    area("key", (-0.9, -1.3, 1.3), 70, 1.4); area("fill", (1.4, -0.7, 0.5), 30, 1.6)
    area("rim", (0.2, 1.5, 1.1), 60, 1.2); area("top", (0, 0, 1.6), 20, 2.0)
    M_A = acrylic("acr_A", "#E2F1FC", 0.04, 0.02); M_C = acrylic("acr_C", "#3AA8D8", 0.45, 0.03)
    M_B = acrylic("acr_B", "#B9B3E3", 0.6, 0.25)
    M_W = algae_thin("water", tint="#2FAE4E", glow=0.15, density=0.7)
    M_LED = mat("led", "#FFFFFF", rough=0.3, emit="#FFD9A0", emit_str=0.0)
    M_PCB = mat("pcb", "#F4F4F4", rough=0.5); M_NY = mat("nylon", "#2B2F38", rough=0.45)
    M_ST = mat("steel", "#C9CDD3", rough=0.25, metal=1.0); M_SI = mat("silicone", "#EEF1F4", rough=0.3, sss=0.2)
    M_CB = mat("cable", "#1B1D22", rough=0.5); M_STONE = mat("stone", "#8C8F96", rough=0.95)
    M_BUB = thin_glass("bubble", tint="#FFFFFF", gloss=0.02)
    M_PED = mat("ped", "#F3F6FA", rough=0.65); M_FL = mat("floor", "#C9D4E3", rough=0.8)
    # alas
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=96, radius1=0.33, radius2=0.33, depth=0.02)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, -FLAT / 2 * U - 0.0102)); mk(bm, "pedestal", M_PED, smooth=True)
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=6)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, -FLAT / 2 * U - 0.0203)); mk(bm, "floor", M_FL)

    root = empty("root"); grp = {}
    for key, y0, y1 in LAY:
        g = empty("g_" + key, parent=root); grp[key] = g
        if key == "A":
            ob = prism("A", hexpts(FLAT), y0, y1, M_A)
        elif key == "B":
            ob = prism("B", hexpts(FLAT), y0, y1, M_B)
            for h in D["HOLES"]:
                cut(ob, prism("cut_" + h["code"], circle(h["d"] / 2, 40, h["x"], h["y"]), y0 - 2, y1 + 2, None))
        else:
            ob = prism(key, hexpts(FLAT), y0, y1, M_C)
            cut(ob, prism("cut_" + key, fillet_pts(hexpts(FLAT_IN), RF, 8), y0 - 2, y1 + 2, None))
        ob.parent = g
        bevel(ob, 0.0005, 2, 40)
        yc = (y0 + y1) / 2
        anchor("tag_" + key, (0, yc, FLAT / 2 + 14), g)
        anchor("lab_" + key, (R, yc, 0), g)
    gA, gC1, gC2, gB = grp["A"], grp["C1"], grp["C2"], grp["B"]
    yA = LAY[0][1]; yC1 = LAY[1][1]; yB0, yB1 = LAY[4][1], LAY[4][2]
    # strip LED di sisi luar cincin tengah
    yc2a, yc2b = LAY[2][1], LAY[2][2]
    pts = hexpts(FLAT)
    for i in range(6):
        p, q = Vector(pts[i]), Vector(pts[(i + 1) % 6]); mid = (p + q) / 2; dvec = (q - p).normalized(); nvec = mid.normalized()
        L = (q - p).length - 6
        a, b = mid - dvec * L / 2, mid + dvec * L / 2
        o0, o1 = nvec * 0.2, nvec * 1.8
        prism(f"strip{i}", [(a + o0).to_tuple(), (b + o0).to_tuple(), (b + o1).to_tuple(), (a + o1).to_tuple()], yc2a + 0.2, yc2b - 0.2, M_PCB, gC2)
        for k in range(5):
            c_ = a + dvec * L * (k + 0.5) / 5 + nvec * 1.8
            sq = [(c_ + dvec * s1 * 2.5 + nvec * s2).to_tuple() for s1, s2 in ((-1, 0), (1, 0), (1, 1.2), (-1, 1.2))]
            prism(f"led{i}_{k}", sq, -2.5 + (yc2a + yc2b) / 2, 2.5 + (yc2a + yc2b) / 2, M_LED, gC2)
    anchor("led", (0, (yc2a + yc2b) / 2, FLAT / 2 + 2), gC2)
    # isi: air alga, batu aerator, selang, sensor suhu, gelembung (diam di tengah saat dibongkar)
    gW = empty("g_W", parent=root)
    prism("water", clip_below(fillet_pts(hexpts(FLAT_IN), RF, 8), WY), LAY[1][1] + 0.3, LAY[3][2] - 0.3, M_W, gW)
    anchor("water", (-40, 0, -30), gW); anchor("waterline", (-90, LAY[1][1], WY), gW)
    sphere(9 * U, M_STONE, loc=(0, 2 * U, (-FLAT_IN / 2 + 10) * U), name="airstone", parent=gW)
    tube("airtube", [(-40, 12, 125), (-40, 8, 100), (-30, 6, -60), (-6, 3, -118), (0, 2, -122)], 2.5, M_SI, gW)
    tube("cable_in", [(40, 12, 125), (40, 8, 110), (40, 6, 95)], 2.2, M_CB, gW)
    vcyl("probe", 3, 60, 95, 40, 6, M_ST, gW)
    bub = []
    for i in range(26):
        r = 1.4 + (i * 37 % 10) / 6.0
        bub.append((sphere(r * U, M_BUB, loc=(0, 0, 0), name=f"bub{i}", parent=gW), i))
    # cable gland di lembar belakang + selang/kabel keluar
    for h in D["HOLES"]:
        big = h["d"] > 14
        nut, body, cap = (12.5, 10.5, 8) if big else (10.5, 8.5, 6.5)
        prism(f"gnut_{h['code']}", [(h["x"] + nut * math.cos(math.radians(a + 30)), h["y"] + nut * math.sin(math.radians(a + 30))) for a in range(0, 360, 60)], yB1, yB1 + 4, M_NY, gB)
        prism(f"gbody_{h['code']}", circle(body, 32, h["x"], h["y"]), yB1 + 4, yB1 + 12, M_NY, gB)
        prism(f"gcap_{h['code']}", circle(cap, 32, h["x"], h["y"]), yB1 + 12, yB1 + 18, M_NY, gB)
        prism(f"glock_{h['code']}", [(h["x"] + nut * math.cos(math.radians(a + 30)), h["y"] + nut * math.sin(math.radians(a + 30))) for a in range(0, 360, 60)], yB0 - 3, yB0, M_NY, gB)
        anchor("hole_" + h["code"], (h["x"], yB1 + 18, h["y"]), gB)
    tube("airtube_out", [(-40, 37, 125), (-40, 52, 125), (-40, 66, 125)], 2.5, M_SI, gB)
    tube("cable_out", [(40, 37, 125), (40, 52, 125), (40, 66, 125)], 2.2, M_CB, gB)
    tube("drain_out", [(0, 37, -125), (0, 52, -125), (0, 66, -125)], 3.0, M_SI, gB)
    # anchor ukuran
    for nm, p in dict(d_l=(-R, yA, 0), d_r=(R, yA, 0), d_tl=(-R / 2, yA, FLAT / 2), d_tr=(R / 2, yA, FLAT / 2),
                      d_bl=(-R / 2, yA, -FLAT / 2), d_br=(R / 2, yA, -FLAT / 2)).items():
        anchor(nm, p, gA)
    anchor("r4", (R_IN - (RF / math.sin(math.radians(60)) - RF), yC1, 0), gC1)
    pin = Vector((R_IN, 0)) + 0.07 * (Vector((R_IN / 2, FLAT_IN / 2)) - Vector((R_IN, 0)))
    pout = pin + Vector((math.cos(math.radians(30)), math.sin(math.radians(30)))) * D["WALL"]
    anchor("w_in", (pin.x, yC1, pin.y), gC1); anchor("w_out", (pout.x, yC1, pout.y), gC1)
    for k, y in enumerate([LAY[0][1]] + [l[2] for l in LAY]):
        anchor(f"L{k}", (R / 2, y, FLAT / 2), root)
    cam = camera((0, -1.2, 0), (0, 0, 0), lens=50)
    return dict(sc=sc, cam=cam, root=root, grp=grp, gW=gW, bub=bub, M_LED=M_LED, M_W=M_W)

def update(d, f):
    t = f / FPS
    e = explode(t)
    for key, _, _ in LAY:
        d["grp"][key].location.y = EXPL[key] * U * e
    d["root"].rotation_euler.z = math.radians(spin(t))
    _, az, el, dist, tgt, lens = cam_at(t)
    tg = Vector(tgt) * U; az, el = math.radians(az), math.radians(el)
    d["cam"].location = tg + Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))) * dist
    look_at(d["cam"], tg); d["cam"].data.lens = lens
    g = glow(t)
    _set(d["M_LED"].node_tree.nodes.get("Principled BSDF"), "Emission Strength", 0.3 + 45 * g)
    em = d["M_W"].node_tree.nodes.get("em")
    if em: em.inputs[1].default_value = 0.12 + 2.2 * g
    zlo, zhi = -FLAT_IN / 2 + 14, WY - 4
    for ob, i in d["bub"]:
        ph = (i * 0.6180339) % 1.0
        u = (t * 0.22 + ph) % 1.0
        z = zlo + (zhi - zlo) * u
        x = math.sin(2 * math.pi * (t * 0.8 + ph)) * 4 + (ph - 0.5) * 50 * u
        y = ((i * 0.381) % 1.0 - 0.5) * 18
        ob.location = (x * U, y * U, z * U)

if __name__ == "__main__":
    A = args()
    f0 = int(A[0]) if len(A) > 0 else 0
    f1 = int(A[1]) if len(A) > 1 else NF - 1
    step = int(os.environ.get("ALG_STEP", "1"))
    only_anchors = os.environ.get("ALG_ANCHORS") == "1"
    out = os.environ.get("ALG_OUT") or OUT; os.makedirs(out, exist_ok=True)
    reset()
    d = build()
    sc = d["sc"]; sc.render.use_persistent_data = True
    ans = [o for o in bpy.data.objects if o.name.startswith("an_")]
    anchors = {}
    frames = [int(x) for x in os.environ["ALG_FRAMES"].split(",")] if os.environ.get("ALG_FRAMES") else range(f0, f1 + 1, step)
    for f in frames:
        update(d, f)
        bpy.context.view_layer.update()
        if only_anchors:
            anchors[str(f)] = {o.name[3:]: [round(v, 5) for v in world_to_camera_view(sc, d["cam"], o.matrix_world.translation)] for o in ans}
            continue
        path = os.path.join(out, f"f_{f:04d}.png")
        if os.path.exists(path):
            continue
        sc.render.filepath = path
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        print("FRAME tech", f, "%.1fs" % (time.time() - t0), flush=True)
    if only_anchors:
        json.dump(anchors, open(os.path.join(out, "anchors.json"), "w"))
        print("ANCHORS", len(anchors))
