"""V18: True GLB armature motion/stress QA, not a cosmetic static preview.

Reimport V17's real four-role MPFB GLB, keyframe the existing 53-bone rig,
render genuine Blender posed meshes, and compare actual skinned body/shirt/pants
frontmost depths. Never auto-fix motion collision by hiding mesh.
"""
import os,sys,json,math,struct,hashlib
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ID=os.environ.get("V18_ID","boss")
assert ID in {"boss","jie"}
ROOT=Path(os.environ.get("V18_INPUT","input/outputs/face_v17")).resolve()
OUT=Path(os.environ.get("V18_OUTPUT","outputs/motion_v18")).resolve()
OUT.mkdir(parents=True,exist_ok=True)
stem={"boss":"boss_v17_ponytail01","jie":"jie_v17_main"}[ID]
source=ROOT/(stem+".glb")
if not source.is_file():
    raise RuntimeError("V18 real V17 MPFB GLB missing "+str(source))
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(source))
meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
rigs=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"]
if len(rigs)!=1:raise RuntimeError("Expected exactly one real game-engine rig")
rig=rigs[0]
body=next(o for o in meshes if o.name.startswith("TrueMPFBBody_"+ID))
shirt=next(o for o in meshes if "OpenSourceCloth_"+ID+"_" in o.name and ("sweater" in o.name or "t-shirt" in o.name))
pants=next(o for o in meshes if "OpenSourceCloth_"+ID+"_" in o.name and "pants" in o.name)
assert len(rig.data.bones)==53,len(rig.data.bones)
required=("upperarm_l","upperarm_r","spine_02","thigh_l","thigh_r","calf_l","calf_r","hand_l","hand_r")
assert all(n in rig.pose.bones for n in required),sorted(rig.pose.bones.keys())

top=max((body.matrix_world@v.co).z for v in body.data.vertices)
height=top-min((body.matrix_world@v.co).z for v in body.data.vertices)
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.samples=20
scene.cycles.device="CPU"
scene.render.resolution_x=520
scene.render.resolution_y=680
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.15,.18,.21,1)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.56
camdata=bpy.data.cameras.new("V18_Motion_QA_Camera")
camera=bpy.data.objects.new("V18_Motion_QA_Camera",camdata)
scene.collection.objects.link(camera);scene.camera=camera;camdata.type="ORTHO"
for name,xyz,power in (("Key",(3,-4,4),440),("Fill",(-3,-3,3),260),("Rim",(-2,3,4),260)):
    light=bpy.data.lights.new(name,"AREA")
    ob=bpy.data.objects.new(name,light);scene.collection.objects.link(ob);ob.location=xyz
    ob.rotation_euler=(Vector((0,0,1.1))-ob.location).to_track_quat("-Z","Y").to_euler()
    light.energy=power;light.size=3.3

def set_camera(view):
    z=top-.52
    if view=="full":
        camera.location=(0,-4.3,height*.52)
        target=(0,0,height*.52)
        camdata.ortho_scale=height*1.27
    else:
        camera.location=(0,-2.5,z)
        target=(0,0,z)
        camdata.ortho_scale=.60
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()

def raster(name,view):
    set_camera(view)
    name=ID+"_v18_"+name+"_"+view+".png"
    scene.render.filepath=str(OUT/name)
    bpy.ops.render.render(write_still=True)
    return name

def pose_frame(frame,angles):
    # Select animation time BEFORE applying transforms; selecting a frame can
    # otherwise overwrite a freshly applied pose with old FCurve evaluation.
    scene.frame_set(frame)
    for bone in rig.pose.bones:
        bone.rotation_mode="XYZ"
        bone.rotation_euler=(0.0,0.0,0.0)
    for name,rotation in angles.items():
        rig.pose.bones[name].rotation_euler=rotation
    bpy.context.view_layer.update()
    for name in required:
        b=rig.pose.bones[name]
        b.keyframe_insert(data_path="rotation_euler",frame=frame,group=name)
    bpy.context.view_layer.update()

def front_hit(obj,bvh,x,z):
    start=Vector((x,-2.,z))
    inverse=obj.matrix_world.inverted()
    hit,_,_,_=bvh.ray_cast(inverse@start,(inverse.to_3x3()@Vector((0,1,0))).normalized(),5.)
    return obj.matrix_world@hit if hit is not None else None

def sample_visibility():
    deps=bpy.context.evaluated_depsgraph_get()
    sb=BVHTree.FromObject(shirt,deps)
    pb=BVHTree.FromObject(pants,deps)
    bb=BVHTree.FromObject(body,deps)
    counts={"rays":0,"body_present":0,"body_front_rays":0,
            "cloth_layer_wrong":0,"cloth_layer_overlap":0,
            "cloth_missing_front_rays":0}
    samples=[]
    for iz in range(35):
        z=top-.76+(.48*iz/34)
        for ix in range(37):
            x=-.19+.38*ix/36
            s=front_hit(shirt,sb,x,z)
            p=front_hit(pants,pb,x,z)
            b=front_hit(body,bb,x,z)
            counts["rays"]+=1
            if s is not None and p is not None:
                counts["cloth_layer_overlap"]+=1
                if p.y < s.y-.0015:
                    counts["cloth_layer_wrong"]+=1
            if b is None:continue
            counts["body_present"]+=1
            clothes=[v.y for v in (s,p) if v is not None]
            if not clothes:
                counts["cloth_missing_front_rays"]+=1
            if not clothes or b.y<min(clothes)-.0015:
                counts["body_front_rays"]+=1
                if len(samples)<20:samples.append([round(x,4),round(z,4)])
    counts["first_body_front_positions"]=samples
    counts["note"]="Orthographic -Y neutral camera, central 37x35 sample; does not capture sleeves or side seams"
    return counts

def calibrate_arm_raise_axis():
    """Test actual FK result instead of assuming left/right local bone axes.
    Choose a real wrist-height-raising axis for EACH arm separately.
    """
    rig_axes={}
    proof={}
    for side in ("l","r"):
        upper=rig.pose.bones["upperarm_"+side]
        wrist=rig.pose.bones["hand_"+side]
        for bone in rig.pose.bones:
            bone.rotation_mode="XYZ"
            bone.rotation_euler=(0.0,0.0,0.0)
        bpy.context.view_layer.update()
        original=rig.matrix_world@wrist.head
        options=[]
        for axis in (0,1,2):
            for radians in (-1.15,-.85,.85,1.15):
                trial=[0.,0.,0.]
                trial[axis]=radians
                upper.rotation_euler=trial
                bpy.context.view_layer.update()
                moved=rig.matrix_world@wrist.head
                height=moved.z-original.z
                # Penalize wrist crossing the torso centreline.
                score=height-max(0,.11-abs(moved.x))*.25
                options.append((score,height,tuple(trial),tuple(moved)))
                upper.rotation_euler=(0.,0.,0.)
        pick=max(options,key=lambda x:x[0])
        if pick[1]<.13:
            raise RuntimeError("No real local-arm rotation raises wrist >=13cm: "+str((side,options)))
        rig_axes["upperarm_"+side]=pick[2]
        proof[side]={"neutral_wrist_z":round(original.z,5),
                     "raised_wrist_z":round(pick[3][2],5),
                     "actual_vertical_lift_m":round(pick[1],5),
                     "rotation_euler_xyz":pick[2]}
        bpy.context.view_layer.update()
    for bone in rig.pose.bones:
        bone.rotation_euler=(0.,0.,0.)
    bpy.context.view_layer.update()
    return rig_axes,proof

raise_axes,raise_proof=calibrate_arm_raise_axis()
poses=[
 ("neutral",1,{}),
 ("arms_raise",13,raise_axes),
 ("torso_bend",25,{"spine_02":(.32,0,0)}),
 ("step",37,{"thigh_l":(.48,0,0),"calf_l":(-.30,0,0),
             "thigh_r":(-.25,0,0),"calf_r":(.12,0,0)}),
 ("reset",49,{})
]
report={}
for name,frame,angles in poses:
    pose_frame(frame,angles)
    if name=="reset":continue
    report[name]=sample_visibility()
    report[name]["render"]=raster(name,"full")
    if name in ("neutral","torso_bend"):
        report[name]["waist_render"]=raster(name,"waist")

# Confirm bone keyframing truly produced distinct skinned geometry.
def wrist_position(frame):
    scene.frame_set(frame);bpy.context.view_layer.update()
    bone=rig.pose.bones["hand_l"]
    return tuple(rig.matrix_world@bone.head)
neutral_wrist=Vector(wrist_position(1))
raise_wrist=Vector(wrist_position(13))
if (neutral_wrist-raise_wrist).length<.13:
    raise RuntimeError("Rig calibrated arm raise did not visibly move hand >=13cm")
report["actual_hand_displacement_m"]=round((neutral_wrist-raise_wrist).length,5)
scene.frame_set(1)
bpy.context.view_layer.update()

# Export real skinned rig + keyframes as a playable GLB animation, not just PNG.
bpy.ops.object.select_all(action="DESELECT")
for ob in bpy.context.scene.objects:
    if ob.type in ("MESH","ARMATURE"):ob.select_set(True)
bpy.context.view_layer.objects.active=rig
glb=OUT/(ID+"_v18_poses_not_walk_cycle.glb")
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",use_selection=True,
    export_skins=True,export_animations=True,export_morph=True,
    export_morph_normal=False,export_cameras=False,export_lights=False)
with glb.open("rb") as stream:
    magic,version,total=struct.unpack("<4sII",stream.read(12))
    jl,kind=struct.unpack("<I4s",stream.read(8))
    document=json.loads(stream.read(jl))
assert magic==b"glTF" and version==2 and total==glb.stat().st_size
assert document.get("skins") and document.get("animations"),"Real pose animation absent"
num_channels=sum(len(x.get("channels",[])) for x in document["animations"])
assert num_channels>=4,num_channels
assert len(document["skins"][0]["joints"])==53
data={
    "character":ID,
    "base_source":stem+".glb",
    "base_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
    "status":"PILOT_POSE_STRESS_NOT_ART_APPROVED",
    "pose_names":[x[0] for x in poses],
    "calibrated_arm_raise":raise_proof,
    "angles_in_radians":{n:a for n,frame,a in poses},
    "bones":len(rig.data.bones),
    "shape_key_meshes":{m.name:list(m.data.shape_keys.key_blocks.keys())[1:] for m in meshes if m.data.shape_keys},
    "actual_glb_animations":len(document["animations"]),
    "actual_animation_channels":num_channels,
    "glb":glb.name,"glb_bytes":glb.stat().st_size,
    "per_pose":report,
    "animation_scope":"Neutral, two real wrist-raising FK arms, torso bend, step, reset. Not a walk cycle.",
    "manual_review_required":True,
    "art_approved":False,
}
(OUT/(ID+"_v18_motion_report.json")).write_text(json.dumps(data,ensure_ascii=False,indent=2))
print("V18_REAL_RIG_STRESS",ID,json.dumps(data))
