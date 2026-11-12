"""ALGORA app assets (transparent PNG, Standard view = exact brand colours).
blender -b --factory-startup -P blender/assets.py -- <out_dir> [names...]"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

A = args()
OUT = os.path.abspath(A[0] if A else os.path.join(ROOT, "app", "assets", "img"))
ONLY = set(A[1:])
os.makedirs(OUT, exist_ok=True)
REG = {}
def asset(name, res=(512, 512), samples=96):
    def deco(fn):
        REG[name] = (fn, res, samples); return fn
    return deco

def studio(res, samples):
    reset()
    setup(res, samples, exposure=-0.2, look=None, transparent=True)
    w = world_color("#EEF3FA", 0.9)
    area("key", (4.5, 1.5, 4), 420, 3.0)
    area("rim", (-4, 3, 2.2), 260, 3, "#BFD8FF")
    area("fill", (-3, -4, 0.3), 90, 3)

def frame(objs_root=None, az=35, el=28, pad=1.18, lens=50):
    """Orthographic camera fitted to all visible mesh bounds."""
    bpy.context.view_layer.update()
    pts = []
    for o in bpy.data.objects:
        if o.type == "MESH" and not o.hide_render:
            pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    ctr = sum(pts, Vector()) / len(pts)
    d = Vector((math.cos(math.radians(el)) * math.sin(math.radians(az)), -math.cos(math.radians(el)) * math.cos(math.radians(az)), math.sin(math.radians(el))))
    cam = camera(ctr + d * 10, ctr, lens)
    cam.data.type = "ORTHO"
    bpy.context.view_layer.update()
    M_ = cam.matrix_world.inverted()
    loc = [M_ @ p for p in pts]
    w = max(p.x for p in loc) - min(p.x for p in loc); h = max(p.y for p in loc) - min(p.y for p in loc)
    cx = (max(p.x for p in loc) + min(p.x for p in loc)) / 2; cy = (max(p.y for p in loc) + min(p.y for p in loc)) / 2
    cam.location = cam.matrix_world @ Vector((cx, cy, 0))
    sc = bpy.context.scene
    asp = sc.render.resolution_x / sc.render.resolution_y
    cam.data.ortho_scale = max(w, h * asp) * pad
    return cam

def glow_alg(name="alg_ui", c="#3FCB78", e=0.35):
    """Opaque-looking culture for transparent UI renders (transmission would show the empty film)."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = mat(name, c, 0.3, coat=0.15, sss=0.2, emit="#5BE38E", emit_str=e)
    color_var(m, "#1E9A55", c, 9)
    return m

# ---------------------------------------------------------------- products --
@asset("module", (768, 768), 128)
def a_module():
    hex_module("M", (0, 0, 0), (math.radians(62), 0, math.radians(18)), culture=glow_alg(), bubbles=30)
    frame(az=0, el=8)

@asset("icon512", (512, 512), 96)
def a_icon():
    hex_module("M", (0, 0, 0), (math.radians(90), 0, 0), culture=glow_alg(), bubbles=24)
    frame(az=0, el=0, pad=1.08)

@asset("hero_cluster", (900, 820), 128)
def a_cluster():
    root = empty("C", rot=(math.radians(58), 0, math.radians(14)))
    cells = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
    for i, (q, r) in enumerate(cells):
        x, y = axial(q, r)
        hex_module(f"H{i}", (x, y, 0.012 * (i % 3)), parent=root, culture=glow_alg(f"alg{i%3}", ["#3FCB78", "#2FB86A", "#58D98C"][i % 3]), seed=i, bubbles=16)
    frame(az=0, el=6, pad=1.08)

# -------------------------------------------------------------- mode icons --
def mini_cluster(root, cells, s=1.0, glow=0.35):
    for i, (q, r) in enumerate(cells):
        x, y = axial(q, r)
        hex_module(f"mc{i}", (x * s, y * s, 0), parent=root, culture=glow_alg("algi%d" % int(glow*10), e=glow), seed=i, bubbles=0, detail=False)

@asset("m_wall")
def a_wall():
    wall = box(1.5, 0.06, 1.3, mat("wall_ui", "#F3F6FA", 0.5), (0, 0.06, 0.65), bev=0.02)
    root = empty("W", (0, 0, 0.66), (math.radians(90), 0, 0))
    mini_cluster(root, [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)])
    frame(az=28, el=16)

@asset("m_floor")
def a_floor():
    root = empty("F", (0, 0, 0))
    mini_cluster(root, [(q, r) for q in range(-2, 3) for r in range(-2, 3) if abs(q + r) <= 2 and abs(q) <= 2 and abs(r) <= 2][:19])
    frame(az=30, el=42)

@asset("m_lamp")
def a_lamp():
    root = empty("L", (0, 0, 0), (math.radians(-90), 0, 0))
    mini_cluster(root, [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)], glow=1.2)
    for x in (-0.28, 0.28):
        cyl(0.006, 0.55, M()["alu"], (x, 0.03, 0.62), name="wire")
    box(0.75, 0.04, 0.03, M()["rim"], (0, 0.03, 0.9), name="canopy", bev=0.01)
    frame(az=0, el=4)

@asset("m_roof")
def a_roof():
    # little house with a gable roof of Algora tiles
    box(1.1, 1.0, 0.6, mat("house_ui", "#F6F8FC", 0.4, coat=0.3), (0, 0, 0.3), bev=0.02)
    box(0.22, 0.03, 0.36, mat("door_ui", "#8CC6FF", 0.3), (0, -0.505, 0.18), bev=0.01)
    for sgn in (-1, 1):
        root = empty("R%d" % sgn, (0, sgn * 0.27, 0.78), (sgn * math.radians(-35), 0, 0))
        mini_cluster(root, [(q, r) for q in range(-2, 3) for r in (0, 1) if not (q == 2 and r == 1)][:9])
    frame(az=32, el=18)

# --------------------------------------------------------------- UI icons ---
def mk_leaf(m, loc=(0, 0, 0), rot=(0, 0, 0), s=1.0):
    bm = bmesh.new()
    n = 24
    prof = [(math.sin(math.pi * t / n) ** 0.9 * 0.32 * s, (t / n - 0.5) * 1.0 * s) for t in range(n + 1)]
    rows = []
    for x, y in prof:
        rows.append([bm.verts.new((x * math.cos(a), y, x * math.sin(a) * 0.25)) for a in [i * 2 * math.pi / 24 for i in range(24)]])
    for k in range(n):
        for i in range(24):
            try:
                bm.faces.new((rows[k][i], rows[k][(i + 1) % 24], rows[k + 1][(i + 1) % 24], rows[k + 1][i]))
            except Exception:
                pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    ob = mk(bm, "leaf", m, smooth=True)
    ob.location, ob.rotation_euler = loc, rot
    return ob

def gm():
    return mat("ui_green", "#33C474", 0.25, coat=0.6, emit="#33C474", emit_str=0.15)
def bm_():
    return mat("ui_blue", BLUE, 0.25, coat=0.6, emit=BLUE, emit_str=0.2)
def wm():
    return mat("ui_white", "#F6F8FC", 0.3, coat=0.6)

@asset("ic_leaf", (256, 256), 64)
def i_leaf():
    mk_leaf(gm(), (0, 0, 0), (0, 0, math.radians(-35)))
    cyl(0.012, 0.25, wm(), (0.22, -0.32, 0), (0, 0, math.radians(55)))
    frame(az=0, el=60)

@asset("ic_drop", (256, 256), 64)
def i_drop():
    bm = bmesh.new()
    prof = []
    for i in range(33):
        t = math.pi * i / 32
        prof.append((0.5 * math.sin(t) * math.sin(t / 2) ** 1.3, 0.6 * math.cos(t)))
    rows = [[bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for a in [k * 2 * math.pi / 32 for k in range(32)]] for r, z in prof]
    for k in range(len(rows) - 1):
        for i in range(32):
            bm.faces.new((rows[k][i], rows[k][(i + 1) % 32], rows[k + 1][(i + 1) % 32], rows[k + 1][i]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    mk(bm, "drop", mat("ui_drop", "#5AA8FF", 0.05, trans=0.6, coat=1, emit=BLUE, emit_str=0.25), smooth=True)
    frame(az=20, el=12)

@asset("ic_temp", (256, 256), 64)
def i_temp():
    cyl(0.09, 0.8, wm(), (0, 0, 0.45), seg=48)
    sphere(0.17, mat("ui_red", "#FF6B5A", 0.25, coat=0.6), (0, 0, 0.0), seg=48)
    cyl(0.045, 0.5, mat("ui_red", "#FF6B5A", 0.25), (0, -0.06, 0.3), seg=32)
    frame(az=25, el=14)

@asset("ic_ph", (256, 256), 64)
def i_ph():
    for i, c in enumerate(["#FF6B5A", "#F5A524", "#33C474", "#2F7BFF", "#7B5CFF"]):
        box(0.16, 0.16, 0.06 + 0.1 * (i + 1), mat("ph%d" % i, c, 0.3, coat=0.6), (i * 0.2 - 0.4, 0, (0.06 + 0.1 * (i + 1)) / 2), bev=0.03)
    frame(az=25, el=24)

@asset("ic_bolt", (256, 256), 64)
def i_bolt():
    bm = bmesh.new()
    P = [(0.1, 0.6), (-0.35, -0.05), (-0.02, -0.05), (-0.12, -0.6), (0.35, 0.08), (0.03, 0.08)]
    vs = [bm.verts.new((x, 0, y)) for x, y in P]
    f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=(0, 0.16, 0), verts=[v for v in r["geom"] if isinstance(v, bmesh.types.BMVert)])
    ob = mk(bm, "bolt", mat("ui_yel", "#FFC23D", 0.25, coat=0.7, emit="#FFC23D", emit_str=0.2))
    bevel(ob, 0.03, 4, 30)
    frame(az=30, el=14)

@asset("ic_co2", (256, 256), 64)
def i_co2():
    sphere(0.22, wm(), (0, 0, 0), seg=48)
    sphere(0.17, mat("ui_grey", "#5B6B88", 0.3, coat=0.5), (-0.36, 0, 0), seg=48)
    sphere(0.17, mat("ui_grey", "#5B6B88", 0.3, coat=0.5), (0.36, 0, 0), seg=48)
    cyl(0.05, 0.72, wm(), (0, 0, 0), (0, math.pi / 2, 0))
    frame(az=20, el=20)

@asset("ic_ai", (256, 256), 64)
def i_ai():
    box(0.7, 0.5, 0.55, wm(), (0, 0, 0), bev=0.12)
    for x in (-0.15, 0.15):
        sphere(0.07, bm_(), (x, -0.25, 0.05), seg=32)
    cyl(0.02, 0.2, wm(), (0, 0, 0.38))
    sphere(0.06, mat("ui_green", "#33C474", 0.25), (0, 0, 0.5))
    frame(az=25, el=12)

# ------------------------------------------------------------------ run ----
for name, (fn, res, samples) in REG.items():
    if ONLY and name not in ONLY:
        continue
    studio(res, samples)
    fn()
    clear = mat("ui_clear", "#FFFFFF", 0.05, alpha=0.07, spec=0.25)
    for o in bpy.data.objects:
        if o.type == "MESH" and (o.name.endswith("_top") or "_baffle" in o.name or o.name.endswith("_bot")):
            o.data.materials.clear(); o.data.materials.append(clear)
    render_still(os.path.join(OUT, name + ".png"))
