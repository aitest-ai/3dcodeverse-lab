"""Gallop actual hoof-SURFACE contact analysis (not proxy bone tails).

Evaluates subdivided, ARMATURE-DEFORMED Hooves material vertices in Blender 5.
Four hoof clusters determined once in the source mesh local rest topology.
40 subframes sampled across Gallop with independent NLA tracks muted.

This is a stationary treadmill animation: horizontal displacement alone
is NOT physical ground slip in a moving-world racing game. Report contact
interval motion and a plausible root translation correction estimate.
"""
import bpy,sys,math,json,statistics
from pathlib import Path
from mathutils import Vector

args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
if len(args)!=1:raise RuntimeError("Pass path to V2 horse asset folder")
folder=Path(args[0]).resolve()
horse=folder.name
bpy.ops.wm.open_mainfile(filepath=str(folder/(horse+"_V2.blend")))
scene=bpy.context.scene
rig=next(o for o in scene.objects if o.type=="ARMATURE" and len(o.data.bones)==50)
mesh=next(o for o in scene.objects if o.type=="MESH" and any(m.type=="ARMATURE" and m.object==rig for m in o.modifiers))
data=rig.animation_data
if data is None:raise RuntimeError("Missing animation_data")
for track in data.nla_tracks:track.mute=True
action=bpy.data.actions.get("Gallop")
if action is None:raise RuntimeError("Gallop action missing")
data.action=action
if action.slots:
    compatible=[slot for slot in action.slots if slot.target_id_type=="OBJECT"]
    if compatible:data.action_slot=compatible[0]
low,high=map(float,action.frame_range)
if high-low<5:raise RuntimeError("Gallop action too short")

# Rest topology contains individual Hooves material faces, retained by V2.
hoof_faces=[poly for poly in mesh.data.polygons if mesh.data.materials[poly.material_index].name=="Hooves"]
hoof_ids={i for face in hoof_faces for i in face.vertices}
if len(hoof_ids)<200:raise RuntimeError("Missing original horse hoof material geometry")
rest={i:mesh.matrix_world@mesh.data.vertices[i].co for i in hoof_ids}
mid_x=(min(p.x for p in rest.values())+max(p.x for p in rest.values()))/2
mid_y=(min(p.y for p in rest.values())+max(p.y for p in rest.values()))/2
groups={
    "front_L":[],"front_R":[],"hind_L":[],"hind_R":[]
}
# Body length is +/- Y in Blender. We use geometry clustering, not guesses
# about which end is front: inspect head bone compared to hoof Y clusters.
head=rig.data.bones.get("Head")
if head is None:raise RuntimeError("Missing Head bone for longitudinal direction")
head_pos=rig.matrix_world @ head.head_local
front_positive=head_pos.y>mid_y
for idx,p in rest.items():
    fore=(p.y>mid_y)==front_positive
    # Left/Right are defined by source bone positions, not by camera view.
    tag=("front_" if fore else "hind_")+("L" if p.x<mid_x else "R")
    groups[tag].append(idx)
if any(len(x)<20 for x in groups.values()):
    raise RuntimeError("Hoof geometry classification failed: "+str({k:len(v) for k,v in groups.items()}))
bounds=[mesh.matrix_world@Vector(c) for c in mesh.bound_box]
height=max(v.z for v in bounds)-min(v.z for v in bounds)
if height<.5:raise RuntimeError("Unexpected horse height")

SAMPLES=40
samples=[]
for j in range(SAMPLES):
    frame=low+(high-low)*j/(SAMPLES-1)
    whole=int(math.floor(frame))
    scene.frame_set(whole,subframe=frame-whole)
    bpy.context.view_layer.update()
    deps=bpy.context.evaluated_depsgraph_get()
    evaluated=mesh.evaluated_get(deps)
    eval_mesh=evaluated.to_mesh(preserve_all_data_layers=False,depsgraph=deps)
    try:
        # Applied subdivision means indexes stay stable through armature-only
        # deformation. This is essential for tracking original hoof geometry.
        if len(eval_mesh.vertices)!=len(mesh.data.vertices):
            raise RuntimeError("Unexpected mesh vertex count during gait evaluation")
        matrix=evaluated.matrix_world
        hoof_positions={}
        for tag,ids in groups.items():
            pts=[matrix@eval_mesh.vertices[i].co for i in ids]
            pts.sort(key=lambda p:p.z)
            n=max(6,len(pts)//12)
            sole=pts[:n]  # lowest 8.3% approximates contacting hoof sole
            center=sum(sole,Vector())/len(sole)
            hoof_positions[tag]={"xyz":[round(v,6) for v in center],
                     "lowest_z":round(pts[0].z,6)}
        samples.append({"frame":round(frame,4),"hoof":hoof_positions})
    finally:
        evaluated.to_mesh_clear()

metrics={}
possible_slip=[]
for tag,ids in groups.items():
    centers=[Vector(s["hoof"][tag]["xyz"]) for s in samples]
    zmin=min(p.z for p in centers)
    zmax=max(p.z for p in centers)
    # 15% of hoof's observed elevation or 1.0% of horse height.
    threshold=max(height*.01,(zmax-zmin)*.15)
    near=[p.z<=zmin+threshold for p in centers]
    slides=[]
    for k in range(1,len(centers)):
        if near[k] and near[k-1]:
            displacement=centers[k]-centers[k-1]
            slides.append({"from_frame":samples[k-1]["frame"],
                           "to_frame":samples[k]["frame"],
                           "xy_motion":round(math.hypot(displacement.x,displacement.y),6),
                           "forward_y_motion":round(displacement.y,6)})
    max_xy=max([x["xy_motion"] for x in slides],default=0)
    m={"hoof_mesh_vertices":len(ids),"height_range":round(zmax-zmin,6),
       "height_range_by_horse_height":round((zmax-zmin)/height,5),
       "near_ground_sample_count":sum(near),
       "contact_motion_steps":len(slides),
       "max_contact_step_xy":round(max_xy,6),
       "max_contact_step_xy_by_horse_height":round(max_xy/height,6),
       "total_contact_xy_motion":round(sum(x["xy_motion"] for x in slides),6),
       "per_step":slides}
    metrics[tag]=m
    if max_xy/height>.045:
        possible_slip.append(tag)
print("ACTUAL_HOOF_QA",json.dumps({tag:{k:v for k,v in m.items() if k!="per_step"} for tag,m in metrics.items()},ensure_ascii=False),flush=True)
report={"asset":horse,"source":"V2 BLEND, Hooves material subset of evaluated skinned mesh",
        "source_file":(horse+"_V2.blend"),
        "animation":"Gallop","frames":SAMPLES,"action_frame_range":[low,high],
        "horse_height_source_units":height,
        "hoof_mesh_counts":{k:len(x) for k,x in groups.items()},
        "hoof_metrics":metrics,"possible_slip_flags":possible_slip,
        "method":"Lowest ~8.3% of original hoof-material vertices per limb after evaluated armature, sample 40 subframes",
        "limitations":["In-place animation has no track distance; observed horizontal motion is not real-world slip",
          "Sole vertex approximation is not a hoof-ground collision/IK constraint",
          "Model scale not calibrated to actual racehorse metres",
          "Facing and side assignment follow original Head bone and geometry"],
        "status":"MESHBASed_HOOF_CONTACT_MEASURED_REVIEW_REQUIRED",
        "samples":samples}
(folder/"hoof_surface_qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
# Trace chart grounded in true skinned vertex data. Same color palette as former proxy.
W,H=1020,510
colors={"front_L":"#bc683b","front_R":"#d49e42","hind_L":"#468b83","hind_R":"#6179a4"}
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">',
'<rect width="100%" height="100%" fill="#f7f7f2"/>',
'<text x="60" y="40" fill="#263e35" font-family="sans-serif" font-size="24">Gallop | Hoof mesh elevation (evaluated skin)</text>',
'<text x="60" y="68" fill="#65766f" font-family="sans-serif" font-size="14">Actual hoof-material vertex groups; normalized independently per limb; not a floor collision test</text>']
for k in range(5):
    y=110+k*63
    parts.append(f'<path d="M60 {y} H960" stroke="#dde2db" fill="none"/>')
for tag,m in metrics.items():
    yvals=[s["hoof"][tag]["xyz"][2] for s in samples]
    ymin,ymax=min(yvals),max(yvals)
    denom=max(.01,ymax-ymin)
    points=" ".join(f"{60+i*900/(SAMPLES-1):.1f},{403-278*(y-ymin)/denom:.1f}" for i,y in enumerate(yvals))
    parts.append(f'<polyline points="{points}" fill="none" stroke="{colors[tag]}" stroke-width="3"/>')
for j,tag in enumerate(groups):
    parts.append(f'<text x="{62+240*j}" y="452" fill="{colors[tag]}" font-family="sans-serif" font-size="19">{tag}</text>')
parts.append('<text x="60" y="490" fill="#64766c" font-family="sans-serif" font-size="14">Data: Blender 5 evaluated horse mesh, CC0 Quaternius original + V2 topology polish</text></svg>')
(folder/"hoof_surface_trace.svg").write_text("\n".join(parts),encoding="utf-8")
