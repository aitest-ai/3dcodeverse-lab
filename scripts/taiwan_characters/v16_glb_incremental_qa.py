"""Fast V16 boss sweater fit QA starting from verified V15 GLB, no original asset CDN.

A diagnostic alternative to the full licensed MPFB build, NOT replacement.
"""
import os,sys,json,struct
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from sweater_visibility_v16 import torso_visibility

root=Path(os.getenv("V16_FAST_OUT","outputs/fast_v16")).resolve()
root.mkdir(parents=True,exist_ok=True)
source=Path(os.environ.get("V15_BOSS_GLB","input/outputs/face_v15/boss_v15_ponytail01.glb")).resolve()
if not source.is_file():raise RuntimeError("Need actual V15 boss GLB "+str(source))
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(source))
meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
body=next((o for o in meshes if o.name.startswith("TrueMPFBBody_boss") and
           "toigo" not in o.name),None)
shirt=next((o for o in meshes if "OpenSourceCloth_boss_toigo_fisherman_sweater" in o.name),None)
rigs=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"]
if not body or not shirt or not rigs:
    raise RuntimeError("GLB reimport must retain body, actual CC0 sweater and armature: "+
                       repr([o.name for o in bpy.context.scene.objects]))
def actual_top(obj):
    return max((obj.matrix_world@v.co).z for v in obj.data.vertices)
top=actual_top(body)
headcenter=top-.14
scene=bpy.context.scene
scene.render.engine="CYCLES";scene.cycles.samples=24;scene.cycles.device="CPU"
scene.render.resolution_x=520;scene.render.resolution_y=640
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.15,.18,.21,1)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.56
camera_data=bpy.data.cameras.new("FastV16Camera")
camera=bpy.data.objects.new("FastV16Camera",camera_data)
scene.collection.objects.link(camera);scene.camera=camera;camera_data.type="ORTHO"
for name,xyz,power in (("Key",(3,-4,4),440),("Fill",(-3,-3,3),260),("Rim",(-2,3,4),260)):
    light=bpy.data.lights.new(name,"AREA");obj=bpy.data.objects.new(name,light)
    scene.collection.objects.link(obj);obj.location=xyz
    obj.rotation_euler=(Vector((0,0,1.15))-obj.location).to_track_quat("-Z","Y").to_euler()
    light.energy=power;light.size=3.3
def render(key):
    center=top-.52
    camera.location=(0,-2.4,center)
    camera.rotation_euler=(Vector((0,0,center))-camera.location).to_track_quat("-Z","Y").to_euler()
    camera_data.ortho_scale=.50
    scene.render.filepath=str(root/("boss_v16_fast_"+key+".png"))
    bpy.ops.render.render(write_still=True)
    return Path(scene.render.filepath).name
before_image=render("before")
before_visibility=torso_visibility(body,shirt,top,grid=41)
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
body_bvh=BVHTree.FromObject(body,deps)
b2w=body.matrix_world.copy()
w2b=b2w.inverted()
normal_transform=b2w.to_3x3().inverted().transposed()
w2c=shirt.matrix_world.inverted()
corrected=0;maximum_offset=0.0
for vertex in shirt.data.vertices:
    world=shirt.matrix_world@vertex.co
    nearest,norm,index,d=body_bvh.find_nearest(w2b@world)
    if nearest is None:continue
    surface=b2w@nearest
    n=normal_transform@norm
    if n.length<1e-8:continue
    n.normalize()
    signed=(world-surface).dot(n)
    delta=(world-surface).length
    if delta>.055 or signed<-.05:continue
    if signed<.013:
        distance=.013-signed
        old=vertex.co.copy()
        new=w2c@(world+n*distance)
        diff=new-old
        if shirt.data.shape_keys:
            for key in shirt.data.shape_keys.key_blocks:
                key.data[vertex.index].co+=diff
        vertex.co=new
        corrected+=1
        maximum_offset=max(maximum_offset,distance)
shirt.data.update()
bpy.context.view_layer.update()
after_image=render("after")
after_visibility=torso_visibility(body,shirt,top,grid=41)
# Only export actual imported human meshes + their rig, never camera/lights.
bpy.ops.object.select_all(action="DESELECT")
for ob in bpy.context.scene.objects:
    if ob.type in ("MESH","ARMATURE"):ob.select_set(True)
bpy.context.view_layer.objects.active=rigs[0]
target=root/"boss_v16_fast_from_v15.glb"
bpy.ops.export_scene.gltf(filepath=str(target),export_format="GLB",use_selection=True,
        export_skins=True,export_animations=False,export_morph=True,
        export_morph_normal=False,export_cameras=False,export_lights=False)
with target.open("rb") as f:
    magic,ver,length=struct.unpack("<4sII",f.read(12))
    chunk_length,kind=struct.unpack("<I4s",f.read(8))
    doc=json.loads(f.read(chunk_length))
if not(magic==b"glTF" and ver==2 and length==target.stat().st_size and doc.get("skins")):
    raise RuntimeError("Diagnostic GLB malformed or skeleton lost")
report={
 "status":"INCREMENTAL_GLTF_REIMPORT_DIAGNOSTIC_NOT_RELEASE",
 "source_v15_glb":source.name,
 "src_sha256":__import__("hashlib").sha256(source.read_bytes()).hexdigest(),
 "original_cc0_garment":"toigo_fisherman_sweater",
 "body_mesh_vertices_gltf_import":len(body.data.vertices),
 "sweater_mesh_vertices":len(shirt.data.vertices),
 "sweater_shape_keys":[x.name for x in shirt.data.shape_keys.key_blocks] if shirt.data.shape_keys else [],
 "corrected_source_vertices":corrected,"maximum_projection_m":maximum_offset,
 "chest_before":before_visibility,"chest_after":after_visibility,
 "before_render":before_image,"after_render":after_image,
 "glb":target.name,"glb_bytes":target.stat().st_size,
 "notes":"Reimported V15 CC0 GLB; preserves inherited texture and rig. Does not restore V15-deleted trouser faces; full MPFB rebuild remains required.",
 "art_approval":False,
}
(root/"boss_v16_fast_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print("V16_FAST_DIAGNOSTIC",json.dumps(report))
