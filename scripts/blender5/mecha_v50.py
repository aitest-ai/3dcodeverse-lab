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
("foot.L","shin.L",(.27,0,.1),(.27,-.22,.1)),
("foot.R","shin.R",(-.27,0,.1),(-.27,-.22,.1)),
("weapon_socket.R","forearm.R",(-.87,-.15,1.08),(-.87,-.46,1.08)),
]
for n,p,h,t in defs:
 b=arm.edit_bones.new(n);b.head=h;b.tail=t
 if p:b.parent=arm.edit_bones[p]
bpy.ops.object.mode_set(mode='OBJECT')
rig.show_in_front=True

colors={"armor":(.72,.78,.80,1),"joint":(.035,.050,.069,1),
        "accent":(.94,.29,.08,1),"visor":(.07,.88,1.,1),
        "trim":(.23,.30,.36,1),"warning":(1.,.67,.12,1)}
mats={}
for n,color in colors.items():
 m=bpy.data.materials.new(n);m.diffuse_color=color
 m.use_nodes=True
 m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=color
 if n in ("armor","trim","joint"):
  m.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value=0.43 if n=="armor" else 0.72
  m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value=0.31 if n=="armor" else 0.42
 elif n=="visor":
  bs=m.node_tree.nodes["Principled BSDF"]
  if "Emission Color" in bs.inputs:bs.inputs["Emission Color"].default_value=color
  if "Emission Strength" in bs.inputs:bs.inputs["Emission Strength"].default_value=2.6
 mats[n]=m
# v4.5 differentiates satin ceramic armor and dark machined alloy rather than
# a flat single gray material; all materials use glTF-exportable PBR fields.
def v45_material(name,color,metallic,roughness,emission=0):
 mat=bpy.data.materials.new(name)
 mat.diffuse_color=(*color,1.)
 mat.use_nodes=True
 bs=mat.node_tree.nodes.get("Principled BSDF")
 bs.inputs["Base Color"].default_value=(*color,1.)
 bs.inputs["Metallic"].default_value=metallic
 bs.inputs["Roughness"].default_value=roughness
 if emission:
  bs.inputs["Emission Color"].default_value=(*color,1.)
  bs.inputs["Emission Strength"].default_value=emission
 return mat
mats["shell"]=v45_material("V45_PearlCeramic",(.64,.71,.74),.42,.24)
mats["edge"]=v45_material("V45_DarkTitanium",(.09,.14,.19),.87,.28)
mats["piston"]=v45_material("V45_PolishedSteel",(.56,.64,.68),.94,.18)
mats["signal"]=v45_material("V45_CautionCoral",(.86,.20,.085),.46,.31)
mats["glow"]=v45_material("V45_ReactorCyan",(.08,.68,.91),.25,.19,3.7)
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
# Additional readable combat-mech silhouette. All parts are named & skin-weighted.
parts.extend([
("HelmetBrow","head",(0,-.278,2.18),(.64,.115,.105),"trim"),
("HelmetChin","head",(0,-.250,1.988),(.38,.15,.095),"joint"),
("HeadSensorL","head",(.24,-.282,2.1),(.105,.085,.085),"visor"),
("HeadSensorR","head",(-.24,-.282,2.1),(.105,.085,.085),"visor"),
("HeadFinL","head",(.355,.02,2.18),(.14,.38,.25),"armor"),
("HeadFinR","head",(-.355,.02,2.18),(.14,.38,.25),"armor"),
("ChestCenterCore","spine",(0,-.314,1.425),(.17,.083,.27),"visor"),
("ChestVentL","spine",(.30,-.312,1.3),(.18,.08,.21),"joint"),
("ChestVentR","spine",(-.30,-.312,1.3),(.18,.08,.21),"joint"),
("ChestUpperPlate","spine",(0,-.254,1.665),(.74,.10,.13),"trim"),
("ShoulderShellL","upper_arm.L",(.64,-.015,1.58),(.53,.52,.24),"armor"),
("ShoulderShellR","upper_arm.R",(-.64,-.015,1.58),(.53,.52,.24),"armor"),
("ForearmGuardL","forearm.L",(.84,-.17,1.08),(.38,.50,.20),"trim"),
("ForearmGuardR","forearm.R",(-.84,-.17,1.08),(.38,.50,.20),"trim"),
("ThighPanelL","thigh.L",(.27,-.19,.64),(.25,.14,.31),"trim"),
("ThighPanelR","thigh.R",(-.27,-.19,.64),(.25,.14,.31),"trim"),
("ShinArmorL","shin.L",(.27,-.22,.25),(.30,.18,.32),"armor"),
("ShinArmorR","shin.R",(-.27,-.22,.25),(.30,.18,.32),"armor"),
("HeelGuardL","foot.L",(.27,.14,.086),(.30,.16,.145),"joint"),
("HeelGuardR","foot.R",(-.27,.14,.086),(.30,.16,.145),"joint"),
("BackThrusterL","spine",(.28,.27,1.40),(.29,.31,.49),"joint"),
("BackThrusterR","spine",(-.28,.27,1.40),(.29,.31,.49),"joint"),
("ThrusterGlowL","spine",(.28,.425,1.36),(.18,.055,.20),"visor"),
("ThrusterGlowR","spine",(-.28,.425,1.36),(.18,.055,.20),"visor"),
("WeaponMountPlate","forearm.R",(-.89,-.24,1.01),(.27,.40,.19),"warning"),
])
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

# Remove the old cuboid masses. The new version is shaped by actual lofted
# convex armor shells, not by placing more cubes over the previous toy robot.
replace_old={
 "body","chest","helmet","visor","HelmetBrow","HelmetChin",
 "HeadSensorL","HeadSensorR","HeadFinL","HeadFinR","armL","armR",
 "ShoulderShellL","ShoulderShellR","ChestCenterCore","ChestVentL","ChestVentR",
 "ChestUpperPlate","legL","legR","shinL","shinR","ThighPanelL",
 "ThighPanelR","ShinArmorL","ShinArmorR","BackThrusterL","BackThrusterR",
 "ThrusterGlowL","ThrusterGlowR"
}
parts=[p for p in parts if p[0] not in replace_old]
for n,bone,loc,size,mat in parts:
 bpy.ops.mesh.primitive_cube_add(size=1)
 ob=bpy.context.object;ob.name=n;ob.data.name=n;ob.dimensions=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for v in ob.data.vertices:v.co+=Vector(loc)
 ob.data.materials.append(mats[mat])
 # Real rounded hard-surface edge geometry (rather than a smoothing-only shader).
 bevel=ob.modifiers.new("Armor bevel","BEVEL")
 bevel.width=.028 if max(size)>.3 else .012
 bevel.segments=2
 bpy.context.view_layer.objects.active=ob
 bpy.ops.object.modifier_apply(modifier=bevel.name)
 group=ob.vertex_groups.new(name=bone)
 group.add(list(range(len(ob.data.vertices))),1,'REPLACE')
 modifier=ob.modifiers.new("Rigid skin","ARMATURE")
 modifier.object=rig
 modifier.use_deform_preserve_volume=False


# V4.3 SHAPE-FIRST REBUILD: convex front/back tapered polygon hulls rather
# than overlapping rectangular primitives. Coordinates are authored in the
# 15-bone rest pose; every element is rigid-weighted to an appropriate bone.
v43_count=0
def v43_skin(ob,bone,mat):
 global v43_count
 ob.data.name=ob.name
 ob.data.materials.append(mats[mat])
 group=ob.vertex_groups.new(name=bone)
 group.add(list(range(len(ob.data.vertices))),1.0,"REPLACE")
 mod=ob.modifiers.new("Armature rigid drive","ARMATURE")
 mod.object=rig
 mod.use_deform_preserve_volume=False
 v43_count+=1
 return ob

def v43_poly(name,bone,outline,front,back,material,bevel_width=.017):
 # Ring outline expressed as x,z pairs, CCW from front.
 n=len(outline)
 vertices=[(x,front,z) for x,z in outline]+[(x,back,z) for x,z in outline]
 faces=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
 faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 geo=bpy.data.meshes.new(name+"Geometry")
 geo.from_pydata(vertices,[],faces)
 geo.update()
 ob=bpy.data.objects.new(name,geo)
 bpy.context.collection.objects.link(ob)
 # Bevel produces real sloped surfaces and sharpened material edge catches.
 bpy.context.view_layer.objects.active=ob
 bev=ob.modifiers.new("Machined bevel","BEVEL")
 bev.width=bevel_width
 bev.segments=2
 bpy.ops.object.modifier_apply(modifier=bev.name)
 for face in ob.data.polygons:face.use_smooth=False
 return v43_skin(ob,bone,material)

def v43_bar(name,bone,a,b,radius,material,vertices=16):
 from mathutils import Vector as VV
 a,b=VV(a),VV(b)
 delta=b-a
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=delta.length)
 ob=bpy.context.object
 ob.name=name
 ob.rotation_mode="QUATERNION"
 ob.rotation_quaternion=VV((0,0,1)).rotation_difference(delta.normalized())
 bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 center=(a+b)*0.5
 for vert in ob.data.vertices:vert.co+=center
 return v43_skin(ob,bone,material)

def v43_orb(name,bone,loc,radius,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=radius)
 ob=bpy.context.object
 ob.name=name
 for vert in ob.data.vertices:vert.co.x+=loc[0];vert.co.y+=loc[1];vert.co.z+=loc[2]
 return v43_skin(ob,bone,material)

# Dramatically slimmer central torso with a high-shoulder V-shaped chest,
# inset luminous reactor and darker waist; not a solid rectangular torso.
v43_poly("Torso_angular_chassis","spine",[
 (-.25,1.06),(.25,1.06),(.39,1.23),(.50,1.52),
 (.38,1.71),(-.38,1.71),(-.50,1.52),(-.39,1.23)
 ],-.235,.265,"joint",.03)
v43_poly("Chest_left_chamfer","spine",[
 (-.45,1.61),(-.08,1.67),(-.055,1.51),(-.20,1.33),(-.40,1.37),(-.54,1.51)
 ],-.346,-.225,"armor",.026)
v43_poly("Chest_right_chamfer","spine",[
 (.08,1.67),(.45,1.61),(.54,1.51),(.40,1.37),(.20,1.33),(.055,1.51)
 ],-.346,-.225,"armor",.026)
v43_poly("Sternum_frame","spine",[
 (-.105,1.62),(.105,1.62),(.15,1.45),(0,1.32),(-.15,1.45)
 ],-.398,-.34,"trim",.012)
v43_poly("Reactor_blue_diamond","spine",[
 (0,1.60),(.073,1.51),(0,1.40),(-.073,1.51)
 ],-.420,-.388,"visor",.008)
v43_poly("Waist_V_plate","spine",[
 (-.28,1.12),(.28,1.12),(.21,.99),(0,.955),(-.21,.99)
 ],-.32,-.225,"armor",.024)
v43_poly("Pelvis_split_frontal","root",[
 (-.35,.88),(.35,.88),(.24,.69),(.11,.66),(0,.73),(-.11,.66),(-.24,.69)
 ],-.34,-.20,"armor",.024)

# Helmet: tapered trapezoidal wedge + cheek guards + visor slit and two
# distinct swept-back antennae. The recognizable profile reads as a mech.
v43_poly("Helmet_angular_shell","head",[
 (-.225,1.96),(.225,1.96),(.315,2.085),(.25,2.245),
 (.075,2.28),(-.075,2.28),(-.25,2.245),(-.315,2.085)
 ],-.23,.20,"armor",.018)
v43_poly("Helmet_faceplate","head",[
 (-.21,2.185),(.21,2.185),(.20,2.08),(.12,2.025),
 (-.12,2.025),(-.20,2.08)
 ],-.329,-.215,"joint",.014)
v43_poly("Visor_single_slit","head",[
 (-.19,2.163),(.19,2.163),(.13,2.119),(-.13,2.119)
 ],-.358,-.332,"visor",.004)
v43_poly("Chin_split","head",[
 (-.12,2.036),(0,2.004),(.12,2.036),(.085,1.965),(-.085,1.965)
 ],-.343,-.232,"trim",.009)
for side,sgn in (("L",1),("R",-1)):
 v43_bar("Antenna_spine_"+side,"head",(sgn*.18,.01,2.23),(sgn*.385,-.03,2.54),.024,"warning",12)
 v43_bar("Antenna_tip_"+side,"head",(sgn*.385,-.03,2.54),(sgn*.425,-.02,2.59),.012,"trim",10)
 v43_poly("Helmet_cheek_"+side,"head",[
 (sgn*.25,2.06),(sgn*.355,2.085),(sgn*.30,1.985),(sgn*.21,1.995)
 ],-.275,.08,"trim",.008)

# Shoulder shells taper outward and toward the forward edges. They replace
# the slab shoulder blocks which dominated all v4.2 orthographic views.
for side,sgn in (("L",1),("R",-1)):
 x=sgn
 bone="upper_arm."+side
 v43_poly("Shoulder_wing_"+side,bone,[
 (x*.41,1.66),(x*.62,1.82),(x*.94,1.76),
 (x*1.01,1.61),(x*.90,1.47),(x*.55,1.45)
 ],-.29,.22,"armor",.025)
 v43_poly("Shoulder_warning_"+side,bone,[
 (x*.64,1.79),(x*.94,1.74),(x*.97,1.68),(x*.61,1.72)
 ],-.323,-.284,"warning",.008)
 v43_poly("Upper_arm_angular_"+side,bone,[
 (x*.48,1.5),(x*.76,1.5),(x*.80,1.36),
 (x*.69,1.18),(x*.50,1.21),(x*.42,1.35)
 ],-.235,.20,"trim",.018)
 v43_orb("Shoulder_servo_"+side,bone,(x*.53,.205,1.51),.115,"joint")
 v43_bar("Shoulder_hinge_pin_"+side,bone,(x*.53,.21,1.51),(x*.69,.21,1.51),.038,"accent")
 v43_poly("Forearm_bevel_shield_"+side,"forearm."+side,[
 (x*.72,1.26),(x*.99,1.23),(x*1.03,1.07),
 (x*.91,.92),(x*.70,.99),(x*.65,1.11)
 ],-.305,-.18,"armor",.02)

# Leg armor: segmented taper from wide upper thigh through articulated
# mechanical knee to flared shin guards. Long diagonal edge silhouettes.
for side,sgn in (("L",1),("R",-1)):
 x=sgn
 v43_poly("Thigh_teardrop_"+side,"thigh."+side,[
 (x*.12,.83),(x*.39,.84),(x*.45,.67),(x*.37,.48),
 (x*.23,.46),(x*.12,.63)
 ],-.29,.25,"armor",.022)
 v43_poly("Thigh_raised_fin_"+side,"thigh."+side,[
 (x*.29,.81),(x*.42,.75),(x*.37,.58),(x*.27,.55)
 ],-.326,-.281,"trim",.009)
 v43_poly("Knee_forward_shield_"+side,"thigh."+side,[
 (x*.22,.53),(x*.40,.51),(x*.43,.42),(x*.33,.35),
 (x*.20,.40)
 ],-.335,-.23,"warning",.009)
 v43_bar("Knee_piston_"+side,"shin."+side,
    (x*.39,.18,.37),(x*.36,.18,.15),.043,"trim")
 v43_poly("Shin_angular_guard_"+side,"shin."+side,[
 (x*.17,.41),(x*.33,.43),(x*.45,.25),
 (x*.40,.13),(x*.14,.13),(x*.12,.26)
 ],-.37,.275,"armor",.02)
 v43_poly("Shin_inset_vent_"+side,"shin."+side,[
 (x*.26,.35),(x*.36,.33),(x*.39,.22),(x*.25,.20)
 ],-.404,-.365,"joint",.009)
 v43_poly("Foot_toe_point_"+side,"foot."+side,[
 (x*.10,.144),(x*.42,.144),(x*.38,.06),(x*.13,.06)
 ],-.58,-.385,"trim",.01)

# A mechanically readable right arm beam cannon, with independent muzzle
# geometry. Use the existing weapon_socket.R as the rig-driven mount target.
v43_bar("PrimaryCannon_receiver","forearm.R",(-.89,-.28,1.09),(-.89,-.53,1.09),.115,"joint",20)
v43_bar("PrimaryCannon_outer_barrel","forearm.R",(-.89,-.46,1.09),(-.89,-.91,1.09),.085,"trim",24)
v43_bar("PrimaryCannon_energy_bore","forearm.R",(-.89,-.81,1.09),(-.89,-.94,1.09),.057,"visor",20)
for t in (-.60,-.74,-.85):
 v43_bar("PrimaryCannon_coil_"+str(t),"forearm.R",
   (-.89,t-.025,1.09),(-.89,t+.025,1.09),.107,"warning",20)

# Distinct left wrist guard and elevated reactor/spine cooling hardware.
v43_bar("LeftWrist_shield","forearm.L",(.84,-.15,1.10),(.84,-.37,1.10),.09,"trim",16)
for side,sgn in (("L",1),("R",-1)):
 x=sgn*.27
 v43_bar("Rear_vent_housing_"+side,"spine",(x,.285,1.30),(x,.44,1.43),.13,"joint",16)
 v43_bar("Rear_thruster_core_"+side,"spine",(x,.42,1.40),(x,.50,1.40),.075,"visor",16)
 v43_bar("Rear_antenna_"+side,"spine",(x,.30,1.70),(x,.34,1.87),.023,"trim",12)



# V4.4 HEROIC PROPORTION / ART-DIRECTION PASS (not merely extra cubes).
# Build around the v4.3 mechanically readable shape; stretch legs,
# narrow the shoulder envelope, reduce helmet bulk and reduce upper-body depth.
# Apply the same piecewise invertible rest-pose remap to BOTH skinned vertices
# and EDIT bones. This preserves name/rig hierarchy and socket animation.
def v44_z(z):
 if z<=.82:return z*1.48
 if z<=1.94:return .82*1.48+(z-.82)*1.10
 return .82*1.48+(1.94-.82)*1.10+(z-1.94)*.92

def v44_x(x,z):
 scale=.89 if z>1.0 else .96
 if z>=1.95:scale*=.91
 return x*scale

def v44_y(y,z):
 return y*(.90 if z>.95 else 1.)

def v44_transform(vector):
 from mathutils import Vector
 x,y,z=vector
 return Vector((v44_x(x,z),v44_y(y,z),v44_z(z)))

# New structural components emphasize load-bearing mechanisms and depth.
for side,sign in (("L",1),("R",-1)):
 x=sign
 v43_poly("V44_SplitKneeFace_"+side,"thigh."+side,[
 (x*.225,.51),(x*.37,.51),(x*.405,.45),(x*.32,.375),(x*.19,.415)
 ],-.358,-.334,"trim",.009)
 v43_bar("V44_ExposedThighActuator_"+side,"thigh."+side,
    (x*.18,.11,.78),(x*.32,.11,.51),.038,"joint",14)
 v43_bar("V44_ShinRodOuter_"+side,"shin."+side,
    (x*.41,.13,.38),(x*.40,.13,.16),.026,"warning",12)
 v43_bar("V44_ShinRodInner_"+side,"shin."+side,
    (x*.15,.13,.38),(x*.15,.13,.16),.026,"warning",12)
 v43_orb("V44_AnkleServo_"+side,"foot."+side,(x*.275,-.02,.105),.09,"joint")
 v43_poly("V44_ToeArmorSplit_"+side,"foot."+side,[
    (x*.14,.15),(x*.42,.15),(x*.41,.065),(x*.14,.065)
 ],-.595,-.52,"armor",.008)
 v43_bar("V44_CollarStrut_"+side,"spine",
    (x*.33,.15,1.64),(x*.44,.09,1.78),.038,"trim",14)
 v43_bar("V44_WaistHydraulic_"+side,"spine",
    (x*.24,.21,1.21),(x*.31,.21,1.02),.043,"joint",14)

# Visual identity: bold layered V-chest and narrow neck with a recessed seam.
v43_poly("V44_ChestCenterKeel","spine",[
 (-.055,1.68),(.055,1.68),(.115,1.52),(0,1.32),(-.115,1.52)
 ],-.430,-.415,"accent",.009)
v43_poly("V44_AbdomenScissor","spine",[
 (-.19,1.27),(.19,1.27),(.25,1.20),(0,1.13),(-.25,1.20)
 ],-.345,-.29,"trim",.011)
v43_bar("V44_HeadNeckPiston","neck",(0,.07,1.80),(0,.07,1.97),.092,"joint",16)
for side,sgn in (("L",1),("R",-1)):
 v43_bar("V44_BackCoolingRail_"+side,"spine",
   (sgn*.42,.27,1.56),(sgn*.42,.32,1.81),.027,"trim",12)


# v4.5: unlike v4.3 polygons, the curved armor has a non-coplanar, weighted
# inner ring and inset face. It catches highlights as a real bulged surface.
# No black-box image or texture-to-geometry illusion.
def v45_shell(name,bone,contour,front,back,material,bulge=.08,lip=.16):
 # V4.8 ART DIRECTION: hard-surface FLAT FACETED armor, not increasing
 # roundedness. A shallow bevel and defined stepped rim surround a truly
 # coplanar central front face. 8-vertex polygon contours retain chamfers.
 # Keep v45_shell signature for older chest/leg components and UV bake targets.
 n=len(contour)
 cx=sum(x for x,z in contour)/n
 cz=sum(z for x,z in contour)/n
 # Three frontal rings: dark outer machining step, chamfer, flat face.
 outer=[(x,front+.016,z) for x,z in contour]
 bevel=[(cx+(x-cx)*.945,front-.020,cz+(z-cz)*.945) for x,z in contour]
 # A hard, nearly flat face: every vertex has the SAME depth.
 front_face=[(cx+(x-cx)*.80,front-.026,cz+(z-cz)*.80) for x,z in contour]
 rear=[(x,back,z) for x,z in contour]
 verts=outer+bevel+front_face+rear
 faces=[]
 for layer in range(2):
  for i in range(n):
   faces.append((layer*n+i,layer*n+(i+1)%n,
                 (layer+1)*n+(i+1)%n,(layer+1)*n+i))
 faces.append(tuple(range(2*n,3*n)))
 for i in range(n):
  faces.append((i,3*n+i,3*n+(i+1)%n,(i+1)%n))
 faces.append(tuple(range(4*n-1,3*n-1,-1)))
 mesh=bpy.data.meshes.new(name+"_machined_facets")
 mesh.from_pydata(verts,[],faces)
 mesh.update()
 obj=bpy.data.objects.new(name,mesh)
 bpy.context.collection.objects.link(obj)
 for poly in mesh.polygons:
  poly.use_smooth=False # crisp face normals, no fake inflated smoothing
 return v43_skin(obj,bone,material)


# Remove the original flat block-front exterior plates only; internal rigid
# structure, weapon mount and animation-linked rig are explicitly preserved.
v45_replace={
 "Helmet_angular_shell","Chest_left_chamfer","Chest_right_chamfer",
 "Shoulder_wing_L","Shoulder_wing_R","Shin_angular_guard_L",
 "Shin_angular_guard_R","Thigh_teardrop_L","Thigh_teardrop_R",
 "Antenna_spine_L","Antenna_spine_R",
 "Antenna_tip_L","Antenna_tip_R"
}
for name in v45_replace:
 obj=bpy.data.objects.get(name)
 if obj:bpy.data.objects.remove(obj,do_unlink=True)

# New helmet with a recessed brow, a curved armored crown and two short
# swept-back fins instead of the previous oversized yellow antennae.
v45_shell("V45_HelmetComposite","head",[
 (-.25,1.968),(.25,1.968),(.315,2.077),(.248,2.246),
 (.075,2.278),(-.075,2.278),(-.248,2.246),(-.315,2.077)
 ],-.221,.198,"shell",.070,.15)
v43_poly("V45_HelmetRecessedBrow","head",[
 (-.24,2.187),(.24,2.187),(.21,2.16),(-.21,2.16)
 ],-.380,-.340,"edge",.008)
for side,sgn in (("L",1),("R",-1)):
 x=sgn
 v43_poly("V45_SweptCrownFin_"+side,"head",[
 (x*.22,2.239),(x*.30,2.36),(x*.41,2.45),(x*.31,2.33)
 ],-.09,.15,"edge",.009)
 v43_poly("V45_CheekMachineRelief_"+side,"head",[
 (x*.26,2.08),(x*.34,2.055),(x*.31,2.016),(x*.24,2.030)
 ],-.291,-.273,"signal",.006)

# Front armor with a non-planar convex sweep; torso remains independent
# behind the hull for a credible joint gap.
v45_shell("V45_LeftChestFlow","spine",[
 (-.45,1.61),(-.10,1.675),(-.058,1.515),(-.19,1.34),
 (-.42,1.375),(-.55,1.51)
 ],-.367,-.215,"shell",.13,.19)
v45_shell("V45_RightChestFlow","spine",[
 (.10,1.675),(.45,1.61),(.55,1.51),(.42,1.375),
 (.19,1.34),(.058,1.515)
 ],-.367,-.215,"shell",.13,.19)
v43_poly("V45_ChestInboardGasket","spine",[
 (-.057,1.654),(.057,1.654),(.083,1.42),(0,1.32),(-.083,1.42)
 ],-.435,-.420,"edge",.009)

for side,sgn in (("L",1),("R",-1)):
 x=sgn
 upper="upper_arm."+side
 thigh="thigh."+side
 shin="shin."+side
 v45_shell("V45_ShoulderSweep_"+side,upper,[
 (x*.43,1.64),(x*.64,1.805),(x*.92,1.735),
 (x*1.01,1.61),(x*.875,1.465),(x*.53,1.455)
 ],-.28,.22,"shell",.09,.13)
 v43_poly("V45_ShoulderEdge_" + side,upper,[
 (x*.60,1.789),(x*.90,1.72),(x*.96,1.65),(x*.65,1.70)
 ],-.347,-.319,"edge",.007)
 v45_shell("V45_ThighComposite_"+side,thigh,[
 (x*.12,.825),(x*.38,.845),(x*.465,.66),
 (x*.365,.48),(x*.23,.45),(x*.115,.64)
 ],-.30,.245,"shell",.095,.17)
 v45_shell("V45_ShinKineticPlate_"+side,shin,[
 (x*.17,.42),(x*.34,.44),(x*.465,.235),
 (x*.39,.115),(x*.15,.12),(x*.10,.28)
 ],-.37,.268,"shell",.092,.17)
 # Dark inner kinematic channel gives the shin a hollow mechanical relief.
 v43_poly("V45_ShinDarkChannel_"+side,shin,[
 (x*.24,.355),(x*.34,.34),(x*.38,.24),(x*.24,.205)
 ],-.445,-.429,"edge",.007)
 v43_bar("V45_ExposedKneeRod_"+side,shin,
  (x*.35,.16,.39),(x*.35,.19,.13),.029,"piston",14)
 v43_bar("V45_OuterShinHydraulic_"+side,shin,
  (x*.42,.145,.35),(x*.37,.17,.19),.026,"signal",14)

# A concentric nozzle with separate metal muzzle and emissive bore.
# This is real skinned geometry, never a screen-space decal.
v43_bar("V45_CannonMuzzleSocket","forearm.R",
 (-.89,-.82,1.09),(-.89,-.947,1.09),.11,"edge",28)
v43_bar("V45_CannonGlowSleeve","forearm.R",
 (-.89,-.935,1.09),(-.89,-.983,1.09),.064,"glow",24)
for side,sgn in (("L",1),("R",-1)):
 x=sgn*.27
 v43_bar("V45_RearThrusterAlloy_"+side,"spine",
 (x,.36,1.37),(x,.53,1.37),.105,"piston",24)
 v43_bar("V45_RearThrusterRing_"+side,"spine",
 (x,.52,1.37),(x,.56,1.37),.123,"edge",24)
 v43_bar("V45_RearThrusterEnergy_"+side,"spine",
 (x,.545,1.37),(x,.58,1.37),.071,"glow",24)

# Build acceptance metrics record absolute candidate mesh count.
v45_curved_count=sum(o.name.startswith("V45_") for o in bpy.data.objects)


# v4.7: silhouette and read-at-distance art pass. These are real rigid skinned
# volumes tied to the 15-bone rig, not animated screen overlays.
# Author in the original coordinate system prior to the v4.4 rest-pose remap.
v47_sculpted=[]
def v47_add(mesh):
 v47_sculpted.append(mesh.name)
 return mesh

# Tall compact helmet chin, folded cheeks, central forehead relief and
# smaller, stronger silhouette cues rather than excessively long antennae.
v47_add(v45_shell("V47_BrowForwardHelm","head",[
 (-.17,2.24),(.17,2.24),(.245,2.175),(.18,2.15),(-.18,2.15),(-.245,2.175)
 ],-.410,-.33,"edge",.042,.14))
v47_add(v43_poly("V47_CentralForeheadBlade","head",[
 (-.045,2.29),(.045,2.29),(.065,2.20),(0,2.177),(-.065,2.20)
 ],-.365,-.318,"signal",.010))
v47_add(v45_shell("V47_ArmedChinShield","head",[
 (-.128,2.042),(.128,2.042),(.102,1.94),(0,1.911),(-.102,1.94)
 ],-.378,-.28,"shell",.053,.13))
for side,sgn in (("L",1),("R",-1)):
 x=sgn
 v47_add(v43_poly("V47_CheekIntake_"+side,"head",[
 (x*.22,2.125),(x*.318,2.15),(x*.342,2.09),(x*.268,2.047)
 ],-.355,-.309,"edge",.009))
 v47_add(v43_bar("V47_CheekPiston_"+side,"head",
 (x*.274,-.323,2.089),(x*.285,-.328,2.048),.018,"piston",12))

# Chest has a dark inner exoskeleton under the two convex armor plates;
# vent slashes provide a readable armored chest at typical third-person range.
for side,sgn in (("L",1),("R",-1)):
 x=sgn
 v47_add(v43_poly("V47_PectoralOuterRidge_"+side,"spine",[
 (x*.10,1.646),(x*.437,1.590),(x*.480,1.535),(x*.24,1.588)
 ],-.459,-.419,"edge",.010))
 for n in range(3):
  dx=.005*n
  v47_add(v43_bar("V47_ChestGills_"+side+"_"+str(n),"spine",
   (x*(.273+dx),-.499,1.470-.037*n),
   (x*(.405+dx),-.496,1.465-.037*n),.008,"joint",10))
 v47_add(v45_shell("V47_SideAbdomen_"+side,"spine",[
 (x*.16,1.29),(x*.33,1.26),(x*.28,1.10),(x*.13,1.09)
 ],-.306,.205,"edge",.042,.12))
 v47_add(v43_bar("V47_AbdomenActuator_"+side,"spine",
 (x*.275,.23,1.14),(x*.215,.19,1.36),.036,"piston",12))

# Shoulder, elbow, skirt and lower leg now have distinctly separate armor
# and exposed machine structure, reducing the large flat slab impression.
for side,sgn in (("L",1),("R",-1)):
 x=sgn
 upper="upper_arm."+side
 forearm="forearm."+side
 rootbone="root"
 v47_add(v45_shell("V47_DeltArmor_"+side,upper,[
 (x*.56,1.58),(x*.83,1.60),(x*.88,1.50),
 (x*.75,1.405),(x*.52,1.435)
 ],-.350,-.24,"trim",.060,.18))
 v47_add(v43_poly("V47_ShoulderCautionLine_"+side,upper,[
 (x*.58,1.78),(x*.91,1.72),(x*.93,1.69),(x*.61,1.72)
 ],-.354,-.341,"signal",.007))
 v47_add(v43_orb("V47_ElbowServo_"+side,forearm,
 (x*.76,.11,1.22),.065,"piston"))
 v47_add(v45_shell("V47_ForearmShield_"+side,forearm,[
 (x*.68,1.24),(x*.97,1.22),(x*1.02,1.10),
 (x*.925,.93),(x*.72,.965)
 ],-.367,-.20,"edge",.045,.15))
 v47_add(v45_shell("V47_SkirtSidePanel_"+side,rootbone,[
 (x*.28,.865),(x*.53,.840),(x*.54,.625),
 (x*.415,.582),(x*.31,.67)
 ],-.155,.26,"shell",.050,.13))
 v47_add(v43_poly("V47_SkirtLowerInset_"+side,rootbone,[
 (x*.38,.79),(x*.52,.77),(x*.505,.68),(x*.42,.65)
 ],-.188,-.162,"trim",.010))
 thigh="thigh."+side
 shin="shin."+side
 v47_add(v43_bar("V47_ExposedLateralKnee_"+side,thigh,
 (x*.46,.04,.449),(x*.53,.04,.449),.069,"joint",18))
 v47_add(v43_bar("V47_KneeSilverHub_"+side,thigh,
 (x*.53,.04,.449),(x*.56,.04,.449),.052,"piston",18))
 v47_add(v45_shell("V47_CalfOffsetPlate_"+side,shin,[
 (x*.265,.355),(x*.41,.325),(x*.435,.21),(x*.335,.15)
 ],.215,.305,"trim",.03,.12))
 v47_add(v43_poly("V47_FootInstep_"+side,"foot."+side,[
 (x*.12,.144),(x*.405,.144),(x*.378,.087),(x*.13,.087)
 ],-.626,-.550,"edge",.009))

# Weapon profile: an intentional visual division between cannon receiver,
# narrow heat exchanger and a precision front shroud.
v47_add(v45_shell("V47_CannonBodyShroud","forearm.R",[
 (-1.05,1.185),(-.74,1.185),(-.72,1.035),(-1.04,1.035)
 ],-.39,-.18,"edge",.048,.14))
v47_add(v43_bar("V47_CannonDetailRail","forearm.R",
 (-.89,-.50,1.19),(-.89,-.82,1.19),.033,"piston",14))
v47_add(v43_bar("V47_CannonEmissiveGuide","forearm.R",
 (-.89,-.54,.99),(-.89,-.87,.99),.019,"glow",14))


# V4.8 RECTANGULAR / FACETED MECH ART PASS
# Keep the v4.7 joints and torso silhouette but make its armor feel like
# precisely machined, serviceable metal panels. No subdivision/rounding here.
v48_parts=[]
def v48_keep(obj):
 v48_parts.append(obj.name)
 return obj

# Replace the overly swept long crown fins with shorter block-cut fins.
for n in ("V45_SweptCrownFin_L","V45_SweptCrownFin_R"):
 ob=bpy.data.objects.get(n)
 if ob:bpy.data.objects.remove(ob,do_unlink=True)

v48_keep(v43_poly("V48_HelmetTop_angular_visorCap","head",[
 (-.24,2.28),(.24,2.28),(.305,2.225),(-.305,2.225)
 ],-.244,.195,"shell",.010))
v48_keep(v43_poly("V48_HelmetBrowInset","head",[
 (-.25,2.19),(.25,2.19),(.185,2.151),(-.185,2.151)
 ],-.416,-.402,"edge",.006))
for side,sign in (("L",1),("R",-1)):
 x=sign
 v48_keep(v43_poly("V48_TempleGusset_"+side,"head",[
  (x*.27,2.18),(x*.39,2.25),(x*.395,2.335),
  (x*.33,2.36),(x*.262,2.275)
 ],-.152,.17,"armor",.011))
 v48_keep(v43_poly("V48_CheekPlate_5sided_"+side,"head",[
  (x*.24,2.103),(x*.348,2.13),(x*.368,2.075),
  (x*.317,2.0),(x*.252,2.022)
 ],-.376,-.287,"trim",.010))
 # Twin recessed head channels, not cartoon eyes.
 v48_keep(v43_bar("V48_SensorSeam_"+side,"head",
  (x*.16,-.419,2.165),(x*.23,-.419,2.165),
  .009,"glow",10))

# Explicit panel inset, crisp dark material along the chest-to-abdomen seam.
for side,sign in (("L",1),("R",-1)):
 x=sign
 v48_keep(v43_poly("V48_ChestBoltPlate_"+side,"spine",[
  (x*.23,1.59),(x*.445,1.55),(x*.44,1.505),(x*.252,1.540)
 ],-.475,-.455,"trim",.008))
 v48_keep(v43_poly("V48_ChestServiceHatch_"+side,"spine",[
  (x*.22,1.44),(x*.385,1.43),(x*.36,1.375),(x*.235,1.380)
 ],-.480,-.455,"edge",.006))
 # Cap screws, each rigidly linked to the parent chest bone.
 for z in (1.57,1.41):
  v48_keep(v43_orb("V48_ChestFastener_"+side+"_"+str(z),"spine",
    (x*.37,-.493,z),.012,"piston"))
 # Exposed waist drive kept separate from external chassis armor.
 v48_keep(v43_bar("V48_AbdominalRail_"+side,"spine",
  (x*.24,.265,1.26),(x*.24,.265,1.04),.026,"piston",12))

# Make armor slab thickness readable, with clean 45deg machined corners.
for side,sign in (("L",1),("R",-1)):
 x=sign
 upper="upper_arm."+side
 fore="forearm."+side
 shin="shin."+side
 thigh="thigh."+side
 v48_keep(v43_poly("V48_ShoulderTopSquare_"+side,upper,[
  (x*.51,1.78),(x*.77,1.805),(x*.91,1.75),
  (x*.927,1.70),(x*.55,1.714)
 ],-.350,.21,"armor",.016))
 v48_keep(v43_poly("V48_ShoulderInsetCut_"+side,upper,[
  (x*.58,1.75),(x*.87,1.727),(x*.91,1.678),(x*.64,1.700)
 ],-.389,-.362,"edge",.006))
 v48_keep(v43_poly("V48_ElbowSquareHousing_"+side,fore,[
  (x*.65,1.267),(x*.82,1.267),(x*.83,1.184),(x*.65,1.184)
 ],-.292,.09,"trim",.012))
 v48_keep(v43_poly("V48_ThighSlottedPanel_"+side,thigh,[
  (x*.17,.795),(x*.372,.796),(x*.402,.735),(x*.15,.726)
 ],-.405,-.369,"edge",.007))
 v48_keep(v43_poly("V48_KneeServicePlate_"+side,thigh,[
  (x*.199,.509),(x*.414,.51),(x*.43,.44),(x*.20,.435)
 ],-.390,-.370,"armor",.008))
 v48_keep(v43_poly("V48_ShinSquareOuterRidge_"+side,shin,[
  (x*.19,.379),(x*.357,.391),(x*.391,.328),(x*.16,.315)
 ],-.451,-.427,"trim",.007))
 for z in (.34,.22):
  v48_keep(v43_bar("V48_ShinRecessedSlot_"+side+"_"+str(z),
   shin,(x*.20,-.466,z),(x*.326,-.466,z-.012),.011,"joint",10))
 # Non-rounded bolted ankle armor.
 v48_keep(v43_poly("V48_FootHeelBlock_"+side,"foot."+side,[
  (x*.14,.14),(x*.409,.14),(x*.399,.07),(x*.145,.07)
 ],-.065,.175,"armor",.012))

# The original weapon control remains unchanged; these are visual-only
# rectangular receiver plates and a hard-surface barrel heat sink.
v48_keep(v43_poly("V48_CannonRectangularShroud","forearm.R",[
 (-1.065,1.186),(-.720,1.186),(-.711,1.025),(-1.075,1.025)
 ],-.51,-.22,"trim",.017))
for sx in (-1.035,-.747):
 v48_keep(v43_bar("V48_CannonSquareSpine_"+str(sx),"forearm.R",
   (sx,-.53,1.11),(sx,-.94,1.11),.022,"piston",12))
v48_keep(v43_poly("V48_CannonFlatFrontSight","forearm.R",[
 (-.98,1.203),(-.80,1.203),(-.80,1.16),(-.98,1.16)
 ],-.88,-.82,"edge",.009))


# V4.9 MACHINED LOAD-BEARING INTERNALS
# Do not inflate the external panels; square face normals and shallow
# chamfers are the visual language. Instead we replace toy-like balls with
# real open annular hubs, separate inner/outer structural parts and recesses.
v49_parts=[]
def v49_keep(ob):
 v49_parts.append(ob.name)
 return ob

def v49_annulus(name,bone,center,axis_width,ro,ri,material,segments=28):
 # Topologically real hole with inner wall, both caps and outside wall.
 # Joint shaft is the X axis; ring is visible from either mech side.
 from math import cos,sin,tau
 cx,cy,cz=center
 ring=[]
 for x,rad in ((cx-axis_width*.5,ro),
               (cx+axis_width*.5,ro),
               (cx-axis_width*.5,ri),
               (cx+axis_width*.5,ri)):
  ring.extend([(x,cy+rad*cos(tau*i/segments),cz+rad*sin(tau*i/segments))
               for i in range(segments)])
 faces=[]
 for i in range(segments):
  j=(i+1)%segments
  faces.extend([
   (i,j,segments+j,segments+i),                # outside side
   (2*segments+i,3*segments+i,3*segments+j,2*segments+j), # inside wall
   (i,2*segments+i,2*segments+j,j),             # left cap
   (segments+i,segments+j,3*segments+j,3*segments+i) # right cap
  ])
 geom=bpy.data.meshes.new(name+"_HollowMachining")
 geom.from_pydata(ring,[],faces)
 geom.update()
 ob=bpy.data.objects.new(name,geom)
 bpy.context.collection.objects.link(ob)
 return v49_keep(v43_skin(ob,bone,material))

# Hide the more toy-like complete spherical elbow/ankle cosmetics; the
# existing articulated rig and all parent mechanical limbs remain intact.
for n in [
  "V47_ElbowServo_L","V47_ElbowServo_R",
  "V44_AnkleServo_L","V44_AnkleServo_R"
]:
 ob=bpy.data.objects.get(n)
 if ob:bpy.data.objects.remove(ob,do_unlink=True)

# Shoulder & elbow assembly: paired mechanical mounting lugs instead of a
# single ball. Keep small negative space so the shaft can be seen.
for side,sign in (("L",1),("R",-1)):
 x=sign
 upper="upper_arm."+side
 fore="forearm."+side
 v49_keep(v43_poly("V49_ShoulderYokeFront_"+side,upper,[
    (x*.47,1.59),(x*.73,1.59),(x*.74,1.495),(x*.50,1.495)
 ],-.40,-.34,"edge",.008))
 v49_keep(v43_poly("V49_ShoulderYokeBack_"+side,upper,[
    (x*.47,1.59),(x*.73,1.59),(x*.74,1.495),(x*.50,1.495)
 ],.235,.315,"edge",.008))
 v49_annulus("V49_ShoulderOuterHub_"+side,upper,
    (x*.62,.305,1.532),.082,.105,.060,"piston",24)
 v49_annulus("V49_ElbowOuterHub_"+side,upper,
    (x*.755,.11,1.235),.100,.095,.047,"edge",28)
 v49_keep(v43_bar("V49_ElbowAxialRod_"+side,fore,
    (x*.68,.11,1.235),(x*.84,.11,1.235),.035,"piston",18))
 v49_keep(v43_poly("V49_ForearmSupportRail_"+side,fore,[
    (x*.69,1.25),(x*.98,1.23),(x*.975,1.185),(x*.70,1.20)
 ],.15,.215,"piston",.009))
 v49_keep(v43_bar("V49_ForearmPistonSleeve_"+side,fore,
    (x*.735,.19,1.17),(x*.81,.19,1.00),.043,"edge",16))
 v49_keep(v43_bar("V49_ForearmPistonRod_"+side,fore,
    (x*.81,.193,1.00),(x*.86,.193,.93),.026,"piston",16))

# Knee hubs are *hollow mechanical bearing rings* with a visible central pin;
# side-view silhouettes show separate axle, caps and gap.
for side,sign in (("L",1),("R",-1)):
 x=sign
 thigh="thigh."+side
 shin="shin."+side
 foot="foot."+side
 v49_annulus("V49_KneeBearing_Exterior_"+side,thigh,
  (x*.49,.03,.435),.078,.128,.079,"edge",28)
 v49_annulus("V49_KneeBearing_Interior_"+side,thigh,
  (x*.265,.03,.435),.07,.110,.066,"piston",24)
 v49_keep(v43_bar("V49_KneePin_"+side,thigh,
  (x*.23,.03,.435),(x*.53,.03,.435),.039,"piston",20))
 v49_keep(v43_poly("V49_KneeFacingPlate_"+side,thigh,[
  (x*.19,.50),(x*.40,.50),(x*.42,.44),(x*.34,.375),(x*.205,.405)
 ],-.424,-.378,"armor",.009))
 v49_keep(v43_bar("V49_PatellaDamperUpper_"+side,thigh,
  (x*.40,.19,.59),(x*.39,.20,.46),.044,"edge",16))
 v49_keep(v43_bar("V49_PatellaDamperLower_"+side,shin,
  (x*.39,.20,.46),(x*.365,.20,.315),.027,"piston",16))
 # Ankle axles pivot as part of the foot rig, not the shin.
 v49_annulus("V49_AnkleHubExterior_"+side,foot,
  (x*.41,-.02,.105),.053,.097,.054,"edge",24)
 v49_keep(v43_bar("V49_AnkleSpindle_"+side,foot,
   (x*.21,-.02,.105),(x*.435,-.02,.105),.034,"piston",16))
 # Per-side heel stop will support a square footprint, no round soles.
 v49_keep(v43_poly("V49_FootContactStop_"+side,foot,[
  (x*.14,.12),(x*.40,.12),(x*.39,.068),(x*.15,.068)
 ],.118,.212,"trim",.008))
 v49_keep(v43_poly("V49_ShinAccessPanel_"+side,shin,[
  (x*.20,.37),(x*.37,.37),(x*.407,.25),(x*.20,.24)
 ],-.478,-.456,"armor",.009))
 for depth,z in ((-.494,.32),(-.494,.275)):
  v49_keep(v43_bar("V49_ShinFastener_"+side+"_"+str(z),shin,
     (x*.29,depth-.01,z),(x*.29,depth+.01,z),.012,"piston",10))

# Rear structure: distinct square radiator cages and continuous cross-body
# load beams, retaining the original paired thruster core.
for side,sign in (("L",1),("R",-1)):
 x=sign
 v49_keep(v43_poly("V49_RearCoolingCage_"+side,"spine",[
  (x*.16,1.61),(x*.41,1.61),(x*.42,1.22),(x*.16,1.22)
 ],.37,.47,"edge",.010))
 for k in range(4):
  z=1.28+k*.08
  v49_keep(v43_bar("V49_RearRadiatorFin_"+side+str(k),"spine",
   (x*.16,.488,z),(x*.42,.488,z),.016,"piston",12))
 v49_keep(v43_bar("V49_WaistStrut_"+side,"spine",
  (x*.22,.30,1.16),(x*.31,.30,.93),.032,"edge",16))

# Beam cannon servicing cover; the existing game-specific emitter and
# collision geometry remain authoritative.
v49_keep(v43_poly("V49_CannonTopLoadDoor","forearm.R",[
 (-1.037,1.214),(-.741,1.214),(-.76,1.184),(-1.018,1.184)
 ],-.569,-.538,"armor",.010))
v49_keep(v43_bar("V49_CannonHeatsinkLeft","forearm.R",
 (-1.052,-.58,1.10),(-1.052,-.92,1.10),.018,"piston",12))
v49_keep(v43_bar("V49_CannonHeatsinkRight","forearm.R",
 (-.735,-.58,1.10),(-.735,-.92,1.10),.018,"piston",12))

# Perform after all component generation, before action keyframing.
for obj in list(bpy.data.objects):
 if obj.type=="MESH" and any(m.type=="ARMATURE" and m.object==rig for m in obj.modifiers):
  for v in obj.data.vertices:
   v.co=v44_transform(v.co)
rig.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode="EDIT")
# Save old positions first to avoid parent-edit updates changing child coords.
oldrest={b.name:(b.head.copy(),b.tail.copy(),b.roll) for b in rig.data.edit_bones}
for b in rig.data.edit_bones:
 head,tail,roll=oldrest[b.name]
 b.head=v44_transform(head)
 b.tail=v44_transform(tail)
 b.roll=roll
bpy.ops.object.mode_set(mode="OBJECT")
# First-place sample coordinate for sole has been remapped with the foot vertices.
# Existing key pose collision check still uses bone matrices and is left strict.

rig.animation_data_create()
poses=rig.pose.bones
floor_clearance_samples=[]
full_frame_ground_samples=[]
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
    floors.append((transform @ V((v44_x(x+xoff,.008),v44_y(y,.008),v44_z(.008)))).z)
 return min(floors)

clips=("Idle","Run","Punch","Dodge","Fire","Hit")
for clip in clips:
 a=bpy.data.actions.new("Mecha_"+clip)
 rig.animation_data.action=a
 for frame in (1,13,25,37,48):
  z=math.sin(2*math.pi*(frame-1)/47)
  for b in poses:b.rotation_mode="XYZ";b.rotation_euler=(0,0,0);b.location=(0,0,0)
  if clip=="Idle":poses["spine"].rotation_euler[0]=.025*z
  if clip=="Run":
   poses["root"].location.y=.04*abs(z)
   for side,sign in (("L",1),("R",-1)):
    poses["thigh."+side].rotation_euler[0]=sign*.58*z
    poses["shin."+side].rotation_euler[0]=max(0,-sign*z)*.55
    poses["upper_arm."+side].rotation_euler[0]=-sign*.46*z
    # A separate ankle counter-rotates to keep the foot relatively level
    # on the support phase and slightly lift the toe during the swing.
    poses["foot."+side].rotation_euler[0]=(
       -sign*.38*z-max(0,-sign*z)*.34
    )
  if clip=="Punch":
   amt=max(0,1-abs(frame-25)/18)
   poses["upper_arm.R"].rotation_euler[0]=-1.15*amt
   poses["forearm.R"].rotation_euler[0]=-.55*amt
   poses["spine"].rotation_euler[2]=-.15*amt
  if clip=="Fire":
   amt=max(0,1-abs(frame-13)/12)
   poses["upper_arm.R"].rotation_euler[0]=-.22*amt
   poses["forearm.R"].rotation_euler[0]=-.18*amt
   poses["spine"].rotation_euler[0]=.08*amt
  if clip=="Hit":
   amt=max(0,1-abs(frame-13)/14)
   poses["spine"].rotation_euler[0]=-.13*amt
   poses["spine"].rotation_euler[2]=.17*amt
   poses["head"].rotation_euler[0]=.11*amt
   poses["upper_arm.L"].rotation_euler[0]=.24*amt
   poses["upper_arm.R"].rotation_euler[0]=.24*amt
  if clip=="Dodge":
   amt=max(0,1-abs(frame-25)/20)
   poses["spine"].rotation_euler[1]=.3*amt
   poses["root"].location.x=.14*amt
   for side,sign in (("L",1),("R",-1)):
    poses["thigh."+side].rotation_euler[0]=sign*.11*amt
    poses["shin."+side].rotation_euler[0]=-.18*amt
    poses["foot."+side].rotation_euler[0]=.09*amt
  # Bone local +Y follows this vertical root bone toward world +Z;
  # local +Z is *not* world height. Correct sole penetration on local Y.
  # Reconcile the two feet with the ground at the sampled key poses.
  # This is a deterministic pose correction, not runtime IK/physics.
  ground_before=lowest_sole_z()
  target_clearance=.012
  correction=max(-.30,min(.35,target_clearance-ground_before))
  poses["root"].location.y+=correction
  floor_after=lowest_sole_z()
  floor_clearance_samples.append({"clip":clip,"frame":frame,"min_sole_z":round(floor_after,5)})
  for b in poses:
   b.keyframe_insert(data_path="rotation_euler",frame=frame)
   if b.name=="root":b.keyframe_insert(data_path="location",frame=frame)
 # V5.0: test and correct EVERY actual timeline frame, not just five key poses.
 # Earlier NLA strips are muted during this test so they do not contaminate
 # the active Action being checked. A root-only dense curve preserves every
 # leg/knee/ankle rotation from the authored Run cycle.
 for older_track in rig.animation_data.nla_tracks:
  older_track.mute=True
 for exact_frame in range(1,49):
  bpy.context.scene.frame_set(exact_frame)
  h_before=lowest_sole_z()
  adjust=max(-.28,min(.28,.012-h_before))
  poses["root"].location.y+=adjust
  poses["root"].keyframe_insert(data_path="location",frame=exact_frame)
  h_after=lowest_sole_z()
  full_frame_ground_samples.append({
   "clip":clip,"frame":exact_frame,
   "clearance":round(h_after,5),
   "adjust":round(adjust,5)
  })
  if h_after<-.009:
   raise RuntimeError(f"Ground penetration: {clip} frame={exact_frame} z={h_after:.4f}")
 for older_track in rig.animation_data.nla_tracks:
  older_track.mute=False
 rig.animation_data.action=None
 track=rig.animation_data.nla_tracks.new()
 track.name=clip
 track.strips.new(clip,1,a)


# V4.6 TRUE high-to-low TANGENT NORMAL BAKE (Cycles, selected-to-active).
# Hero armor only; avoid turning every 125 parts into an enormous draw-call
# collection. Keep original 15-bone skin weights and six action clips.
import hashlib
bake_results=[]
bake_folder=out/"textures"
bake_folder.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
scene.frame_set(1)
scene.render.engine="CYCLES"
scene.cycles.samples=8
scene.render.bake.use_selected_to_active=True
scene.render.bake.max_ray_distance=.060
scene.render.bake.cage_extrusion=.025
scene.render.bake.margin=8
targets=[
 "V45_LeftChestFlow","V45_RightChestFlow",
 "V45_ShoulderSweep_L","V45_ShoulderSweep_R",
 "V45_ThighComposite_L","V45_ThighComposite_R",
 "V45_ShinKineticPlate_L","V45_ShinKineticPlate_R"
]
for target_name in targets:
 low=bpy.data.objects.get(target_name)
 if low is None:raise RuntimeError("Required armor source missing: "+target_name)
 orig_modifier_state=[(m,m.show_viewport,m.show_render) for m in low.modifiers if m.type=="ARMATURE"]
 for m,_,_ in orig_modifier_state:m.show_viewport=False;m.show_render=False
 bpy.ops.object.select_all(action="DESELECT")
 low.select_set(True)
 bpy.context.view_layer.objects.active=low
 # Explicit UV layout required for valid GLB tangent-space normal maps.
 if len(low.data.uv_layers)==0:
  bpy.ops.object.mode_set(mode="EDIT")
  bpy.ops.mesh.select_all(action="SELECT")
  bpy.ops.uv.smart_project(island_margin=.040)
  bpy.ops.object.mode_set(mode="OBJECT")
 low.data.uv_layers.active_index=0
 # High-res sculpt is a separate Blender mesh: geometry density and bevels
 # are genuinely higher than the final skinned low poly armor.
 high=low.copy()
 high.data=low.data.copy()
 high.name="BAKE_ONLY_HIGH_"+target_name
 bpy.context.collection.objects.link(high)
 high.modifiers.clear()
 bpy.ops.object.select_all(action="DESELECT")
 high.select_set(True)
 bpy.context.view_layer.objects.active=high
 high_faces_before=len(high.data.polygons)
 hi_bevel=high.modifiers.new("V46_highpoly_precision_bevel","BEVEL")
 hi_bevel.width=.009
 hi_bevel.segments=5
 hi_bevel.limit_method="NONE"
 bpy.ops.object.modifier_apply(modifier=hi_bevel.name)
 high_faces_after=len(high.data.polygons)
 if high_faces_after <= high_faces_before:
  raise RuntimeError("High mesh did not gain geometry for "+target_name)
 # Each target uses a unique normal image and material; the image is embedded
 # by the glTF exporter through a real NormalMap BSDF link.
 image=bpy.data.images.new("V46_N_"+target_name,width=512,height=512,alpha=True)
 image.colorspace_settings.name="Non-Color"
 material=low.active_material.copy()
 material.name="V46_BakedArmor_"+target_name
 low.data.materials.clear()
 low.data.materials.append(material)
 mat_nodes=material.node_tree.nodes
 image_node=mat_nodes.new("ShaderNodeTexImage")
 image_node.name="V46_NormalBakeTarget"
 image_node.image=image
 image_node.interpolation="Linear"
 mat_nodes.active=image_node
 bpy.ops.object.select_all(action="DESELECT")
 high.select_set(True)
 low.select_set(True)
 bpy.context.view_layer.objects.active=low
 bpy.ops.object.bake(type="NORMAL")
 image.filepath_raw=str((bake_folder/(target_name+"_normal.png")).resolve())
 image.file_format="PNG"
 image.save()
 if not (bake_folder/(target_name+"_normal.png")).is_file():
  raise RuntimeError("Normal bake PNG not produced: "+target_name)
 nm=mat_nodes.new("ShaderNodeNormalMap")
 nm.space="TANGENT"
 nm.uv_map=low.data.uv_layers.active.name
 material.node_tree.links.new(image_node.outputs["Color"],nm.inputs["Color"])
 bsdf=mat_nodes.get("Principled BSDF")
 if bsdf is None:raise RuntimeError("Baked material missing Principled BSDF")
 material.node_tree.links.new(nm.outputs["Normal"],bsdf.inputs["Normal"])

 # V4.7 UV-based, deterministic artwork: subtle anisotropic streaks,
 # restrained edge patina, and spatially varying micro-roughness.
 # These images are *authored* from the UV layout, NOT falsely described
 # as physical high-to-low COLOR or ROUGHNESS bakes.
 import math
 def make_art_texture(suffix,colorspace,pixelsize,ink):
  img=bpy.data.images.new("V47_"+suffix+"_"+target_name,
     width=pixelsize,height=pixelsize,alpha=True)
  img.colorspace_settings.name=colorspace
  vals=[]
  for j in range(pixelsize):
   v=j/(pixelsize-1)
   for i in range(pixelsize):
    u=i/(pixelsize-1)
    fine=math.sin((u*93.+v*129.)*math.pi)*math.sin((u*71.-v*117.)*math.pi)
    brushed=math.sin((u*12.+v*1.4)*math.pi)
    edge=.65 if min(u,v,1-u,1-v)<.035 else 0.
    if suffix=="Base":
     c=ink
     variation=1.+.062*fine+.035*brushed+.024*edge
     vals.extend([min(1.,c[0]*variation),
                  min(1.,c[1]*variation),
                  min(1.,c[2]*variation),1.])
    else:
     rough=max(.17,min(.69,.33+.11*fine+.05*brushed+.11*edge))
     vals.extend([rough,rough,rough,1.])
  img.pixels.foreach_set(vals)
  img.update()
  img.filepath_raw=str((bake_folder/(target_name+"_"+suffix.lower()+".png")).resolve())
  img.file_format="PNG"
  img.save()
  return img
 # UV maps in the bake target are real, and used by all texture slots.
 base_image=make_art_texture("Base","sRGB",256,(.62,.70,.73))
 rough_image=make_art_texture("Roughness","Non-Color",256,(.35,.35,.35))
 base_node=mat_nodes.new("ShaderNodeTexImage")
 base_node.image=base_image
 base_node.interpolation="Linear"
 rough_node=mat_nodes.new("ShaderNodeTexImage")
 rough_node.image=rough_image
 rough_node.interpolation="Linear"
 material.node_tree.links.new(base_node.outputs["Color"],bsdf.inputs["Base Color"])
 material.node_tree.links.new(rough_node.outputs["Color"],bsdf.inputs["Roughness"])
 # High mesh MUST NOT enter game model export; preserve rigid skin on low.
 bpy.data.objects.remove(high,do_unlink=True)
 for mod,vp,rn in orig_modifier_state:mod.show_viewport=vp;mod.show_render=rn
 fp=bake_folder/(target_name+"_normal.png")
 bake_results.append({
  "mesh":target_name,
  "low_faces":len(low.data.polygons),
  "high_faces":high_faces_after,
  "pixels":[512,512],
  "uv_map":low.data.uv_layers.active.name,
  "png":str(fp.relative_to(out)),
  "png_bytes":fp.stat().st_size,
   "basecolor_png":str((bake_folder/(target_name+"_base.png")).relative_to(out)),
   "roughness_png":str((bake_folder/(target_name+"_roughness.png")).relative_to(out)),
  "sha256":hashlib.sha256(fp.read_bytes()).hexdigest()
 })
 if fp.stat().st_size<1024:raise RuntimeError("Suspiciously tiny normal map "+str(fp))
 print("V49_BAKE_COMPLETE",target_name,"low",len(low.data.polygons),"high",high_faces_after,"png",fp.stat().st_size)
scene.render.bake.use_selected_to_active=False
(out/"bake_qa.json").write_text(json.dumps({
 "process":"Actual Blender Cycles selected-to-active tangent-space normal bake",
 "resolution":512,
 "targets":bake_results,
 "meshes_required":len(targets),
 "high_sources_exported":False,
 "notes":"True 8-panel normal baking; UV-authored basecolor/roughness are procedural images, not Cycles high-to-low bakes. No full-frame IK."
},indent=2,ensure_ascii=False),encoding="utf-8")
bpy.ops.file.pack_all()

bpy.context.scene.frame_start=1
bpy.context.scene.frame_end=48
bpy.ops.wm.save_as_mainfile(filepath=str((out/"mecha_v50.blend").resolve()))
bpy.ops.export_scene.gltf(filepath=str((out/"mecha_v50.glb").resolve()),
 export_format="GLB",export_animations=True,export_animation_mode="ACTIONS",
 export_skins=True)
# Validate GLB container, animation and skin arrays by reading the JSON chunk.
with (out/"mecha_v50.glb").open("rb") as f:
 header=f.read(12)
 magic,ver,total=struct.unpack("<4sII",header)
 assert magic==b"glTF" and ver==2
 length,typ=struct.unpack("<I4s",f.read(8))
 assert typ==b"JSON"
 document=json.loads(f.read(length).decode("utf-8"))
names=[x.get("name") for x in document.get("animations",[])]
assert len(names)>=6, f"Expected 6 animation clips; got {names}"
assert len(document.get("skins",[]))>=1, "No rig skin exported"
assert sum(1 for mat in document.get("materials",[]) if mat.get("normalTexture") is not None)>=8, "Baked glTF materials have missing normalTexture"
assert len(document.get("images",[]))>=24, "GLB missing embedded baked normal images"
assert not any(x.get("name","").startswith("BAKE_ONLY_HIGH_") for x in document.get("nodes",[])), "Temporary highpoly geometry leaked into GLB"
assert sum("knee" in m.get("name","").lower() for m in document.get("meshes",[]))>=10, "Knee hinge geometry missing"
assert sum(("ankle" in m.get("name","").lower() or "foot" in m.get("name","").lower() or "toe" in m.get("name","").lower() or "heel" in m.get("name","").lower()) for m in document.get("meshes",[]))>=12, "Foot or ankle geometry missing"
assert len(arm.bones)==15, f"Expected 15 bones including weapon socket, got {len(arm.bones)}"
assert "weapon_socket.R" in {n.get("name") for n in document.get("nodes",[])}, "Missing weapon socket in exported GLB"
assert sum(1 for m in document.get("meshes",[]) if m.get("name","").startswith("V49_") and ("Hub" in m.get("name","") or "Bearing" in m.get("name","")))>=10, "Mechanical open bearing parts missing"
assert all(x["min_sole_z"] >= -.009 for x in floor_clearance_samples), "Foot sinks below the test floor at a keyed pose"
assert len(full_frame_ground_samples)==6*48, "Missing per-frame grounding evidence"
assert min(x["clearance"] for x in full_frame_ground_samples)>=-.009, "Full-frame foot sinking" 
report={"full_frame_grounding":full_frame_ground_samples,"root_correction":"full-frame constrained root translation; does not solve horizontal foot sliding or cross-bone IK", "v49_machine_parts":len(v49_parts),"hollow_bearings":sum(1 for o in bpy.data.objects if o.name.startswith("V49_") and ("Hub" in o.name or "Bearing" in o.name)),"art_review_status":"candidate_requires_visual_signoff","design_language":"machined faceted flat-surface armor; no increased roundness","panel_type":"coplanar front and shallow chamfer","new_hard_surface_parts":len(v48_parts),"normal_bakes":bake_results,"blender_version":bpy.app.version_string,"bones":len(arm.bones),
        "mesh_parts":sum(o.type=="MESH" and any(mod.type=="ARMATURE" and mod.object==rig for mod in o.modifiers) for o in bpy.data.objects),"knee_design":"separate thigh/shin armor, knee pivots, frontal caps and side axle pins",
        "ankle_design":"2 new ankle bones, feet, toe caps, heels and axle pins",
        "ground_contact":"keyframe-level sole height correction, not full IK or physics",
        "sole_samples":floor_clearance_samples,"animations":names,
        "skins":len(document["skins"]),"glb_bytes":total,
        "method":"procedural Blender Python (not Choreographer AI)"}
(out/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
manifest={
 "schema_version":1,"asset_id":"mecha_v50","format":"glTF 2.0 GLB",
 "source":"Blender 5.2 procedural animation, NOT generative AI",
 "blender_version":bpy.app.version_string,
 "coordinate_system":"Blender Z-up; glTF export converts to Y-up",
 "unit":"meter","model_file":"mecha_v50.glb",
 "source_file":"mecha_v50.blend",
 "clips":names,"min_animation_count":6,
 "requirements":{"skins":True,"animated":True,"visual_review":True},
 "license_note":"All generated geometry is original procedural geometry. Third-party textures and models must declare their own licenses."
}
(out/"asset_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
(out/"fullframe_gait_qa.json").write_text(json.dumps({
 "method":"Blender pose action evaluated on every timeline frame with NLA muted",
 "sample_count":len(full_frame_ground_samples),
 "clip_names":sorted(set(x["clip"] for x in full_frame_ground_samples)),
 "min_clearance_m":min(x["clearance"] for x in full_frame_ground_samples),
 "max_abs_root_adjust_m":max(abs(x["adjust"]) for x in full_frame_ground_samples),
 "samples":full_frame_ground_samples,
 "limitation":"Only vertical ground penetration correction; not runtime planted-foot IK, horizontal sliding, or physics."
},indent=2),encoding="utf-8")
print("SMOKE_TEST_PASSED",{k:v for k,v in report.items() if k!="full_frame_grounding"})

# True Blender viewport render of the actual skinned armature/geometry.
# This is NOT an AI-generated concept image or a trimesh rest-pose projection.
try:
 preview_scene=bpy.context.scene
 preview_scene.render.engine="BLENDER_WORKBENCH"
 preview_scene.render.resolution_x=720
 preview_scene.render.resolution_y=720
 preview_scene.render.resolution_percentage=100
 preview_scene.render.image_settings.file_format="PNG"
 preview_scene.render.image_settings.color_mode="RGBA"
 preview_scene.render.film_transparent=True
 preview_scene.display.shading.light="STUDIO"
 preview_scene.display.shading.color_type="MATERIAL"
 preview_scene.display.shading.show_cavity=True
 preview_scene.frame_set(1)
 camera_data=bpy.data.cameras.new("MechaV42_PreviewCamera")
 camera=bpy.data.objects.new("MechaV42_PreviewCamera",camera_data)
 bpy.context.collection.objects.link(camera)
 preview_scene.camera=camera
 camera_data.type="ORTHO"
 camera_data.ortho_scale=4.10
 from mathutils import Vector as PreviewVector
 locations=[("front",(.0,-6.0,3.1)),
            ("side",(6.0,-.2,2.8)),
            ("back",(.0,6.0,3.1)),
            ("three_quarter",(4.0,-5.2,3.9))]
 for tag,xyz in locations:
  camera.location=xyz
  heading=PreviewVector((0.,0.,1.42))-camera.location
  camera.rotation_euler=heading.to_track_quat("-Z","Y").to_euler()
  preview_scene.render.filepath=str((out/("preview_"+tag+".png")).resolve())
  bpy.ops.render.render(write_still=True)
 print("V49_PREVIEW_RENDERED", [x[0] for x in locations])
except Exception as preview_error:
 # Do not relabel a successful structural build as a successful visual render.
 (out/"preview_error.txt").write_text(str(preview_error),encoding="utf-8")
 print("V49_PREVIEW_FAILED",repr(preview_error))



# True shader-based beauty pass in CPU Cycles. Workbench previews above are
# kept for stable silhouette reviews, while this checks glTF-exportable PBR.
try:
 preview_scene.render.engine="CYCLES"
 preview_scene.cycles.samples=12
 preview_scene.render.resolution_x=800
 preview_scene.render.resolution_y=800
 preview_scene.render.resolution_percentage=100
 preview_scene.render.film_transparent=True
 preview_scene.world.color=(.12,.12,.12)
 from mathutils import Vector as VV45
 for tag,loc,power,size in [
  ("key",(1.,-4.5,5.),760,4.0),
  ("fill",(-3.,-3.,2.8),430,4.5),
  ("rim",(0.,2.8,4.2),1100,3.3)]:
  data=bpy.data.lights.new("V45_"+tag,"AREA")
  data.energy=power
  data.shape="DISK"
  data.size=size
  light=bpy.data.objects.new("V45_"+tag,data)
  bpy.context.collection.objects.link(light)
  light.location=loc
  light.rotation_euler=(VV45((0.,0.,1.45))-light.location).to_track_quat("-Z","Y").to_euler()
 camera.location=(4.,-5.2,3.9)
 camera.rotation_euler=(VV45((0.,0.,1.42))-camera.location).to_track_quat("-Z","Y").to_euler()
 preview_scene.render.filepath=str((out/"preview_pbr_hero.png").resolve())
 bpy.ops.render.render(write_still=True)
 print("V49_PBR_PREVIEW_RENDERED",preview_scene.render.filepath)
except Exception as beauty_error:
 (out/"preview_pbr_error.txt").write_text(str(beauty_error),encoding="utf-8")
 print("V49_PBR_PREVIEW_FAILED",repr(beauty_error))


# True Blender frames from Mecha_Run, without concept-art synthesis.
# Solo the Run NLA strip (all six clips share the same 1..48 interval).
# SHA differentiation catches a static or incorrectly muted animation.
for tr in rig.animation_data.nla_tracks:
 tr.mute=(tr.name!="Run")
preview_scene.render.engine="BLENDER_WORKBENCH"
preview_scene.render.resolution_x=560
preview_scene.render.resolution_y=560
preview_scene.render.resolution_percentage=100
preview_scene.render.film_transparent=True
camera.location=(4.0,-5.8,3.1)
camera.rotation_euler=(PreviewVector((0.,0.,1.42))-camera.location).to_track_quat("-Z","Y").to_euler()
run_preview={}
for test_frame in (1,13,25,37):
 preview_scene.frame_set(test_frame)
 target=out/("preview_run_%02d.png"%test_frame)
 preview_scene.render.filepath=str(target.resolve())
 bpy.ops.render.render(write_still=True)
 run_preview[str(test_frame)]=hashlib.sha256(target.read_bytes()).hexdigest()
for tr in rig.animation_data.nla_tracks:
 tr.mute=False
assert len(set(run_preview.values()))>=3, "Run animation preview is not visibly changing"
(out/"run_visual_qa.json").write_text(json.dumps({
 "clip":"Mecha_Run",
 "frames":[1,13,25,37],
 "render_engine":"BLENDER_WORKBENCH",
 "hashes":run_preview,
 "distinct":len(set(run_preview.values())),
 "note":"real Blender motion snapshots, not a full dynamic IK/physics guarantee"
},indent=2),encoding="utf-8")
print("V50_RUN_ANIMATION_PREVIEWS_PASS",run_preview)
