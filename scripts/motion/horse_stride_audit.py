"""Audit a complete horse Gallop clip using real Blender 5 pose bones.

No physics claims: hoof proxy = lower-leg bone tail (not actual hoof mesh surface).
All displacement reported in original Blender scene units, also normalized by
model height. Designed to catch static animations and aid visual review.
"""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
if len(args)!=1:
    raise RuntimeError("Usage -- output/horse_v2/Horse")
folder=Path(args[0]).resolve()
name=folder.name
path=folder/(name+"_V2.blend")
if not path.is_file():
    raise FileNotFoundError(path)
bpy.ops.wm.open_mainfile(filepath=str(path))
scene=bpy.context.scene
rig=next((o for o in scene.objects if o.type=="ARMATURE" and
          len(o.data.bones)>=45),None)
if rig is None:raise RuntimeError("Horse 50-bone rig not found")
data=rig.animation_data
if data is None:raise RuntimeError("Horse has no animation data")
for track in data.nla_tracks:track.mute=True
action=bpy.data.actions.get("Gallop")
if action is None:raise RuntimeError("Gallop action not found")
data.action=action
if action.slots:
    slots=[s for s in action.slots if s.target_id_type=="OBJECT"]
    if slots:data.action_slot=slots[0]
start,end=map(float,action.frame_range)
if end-start<5:raise RuntimeError("Gallop action has insufficient frames")
hooves={
 "front_L":"FrontLowerLeg.L","front_R":"FrontLowerLeg.R",
 "hind_L":"BackLowerLeg.L","hind_R":"BackLowerLeg.R"
}
for b in hooves.values():
    if b not in rig.pose.bones:raise RuntimeError("Missing horse leg bone "+b)
bodies=[o for o in scene.objects if o.type=="MESH" and any(m.type=="ARMATURE" for m in o.modifiers)]
if not bodies:raise RuntimeError("No deformed horse body")
body=max(bodies,key=lambda o:len(o.data.vertices))
corners=[body.matrix_world @ Vector(c) for c in body.bound_box]
height=max(v.z for v in corners)-min(v.z for v in corners)
if height<1:raise RuntimeError("Horse height suspiciously small")

samples=[]
N=40
for i in range(N):
    frame=start+(end-start)*i/(N-1)
    scene.frame_set(int(math.floor(frame)),subframe=frame-math.floor(frame))
    bpy.context.view_layer.update()
    positions={}
    for tag,bone_name in hooves.items():
        p=rig.pose.bones[bone_name]
        point=rig.matrix_world @ p.tail
        positions[tag]=[round(float(v),6) for v in point]
    samples.append({"frame":round(frame,4),"positions":positions})
report={}
for tag in hooves:
    series=[Vector(s["positions"][tag]) for s in samples]
    z=[p.z for p in series]
    minimum=min(z)
    amplitude=max(z)-minimum
    tolerance=max(.015*height,.17*amplitude)
    contact=[p.z<=minimum+tolerance for p in series]
    movements=[]
    for i in range(1,len(series)):
        if contact[i] and contact[i-1]:
            step=series[i]-series[i-1]
            movements.append(math.hypot(step.x,step.y))
    # Absolute X/Y motion includes in-place gait; not a contact collision solver.
    report[tag]={
      "low_z":round(minimum,5),"high_z":round(max(z),5),
      "vertical_range_in_source_units":round(amplitude,5),
      "range_as_horse_height":round(amplitude/height,5),
      "near_ground_samples":sum(contact),
      "max_proxy_near_ground_slide_source_units":round(max(movements) if movements else 0,5),
      "max_proxy_near_ground_slide_as_horse_height":round((max(movements) if movements else 0)/height,5)
    }
if sum(1 for r in report.values() if r["range_as_horse_height"]>.008)<3:
    raise RuntimeError("Gallop animated horse legs are unexpectedly static")
warnings=[]
for tag,row in report.items():
    if row["max_proxy_near_ground_slide_as_horse_height"]>.05:
        warnings.append(tag+": possible hoof sliding; manually inspect actual hoof surface")
result={
 "asset":name,"source_file":path.name,"action":"Gallop",
 "sample_count":N,"action_frame_range":[start,end],
 "relative_height_units":round(height,5),"hoof_proxy_bones":hooves,
 "limbs":report,"warnings":warnings,
 "method":"Blender pose evaluated at 40 subframes, lower-leg bone-tail proxies, Z-up scene",
 "limitations":"No mesh/surface raycasting, no floor collider, no actual race movement, no physical IK, and source scale is NOT calibrated metres",
 "status":"GAIT_MOTION_MEASURED_NOT_PHYSICALLY_VALIDATED",
 "trajectory":samples
}
folder.joinpath("stride_qa.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
print("HORSE_V2_GALLOP_STRIDE_AUDIT",json.dumps({k:v for k,v in result.items() if k!="trajectory"},ensure_ascii=False),flush=True)

# Self-contained original visualization (SVG is generated from real data).
# Four normalized hoof-height trajectories per Gallop cycle, useful to
# identify phase errors. This is not a 3D render or physics proof.
colors={"front_L":"#bf6b3b","front_R":"#ccaf62",
        "hind_L":"#46837a","hind_R":"#5b7198"}
W,H=1010,540
def px(i):return 82+(W-140)*i/(N-1)
def py(tag,i):
    z=samples[i]["positions"][tag][2]
    return 400-285*(z-report[tag]["low_z"])/max(.01,report[tag]["vertical_range_in_source_units"])
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">',
       '<rect width="100%" height="100%" fill="#f5f6f1"/>',
       '<text x="70" y="50" fill="#263f37" font-size="25" font-family="sans-serif">Gallop / hoof proxy height across 40 samples</text>',
       '<text x="70" y="78" fill="#6f7f77" font-size="14" font-family="sans-serif">Normalized per limb; comparisons show phase, not absolute ground contact</text>']
for i in range(5):
    y=115+i*71
    parts.append(f'<path d="M80 {y} H955" stroke="#d4ddd5" stroke-width="1"/>')
for j,tag in enumerate(hooves):
    points=" ".join(f'{px(i):.1f},{py(tag,i):.1f}' for i in range(N))
    parts.append(f'<polyline fill="none" stroke="{colors[tag]}" stroke-width="3" points="{points}"/>')
    parts.append(f'<text x="{95+j*225}" y="470" fill="{colors[tag]}" font-size="20" font-family="sans-serif">{tag}</text>')
parts.append('<text x="70" y="515" fill="#66766f" font-size="14" font-family="sans-serif">Horse V2, Quaternius CC0 - independent Blender pose evaluation</text>')
parts.append("</svg>")
(folder/"gallop_stride_chart.svg").write_text("\n".join(parts),encoding="utf-8")
