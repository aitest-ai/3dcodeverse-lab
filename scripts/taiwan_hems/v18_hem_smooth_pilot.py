"""V18 experimental CC0 sweater hem smoothing, from genuine V17 GLB.

Preserves mesh topology, UV indices, bone weights and all morph deltas.
Not for merging without actual Blender before/after art acceptance.
"""
import os,sys,json,math,struct
from collections import Counter,defaultdict
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT=Path(os.environ.get("HEM_OUT","outputs/v18_hem")).resolve()
SOURCE=Path(os.environ.get("HEM_SOURCE","input/outputs/face_v17/boss_v17_ponytail01.glb")).resolve()
assert SOURCE.is_file()
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
shirt=next(o for o in bpy.context.scene.objects if o.type=="MESH" and "OpenSourceCloth_boss_toigo_fisherman_sweater" in o.name)
pants=next(o for o in bpy.context.scene.objects if o.type=="MESH" and "OpenSourceCloth_boss_toigo_wool_pants" in o.name)
body=next(o for o in bpy.context.scene.objects if o.type=="MESH" and o.name.startswith("TrueMPFBBody_boss"))
rig=next(o for o in bpy.context.scene.objects if o.type=="ARMATURE")
assert len(rig.data.bones)==53
top=max((body.matrix_world@v.co).z for v in body.data.vertices)

# Source mesh's authentic open edges (not UV splits on re-export).
counts=Counter()
for p in shirt.data.polygons:
    arr=list(p.vertices)
    for i,a in enumerate(arr):
        b=arr[(i+1)%len(arr)]
        counts[tuple(sorted((a,b)))]+=1
adj=defaultdict(set)
for (a,b),n in counts.items():
    if n==1:adj[a].add(b);adj[b].add(a)
components=[];seen=set()
for root in adj:
    if root in seen:continue
    group=set([root]);q=[root];seen.add(root)
    while q:
        u=q.pop()
        for v in adj[u]:
            if v not in seen:seen.add(v);group.add(v);q.append(v)
    if len(group)>=8:components.append(group)
def stats(ids):
    pts=[shirt.matrix_world@shirt.data.vertices[i].co for i in ids]
    return {"n":len(ids),"zmin":round(min(p.z for p in pts),5),
            "zmax":round(max(p.z for p in pts),5),
            "width":round(max(p.x for p in pts)-min(p.x for p in pts),5),
            "zmean":sum(p.z for p in pts)/len(pts)}
candidates=[(stats(c),c) for c in components if stats(c)["width"]>.15]
if not candidates:raise RuntimeError("No authentic wide source hem boundary")
summary,hem=min(candidates,key=lambda pair:pair[0]["zmean"])
if len(hem)<20:raise RuntimeError("Hem component unexpectedly small")
pre_points={i:shirt.data.vertices[i].co.copy() for i in hem}
keys=list(shirt.data.shape_keys.key_blocks) if shirt.data.shape_keys else []
vertex_count=len(shirt.data.vertices);face_count=len(shirt.data.polygons)
def curvature():
    errors=[]
    for v in hem:
        ns=list(adj[v])
        if len(ns)!=2:continue
        p=shirt.data.vertices[v].co
        q=(shirt.data.vertices[ns[0]].co+shirt.data.vertices[ns[1]].co)*.5
        errors.append(abs(p.z-q.z))
    return sum(errors)/len(errors),max(errors),len(errors)
before_curvature=curvature()
# Only a few millimetres of bounded local reflow; preserve original lower-hem height trend.
moved=set();peak_shift=0
for sweep in range(3):
    updates={}
    for idx in hem:
        ns=list(adj[idx])
        if len(ns)!=2:continue
        p=shirt.data.vertices[idx].co
        neighbor=(shirt.data.vertices[ns[0]].co+shirt.data.vertices[ns[1]].co)*.5
        dy=max(-.002,min(.002,(neighbor.y-p.y)*.30))
        dz=max(-.002,min(.002,(neighbor.z-p.z)*.38))
        if abs(dz)+abs(dy)<1e-6:continue
        updates[idx]=Vector((0.,dy,dz))
    for idx,delta in updates.items():
        # Prevent smoothing from drifting far from the licensed hem shape.
        projected=shirt.data.vertices[idx].co+delta
        total=projected-pre_points[idx]
        if total.length>.007:
            delta*=.007/total.length
        shirt.data.vertices[idx].co+=delta
        for block in keys:block.data[idx].co+=delta
        moved.add(idx);peak_shift=max(peak_shift,(shirt.data.vertices[idx].co-pre_points[idx]).length)
shirt.data.update()
after_curvature=curvature()
assert len(shirt.data.vertices)==vertex_count and len(shirt.data.polygons)==face_count
if after_curvature[0]>before_curvature[0]:
    raise RuntimeError("Hem reflow worsened original edge curvature")
# Reproject selected hem boundary outward only if actual pants behind it (avoid painting fake patches).
from mathutils.bvhtree import BVHTree
bvh=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
def first_pant_hit(x,z):
    start=Vector((x,-2,z))
    inv=pants.matrix_world.inverted()
    p,_,_,_=bvh.ray_cast(inv@start,(inv.to_3x3()@Vector((0,1,0))).normalized(),5.)
    return pants.matrix_world@p if p is not None else None
hem_wrong=0
for idx in hem:
    w=shirt.matrix_world@shirt.data.vertices[idx].co
    p=first_pant_hit(w.x,w.z)
    if p is not None and p.y<w.y-.0015:hem_wrong+=1

sc=bpy.context.scene;sc.render.engine="CYCLES";sc.cycles.samples=24;sc.cycles.device="CPU"
sc.render.resolution_x=560;sc.render.resolution_y=640;sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.15,.18,.21,1)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.56
cdata=bpy.data.cameras.new("HemReviewCamera");cam=bpy.data.objects.new("HemReviewCamera",cdata)
sc.collection.objects.link(cam);sc.camera=cam;cdata.type="ORTHO"
for name,xyz,power in (("Key",(3,-4,4),440),("Fill",(-3,-3,3),260),("Rim",(-2,3,4),260)):
    lamp=bpy.data.lights.new(name,"AREA");o=bpy.data.objects.new(name,lamp)
    sc.collection.objects.link(o);o.location=xyz
    o.rotation_euler=(Vector((0,0,1.1))-o.location).to_track_quat("-Z","Y").to_euler()
    lamp.energy=power;lamp.size=3.3
def render(view,version):
    look=top-.69
    if view=="front":cam.location=(0,-2.4,look);cdata.ortho_scale=.40
    else:cam.location=(1.15,-2.4,look);cdata.ortho_scale=.42
    cam.rotation_euler=(Vector((0,0,look))-cam.location).to_track_quat("-Z","Y").to_euler()
    sc.render.filepath=str(OUT/("boss_v18_"+version+"_hem_"+view+".png"))
    bpy.ops.render.render(write_still=True)

# True apples-to-apples compare in one Blender import and exact same camera.
deltas={idx:shirt.data.vertices[idx].co-pre_points[idx] for idx in moved}
for idx,delta in deltas.items():
    shirt.data.vertices[idx].co-=delta
    for block in keys:block.data[idx].co-=delta
shirt.data.update()
for view in ("front","threequarter"):render(view,"before")
for idx,delta in deltas.items():
    shirt.data.vertices[idx].co+=delta
    for block in keys:block.data[idx].co+=delta
shirt.data.update()
for view in ("front","threequarter"):render(view,"after")
bpy.ops.object.select_all(action="DESELECT")
for o in bpy.context.scene.objects:
    if o.type in ("ARMATURE","MESH"):o.select_set(True)
bpy.context.view_layer.objects.active=rig
outglb=OUT/"boss_v18_smoothed_hem_PILOT.glb"
bpy.ops.export_scene.gltf(filepath=str(outglb),export_format="GLB",use_selection=True,
   export_skins=True,export_animations=False,export_morph=True,
   export_morph_normal=False,export_cameras=False,export_lights=False)
with outglb.open("rb") as f:
    magic,version,length=struct.unpack("<4sII",f.read(12))
    jl,typ=struct.unpack("<I4s",f.read(8))
    gltf=json.loads(f.read(jl))
assert magic==b"glTF" and version==2 and length==outglb.stat().st_size
assert gltf.get("skins") and len(gltf["skins"][0]["joints"])==53
report={"status":"HEM_EDGE_SMOOTHING_EXPERIMENT_NOT_ART_APPROVED",
        "source":SOURCE.name,
        "original_hem":summary,
        "open_edge_components":len(components),"hem_vertices":len(hem),
        "moved_hem_vertices":len(moved),"max_vertex_shift_m":round(peak_shift,6),
        "local_z_curvature_before":list(before_curvature),
        "local_z_curvature_after":list(after_curvature),
        "boundary_vertices_with_pants_in_front":hem_wrong,
        "topology_preserved":True,"all_shape_keys_preserved":bool(keys),
        "pilot_glb":outglb.name,"pilot_glb_bytes":outglb.stat().st_size,
        "need_visual_review":True}
(OUT/"v18_hem_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
print("V18_REAL_HEM_EXPERIMENT",json.dumps(report))
