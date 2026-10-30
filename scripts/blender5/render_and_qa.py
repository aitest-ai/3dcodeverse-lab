"""Inspect a Blender 5 rig at *every* frame and render three viewpoints per clip.
Invoked from CI: blender -b --python render_and_qa.py -- outputs
The diagnostics quantify deficiencies; this is not automatic proof of good motion.
"""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
folder = Path(args[0] if args else "outputs").resolve()
manifest = json.loads((folder / "asset_manifest.json").read_text(encoding="utf-8"))
source = folder / manifest["source_file"]
bpy.ops.wm.open_mainfile(filepath=str(source))
rig = bpy.data.objects.get("MechaRig")
if rig is None or rig.type != "ARMATURE":
    raise RuntimeError("Expected MechaRig armature in the saved Blender scene.")
scene = bpy.context.scene
data = rig.animation_data
if data is None:
    raise RuntimeError("MechaRig has no animation data.")
for track in data.nla_tracks:
    track.mute = True

preview_dir = folder / "previews"
preview_dir.mkdir(exist_ok=True)

def choose_action(clip):
    # Asset manifest uses the exact exported glTF clip name. Avoid double prefix.
    name = clip if clip.startswith("Mecha_") else "Mecha_" + clip
    action = bpy.data.actions.get(name)
    if action is None:
        raise RuntimeError("Missing Blender action: " + name)
    data.action = action
    # Blender 5 supports layered Actions; explicitly choose the Object slot.
    slots = getattr(action, "slots", None)
    if slots and len(slots):
        candidates = [slot for slot in slots
                      if getattr(slot, "target_id_type", "OBJECT") == "OBJECT"]
        data.action_slot = candidates[0] if candidates else slots[0]
    scene.frame_set(1)

def point_in_world(bone_name, rest_point):
    pose = rig.pose.bones[bone_name]
    rest_inv = rig.data.bones[bone_name].matrix_local.inverted()
    return rig.matrix_world @ pose.matrix @ rest_inv @ Vector(rest_point)

def foot_samples(side):
    x = .27 if side == "L" else -.27
    return [point_in_world("foot." + side, (x + dx, y, .009))
            for dx in (-.18, .18) for y in (-.40, .12)]

def diagnostics():
    samples = []
    warnings = []
    prev = {}
    for clip in manifest.get("clips", []):
        choose_action(clip)
        for frame in range(scene.frame_start, scene.frame_end + 1):
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            for side in ("L", "R"):
                sole = foot_samples(side)
                lowest = min(p.z for p in sole)
                sole_center = sum(sole, Vector((0.0, 0.0, 0.0))) / len(sole)
                thigh = rig.pose.bones["thigh." + side]
                shin = rig.pose.bones["shin." + side]
                upper = (thigh.tail - thigh.head).normalized()
                lower = (shin.tail - shin.head).normalized()
                bend = math.degrees(math.acos(max(-1.0, min(1.0, upper.dot(lower)))))
                grounded = lowest <= .035
                displacement = 0.0
                key = (clip, side)
                if grounded and key in prev and prev[key]["grounded"]:
                    delta = sole_center - prev[key]["center"]
                    displacement = math.hypot(delta.x, delta.y)
                prev[key] = {"grounded": grounded, "center": sole_center}
                rec = {"clip": clip, "frame": frame, "side": side,
                       "sole_z_m": round(lowest, 5),
                       "knee_flex_deg": round(bend, 2),
                       "stance_drift_m": round(displacement, 5),
                       "grounded": grounded}
                samples.append(rec)
                if lowest < -.01:
                    warnings.append("Sole penetrates ground: " + str(rec))
                if bend > 125:
                    warnings.append("Knee flexion over 125 degrees: " + str(rec))
    return samples, warnings

samples, warnings = diagnostics()
totals = {}
for clip in manifest["clips"]:
    selected = [v for v in samples if v["clip"] == clip]
    totals[clip] = {
        "min_sole_z_m": min(v["sole_z_m"] for v in selected),
        "max_knee_flex_deg": max(v["knee_flex_deg"] for v in selected),
        "max_grounded_slide_per_frame_m": max(v["stance_drift_m"] for v in selected),
        "total_grounded_slide_m": round(sum(v["stance_drift_m"] for v in selected), 4),
        "samples": len(selected),
    }
qa = {
    "source": manifest["source_file"],
    "method": "Blender scene evaluated at every frame; floor at world Z=0",
    "caveat": "Approximate sole corners; not a mesh-mesh collision test or full physical IK.",
    "animation_ranges": [scene.frame_start, scene.frame_end],
    "samples": samples,
    "summary": totals,
    "warnings": warnings[:100],
    "warning_count": len(warnings),
    "foot_slide_review_required": any(
        item["max_grounded_slide_per_frame_m"] > 0.015 for item in totals.values()),
    "ground_penetration_pass": all(s["sole_z_m"] >= -.01 for s in samples),
}
(folder / "motion_qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")

# Create simple studio previews without changing the exported GLB or .blend.
bpy.ops.mesh.primitive_plane_add(size=30)
floor = bpy.context.object
floor.name = "QA_ground_not_exported"
floor.location.z = -.025
floor_material = bpy.data.materials.new("QA_ground_gray")
floor_material.diffuse_color = (.34, .38, .44, 1)
floor.data.materials.append(floor_material)
cam_data = bpy.data.cameras.new("QA_orthographic")
cam = bpy.data.objects.new("QA_orthographic", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam_data.type = "ORTHO"
cam_data.ortho_scale = 3.45

scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.show_shadows = True
scene.render.resolution_x = 512
scene.render.resolution_y = 512
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.image_settings.color_mode = "RGBA"

angles = {
    "front": (0, -6.0, 2.15),
    "side": (6.0, -.15, 2.15),
    "isometric": (4.5, -5.0, 3.05),
}
frames = {"Idle": 1, "Run": 13, "Punch": 25, "Dodge": 25}
image_records = []
for clip in manifest["clips"]:
    choose_action(clip)
    scene.frame_set(frames.get(clip.removeprefix("Mecha_"), 25))
    for name, xyz in angles.items():
        cam.location = xyz
        target = Vector((0, 0, 1.17))
        cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
        path = preview_dir / (clip.lower() + "_" + name + ".png")
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError("Preview image was not written: " + str(path))
        image_records.append({"clip": clip, "view": name,
                              "file": str(path.relative_to(folder))})
(folder / "preview_index.json").write_text(
    json.dumps(image_records, ensure_ascii=False, indent=2), encoding="utf-8")
# Render images before failing, so the evidence remains in Actions artifacts.
if not qa["ground_penetration_pass"]:
    raise RuntimeError(
        "Ground penetration detected in saved .blend animation; see motion_qa.json")
print("MOTION_QA_FINISHED", json.dumps({"frames": len(samples),
                                     "warnings": len(warnings),
                                     "previews": len(image_records)}))
