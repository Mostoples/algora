"""ALGORA showreel shots (Cycles, frame-by-frame, auto-resume).
blender -b -P blender/film.py -- <shot> [start end]      shots: hero wall floor lamp roof
Frames -> output/frames/<shot>/f_0000.png ; label anchors -> output/frames/<shot>/anchors.json"""
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from lib import _set
import scenes as S
from bpy_extras.object_utils import world_to_camera_view

FPS = 30
SHOTS = dict(hero=270, wall=180, floor=150, lamp=150, roof=150)
RES = (int(os.environ.get("ALG_W", "1280")), int(os.environ.get("ALG_H", "720")))
SPP = int(os.environ.get("ALG_SPP", "40"))

def ss(a, b, t):
    t = max(0.0, min(1.0, (t - a) / (b - a)))
    return t * t * (3 - 2 * t)

def lerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)

def cam_to(cam, pos, tgt):
    cam.location = pos
    look_at(cam, tgt)

def set_glow(prefix, v, vol=True):
    for m in bpy.data.materials:
        if m.name.startswith(prefix):
            b = m.node_tree.nodes.get("Principled BSDF")
            _set(b, "Emission Strength", v)
            n = m.node_tree.nodes.get("vol")
            if n and vol:
                n.inputs["Emission Strength"].default_value = v * 1.6

# ------------------------------------------------------------- hero studio --
PART_OFF = {  # exploded offsets along module local Z (m)
    "_top": 0.16, "_dome": 0.30, "_hubled": 0.30, "_hub": 0.30, "_baffle": 0.06, "_culture": 0.0, "_bub": 0.0,
    "_ledstrip": -0.07, "_bot": -0.17, "_rim": -0.10, "_pad": -0.10, "_pogo": -0.10, "_port": -0.10,
}
def part_key(name):
    for k in ("_hubled", "_hub", "_dome", "_top", "_baffle", "_culture", "_bub", "_ledstrip", "_bot", "_rim", "_pad", "_pogo", "_port"):
        if k in name:
            return k
    return None

def build_hero():
    setup(RES, SPP, exposure=-0.1, look="AgX - Medium High Contrast")
    world_color("#C9D6E8", 0.35)
    # cyclorama
    bm = bmesh.new()
    prof = [(-6, 0)] + [(math.sin(a) * 2.5, 2.5 - math.cos(a) * 2.5) for a in [i * math.pi / 2 / 16 for i in range(17)]] + [(2.5, 8)]
    rows = [[bm.verts.new((x, y + 1.0, z)) for (y, z) in prof] for x in (-12, 12)]
    for i in range(len(prof) - 1):
        bm.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
    cyc = mk(bm, "cyc", mat("cyc", "#D9E3F0", 0.7), smooth=True)
    area("key", (2.2, -2.4, 3.0), 520, 2.4, target=(0, 0, 0.3))
    area("rim", (-2.8, 1.6, 1.4), 380, 2.0, "#9CC4FF", target=(0, 0, 0.3))
    area("fill", (-2, -3, 0.6), 120, 3.0, target=(0, 0, 0.3))
    area("top", (0, 0, 4), 160, 4.0, target=(0, 0, 0))
    centre = hex_module("HERO", (0, 0, 0.42), (math.radians(65), 0, 0), culture=algae_mat("alg_hero", 1.5, 0.3), bubbles=40, seed=7)
    parts = {}
    for o in bpy.data.objects:
        if o.parent == centre:
            parts[o.name] = (o, o.location.copy(), part_key(o.name))
    ring = []
    dirs = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
    for i, (q, r) in enumerate(dirs):
        x, y = axial(q, r)
        m = hex_module(f"N{i}", (x, y, 0), parent=centre, culture=algae_mat("alg_n%d" % (i % 3), 1.3 + 0.2 * (i % 3), 0.3), bubbles=10, seed=20 + i)
        ring.append((m, Vector((x, y, 0))))
    cam = camera((0, -2.0, 0.62), (0, 0, 0.42), 55, dof=2.0, fstop=4.0)
    return dict(cam=cam, centre=centre, parts=parts, ring=ring)

def upd_hero(d, f):
    t = f / FPS
    c = d["centre"]
    # 0-2.6s turntable; 2.6-5.2 exploded; 5.2-6.0 collapse; 6.0-9.0 neighbours snap in
    c.rotation_euler = (math.radians(44 + 6 * ss(5.2, 7.0, t) + 16 * (1 - ss(0, 2.4, t))), 0, math.radians(-40 + 60 * ss(0, 5.2, t) - 20 * ss(5.2, 7.5, t)))
    ex = ss(2.4, 3.6, t) * (1 - ss(5.0, 5.9, t))
    for name, (o, base, k) in d["parts"].items():
        o.location = base + Vector((0, 0, PART_OFF.get(k, 0) * ex))
    for i, (m, home) in enumerate(d["ring"]):
        s = ss(6.0 + i * 0.22, 6.9 + i * 0.22, t)
        out = home * 3.2 + Vector((0, 0, 0.25))
        m.location = out.lerp(home, s)
        for ch in [m] + list(m.children_recursive):
            ch.hide_render = s <= 0.0
        m.rotation_euler = (0, 0, (1 - s) * 0.6)
    pull = ss(5.6, 8.4, t)
    cam_to(d["cam"], lerp((1.0, -1.42, 0.78), (0.0, -2.5, 1.75), pull), lerp((0, 0, 0.44), (0, 0.25, 0.42), pull))
    d["cam"].data.lens = 58 - 20 * pull
    d["cam"].data.dof.focus_distance = 1.3 + 1.6 * pull
    set_glow("alg_hero", 0.3 + 0.6 * ss(7.6, 8.6, t))
    set_glow("alg_n", 0.3 + 0.6 * ss(7.6, 8.6, t))

def anchors_hero(d):
    """Exploded-view label anchors (world points) for the compositor."""
    c = d["centre"]
    pts = {}
    for name, (o, base, k) in d["parts"].items():
        key = {"_top": "top", "_hub": "core", "_culture": "culture", "_bot": "bottom", "_pad": "connector", "_ledstrip": "led"}.get(k)
        if key and key not in pts:
            pts[key] = o
    return pts

# ------------------------------------------------------------- scene shots --
def build_wall():
    d = S.scene_wall(0.0)
    return d

def upd_wall(d, f):
    t = f / SHOTS["wall"]
    s = ss(0.12, 0.62, t)
    nm = d["newm"]
    nm.location = d["approach"].lerp(d["hole"], s)
    nm.rotation_euler = (math.radians(90 - 12 * (1 - s)), 0, math.radians(8 * (1 - s)))
    rig = d["rig"]
    S.pose_reset(rig)
    bpy.context.view_layer.update()
    side = (nm.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()
    c = nm.location
    let_go = ss(0.66, 0.85, t)
    hl = c + side * (R * 0.95) + Vector((0, -0.04, -0.02))
    hr = c - side * (R * 0.95) + Vector((0, -0.04, -0.02))
    if let_go > 0:
        S.arms_down(rig)
        bpy.context.view_layer.update()
        dl, dr = S.rest(rig, "hand_ik.L"), S.rest(rig, "hand_ik.R")
        S.pose_reset(rig)
        hl, hr = hl.lerp(dl, let_go), hr.lerp(dr, let_go)
    S.pose_reach(rig, hand_l=hl, hand_r=hr, look=c)
    # glow ripple after the snap
    pulse = ss(0.62, 0.7, t) * (1 - 0.6 * ss(0.72, 0.95, t))
    set_glow("alg_w", 0.3 + 0.4 * pulse)
    set_glow("alg_new", 0.6 + 0.5 * pulse)
    _set(bpy.data.materials["led_blue"].node_tree.nodes["Principled BSDF"], "Emission Strength", 6 + 30 * pulse)
    cam_to(d["cam"], lerp((-2.4, -2.9, 1.4), (-1.3, -1.6, 1.45), ss(0, 1, t)), lerp((0.5, 2.2, 1.35), (0.95, 2.3, 1.45), ss(0, 1, t)))

def build_floor():
    d = S.scene_floor(0.0)
    rig = d["rig"]
    d["start"] = rig.location.copy()
    f, l, u = S.axes(rig)
    d["dir"] = f
    return d

def upd_floor(d, f):
    t = f / FPS
    rig = d["rig"]
    speed = 0.9
    rig.location = d["start"] + d["dir"] * (speed * t - 0.6)
    S.pose_reset(rig)
    bpy.context.view_layer.update()
    S.pose_walk(rig, (speed * t / 1.05) % 1.0)
    p = rig.location
    cam_to(d["cam"], p + Vector((2.6, -3.4, 0.9)) + Vector((0, 0, 0.15 * math.sin(t * 0.8))), p + Vector((-0.1, 0.4, 0.75)))
    set_glow("alg_p", 1.0 + 0.15 * math.sin(t * 2.4))

def build_lamp():
    return S.scene_lamp(0.0)

def upd_lamp(d, f):
    t = f / SHOTS["lamp"]
    on = ss(0.12, 0.42, t)
    set_glow("alg_l", 0.05 + 2.95 * on)
    bpy.data.objects["pend_down"].data.energy = 3 + 157 * on
    _set(bpy.data.materials["led_white"].node_tree.nodes["Principled BSDF"], "Emission Strength", 1 + 11 * on)
    a = -0.5 + 0.25 * ss(0, 1, t)
    r = 3.4 - 0.5 * ss(0, 1, t)
    cam_to(d["cam"], (r * math.sin(a) + 0.1, 0.7 - r * math.cos(a), 0.95 + 0.35 * ss(0, 1, t)), (0.1, 0.7, 1.35 - 0.15 * ss(0, 1, t)))

def build_roof():
    return S.scene_roof(0.0)

def upd_roof(d, f):
    t = f / SHOTS["roof"]
    k = ss(0, 1, t)
    sun_ob = bpy.data.objects.get("sun")
    if sun_ob:
        sun_ob.rotation_euler = (math.radians(28), 0, math.radians(150 + 25 * k))
    cam_to(d["cam"], lerp((5.6, -6.9, 2.4), (1.2, -1.0, 1.3), k), lerp((0.0, 0.2, 1.7), (-0.6, 1.0, 2.7), k))
    d["cam"].data.lens = 30 - 12 * k
    d["cam"].data.dof.focus_distance = 9.0 - 6.8 * k

BUILD = dict(hero=build_hero, wall=build_wall, floor=build_floor, lamp=build_lamp, roof=build_roof)
UPD = dict(hero=upd_hero, wall=upd_wall, floor=upd_floor, lamp=upd_lamp, roof=upd_roof)

if __name__ == "__main__":
    A = args()
    shot = A[0]
    f0 = int(A[1]) if len(A) > 1 else 0
    f1 = int(A[2]) if len(A) > 2 else SHOTS[shot] - 1
    step = int(os.environ.get("ALG_STEP", "1"))
    out = os.path.join(os.environ.get("ALG_OUT") or os.path.join(ROOT, "output", "frames"), shot)
    os.makedirs(out, exist_ok=True)
    reset()
    import addon_utils
    addon_utils.enable("io_scene_gltf2", default_set=True)
    d = BUILD[shot]()
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = RES
    sc.cycles.samples = SPP
    sc.render.use_persistent_data = os.environ.get("ALG_PERSIST", "1") == "1"
    anchors = {}
    for f in range(f0, f1 + 1, step):
        path = os.path.join(out, f"f_{f:04d}.png")
        UPD[shot](d, f)
        bpy.context.view_layer.update()
        if shot == "hero":
            cam = d["cam"]
            anchors[f] = {k: list(world_to_camera_view(sc, cam, o.matrix_world.translation))[:2] for k, o in anchors_hero(d).items()}
        if os.path.exists(path):
            continue
        sc.render.filepath = path
        import time as _t
        t0 = _t.time()
        bpy.ops.render.render(write_still=True)
        print("FRAME", shot, f, "%.1fs" % (_t.time() - t0), flush=True)
    if anchors:
        old = {}
        ap = os.path.join(out, "anchors.json")
        if os.path.exists(ap):
            old = json.load(open(ap))
        old.update({str(k): v for k, v in anchors.items()})
        json.dump(old, open(ap, "w"))
