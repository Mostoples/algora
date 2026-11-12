"""ALGORA in-use scenes (concept stills + animation source).
blender -b -P blender/scenes.py -- <out_dir> <wall|floor|lamp|roof|hero> [still|anim] [frame_start frame_end]
Each builder returns a dict with the camera + animated handles so film.py can keyframe them."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from lib import _set

# ------------------------------------------------------------ environment --
def planks(name="planks", c1="#9A6A44", c2="#C99A6A", scale=4.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = mat(name, c1, 0.42, coat=0.25)
    nt = m.node_tree; b = nt.nodes.get("Principled BSDF")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Scale"].default_value = scale; br.inputs["Mortar Size"].default_value = 0.004
    br.inputs["Brick Width"].default_value = 1.6; br.inputs["Row Height"].default_value = 0.16
    br.inputs["Color1"].default_value = lin(c1); br.inputs["Color2"].default_value = lin(c2)
    br.inputs["Mortar"].default_value = lin("#4A3020"); br.offset = 0.37
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 30; wv.inputs["Distortion"].default_value = 8
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 0.25
    nt.links.new(tc.outputs["Object"], br.inputs["Vector"]); nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    nt.links.new(br.outputs["Color"], mix.inputs["A"]); nt.links.new(wv.outputs["Color"], mix.inputs["B"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.25
    nt.links.new(br.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def plaster(name="plaster", c="#ECEEF1"):
    m = bpy.data.materials.get(name)
    if m:
        return m
    return noise_bump(color_var(mat(name, c, 0.85), c, "#E2E5EA", 4), 90, 0.04)

def concrete(name="concrete", c1="#A9ADB2", c2="#C9CCD0"):
    m = bpy.data.materials.get(name)
    if m:
        return m
    return noise_bump(color_var(mat(name, c1, 0.75), c1, c2, 6), 40, 0.15)

def room(W=7.0, D=5.5, H=2.9, window=True, floor_m=None, back_c="#E9ECEF"):
    """Floor, back wall (y=+D/2), left wall (x=-W/2) with a big window, ceiling."""
    floor_m = floor_m or planks()
    box(W + 0.4, D + 0.4, 0.05, floor_m, (0, 0, -0.025), name="floor")
    box(W + 0.4, 0.12, H, plaster("back", back_c), (0, D / 2 + 0.06, H / 2), name="wall_back")
    box(0.12, D + 0.4, H, plaster(), (W / 2 + 0.06, 0, H / 2), name="wall_right")
    box(W + 0.4, D + 0.4, 0.1, plaster(), (0, 0, H + 0.05), name="ceiling")
    wx = -W / 2 - 0.06
    if window:
        y0, y1, z0, z1 = -1.6, 1.6, 0.45, 2.55
        box(0.12, (D / 2 + 0.2) - y1, H, plaster(), (wx, (y1 + D / 2 + 0.2) / 2, H / 2), name="wl1")
        box(0.12, y0 + D / 2 + 0.2, H, plaster(), (wx, (y0 - D / 2 - 0.2) / 2, H / 2), name="wl2")
        box(0.12, y1 - y0, z0, plaster(), (wx, 0, z0 / 2), name="wl3")
        box(0.12, y1 - y0, H - z1, plaster(), (wx, 0, (H + z1) / 2), name="wl4")
        fm = mat("frame_dark", "#2B2F36", 0.4, metal=0.6)
        for y in (y0, 0, y1):
            box(0.06, 0.05, z1 - z0, fm, (wx, y, (z0 + z1) / 2), name="mullion")
        for z in (z0, z1):
            box(0.06, y1 - y0, 0.05, fm, (wx, 0, z), name="transom")
        g = box(0.01, y1 - y0, z1 - z0, mat("window_glass", "#FFFFFF", 0.0, trans=1.0, ior=1.05), (wx, 0, (z0 + z1) / 2), name="glass")
        g.visible_shadow = False
    else:
        box(0.12, D + 0.4, H, plaster(), (wx, 0, H / 2), name="wall_left")

def skirting(W, D):
    m = mat("skirt", "#F3F4F6", 0.4)
    box(W, 0.02, 0.08, m, (0, D / 2 - 0.01, 0.04), name="skirt")

def outdoor_ground(size=40, grass=True, density=1.0, grass_size=14):
    if grass and grass_size < size:
        box(size * 6, size * 6, 0.02, noise_bump(color_var(mat("soil_far", "#4E7A2C", 0.9), "#3E6A24", "#6C9A3A", 0.5), 3, 0.2), (0, 0, -0.012), name="ground_far")
        size = grass_size
    g = box(size, size, 0.02, noise_bump(color_var(mat("soil", "#4E6B2F", 0.9), "#3E5A26", "#6C8A3A", 3), 30, 0.3), (0, 0, -0.01), name="ground")
    if grass:
        ps = g.modifiers.new("grass", "PARTICLE_SYSTEM").particle_system.settings
        ps.type = "HAIR"; ps.count = int(220 * size * size * density); ps.hair_length = 0.08
        ps.child_type = "INTERPOLATED"; ps.rendered_child_count = 20; ps.child_length = 0.9
        ps.roughness_2 = 0.5; ps.clump_factor = 0.2; ps.use_advanced_hair = True
        ps.brownian_factor = 0.02; ps.roughness_endpoint = 0.04
        ps.root_radius = 0.0016; ps.tip_radius = 0.0
        gm = mat("grass_m", "#4F8A2E", 0.55, sss=0.2)
        color_var(gm, "#3C7A24", "#7BA642", 2)
        g.data.materials.append(gm)
        ps.material = 2
        ps.display_step = 2; ps.render_step = 3
    return g

def hide_where(fn):
    for o in list(bpy.data.objects):
        if fn(o):
            o.hide_render = True

def clear_cells(cells, holes):
    return [c for c in cells if c not in holes]

# ----------------------------------------------------------------- phone ---
def phone(loc=(0, 0, 0), rot=(0, 0, 0), screen_img=None, parent=None):
    root = empty("phone", loc, rot, parent)
    box(0.074, 0.008, 0.155, mat("phone_body", "#1C2230", 0.25, metal=0.4, coat=0.8), (0, 0, 0), name="ph_body", parent=root, bev=0.006)
    sm = bpy.data.materials.get("phone_screen") or mat("phone_screen", "#000000", 0.1)
    if screen_img and os.path.exists(screen_img) and not sm.node_tree.nodes.get("img"):
        nt = sm.node_tree; b = nt.nodes.get("Principled BSDF")
        tx = nt.nodes.new("ShaderNodeTexImage"); tx.name = "img"; tx.image = bpy.data.images.load(screen_img)
        nt.links.new(tx.outputs["Color"], b.inputs["Emission Color"]); nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
        _set(b, "Emission Strength", 1.6)
    bm = bmesh.new()
    w, h = 0.068, 0.148
    v = [bm.verts.new((x, 0, z)) for x, z in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
    f = bm.faces.new(v)
    uv = bm.loops.layers.uv.new()
    for l, (u, vv) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        l[uv].uv = (u, vv)
    s = mk(bm, "ph_screen", sm, root)
    s.location = (0, -0.0042, 0)
    return root

# ------------------------------------------------------------ human poses ---
def person(rot_z=0.0, loc=(0, 0, 0), **kw):
    base, rig = make_human(**kw)
    rig.location = loc
    rig.rotation_euler = (0, 0, rot_z)
    bpy.context.view_layer.update()
    return base, rig

def axes(rig):
    R3 = rig.matrix_world.to_3x3().normalized()
    return R3 @ Vector((0, -1, 0)), R3 @ Vector((1, 0, 0)), Vector((0, 0, 1))  # forward, character-left, up

def pose_reset(rig):
    for pb in rig.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
    for pb in rig.pose.bones:
        if "IK_FK" in pb.keys():
            pb["IK_FK"] = 0.0
        if "IK_Stretch" in pb.keys():
            pb["IK_Stretch"] = 0.0
    bpy.context.view_layer.update()

def rest(rig, name):
    """World position of a control in rest/current pose."""
    bpy.context.view_layer.update()
    return rig.matrix_world @ rig.pose.bones[name].head

def arms_down(rig, out=0.0):
    f, l, u = axes(rig)
    for s, sg in (("L", 1), ("R", -1)):
        sh = rest(rig, f"upper_arm_fk.{s}") if f"upper_arm_fk.{s}" in rig.pose.bones else rest(rig, f"hand_ik.{s}")
        tgt = sh + l * sg * (0.06 + out) - u * 0.62 + f * 0.04
        place_bone(rig, f"hand_ik.{s}", tgt)

def pose_reach(rig, hand_l=None, hand_r=None, look=None):
    """Hands to world targets (IK), the other arm relaxed."""
    arms_down(rig)
    if hand_l is not None:
        place_bone(rig, "hand_ik.L", hand_l)
    if hand_r is not None:
        place_bone(rig, "hand_ik.R", hand_r)
    if look is not None:
        head_look(rig, look)

def head_look(rig, target, amount=0.7):
    pb = rig.pose.bones.get("head")
    if not pb:
        return
    bpy.context.view_layer.update()
    hp = rig.matrix_world @ pb.head
    f, l, u = axes(rig)
    d = (Vector(target) - hp).normalized()
    yaw = math.atan2(d.dot(l), d.dot(f)) * amount
    pitch = math.asin(max(-1, min(1, d.dot(u)))) * amount
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = (-pitch, yaw, 0)
    bpy.context.view_layer.update()

def pose_walk(rig, phase, stride=0.32, lift=0.07):
    """Procedural walk cycle around the current rig location. phase in [0,1)."""
    f, l, u = axes(rig)
    a = 2 * math.pi * phase
    for s, sg, off in (("L", 1, 0.0), ("R", -1, math.pi)):
        ft = rest(rig, f"foot_ik.{s}")
        fwd = math.sin(a + off) * stride / 2
        up = max(0.0, math.cos(a + off)) * lift
        place_bone(rig, f"foot_ik.{s}", ft + f * fwd + u * up)
    tb = rig.pose.bones.get("torso")
    if tb:
        tb.location = (0, 0, 0)
        bpy.context.view_layer.update()
        tw = rest(rig, "torso")
        place_bone(rig, "torso", tw + u * (-0.025 + 0.018 * abs(math.cos(a))))
    for s, sg, off in (("L", 1, math.pi), ("R", -1, 0.0)):
        sh = rest(rig, f"upper_arm_fk.{s}") if f"upper_arm_fk.{s}" in rig.pose.bones else None
        if sh is None:
            continue
        sw = math.sin(a + off) * 0.16
        place_bone(rig, f"hand_ik.{s}", sh + l * sg * 0.1 - u * 0.6 + f * (0.05 + sw))

# ------------------------------------------------------------------ scenes --
APP_SHOT = os.path.join(ROOT, "output", "app", "id_home.png")

def scene_wall(frame_t=0.0):
    """Living room, evening. Honeycomb wall above the sofa; person snaps in a new module."""
    setup((1600, 900), 96, exposure=0.6)
    world_sky(0.35, sun_el=4, sun_rot=-70)
    room(7.0, 5.5, 2.9)
    D = 5.5
    wy = D / 2 - 0.035
    rnd = random.Random(5)
    cells = []
    for q in range(-6, 7):
        for r in range(-6, 7):
            x, y = axial(q, r)
            e = (x / 1.55) ** 2 + (y / 0.78) ** 2
            if e < 1.0 - rnd.random() * 0.25 * (e > 0.6):
                cells.append((q, r))
    hole = max(cells, key=lambda c: axial(*c)[0] - abs(axial(*c)[1] - 0.05) * 2)
    cells.remove(hole)
    wall_root = empty("HONEY", (0.2, wy - DIM["depth"] * MM / 2, 1.62), (math.radians(90), 0, 0))
    for i, (q, r) in enumerate(cells):
        x, y = axial(q, r)
        hex_module(f"W{i:02d}", (x, y, 0), parent=wall_root, culture=algae_mat("alg_w%d" % (i % 3), 1.4 + 0.3 * (i % 3), 0.3), seed=i, bubbles=12, bottom="frost")
    # new module in the hands
    hx, hy = axial(*hole)
    bpy.context.view_layer.update()
    hole_w = wall_root.matrix_world @ Vector((hx, hy, 0))
    newm = hex_module("NEW", (0, 0, 0), culture=algae_mat("alg_new", 0.6, 0.9), seed=99, bubbles=16)
    approach = hole_w + Vector((0, -0.28, -0.05))
    t = frame_t
    newm.location = approach.lerp(hole_w, t)
    newm.rotation_euler = (math.radians(90 - 12 * (1 - t)), 0, math.radians(8 * (1 - t)))
    # furniture (Sketchfab)
    import_glb("sofa", (0.0, 1.95, 0), math.radians(180), width=2.3)
    import_glb("monstera", (-2.05, 2.15, 0), 0.4, height=1.35)
    import_glb("pothos", (-1.35, 2.35, 0.0), 0.0, height=0.55)
    import_glb("palm", (2.95, 2.25, 0), 1.0, height=1.9)
    rug = box(2.8, 1.9, 0.012, noise_bump(mat("rug", "#D8D2C8", 0.95), 200, 0.25), (0.1, 0.55, 0.006), name="rug")
    cyl(0.5, 0.04, mat("marble", "#F4F2EE", 0.15, coat=0.6), (0.1, 0.55, 0.38), name="table_top", seg=96)
    cyl(0.06, 0.36, wood("oak", "#B58A5F", "#D8B48A"), (0.1, 0.55, 0.18), name="table_leg")
    cyl(0.28, 0.02, wood("oak"), (0.1, 0.55, 0.01), name="table_base", seg=64)
    phone((0.3, 0.45, 0.405), (math.radians(90), 0, 0.4), APP_SHOT)
    # person
    base, rig = person(math.radians(155), (hole_w.x + 0.42, hole_w.y - 0.62, 0))
    pose_reset(rig)
    f, l, u = axes(rig)
    side = (newm.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()
    bpy.context.view_layer.update()
    c = newm.location
    pose_reach(rig, hand_l=c + side * (R * 0.95) + Vector((0, -0.04, -0.02)), hand_r=c - side * (R * 0.95) + Vector((0, -0.04, -0.02)), look=c)
    # light
    area("ceiling_soft", (0.3, 0.2, 2.8), 120, 2.5, "#FFE9CF", target=(0.3, 0.2, 0))
    point("floorlamp", (-2.8, 1.6, 1.6), 60, "#FFC98A", 0.15)
    cam = camera((-2.15, -2.45, 1.38), (0.55, 2.2, 1.35), 30, dof=4.2, fstop=4.0)
    return dict(cam=cam, rig=rig, newm=newm, hole=hole_w, approach=approach)

def scene_floor(frame_t=0.0):
    """Garden terrace at blue hour: a glowing hexagon paving path through the lawn."""
    setup((1600, 900), 96, exposure=0.4)
    world_sky(0.45, sun_el=-1.0, sun_rot=200, dust=2)
    lawn = noise_bump(color_var(mat("lawn", "#3F6E26", 0.85, sss=0.05), "#2E5A1C", "#5E8E34", 22), 220, 0.6, 8)
    box(60, 60, 0.02, lawn, (0, 0, -0.01), name="ground")
    # path: meandering 2-3 cells wide, flush with the ground
    path = set()
    for q in range(-14, 13):
        rc = int(round(-q / 2 + 1.4 * math.sin(q / 3.5)))
        for dr in (-2, -1, 0, 1, 2):
            if abs(dr) < 2 or (q + dr) % 3:
                path.add((q, rc + dr))
    # round terrace "plaza" at the end of the path
    for (q, r) in hex_ring(3):
        path.add((q + 9, r - 4))
    root = empty("PATH", (0, 0, -DIM["depth"] * MM / 2 + 0.008), (0, 0, math.radians(-12)))
    for i, (q, r) in enumerate(sorted(path)):
        x, y = axial(q, r)
        hex_module(f"P{i:03d}", (x, y, 0), parent=root, culture=(bpy.data.materials.get("alg_p%d" % (i % 3)) or color_var(mat("alg_p%d" % (i % 3), "#2DBE6C", 0.25, emit="#3EDC78", emit_str=1.0), ["#1E9A50", "#22A456", "#2AAE5E"][i % 3], "#6FE39A", 9)), seed=i, bubbles=0,
                   rim_m=mat("rim_paver", "#8E959E", 0.55), detail=(i % 5 == 0), bottom="frost")
    # bed of gravel along the path
    gr = box(0.01, 0.01, 0.01, mat("x", "#000000"))
    gr.hide_render = True
    import_glb("maple", (-3.4, 3.4, 0), 0.6, height=3.8)
    import_glb("lounge", (3.1, 1.2, 0), math.radians(-120), width=1.8)
    import_glb("palm", (1.5, 3.6, 0), 0.3, height=1.8)
    # house facade behind
    box(16, 0.3, 4.2, plaster("facade", "#E6E2DA"), (0, 6.5, 2.1), name="facade")
    fm = mat("frame_dark", "#2B2F36", 0.4, metal=0.6)
    for x in (-4.0, 0, 4.0):
        box(2.2, 0.05, 2.4, mat("win_warm", "#FFD8A0", 0.6, emit="#FFC680", emit_str=0.35), (x, 6.33, 1.6), name="win")
        for dx in (-1.1, 0, 1.1):
            box(0.06, 0.08, 2.5, fm, (x + dx, 6.3, 1.6), name="mull")
        for z in (0.4, 1.6, 2.8):
            box(2.3, 0.08, 0.06, fm, (x, 6.3, z), name="trans")
    point("porch", (0, 6.0, 2.8), 60, "#FFC98A", 0.2)
    base, rig = person(math.radians(80), (-2.0, 0.3, 0.012), outfit="female_casualsuit02", hair="ponytail01",
                       skin="young_asian_female", shoes="shoes04", gender=0.0, height=0.45, muscle=0.4)
    pose_reset(rig)
    pose_walk(rig, frame_t)
    cam = camera((2.4, -3.6, 0.85), (-0.6, 0.6, 0.45), 28, dof=4.4, fstop=3.2)
    return dict(cam=cam, rig=rig)

def scene_lamp(frame_t=0.0):
    """Dining room: a 7-module pendant over the table, culture glowing downward."""
    setup((1600, 900), 96, exposure=0.4)
    world_sky(0.12, sun_el=-2, sun_rot=-60)
    room(7.0, 5.5, 2.9, back_c="#E4E7EA")
    import_glb("dining", (0, 0.6, 0), math.radians(90), scale=1.0, drop=("FLOOR", "WALL", "LIGHT_PENDANT", "LAMP", "FRAME", "SIDE_BOARD"))
    import_glb("monstera", (2.6, 2.2, 0), 0.4, height=1.4)
    import_glb("pothos", (-2.6, 2.2, 0), 0.4, height=0.7)
    pend = empty("PENDANT", (0, 0.6, 1.62), (0, 0, math.radians(10)))
    for i, (q, r) in enumerate([(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]):
        x, y = axial(q, r)
        hex_module(f"L{i}", (x, y, 0), parent=pend, culture=algae_mat("alg_l%d" % (i % 2), 0.6, 3.0), seed=i, bubbles=14, bottom="frost")
    for k in range(3):
        a = k * 2 * math.pi / 3 + 0.3
        p = Vector((0.45 * math.cos(a), 0.6 + 0.45 * math.sin(a), 0))
        cyl(0.0025, 1.26, M()["alu"], (p.x, p.y, 1.62 + 0.63), name="cable")
    cyl(0.12, 0.03, M()["rim"], (0, 0.6, 2.885), name="canopy")
    # downlight from the pendant underside
    area("pend_down", (0, 0.6, 1.58), 90, 0.9, "#E9FFE9", target=(0, 0.6, 0), shape="DISK")
    point("corner", (-3, -1.5, 1.8), 30, "#FFC98A", 0.2)
    # framed art + sideboard on back wall
    box(1.8, 0.45, 0.75, wood("walnut", "#5A3A26", "#7A5236"), (0, 2.5, 0.375), name="sideboard", bev=0.01)
    base, rig = person(math.radians(200), (0.95, -0.55, 0))
    pose_reset(rig)
    f, l, u = axes(rig)
    ph = rest(rig, "hand_ik.R")
    head = rest(rig, "head") if "head" in rig.pose.bones else ph + u * 0.5
    phone_pos = head + f * 0.32 - u * 0.33
    arms_down(rig)
    place_bone(rig, "hand_ik.R", phone_pos - l * 0.03)
    place_bone(rig, "hand_ik.L", phone_pos + l * 0.04 - u * 0.02)
    yaw = math.atan2(f.y, f.x)
    phone(phone_pos + f * 0.02 + u * 0.03, (math.radians(55), 0, yaw - math.pi / 2), APP_SHOT)
    cam = camera((-2.3, -2.6, 1.15), (0.1, 0.7, 1.25), 28, dof=3.6, fstop=3.5)
    return dict(cam=cam, rig=rig, pend=pend)

def scene_roof(frame_t=0.0):
    """Pergola roofed with ALGORA tiles: daylight filters green through the culture."""
    setup((1600, 900), 96, exposure=-1.6)
    world_sky(0.35, sun_el=58, sun_rot=150)
    sun("sun", (28, 0, 160), 3.2, "#FFF3E0", 1.0)
    outdoor_ground(30, grass=True, density=1.0)
    deck = box(5.2, 4.2, 0.06, planks("deck", "#8C6A4E", "#A98260", 3.0), (0, 0, 0.03), name="deck")
    # pergola frame
    wm_ = wood("pergola", "#6E4B32", "#94684A")
    for x in (-2.4, 2.4):
        for y in (-1.9, 1.9):
            box(0.12, 0.12, 2.6, wm_, (x, y, 1.3), name="post", bev=0.01)
    for y in (-1.9, 1.9):
        box(5.1, 0.1, 0.2, wm_, (0, y, 2.6), name="beam", bev=0.01)
    tilt = math.radians(14)
    roof = empty("ROOF", (0, 0, 2.78), (tilt, 0, 0))
    cells = [(q, r) for q in range(-9, 10) for r in range(-10, 10)]
    i = 0
    for (q, r) in cells:
        x, y = axial(q, r)
        if abs(x) <= 2.55 and abs(y) <= 2.15:
            hex_module(f"R{i:03d}", (x, y, 0), parent=roof, culture=algae_mat("alg_r%d" % (i % 3), 0.9 + 0.25 * (i % 3), 0.25), seed=i, bubbles=4,
                       led_on=False, detail=(i % 4 == 0), bottom="acrylic")
            i += 1
    daylight_modules("R")
    area("roof_filter", (0, 0, 2.5), 90, 4.8, "#86F59E", target=(0, 0, 0), size_y=4.0)
    for x in (-2.4, -1.2, 0, 1.2, 2.4):
        box(0.08, 4.4, 0.12, wm_, (x, 0, 2.66), (tilt, 0, 0), name="rafter", bev=0.01)
    import_glb("lounge", (-0.9, -0.3, 0.06), math.radians(20), width=2.1)
    import_glb("palm", (2.0, 1.4, 0.06), 0.3, height=1.6)
    import_glb("maple", (5.5, 4.5, 0), 1.2, height=4.2)
    import_glb("pothos", (-2.1, 1.6, 0.06), 0.3, height=0.5)
    box(18, 0.25, 3.6, plaster("facade", "#E6E2DA"), (0, 4.4, 1.8), name="house")
    base, rig = person(math.radians(-25), (1.0, -0.4, 0.06))
    pose_reset(rig)
    f, l, u = axes(rig)
    head = rest(rig, "head") if "head" in rig.pose.bones else Vector((1, -0.4, 1.6))
    arms_down(rig)
    place_bone(rig, "hand_ik.R", head + f * 0.25 - l * 0.32 + u * 0.35)   # pointing up at the roof
    head_look(rig, (0.5, 0.3, 2.8))
    for x in (-5.0, 5.0):
        box(2.0, 0.05, 1.6, mat("win_day", "#9FB6CC", 0.05, metal=0.3), (x, 4.27, 1.7), name="win")
    cam = camera((6.2, -6.6, 2.6), (0.0, 0.2, 1.7), 32, dof=9.0, fstop=8.0)
    return dict(cam=cam, rig=rig)

SCENES = dict(wall=scene_wall, floor=scene_floor, lamp=scene_lamp, roof=scene_roof)

if __name__ == "__main__":
    A = args()
    out = os.path.abspath(A[0]); which = A[1]; mode = A[2] if len(A) > 2 else "still"
    os.makedirs(out, exist_ok=True)
    reset()
    import addon_utils
    addon_utils.enable("io_scene_gltf2", default_set=True)
    res = int(os.environ.get("ALG_RES", "1280"))
    d = SCENES[which](0.55 if which == "wall" else 0.25)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = res, res * 9 // 16
    sc.cycles.samples = int(os.environ.get("ALG_SPP", "64"))
    if os.environ.get("ALG_SAVE"):
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, which + ".blend"))
    render_still(os.path.join(out, f"concept_{which}.png"))
