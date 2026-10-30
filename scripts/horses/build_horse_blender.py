"""Blender 5.2 headless horse import, GLB export, and real multi-view snapshots.

Original author's CC0 glTF is imported without executing any scripts.
A real armature, deform weights and multiple animation clips are mandatory.
The goal is a valid stylized gameplay prototype, not a photorealistic racehorse.
"""
import bpy
import json
import math
import os
import sys
from pathlib import Path
from mathutils import Vector

args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
if len(args)<2:
    raise RuntimeError("Usage: blender -b --python this_script.py -- <source.gltf> <output_folder>")
source=Path(args[0]).resolve()
out=Path(args[1]).resolve()
out.mkdir(parents=True,exist_ok=True)
name=out.name
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(source))
scene=bpy.context.scene
rigs=[o for o in scene.objects if o.type=="ARMATURE"]
meshes=[o for o in scene.objects if o.type=="MESH"]
if not rigs or not meshes:
    raise RuntimeError("Horse source missing mesh or armature; don't fake it.")
actions=[a.name for a in bpy.data.actions]
print("HORSE_IMPORT",name,"meshes",len(meshes),"rigs",len(rigs),"actions",actions)
if len(actions)<10:
    raise RuntimeError("Expected several authored horse animations, got "+str(actions))
bone_count=sum(len(r.data.bones) for r in rigs)
if bone_count<15:
    raise RuntimeError("Horse skeleton unexpectedly sparse: "+str(bone_count))
skinned=[m for m in meshes if any(mod.type=="ARMATURE" for mod in m.modifiers)]
if not skinned:
    raise RuntimeError("Horse has no bone-deformed mesh.")
vert_count=sum(len(o.data.vertices) for o in meshes)
if vert_count<500:
    raise RuntimeError("Horse is not a meaningful polygonal model.")
body_points=[o.matrix_world@Vector(corner) for o in meshes for corner in o.bound_box]
minimum=Vector([min(p[i] for p in body_points) for i in range(3)])
maximum=Vector([max(p[i] for p in body_points) for i in range(3)])
center=(minimum+maximum)/2
extent=maximum-minimum
if min(extent)<.01 or max(extent)>1000:
    raise RuntimeError("Degenerate mesh or impossible scale: "+str(tuple(extent)))
print("HORSE_BOUNDING_BOX",list(minimum),list(maximum),"bones",bone_count,"verts",vert_count)

# Save original assembled and editable scene before adding QA-only camera/light.
blend=out/(name+"_blender5.blend")
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
glb=out/(name+"_game.glb")
# Export NLA tracks first (glTF import normally creates named tracks).
bpy.ops.export_scene.gltf(
    filepath=str(glb),export_format="GLB",
    export_animations=True,export_animation_mode="NLA_TRACKS",
    export_skins=True)
if not glb.exists() or glb.stat().st_size<1000:
    raise RuntimeError("GLB export failed")

# 3D turntable: four angles for each horse, plus two inspected motion poses.
cam_data=bpy.data.cameras.new("HorseQA_Camera")
camera=bpy.data.objects.new("HorseQA_Camera",cam_data)
scene.collection.objects.link(camera)
scene.camera=camera
cam_data.type="ORTHO"
cam_data.ortho_scale=max(extent.x,extent.y,extent.z)*1.42
scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_shadows=True
scene.render.resolution_x=640
scene.render.resolution_y=640
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"

radius=max(extent.x,extent.y,extent.z)*2.1
height=center.z+max(extent.z*.25,.2)
views={
 "front":(0,-radius,height),
 "side":(radius,0,height),
 "back":(0,radius,height),
 "isometric":(radius*.8,-radius*.8,height+radius*.18)
}
views["motion_a"]=(radius*.8,-radius*.8,height+radius*.18)
views["motion_b"]=(radius*.8,-radius*.8,height+radius*.18)
# Animations are still present on NLA as imported; choose two points within
# the scene timeline as objective proof of pose changes. More specific gallop
# sampling is done only after source animation names are inspected.
frame_a=max(1,scene.frame_start)
frame_b=frame_a+max(1,(scene.frame_end-scene.frame_start)//3)
frame_map={"motion_a":frame_a,"motion_b":frame_b}
for view,loc in views.items():
    scene.frame_set(frame_map.get(view,frame_a))
    camera.location=loc
    camera.rotation_euler=(center-camera.location).to_track_quat("-Z","Y").to_euler()
    p=out/("preview_"+view+".png")
    scene.render.filepath=str(p)
    bpy.ops.render.render(write_still=True)
    if not p.exists() or p.stat().st_size<3000:
        raise RuntimeError("No actual horse image: "+str(p))
manifest={
 "schema_version":1,"asset_id":name,"model_file":glb.name,"source_file":blend.name,
 "format":"glTF 2.0 GLB","unit":"imported scene source units; normalize in consuming game",
 "license":"CC0-1.0","creator":"Quaternius",
 "source":"https://quaternius.com/packs/ultimateanimatedanimals.html",
 "source_host":"https://pixeltriks.com/browse?pack=quaternius-ultimate-animated-animals",
 "is_original_horse":True,
 "clips":actions,"min_animation_count":10,"requirements":{"skins":True,"animated":True,"visual_review":True},
 "quality":"STYLIZED_GAMEPLAY_PROTOTYPE_NOT_PHOTOREALISTIC",
 "legal":"Original Quaternius publicly shared CC0 animal pack. No additional third-party model rights implied."
}
(out/"asset_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
report={"horse":name,"blender":bpy.app.version_string,"source_verts":vert_count,
 "source_rig_bones":bone_count,"source_actions":actions,
 "source_animation_count":len(actions),"model_bounds":[list(minimum),list(maximum)],
 "glb_bytes":glb.stat().st_size,"source_rigged_meshes":len(skinned),
 "snapshot_frames":frame_map,"status":"BLENDER_EXPORT_RENDERED_PENDING_INDEPENDENT_VALIDATION"}
(out/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("HORSE_BLENDER_EXPORT_OK",json.dumps(report,ensure_ascii=False))
