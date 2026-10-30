"""Polish the original MPFB BLEND, relinking its verified textures from the GLB.
No shape-altering GLB roundtrips; no 267 MB source archive; real Cycles renders.
"""
import bpy, os, json, struct
from pathlib import Path
from mathutils import Vector
style=os.getenv("HUMAN_STYLE","studio")
assert style in ("studio","street","sport")
base=Path(os.getenv("BASE_SOURCE","inputs/baseline")).resolve()
out=Path(os.getenv("ASSET_OUT","outputs/human_"+style)).resolve()
out.mkdir(parents=True,exist_ok=True)

# Extract PNG images already embedded in our verified previous GLB.
with (base/"human_mpfb_blender5.glb").open("rb") as f:
    magic,ver,total=struct.unpack("<4sII",f.read(12))
    assert magic==b"glTF" and ver==2
    n,k=struct.unpack("<I4s",f.read(8)); assert k==b"JSON"
    gltf=json.loads(f.read(n))
    n,k=struct.unpack("<I4s",f.read(8)); assert k==b"BIN\\x00"
    binary=f.read(n)
imgdir=out/"recovered_images"
imgdir.mkdir(exist_ok=True)
images={}
for idx,img in enumerate(gltf.get("images",[])):
    v=gltf["bufferViews"][img["bufferView"]]
    ext=".png" if img.get("mimeType")=="image/png" else ".jpg"
    name=img.get("name",str(idx))
    p=imgdir/(name+ext)
    p.write_bytes(binary[v.get("byteOffset",0):v.get("byteOffset",0)+v["byteLength"]])
    images[name.casefold()]=p

bpy.ops.wm.open_mainfile(filepath=str(base/"human_mpfb_blender5.blend"))
sc=bpy.context.scene
linked=0
unmatched=[]
for im in bpy.data.images:
    if im.source!="FILE":continue
    keys=[Path(im.name).stem.casefold(),Path(bpy.path.abspath(im.filepath)).stem.casefold()]
    matches=[p for key in keys for n,p in images.items() if key==n or key.startswith(n) or n.startswith(key)]
    if matches:
        im.filepath=str(matches[0]);im.reload();linked+=1
    else:
        unmatched.append([im.name,im.filepath])
print("RELINK",linked,"of",len(images),"unmatched",unmatched)
if linked<7:raise RuntimeError("Could not relink enough embedded PBR images")
bpy.ops.file.pack_all()
rig=next(o for o in bpy.data.objects if o.type=="ARMATURE")
body=next(o for o in bpy.data.objects if o.type=="MESH" and o.name=="Human_Body_MakeHumanTopology")
hair=next(o for o in bpy.data.objects if o.type=="MESH" and o.name.endswith(".long01"))
clothes=next(o for o in bpy.data.objects if o.type=="MESH" and o.name.endswith(".female_casualsuit01"))
print("SOURCE_OBJECTS",body.name,hair.name,clothes.name,len(body.data.vertices),len(rig.data.bones))
# Existing CC0 mesh, exact UVs, source clothing and bone weights are retained.
# Test modest long-hair length adjustments with all original topology intact.
ratio={"studio":.76,"street":1.0,"sport":.58}[style]
if ratio!=1:
    matrix=hair.matrix_world;inverse=matrix.inverted()
    for v in hair.data.vertices:
        p=matrix@v.co
        if p.z<1.57:
            p.z=1.57-(1.57-p.z)*ratio
            v.co=inverse@p
    hair.data.update()
# Adjust only textile surface roughness; DO NOT reassign face materials,
# which could expose unrelated clothing/surface layers in a packed rig.
for mat in clothes.data.materials:
    if mat and mat.use_nodes:
        shader=next((n for n in mat.node_tree.nodes if n.type=="BSDF_PRINCIPLED"),None)
        if shader:shader.inputs["Roughness"].default_value=.76 if style=="studio" else .64
bpy.context.view_layer.update()
height=max((body.matrix_world@v.co).z for v in body.data.vertices)-min((body.matrix_world@v.co).z for v in body.data.vertices)
assert 1.0<height<2.4
blend=out/("human_"+style+".blend")
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.object.select_all(action="DESELECT")
rig.select_set(True)
for o in bpy.data.objects:
    if o.type=="MESH":o.select_set(True)
bpy.context.view_layer.objects.active=rig
glb=out/("human_"+style+".glb")
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",use_selection=True,export_animations=False,export_skins=True)
assert glb.stat().st_size>15000000

manifest={"schema_version":1,"asset_id":"human_"+style,"model_file":glb.name,
 "source_file":blend.name,"style":style,"unit":"meter","clips":[],"min_animation_count":0,
 "requirements":{"skins":True,"animated":False,"visual_review":True},
 "license_note":"Source MakeHuman CC0 system assets; preserves clothing/UV/rig. Requires independent attribution check for any future external additions.",
 "quality_status":"REAL_BLEND_RIGGED_CHARACTER_VISUAL_REVIEW_REQUIRED"}
(out/"asset_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
sc.render.engine="CYCLES"
sc.cycles.device="CPU";sc.cycles.samples=18
sc.render.resolution_x=520;sc.render.resolution_y=640
sc.render.resolution_percentage=100;sc.render.image_settings.file_format="PNG"
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.6
camd=bpy.data.cameras.new("QA_Cam");cam=bpy.data.objects.new("QA_Cam",camd)
sc.collection.objects.link(cam);sc.camera=cam;camd.type="ORTHO"
for name,loc,power in [("Key",(3,-4,4),650),("Fill",(-3,-3,3),400),("Rim",(-2,3.5,4),480)]:
    light=bpy.data.lights.new(name,"AREA");ob=bpy.data.objects.new(name,light)
    sc.collection.objects.link(ob);ob.location=loc
    ob.rotation_euler=(Vector((0,0,1.15))-ob.location).to_track_quat("-Z","Y").to_euler()
    light.energy=power;light.size=3.5
views={
 "front":((0,-5,1.2),(0,0,.95),2.45),
 "side":((5,0,1.2),(0,0,.95),2.45),
 "back":((0,5,1.2),(0,0,.95),2.45),
 "isometric":((4,-4,2.5),(0,0,.95),2.45),
 "face":((0,-3.5,1.52),(0,0,1.51),.70),
 "outfit":((2.5,-4,1.2),(0,0,1.05),1.35)}
for name,(pos,target,scale) in views.items():
    cam.location=pos
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    camd.ortho_scale=scale
    path=out/("preview_"+name+".png");sc.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    assert path.stat().st_size>10000
report={"style":style,"source":"existing original Blender file","relinked_images":linked,
    "source_image_count":len(images),"unmatched_images":unmatched,
    "mesh_count":len([o for o in bpy.data.objects if o.type=="MESH"]),
    "height_m":round(height,4),"bones":len(rig.data.bones),
    "hair_vertices":len(hair.data.vertices),"glb_bytes":glb.stat().st_size,
    "status":"RENDERED_NEEDS_HUMAN_VISUAL_REVIEW"}
(out/"report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("REAL_BLEND_POLISH_OK",json.dumps(report))
