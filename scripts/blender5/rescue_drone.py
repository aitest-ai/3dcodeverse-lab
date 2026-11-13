"""Rescue Drone - original procedural quadcopter (Blender 5.x, headless).
Original geometry written for this repo; no external assets.
Outputs: outputs/rescue_drone.blend/.glb, asset_manifest.json, report.json, preview*.png
Node names: Body, Gimbal, Prop_FL/FR/BL/BR (origin = rotor hub, spin around local Z in Blender / Y in glTF),
            LED_*, Hook. Front of the drone points to Blender -Y (glTF +Z).
"""
import bpy, bmesh, math, json
from pathlib import Path
from mathutils import Vector

out = Path("outputs"); out.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ---------- helpers ----------
def mat(name, color, metal=0.0, rough=0.5, emit=None, emit_k=0.0, coat=0.0, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if coat and "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = coat
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = emit_k
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        try: m.blend_method = 'BLEND'
        except Exception: pass
    return m

M = {
    "shell": mat("Shell_White", (0.93, 0.95, 0.97), 0.0, 0.28, coat=0.8),
    "orange": mat("Rescue_Orange", (1.0, 0.36, 0.06), 0.0, 0.32, coat=0.6),
    "carbon": mat("Carbon", (0.045, 0.05, 0.06), 0.35, 0.38),
    "metal": mat("Motor_Metal", (0.55, 0.57, 0.6), 1.0, 0.28),
    "rubber": mat("Rubber", (0.02, 0.02, 0.022), 0.0, 0.85),
    "glass": mat("Lens_Glass", (0.01, 0.03, 0.06), 0.0, 0.05, emit=(0.1, 0.5, 1.0), emit_k=0.6),
    "red": mat("Cross_Red", (0.9, 0.06, 0.05), 0.0, 0.4),
    "prop": mat("Prop_Gray", (0.12, 0.13, 0.15), 0.0, 0.45),
    "ledg": mat("LED_Green", (0.1, 1.0, 0.35), 0.0, 0.3, emit=(0.1, 1.0, 0.35), emit_k=6),
    "ledr": mat("LED_Red", (1.0, 0.1, 0.08), 0.0, 0.3, emit=(1.0, 0.1, 0.08), emit_k=6),
    "light": mat("Light_Bar", (1, 1, 0.95), 0.0, 0.3, emit=(1, 0.98, 0.9), emit_k=8),
}

def finish(o, material, bevel=None, subsurf=0, smooth=True):
    o.data.materials.clear(); o.data.materials.append(material)
    bpy.context.view_layer.objects.active = o
    if bevel:
        md = o.modifiers.new("Bevel", 'BEVEL'); md.width = bevel; md.segments = 4; md.limit_method = 'ANGLE'
        bpy.ops.object.modifier_apply(modifier=md.name)
    if subsurf:
        md = o.modifiers.new("Sub", 'SUBSURF'); md.levels = subsurf; md.render_levels = subsurf
        bpy.ops.object.modifier_apply(modifier=md.name)
    if smooth:
        for p in o.data.polygons: p.use_smooth = True
    return o

def box(name, size, loc, material, bevel=0.012, subsurf=0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return finish(o, material, bevel, subsurf)

def cyl(name, r, h, loc, material, rot=(0, 0, 0), verts=40, bevel=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=verts, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name
    return finish(o, material, bevel)

def sphere(name, r, loc, material, scale=(1, 1, 1), seg=40):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=seg // 2, location=loc)
    o = bpy.context.object; o.name = name; o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    return finish(o, material)

def torus(name, R, r, loc, material, rot=(0, 0, 0), seg=64):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=seg, minor_segments=14, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name
    return finish(o, material)

def join(objs, name, active=None):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = active or objs[0]
    bpy.ops.object.join(); o = bpy.context.object; o.name = name; o.data.name = name
    return o

# ---------- body ----------
parts = []
hull = sphere("hull", 0.5, (0, 0, 0), M["shell"], scale=(0.34, 0.5, 0.17), seg=64)           # 流線機殼
parts.append(hull)
belly = box("belly", (0.40, 0.56, 0.1), (0, 0.02, -0.12), M["carbon"], bevel=0.04, subsurf=1)   # 電池艙
parts.append(belly)
cap = sphere("cap", 0.5, (0, 0.07, 0.07), M["orange"], scale=(0.24, 0.30, 0.1), seg=48)       # 橘色頂蓋
parts.append(cap)
for sx in (-1, 1):                                                                                # 側邊橘色條
    parts.append(box("stripe", (0.025, 0.46, 0.05), (sx * 0.178, 0.0, 0.0), M["orange"], bevel=0.01))
cross_w = box("cross_w", (0.15, 0.15, 0.012), (0, 0.09, 0.158), M["shell"], bevel=0.006)
cross_a = box("cross_a", (0.1, 0.03, 0.016), (0, 0.09, 0.162), M["red"], bevel=0.004)
cross_b = box("cross_b", (0.03, 0.1, 0.016), (0, 0.09, 0.162), M["red"], bevel=0.004)
parts += [cross_w, cross_a, cross_b]
parts.append(box("light_bar", (0.2, 0.02, 0.022), (0, -0.495, 0.035), M["light"], bevel=0.008))   # 前燈
parts.append(cyl("antenna", 0.007, 0.26, (0.1, 0.22, 0.25), M["carbon"], verts=12))
parts.append(sphere("antenna_tip", 0.017, (0.1, 0.22, 0.385), M["ledr"], seg=16))
body = join(parts, "Body", active=hull)
# materials are per-object slots; join keeps all of them
# ---------- gimbal (camera) ----------
g = []
gb = sphere("gball", 0.085, (0, 0, 0), M["carbon"], seg=40)
gl = cyl("glens", 0.052, 0.08, (0, -0.07, 0), M["metal"], rot=(math.pi / 2, 0, 0), verts=32)
gg = cyl("gglass", 0.042, 0.012, (0, -0.112, 0), M["glass"], rot=(math.pi / 2, 0, 0), verts=32)
gr = torus("gring", 0.052, 0.006, (0, -0.108, 0), M["orange"], rot=(math.pi / 2, 0, 0), seg=32)
gm = box("gmount", (0.05, 0.05, 0.06), (0, 0.0, 0.1), M["carbon"], bevel=0.01)
gimbal = join([gb, gl, gg, gr, gm], "Gimbal", active=gb)
gimbal.location = (0, -0.43, -0.09)

# ---------- arms, motors, guards, props ----------
ARM = 0.5   # center to motor on each axis => motor radius ~0.707
motors = {"FL": (-ARM, -ARM), "FR": (ARM, -ARM), "BL": (-ARM, ARM), "BR": (ARM, ARM)}
fixed = []
for key, (mx, my) in motors.items():
    L = math.hypot(mx, my) - 0.16
    ang = math.atan2(my, mx)
    arm = box("arm_" + key, (L, 0.075, 0.05), (mx * 0.5 + (mx / abs(mx)) * 0.07 * 0.0, my * 0.5, -0.01), M["carbon"], bevel=0.018, subsurf=1)
    arm.location = (mx * 0.52, my * 0.52, -0.01); arm.rotation_euler = (0, 0, ang)
    cover = box("armcover_" + key, (L * 0.45, 0.082, 0.02), (0, 0, 0.03), M["orange"], bevel=0.008)
    cover.location = (mx * 0.40, my * 0.40, 0.025); cover.rotation_euler = (0, 0, ang)
    mh = cyl("motor_" + key, 0.085, 0.13, (mx, my, 0.03), M["metal"], verts=48, bevel=0.01)
    mr = cyl("mring_" + key, 0.092, 0.03, (mx, my, 0.1), M["orange"], verts=48, bevel=0.006)
    mb = cyl("mbase_" + key, 0.075, 0.05, (mx, my, -0.05), M["carbon"], verts=40)
    guard = torus("guard_" + key, 0.385, 0.016, (mx, my, 0.045), M["orange"], seg=72)
    fixed += [arm, cover, mh, mr, mb, guard]
    # 護圈支架（兩根）
    for s in (-1, 1):
        a2 = ang + s * 0.5
        tip = Vector((mx + math.cos(a2 + math.pi) * 0.0, my, 0.045))
        d = Vector((math.cos(ang + s * math.radians(55)), math.sin(ang + s * math.radians(55)), 0)) * 0.385
        mid = Vector((mx, my, 0.045)) + d * 0.5
        st = cyl("strut", 0.011, 0.385 - 0.085, (mid.x, mid.y, 0.045), M["carbon"], verts=10)
        st.rotation_euler = (math.pi / 2, 0, ang + s * math.radians(55) + math.pi / 2)
        fixed.append(st)
    led = sphere("LED_" + key, 0.026, (mx, my + (-1 if my < 0 else 1) * 0.0, -0.075), M["ledg"] if my < 0 else M["ledr"], seg=16)
    led.name = "LED_" + key; led.location = (mx * 0.94, my * 0.94, -0.04)
    fixed.append(led)
rig = join([o for o in fixed if not o.name.startswith("LED_")], "Frame", active=fixed[0])

props = []
for key, (mx, my) in motors.items():
    hub_parts = []
    hub = cyl("hub", 0.045, 0.07, (mx, my, 0.14), M["metal"], verts=32)
    cone = sphere("cone", 0.05, (mx, my, 0.165), M["orange"], scale=(1, 1, 0.7), seg=24)
    hub_parts += [hub, cone]
    for k in range(2):
        a = k * math.pi
        bl = box("blade", (0.34, 0.07, 0.008), (mx, my, 0.15), M["prop"], bevel=0.003)
        # 扭轉的槳葉
        bpy.context.view_layer.objects.active = bl
        for v in bl.data.vertices:
            t = v.co.x / 0.34
            v.co.z += t * 0.02
        bl.location = (mx + math.cos(a) * 0.19, my + math.sin(a) * 0.19, 0.15)
        bl.rotation_euler = (math.radians(7) * (1 if k == 0 else -1), 0, a)
        tip = box("tip", (0.06, 0.071, 0.01), (0, 0, 0), M["orange"], bevel=0.003)
        tip.location = (mx + math.cos(a) * 0.34, my + math.sin(a) * 0.34, 0.152); tip.rotation_euler = (0, 0, a)
        hub_parts += [bl, tip]
    props.append(join(hub_parts, "Prop_" + key, active=hub_parts[0]))
# 讓每個螺旋槳的原點移到轉軸中心
for p in props:
    k = p.name.split("_")[1]; mx, my = motors[k]
    bpy.context.scene.cursor.location = (mx, my, 0.15)
    bpy.context.view_layer.objects.active = p; bpy.ops.object.select_all(action='DESELECT'); p.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

# ---------- landing skids ----------
sk = []
for sx in (-1, 1):
    x = sx * 0.2
    rail = cyl("rail", 0.022, 0.62, (x, 0.0, -0.4), M["carbon"], rot=(math.pi / 2, 0, 0), verts=20)
    foot = cyl("foot", 0.026, 0.6, (x, 0.0, -0.4), M["rubber"], rot=(math.pi / 2, 0, 0), verts=20)
    foot.scale = (1, 1, 0.5)
    sk.append(rail)
    for y in (-0.2, 0.2):
        sk.append(cyl("leg", 0.017, 0.3, (x, y, -0.255), M["carbon"], rot=(0, math.radians(sx * 8), 0), verts=14))
skids = join(sk, "Skids", active=sk[0])

# ---------- hook / winch ----------
hk = [cyl("winch", 0.045, 0.06, (0, 0.05, -0.2), M["metal"], verts=24),
      cyl("cable", 0.006, 0.12, (0, 0.05, -0.27), M["carbon"], verts=8),
      torus("hookring", 0.026, 0.006, (0, 0.05, -0.345), M["metal"], rot=(math.pi / 2, 0, 0), seg=24)]
hook = join(hk, "Hook", active=hk[0])

# LED 在 join 裡被排除，留作獨立節點（可閃爍）
# ---------- finalize ----------
for o in bpy.data.objects:
    if o.type == 'MESH':
        for p in o.data.polygons: p.use_smooth = True
bpy.ops.object.select_all(action='DESELECT')
tris = 0
for o in bpy.data.objects:
    if o.type == 'MESH':
        tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
names = sorted(o.name for o in bpy.data.objects if o.type == 'MESH')
print("TRIS", tris, names)

bb_min = Vector((1e9,) * 3); bb_max = Vector((-1e9,) * 3)
for o in bpy.data.objects:
    if o.type == 'MESH':
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            bb_min = Vector(map(min, bb_min, w)); bb_max = Vector(map(max, bb_max, w))
size = bb_max - bb_min

bpy.ops.wm.save_as_mainfile(filepath=str((out / "rescue_drone.blend").resolve()))
bpy.ops.export_scene.gltf(filepath=str((out / "rescue_drone.glb").resolve()), export_format="GLB",
                          export_animations=False, export_apply=True, export_yup=True)

# ---------- previews (best effort) ----------
try:
    sc.render.engine = 'CYCLES'; sc.cycles.samples = 48; sc.cycles.device = 'CPU'
    sc.render.resolution_x = 900; sc.render.resolution_y = 700
    try: sc.cycles.use_denoising = True
    except Exception: pass
    world = bpy.data.worlds.new("W"); sc.world = world; world.use_nodes = True
    bgn = world.node_tree.nodes["Background"]; bgn.inputs[0].default_value = (0.62, 0.78, 0.95, 1); bgn.inputs[1].default_value = 1.1
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, -0.43)); floor = bpy.context.object
    floor.data.materials.append(mat("Floor", (0.55, 0.78, 0.45), 0, 0.9))
    bpy.ops.object.light_add(type='SUN', location=(3, -3, 5)); sun = bpy.context.object; sun.data.energy = 4; sun.rotation_euler = (math.radians(50), 0, math.radians(35))
    cam = bpy.data.cameras.new("C"); co = bpy.data.objects.new("C", cam); sc.collection.objects.link(co); sc.camera = co
    cam.lens = 55
    for name, loc in (("preview_front34", (2.0, -2.9, 1.5)), ("preview_top", (0.01, -0.6, 3.6)), ("preview_side", (3.8, 0.0, 0.5))):
        co.location = loc
        d = Vector((0, 0, -0.05)) - Vector(loc); co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = str((out / (name + ".png")).resolve()); bpy.ops.render.render(write_still=True)
except Exception as e:
    print("PREVIEW_SKIPPED", e)

(out / "report.json").write_text(json.dumps({
    "blender_version": bpy.app.version_string, "triangles": tris, "meshes": names,
    "size_m": [round(x, 3) for x in size], "visual_review": "pending",
    "notes": "Procedural original model. Props are separate nodes (Prop_FL/FR/BL/BR) with origin at hub for runtime spin."
}, indent=2), encoding="utf-8")
(out / "asset_manifest.json").write_text(json.dumps({
    "schema_version": 1, "asset_id": "rescue_drone", "format": "glTF 2.0 GLB",
    "source": "original procedural Blender script (scripts/blender5/rescue_drone.py)", "unit": "meter",
    "coordinate_system": "Blender Z-up; glTF export converts to Y-up",
    "model_file": "rescue_drone.glb", "source_file": "rescue_drone.blend",
    "clips": [], "min_animation_count": 0,
    "requirements": {"skins": False, "animated": False, "visual_review": True},
    "license_note": "Original geometry created for this project; CC0."
}, indent=2), encoding="utf-8")
print("RESCUE_DRONE_DONE")
