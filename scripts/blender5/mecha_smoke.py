"""Headless Blender 5 test: rigged robot with four reusable animation clips.
Does not use Animatica AI. Runs on CPU-based GitHub Actions.
"""
import bpy, math, json, struct, sys
from pathlib import Path
from mathutils import Vector

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
]
# Side axle pins rotate with the thigh and are visible from either side.
# Cylinder local Z is turned toward world X, which is the knee hinge axis.
for side,x in (("L",.27),("R",-.27)):
 for suffix,offset in (("Outer",.19),("Inner",-.19)):
  n="kneeAxle"+side+suffix
  bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.103,depth=.07,location=(x+offset,0,.43),rotation=(0,math.pi/2,0))
  ob=bpy.context.object;ob.name=n
  ob.data.materials.append(mats["accent"])
  vg=ob.vertex_groups.new(name="thigh."+side)
  vg.add(list(range(len(ob.data.vertices))),1,"REPLACE")
  mod=ob.modifiers.new("Rigid skin","ARMATURE");mod.object=rig
  mod.use_deform_preserve_volume=False

for n,bone,loc,size,mat in parts:
 bpy.ops.mesh.primitive_cube_add(size=1)
 ob=bpy.context.object;ob.name=n;ob.dimensions=size
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
clips=("Idle","Run","Punch","Dodge")
for clip in clips:
 a=bpy.data.actions.new("Mecha_"+clip)
 rig.animation_data.action=a
 for frame in (1,13,25,37,48):
  z=math.sin(2*math.pi*(frame-1)/47)
  for b in poses:b.rotation_mode="XYZ";b.rotation_euler=(0,0,0);b.location=(0,0,0)
  if clip=="Idle":poses["spine"].rotation_euler[0]=.025*z
  if clip=="Run":
   poses["root"].location.z=.04*abs(z)
   for side,sign in (("L",1),("R",-1)):
    poses["thigh."+side].rotation_euler[0]=sign*.58*z
    poses["shin."+side].rotation_euler[0]=max(0,-sign*z)*.55
    poses["upper_arm."+side].rotation_euler[0]=-sign*.46*z
  if clip=="Punch":
   amt=max(0,1-abs(frame-25)/18)
   poses["upper_arm.R"].rotation_euler[0]=-1.15*amt
   poses["forearm.R"].rotation_euler[0]=-.55*amt
   poses["spine"].rotation_euler[2]=-.15*amt
  if clip=="Dodge":
   amt=max(0,1-abs(frame-25)/20)
   poses["spine"].rotation_euler[1]=.3*amt
   poses["root"].location.x=.14*amt
  for b in poses:
   b.keyframe_insert(data_path="rotation_euler",frame=frame)
   if b.name=="root":b.keyframe_insert(data_path="location",frame=frame)
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
report={"blender_version":bpy.app.version_string,"bones":len(arm.bones),
        "mesh_parts":len(parts)+4,"knee_design":"separate thigh/shin armor, knee pivots, frontal caps and side axle pins","animations":names,
        "skins":len(document["skins"]),"glb_bytes":total,
        "method":"procedural Blender Python (not Choreographer AI)"}
(out/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
print("SMOKE_TEST_PASSED",report)
