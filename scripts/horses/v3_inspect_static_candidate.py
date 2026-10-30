"""Blender 5.2 inspect/render quarantined higher-fidelity CC0 horse candidate.

This is an UNRIGGED stand horse; never transfer Quaternius's 13 animations
without separate rigging/retargeting and bone-weight deformation tests.

The candidate bytes mismatch site's published SHA256/size and remain in
review. This script renders their actual mesh and logs metadata, NO approval.
"""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector

args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
if len(args)!=2:raise RuntimeError("Usage -- horse-quarantine.glb output-folder")
source=Path(args[0]).resolve()
out=Path(args[1]).resolve()
out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(source))
meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
rigs=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"]
if not meshes:raise RuntimeError("Candidate contains no polygon meshes")
verts=sum(len(o.data.vertices) for o in meshes)
faces=sum(len(o.data.polygons) for o in meshes)
triangles=sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons)
if verts<1000 or verts>2_000_000 or faces>3_000_000:raise RuntimeError("Implausible source mesh complexity")
materials={m.name for o in meshes for m in o.data.materials if m}
image_count=sum(1 for img in bpy.data.images if img.source=="FILE")
corner_points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
low=Vector(tuple(min(v[i] for v in corner_points) for i in range(3)))
high=Vector(tuple(max(v[i] for v in corner_points) for i in range(3)))
extent=high-low
center=(high+low)*.5
if max(extent)>1000 or min(extent)<.05:raise RuntimeError("Invalid mesh dimensions")
scene=bpy.context.scene

# Preserve the source scene in an editable BLEND, before QA lighting.
blend=out/"V3_static_horse_unrigged.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))

scene.render.engine="CYCLES"
scene.cycles.device="CPU";scene.cycles.samples=16
scene.render.resolution_x=760;scene.render.resolution_y=640
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.world.use_nodes=True
worldbg=scene.world.node_tree.nodes.get("Background")
worldbg.inputs["Color"].default_value=(.30,.35,.41,1)
worldbg.inputs["Strength"].default_value=.75
maxsize=max(extent)
def light(name,offset,power):
    lamp=bpy.data.lights.new(name,"AREA")
    obj=bpy.data.objects.new(name,lamp)
    scene.collection.objects.link(obj)
    obj.location=center+Vector(offset)
    obj.rotation_euler=(center-obj.location).to_track_quat("-Z","Y").to_euler()
    lamp.energy=power;lamp.shape="DISK";lamp.size=maxsize*1.1
light("Key",(maxsize*.75,-maxsize*.8,maxsize*.9),1250)
light("Fill",(-maxsize*.8,-maxsize*.5,maxsize*.5),800)
light("Rim",(maxsize*.3,maxsize*.9,maxsize*.7),1200)
camdat=bpy.data.cameras.new("V3QAOrtho")
camera=bpy.data.objects.new("V3QAOrtho",camdat)
scene.collection.objects.link(camera);scene.camera=camera
camdat.type="ORTHO";camdat.ortho_scale=maxsize*1.35
r=maxsize*2.1
views={
 "side":(r,0,r*.35),
 "front":(0,-r,r*.35),
 "back":(0,r,r*.35),
 "isometric":(r*.7,-r*.7,r*.52)
}
for name,pos in views.items():
    camera.location=center+Vector(pos)
    camera.rotation_euler=(center-camera.location).to_track_quat("-Z","Y").to_euler()
    target=out/("V3_static_"+name+".png")
    scene.render.filepath=str(target)
    bpy.ops.render.render(write_still=True)
    if target.stat().st_size<7000:raise RuntimeError("No renderer proof for "+name)
report={
 "source":str(source.name),
 "status":"STATIC_VISUAL_AUDIT_ONLY_NOT_RIGGED_NOT_LICENSE_SHA_VERIFIED",
 "mesh_count":len(meshes),"vertices":verts,"faces":faces,
 "triangle_count":triangles,"armature_objects":len(rigs),
 "materials":sorted(materials),"image_files_in_scene":image_count,
 "bounding_box_dimensions_scene_units":[round(float(v),4) for v in extent],
 "source_license_claim":"CC0 per Innerscene listing",
 "source_integrity_issue":"Download SHA256 and byte size must be reconciled with site metadata",
 "v3_promotion_blockers":["source hash mismatch","check anatomy in actual renders",
                          "static no gallop bones or clips","needs licensed rig and retarget"],
 "Blender_version":bpy.app.version_string
}
(out/"inspection.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
print("V3_STATIC_MODEL_INSPECTED",json.dumps(report,ensure_ascii=False),flush=True)
