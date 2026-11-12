"""
ALGORA - shared Blender library (Blender 5.2, Cycles).
1 unit = 1 metre. Every visual comes from code: change DIM / palette and re-run.
"""
import bpy, bmesh, math, os, sys, glob, random
from mathutils import Vector, Matrix, Euler

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SF = os.path.join(ROOT, "assets", "sketchfab")

# ------------------------------------------------------------------ palette --
def lin(h, a=1.0):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*c, a)

BLUE, DEEP, SKY, ICE, BG, INK = "#2F7BFF", "#1646D6", "#8CC6FF", "#DDEBFF", "#E9EFF7", "#16233F"
ALGAE, ALGAE_DEEP, ALGAE_GLOW = "#2FB86A", "#0E6B3A", "#7DFFA0"
WHITE = "#F4F7FC"

# Product dimensions (mm) - single source of truth, mirrored in app/js/app.js
DIM = dict(
    flat=300,        # flat-to-flat of one hexagon module
    depth=42,        # total module thickness
    rim=11,          # polymer frame wall width
    sheet=5,         # acrylic sheet thickness (top & bottom)
    gap=3,           # joint gap between neighbour modules
    hub_r=34,        # AIoT core radius (centre puck)
    hub_h=30,
    port_w=56,       # connector pad width on each side face
)
MM = 0.001
F = DIM["flat"] * MM
R = F / math.sqrt(3)            # circumradius (flat-top hexagon)

def axial(q, r, gap=DIM["gap"] * MM):
    """Flat-top hex axial coordinate -> local (x, y)."""
    f = F + gap
    rr = f / math.sqrt(3)
    return (1.5 * rr * q, f * (r + q / 2))

def hex_ring(n):
    """Axial coords of a filled hex 'blob' of radius n (n=1 -> 7 cells)."""
    out = []
    for q in range(-n, n + 1):
        for r in range(max(-n, -q - n), min(n, -q + n) + 1):
            out.append((q, r))
    return out

# -------------------------------------------------------------- scene setup --
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

_gpu = False
def setup(res=(1600, 900), samples=96, exposure=0.0, look="AgX - Medium High Contrast", transparent=False):
    global _gpu
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    if not _gpu:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        try:
            prefs.compute_device_type = "OPTIX"
            prefs.refresh_devices()
            for d in prefs.devices:
                d.use = d.type == "OPTIX"
        except Exception as e:
            print("GPU fallback CPU", e)
        _gpu = True
    sc.cycles.device = "GPU"
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.02
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = "OPTIX"
    except Exception:
        pass
    sc.cycles.max_bounces = 10
    sc.cycles.transmission_bounces = 10
    sc.cycles.transparent_max_bounces = 12
    sc.cycles.volume_bounces = 1
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 1.0
    sc.render.use_persistent_data = False
    sc.render.film_transparent = transparent
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    # scenes use AgX (photographic); product/UI assets use Standard (brand colours exact)
    try:
        sc.view_settings.view_transform = "AgX" if look else "Standard"
        if look:
            sc.view_settings.look = look
    except Exception as e:
        print("look", e)
    sc.view_settings.exposure = exposure
    return sc

def world_sky(strength=1.0, sun_el=35, sun_rot=40, air=1.0, dust=1.0):
    """Physical sky (Nishita/'Multiple Scattering')."""
    w = bpy.data.worlds.new("sky")
    bpy.context.scene.world = w
    nt = w.node_tree
    bg = nt.nodes.get("Background")
    sky = nt.nodes.new("ShaderNodeTexSky")
    for t in ("MULTIPLE_SCATTERING", "NISHITA"):
        try:
            sky.sky_type = t
            break
        except Exception:
            pass
    try:
        sky.sun_elevation = math.radians(sun_el)
        sky.sun_rotation = math.radians(sun_rot)
        sky.air_density = air
        sky.aerosol_density = dust
    except Exception as e:
        print("sky", e)
    nt.links.new(sky.outputs[0], bg.inputs[0])
    bg.inputs[1].default_value = strength
    return w

def world_color(color="#DDE6F2", strength=0.6):
    w = bpy.data.worlds.new("w")
    bpy.context.scene.world = w
    bg = w.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = lin(color)
    bg.inputs[1].default_value = strength
    return w

def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

def area(name, loc, energy, size, color="#FFFFFF", target=(0, 0, 0), shape="RECTANGLE", size_y=None):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy, ld.color = energy, lin(color)[:3]
    ld.shape = shape
    ld.size = size
    ld.size_y = size_y or size
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    look_at(ob, target)
    return ob

def sun(name, rot, energy=3.0, color="#FFF4E5", angle=1.0):
    ld = bpy.data.lights.new(name, "SUN")
    ld.energy, ld.color, ld.angle = energy, lin(color)[:3], math.radians(angle)
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = [math.radians(a) for a in rot]
    return ob

def point(name, loc, energy, color="#FFFFFF", radius=0.05):
    ld = bpy.data.lights.new(name, "POINT")
    ld.energy, ld.color = energy, lin(color)[:3]
    ld.shadow_soft_size = radius
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    return ob

def camera(loc, target, lens=35, dof=None, fstop=2.8, name="cam"):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_width = 36
    ob = bpy.data.objects.new(name, cd)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    look_at(ob, target)
    if dof:
        cd.dof.use_dof = True
        cd.dof.focus_distance = dof
        cd.dof.aperture_fstop = fstop
    bpy.context.scene.camera = ob
    return ob

# ---------------------------------------------------------------- materials --
def _set(node, name, val):
    if name in node.inputs:
        node.inputs[name].default_value = val

def mat(name, color=WHITE, rough=0.4, metal=0.0, coat=0.0, trans=0.0, ior=1.45, emit=None, emit_str=0.0,
        sss=0.0, alpha=1.0, spec=0.5):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    _set(b, "Base Color", lin(color))
    _set(b, "Roughness", rough)
    _set(b, "Metallic", metal)
    _set(b, "Coat Weight", coat)
    _set(b, "Coat Roughness", 0.05)
    _set(b, "Transmission Weight", trans)
    _set(b, "IOR", ior)
    _set(b, "Subsurface Weight", sss)
    _set(b, "Specular IOR Level", spec)
    _set(b, "Alpha", alpha)
    if emit:
        _set(b, "Emission Color", lin(emit))
        _set(b, "Emission Strength", emit_str)
    return m

def noise_bump(m, scale=60, strength=0.08, detail=6):
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    tx = nt.nodes.new("ShaderNodeTexNoise"); tx.inputs["Scale"].default_value = scale
    tx.inputs["Detail"].default_value = detail
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = strength
    nt.links.new(tx.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def color_var(m, c1, c2, scale=8):
    """Two-tone noise base colour (concrete, plaster, wood-ish)."""
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    tx = nt.nodes.new("ShaderNodeTexNoise"); tx.inputs["Scale"].default_value = scale
    tx.inputs["Detail"].default_value = 8
    rp = nt.nodes.new("ShaderNodeValToRGB")
    rp.color_ramp.elements[0].color = lin(c1); rp.color_ramp.elements[1].color = lin(c2)
    rp.color_ramp.elements[0].position = 0.35; rp.color_ramp.elements[1].position = 0.7
    nt.links.new(tx.outputs["Fac"], rp.inputs[0])
    nt.links.new(rp.outputs[0], b.inputs["Base Color"])
    return m

def wood(name="wood", c1="#8A5A36", c2="#C08A5C", scale=3.0, rough=0.45):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = mat(name, c1, rough)
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1, 18, 1)
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = scale
    wv.inputs["Distortion"].default_value = 6; wv.inputs["Detail"].default_value = 4
    rp = nt.nodes.new("ShaderNodeValToRGB")
    rp.color_ramp.elements[0].color = lin(c1); rp.color_ramp.elements[1].color = lin(c2)
    nt.links.new(tc.outputs["Object"], mp.inputs[0]); nt.links.new(mp.outputs[0], wv.inputs[0])
    nt.links.new(wv.outputs["Color"], rp.inputs[0]); nt.links.new(rp.outputs[0], b.inputs["Base Color"])
    return m

def M():
    """Product material set (created once)."""
    return dict(
        acrylic=mat("acrylic", "#FFFFFF", 0.015, trans=1.0, ior=1.49, spec=0.6),
        frost=mat("acrylic_frost", "#F2F7FF", 0.38, trans=1.0, ior=1.49),
        rim=mat("rim_polymer", "#F3F6FA", 0.32, coat=0.4),
        rim_dark=mat("rim_graphite", "#2A3242", 0.4, coat=0.3),
        alu=mat("alu", "#C9D1DC", 0.22, metal=1.0),
        gold=mat("pogo_gold", "#E2B65A", 0.2, metal=1.0),
        hub=mat("hub_white", "#F7F9FC", 0.25, coat=0.8),
        blue=mat("led_blue", BLUE, 0.3, emit=BLUE, emit_str=6),
        led=mat("led_white", "#FFFFFF", 0.3, emit="#F2FFF6", emit_str=12),
        glass_bub=mat("bubble", "#FFFFFF", 0.0, trans=1.0, ior=1.33),
        seal=mat("seal", "#1D2533", 0.6),
    )

def algae_mat(name="algae", density=1.0, glow=0.0, color=ALGAE):
    """Microalgae culture: transmissive green liquid with absorption + scattering volume
    and optional emission (LED-lit culture). Inputs re-found by name each frame."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    _set(b, "Base Color", lin(color))
    _set(b, "Roughness", 0.02)
    _set(b, "Transmission Weight", 1.0)
    _set(b, "IOR", 1.34)
    _set(b, "Emission Color", lin(ALGAE_GLOW))
    _set(b, "Emission Strength", glow)
    out = nt.nodes.get("Material Output")
    vol = nt.nodes.new("ShaderNodeVolumePrincipled"); vol.name = "vol"
    vol.inputs["Color"].default_value = lin("#46C46A")
    vol.inputs["Density"].default_value = 6 * density
    vol.inputs["Anisotropy"].default_value = 0.3
    vol.inputs["Absorption Color"].default_value = lin("#5FBF5A")
    try:
        vol.inputs["Emission Color"].default_value = lin(ALGAE_GLOW)
        vol.inputs["Emission Strength"].default_value = glow * 1.6
    except Exception:
        pass
    # organic clumps: noise-modulated density (object space)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 14; nz.inputs["Detail"].default_value = 6
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 3 * density; mr.inputs["To Max"].default_value = 10 * density
    nt.links.new(nz.outputs["Fac"], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], vol.inputs["Density"])
    nt.links.new(vol.outputs[0], out.inputs["Volume"])
    return m

# ---------------------------------------------------------------- geometry ---
def link(ob, coll=None):
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob

def mk(bm, name, m, parent=None, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    link(ob)
    if m:
        me.materials.append(m)
    if parent:
        ob.parent = parent
    return ob

def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    link(e)
    e.location, e.rotation_euler = loc, rot
    e.empty_display_size = 0.1
    if parent:
        e.parent = parent
    return e

def bevel(ob, w, segs=3, angle=40):
    b = ob.modifiers.new("bev", "BEVEL")
    b.width, b.segments = w, segs
    b.limit_method = "ANGLE"
    b.angle_limit = math.radians(angle)
    b.harden_normals = False
    return b

def hex_prism(r, z0, z1, m, name="hex", parent=None, rot_off=0.0, segs=6):
    bm = bmesh.new()
    bot = [bm.verts.new((r * math.cos(rot_off + i * 2 * math.pi / segs), r * math.sin(rot_off + i * 2 * math.pi / segs), z0)) for i in range(segs)]
    top = [bm.verts.new((v.co.x, v.co.y, z1)) for v in bot]
    bm.faces.new(bot[::-1]); bm.faces.new(top)
    for i in range(segs):
        bm.faces.new((bot[i], bot[(i + 1) % segs], top[(i + 1) % segs], top[i]))
    return mk(bm, name, m, parent)

def hex_ring_mesh(r_out, r_in, z0, z1, m, name="ring", parent=None):
    bm = bmesh.new()
    def ring(r, z):
        return [bm.verts.new((r * math.cos(i * math.pi / 3), r * math.sin(i * math.pi / 3), z)) for i in range(6)]
    ob, ot, ib, it = ring(r_out, z0), ring(r_out, z1), ring(r_in, z0), ring(r_in, z1)
    for i in range(6):
        j = (i + 1) % 6
        bm.faces.new((ob[i], ob[j], ot[j], ot[i]))          # outer wall
        bm.faces.new((it[i], it[j], ib[j], ib[i]))          # inner wall
        bm.faces.new((ot[i], ot[j], it[j], it[i]))          # top
        bm.faces.new((ib[i], ib[j], ob[j], ob[i]))          # bottom
    return mk(bm, name, m, parent)

def cyl(r, h, m, loc=(0, 0, 0), rot=(0, 0, 0), seg=48, name="cyl", parent=None, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r2 if r2 is not None else r, depth=h)
    ob = mk(bm, name, m, parent, smooth=True)
    ob.location, ob.rotation_euler = loc, rot
    ob.data.shade_auto_smooth() if hasattr(ob.data, "shade_auto_smooth") else None
    return ob

def box(sx, sy, sz, m, loc=(0, 0, 0), rot=(0, 0, 0), name="box", parent=None, bev=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
    ob = mk(bm, name, m, parent)
    ob.location, ob.rotation_euler = loc, rot
    if bev:
        bevel(ob, bev, 3)
    return ob

def sphere(r, m, loc=(0, 0, 0), name="sph", parent=None, seg=16):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)
    ob = mk(bm, name, m, parent, smooth=True)
    ob.location = loc
    return ob

def torus_ring(R_, r, m, loc=(0, 0, 0), name="torus", parent=None, seg=64):
    bpy.ops.mesh.primitive_torus_add(major_radius=R_, minor_radius=r, major_segments=seg, minor_segments=12, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    if parent:
        ob.parent = parent
    return ob

# ------------------------------------------------------------ ALGORA module --
def hex_module(name="ALG", loc=(0, 0, 0), rot=(0, 0, 0), parent=None, culture=None, led_on=True,
               rim_m=None, bubbles=10, seed=0, detail=True, bottom="frost"):
    """One ALGORA module, lying in local XY (top face +Z).
       Layers (bottom->top): frosted/clear acrylic sheet, culture chamber with 6 radial
       baffles + AIoT core hub, clear acrylic top sheet, polymer rim with 6 connector pads
       (magnetic pogo + fluid quick-connect). Returns the root empty."""
    mm = M()
    rim_m = rim_m or mm["rim"]
    culture = culture or algae_mat()
    d, rim, sh = DIM["depth"] * MM, DIM["rim"] * MM, DIM["sheet"] * MM
    root = empty(name, loc, rot, parent)
    h = d / 2
    # frame
    fr = hex_ring_mesh(R, R - rim * 2 / math.sqrt(3), -h, h, rim_m, name + "_rim", root)
    bevel(fr, 0.0025, 3)
    # acrylic sheets
    ri = R - rim * 2 / math.sqrt(3) + 0.0035
    top = hex_prism(ri, h - sh, h + 0.0004, mm["acrylic"], name + "_top", root)
    bevel(top, 0.0012, 2)
    bot = hex_prism(ri, -h - 0.0004, -h + sh, mm[bottom], name + "_bot", root)
    # culture volume (slightly inset so faces don't coincide)
    cul = hex_prism(ri - 0.0012, -h + sh + 0.0006, h - sh - 0.0006, culture, name + "_culture", root)
    # AIoT core hub (through the culture, top cap visible above top sheet)
    hub_r, hub_h = DIM["hub_r"] * MM, DIM["hub_h"] * MM
    cyl(hub_r, d + 0.006, mm["hub"], (0, 0, 0.003), name=name + "_hub", parent=root, seg=64)
    if detail:
        torus_ring(hub_r * 0.78, 0.0018, mm["blue"] if led_on else mm["alu"], (0, 0, h + 0.0062), name + "_hubled", root, 64)
        sphere(hub_r * 0.5, mm["hub"], (0, 0, h + 0.0035), name + "_dome", root, 32).scale = (1, 1, 0.35)
        # radial baffles
        for k in range(6):
            a = k * math.pi / 3 + math.pi / 6
            L = (F / 2 - rim) - hub_r - 0.004
            c = hub_r + 0.002 + L / 2
            b = box(L * 0.82, 0.002, d - 2 * sh - 0.002, mm["acrylic"], (math.cos(a) * (hub_r + L * 0.41 + 0.002), math.sin(a) * (hub_r + L * 0.41 + 0.002), 0),
                    (0, 0, a), name + "_baffle", root)
        # connector pads on each of 6 side faces (flat-top: side normals at 30deg + k*60)
        apo = F / 2
        for k in range(6):
            a = math.radians(30 + 60 * k)
            n = Vector((math.cos(a), math.sin(a), 0))
            t = Vector((-n.y, n.x, 0))
            p = n * (apo + 0.0004)
            pad = box(0.0012, DIM["port_w"] * MM, d * 0.55, mm["rim_dark"], p, (0, 0, a), name + "_pad", root, bev=0.0004)
            for s in (-1, 1):  # pogo pins
                q = p + t * s * 0.016 + n * 0.0008
                cyl(0.0022, 0.0016, mm["gold"], q, (0, math.pi / 2, a), name=name + "_pogo", parent=root, seg=16)
            cyl(0.0042, 0.0018, mm["alu"], p + n * 0.0009, (0, math.pi / 2, a), name=name + "_port", parent=root, seg=24)
        # inner LED strip just inside the rim (lights the culture edge-on)
        if led_on:
            hex_ring_mesh(ri - 0.0005, ri - 0.0030, -0.003, 0.003, mm["led"], name + "_ledstrip", root)
    # bubbles from the hub diffuser
    rnd = random.Random(seed)
    for i in range(bubbles):
        a = rnd.uniform(0, 2 * math.pi); r = rnd.uniform(hub_r + 0.01, F / 2 - rim - 0.01)
        sphere(rnd.uniform(0.0015, 0.0042), mm["glass_bub"], (r * math.cos(a), r * math.sin(a), rnd.uniform(-h + sh + 0.006, h - sh - 0.006)),
               name + "_bub", root, 10)
    return root

def honeycomb(cells, parent=None, prefix="A", **kw):
    out = []
    for i, (q, r) in enumerate(cells):
        x, y = axial(q, r)
        out.append(hex_module(f"{prefix}{i:02d}", (x, y, 0), parent=parent, seed=i, **kw))
    return out

# ------------------------------------------------------------ GLB importer ---
def import_glb(key, loc=(0, 0, 0), rot_z=0.0, height=None, width=None, name=None, drop=(), scale=None):
    """Import assets/sketchfab/<key>.glb (or gltf folder), normalise: base on z=0, centred XY,
    scaled to `height` (m) or `width` (m). Returns the root empty."""
    path = os.path.join(SF, key + ".glb")
    if not os.path.exists(path):
        g = glob.glob(os.path.join(SF, key, "**", "*.gltf"), recursive=True)
        if not g:
            print("MISSING asset", key); return None
        path = g[0]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    for o in list(new):
        if any(d.lower() in o.name.lower() for d in drop):
            new.remove(o); bpy.data.objects.remove(o, do_unlink=True)
    root = empty(name or ("SF_" + key))
    tops = [o for o in new if o.parent is None]
    for o in tops:
        o.parent = root
    bpy.context.view_layer.update()
    pts = []
    for o in new:
        if o.type == "MESH":
            pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    if not pts:
        return root
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    size = mx - mn
    s = scale or 1.0
    if scale:
        pass
    elif height:
        s = height / max(size.z, 1e-6)
    elif width:
        s = width / max(size.x, size.y, 1e-6)
    ctr = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
    for o in tops:
        o.matrix_world = Matrix.Translation(-ctr) @ o.matrix_world
    root.scale = (s, s, s)
    root.location = loc
    root.rotation_euler = (0, 0, rot_z)
    for o in new:  # hide imported empties/bones from render clutter
        if o.type == "MESH":
            o.visible_shadow = True
    return root

# ------------------------------------------------------------------ human ----
def make_human(outfit="male_casualsuit03", hair="short02", skin="young_asian_male", shoes="shoes02",
               gender=1.0, age=0.5, height=0.55, muscle=0.55, weight=0.5, name="Person"):
    """MPFB (MakeHuman, CC0) body + Rigify: metarig 'rigify.human' -> clothes -> rigify_generate
    -> meshes re-targeted to the generated control rig. Returns (basemesh, rig)."""
    import addon_utils
    addon_utils.enable("rigify", default_set=True)
    addon_utils.enable("bl_ext.user_default.mpfb", default_set=True)
    from bl_ext.user_default.mpfb.services.humanservice import HumanService
    from bl_ext.user_default.mpfb.services.targetservice import TargetService
    from bl_ext.user_default.mpfb.entities.rigging.rigifyhelpers.rigifyhelpers import RigifyHelpers
    MH = os.path.join(os.environ.get("APPDATA", ""), "Blender Foundation", "Blender", "5.2", "extensions", ".user", "user_default", "mpfb", "data")

    def mh(kind, nm, ext):
        f = glob.glob(os.path.join(MH, kind, nm, "*" + ext)) or glob.glob(os.path.join(MH, kind, nm, "**", "*" + ext), recursive=True)
        return f[0] if f else None

    macro = TargetService.get_default_macro_info_dict()
    macro["gender"], macro["age"], macro["height"], macro["muscle"], macro["weight"] = gender, age, height, muscle, weight
    macro["race"] = {"african": 0.1, "asian": 0.8, "caucasian": 0.1}
    base = HumanService.create_human(macro_detail_dict=macro, scale=0.1)   # 1 unit = 1 m
    f = mh("skins", skin, ".mhmat")
    if f:
        HumanService.set_character_skin(f, base, skin_type="MAKESKIN")
    meta = HumanService.add_builtin_rig(base, "rigify.human")
    for kind, nm in (("eyes", "high-poly"), ("eyebrows", "eyebrow001"), ("eyelashes", "eyelashes02"),
                     ("hair", hair), ("clothes", outfit), ("clothes", shoes)):
        f = mh(kind, nm, ".mhclo") if nm else None
        if f:
            atype = {"eyes": "Eyes", "eyebrows": "Eyebrows", "eyelashes": "Eyelashes", "hair": "Hair"}.get(kind, "Clothes")
            try:
                HumanService.add_mhclo_asset(f, base, asset_type=atype, subdiv_levels=1)
            except Exception as e:
                print("asset fail", nm, e)
    # --- Rigify generate (Blender's rigging add-on) ---
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = meta
    meta.select_set(True)
    meta.data.rigify_rig_basename = name + "_rig"
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.pose.rigify_generate()
    rig = bpy.context.active_object
    RigifyHelpers.adjust_children_for_rigify(rig, meta)
    meta.hide_viewport = meta.hide_render = True
    rig.hide_render = True
    bpy.ops.object.mode_set(mode="OBJECT")
    # all limbs on IK so we can pose by placing hands/feet
    for pb in rig.pose.bones:
        if "IK_FK" in pb.keys():
            pb["IK_FK"] = 0.0
        if "IK_Stretch" in pb.keys():
            pb["IK_Stretch"] = 0.0
    return base, rig

def bone_world(rig, bone):
    return rig.matrix_world @ rig.pose.bones[bone].head

def place_bone(rig, bone, world_pos, world_rot=None):
    """Move a rigify control (e.g. hand_ik.L, foot_ik.R, torso) to a world position."""
    pb = rig.pose.bones.get(bone)
    if not pb:
        print("no bone", bone); return
    bpy.context.view_layer.update()
    Mw = rig.matrix_world @ pb.matrix
    rot = world_rot.to_matrix().to_4x4() if world_rot is not None else Mw.to_3x3().normalized().to_4x4()
    target = Matrix.Translation(Vector(world_pos)) @ rot
    pb.matrix = rig.matrix_world.inverted() @ target
    bpy.context.view_layer.update()

def key_bones(rig, frame, bones):
    for b in bones:
        pb = rig.pose.bones.get(b)
        if pb:
            pb.keyframe_insert("location", frame=frame)
            pb.keyframe_insert("rotation_quaternion" if pb.rotation_mode == "QUATERNION" else "rotation_euler", frame=frame)

def render_still(path):
    sc = bpy.context.scene
    sc.render.filepath = os.path.abspath(path)
    bpy.ops.render.render(write_still=True)
    print("WROTE", path)

def args():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

def thin_glass(name="thin_glass", tint="#FFFFFF", gloss=0.03, fres=1.45):
    """Transparent + Glossy mixed by Fresnel: lets light through for shadows (no caustics needed)."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    out = nt.nodes.get("Material Output")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); tr.inputs[0].default_value = lin(tint)
    gl = nt.nodes.new("ShaderNodeBsdfGlossy"); gl.inputs["Roughness"].default_value = gloss
    fr = nt.nodes.new("ShaderNodeFresnel"); fr.inputs["IOR"].default_value = fres
    mx = nt.nodes.new("ShaderNodeMixShader")
    # Fresnel on a backface = total internal reflection -> black panes; zero it on backfaces
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    nt.links.new(geo.outputs["Backfacing"], inv.inputs[1])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    nt.links.new(fr.outputs[0], mul.inputs[0]); nt.links.new(inv.outputs[0], mul.inputs[1])
    nt.links.new(mul.outputs[0], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    return m

def algae_thin(name="algae_thin", tint="#2FAE4E", glow=0.3, density=0.55):
    """Culture as a tinted see-through layer: casts green light (roof / daylight shots)."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    out = nt.nodes.get("Material Output")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 12; nz.inputs["Detail"].default_value = 5
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    rp = nt.nodes.new("ShaderNodeValToRGB")
    rp.color_ramp.elements[0].color = lin(tint); rp.color_ramp.elements[1].color = lin("#7FE08F")
    nt.links.new(nz.outputs["Fac"], rp.inputs[0])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); nt.links.new(rp.outputs[0], tr.inputs[0])
    df = nt.nodes.new("ShaderNodeBsdfDiffuse"); df.inputs[0].default_value = lin("#1E8A3E")
    em = nt.nodes.new("ShaderNodeEmission"); em.name = "em"; em.inputs[0].default_value = lin(ALGAE_GLOW); em.inputs[1].default_value = glow
    m1 = nt.nodes.new("ShaderNodeMixShader"); m1.inputs[0].default_value = density
    nt.links.new(tr.outputs[0], m1.inputs[1]); nt.links.new(df.outputs[0], m1.inputs[2])
    ad = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(m1.outputs[0], ad.inputs[0]); nt.links.new(em.outputs[0], ad.inputs[1])
    nt.links.new(ad.outputs[0], out.inputs["Surface"])
    return m

def daylight_modules(prefix):
    """Swap module glass/culture to shadow-friendly thin materials (for sun-lit scenes)."""
    tg = thin_glass()
    at = algae_thin("algae_thin", "#2FAE4E", glow=0.35, density=0.5)
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith(prefix):
            continue
        if o.name.endswith(("_top", "_bot")) or "_baffle" in o.name:
            o.data.materials.clear(); o.data.materials.append(tg)
        elif o.name.endswith("_culture"):
            o.data.materials.clear(); o.data.materials.append(at)
        elif "_bub" in o.name:
            o.hide_render = True
