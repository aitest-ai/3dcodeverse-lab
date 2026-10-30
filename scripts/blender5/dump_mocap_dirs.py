"""Dump per-frame joint positions of the CC0 UAL jog/walk loops (UE-mannequin skeleton) as JSON, so the Q-style kid can be driven by real mocap.
Run: ASSET_SRC=<dir with ubc/ and ual1.glb> blender -b --factory-startup --python scripts/blender5/dump_mocap_dirs.py   -> data/mocap_dirs.json"""
import bpy, json, os
from pathlib import Path
SRC = Path(os.environ.get("ASSET_SRC", "assets_src")); OUT = Path(os.environ.get("ASSET_OUT", "data/mocap_dirs.json"))
bpy.ops.import_scene.gltf(filepath=str(SRC / "ubc/Base Characters/Godot - UE/Superhero_Male_FullBody.gltf"))
rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
base = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=str(SRC / "ual1.glb"))
for o in list(bpy.data.objects):
    if o not in base: bpy.data.objects.remove(o, do_unlink=True)
rig.animation_data_create()
NEED = ["pelvis", "spine_01", "spine_03", "neck_01", "Head", "clavicle_l", "clavicle_r", "upperarm_l", "upperarm_r", "lowerarm_l", "lowerarm_r", "hand_l", "hand_r",
        "thigh_l", "thigh_r", "calf_l", "calf_r", "foot_l", "foot_r", "ball_l", "ball_r"]
out = {}
for src, name in (("Jog_Fwd_Loop", "Run"), ("Walk_Loop", "Walk")):
    a = bpy.data.actions[src]; rig.animation_data.action = a
    if a.slots: rig.animation_data.action_slot = a.slots[0]
    f0, f1 = int(a.frame_range[0]), int(a.frame_range[1]); frames = []
    for f in range(f0, f1):   # loop clip: last frame repeats the first
        bpy.context.scene.frame_set(f); bpy.context.view_layer.update(); row = {}
        for b in NEED:
            pb = rig.pose.bones[b]; row[b] = [round(c, 5) for c in (rig.matrix_world @ pb.head)]
            if b == "Head": row["Head_tail"] = [round(c, 5) for c in (rig.matrix_world @ pb.tail)]
        frames.append(row)
    out[name] = {"fps": 24, "frames": frames}
OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(out))
print("DUMP_OK", {k: len(v["frames"]) for k, v in out.items()})
