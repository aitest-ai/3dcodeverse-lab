"""Original procedural arcade cabinet (Blender 5, headless) for the Scratch game-studio classroom site.
All geometry is built with bmesh (no context-dependent operators) so the result is deterministic.
Axes while modelling: X width, Y depth (front = -Y), Z up.  glTF export converts to Y-up, front faces +Z.
Named parts: Screen (UV 0-1), Marquee, Joystick, Button_A/B/C/Start (pivot at base), CartSlot, CoinDoor.
License: original geometry (CC0).
"""
import bpy, bmesh, math, json
from pathlib import Path
from mathutils import Vector, Matrix, Euler

out = Path("outputs"); out.mkdir(parents=True, exist_ok=True)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)

def mat(name, color, metal=0.0, rough=0.5, emit=None, strength=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = color
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = emit
        b.inputs["Emission Strength"].default_value = strength
    m.diffuse_color = color
    return m

BODY = mat("body_navy", (.09, .08, .30, 1), .15, .38)
BODY2 = mat("body_panel", (.16, .13, .45, 1), .1, .45)
BLACK = mat("black_trim", (.02, .02, .04, 1), .2, .5)
CHROME = mat("chrome", (.85, .86, .9, 1), 1.0, .18)
PINK = mat("neon_pink", (1, .2, .6, 1), 0, .3, (1, .2, .6, 1), 3.5)
CYAN = mat("neon_cyan", (.2, .9, 1, 1), 0, .3, (.2, .9, 1, 1), 3.5)
YEL = mat("neon_yellow", (1, .8, .15, 1), 0, .3, (1, .8, .15, 1), 3.0)
RED = mat("red", (.9, .12, .12, 1), 0, .25, (.9, .12, .12, 1), .6)
BLUE = mat("blue", (.15, .4, .95, 1), 0, .25, (.15, .4, .95, 1), .6)
GREEN = mat("green", (.15, .8, .3, 1), 0, .25, (.15, .8, .3, 1), .6)
SCREEN = mat("screen", (.02, .03, .08, 1), 0, .15, (.1, .15, .35, 1), 1.2)
MARQ = mat("marquee", (.1, .05, .2, 1), 0, .3, (.9, .5, .1, 1), 0.8)
STEEL = mat("steel_dark", (.15, .15, .18, 1), .8, .35)

def make(name, bm, m, loc=(0, 0, 0), smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.data.materials.append(m)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    return o

def bevel_mod(o, w=.01, seg=2):
    md = o.modifiers.new("bevel", 'BEVEL'); md.width = w; md.segments = seg; md.limit_method = 'ANGLE'; md.angle_limit = math.radians(35)

def box(name, size, center, m, bev=0.0, rx=0.0, pivot=None):
    """Axis box (size) rotated by rx about X, centred at `center` (world). pivot -> object origin placed there."""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    R = Matrix.Rotation(rx, 4, 'X')
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bmesh.ops.transform(bm, matrix=R, verts=bm.verts)
    c = Vector(center); p = Vector(pivot) if pivot is not None else c
    bmesh.ops.translate(bm, vec=c - p, verts=bm.verts)
    o = make(name, bm, m, p, smooth=False)
    if bev: bevel_mod(o, bev)
    return o

def cyl(name, r, h, center, m, rx=0.0, verts=32, pivot=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r, depth=h)
    bmesh.ops.transform(bm, matrix=Matrix.Rotation(rx, 4, 'X'), verts=bm.verts)
    c = Vector(center); p = Vector(pivot) if pivot is not None else c
    bmesh.ops.translate(bm, vec=c - p, verts=bm.verts)
    return make(name, bm, m, p)

def sphere(name, r, center, m, pivot=None):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=r)
    c = Vector(center); p = Vector(pivot) if pivot is not None else c
    bmesh.ops.translate(bm, vec=c - p, verts=bm.verts)
    return make(name, bm, m, p)

W = 0.76
HW = W / 2
# ---------- body: side profile (y, z) extruded along X.  Front is -Y. ----------
prof = [(0.57, 0.0), (0.57, 1.92), (-0.30, 1.92), (-0.30, 1.70), (0.00, 1.66),     # back, top, marquee, recess top
        (-0.16, 1.12), (-0.40, 1.03), (-0.40, 0.98), (-0.30, 0.96), (-0.30, 0.10),   # screen slope, control panel, front
        (-0.24, 0.10), (-0.24, 0.0)]
bm = bmesh.new()
vs = [bm.verts.new((-HW, y, z)) for (y, z) in prof]
f = bm.faces.new(vs)
res = bmesh.ops.extrude_face_region(bm, geom=[f])
nv = [v for v in res['geom'] if isinstance(v, bmesh.types.BMVert)]
bmesh.ops.translate(bm, vec=(W, 0, 0), verts=nv)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
body = make("CabinetBody", bm, BODY, smooth=False)
bevel_mod(body, .014, 3)

# helpers on the sloped surfaces
scr_top = Vector((0.00, 1.66)); scr_bot = Vector((-0.16, 1.12))
st = (scr_bot - scr_top).normalized()
sn = Vector((-abs(st.y), abs(st.x)))
th_s = math.asin(abs(sn.x))        # plane normal (0,-sin,cos)
pan_a = Vector((-0.16, 1.12)); pan_b = Vector((-0.40, 1.03))
pt = (pan_b - pan_a).normalized(); pn = Vector((-abs(pt.y), abs(pt.x)))
th_p = math.asin(abs(pn.x))
def on_panel(x, s, lift=0.0):
    yz = pan_a + pt * s + pn * lift
    return (x, yz.x, yz.y)

# screen glass + black bezel just in front of the recess
cen = (scr_top + scr_bot) / 2; slen = (scr_top - scr_bot).length
bez = box("Bezel", (W - .06, slen + .06, .012), (0, (cen - sn * .004).x, (cen - sn * .004).y), BLACK, 0, rx=th_s)
sc = cen + sn * .008
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=.5)
uv = bm.loops.layers.uv.verify()
for l in [l for fc in bm.faces for l in fc.loops]:
    v = l.vert.co; l[uv].uv = (v.x + .5, v.y + .5)
bmesh.ops.scale(bm, vec=Vector((W - .16, slen - .06, 1)), verts=bm.verts)
bmesh.ops.transform(bm, matrix=Matrix.Rotation(th_s, 4, 'X'), verts=bm.verts)
screen = make("Screen", bm, SCREEN, (0, sc.x, sc.y), smooth=False)

# marquee (lit header) + frame
box("MarqueeFrame", (W - .02, .02, .26), (0, -0.305, 1.81), BLACK, .006)
box("Marquee", (W - .12, .01, .19), (0, -0.32, 1.81), MARQ, .003)
# side art: diagonal neon stripes + stars on both flanks
for sx in (-1, 1):
    x = sx * (HW + .003)
    for i, m in enumerate([PINK, CYAN, YEL]):
        box(f"SideStripe{sx}_{i}", (.006, .75, .045), (x, .10, .38 + i * .085), m, 0, rx=math.radians(38))
    for k in range(6):
        box(f"Star{sx}_{k}", (.006, .05, .05), (x, -.12 + (k % 3) * .20, 1.25 + (k // 3) * .30), YEL, 0, rx=math.radians(45))
# front lower: coin door, cartridge slot, kick plate, glow strip
box("KickPlate", (W - .02, .02, .10), (0, -0.25, .05), STEEL, .004)
box("CoinDoor", (.30, .02, .34), (0, -0.31, .60), BLACK, .006)
for i, x in enumerate((-.07, .07)):
    box(f"CoinSlot{i}", (.06, .012, .016), (x, -0.325, .68), RED)
    cyl(f"CoinBtn{i}", .028, .014, (x, -0.325, .58), CHROME, rx=math.radians(90))
box("CartSlotFrame", (.50, .03, .10), (0, -0.31, .30), STEEL, .006)
box("CartSlot", (.42, .02, .04), (0, -0.325, .30), BLACK, .004)
box("CartSlotGlow", (.40, .004, .008), (0, -0.337, .335), CYAN)
box("GlowStrip", (W - .1, .008, .014), (0, -0.30, .14), PINK)
for sx in (-1, 1):
    box(f"TMold{sx}", (.016, .018, .84), (sx * HW, -0.30, .53), CYAN, .004)
# speaker grille under marquee
for i in range(7):
    box(f"Grille{i}", (.05, .01, .012), (-.15 + i * .05, -0.30, 1.775), BLACK)
# control panel top trim
box("PanelTrim", (W - .02, .02, .02), (0, -0.40, 1.0), PINK, .004)
# joystick (pivot at base, tilt-able) + buttons
jb = Vector(on_panel(-.20, .12))
cyl("JoyBase", .05, .012, on_panel(-.20, .12, .006), STEEL, rx=th_p)
shaft_c = Vector(on_panel(-.20, .12, .075)); ball_c = Vector(on_panel(-.20, .12, .15))
# joystick = shaft + ball in one mesh, origin at its base
jy = bmesh.new()
bmesh.ops.create_cone(jy, cap_ends=True, segments=16, radius1=.009, radius2=.009, depth=.14)
bmesh.ops.translate(jy, vec=(0, 0, .07), verts=jy.verts)
s2 = bmesh.new(); bmesh.ops.create_uvsphere(s2, u_segments=24, v_segments=12, radius=.034); bmesh.ops.translate(s2, vec=(0, 0, .15), verts=s2.verts)
me_s = bpy.data.meshes.new("tmp_ball"); s2.to_mesh(me_s); s2.free()
jy.from_mesh(me_s); bpy.data.meshes.remove(me_s)
bmesh.ops.transform(jy, matrix=Matrix.Rotation(th_p, 4, 'X'), verts=jy.verts)
joy = make("Joystick", jy, RED, jb)
for i, (x, s, m, nme) in enumerate([(.02, .05, RED, "Button_A"), (.10, .075, BLUE, "Button_B"), (.18, .10, GREEN, "Button_C"), (.29, .03, YEL, "Button_Start")]):
    base = Vector(on_panel(x, s))
    cyl(nme + "_ring", .031, .008, on_panel(x, s, .004), STEEL, rx=th_p)
    cyl(nme, .026, .022, on_panel(x, s, .011), m, rx=th_p, pivot=base)
# feet
for sx in (-1, 1):
    for yy in (-.05, .45):
        box(f"Foot{sx}_{yy}", (.08, .08, .02), (sx * .30, yy, .0), STEEL, .008)

# ---------- export + diagnostics ----------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.save_as_mainfile(filepath=str((out / "arcade_cabinet.blend").resolve()))
bpy.ops.export_scene.gltf(filepath=str((out / "arcade_cabinet.glb").resolve()), export_format='GLB', export_apply=True, export_yup=True)
diag = {}
dg = bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type != 'MESH': continue
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    diag[o.name] = [[round(min(p[i] for p in pts), 3) for i in range(3)], [round(max(p[i] for p in pts), 3) for i in range(3)]]
(out / "report.json").write_text(json.dumps({"blender_version": bpy.app.version_string, "bounds_blender_zup": diag, "note": "visual review required"}, indent=2), encoding="utf-8")
(out / "asset_manifest.json").write_text(json.dumps({
    "schema_version": 1, "asset_id": "arcade_cabinet", "format": "glTF 2.0 GLB", "source": "original procedural Blender script (bmesh)",
    "unit": "meter", "coordinate_system": "Blender Z-up; glTF export converts to Y-up; front faces +Z",
    "model_file": "arcade_cabinet.glb", "source_file": "arcade_cabinet.blend", "clips": [], "min_animation_count": 0,
    "requirements": {"skins": False, "animated": False, "visual_review": True},
    "license_note": "Original geometry (CC0). Named parts: Screen, Marquee, Joystick, Button_A/B/C/Start, CartSlot, CoinDoor."}, indent=2), encoding="utf-8")
print("ARCADE_CABINET_OK", len(diag))
