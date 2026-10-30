"""Real MPFB face-first pilot. One human, one target stack, same skeleton/eyes.
Never transfer face vertices onto an unrelated pre-rigged neutral avatar.
"""
import os,sys,json,math,importlib
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.kdtree import KDTree
ID=os.getenv("FACE_ID","you")
assert ID in ("you","boss")
OUT=Path(os.getenv("FACE_OUT","outputs/face_v3")).resolve()
OUT.mkdir(parents=True,exist_ok=True)
ASSETS=Path(os.environ["MAKEHUMAN_ASSET_ROOT"]).resolve()
assert ASSETS.is_dir()
PROFILES={
 "you":{"gender":.95,"age":.48,"weight":.39,"muscle":.56,"height":.53,"proportions":.52},
 "boss":{"gender":.05,"age":.79,"weight":.77,"muscle":.30,"height":.42,"proportions":.45}}
def need(filename):
    matches=list(ASSETS.rglob(filename))
    if not matches:raise RuntimeError("Missing original licensed MakeHuman asset: "+filename)
    return str(matches[0])
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.ops.preferences.addon_enable(module="bl_ext.local_mpfb.mpfb")
import bl_ext.local_mpfb.mpfb
def service(suffix,name):
    names=[x for x in sys.modules if x.endswith(suffix)]
    assert len(names)==1,(suffix,names)
    return getattr(importlib.import_module(names[0]),name)
HumanService=service("mpfb.services.humanservice","HumanService")
TargetService=service("mpfb.services.targetservice","TargetService")
macro=TargetService.get_default_macro_info_dict()
macro.update(PROFILES[ID])
macro["race"]={"asian":.78,"caucasian":.17,"african":.05}
body=HumanService.create_human(mask_helpers=True,extra_vertex_groups=True,
                               feet_on_ground=True,scale=.1,macro_detail_dict=macro)
assert body.type=="MESH" and len(body.data.vertices)==19158
body.name="TrueMPFBBody_"+ID
# A unique rig fitted AFTER that particular body is created and morphed.
rig=HumanService.add_builtin_rig(body,"game_engine")
assert rig and rig.type=="ARMATURE"
rig.name="RootRig_"+ID
# Attach to the genuine morphed body while all MPFB target keys still exist.
# Asset positions, rigging, and skin must be fitted together as a unit.
skin=need("young_caucasian_female.mhmat")
HumanService.set_character_skin(skin,body,skin_type="GAMEENGINE")
attached=[]
for filename,category in [
 ("high-poly.mhclo","Eyes"),
 ("eyebrow001.mhclo","Eyebrows"),
 ("eyelashes01.mhclo","Eyelashes"),
 ("teeth_base.mhclo","Teeth"),
 ("tongue01.mhclo","Tongue")]:
    asset=HumanService.add_mhclo_asset(need(filename),body,asset_type=category,
                      subdiv_levels=0,material_type="GAMEENGINE")
    if asset is None:raise RuntimeError("MPFB failed to fit "+filename)
    attached.append(asset)
# Morph geometry is visibly real, not merely shape key weights in Blender.
TargetService.bake_targets(body)
for mod in tuple(body.modifiers):
    if mod.type=="MASK":body.modifiers.remove(mod)
bm=bmesh.new();bm.from_mesh(body.data);bm.verts.ensure_lookup_table();bm.verts.index_update()
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index>=13380],context="VERTS")
bm.to_mesh(body.data);bm.free();body.data.update()
assert len(body.data.vertices)==13380
assert all(m.type!="MASK" for m in body.modifiers)
# All fitted eyes/teeth remain independent and are not altered by artificial
# per-object "face width" interpolation. Preserve their original materials.
bpy.context.view_layer.update()
Z=[(body.matrix_world@v.co).z for v in body.data.vertices]
top=max(Z);height=max(Z)-min(Z)
headcenter=top-.14
# Limit all source texture images to 512px and pack in the BLEND.
texture_dimensions=[]
for im in bpy.data.images:
    if not im.has_data or im.source!="FILE":continue
    if im.size[0]>512 or im.size[1]>512:
        im.scale(min(512,im.size[0]),min(512,im.size[1]))
    texture_dimensions.append([im.name,*list(im.size)])
scene=bpy.context.scene
scene.render.engine="CYCLES";scene.cycles.samples=18
scene.cycles.device="CPU"
scene.render.resolution_x=480;scene.render.resolution_y=590
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.15,.18,.21,1)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.85
camera_data=bpy.data.cameras.new("QA_FaceCamera")
camera=bpy.data.objects.new("QA_FaceCamera",camera_data)
scene.collection.objects.link(camera);scene.camera=camera
camera_data.type="ORTHO"
for name,xyz,power in (("Key",(3,-4,4),650),("Fill",(-3,-3,3),380),("Rim",(-2,3,4),430)):
    light=bpy.data.lights.new(name,"AREA");obj=bpy.data.objects.new(name,light)
    scene.collection.objects.link(obj);obj.location=xyz
    obj.rotation_euler=(Vector((0,0,1.15))-obj.location).to_track_quat("-Z","Y").to_euler()
    light.energy=power;light.size=3.3
views={
 "face":((0,-3,headcenter),(0,0,headcenter),.50),
 "side":((3,0,headcenter),(0,0,headcenter),.57),
 "front":((0,-4.5,height*.52),(0,0,height*.52),height*1.28)}
for view,(pos,target,scale) in views.items():
    camera.location=pos
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    camera_data.ortho_scale=scale
    scene.render.filepath=str(OUT/(ID+"_v3_"+view+".png"))
    bpy.ops.render.render(write_still=True)
# This pilot isn't claiming the export-ready expressions are complete;
# actual faces must pass visual review BEFORE the full GLB pipeline is enabled.
report={"character":ID,"status":"FACE_ONLY_PILOT_REQUIRES_VISUAL_APPROVAL",
        "source":"MPFB2 official phenotype and attached CC0 system face assets",
        "phenotype":macro,"body_vertices":len(body.data.vertices),
        "head_top_m":top,"height_m":height,"bones":len(rig.data.bones),
        "attached_original_face_assets":[x.name for x in attached],
        "textures":texture_dimensions,
        "views":[ID+"_v3_"+x+".png" for x in views],
        "note":"Face-only QA; no proof yet of acceptable art, expressions, garments or final license metadata."}
(OUT/(ID+"_v3_report.json")).write_text(json.dumps(report,indent=2,ensure_ascii=False))
print("FACE_V3_PILOT",json.dumps(report))
