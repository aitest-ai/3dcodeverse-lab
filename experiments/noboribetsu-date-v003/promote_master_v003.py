"""Promote frozen V002 master to a source-native V003 master inside Blender 5.2.3 LTS.

Expected usage:
  export NOBORIBETSU_PROJECT_ROOT=/path/to/Noboribetsu_Date_V002
  blender -b "$NOBORIBETSU_PROJECT_ROOT/authoring/date_v002_master.blend" \
    --python experiments/noboribetsu-date-v003/promote_master_v003.py

The V002 project root is intentionally external to this public repository.
The script never overwrites V002.
"""
from __future__ import annotations

import gc
import hashlib
import importlib.util
import json
import os
from pathlib import Path

import bpy
from mathutils import Vector

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(os.environ.get("NOBORIBETSU_PROJECT_ROOT", Path.cwd())).resolve()

V002_SHA = "1d7637c7dd98642ffbfa03074fa6f3af50339a5e965afc2feb47e1ed86567ee1"
BASE = PROJECT_ROOT / "authoring/date_v002_master.blend"
OUT = PROJECT_ROOT / "authoring/date_v003_master.blend"
MODEL = PROJECT_ROOT / "models/scene_B_native_v003.glb"
EVID = PROJECT_ROOT / "evidence/v003_native"
QA = PROJECT_ROOT / "qa/v003_native_blender_replay.json"
EVID.mkdir(parents=True, exist_ok=True)
QA.parent.mkdir(parents=True, exist_ok=True)

os.environ["NOBORIBETSU_PROJECT_ROOT"] = str(PROJECT_ROOT)

spec = importlib.util.spec_from_file_location(
    "refine_scene_v003_blender",
    SCRIPT_DIR / "refine_scene_v003_blender.py",
)
assert spec and spec.loader
v3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v3)


def sha(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


assert BASE.exists(), f"V002 master missing: {BASE}"
assert sha(BASE) == V002_SHA, "Frozen V002 master hash mismatch"

if not bpy.data.filepath or Path(bpy.data.filepath).resolve() != BASE.resolve():
    bpy.ops.wm.open_mainfile(filepath=str(BASE))

report = v3.apply_all()

# V002 intentionally carries nine packed, currently-unreferenced ground-source
# textures for future authoring. Blender may drop zero-user datablocks on
# save/reopen, so give only those already-packed zero-user images a Fake User.
# This preserves source bytes/resolution; it does not connect them to materials.
preserved_packed_zero_user_images = []
for image in bpy.data.images:
    if image.packed_file and image.users == 0:
        image.use_fake_user = True
        preserved_packed_zero_user_images.append(image.name)
report["preserved_packed_zero_user_images"] = sorted(preserved_packed_zero_user_images)

scene = bpy.context.scene
scene["project"] = "Noboribetsu Date Jidaimura V003"
scene["v003_scope"] = (
    "Same V002 core; material/noren/render-only edge refinements. "
    "No expansion. Third person disabled."
)
scene["v003_constraints"] = json.dumps(report["constraints"], ensure_ascii=False)

bpy.ops.file.pack_all()
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), compress=False)

# Export B only, while A remains untouched in the saved master.
A = bpy.data.collections.get("A_DATA_SKELETON")
B = bpy.data.collections.get("B_SITE_REFINEMENT")
assert A and B
A.hide_viewport = True
A.hide_render = True
B.hide_viewport = False
B.hide_render = False

bpy.ops.object.select_all(action="DESELECT")
deps = bpy.context.evaluated_depsgraph_get()
temp = bpy.data.collections.new("_V003_EXPORT_TEMP")
scene.collection.children.link(temp)
copies = []

for obj in B.all_objects:
    if obj.type not in {"MESH", "CURVE", "FONT"} or obj.hide_render:
        continue
    evaluated = obj.evaluated_get(deps)
    mesh = bpy.data.meshes.new_from_object(
        evaluated,
        preserve_all_data_layers=True,
        depsgraph=deps,
    )
    mesh.transform(obj.matrix_world)
    copy_obj = bpy.data.objects.new(obj.name + "_v003_export", mesh)
    temp.objects.link(copy_obj)
    copies.append(copy_obj)

assert copies, "No B objects available for export"
for obj in copies:
    obj.select_set(True)
bpy.context.view_layer.objects.active = copies[0]
bpy.ops.object.join()
merged = bpy.context.object
merged.name = "B_SITE_REFINEMENT_V003_compiled"

bpy.ops.export_scene.gltf(
    filepath=str(MODEL),
    export_format="GLB",
    use_selection=True,
    export_apply=True,
    export_yup=True,
    export_extras=True,
    export_materials="EXPORT",
    export_cameras=False,
    export_lights=False,
)

bpy.data.objects.remove(merged, do_unlink=True)
bpy.data.collections.remove(temp)
for mesh in list(bpy.data.meshes):
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)
gc.collect()

# Re-open the actually saved V003 master before producing evidence.
bpy.ops.wm.open_mainfile(filepath=str(OUT))
scene = bpy.context.scene
A = bpy.data.collections["A_DATA_SKELETON"]
B = bpy.data.collections["B_SITE_REFINEMENT"]
cam = bpy.data.objects["AB_identical_camera"]

cameras = [
    {"id": "gate_front", "position": [0.4, 23, 2.2], "target": [0, 0, 2.15], "lens": 34},
    {"id": "gate_oblique", "position": [14, 18, 6.3], "target": [0, -2, 2.1], "lens": 33},
    {"id": "street", "position": [-4, -7, 2.0], "target": [4, -23, 2.6], "lens": 31},
]

for camera_spec in cameras:
    cam.location = camera_spec["position"]
    cam.rotation_euler = (
        Vector(camera_spec["target"]) - cam.location
    ).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = camera_spec["lens"]
    for collection, stage in ((A, "A"), (B, "B")):
        A.hide_render = stage != "A"
        B.hide_render = stage != "B"
        scene.render.filepath = str(EVID / f"{camera_spec['id']}_{stage}.png")
        bpy.ops.render.render(write_still=True)

report["v002_master_sha256"] = V002_SHA
report["v003_master_sha256"] = sha(OUT)
report["native_B_sha256"] = sha(MODEL)
report["project_root"] = str(PROJECT_ROOT)
QA.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V003_NATIVE_PROMOTION_COMPLETE", json.dumps(report, ensure_ascii=False))
