"""Original procedural arcade cabinet (Blender 5, headless) for the Scratch game-studio classroom site.
Parts are separate named objects so Three.js can drive them:
  Screen (UV 0-1, replace its emissive texture), Marquee, Joystick (pivot at base), Button_A/B/C/Start (pivot at base),
  CartSlot, CoinDoor.  Y-up export, metres, front faces +Z.  License: original geometry, CC0.
"""
import bpy, bmesh, math, json
from pathlib import Path
from mathutils import Vector

out = Path("outputs"); out.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

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
BODY2 = mat("body_panel", (.14, .12, .42, 1), .1, .45)
BLACK = mat("black_trim", (.02, .02, .04, 1), .2, .5)
CHROME = mat("chrome", (.85, .86, .9, 1), 1.0, .18)
PINK = mat("neon_pink", (1, .2, .6, 1), 0, .3, (1, .2, .6, 1), 3.5)
CYAN = mat("neon_cyan", (.2, .9, 1, 1), 0, .3, (.2, .9, 1, 1), 3.5)
YEL = mat("neon_yellow", (1, .8, .15, 1), 0, .3, (1, .8, .15, 1), 3.0)
RED = mat("red", (.9, .12, .12, 1), 0, .25, (.9, .12, .12, 1), .6)
BLUE = mat("blue", (.15, .4, .95, 1), 0, .25, (.15, .4, .95, 1), .6)
GREEN = mat("green", (.15, .8, .3, 1), 0, .25, (.15, .8, .3, 1), .6)
SCREEN = mat("screen", (.02, .03, .08, 1), 0, .15, (.1, .15, .35, 1), 1.2)
MARQ = mat("marquee", (.1, .05, .2, 1), 0, .3, (.9, .5, .1, 1), 2.0)
STEEL = mat("steel_dark", (.15, .15, .18, 1), .8, .35)

def bevel(o, w=.012, seg=2):
    m = o.modifiers.new("bevel", 'BEVEL'); m.width = w; m.segments = seg; m.limit_method = 'ANGLE'
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.modifier_apply(modifier="bevel"); o.select_set(False)

def box(name, size, loc, m, bev=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(m)
    if bev: bevel(o, bev)
    bpy.ops.object.shade_smooth()
    return o

def cyl(name, r, h, loc, m, rot=(0, 0, 0), verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=verts, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o

def set_origin(o, point):
    bpy.context.scene.cursor.location = point
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR'); o.select_set(False)

# ---------- Side profile (Y = depth, Z = height) extruded along X: classic upright cabinet ----------
W = 0.76                       # cabinet width (x)
prof = [  # (y, z): front is -Y in Blender -> becomes +Z after Y-up export
    (0.00, 0.00), (0.80, 0.00), (0.80, 1.70), (0.62, 1.86), (0.34, 1.86), (0.34, 1.60), (0.02, 1.52),   # top & screen recess slope
    (-0.02, 1.52), (-0.20, 1.52), (-0.28, 1.00), (-0.28, 0.12), (-0.18, 0.12), (-0.18, 0.00)]
prof = [(-y + 0.0, z) for (y, z) in prof]  # flip so the front faces -Y (Blender front) => glTF +Z
bm = bmesh.new()
vs = [bm.verts.new((-W / 2, y, z)) for (y, z) in prof]
f = bm.faces.new(vs)
res = bmesh.ops.extrude_face_region(bm, geom=[f])
verts = [v for v in res['geom'] if isinstance(v, bmesh.types.BMVert)]
bmesh.ops.translate(bm, verts=verts, vec=(W, 0, 0))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new("CabinetBody"); bm.to_mesh(me); bm.free()
body = bpy.data.objects.new("CabinetBody", me); bpy.context.collection.objects.link(body)
body.data.materials.append(BODY)
bevel(body, .015, 3)
bpy.context.view_layer.objects.active = body; bpy.ops.object.shade_smooth()

# Side art: diagonal neon stripes + stars on both flanks
for sx in (-1, 1):
    x = sx * (W / 2 + 0.004)
    for i, (m, y0) in enumerate([(PINK, -0.38), (CYAN, -0.52), (YEL, -0.66)]):
        s = box(f"SideStripe{sx}_{i}", (0.004, 0.55, 0.035), (x, y0 * -1 - 0.5, 1.0 + i * 0.0), m, 0, (math.radians(38 * sx * 0 + 38), 0, 0))
        s.location = (x, -0.35 - i * 0.0, 0.55 + i * 0.07)
        s.rotation_euler = (math.radians(52), 0, 0)
    for k in range(6):
        st = box(f"Star{sx}_{k}", (0.004, 0.035, 0.035), (x, -0.25 - (k % 3) * 0.17, 1.2 + (k // 3) * 0.28), YEL, 0, (0, 0, math.radians(45)))

# ---------- Front: kick plate, coin door, control panel, bezel, screen, marquee ----------
FY = -0.28                      # front plane (y)
box("KickPlate", (W - .02, .02, .1), (0, FY - .005, .06), STEEL, .004)
door = box("CoinDoor", (.30, .03, .36), (0, FY - .012, .50), BLACK, .008)
for i, x in enumerate((-.07, .07)):
    box(f"CoinSlot{i}", (.06, .012, .015), (x, FY - .032, .58), RED, 0)
    cyl(f"CoinBtn{i}", .028, .014, (x, FY - .034, .50), CHROME, rot=(math.radians(90), 0, 0))
box("CartSlotFrame", (.50, .035, .09), (0, FY - .014, .26), STEEL, .006)
slot = box("CartSlot", (.42, .02, .035), (0, FY - .034, .26), BLACK, .004)
box("CartSlotGlow", (.40, .004, .008), (0, FY - .045, .295), CYAN, 0)

# control panel (tilted slab)
cp = box("ControlPanel", (W - .04, .34, .05), (0, FY - .12, 1.025), BODY2, .01, (math.radians(-18), 0, 0))
cp.location = (0, FY - .10, 1.03)
cp_top = 1.03 + .027
box("PanelTrim", (W - .02, .02, .02), (0, FY - .27, .965), PINK, 0, (math.radians(-18), 0, 0))
# joystick: base plate, shaft, ball (pivot at base for animation)
base_c = Vector((-.2, FY - .10, cp_top + .006))
cyl("JoyBase", .05, .012, base_c, STEEL, rot=(math.radians(-18), 0, 0))
shaft = cyl("JoyShaft", .009, .13, (base_c.x, base_c.y, base_c.z + .065), CHROME, verts=16)
ball = bpy.data.objects.new("x", None)
bpy.ops.mesh.primitive_uv_sphere_add(radius=.034, location=(base_c.x, base_c.y, base_c.z + .145), segments=32, ring_count=16)
ballo = bpy.context.object; ballo.name = "JoyBall"; ballo.data.materials.append(RED); bpy.ops.object.shade_smooth()
bpy.ops.object.select_all(action='DESELECT'); shaft.select_set(True); ballo.select_set(True)
bpy.context.view_layer.objects.active = shaft; bpy.ops.object.join(); shaft.name = "Joystick"
set_origin(shaft, base_c)
# buttons (pivot at base)
def button(name, x, dy, m):
    c = Vector((x, FY - .10 + dy, cp_top + .004))
    b = cyl(name, .026, .022, (c.x, c.y, c.z + .011), m, verts=32)
    cyl(name + "_ring", .031, .008, (c.x, c.y, c.z + .002), STEEL, verts=32)
    set_origin(b, c); return b
button("Button_A", .02, .045, RED); button("Button_B", .09, .02, BLUE); button("Button_C", .16, -.005, GREEN)
button("Button_Start", .27, .06, YEL)

# bezel + screen
box("Bezel", (W - .06, .10, .56), (0, FY + .17, 1.52), BLACK, .01, (math.radians(-18), 0, 0))
bezel = bpy.data.objects["Bezel"]; bezel.location = (0, -0.06, 1.55)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -0.06 - .063, 1.55), rotation=(math.radians(90 - 18), 0, 0))
scr = bpy.context.object; scr.name = "Screen"; scr.scale = (.56, .42, 1); bpy.ops.object.transform_apply(scale=True)
scr.data.materials.append(SCREEN)
# marquee header
mq = box("Marquee", (W - .08, .05, .20), (0, FY - .02 + .28, 1.76), MARQ, .006)
mq.location = (0, -0.46, 1.78)
box("MarqueeFrame", (W - .03, .12, .24), (0, -0.44, 1.78), BLACK, .008)
# speaker grille on top front
for i in range(7):
    box(f"Grille{i}", (.05, .01, .012), (-.15 + i * .05, -0.28, 1.43), BLACK, 0)
# T-molding (front vertical edges) + feet
for sx in (-1, 1):
    box(f"TMold{sx}", (.016, .02, 1.40), (sx * (W / 2), FY - .004, .84), CYAN, .004)
    box(f"Foot{sx}", (.08, .08, .035), (sx * .30, -.55, .018), STEEL, .01)
    box(f"Foot_b{sx}", (.08, .08, .035), (sx * .30, -.05, .018), STEEL, .01)
# neon under-glow strip
box("GlowStrip", (W - .1, .01, .015), (0, FY - .02, .115), PINK, 0)

# ---------- Cleanup, export ----------
for o in bpy.data.objects:
    if o.type == 'EMPTY' or o.name == 'x': bpy.data.objects.remove(o)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.save_as_mainfile(filepath=str((out / "arcade_cabinet.blend").resolve()))
bpy.ops.export_scene.gltf(filepath=str((out / "arcade_cabinet.glb").resolve()), export_format='GLB', export_apply=True, export_yup=True, export_cameras=False, export_lights=False)
names = sorted(o.name for o in bpy.data.objects if o.type == 'MESH')
(out / "report.json").write_text(json.dumps({"blender_version": bpy.app.version_string, "objects": names, "note": "visual review required"}, indent=2), encoding="utf-8")
(out / "asset_manifest.json").write_text(json.dumps({
    "schema_version": 1, "asset_id": "arcade_cabinet", "format": "glTF 2.0 GLB", "source": "original procedural Blender script",
    "unit": "meter", "coordinate_system": "Blender Z-up; glTF export converts to Y-up; front faces +Z",
    "model_file": "arcade_cabinet.glb", "source_file": "arcade_cabinet.blend", "clips": [], "min_animation_count": 0,
    "requirements": {"skins": False, "animated": False, "visual_review": True},
    "license_note": "Original geometry (CC0). Named parts: Screen, Marquee, Joystick, Button_A/B/C/Start, CartSlot, CoinDoor."}, indent=2), encoding="utf-8")
print("ARCADE_CABINET_OK", len(names))
