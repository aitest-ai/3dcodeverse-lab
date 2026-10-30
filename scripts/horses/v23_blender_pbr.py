"""Horse V2.3: give the ACTUAL animated Quaternius horse a proper PBR coat.

Start from V2.2 BLEND, preserve original 50-bone armature, 13 actions, rigged
mane/tail wisps. Smart UV project only the main skinned horse mesh, attach our
original 1024-square coat albedo, tangent normal and roughness PNGs. GLB must
contain image data and TEXCOORD_0. Avoid touching rigging/animation.
"""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
if len(argv)!=3:raise RuntimeError("Usage -- V22_BLENDFILE MAPS_DIR OUT_DIR")
src=Path(argv[0]).resolve()
maps=Path(argv[1]).resolve()
out=Path(argv[2]).resolve()
out.mkdir(parents=True,exist_ok=True)
name=out.name
bpy.ops.wm.open_mainfile(filepath=str(src))
scene=bpy.context.scene
rig=next((o for o in scene.objects if o.type=="ARMATURE" and len(o.data.bones)==50),None)
if rig is None:raise RuntimeError("Source 50-bone rig missing")
skinned=[o for o in scene.objects if o.type=="MESH" and any(m.type=="ARMATURE" and m.object==rig for m in o.modifiers)]
if len(skinned)!=2:raise RuntimeError("Expected skinned body plus wisps")
body=max(skinned,key=lambda o:len(o.data.vertices))
wisps=min(skinned,key=lambda o:len(o.data.vertices))
actions=[a.name for a in bpy.data.actions]
if len(actions)!=13 or not any(x.lower()=="gallop" for x in actions):
    raise RuntimeError("Source 13 actions or Gallop missing")
before_bones=len(rig.data.bones)
before_main_vertices=len(body.data.vertices)
before_wisp_vertices=len(wisps.data.vertices)
# Repacking UV must not modify original vertex positions or skin weights.
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True);bpy.context.view_layer.objects.active=body
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(island_margin=.012,rotate_method="AXIS_ALIGNED_Y",scale_to_bounds=False)
bpy.ops.object.mode_set(mode="OBJECT")
uv=body.data.uv_layers.active
if uv is None:raise RuntimeError("Smart UV failed; reject")
print("UV_REAL_LAYER",name,uv.name,"corners",len(uv.data),flush=True)
# Pack original authored PBR maps into the editable .blend and GLB.
albedo=bpy.data.images.load(str(maps/"coat_albedo.png"),check_existing=False)
albedo.name="V23_HorseCoat_Albedo"
albedo.pack()
norm=bpy.data.images.load(str(maps/"coat_normal.png"),check_existing=False)
norm.name="V23_HorseCoat_Normal"
norm.colorspace_settings.name="Non-Color"
norm.pack()
rough=bpy.data.images.load(str(maps/"coat_roughness.png"),check_existing=False)
rough.name="V23_HorseCoat_Roughness"
rough.colorspace_settings.name="Non-Color"
rough.pack()
# Attach maps only to the major hide/coat material; preserve face/hoof/
# eyes/mane materials and avoid muddying natural boundary colors.
coat=body.data.materials.get("Main")
if coat is None:raise RuntimeError("Main material not present")
coat.use_nodes=True
nodes=coat.node_tree.nodes
links=coat.node_tree.links
bsdf=next((n for n in nodes if n.type=="BSDF_PRINCIPLED"),None)
if bsdf is None:raise RuntimeError("No Principled BSDF")
# Pure GLTF export-friendly texture nodes.
def tex(name,img,location):
    n=nodes.new("ShaderNodeTexImage");n.label=name;n.name=name
    n.image=img;n.location=location;n.interpolation="Linear"
    return n
bc=tex("Coat_Actual_BaseColor",albedo,(-520,360))
nm=tex("Coat_Actual_TangentNormal",norm,(-520,65))
rg=tex("Coat_Actual_Roughness",rough,(-520,-210))
nmnode=nodes.new("ShaderNodeNormalMap")
nmnode.name="Coat_GLTFTangentNormal"
nmnode.space="TANGENT";nmnode.inputs["Strength"].default_value=.38
nmnode.location=(-215,65)
links.new(bc.outputs["Color"],bsdf.inputs["Base Color"])
links.new(nm.outputs["Color"],nmnode.inputs["Color"])
links.new(nmnode.outputs["Normal"],bsdf.inputs["Normal"])
links.new(rg.outputs["Color"],bsdf.inputs["Roughness"])
bsdf.inputs["Metallic"].default_value=0
coat.diffuse_color=(.52,.28,.18,1) if name=="Horse" else (.78,.75,.70,1)
# Save fully editable scene BEFORE QA cameras, without any license-unclear assets.
blend=out/(name+"_V23.blend")
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.object.select_all(action="DESELECT")
for obj in (body,wisps,rig):obj.select_set(True)
bpy.context.view_layer.objects.active=rig
glb=out/(name+"_V23.glb")
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
    use_selection=True,export_animations=True,
    export_animation_mode="NLA_TRACKS",export_skins=True,
    export_texcoords=True,export_normals=True)
if glb.stat().st_size<1000000:raise RuntimeError("GLB size too small")
# Real Blender Cycles preview; same camera style as V2.2 for direct visual QA
if rig.animation_data:
    for track in rig.animation_data.nla_tracks:track.mute=True
scene.frame_set(1)
bpy.context.view_layer.update()
points=[body.matrix_world@Vector(c) for c in body.bound_box]
low=Vector(tuple(min(v[k] for v in points) for k in range(3)))
high=Vector(tuple(max(v[k] for v in points) for k in range(3)))
center=(low+high)*.5
r=max(high-low)*2.0
camera_data=bpy.data.cameras.new("HorseV23_CompareCamera")
camera=bpy.data.objects.new("HorseV23_CompareCamera",camera_data)
scene.collection.objects.link(camera);scene.camera=camera;camera_data.type="ORTHO"
camera_data.ortho_scale=max(high-low)*1.25
scene.render.engine="CYCLES";scene.cycles.device="CPU";scene.cycles.samples=16
scene.render.resolution_x=760;scene.render.resolution_y=680
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.36,.43,.49,1)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.75
for label,offset,power in [
 ("Key",(r*.55,-r*.65,r*.65),1200),
 ("Fill",(-r*.62,-r*.4,r*.33),850),
 ("Rim",(r*.16,r*.65,r*.6),1100)]:
    lamp=bpy.data.lights.new(label,"AREA")
    obj=bpy.data.objects.new(label,lamp)
    scene.collection.objects.link(obj);obj.location=center+Vector(offset)
    obj.rotation_euler=(center-obj.location).to_track_quat("-Z","Y").to_euler()
    lamp.energy=power;lamp.shape="DISK";lamp.size=5
views={"side":(r,0,r*.32),"front":(0,-r,r*.32),
       "back":(0,r,r*.32),"isometric":(r*.65,-r*.65,r*.42)}
for view,delta in views.items():
    camera.location=center+Vector(delta)
    camera.rotation_euler=(center-camera.location).to_track_quat("-Z","Y").to_euler()
    path=out/("V23_"+view+".png")
    scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    if path.stat().st_size<10000:raise RuntimeError("No actual Cycles preview: "+view)
report={
 "asset":name,"source":"Quaternius CC0 original, V2.2 skinned PBR extension",
 "source_blend":src.name,"status":"REAL_UV_PBR_4VIEW_RENDERED_NEEDS_ART_REVIEW",
 "body_vertices":before_main_vertices,"hair_fiber_vertices":before_wisp_vertices,
 "bones":before_bones,"clips":sorted(actions),"UV_layer":uv.name,
 "images":[im.name for im in (albedo,norm,rough)],
 "texture_files":["coat_albedo.png","coat_normal.png","coat_roughness.png"],
 "glb_bytes":glb.stat().st_size,
 "limitations":"Synthetic micro-coat maps, not photographed real horse fur; topology and leg anatomy unchanged; actual in-game material and gait QA pending"}
(out/"v23_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("HORSE_V23_RENDERED",json.dumps(report,ensure_ascii=False),flush=True)
