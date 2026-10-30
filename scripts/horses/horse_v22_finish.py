"""Horse V2.2: stylized-to-natural surface detail with rig-weighted hair wisps.

Loads PASSED V2 BLEND (not the rejected triangle-plate version), preserves the
50 original joints and 13 Actions. Adds short layered mane/tail ribbon strands
with copied vertex-group influences, and softens over-glossy coat materials.
No fake photorealism: no hair physics, scanned texture or new anatomy is claimed.
"""
import bpy,sys,json,math,random
from pathlib import Path
from mathutils import Vector

args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
if len(args)!=2:
    raise RuntimeError("Usage -- V2_SOURCE_FOLDER V22_OUTPUT_FOLDER")
src=Path(args[0]).resolve()
out=Path(args[1]).resolve()
out.mkdir(parents=True,exist_ok=True)
name=src.name
bpy.ops.wm.open_mainfile(filepath=str(src/(name+"_V2.blend")))
scene=bpy.context.scene
rig=next((o for o in bpy.data.objects if o.type=="ARMATURE" and len(o.data.bones)==50),None)
if rig is None:raise RuntimeError("Expected original 50-bone horse rig")
body=next((o for o in bpy.data.objects if o.type=="MESH" and any(mod.type=="ARMATURE" and mod.object==rig for mod in o.modifiers)),None)
if body is None:raise RuntimeError("Missing deformed horse mesh")
original_actions=sorted(a.name for a in bpy.data.actions)
if len(original_actions)!=13:raise RuntimeError("Original 13 Actions not present")
original_vertices=len(body.data.vertices)
skin_name_set={b.name for b in rig.data.bones}

# PBR refinement: the previous glossy stripe from .37 roughness looked like
# polished plastic. Use glTF-compatible values for coat, hoof and hair.
pbr={}
for material in body.data.materials:
    if material is None:continue
    material.use_nodes=True
    bsdf=next((n for n in material.node_tree.nodes if n.type=="BSDF_PRINCIPLED"),None)
    if not bsdf:raise RuntimeError("No Principled BSDF: "+material.name)
    category=material.name
    if category.startswith("Main"):
        rough=.67
        coat=.055
    elif category=="Hooves":
        rough=.72;coat=0
    elif category=="Hair":
        rough=.78;coat=0
    elif category.startswith("Eye_"):
        rough=.23;coat=.12
    else:
        rough=.73;coat=0
    bsdf.inputs["Roughness"].default_value=rough
    bsdf.inputs["Metallic"].default_value=0
    coat_node=bsdf.inputs.get("Coat Weight")
    if coat_node is not None:coat_node.default_value=coat
    pbr[category]={"roughness":rough,"coat_weight":coat}

hair_mats=[i for i,m in enumerate(body.data.materials) if m and m.name=="Hair"]
if len(hair_mats)!=1:raise RuntimeError("Hair material not found")
hair_mat=hair_mats[0]
faces=[p for p in body.data.polygons if p.material_index==hair_mat]
if len(faces)<80:raise RuntimeError("Not enough source hair polygons")
print("HORSE_V22_HAIR_FACES",len(faces),flush=True)

rng=random.Random(20261030)
stride=max(3,len(faces)//140)
selected=faces[::stride]
if len(selected)>180:selected=rng.sample(selected,180)
verts=[]
polygons=[]
assignments=[]
colors=[]
for idx,p in enumerate(selected):
    # Flattened hair faces are used only to anchor geometry in the SAME rest
    # coordinate frame; each strand receives the original vertex skin weights.
    source_idx=p.vertices[0]
    source_v=body.data.vertices[source_idx]
    anchor=sum((body.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
    normal=p.normal.normalized()
    direction=Vector((.10*(rng.random()-.5),-.18,-.98)).normalized()
    width=rng.uniform(.005,.011)
    length=rng.uniform(.055,.14)
    outward=.008+(.007*rng.random())
    tangent=normal.cross(direction)
    if tangent.length<.001:tangent=Vector((1,0,0))
    tangent.normalize()
    base=anchor+normal*outward
    middle=anchor+normal*(outward+.011)+direction*length*.65
    tip=anchor+normal*(outward+.020)+direction*length
    nodes=[base+tangent*width,base-tangent*width,
           middle+tangent*width*.55,middle-tangent*width*.55,tip]
    offset=len(verts)
    verts.extend(nodes)
    polygons.extend([(offset+0,offset+1,offset+2),
                     (offset+1,offset+3,offset+2),
                     (offset+2,offset+3,offset+4)])
    weights={}
    for entry in source_v.groups:
        gname=body.vertex_groups[entry.group].name
        if gname in skin_name_set:weights[gname]=entry.weight
    if not weights:raise RuntimeError("Hair root missing bone weights at original vertex "+str(source_idx))
    for j in range(5):
        assignments.append((offset+j,weights))
    colors.append(idx%3)
mesh_data=bpy.data.meshes.new("RiggedLayeredManeTail_V22")
mesh_data.from_pydata(verts,[],polygons)
mesh_data.update()
strands=bpy.data.objects.new("ManeTail_IndividualWisps",mesh_data)
scene.collection.objects.link(strands)
strand_materials=[]
source_mat=body.data.materials[hair_mat]
for i,mult in enumerate((.82,1.0,1.17)):
    mat=source_mat.copy()
    mat.name="HairFibreTones_"+str(i)
    mat.use_nodes=True
    bsdf=next(n for n in mat.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
    base=bsdf.inputs["Base Color"].default_value
    color=tuple(min(.85,max(.006,base[k]*mult)) for k in range(3))+(1,)
    bsdf.inputs["Base Color"].default_value=color
    mat.diffuse_color=color
    bsdf.inputs["Roughness"].default_value=.82
    strand_materials.append(mat)
    mesh_data.materials.append(mat)
for group_idx,cidx in enumerate(colors):
    for k in range(3):
        mesh_data.polygons[group_idx*3+k].material_index=cidx
for vertex_idx,weights in assignments:
    for group,weight in weights.items():
        vg=strands.vertex_groups.get(group)
        if vg is None:vg=strands.vertex_groups.new(name=group)
        vg.add([vertex_idx],weight,"REPLACE")
modifier=strands.modifiers.new("HorseOriginalArmature","ARMATURE")
modifier.object=rig
new_verts=len(mesh_data.vertices)
print("HORSE_V22_RIGGED_FIBERS",len(selected),new_verts,len(strands.vertex_groups),flush=True)

# Save editable source BEFORE lighting and camera assets.
blend=out/(name+"_V22.blend")
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.object.select_all(action="DESELECT")
for obj in (body,strands,rig):obj.select_set(True)
bpy.context.view_layer.objects.active=rig
glb=out/(name+"_V22.glb")
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
    use_selection=True,export_animations=True,
    export_animation_mode="NLA_TRACKS",export_skins=True)
if glb.stat().st_size<100000:
    raise RuntimeError("V22 GLB export failed")

# Stable pose for side-by-side visual QA, without touching exported Actions.
if rig.animation_data:
    for track in rig.animation_data.nla_tracks:track.mute=True
scene.frame_set(1)
bpy.context.view_layer.update()
bounds=[body.matrix_world@Vector(c) for c in body.bound_box]
small=Vector([min(p[k] for p in bounds) for k in range(3)])
large=Vector([max(p[k] for p in bounds) for k in range(3)])
center=(small+large)*.5
span=large-small
r=max(span)*2.0
camdata=bpy.data.cameras.new("HorseV22_ProofCam")
cam=bpy.data.objects.new("HorseV22_ProofCam",camdata)
scene.collection.objects.link(cam);scene.camera=cam;camdata.type="ORTHO"
scene.render.engine="CYCLES"
scene.cycles.device="CPU";scene.cycles.samples=16
scene.render.resolution_x=760;scene.render.resolution_y=680
scene.render.resolution_percentage=100;scene.render.image_settings.file_format="PNG"
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value=(.36,.43,.49,1)
bg.inputs["Strength"].default_value=.75
for lname,loc,power in [
    ("Key",(r*.55,-r*.65,r*.65),1200),
    ("Fill",(-r*.62,-r*.4,r*.33),850),
    ("Rim",(r*.16,r*.65,r*.6),1100)]:
    data=bpy.data.lights.new(lname,"AREA")
    obj=bpy.data.objects.new(lname,data)
    scene.collection.objects.link(obj)
    obj.location=center+Vector(loc)
    obj.rotation_euler=(center-obj.location).to_track_quat("-Z","Y").to_euler()
    data.energy=power;data.shape="DISK";data.size=5
views={
 "side":((r,0,r*.32),max(span)*1.25,center),
 "front":((0,-r,r*.32),max(span)*1.25,center),
 "back":((0,r,r*.32),max(span)*1.25,center),
 "isometric":((r*.65,-r*.65,r*.42),max(span)*1.25,center),
}
for name_view,(pos,ortho,target) in views.items():
    cam.location=center+Vector(pos)
    cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
    camdata.ortho_scale=ortho
    path=out/("V22_"+name_view+".png");scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    if path.stat().st_size<10000:raise RuntimeError("Missing Blender proof image "+name_view)
report={
    "asset":name,"original_source":"Quaternius Ultimate Animated Animals CC0",
    "source":"previously validated V2 BLEND",
    "old_body_vertices":original_vertices,
    "new_body_vertices":len(body.data.vertices),
    "new_rigged_hair_vertices":new_verts,
    "strand_count":len(selected),
    "rigged_weight_groups":len(strands.vertex_groups),
    "bones":len(rig.data.bones),
    "animation_actions":original_actions,
    "pbr":pbr,"views":list(views),
    "glb_bytes":glb.stat().st_size,
    "status":"RENDERED_QUALITY_REQUIRES_VISUAL_REVIEW",
    "limitations":"Strands are procedural faceted ribbons, not photorealistic fur/hair; existing mesh anatomy unchanged"
}
(out/"quality_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("HORSE_V22_COMPLETE",json.dumps({k:v for k,v in report.items() if k!="pbr"},ensure_ascii=False),flush=True)
