"""Horse V2: geometry and material polish on the ORIGINAL, already-rigged .blend.

Non-destructive to published V1. Subdivision is applied BEFORE the armature
and keeps interpolated vertex weights, all 13 NLA animations and CC0 source.
Exports truthful glTF-compatible PBR factors and real Cycles studio previews.
No photo-grade realism is claimed. No source textures are invented.
"""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
if len(args)!=2:
    raise RuntimeError("Usage: blender --python polish_horse_v2.py -- SOURCE_DIR OUTPUT_DIR")
source=Path(args[0]).resolve()
out=Path(args[1]).resolve()
out.mkdir(parents=True,exist_ok=True)
horse=source.name
blend_src=source/(horse+"_blender5.blend")
if not blend_src.is_file():
    raise FileNotFoundError("Source .blend missing: "+str(blend_src))
bpy.ops.wm.open_mainfile(filepath=str(blend_src))
scene=bpy.context.scene
rigs=[o for o in scene.objects if o.type=="ARMATURE"]
meshes=[o for o in scene.objects if o.type=="MESH"]
if len(rigs)!=1 or len(meshes)!=1:
    raise RuntimeError("Expected exactly one original Quaternius rigged horse")
rig=rigs[0]
body=meshes[0]
if not any(m.type=="ARMATURE" for m in body.modifiers):
    raise RuntimeError("Source skinning is missing")
source_actions=sorted(a.name for a in bpy.data.actions)
if len(source_actions)!=13 or "Gallop" not in source_actions:
    raise RuntimeError("Refuse source without all 13 original actions")
source_bones=len(rig.data.bones)
source_vertices=len(body.data.vertices)
if source_bones!=50:raise RuntimeError("Unexpected source bone count")
print("HORSE_V2_BASELINE",horse,source_vertices,source_bones,source_actions,flush=True)

# Smooth only the coat/body, not the small hard-edged hoof polygons. The
# original source geometry is not altered until a real Subsurf evaluation.
soft={"Main","Main_Dark","Main_Light","Muzzle","Hair"}
for polygon in body.data.polygons:
    mat=body.data.materials[polygon.material_index]
    polygon.use_smooth=mat is not None and mat.name in soft

bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active=body
sub=body.modifiers.new("HorseV2_OneLevelSmoothTopology","SUBSURF")
sub.subdivision_type="CATMULL_CLARK"
sub.levels=1
sub.render_levels=1
# Move modifier ahead of original armature so applied subdivision preserves
# correct rest-pose weights rather than baking an animated deformation.
while body.modifiers[0] != sub:
    bpy.ops.object.modifier_move_up(modifier=sub.name)
bpy.ops.object.modifier_apply(modifier=sub.name)
new_vertices=len(body.data.vertices)
if new_vertices < source_vertices*1.6:
    raise RuntimeError("Subdivision did not add expected true mesh detail")
if not any(m.type=="ARMATURE" for m in body.modifiers):
    raise RuntimeError("Subdivision accidentally discarded skin modifier")
if not body.vertex_groups:
    raise RuntimeError("Subdivision discarded joint influences")

# Upgrade to physically plausible dielectric PBR. Since the original horse
# has NO UV image textures, avoid Blender-only noise nodes that would be lost
# in a GLB. Every change below is representable in the glTF 2.0 material.
color_overrides={
    "Horse":{
      "Main":(.23,.085,.035,1),
      "Main_Dark":(.105,.038,.020,1),
      "Main_Light":(.38,.16,.071,1),
      "Hooves":(.09,.068,.049,1),
      "Hair":(.023,.020,.018,1),
      "Muzzle":(.070,.049,.041,1)},
    "Horse_White":{
      "Main":(.76,.73,.66,1),
      "Main_Light":(.54,.52,.49,1),
      "Hooves":(.32,.26,.21,1),
      "Hair":(.61,.54,.43,1),
      "Muzzle":(.46,.36,.31,1)}
}
palette=color_overrides[horse]
pbr_settings={}
for mat in body.data.materials:
    if not mat:continue
    mat.use_nodes=True
    bsdf=next((n for n in mat.node_tree.nodes if n.type=="BSDF_PRINCIPLED"),None)
    if bsdf is None:raise RuntimeError("Missing Principled for "+mat.name)
    albedo=palette.get(mat.name)
    if albedo is not None:
        bsdf.inputs["Base Color"].default_value=albedo
        mat.diffuse_color=albedo
    category="coat" if mat.name.startswith("Main") else mat.name.lower()
    roughness={
      "coat":.37, "hooves":.53, "hair":.46, "muzzle":.62,
      "eye_white":.30,"eye_black":.15}.get(category,.42)
    bsdf.inputs["Metallic"].default_value=0
    bsdf.inputs["Roughness"].default_value=roughness
    coat=bsdf.inputs.get("Coat Weight")
    if coat is not None:coat.default_value=.18 if category=="coat" else 0
    cr=bsdf.inputs.get("Coat Roughness")
    if cr is not None:cr.default_value=.27
    pbr_settings[mat.name]={
      "color":list(bsdf.inputs["Base Color"].default_value),
      "roughness":roughness, "metallic":0}

# Preserve all NLA strips for export. Save a fully editable finished .blend.
result_blend=out/(horse+"_V2.blend")
bpy.ops.wm.save_as_mainfile(filepath=str(result_blend))
out_glb=out/(horse+"_V2.glb")
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True);rig.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(
    filepath=str(out_glb),export_format="GLB",use_selection=True,
    export_animations=True,export_animation_mode="NLA_TRACKS",export_skins=True,
    export_apply=True)
if out_glb.stat().st_size<100000:
    raise RuntimeError("GLB output missing")

# CI-friendly physically lit image: actual exported-geometry-based source
# rendered by Blender Cycles. Do not include QA floor or cameras in GLB.
# Mute NLA during turntable shots to show consistent rest geometry.
if rig.animation_data:
    for track in rig.animation_data.nla_tracks:track.mute=True
scene.frame_set(1)
bpy.context.view_layer.update()
bounds=[body.matrix_world@Vector(c) for c in body.bound_box]
minimum=Vector([min(v[i] for v in bounds) for i in range(3)])
maximum=Vector([max(v[i] for v in bounds) for i in range(3)])
center=(minimum+maximum)*.5
extent=maximum-minimum
r=max(extent)*2.05
cam_data=bpy.data.cameras.new("HorseV2_StudioCam")
cam=bpy.data.objects.new("HorseV2_StudioCam",cam_data)
scene.collection.objects.link(cam);scene.camera=cam
cam_data.type="ORTHO";cam_data.ortho_scale=max(extent)*1.25
scene.render.engine="CYCLES"
scene.cycles.device="CPU";scene.cycles.samples=20
scene.render.resolution_x=760;scene.render.resolution_y=680
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.36,.43,.5,1)
bg.inputs["Strength"].default_value=.75
def area(name,pos,power,size):
    light=bpy.data.lights.new(name,"AREA")
    o=bpy.data.objects.new(name,light)
    scene.collection.objects.link(o)
    o.location=center+Vector(pos)
    o.rotation_euler=(center-o.location).to_track_quat("-Z","Y").to_euler()
    light.energy=power;light.shape="DISK";light.size=size
area("KeyLight",(r*.55,-r*.65,r*.65),1600,5)
area("FillLight",(-r*.62,-r*.4,r*.33),850,6)
area("RimLight",(r*.16,r*.65,r*.6),1600,4.5)
views={
 "side":(r,0,r*.32),
 "front":(0,-r,r*.32),
 "back":(0,r,r*.32),
 "isometric":(r*.65,-r*.65,r*.42)}
for view,offset in views.items():
    cam.location=center+Vector(offset)
    cam.rotation_euler=(center-cam.location).to_track_quat("-Z","Y").to_euler()
    path=out/("V2_"+view+".png")
    scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    if not path.is_file() or path.stat().st_size<9000:
        raise RuntimeError("Missing V2 actual render "+str(path))
report={
    "horse":horse,"source_blend":str(blend_src.name),
    "blender":bpy.app.version_string,
    "source_vertices":source_vertices,"new_vertices":new_vertices,
    "subdivision_ratio":round(new_vertices/source_vertices,2),
    "bones":source_bones,"actions":source_actions,
    "pbr_materials":pbr_settings,
    "glb_bytes":out_glb.stat().st_size,
    "views":list(views),
    "status":"GEOMETRY_PBR_UPGRADE_EXPORTED_NEEDS_HUMAN_ART_REVIEW",
    "important_limitations":["No scanned hair/fur textures, still stylized","No new anatomically vetted leg mesh","Hoof gait and bone animation require separate QA"]
}
(out/"quality_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
print("HORSE_V2_POLISH_FINISHED",json.dumps({k:v for k,v in report.items() if k!="pbr_materials"},ensure_ascii=False),flush=True)
