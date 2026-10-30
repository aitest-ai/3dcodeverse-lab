"""aviator_human -- realistic-proportion pilot built from CC0 assets + procedural flight gear (Blender 5.2, headless).

Inputs (CC0, Quaternius): Universal Base Characters [Standard] (Superhero body, same UE-mannequin skeleton) and
Universal Animation Library [Standard] (mocap-style clips).  Everything else (flight suit, boots, gloves, belt,
scarf, goggles) is generated here from the body mesh / simple shapes, so the outfit is original and recolourable.
Run:  ASSET_SRC=<dir with ubc/ and ual1.glb> ASSET_OUT_DIR=outputs blender -b --factory-startup --python scripts/blender5/aviator_human.py
Env:  CHAR=male|female (default male)
"""
import bpy, bmesh, math, json, os, struct
from pathlib import Path
from mathutils import Vector, Matrix

CHAR = os.environ.get("CHAR", "male")
ASSET_ID = "aviator_human_" + ("m" if CHAR == "male" else "f")
SRC = Path(os.environ.get("ASSET_SRC", "assets_src"))
OUT = Path(os.environ.get("ASSET_OUT_DIR", "outputs")); OUT.mkdir(parents=True, exist_ok=True)
BODY_FILE = {"male": "Superhero_Male_FullBody.gltf", "female": "Superhero_Female_FullBody.gltf"}[CHAR]
KEEP = {"Idle_Loop": "Idle", "Walk_Loop": "Walk", "Jog_Fwd_Loop": "Run", "Sprint_Loop": "Sprint", "Sitting_Idle_Loop": "Sit",
        "Driving_Loop": "Drive", "Interact": "Interact", "Dance_Loop": "Cheer", "Idle_Talking_Loop": "Talk", "Jump_Start": "JumpStart", "Jump_Loop": "JumpLoop", "Jump_Land": "JumpLand"}
LOCO = {"Walk": 0.0, "Run": 0.0, "Sprint": 0.0}
TEX = int(os.environ.get("TEX_SIZE", "1024"))

def lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def hexrgb(h): return (lin(((h >> 16) & 255) / 255), lin(((h >> 8) & 255) / 255), lin((h & 255) / 255), 1.0)

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
for blk in (bpy.data.actions, bpy.data.meshes, bpy.data.materials):
    for x in list(blk): blk.remove(x)

# ---------------------------------------------------------------- import body + animation library
bpy.ops.import_scene.gltf(filepath=str(SRC / "ubc/Base Characters/Godot - UE" / BODY_FILE))
rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE'); rig.name = "HumanRig"
body = next(o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith("Super")); body.name = "body"
base_objs = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(SRC / "ual1.glb"))
for o in list(bpy.data.objects):
    if o not in base_objs: bpy.data.objects.remove(o, do_unlink=True)
for a in list(bpy.data.actions):
    if a.name not in KEEP: bpy.data.actions.remove(a)
for old, new in KEEP.items():
    a = bpy.data.actions[old]; a.name = new; a.use_fake_user = True
sc = bpy.context.scene; sc.render.fps = 24
rig.animation_data_create()
def use_action(name):
    a = bpy.data.actions[name]; rig.animation_data.action = a
    if a.slots: rig.animation_data.action_slot = a.slots[0]
    return a

# ---------------------------------------------------------------- hair (rigged-to-head glTF reuses the same bone names)
hair_name = os.environ.get("HAIR", "Hair_SimpleParted" if CHAR == "male" else "Hair_Buns")
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(SRC / "ubc/Hairstyles/Rigged to Head Bone/glTF (Godot -Unreal)" / (hair_name + ".gltf")))
new = [o for o in bpy.data.objects if o not in before]
for o in new:
    if o.type == 'MESH':
        o.name = "hair"; o.parent = rig
        for m in o.modifiers:
            if m.type == 'ARMATURE': m.object = rig
        o.matrix_parent_inverse = Matrix.Identity(4)
for o in new:
    if o.type == 'ARMATURE': bpy.data.objects.remove(o, do_unlink=True)

# ---------------------------------------------------------------- outfit generated from the body mesh
me0 = body.data
gname = {i: g.name for i, g in enumerate(body.vertex_groups)}
def vcat(v):
    best, bw = None, 0
    for g in v.groups:
        if g.weight > bw: best, bw = gname[g.group], g.weight
    if best is None: return "skin"
    if best.startswith(("hand_", "index_", "middle_", "pinky_", "ring_", "thumb_")): return "glove"
    if best.startswith(("foot_", "ball_")): return "boot"
    if best.startswith("calf_") and v.co.z < 0.30: return "boot"   # boot shaft height (m)
    if best.startswith(("pelvis", "spine_", "clavicle_", "upperarm_", "lowerarm_", "thigh_", "calf_")): return "suit"
    return "skin"
cat = [vcat(v) for v in me0.vertices]
bm0 = bmesh.new(); bm0.from_mesh(me0); bm0.verts.ensure_lookup_table(); bm0.normal_update()
normals = [v.normal.copy() for v in bm0.verts]; bm0.free()

MATS = {}
def mat(name, hexc, rough=.7, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = hexrgb(hexc); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    m.diffuse_color = hexrgb(hexc); MATS[name] = m; return m
PAL = {"suit": (0x5B6B4B, .85, 0), "boot": (0x3B2A20, .6, 0), "glove": (0xA9794A, .7, 0), "belt": (0x2A2A2A, .6, 0), "buckle": (0xC9A24A, .3, .85),
       "scarf": (0xE3AA1E, .85, 0), "goggle_lens": (0x9EC8E0, .15, .2), "goggle_strap": (0x6A4A30, .8, 0), "patch": (0xE8E2D0, .8, 0)}
for k, (h, r, mt) in PAL.items(): mat(k, h, r, mt)

OFFS = {"suit": 0.011, "boot": 0.014, "glove": 0.007}
# a vertex-group-preserving approach: duplicate the body (keeps groups + armature modifier), then delete foreign faces
def layer_from_body(kind):
    ob = body.copy(); ob.data = body.data.copy(); ob.name = kind; bpy.context.collection.objects.link(ob)
    ob.parent = rig; ob.matrix_parent_inverse = body.matrix_parent_inverse.copy()
    ob.data.materials.clear(); ob.data.materials.append(MATS[kind])
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.verts.ensure_lookup_table()
    for v in bm.verts:
        z0 = v.co.z; v.co += normals[v.index] * OFFS[kind]
        if kind == "boot" and normals[v.index].z < 0: v.co.z = z0   # keep the sole flat, do not push it under the floor
    kill = [f for f in bm.faces if sum(1 for v in f.verts if cat[v.index] == kind) * 2 < len(f.verts)]
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bm.to_mesh(ob.data); bm.free()
    for p in ob.data.polygons: p.use_smooth = True
    return ob
suit = layer_from_body("suit"); boots = layer_from_body("boot"); gloves = layer_from_body("glove")
# the original body keeps skin; hide nothing (clothing sits 1 cm above it)

# ---------------------------------------------------------------- rigid accessories (acc_ prefix = optional in engine)
def rigid_part(name, bone, bm, matname):
    for f in bm.faces: f.smooth = True
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("acc_" + name, me); bpy.context.collection.objects.link(ob)
    ob.data.materials.append(MATS[matname])
    vg = ob.vertex_groups.new(name=bone); vg.add(list(range(len(me.vertices))), 1.0, 'REPLACE')
    md = ob.modifiers.new("Armature", 'ARMATURE'); md.object = rig; ob.parent = rig
    return ob
def ell(center, radii, seg=16, rings=10, rot=None):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * radii[0], v.co.y * radii[1], v.co.z * radii[2]))
    if rot is not None: bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=rot)
    bmesh.ops.translate(bm, verts=bm.verts, vec=center); return bm
def torus(center, R, r, n1=28, n2=8, sx=1.0, sy=1.0):
    bm = bmesh.new(); V = []
    for i in range(n1):
        a = 2 * math.pi * i / n1; ring = []
        for j in range(n2):
            b = 2 * math.pi * j / n2
            ring.append(bm.verts.new((((R + r * math.cos(b)) * math.cos(a)) * sx, ((R + r * math.cos(b)) * math.sin(a)) * sy, r * math.sin(b))))
        V.append(ring)
    for i in range(n1):
        for j in range(n2): bm.faces.new((V[i][j], V[(i + 1) % n1][j], V[(i + 1) % n1][(j + 1) % n2], V[i][(j + 1) % n2]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bmesh.ops.translate(bm, verts=bm.verts, vec=center); return bm


def ring_fit(point, axis, cats, band=0.012, extra=0.0):
    """mean radius of body vertices (in categories `cats`) lying within `band` of the plane through `point` normal to `axis`."""
    pts = [v.co for v in body.data.vertices if cat[v.index] in cats and abs((v.co - point).dot(axis)) < band and (v.co - point).length < 0.12]
    if not pts: return None
    c = sum(((q - (q - point).dot(axis) * axis) for q in pts), Vector()) / len(pts)
    r = sum(((q - c) - (q - c).dot(axis) * axis).length for q in pts) / len(pts)
    return c, r + extra
def ring_part(name, bone, point, axis, cats, tube, matname, extra=0.0, squash=1.0):
    fit = ring_fit(point, axis, cats, extra=extra)
    if fit is None: return None
    c, r = fit; bm = torus((0, 0, 0), 1.0, tube, n1=28, n2=8, sx=r, sy=r * squash)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Vector((0, 0, 1)).rotation_difference(axis).to_matrix())
    bmesh.ops.translate(bm, verts=bm.verts, vec=c); return rigid_part(name, bone, bm, matname)
bones = rig.data.bones
def hp(n): return bones[n].head_local.copy()
head = hp("Head"); neck = hp("neck_01"); sp1 = hp("spine_01"); sp3 = hp("spine_03"); pel = hp("pelvis")
dims = body.dimensions; H = max(v.co.z for v in body.data.vertices)
hx = 0.098 if CHAR == "male" else 0.088   # half head width (m), measured from mesh below
# measure head extents from the head-weighted vertices
hv = [v.co for v in body.data.vertices if cat[v.index] == "skin" and v.co.z > head.z + 0.03]
if hv:
    xs = [c.x for c in hv]; ys = [c.y for c in hv]; zs = [c.z for c in hv]
    hx = (max(xs) - min(xs)) / 2; hy = (max(ys) - min(ys)) / 2; hcz = (max(zs) + min(zs)) / 2; hcy = (max(ys) + min(ys)) / 2; htop = max(zs)
else:
    hy = 0.11; hcz = head.z + 0.1; hcy = head.y; htop = head.z + 0.2
FRONT = -1.0  # character faces -Y in Blender
gz = htop - 0.032   # goggle band height (on the forehead, above the brows)
rigid_part("goggle_strap", "Head", torus((0, hcy, gz), 1.0, 0.009, sx=hx * 1.10, sy=hy * 1.10), "goggle_strap")
for sg in (1, -1):
    rigid_part("goggle_rim_" + ("L" if sg > 0 else "R"), "Head", ell((sg * hx * 0.42, hcy + FRONT * hy * 1.04, gz + 0.004), (0.034, 0.014, 0.034), 16, 10), "buckle")
    rigid_part("goggle_lens_" + ("L" if sg > 0 else "R"), "Head", ell((sg * hx * 0.42, hcy + FRONT * hy * 1.10, gz + 0.004), (0.028, 0.010, 0.028), 16, 10), "goggle_lens")
for sg, sd in ((1, "l"), (-1, "r")):
    ring_part("boot_cuff_" + sd, "calf_" + sd, Vector((sg * 0.09, 0.0, 0.30)), Vector((0, 0, 1)), ("suit", "boot"), 0.017, "boot", extra=0.016)
    wr = hp("hand_" + sd); fa = (hp("hand_" + sd) - hp("lowerarm_" + sd)).normalized()
    ring_part("sleeve_cuff_" + sd, "lowerarm_" + sd, wr - fa * 0.015, fa, ("suit",), 0.012, "belt", extra=0.014)
rigid_part("scarf", "neck_01", torus((0, neck.y, neck.z + 0.045), 1.0, 0.026, sx=0.082, sy=0.085), "scarf")
rigid_part("scarf_tail", "spine_03", ell((0.0, sp3.y + 0.085, sp3.z + 0.02), (0.035, 0.012, 0.15), 10, 8), "scarf")
rigid_part("chest_patch", "spine_03", ell((0.085, sp3.y - 0.11, sp3.z - 0.02), (0.035, 0.006, 0.028), 12, 8), "patch")

# hair colour: the source hair texture is neutral grey, tint it (HAIR_TINT=R,G,B 0..1 multipliers)
tint = [float(x) for x in os.environ.get("HAIR_TINT", "0.62,0.36,0.20").split(",")]
for im in bpy.data.images:
    if "Hair" in im.name and "BaseColor" in im.name and "Normal" not in im.name:
        px = list(im.pixels)
        for i in range(0, len(px), 4):
            l = (px[i] + px[i + 1] + px[i + 2]) / 3.0
            px[i] = min(1, l * tint[0] * 1.25); px[i + 1] = min(1, l * tint[1] * 1.25); px[i + 2] = min(1, l * tint[2] * 1.25)
        im.pixels = px; im.update()

# ---------------------------------------------------------------- textures: downscale for the web (JPEG for opaque maps, PNG where alpha matters)
for im in bpy.data.images:
    if im.name == "Render Result" or im.name == "Viewer Node": continue
    try:
        t = TEX if "Superhero" in im.name else TEX // 2
        if im.size[0] > t: im.scale(t, t)
        im.file_format = 'PNG' if ("Hair" in im.name and "BaseColor" in im.name) else 'JPEG'
        im.pack()
    except Exception: pass

# ---------------------------------------------------------------- measurements: foot grounding, slip, speed
foot_idx = [v.index for v in me0.vertices if cat[v.index] in ("boot",)]
def eval_sole_and_feet():
    dg = bpy.context.evaluated_depsgraph_get(); ev = boots.evaluated_get(dg); m = ev.to_mesh()
    zs = [(rig.matrix_world @ v.co).z for v in m.vertices]; ev.to_mesh_clear(); return min(zs)
STATS = {}; CLIPINFO = {}
for name in KEEP.values():
    a = use_action(name); f0, f1 = int(a.frame_range[0]), int(a.frame_range[1]); rows = []
    for f in range(f0, f1 + 1):
        sc.frame_set(f); bpy.context.view_layer.update()
        pb = rig.pose.bones
        rows.append((f, eval_sole_and_feet(), pb["ball_l"].head.y, pb["ball_l"].head.z, pb["ball_r"].head.y, pb["ball_r"].head.z))
    STATS[name] = {"frames": f1 - f0, "min_sole_z_m": round(min(r[1] for r in rows), 4), "max_sole_min_z_m": round(max(r[1] for r in rows), 4)}
    if name in LOCO:
        # stance = ball height within 2 cm of its minimum. The character faces -Y, so a planted foot travels toward +Y
        # (in character space) at the clip speed; speed = that travel / stance time, slip = residual drift after removing it.
        n = f1 - f0   # loop clips repeat frame 0 at the end: use n unique frames, circular
        def find_runs(THR):
            out = []
            for yi, zi in ((2, 3), (4, 5)):
                zmin = min(r[zi] for r in rows[:n]); st = [rows[i][zi] <= zmin + THR for i in range(n)]
                if all(st) or not any(st): continue
                start = next(i for i in range(n) if st[i] and not st[i - 1]); i = start
                while i < start + n:
                    if st[i % n]:
                        r = []
                        while st[i % n] and len(r) < n: r.append(i); i += 1
                        if len(r) >= 3: out.append((yi, r))
                    else: i += 1
            return out
        runs_all = []
        for THR in (0.015, 0.03, 0.05):
            runs_all = find_runs(THR)
            if runs_all: break
        v_est = [(rows[r[-1] % n][yi] - rows[r[0] % n][yi]) / ((r[-1] - r[0]) / 24.0) for yi, r in runs_all]
        v = sum(v_est) / max(1, len(v_est)); LOCO[name] = v; worst = 0.0
        for yi, r in runs_all:
            g = [rows[i % n][yi] - v * ((i - r[0]) / 24.0) for i in r]; worst = max(worst, max(g) - min(g))
        STATS[name]["speed_mps"] = round(v, 3); STATS[name]["max_stance_slip_m"] = round(worst, 4); STATS[name]["stance_runs"] = len(runs_all)
        CLIPINFO[name] = {"frames": f1 - f0, "fps": 24, "loop": True, "speed_mps": round(v, 3)}
    else:
        CLIPINFO[name] = {"frames": f1 - f0, "fps": 24, "loop": name in ("Idle", "Walk", "Run", "Sprint", "Sit", "Drive", "Cheer", "Talk", "JumpLoop")}


# ---------------------------------------------------------------- per-clip ground correction (retargeting leaves the soles a few cm off the floor)
def ground_fix(name, delta):
    a = use_action(name); f0, f1 = int(a.frame_range[0]), int(a.frame_range[1]); root = rig.pose.bones["root"]
    # world +Z delta expressed in the root bone's local axes
    M = (rig.matrix_world @ root.bone.matrix_local).to_3x3(); loc = M.inverted() @ Vector((0, 0, delta))
    base = [root.location.copy()]
    for f in range(f0, f1 + 1):
        sc.frame_set(f); bpy.context.view_layer.update()
        cur = root.location.copy(); root.location = cur + loc; root.keyframe_insert("location", frame=f)
for name in list(KEEP.values()):
    d = -STATS[name]["min_sole_z_m"]
    if abs(d) > 0.004 and name not in ("Run", "Sprint"):   # jogging clips already touch the floor; flight frames must stay airborne
        ground_fix(name, d); STATS[name]["ground_correction_m"] = round(d, 4)
for name in KEEP.values():   # re-measure
    a = use_action(name); f0, f1 = int(a.frame_range[0]), int(a.frame_range[1]); lo = 9
    for f in range(f0, f1 + 1):
        sc.frame_set(f); bpy.context.view_layer.update(); lo = min(lo, eval_sole_and_feet())
    STATS[name]["min_sole_z_after_m"] = round(lo, 4)

# ---------------------------------------------------------------- save + export
rig.animation_data.action = None
use_action("Idle"); sc.frame_set(1); sc.frame_start = 1; sc.frame_end = 60
bpy.ops.wm.save_as_mainfile(filepath=str((OUT / (ASSET_ID + ".blend")).resolve()))
rig.animation_data.action = None
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.type in ('MESH', 'ARMATURE'): o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str((OUT / (ASSET_ID + ".glb")).resolve()), export_format='GLB', use_selection=True,
                          export_animations=True, export_animation_mode='ACTIONS', export_skins=True, export_force_sampling=True,
                          export_yup=True, export_image_format='JPEG', export_jpeg_quality=85)

with (OUT / (ASSET_ID + ".glb")).open("rb") as f:
    magic, ver, total = struct.unpack("<4sII", f.read(12)); ln, typ = struct.unpack("<I4s", f.read(8)); doc = json.loads(f.read(ln).decode())
anim = [a.get("name") for a in doc.get("animations", [])]
need = ["Idle", "Walk", "Run", "Sprint", "Sit"]
assert all(n in anim for n in need), "missing clips: %s" % anim
assert len(doc.get("skins", [])) >= 1
for c in ("Walk", "Run", "Sprint"):
    assert STATS[c]["max_stance_slip_m"] <= 0.06, "stance slip too large in %s: %s" % (c, STATS[c])
for c in ("Idle", "Walk", "Run", "Sprint", "Sit"):
    assert STATS[c]["min_sole_z_after_m"] >= -0.015, "sole sinks in %s: %s" % (c, STATS[c])
h = round(max((o.matrix_world @ Vector(c)).z for o in bpy.data.objects if o.type == 'MESH' for c in o.bound_box), 2)
report = {"asset_id": ASSET_ID, "blender_version": bpy.app.version_string, "glb_bytes": total, "clips": anim, "measurements": STATS, "height_m": h,
          "meshes": [o.name for o in bpy.data.objects if o.type == 'MESH'],
          "not_checked_automatically": ["visual quality / likeness", "cloth interpenetration beyond the 1 cm offset shell", "real-GPU performance"],
          "method": "CC0 body + CC0 mocap-style clips (Quaternius) retargeted by shared bone names; outfit generated from the body mesh"}
(OUT / (ASSET_ID + "_report.json")).write_text(json.dumps(report, indent=2), encoding="utf-8")
manifest = {"schema_version": 1, "asset_id": ASSET_ID, "format": "glTF 2.0 GLB", "model_file": ASSET_ID + ".glb", "source_file": ASSET_ID + ".blend",
            "blender_version": bpy.app.version_string, "unit": "meter", "clips": anim, "min_animation_count": len(anim),
            "requirements": {"skins": True, "animated": True, "visual_review": True},
            "character": {"height_m": h, "style": "realistic adult proportions", "forward_axis_glb": "+Z", "root_bone": "root", "ground_y": 0.0, "skeleton": "UE mannequin (65 bones)"},
            "clip_info": CLIPINFO,
            "customization": {"recolor_by_material_name": ["suit", "boot", "glove", "scarf", "buckle", "goggle_strap", "patch"], "optional_nodes": [o.name for o in bpy.data.objects if o.name.startswith("acc_")]},
            "license_note": "Body mesh and clips: CC0 1.0 (Quaternius, Universal Base Characters [Standard] and Universal Animation Library [Standard]). Outfit/accessories: original, generated by this script."}
(OUT / (ASSET_ID + "_manifest.json")).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print("ASSET_BUILD_OK", json.dumps({c: STATS[c] for c in ("Idle", "Walk", "Run", "Sprint", "Sit")}))
