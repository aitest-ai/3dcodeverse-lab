"""V17 Blender real CC0 sweater/trouser surface comparison starting from verified V16 GLB.
Diagnostic only, not final MPFB asset acceptance.
"""
import os,sys,json,struct
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
# Blender standalone --python does not always add the script folder to sys.path.
sys.path.insert(0,str(Path(__file__).resolve().parent))
from garment_layer_v17 import layering_report,correct_sweater_layer

root=Path(os.getenv("V17_FAST_OUT","outputs/fast_v17")).resolve()
root.mkdir(parents=True,exist_ok=True)
source=Path(os.environ.get("V16_BOSS_GLB","input/outputs/face_v16/boss_v16_ponytail01.glb")).resolve()
if not source.is_file():raise RuntimeError("Need actual V16 boss GLB "+str(source))
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
camera_data=bpy.data.cameras.new("FastV17Camera")
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
    scene.render.filepath=str(root/("boss_v17_layer_"+key+".png"))
    bpy.ops.render.render(write_still=True)
    return Path(scene.render.filepath).name
before_image=render("before")
before_layer=layering_report(shirt, next(o for o in meshes if "OpenSourceCloth_boss_toigo_wool_pants" in o.name),top)
pants=next(o for o in meshes if "OpenSourceCloth_boss_toigo_wool_pants" in o.name)
sweater_vertices=len(shirt.data.vertices)
pants_vertices=len(pants.data.vertices)
sweater_faces=len(shirt.data.polygons)
pants_faces=len(pants.data.polygons)
correction=correct_sweater_layer(shirt,pants,top)
after_layer=layering_report(shirt,pants,top)
after_image=render("after")
if after_layer["pants_in_front"]>=before_layer["pants_in_front"]:
    raise RuntimeError("V17 layering correction did not reduce wrong-facing trouser rays: "
      +repr([before_layer,after_layer]))
assert len(shirt.data.vertices)==sweater_vertices and len(shirt.data.polygons)==sweater_faces
assert len(pants.data.vertices)==pants_vertices and len(pants.data.polygons)==pants_faces
# Only export actual imported human meshes + their rig, never camera/lights.
bpy.ops.object.select_all(action="DESELECT")
for ob in bpy.context.scene.objects:
    if ob.type in ("MESH","ARMATURE"):ob.select_set(True)
bpy.context.view_layer.objects.active=rigs[0]
target=root/"boss_v17_layer_from_v16.glb"
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
 "status":"V17_GARMENT_LAYER_DEBUG_NOT_RELEASE",
 "source_v16_glb":source.name,
 "source_sha256":__import__("hashlib").sha256(source.read_bytes()).hexdigest(),
 "blender_imported_body_vertices":len(body.data.vertices),
 "knit_garment":"original CC0 toigo_fisherman_sweater",
 "pants_garment":"original CC0 toigo_wool_pants",
 "sweater_vertices_unchanged":len(shirt.data.vertices)==sweater_vertices,
 "sweater_faces_unchanged":len(shirt.data.polygons)==sweater_faces,
 "pants_vertices_unchanged":len(pants.data.vertices)==pants_vertices,
 "pants_faces_unchanged":len(pants.data.polygons)==pants_faces,
 "layer_before":before_layer,"layer_after":after_layer,"adjustment":correction,
 "before_render":before_image,"after_render":after_image,"glb":target.name,
 "glb_bytes":target.stat().st_size,"art_approval":False,"dynamic_qa":False,
 "note":"Experimental real-surface cloth layering. Source MPFB topology and authorized CC0 clothing preserved. No animation approval."
}
(root/"boss_v17_layer_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print("V17_GARMENT_LAYER_DIAGNOSTIC",json.dumps(report))
