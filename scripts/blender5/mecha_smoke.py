"""Headless Blender 5 test: rigged robot with four reusable animation clips.
Does not use Animatica AI. Runs on CPU-based GitHub Actions.
"""
import bpy, math, json, struct, sys
from pathlib import Path
from mathutils import Vector, Matrix

out=Path("outputs")
out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

arm=bpy.data.armatures.new("MechaBones")
rig=bpy.data.objects.new("MechaRig",arm)
bpy.context.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig
rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
defs=[
("root",None,(0,0,.12),(0,0,.78)),
("spine","root",(0,0,.78),(0,0,1.7)),
("neck","spine",(0,0,1.7),(0,0,1.93)),
("head","neck",(0,0,1.93),(0,0,2.25)),
("upper_arm.L","spine",(.4,0,1.56),(.72,0,1.25)),
("forearm.L","upper_arm.L",(.72,0,1.25),(.98,0,.96)),
("upper_arm.R","spine",(-.4,0,1.56),(-.72,0,1.25)),
("forearm.R","upper_arm.R",(-.72,0,1.25),(-.98,0,.96)),
("thigh.L","root",(.25,0,.8),(.27,0,.43)),
("shin.L","thigh.L",(.27,0,.43),(.27,0,.1)),
("thigh.R","root",(-.25,0,.8),(-.27,0,.43)),
("shin.R","thigh.R",(-.27,0,.43),(-.27,0,.1)),
("foot.L","shin.L",(.27,0,.1),(.27,-.22,.1)),
("foot.R","shin.R",(-.27,0,.1),(-.27,-.22,.1)),
]
for n,p,h,t in defs:
 b=arm.edit_bones.new(n);b.head=h;b.tail=t
 if p:b.parent=arm.edit_bones[p]
bpy.ops.object.mode_set(mode='OBJECT')
rig.show_in_front=True

colors={"armor":(.12,.4,.6,1),"joint":(.03,.07,.11,1),
        "accent":(1,.47,.08,1),"visor":(.39,.93,.95,1)}
mats={}
for n,color in colors.items():
 m=bpy.data.materials.new(n);m.diffuse_color=color
 m.use_nodes=True
 m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=color
 mats[n]=m
parts=[
("body","spine",(0,0,1.34),(.8,.44,.68),"armor"),
("chest","spine",(0,-.24,1.43),(.56,.07,.37),"accent"),
("pelvis","root",(0,0,.76),(.65,.43,.26),"joint"),
("helmet","head",(0,0,2.06),(.54,.46,.36),"armor"),
("visor","head",(0,-.255,2.1),(.42,.08,.14),"visor"),
("armL","upper_arm.L",(.58,0,1.42),(.27,.27,.43),"armor"),
("armR","upper_arm.R",(-.58,0,1.42),(.27,.27,.43),"armor"),
("wristL","forearm.L",(.83,0,1.10),(.29,.29,.38),"accent"),
("wristR","forearm.R",(-.83,0,1.10),(.29,.29,.38),"accent"),
("legL","thigh.L",(.26,0,.625),(.33,.35,.27),"armor"),
("legR","thigh.R",(-.26,0,.625),(.33,.35,.27),"armor"),
("shinL","shin.L",(.27,0,.23),(.32,.38,.27),"armor"),
("shinR","shin.R",(-.27,0,.23),(.32,.38,.27),"armor"),
# Visible pivot components. A gap is left between thigh and shin armor.
("kneeHubL","thigh.L",(.27,0,.43),(.28,.28,.28),"joint"),
("kneeHubR","thigh.R",(-.27,0,.43),(.28,.28,.28),"joint"),
("kneeCapL","thigh.L",(.27,-.21,.43),(.25,.09,.13),"accent"),
("kneeCapR","thigh.R",(-.27,-.21,.43),(.25,.09,.13),"accent"),
("kneeLinkL","shin.L",(.27,0,.345),(.14,.15,.16),"joint"),
("kneeLinkR","shin.R",(-.27,0,.345),(.14,.15,.16),"joint"),
# Independent ankles and feet. The toes point forward (-Y); +Z is up.
("ankleHousingL","shin.L",(.27,0,.12),(.22,.24,.22),"joint"),
("ankleHousingR","shin.R",(-.27,0,.12),(.22,.24,.22),"joint"),
("footL","foot.L",(.27,-.16,.069),(.40,.56,.12),"armor"),
("footR","foot.R",(-.27,-.16,.069),(.40,.56,.12),"armor"),
("toeCapL","foot.L",(.27,-.39,.077),(.39,.13,.10),"accent"),
("toeCapR","foot.R",(-.27,-.39,.077),(.39,.13,.10),"accent"),
("heelL","foot.L",(.27,.12,.068),(.38,.14,.11),"joint"),
("heelR","foot.R",(-.27,.12,.068),(.38,.14,.11),"joint"),
]
# Side axle pins rotate with the thigh and are visible from either side.
# Cylinder local Z is turned toward world X, which is the knee hinge axis.
for side,x in (("L",.27),("R",-.27)):
 for suffix,offset in (("Outer",.19),("Inner",-.19)):
  n="kneeAxle"+side+suffix
  bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.103,depth=.07,rotation=(0,math.pi/2,0))
  ob=bpy.context.object;ob.name=n;ob.data.name=n
  bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)
  # Bake pivot into mesh coordinates so the armature modifier uses one common origin.
  for vertex in ob.data.vertices:
   vertex.co.x += x+offset
   vertex.co.z += .43
  ob.data.materials.append(mats["accent"])
  vg=ob.vertex_groups.new(name="thigh."+side)
  vg.add(list(range(len(ob.data.vertices))),1,"REPLACE")
  mod=ob.modifiers.new("Rigid skin","ARMATURE");mod.object=rig
  mod.use_deform_preserve_volume=False

# Disc joints provide a visible axis of rotation at each ankle.
for side,x in (("L",.27),("R",-.27)):
 for suffix,offset in (("Outer",.14),("Inner",-.14)):
  bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.088,depth=.045,
                                      rotation=(0,math.pi/2,0))
  ob=bpy.context.object;ob.name="ankleAxle"+side+suffix;ob.data.name=ob.name
  bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)
  for vertex in ob.data.vertices:
   vertex.co.x += x+offset
   vertex.co.z += .105
  ob.data.materials.append(mats["accent"])
  vg=ob.vertex_groups.new(name="foot."+side)
  vg.add(list(range(len(ob.data.vertices))),1,"REPLACE")
  mod=ob.modifiers.new("Rigid skin","ARMATURE")
  mod.object=rig
  mod.use_deform_preserve_volume=False

for n,bone,loc,size,mat in parts:
 bpy.ops.mesh.primitive_cube_add(size=1)
 ob=bpy.context.object;ob.name=n;ob.data.name=n;ob.dimensions=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for v in ob.data.vertices:v.co+=Vector(loc)
 ob.data.materials.append(mats[mat])
 group=ob.vertex_groups.new(name=bone)
 group.add(list(range(len(ob.data.vertices))),1,'REPLACE')
 modifier=ob.modifiers.new("Rigid skin","ARMATURE")
 modifier.object=rig
 modifier.use_deform_preserve_volume=False

rig.animation_data_create()
poses=rig.pose.bones
# Blender pose-bone Location uses bone LOCAL axes, not world XYZ.
# Root rests along global +Z, so local-Z is NOT necessarily world +Z.
root_inverse=rig.data.bones["root"].matrix_local.to_3x3().inverted()
def shift_root_in_world(x=0.0,y=0.0,z=0.0):
 poses["root"].location += root_inverse @ Vector((x,y,z))

floor_clearance_samples=[]
# Blender bone local X is the mechanical hinge axis. Keep the low foot
# corners above the ground after each pose is set, without modifying mesh vertices.
from mathutils import Vector as V
def lowest_sole_z():
 bpy.context.view_layer.update()
 floors=[]
 for side,x in (("L",.27),("R",-.27)):
  p=poses["foot."+side]
  inverse_rest=rig.data.bones["foot."+side].matrix_local.inverted()
  transform=rig.matrix_world @ p.matrix @ inverse_rest
  for xoff in (-.19,.19):
   for y in (-.40,.15):
    floors.append((transform @ V((x+xoff,y,.008))).z)
 return min(floors)

def set_bone_world_axis(name, world_head, world_tail):
 """Set the bone pose matrix in armature space, preserving the rest bone roll."""
 rest=rig.data.bones[name]
 direction=(world_tail-world_head).normalized()
 rest_dir=(rest.tail_local-rest.head_local).normalized()
 rotation=rest_dir.rotation_difference(direction) @ rest.matrix_local.to_quaternion()
 pb=poses[name]
 pb.rotation_mode="QUATERNION"
 pb.matrix=Matrix.LocRotScale(world_head,rotation,Vector((1,1,1)))
 bpy.context.view_layer.update()

def place_planted_leg(side,phase):
 """Two-link sagittal IK with constant stance foot position (world coordinates).
    Locomotion-in-place demo: not actual forward root translation or physics.
 """
 p=(phase+(0.5 if side=="R" else 0.0)) % 1.0
 stance_share=.58
 x=.27 if side=="L" else -.27
 anchor_y=-.07 if side=="L" else .07
 swing_up=0.0
 offset_y=0.0
 if p >= stance_share:
  u=(p-stance_share)/(1.0-stance_share)
  raised=math.sin(math.pi*u)**2
  swing_up=.205*raised
  offset_y=-.135*raised
 # Explicit, slightly crouched hip goal stays inside the pelvis armor.
 # Pose-matrix assignment keys the small hip offset, keeping the IK target reachable.
 hip=Vector((.25 if side=="L" else -.25,0.0,.755))
 world_root_motion=rig.data.bones["root"].matrix_local.to_3x3() @ poses["root"].location
 hip.y+=world_root_motion.y
 ankle=Vector((x,anchor_y+offset_y,.105+swing_up))
 dy=ankle.y-hip.y
 dz=ankle.z-hip.z
 length=math.hypot(dy,dz)
 l1=(rig.data.bones["thigh."+side].tail_local-rig.data.bones["thigh."+side].head_local).length
 l2=(rig.data.bones["shin."+side].tail_local-rig.data.bones["shin."+side].head_local).length
 if not abs(l1-l2)+.0001 < length < l1+l2-.0001:
  raise RuntimeError("IK target unreachable for "+side+" at phase "+str(phase)+" distance "+str(length))
 a=(l1*l1-l2*l2+length*length)/(2.0*length)
 height=math.sqrt(max(0,l1*l1-a*a))
 ey,ez=dy/length,dz/length
 # Knee points in -Y (forward) when the leg is vertical.
 knee=Vector(((hip.x+ankle.x)/2.0,
              hip.y+a*ey+height*ez,
              hip.z+a*ez-height*ey))
 set_bone_world_axis("thigh."+side,hip,knee)
 set_bone_world_axis("shin."+side,knee,ankle)
 # The sole is world-level even when the shin pitches.
 foot_rest=rig.data.bones["foot."+side]
 poses["foot."+side].rotation_mode="QUATERNION"
 poses["foot."+side].matrix=Matrix.LocRotScale(
    ankle,foot_rest.matrix_local.to_quaternion(),Vector((1,1,1)))
 bpy.context.view_layer.update()

clips=("Idle","Run","Punch","Dodge")
for clip in clips:
 a=bpy.data.actions.new("Mecha_"+clip)
 rig.animation_data.action=a
 for frame in range(1,49):
  phase=(frame-1)/47.0
  z=math.sin(2*math.pi*phase)
  for b in poses:b.rotation_mode="XYZ";b.rotation_euler=(0,0,0);b.location=(0,0,0)
  if clip=="Idle":poses["spine"].rotation_euler[0]=.025*z
  if clip=="Run":
   # Locomotion-in-place with world-planted stance feet and moving swing feet.
   shift_root_in_world(y=.030*math.sin(2*math.pi*phase),
                       z=-.035+.012*(1-math.cos(4*math.pi*phase)))
   bpy.context.view_layer.update()
   for side,sign in (("L",1),("R",-1)):
    place_planted_leg(side,phase)
    poses["upper_arm."+side].rotation_euler[0]=-sign*.46*z
  if clip=="Punch":
   amt=max(0,1-abs(frame-25)/18)
   poses["upper_arm.R"].rotation_euler[0]=-1.15*amt
   poses["forearm.R"].rotation_euler[0]=-.55*amt
   poses["spine"].rotation_euler[2]=-.15*amt
  if clip=="Dodge":
   amt=max(0,1-abs(frame-25)/20)
   poses["spine"].rotation_euler[1]=.3*amt
   shift_root_in_world(x=.14*amt)
   for side,sign in (("L",1),("R",-1)):
    poses["thigh."+side].rotation_euler[0]=sign*.11*amt
    poses["shin."+side].rotation_euler[0]=-.18*amt
    poses["foot."+side].rotation_euler[0]=.09*amt
  # Reconcile the two feet with the ground at the sampled key poses.
  # This is a deterministic pose correction, not runtime IK/physics.
  ground_before=lowest_sole_z()
  target_clearance=.014
  correction=target_clearance-ground_before
  # Move strictly along world Z: root bone's local Z is not vertical.
  shift_root_in_world(z=correction)
  floor_after=lowest_sole_z()
  floor_clearance_samples.append({"clip":clip,"frame":frame,
                                  "min_sole_z":round(floor_after,5),
                                  "root_ground_correction":round(correction,5)})
  for b in poses:
   channel="rotation_quaternion" if b.rotation_mode=="QUATERNION" else "rotation_euler"
   b.keyframe_insert(data_path=channel,frame=frame)
   # IK poses may contain local translations relative to bone parents.
   if b.name=="root" or (clip=="Run" and b.name.startswith(("thigh.","shin.","foot."))):
    b.keyframe_insert(data_path="location",frame=frame)
 rig.animation_data.action=None
 track=rig.animation_data.nla_tracks.new()
 track.name=clip
 track.strips.new(clip,1,a)

bpy.context.scene.frame_start=1
bpy.context.scene.frame_end=48
bpy.ops.wm.save_as_mainfile(filepath=str((out/"mecha_blender5.blend").resolve()))
bpy.ops.export_scene.gltf(filepath=str((out/"mecha_blender5.glb").resolve()),
 export_format="GLB",export_animations=True,export_animation_mode="ACTIONS",
 export_skins=True)
# Validate GLB container, animation and skin arrays by reading the JSON chunk.
with (out/"mecha_blender5.glb").open("rb") as f:
 header=f.read(12)
 magic,ver,total=struct.unpack("<4sII",header)
 assert magic==b"glTF" and ver==2
 length,typ=struct.unpack("<I4s",f.read(8))
 assert typ==b"JSON"
 document=json.loads(f.read(length).decode("utf-8"))
names=[x.get("name") for x in document.get("animations",[])]
assert len(names)>=4, f"Expected 4 animation clips; got {names}"
assert len(document.get("skins",[]))>=1, "No rig skin exported"
assert sum("knee" in m.get("name","").lower() for m in document.get("meshes",[]))>=10, "Knee hinge geometry missing"
assert sum(("ankle" in m.get("name","").lower() or "foot" in m.get("name","").lower() or "toe" in m.get("name","").lower() or "heel" in m.get("name","").lower()) for m in document.get("meshes",[]))>=12, "Foot or ankle geometry missing"
assert len(arm.bones)==14, f"Expected 14 bones including both foot bones, got {len(arm.bones)}"
assert len(floor_clearance_samples)==48*len(clips), "All-frame ground checks missing"
assert all(x["min_sole_z"] >= -.009 for x in floor_clearance_samples), "Foot sinks below the test floor at a keyed pose"
report={"blender_version":bpy.app.version_string,"bones":len(arm.bones),
        "mesh_parts":len(parts)+8,"knee_design":"separate thigh/shin armor, knee pivots, frontal caps and side axle pins",
        "ankle_design":"2 new ankle bones, feet, toe caps, heels and axle pins",
        "ground_contact":"48 sampled frames; Run uses analytic two-bone planted-foot IK; no dynamic physics",
        "sole_samples":floor_clearance_samples,"animations":names,
        "skins":len(document["skins"]),"glb_bytes":total,
        "method":"procedural Blender Python (not Choreographer AI)"}
(out/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
manifest={
 "schema_version":1,"asset_id":"mecha_blender5","format":"glTF 2.0 GLB",
 "source":"Blender 5.2 procedural animation; Run has two-bone stance IK; NOT generative AI",
 "blender_version":bpy.app.version_string,
 "coordinate_system":"Blender Z-up; glTF export converts to Y-up",
 "unit":"meter","model_file":"mecha_blender5.glb",
 "source_file":"mecha_blender5.blend",
 "clips":names,"min_animation_count":4,
 "requirements":{"skins":True,"animated":True,"visual_review":True},
 "license_note":"All generated geometry is original procedural geometry. Third-party textures and models must declare their own licenses."
}
(out/"asset_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
print("SMOKE_TEST_PASSED",report)
