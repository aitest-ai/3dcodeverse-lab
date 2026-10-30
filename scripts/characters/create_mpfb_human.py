"""MPFB 2.0.18 + Blender 5.2 headless integration smoke test.

Uses upstream HumanService, not a fake human constructed from boxes.
Model is a neutral topology/rig test body. It is NOT a finished photorealistic
avatar: realistic hair, clothing and face textures need licensed asset packs.
Outputs: rigged human GLB + editable BLEND + 4 orthographic studio renders.
"""
import bpy
import sys
import math
import json
import importlib
import os
from pathlib import Path
from mathutils import Vector

OUT = Path(os.environ.get("ASSET_OUT", "outputs/human_mpfb")).resolve()
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

# Blender's packaged extensions use unknown module paths. Find the MPFB service
# by its declared suffix, exactly as MPFB's official script samples document.
def service(module_suffix, symbol):
    matching = [m for m in tuple(sys.modules) if m.endswith(module_suffix)]
    if len(matching) != 1:
        raise RuntimeError(f"Expected active MPFB module ending {module_suffix}; found {matching}. Check extension installation.")
    module = importlib.import_module(matching[0])
    return getattr(module, symbol)

try:
    bpy.ops.preferences.addon_enable(module="bl_ext.local_mpfb.mpfb")
except Exception as e:
    print("Enable addon attempt:", str(e))
try:
    import bl_ext.local_mpfb.mpfb   # The registered Blender extension module
except ImportError as e:
    raise RuntimeError("MPFB must be installed/enabled as 'bl_ext.local_mpfb.mpfb'") from e

HumanService = service("mpfb.services.humanservice", "HumanService")

print("MPFB creating real MakeHuman basemesh")
body = HumanService.create_human(mask_helpers=True, extra_vertex_groups=True, feet_on_ground=True, scale=0.1)
assert body and body.type == "MESH", "MPFB did not return a human mesh"
body.name = "Human_Body_MakeHumanTopology"
print("MPFB adding game-engine rig")
rig = HumanService.add_builtin_rig(body, "game_engine")
assert rig and rig.type == "ARMATURE", "MPFB built-in rig creation failed"
rig.name = "Human_GameRig"

# Material exists in the glTF 2.0 payload. It is an editable neutral skin test,
# deliberately not falsely marketed as scanned skin.
skin = bpy.data.materials.new("NeutralSkin_PBR_TestOnly")
skin.use_nodes = True
skin.diffuse_color = (0.47, 0.27, 0.21, 1)
bsdf = skin.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.47, 0.27, 0.21, 1)
bsdf.inputs["Roughness"].default_value = 0.62
bsdf.inputs["Metallic"].default_value = 0
body.data.materials.clear()
body.data.materials.append(skin)

# Optional official CC0 asset pack: real textures, eyes, hair and clothing.
# Download the upstream 267 MB archive only on isolated CI runners; never
# commit it to this repository or silently fetch third-party assets at runtime.
asset_root = os.environ.get("MAKEHUMAN_ASSET_ROOT")
added_objects = []
asset_records = []
if asset_root:
    root = Path(asset_root)
    if not root.is_dir():
        raise RuntimeError("MAKEHUMAN_ASSET_ROOT not found: " + str(root))
    def asset_file(name):
        matches = list(root.rglob(name))
        if not matches:
            raise RuntimeError("CC0 system pack missing required asset: " + name)
        return str(matches[0].resolve())
    skin_name = "young_caucasian_female.mhmat"
    HumanService.set_character_skin(asset_file(skin_name), body, skin_type="GAMEENGINE")
    asset_records.append({"file": skin_name, "category": "skins", "license": "CC0"})
    items = [
        ("eyes", "low-poly.mhclo", "Eyes"),
        ("eyebrows", "eyebrow001.mhclo", "Eyebrows"),
        ("eyelashes", "eyelashes01.mhclo", "Eyelashes"),
        ("tongue", "tongue01.mhclo", "Tongue"),
        ("teeth", "teeth_base.mhclo", "Teeth"),
        ("hair", "long01.mhclo", "Hair"),
        ("clothes", "female_casualsuit01.mhclo", "Clothes"),
        ("clothes", "shoes01.mhclo", "Clothes"),
    ]
    for subdir, filename, kind in items:
        path = asset_file(filename)
        print("LOADING_CC0_ASSET", subdir, path)
        item = HumanService.add_mhclo_asset(
            path, body, asset_type=kind, subdiv_levels=0,
            material_type="GAMEENGINE")
        if item is None:
            raise RuntimeError("Failed to add asset " + filename)
        added_objects.append(item)
        asset_records.append({"file": filename, "category": subdir, "license": "CC0"})
    print("LOADED_CC0_ASSETS", [x["file"] for x in asset_records])
else:
    print("NO_SYSTEM_ASSET_PACK: neutral body only")

# MakeHuman can contain large helper groups. Verify final geometry while
# preserving original topological detail rather than simplifying it away.
for polygon in body.data.polygons:
    polygon.use_smooth = True

bpy.context.view_layer.update()
minz = min((body.matrix_world @ v.co).z for v in body.data.vertices)
maxz = max((body.matrix_world @ v.co).z for v in body.data.vertices)
height = maxz - minz
print("HUMAN_BASE_HEIGHT", height, "verteces", len(body.data.vertices))
if not 1.0 < height < 2.4:
    raise RuntimeError(f"Unexpected human height {height:.3f}m. Inspect MPFB scaling; do not auto export in wrong units.")
bone_count = len(rig.data.bones)
if bone_count < 30:
    raise RuntimeError(f"Human rig has only {bone_count} bones; expected hand/leg spine skeleton.")
if not any(m.type == "ARMATURE" for m in body.modifiers):
    raise RuntimeError("MPFB body has no armature modifier.")
if len(body.vertex_groups) < 20:
    raise RuntimeError("MPFB body missing deforming weights.")

# Save pure source scene, before adding non-export studio camera/background.
blend = OUT / "human_mpfb_blender5.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.object.select_all(action="DESELECT")
rig.select_set(True)
body.select_set(True)
for asset_obj in added_objects:
    asset_obj.select_set(True)
bpy.context.view_layer.objects.active=rig
glb = OUT / "human_mpfb_blender5.glb"
bpy.ops.export_scene.gltf(
    filepath=str(glb),
    export_format="GLB",
    use_selection=True,
    export_animations=False,
    export_skins=True,
    export_apply=False,
)
if not glb.exists() or glb.stat().st_size < 10000:
    raise RuntimeError("Human GLB missing or unusually tiny")

manifest = {
  "schema_version":1, "asset_id":"human_mpfb_blender5",
  "format":"glTF 2.0 GLB", "unit":"meter",
  "coordinate_system":"Blender Z-up; GLB Y-up on import",
  "model_file":glb.name, "source_file":blend.name,
  "clips":[], "min_animation_count":0,
  "requirements":{"skins":True,"animated":False,"visual_review":True},
  "source":"MakeHuman Community MPFB 2.0.18; Blender 5.2.3",
  "license_note":"MPFB plugin GPLv3+; MPFB bundled core geometry/data CC0. This model uses original authored neutral test material. Verify upstream files/licensing before commercial asset publication.",
  "quality_status":"LICENSED_ASSET_CHARACTER_NEEDS_VISUAL_REVIEW" if asset_records else "BASEMESH_AND_RIG_TEST_NOT_PHOTOREAL_READY",
  "features":["human topology","deform skeleton","PBR skin","licensed CC0 assets" if asset_records else "neutral test skin"],
  "asset_sources":[{"source_url":"https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html", "license":"CC0","assets":asset_records}] if asset_records else [],
  "missing_before_high_quality":["premium hair strand detail","real skin microdetail","expressions","manual garment and joint deformation QA"] if asset_records else ["photorealistic skin details","eyes/eyelashes","hair","clothing","facial expressions"]
}
(OUT/"asset_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
report={
    "blender":bpy.app.version_string,"source_extension":"MPFB 2.0.18",
    "body_vertices":len(body.data.vertices),"body_faces":len(body.data.polygons),
    "height_m":round(height,4),"rig_bones":bone_count,
    "weight_groups":len(body.vertex_groups),
    "glb_bytes":glb.stat().st_size, "asset_count":len(added_objects), "asset_details":asset_records,
    "status":"PENDING_RENDER_AND_GLTF_INSPECTION",
}
(OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")

# Orthographic turntable studio views: direct evidence instead of AI illustration.
cam_data=bpy.data.cameras.new("QA_Camera")
cam=bpy.data.objects.new("QA_Camera",cam_data)
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera=cam
cam_data.type="ORTHO"
cam_data.ortho_scale=2.45
scene=bpy.context.scene
if asset_records:
    # Workbench ignores most diffuse textures. Use Cycles CPU to demonstrate
    # the actual PBR skin, clothes and hair maps from glTF, not grey clay.
    scene.render.engine="CYCLES"
    scene.cycles.device="CPU"
    scene.cycles.samples=20
    scene.render.resolution_x=512
    scene.render.resolution_y=512
    scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value=(0.24,0.27,0.32,1)
    bg.inputs["Strength"].default_value=0.8
    for name,location,power,size in (
        ("Key_Area",(3.0,-4.0,5.5),650.0,3.5),
        ("Fill_Area",(-4.0,-2.5,3.5),380.0,4.0),
        ("Rim_Area",(1.5,3.8,4.0),500.0,3.0),
    ):
        lamp=bpy.data.lights.new(name,"AREA")
        obj=bpy.data.objects.new(name,lamp)
        scene.collection.objects.link(obj)
        obj.location=location
        obj.rotation_euler=(Vector((0,0,1.1))-obj.location).to_track_quat("-Z","Y").to_euler()
        lamp.energy=power
        lamp.shape="DISK"
        lamp.size=size
else:
    scene.render.engine="BLENDER_WORKBENCH"
    scene.display.shading.light="STUDIO"
    scene.display.shading.color_type="MATERIAL"
    scene.display.shading.show_shadows=True
    scene.render.resolution_x=640
    scene.render.resolution_y=640
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
views={"front":(0,-5.5,1.2),"side":(5.5,0,1.2),
       "back":(0,5.5,1.2),"isometric":(4.6,-4.6,2.45)}
for name,loc in views.items():
    cam.location=loc
    target=Vector((0,0,0.95))
    cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
    path=OUT/("preview_"+name+".png")
    scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    if not path.exists() or path.stat().st_size < 5000:
        raise RuntimeError("Cannot render real Blender preview: "+str(path))
print("MPFB_HUMAN_SMOKE_SUCCEEDED",report)
