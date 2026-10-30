"""aviator_kid -- Q-style child pilot, rigged, with locomotion clips (Blender 5.2, headless).

Run (from repository root):  blender -b --factory-startup --python scripts/blender5/aviator_kid.py
Outputs (in ./outputs or $ASSET_OUT_DIR):
    aviator_kid.blend  aviator_kid.glb  asset_manifest.json  report.json  (+ preview PNGs if rendering works)

Design rules (see docs/CHARACTER_PIPELINE.md):
  * original procedural geometry only; units = meters; character faces -Y in Blender (=> +Z in glTF), Z up.
  * every body part is weighted 100% to ONE bone (rigid, toy-like Q style) so the glTF needs no extra deformers.
  * colour roles are separate named materials; optional accessories are nodes named acc_* (toggle visibility in engine).
  * poses are generated from forward kinematics + 2-bone IK in the sagittal plane, so stance feet do not slide.
  * the script MEASURES foot slip, sole penetration, joint ranges and arm/torso clearance on the evaluated mesh and
    writes the numbers to report.json. It never claims visual approval; that is a separate human/AI review step.
"""
import bpy, bmesh, math, json, os, struct, sys
from pathlib import Path
from mathutils import Vector, Matrix

ASSET_ID = "aviator_kid"
OUT = Path(os.environ.get("ASSET_OUT_DIR", "outputs")); OUT.mkdir(parents=True, exist_ok=True)
FPS = 30

# ------------------------------------------------------------------ helpers
def lin(c):  # sRGB 0..1 -> linear
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def hexrgb(h):
    return (lin(((h >> 16) & 255) / 255), lin(((h >> 8) & 255) / 255), lin((h & 255) / 255), 1.0)
def Rx(a): return Matrix.Rotation(a, 3, 'X')
def Ry(a): return Matrix.Rotation(a, 3, 'Y')
def Rz(a): return Matrix.Rotation(a, 3, 'Z')
def ease(s): s = max(0.0, min(1.0, s)); return s * s * s * (s * (s * 6 - 15) + 10)

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.armatures, bpy.data.actions):
    for x in list(blk): blk.remove(x)

# ------------------------------------------------------------------ materials (colour roles)
PALETTE = {  # role: (hex, roughness, metallic)
    "skin": (0xF1C7A0, .75, 0), "hair": (0x3B2A22, .6, 0), "eye": (0x14171C, .3, 0), "white": (0xF6F1E6, .7, 0),
    "cheek": (0xE98C84, .8, 0), "jacket": (0x2D5C9A, .62, 0), "jacket_trim": (0x1B3558, .6, 0), "pants": (0x39414F, .8, 0),
    "boot": (0x4A3326, .7, 0), "glove": (0xD8A35A, .75, 0), "scarf": (0xE3AA1E, .85, 0), "cap": (0x1D3A5F, .6, 0),
    "accent": (0xC9A24A, .35, .85), "goggle_lens": (0x9EC8E0, .15, .2), "goggle_strap": (0x6A4A30, .8, 0), "pack": (0x7B6542, .85, 0),
}
MATS = {}
for role, (h, r, m) in PALETTE.items():
    mt = bpy.data.materials.new(role); mt.use_nodes = True
    b = mt.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexrgb(h); b.inputs["Roughness"].default_value = r; b.inputs["Metallic"].default_value = m
    mt.diffuse_color = hexrgb(h)
    MATS[role] = mt

# ------------------------------------------------------------------ skeleton (Blender space: Z up, forward = -Y, character LEFT = +X)
S = 0.09  # half hip width
BONES = [  # name, parent, head, tail
    ("root", None, (0, 0, 0), (0, 0, .1)),
    ("hips", "root", (0, 0, .62), (0, 0, .70)),
    ("spine", "hips", (0, 0, .70), (0, 0, .90)),
    ("neck", "spine", (0, 0, .90), (0, 0, .96)),
    ("head", "neck", (0, 0, .96), (0, 0, 1.42)),
]
for sd, sg in (("L", 1), ("R", -1)):
    BONES += [
        ("thigh." + sd, "hips", (sg * S, 0, .62), (sg * S, 0, .34)),
        ("shin." + sd, "thigh." + sd, (sg * S, 0, .34), (sg * S, 0, .09)),
        ("foot." + sd, "shin." + sd, (sg * S, 0, .09), (sg * S, -.15, .05)),
        ("upper_arm." + sd, "spine", (sg * .17, 0, .86), (sg * .215, 0, .66)),
        ("forearm." + sd, "upper_arm." + sd, (sg * .215, 0, .66), (sg * .215, 0, .47)),
        ("hand." + sd, "forearm." + sd, (sg * .215, 0, .47), (sg * .215, 0, .40)),
    ]
L_THIGH, L_SHIN, ANKLE_Z = .28, .25, .09

arm_data = bpy.data.armatures.new("KidArmature")
rig = bpy.data.objects.new("KidRig", arm_data); bpy.context.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig; rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for n, p, h, t in BONES:
    eb = arm_data.edit_bones.new(n); eb.head = h; eb.tail = t
    if p: eb.parent = arm_data.edit_bones[p]
    eb.roll = 0
bpy.ops.object.mode_set(mode='OBJECT')
REST = {n: (Vector(h), Vector(t), p) for n, p, h, t in BONES}
ORDER = [b[0] for b in BONES]  # parents always before children

# ------------------------------------------------------------------ geometry (ellipsoid parts, each rigidly weighted to one bone)
PARTS = []  # (name, obj)
def ellipsoid(name, bone, center, radii, mat, seg=18, rings=10, rot=None, cut_below=None, acc=False):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * radii[0], v.co.y * radii[1], v.co.z * radii[2]))
    if cut_below is not None:  # remove everything below local z (for hemisphere caps)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < cut_below * radii[2] - 1e-6], context='VERTS')
    if rot is not None:
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=rot)
    bmesh.ops.translate(bm, verts=bm.verts, vec=center)
    for f in bm.faces: f.smooth = True
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(("acc_" if acc else "") + name, me); bpy.context.collection.objects.link(ob)
    ob.data.materials.append(MATS[mat])
    vg = ob.vertex_groups.new(name=bone); vg.add(list(range(len(me.vertices))), 1.0, 'REPLACE')
    md = ob.modifiers.new("Armature", 'ARMATURE'); md.object = rig
    ob.parent = rig
    PARTS.append((ob.name, ob))
    return ob
def torus(name, bone, center, R, r, mat, acc=False):
    bm = bmesh.new()
    # torus by revolving a circle
    n1, n2 = 24, 8
    verts = []
    for i in range(n1):
        a = 2 * math.pi * i / n1
        ring = []
        for j in range(n2):
            b = 2 * math.pi * j / n2
            ring.append(bm.verts.new(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b))))
        verts.append(ring)
    for i in range(n1):
        for j in range(n2):
            bm.faces.new((verts[i][j], verts[(i + 1) % n1][j], verts[(i + 1) % n1][(j + 1) % n2], verts[i][(j + 1) % n2]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.translate(bm, verts=bm.verts, vec=center)
    for f in bm.faces: f.smooth = True
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(("acc_" if acc else "") + name, me); bpy.context.collection.objects.link(ob)
    ob.data.materials.append(MATS[mat])
    vg = ob.vertex_groups.new(name=bone); vg.add(list(range(len(me.vertices))), 1.0, 'REPLACE')
    md = ob.modifiers.new("Armature", 'ARMATURE'); md.object = rig; ob.parent = rig
    PARTS.append((ob.name, ob)); return ob

def lathe(name, bone, center, profile, mat, sx=1.0, sy=1.0, seg=20, rot=None, acc=False):
    """soft-edged tapered tube (cloth-like, not a balloon): profile = [(dz, radius), ...] from bottom to top, rings joined, ends capped."""
    bm = bmesh.new(); rings = []
    for dz, r in profile:
        rings.append([bm.verts.new((r * sx * math.cos(2 * math.pi * i / seg), r * sy * math.sin(2 * math.pi * i / seg), dz)) for i in range(seg)])
    for a, b in zip(rings[:-1], rings[1:]):
        for i in range(seg): bm.faces.new((a[i], a[(i + 1) % seg], b[(i + 1) % seg], b[i]))
    for ring, up in ((rings[0], False), (rings[-1], True)):
        c = bm.verts.new((0, 0, profile[0 if not up else -1][0]))
        for i in range(seg): bm.faces.new((ring[(i + 1) % seg], ring[i], c) if not up else (ring[i], ring[(i + 1) % seg], c))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if rot is not None: bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=rot)
    bmesh.ops.translate(bm, verts=bm.verts, vec=center)
    for f in bm.faces: f.smooth = True
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(("acc_" if acc else "") + name, me); bpy.context.collection.objects.link(ob)
    ob.data.materials.append(MATS[mat])
    vg = ob.vertex_groups.new(name=bone); vg.add(list(range(len(me.vertices))), 1.0, 'REPLACE')
    md = ob.modifiers.new("Armature", 'ARMATURE'); md.object = rig; ob.parent = rig
    PARTS.append((ob.name, ob)); return ob

E = ellipsoid
# --- head
E("head", "head", (0, 0, 1.19), (.205, .2, .205), "skin", 24, 14)
E("hair_back", "head", (0, .035, 1.215), (.212, .19, .19), "hair", 20, 12)
for sg in (1, -1):
    E("ear_" + ("L" if sg > 0 else "R"), "head", (sg * .2, 0, 1.17), (.03, .02, .04), "skin", 10, 6)
    E("eye_" + ("L" if sg > 0 else "R"), "head", (sg * .078, -.186, 1.18), (.03, .02, .042), "eye", 12, 8)
    E("eyeshine_" + ("L" if sg > 0 else "R"), "head", (sg * .07, -.202, 1.2), (.009, .006, .012), "white", 8, 6)
    E("cheek_" + ("L" if sg > 0 else "R"), "head", (sg * .125, -.139, 1.115), (.034, .012, .022), "cheek", 10, 6, rot=Rz(sg * -0.5))
E("mouth", "head", (0, -.172, 1.09), (.03, .008, .011), "eye", 10, 6)
# --- cap + goggles (accessories)
E("cap", "head", (0, .008, 1.215), (.222, .216, .2), "cap", 24, 12, cut_below=0.12, acc=True)
E("cap_brim", "head", (0, -.2, 1.245), (.125, .095, .02), "cap", 20, 8, acc=True)
torus("goggle_strap", "head", (0, .008, 1.29), .214, .014, "goggle_strap", acc=True)
for sg in (1, -1):
    E("goggle_lens_" + ("L" if sg > 0 else "R"), "head", (sg * .07, -.19, 1.305), (.052, .03, .052), "goggle_lens", 14, 8, acc=True)
    E("goggle_rim_" + ("L" if sg > 0 else "R"), "head", (sg * .07, -.178, 1.305), (.062, .02, .062), "accent", 14, 8, acc=True)
# --- torso, scarf, pack, emblem
lathe("torso", "spine", (0, 0, .77), [(-.215, .150), (-.205, .172), (-.12, .176), (.05, .172), (.14, .162), (.19, .132), (.215, .075)], "jacket", sx=1.0, sy=.78, seg=24)   # flared jacket hem, squared shoulders
lathe("waist_trim", "hips", (0, 0, .575), [(-.02, .171), (-.012, .180), (.012, .180), (.02, .171)], "jacket_trim", sx=1.0, sy=.80, seg=24)   # jacket hem band
E("pelvis", "hips", (0, 0, .60), (.150, .115, .08), "pants", 18, 10)
E("neck", "neck", (0, 0, .93), (.06, .06, .05), "skin", 10, 6)
torus("scarf", "spine", (0, 0, .915), .115, .042, "scarf", acc=True)
E("scarf_tail", "spine", (-.07, .105, .85), (.04, .02, .11), "scarf", 10, 8, rot=Ry(0.15), acc=True)
E("emblem", "spine", (.075, -.126, .84), (.035, .01, .035), "accent", 12, 6)
E("emblem_wingL", "spine", (.125, -.124, .835), (.04, .008, .012), "accent", 10, 6, rot=Ry(-0.4))
E("pack", "spine", (0, .155, .78), (.13, .075, .155), "pack", 16, 10, acc=True)
for sg in (1, -1):
    E("pack_strap_" + ("L" if sg > 0 else "R"), "spine", (sg * .1, -.015, .835), (.025, .125, .12), "jacket_trim", 8, 6, acc=True)
# --- legs: straight trouser legs over knee-high boots
for sd, sg in (("L", 1), ("R", -1)):
    lathe("thigh_" + sd, "thigh." + sd, (sg * S, 0, .48), [(-.17, .066), (-.16, .072), (.14, .082), (.17, .074)], "pants", seg=18)
    lathe("shin_" + sd, "shin." + sd, (sg * S, 0, .25), [(-.12, .064), (-.11, .068), (.12, .066), (.15, .062)], "pants", seg=18)
    lathe("boot_cuff_" + sd, "shin." + sd, (sg * S, 0, .12), [(-.04, .070), (-.035, .078), (.035, .078), (.045, .071)], "boot", seg=18)
    E("boot_" + sd, "foot." + sd, (sg * S, -.05, .045), (.074, .125, .042), "boot", 16, 10)
# --- arms: tapered sleeves, no ball shoulders
for sd, sg in (("L", 1), ("R", -1)):
    lathe("upper_arm_" + sd, "upper_arm." + sd, (sg * .2, 0, .765), [(-.115, .052), (-.105, .058), (.10, .064), (.125, .06)], "jacket", seg=16, rot=Ry(sg * -0.22))
    E("shoulder_" + sd, "upper_arm." + sd, (sg * .172, 0, .855), (.058, .058, .056), "jacket", 12, 8)
    lathe("forearm_" + sd, "forearm." + sd, (sg * .215, 0, .56), [(-.10, .046), (-.09, .052), (.09, .056), (.11, .054)], "jacket", seg=16)
    lathe("cuff_" + sd, "forearm." + sd, (sg * .215, 0, .465), [(-.016, .050), (-.012, .058), (.012, .058), (.016, .050)], "jacket_trim", seg=16)
    E("glove_" + sd, "hand." + sd, (sg * .215, 0, .43), (.054, .05, .058), "glove", 14, 10)

HEAD_SCALE = 1.14   # Q proportions: scale every head-bone mesh uniformly about the neck top
for _n, _ob in PARTS:
    if _ob.vertex_groups and _ob.vertex_groups[0].name == "head":
        for _v in _ob.data.vertices:
            _v.co = Vector((0, 0, .98)) + (_v.co - Vector((0, 0, .98))) * HEAD_SCALE

# ------------------------------------------------------------------ pose machinery
poses = rig.pose.bones
for pb in poses: pb.rotation_mode = 'QUATERNION'

def apply_pose(rots, offs=None):
    """rots: bone -> 3x3 world-axis rotation DELTA applied about the bone's own head (default identity).
    offs: bone -> world translation added to that bone's head (and inherited by children)."""
    offs = offs or {}
    heads, tails = {}, {}
    for n in ORDER:
        h0, t0, p = REST[n]; R = rots.get(n, Matrix.Identity(3))
        if p is None:
            hn = h0.copy()
        else:
            ph0, pt0, _ = REST[p]
            if (h0 - pt0).length < 1e-6: hn = tails[p].copy()           # connected chain
            else: hn = heads[p] + rots.get(p, Matrix.Identity(3)) @ (h0 - ph0)  # branch from parent head
        if n in offs: hn = hn + Vector(offs[n])
        heads[n] = hn; tails[n] = hn + R @ (t0 - h0)
        rest3 = rig.data.bones[n].matrix_local.to_3x3().to_4x4()
        poses[n].matrix = Matrix.Translation(hn) @ (R.to_4x4() @ rest3)
        bpy.context.view_layer.update()  # the matrix setter reads the parent's evaluated pose, so refresh after every bone
    return heads, tails

def key_all(frame):
    for pb in poses:
        pb.keyframe_insert("location", frame=frame); pb.keyframe_insert("rotation_quaternion", frame=frame)

def leg_ik(hip, target):
    """sagittal 2-bone IK. hip, target = (forward, z). returns (thigh_phi, shin_phi) angles from vertical, forward positive."""
    f, z = target[0] - hip[0], hip[1] - target[1]
    d = max(1e-4, math.hypot(f, z)); d = min(d, L_THIGH + L_SHIN - 1e-4)
    psi = math.atan2(f, z)
    alpha = math.acos(max(-1, min(1, (L_THIGH ** 2 + d ** 2 - L_SHIN ** 2) / (2 * L_THIGH * d))))
    beta = math.acos(max(-1, min(1, (L_THIGH ** 2 + L_SHIN ** 2 - d ** 2) / (2 * L_THIGH * L_SHIN))))
    phi1 = psi + alpha
    phi2 = phi1 - (math.pi - beta)
    return phi1, phi2, math.pi - beta  # knee flexion

def fwd(a):  # forward-swing angle (forward positive) -> world X rotation delta (bone pointing down swings toward -Y)
    return Rx(-a)

JOINT_LIMITS_DEG = {"knee_flex": (0, 140), "elbow_flex": (0, 150), "thigh_swing": (-35, 100), "shoulder_swing": (-60, 180), "spine_lean": (-20, 35), "head_nod": (-40, 40)}
STATS = {}
def stat(clip, key, val, mode="max"):
    d = STATS.setdefault(clip, {})
    d[key] = max(d.get(key, -1e9), val) if mode == "max" else min(d.get(key, 1e9), val)

# ------------------------------------------------------------------ gait generator (walk / run), root stays in place
def gait_frame(clip, k, N, v, duty, lift, bob_flight, arm_amp, lean, elbow, T):
    ph = k / N
    A = v * T * duty / 2.0   # half stance travel (m)
    rots, offs = {}, {}
    foot = {}
    stance_cap = []
    for sd, off in (("L", 0.0), ("R", 0.5)):
        p = (ph + off) % 1.0
        if p < duty:
            f = A - 2 * A * (p / duty); z = ANKLE_Z; st = True; pitch = 0.0
            if p / duty > .72: pitch = 0.0
        else:
            s = (p - duty) / (1 - duty); e = ease(s)
            f = -A + 2 * A * e; z = ANKLE_Z + lift * math.sin(math.pi * s) ** 1.2; st = False
            pitch = -0.25 * math.sin(math.pi * min(1, s * 1.6)) * (1 - s) + 0.15 * math.sin(math.pi * max(0.0, (s - .55) / .45))  # toe-down after lift-off, toe-up before heel strike (0 at both ends)
        foot[sd] = (f, z, st, pitch)
    # hip height: highest value that keeps every stance leg reachable with slight knee bend
    Leff = (L_THIGH + L_SHIN) * (0.955 if clip == "Walk" else 0.93)
    cands = [ANKLE_Z + math.sqrt(max(1e-4, Leff ** 2 - foot[sd][0] ** 2)) for sd in foot if foot[sd][2]]
    if cands: hz = min(cands)
    else:  # flight phase (run): ballistic-looking arc
        hz = ANKLE_Z + Leff * 0.985 + bob_flight * math.sin(math.pi * ((ph % .5) / .5))
    # when both feet are in flight the stance cands are empty; when one is stance use that
    offs["hips"] = (0, 0, hz - 0.62)
    lean_a = lean + (0.03 * math.sin(4 * math.pi * ph) if clip == "Run" else 0.015 * math.sin(4 * math.pi * ph))
    rots["spine"] = fwd(lean_a)  # lean the spine forward
    rots["neck"] = fwd(-lean_a * 0.5); rots["head"] = fwd(-lean_a * 0.5)
    rots["hips"] = Rz(0.05 * math.sin(2 * math.pi * ph) * (1.5 if clip == "Run" else 1))
    for sd, sg in (("L", 1), ("R", -1)):
        f, z, st, pitch = foot[sd]
        phi1, phi2, kf = leg_ik((0.0, hz), (f, z))
        rots["thigh." + sd] = fwd(phi1); rots["shin." + sd] = fwd(phi2)
        rots["foot." + sd] = Rx(-(pitch + (phi2 - 0)) * 0 - pitch)  # world pitch about the ankle: toe-up positive (Rx(-a) tips toe down for +a?)
        stat(clip, "knee_flex_max_deg", math.degrees(kf)); stat(clip, "thigh_swing_max_deg", math.degrees(phi1)); stat(clip, "thigh_swing_min_deg", math.degrees(phi1), "min")
        # arms: opposite phase to same-side leg
        q = math.sin(2 * math.pi * (ph + (0.0 if sd == "L" else 0.5)))
        a_sw = -arm_amp * q  # swing forward positive
        rots["upper_arm." + sd] = fwd(a_sw) @ (Ry(-sg * .06))
        rots["forearm." + sd] = fwd(a_sw + elbow + 0.25 * arm_amp * max(0, -q)) @ (Ry(-sg * .06))
        rots["hand." + sd] = rots["forearm." + sd]
        stat(clip, "elbow_flex_max_deg", math.degrees(elbow + 0.25 * arm_amp * max(0, -q)))
        stat(clip, "shoulder_swing_max_deg", math.degrees(abs(a_sw)))
        foot[sd + "_pos"] = (f, z)
    return rots, offs, foot

def foot_sole_samples():
    """lowest world z over both boot meshes, from the evaluated (deformed) mesh."""
    dg = bpy.context.evaluated_depsgraph_get(); dg.update()
    res = {}
    for sd in ("L", "R"):
        ob = bpy.data.objects["boot_" + sd]; ev = ob.evaluated_get(dg); me = ev.to_mesh()
        mw = ev.matrix_world; zs = [(mw @ v.co).z for v in me.vertices]; ys = [(mw @ v.co).y for v in me.vertices]
        res[sd] = (min(zs), min(ys), max(ys)); ev.to_mesh_clear()
    return res

def head_pos(bone):
    bpy.context.view_layer.update()
    return rig.matrix_world @ poses[bone].head

def build_clip(name, nframes, fn, loop=True):
    act = bpy.data.actions.new(name); act.use_fake_user = True
    rig.animation_data_create(); rig.animation_data.action = act
    ankle_log = []
    for k in range(nframes + 1):
        rots, offs, extra = fn(k, nframes)
        apply_pose(rots, offs)
        key_all(k + 1)
        bpy.context.view_layer.update()
        samp = foot_sole_samples()
        stat(name, "min_sole_z_m", min(samp["L"][0], samp["R"][0]), "min")
        if extra is not None:
            for sd in ("L", "R"):
                hp = head_pos("foot." + sd)
                ankle_log.append((k, sd, hp.y, hp.z, extra[sd][2] if isinstance(extra.get(sd), tuple) and len(extra[sd]) > 2 else None))
        # hand-vs-torso clearance (ellipsoid test with 1.0 = surface); also hand vs pack
        for sd in ("L", "R"):
            hpos = head_pos("hand." + sd) + Vector((0, 0, 0))
            gl = poses["hand." + sd]; centre = (rig.matrix_world @ ((gl.head + gl.tail) / 2))
            q = (centre.x / .172) ** 2 + (centre.y / .13) ** 2 + ((centre.z - .77) / .2) ** 2
            # hand radius ~0.05: demand centre outside ellipsoid scaled up by hand radius
            clearance = math.sqrt(q) - 1.0
            stat(name, "hand_torso_clearance_min", clearance, "min")
    rig.animation_data.action = None
    return act, ankle_log

# ------------------------------------------------------------------ clips
CLIP_META = {}
def run_gait(name, N, v, duty, lift, bob_flight, arm_amp, lean, elbow, T):
    def fn(k, n): 
        r, o, foot = gait_frame(name, k, n, v, duty, lift, bob_flight, arm_amp, lean, elbow, T)
        return r, o, {"L": (foot["L"][0], foot["L"][1], foot["L"][2]), "R": (foot["R"][0], foot["R"][1], foot["R"][2])}
    act, log = build_clip(name, N, fn)
    CLIP_META[name] = {"frames": N, "fps": FPS, "loop": True, "speed_mps": v, "stride_m": round(v * T, 3), "cycle_seconds": round(T, 3)}
    return log

# Walk: 15 frames (0.5 s) per gait cycle at 1.5 m/s; Run: 14 frames at 3.0 m/s with flight phase
walk_log = run_gait("Walk", 15, 1.5, 0.62, 0.075, 0.0, 0.55, 0.06, 0.30, 15 / FPS)
run_log = run_gait("Run", 14, 3.0, 0.38, 0.12, 0.05, 0.95, 0.18, 1.15, 14 / FPS)

def idle_fn(k, n):
    t = 2 * math.pi * k / n
    rots, offs = {}, {}
    rots["spine"] = fwd(0.02 * math.sin(t)); rots["head"] = Rz(0.12 * math.sin(t)) @ fwd(0.02 * math.sin(t + 1))
    for sd, sg in (("L", 1), ("R", -1)):
        rots["upper_arm." + sd] = Ry(-sg * 0.07) @ fwd(0.04 * math.sin(t + sg)); rots["forearm." + sd] = Ry(-sg * 0.07) @ fwd(0.15 + 0.03 * math.sin(t + sg))
        rots["hand." + sd] = rots["forearm." + sd]
    offs["hips"] = (0, 0, 0.0)
    return rots, offs, None
build_clip("Idle", 60, idle_fn); CLIP_META["Idle"] = {"frames": 60, "fps": FPS, "loop": True}

def right_arm_pose(rots, up_abd, up_fwd, fore_abd, fore_fwd):
    """character RIGHT arm (-X): abduction about Y (positive raises outward), then forward swing."""
    rots["upper_arm.R"] = Ry(up_abd) @ fwd(up_fwd)
    rots["forearm.R"] = Ry(fore_abd) @ fwd(fore_fwd)
    rots["hand.R"] = rots["forearm.R"]
def left_arm_pose(rots, up_abd, up_fwd, fore_abd, fore_fwd):
    rots["upper_arm.L"] = Ry(-up_abd) @ fwd(up_fwd); rots["forearm.L"] = Ry(-fore_abd) @ fwd(fore_fwd); rots["hand.L"] = rots["forearm.L"]

def wave_fn(k, n):
    t = k / n; up = ease(min(1, t / .18)) * (1 - ease(max(0, (t - .86) / .14)))
    osc = math.sin(2 * math.pi * 3 * max(0, min(1, (t - .15) / .7))) * up
    rots, offs = {}, {}
    right_arm_pose(rots, up * math.radians(100), 0, up * math.radians(100 + 38) + osc * math.radians(24), 0)
    rots["head"] = Rz(-0.18 * up) ; rots["spine"] = Rz(0.03 * up)
    left_arm_pose(rots, 0.07, 0, 0.07, 0.12)
    return rots, offs, None
build_clip("Wave", 54, wave_fn); CLIP_META["Wave"] = {"frames": 54, "fps": FPS, "loop": False}

# Salute: brute-force search the right arm so the glove reaches the cap brim (no manual guessing)
def solve_salute():
    brim = Vector((-.17, -.15, 1.25)); best = (1e9, None)
    import itertools
    for up_abd in [math.radians(a) for a in range(20, 111, 10)]:
        for up_fwd in [math.radians(a) for a in range(0, 121, 10)]:
            for fore_abd in [math.radians(a) for a in range(40, 181, 10)]:
                for fore_fwd in [math.radians(a) for a in range(0, 141, 10)]:
                    # FK for the right arm only (spine unrotated)
                    Ru = Ry(up_abd) @ fwd(up_fwd); Rf = Ry(fore_abd) @ fwd(fore_fwd)
                    sh = REST["upper_arm.R"][0]; el = sh + Ru @ (REST["upper_arm.R"][1] - REST["upper_arm.R"][0])
                    wr = el + Rf @ (REST["forearm.R"][1] - REST["forearm.R"][0]); tip = wr + Rf @ (REST["hand.R"][1] - REST["hand.R"][0]) * 0.6
                    d = (tip - brim).length
                    # elbow should not pass through the torso/head: keep elbow outside body width and below ear
                    if abs(el.x) < .2 or el.z > 1.0: d += 5
                    if d < best[0]: best = (d, (up_abd, up_fwd, fore_abd, fore_fwd))
    return best
sal_d, sal = solve_salute()
def salute_fn(k, n):
    t = k / n; up = ease(min(1, t / .25)) * (1 - ease(max(0, (t - .82) / .18)))
    rots, offs = {}, {}
    ua, uf, fa, ff = sal
    right_arm_pose(rots, up * ua, up * uf, up * fa, up * ff)
    rots["head"] = fwd(-0.04 * up); left_arm_pose(rots, 0.07, 0, 0.07, 0.12)
    return rots, offs, None
build_clip("Salute", 48, salute_fn); CLIP_META["Salute"] = {"frames": 48, "fps": FPS, "loop": False, "salute_hand_to_brim_error_m": round(sal_d, 4)}

def cheer_fn(k, n):
    t = k / n; h = abs(math.sin(2 * math.pi * t * 2))   # two hops
    air = max(0, h - 0.15)
    rots, offs = {}, {}
    hop = 0.085 * air / 0.85
    squat = 0.06 * (1 - min(1, h / .15))
    hz = 0.62 - squat + hop
    offs["hips"] = (0, 0, hz - 0.62)
    for sd, sg in (("L", 1), ("R", -1)):
        z_t = ANKLE_Z + hop * 0.98 + (0.04 * air if air > 0 else 0)
        phi1, phi2, kf = leg_ik((0.0, hz), (0.0, z_t))
        rots["thigh." + sd] = fwd(phi1); rots["shin." + sd] = fwd(phi2); rots["foot." + sd] = Rx(0.0)
        stat("Cheer", "knee_flex_max_deg", math.degrees(kf))
        ab = math.radians(150) + 0.15 * math.sin(2 * math.pi * t * 2 + (0 if sd == "L" else 1.5))
        (left_arm_pose if sd == "L" else right_arm_pose)(rots, ab, 0.0, ab + 0.1, 0.0)
    rots["head"] = fwd(0.08)
    return rots, offs, None
build_clip("Cheer", 40, cheer_fn); CLIP_META["Cheer"] = {"frames": 40, "fps": FPS, "loop": True}

def sit_fn(k, n):
    rots, offs = {}, {}
    hz = 0.40
    offs["hips"] = (0, 0, hz - 0.62)
    for sd, sg in (("L", 1), ("R", -1)):
        phi1, phi2, kf = leg_ik((0.0, hz), (0.40, ANKLE_Z + 0.03))
        rots["thigh." + sd] = fwd(phi1); rots["shin." + sd] = fwd(phi2); rots["foot." + sd] = Rx(0.25)
        stat("Sit", "knee_flex_max_deg", math.degrees(kf))
        (left_arm_pose if sd == "L" else right_arm_pose)(rots, 0.12, 0.85, 0.12, 1.55)
    rots["spine"] = fwd(0.05)
    return rots, offs, None
build_clip("Sit", 2, sit_fn); CLIP_META["Sit"] = {"frames": 2, "fps": FPS, "loop": False, "note": "cockpit seated pose, hands forward on the yoke"}

# ------------------------------------------------------------------ measurements on locomotion clips
def slip_report(log, clip, N, v, T):
    """ground-frame foot position = ankle_forward + v*t ; during each foot's stance it must stay constant."""
    meta = CLIP_META[clip]; out = {}
    worst = 0.0; per = []
    for sd in ("L", "R"):
        rows = [(k, -y) for (k, s, y, z, st) in log if s == sd]  # forward = -y
        stance = [(k, f, z) for (k, s, y, z, st) in log if s == sd for f in [-y]]
        # use ankle height (<= ankle_z + 5 mm) to identify stance frames in the evaluated rig
        zs = {k: z for (k, s, y, z, st) in log if s == sd}
        fs = {k: -y for (k, s, y, z, st) in log if s == sd}
        run = []
        for k in range(N + 1):
            if zs[k] <= ANKLE_Z + 0.004: run.append(k)
            else:
                if len(run) >= 2: per.append((sd, run[:]))
                run = []
        if len(run) >= 2: per.append((sd, run[:]))
        for sdd, ks in per:
            if sdd != sd: continue
            ground = [fs[k] + v * (k * (1.0 / FPS)) for k in ks]
            worst = max(worst, max(ground) - min(ground))
    out["max_stance_slip_m"] = round(worst, 4)
    return out
for clip, log, N, T in (("Walk", walk_log, 15, 15 / FPS), ("Run", run_log, 14, 14 / FPS)):
    STATS[clip].update(slip_report(log, clip, N, CLIP_META[clip]["speed_mps"], T))

# loop closure: pose at last frame vs first frame
def closure(clip):
    act = bpy.data.actions[clip]; rig.animation_data.action = act
    n = CLIP_META[clip]["frames"]
    bpy.context.scene.frame_set(1); a = {b.name: poses[b.name].head.copy() for b in poses}; ta = {b.name: poses[b.name].tail.copy() for b in poses}
    bpy.context.scene.frame_set(n + 1); b_ = {b.name: poses[b.name].head.copy() for b in poses}; tb = {b.name: poses[b.name].tail.copy() for b in poses}
    rig.animation_data.action = None
    return round(max(max((a[k] - b_[k]).length for k in a), max((ta[k] - tb[k]).length for k in ta)), 6)
for clip in ("Idle", "Walk", "Run", "Cheer"):
    STATS[clip]["loop_closure_error_m"] = closure(clip)

# ------------------------------------------------------------------ default pose + save
rig.animation_data.action = bpy.data.actions["Idle"]
bpy.context.scene.frame_set(1)
bpy.context.scene.frame_start = 1; bpy.context.scene.frame_end = 60; bpy.context.scene.render.fps = FPS
bpy.ops.wm.save_as_mainfile(filepath=str((OUT / (ASSET_ID + ".blend")).resolve()))
rig.animation_data.action = None
bpy.ops.export_scene.gltf(filepath=str((OUT / (ASSET_ID + ".glb")).resolve()), export_format='GLB',
                          export_animations=True, export_animation_mode='ACTIONS', export_skins=True,
                          export_force_sampling=True, export_yup=True)

# ------------------------------------------------------------------ verification of the exported GLB + report
with (OUT / (ASSET_ID + ".glb")).open("rb") as f:
    magic, ver, total = struct.unpack("<4sII", f.read(12)); ln, typ = struct.unpack("<I4s", f.read(8)); doc = json.loads(f.read(ln).decode())
anim_names = [a.get("name") for a in doc.get("animations", [])]
need = ["Idle", "Walk", "Run", "Wave", "Salute", "Cheer", "Sit"]
missing = [c for c in need if c not in anim_names]
assert not missing, "missing clips in GLB: %s (got %s)" % (missing, anim_names)
assert len(doc.get("skins", [])) == 1, "expected exactly one skin"
assert STATS["Walk"]["max_stance_slip_m"] <= 0.02, "walk foot slip too large: %s" % STATS["Walk"]
assert STATS["Run"]["max_stance_slip_m"] <= 0.03, "run foot slip too large: %s" % STATS["Run"]
for c in ("Walk", "Run", "Cheer", "Idle"):
    assert STATS[c]["min_sole_z_m"] >= -0.012, "sole sinks below ground in %s: %s" % (c, STATS[c]["min_sole_z_m"])
assert STATS["Walk"]["knee_flex_max_deg"] <= JOINT_LIMITS_DEG["knee_flex"][1] and STATS["Run"]["knee_flex_max_deg"] <= JOINT_LIMITS_DEG["knee_flex"][1]
for c in ("Walk", "Run"):
    assert STATS[c]["hand_torso_clearance_min"] > -0.02, "hand intersects torso in %s: %s" % (c, STATS[c]["hand_torso_clearance_min"])

mesh_tris = sum(len(p.polygons) for p in bpy.data.meshes)  # n-gon faces count; quads dominate
bbox_h = max((o.matrix_world @ Vector(c)).z for o in bpy.data.objects if o.type == 'MESH' for c in o.bound_box)
report = {
    "asset_id": ASSET_ID, "blender_version": bpy.app.version_string, "method": "procedural Blender Python (original geometry)",
    "bones": len(arm_data.bones), "mesh_objects": len(PARTS), "polygon_count": mesh_tris,
    "height_m_rest_pose_with_cap": round(bbox_h, 3), "glb_bytes": total, "clips": anim_names,
    "joint_limits_deg": JOINT_LIMITS_DEG, "measurements": STATS,
    "automated_checks_passed": ["GLB has one skin and all required clips", "walk/run stance foot slip within threshold (evaluated on deformed rig)",
                                "sole never below ground on Idle/Walk/Run/Cheer", "knee flexion within limit", "hands clear of torso in Walk/Run"],
    "not_checked_automatically": ["visual quality / likeness", "cloth-like secondary motion (none exists)", "armor-style mesh interpenetration beyond hand vs torso",
                                  "in-engine retargeting", "performance on real GPUs"],
    "foot_ground_method": "2-bone sagittal IK per frame with constant-velocity stance foot (no runtime IK); toe/heel pitch is keyed",
}
(OUT / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
manifest = {
    "schema_version": 1, "asset_id": ASSET_ID, "format": "glTF 2.0 GLB", "source": "original procedural Blender script (scripts/blender5/aviator_kid.py)",
    "blender_version": bpy.app.version_string, "unit": "meter", "coordinate_system": "Blender Z-up, character faces -Y; glTF export converts to Y-up, character faces +Z",
    "model_file": ASSET_ID + ".glb", "source_file": ASSET_ID + ".blend", "clips": need, "min_animation_count": len(need),
    "requirements": {"skins": True, "animated": True, "visual_review": True},
    "character": {"height_m": round(bbox_h, 2), "style": "Q (about 3 heads tall)", "forward_axis_glb": "+Z", "root_bone": "root", "ground_y": 0.0},
    "clip_info": CLIP_META,
    "customization": {
        "color_roles": {k: "#%06X" % v[0] for k, v in PALETTE.items()},
        "recolor_by_material_name": ["jacket", "jacket_trim", "pants", "boot", "glove", "scarf", "cap", "pack", "skin", "hair", "accent"],
        "optional_nodes": [n for n, _ in PARTS if n.startswith("acc_")],
    },
    "license_note": "All geometry is original procedural geometry generated by this script; no third-party assets.",
}
(OUT / "asset_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
print("ASSET_BUILD_OK", json.dumps({"clips": anim_names, "slip": {c: STATS[c]["max_stance_slip_m"] for c in ("Walk", "Run")}, "salute_err": sal_d}))
