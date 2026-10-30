"""Check a real Gallop pose change in a Blender 5 original horse .blend.

This is a second-stage test: the existing GLB animation list is insufficient
to prove the bones actually move. Generate two actual pose renders and metrics.
No changes to source .blend or exported .glb.
"""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
if len(args)!=1:raise RuntimeError("Pass output folder")
folder=Path(args[0]).resolve()
name=folder.name
bpy.ops.wm.open_mainfile(filepath=str(folder/(name+"_blender5.blend")))
rigs=[o for o in bpy.data.objects if o.type=="ARMATURE"]
if not rigs:raise RuntimeError("Source Blend missing armature")
rig=rigs[0]
data=rig.animation_data
if data is None:raise RuntimeError("Source Blend missing animation data")
for track in data.nla_tracks:track.mute=True
a=bpy.data.actions.get("Gallop")
if a is None:raise RuntimeError("Original horse missing Gallop action")
data.action=a
if a.slots:
    compatible=[s for s in a.slots if s.target_id_type=="OBJECT"]
    if compatible:data.action_slot=compatible[0]
sc=bpy.context.scene
start,end=map(float,a.frame_range)
print("GALLOP_ACTION_FRAME_RANGE",start,end,"slots",len(a.slots))
span=end-start
if span<5:raise RuntimeError("Gallop action suspiciously short")
frames=[max(int(math.floor(start)),1), min(int(math.floor(start+span*.33)),int(end))]
if frames[0]==frames[1]:raise RuntimeError("Gallop QA frames identical")
def evaluate(frame):
    sc.frame_set(frame)
    bpy.context.view_layer.update()
    return {p.name:tuple(float(v) for row in p.matrix for v in row) for p in rig.pose.bones}
p1=evaluate(frames[0])
p2=evaluate(frames[1])
changes={name:round(sum(abs(x-y) for x,y in zip(p1[name],p2[name])),5) for name in p1}
changed=[(name,value) for name,value in changes.items() if value>.001]
if len(changed)<5:raise RuntimeError("Gallop is present but actual bones barely move! "+str(changed[:10]))
print("GALLOP_POSE_DIFFERENCE",len(changed),sorted(changed,key=lambda x:-x[1])[:8])

# Preview setup; do not save changes back to source file.
objects=[o for o in bpy.data.objects if o.type=="MESH"]
bounds=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
minimum=Vector([min(p[i] for p in bounds) for i in range(3)])
maximum=Vector([max(p[i] for p in bounds) for i in range(3)])
center=(minimum+maximum)/2
maxsize=max(maximum[i]-minimum[i] for i in range(3))
camdata=bpy.data.cameras.new("GallopQA_Camera")
cam=bpy.data.objects.new("GallopQA_Camera",camdata)
sc.collection.objects.link(cam);sc.camera=cam
camdata.type="ORTHO";camdata.ortho_scale=maxsize*1.5
cam.location=center+Vector((maxsize*1.6,-maxsize*1.6,maxsize*.65))
cam.rotation_euler=(center-cam.location).to_track_quat("-Z","Y").to_euler()
sc.render.engine="BLENDER_WORKBENCH"
sc.display.shading.light="STUDIO";sc.display.shading.color_type="MATERIAL"
sc.render.resolution_x=700;sc.render.resolution_y=600
sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
for i,frame in enumerate(frames,1):
    sc.frame_set(frame)
    bpy.context.view_layer.update()
    path=folder/("preview_gallop_"+str(i)+".png")
    sc.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    if path.stat().st_size<3000:raise RuntimeError("No real gallop frame render")

report={
 "frames":frames,"gallop_action":a.name,"gallop_frame_range":[start,end],
 "moving_bones":len(changed),"total_bones":len(p1),
 "top_motion_bones":sorted(changed,key=lambda x:-x[1])[:15],
 "pass":True,
 "limitations":"Two discrete poses only; realistic racing stride, leg timing, foot contacts and hoof sliding still need motion review"}
(folder/"gallop_qa.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
print("GALLOP_MOTION_PROOF",json.dumps(report,ensure_ascii=False))
