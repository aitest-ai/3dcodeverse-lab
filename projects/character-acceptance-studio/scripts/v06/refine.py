"""Native-bone finger relaxation and deterministic skirt clearance correction; not a cloth simulation."""
import math
from mathutils import Vector,Quaternion
from v05.blender_utils import bone_world,set_q,set_world
FINGER_POSES={name:tuple(a*factor for a in (.45,.65,.33)) for name,factor in [('Idle',.65),('Walk',.66),('Run',.67)]}
CLOTH_EASE_M_PER_RAD=.070

def relaxed_fingers(rig,name,t,duration):
 if name in FINGER_POSES:angles=FINGER_POSES[name]
 elif name in ['Start','Stop']:
  u=t/duration;x=max(0,min(1,u/.25 if name=='Start' else (1-u)/.25));x=x*x*(3-2*x);angles=tuple(a+(b-a)*x for a,b in zip(FINGER_POSES['Idle'],FINGER_POSES['Walk']))
 else:angles=FINGER_POSES['Idle']
 for side in ['L','R']:
  prefix='J_Bip_'+side+'_';rest=lambda key:rig.data.bones[prefix+key].matrix_local
  hand=rest('Hand');along=rest('Middle1').translation-hand.translation;across=rest('Index1').translation-rest('Little1').translation;palm=along.cross(across).normalized()
  if palm.z>0:palm=-palm
  delta=bone_world(rig,prefix+'Hand').to_quaternion()@hand.to_quaternion().inverted()
  for digit,factor in [('Index',.88),('Middle',1),('Ring',1.08),('Little',1.15),('Thumb',.55)]:
   direction=(rest(digit+'2').translation-rest(digit+'1').translation).normalized();axis=delta@direction.cross(palm).normalized()
   for i,angle in enumerate(angles,1):
    n=prefix+digit+str(i);set_q(rig,n,Quaternion(axis,angle*factor)@bone_world(rig,n).to_quaternion())

def skirt_clearance(rig,root,name):
 if name!='Run':return {}
 forward=root.rotation_quaternion@Vector((0,1,0));out={}
 for side in ['L','R']:
  v=bone_world(rig,'J_Bip_'+side+'_LowerLeg').translation-bone_world(rig,'J_Bip_'+side+'_UpperLeg').translation;angle=max(0,math.atan2(v.dot(forward),-v.z));ease=CLOTH_EASE_M_PER_RAD*angle;n='J_Sec_'+side+'_SkirtFront0';m=bone_world(rig,n);m.translation+=forward*ease;set_world(rig,n,m);out[side]=ease
 return out

def turn_heading_twist(rig,root,name):
 """Correct heading-dependent axial twist without moving the existing joint/foot world positions."""
 if name not in ['TurnLeft','TurnRight']:return
 from mathutils import Matrix
 from v05.blender_utils import set_world
 base=Quaternion((0,0,1),math.pi);yaw=root.rotation_quaternion@base.inverted()
 before={p.name:bone_world(rig,p.name).copy() for p in rig.pose.bones};corrected={}
 for side in ['L','R']:
  for part,child in [('UpperArm','LowerArm'),('UpperLeg','LowerLeg'),('LowerLeg','Foot')]:
   n='J_Bip_'+side+'_'+part;c='J_Bip_'+side+'_'+child
   ref=base@(rig.data.bones[c].matrix_local.translation-rig.data.bones[n].matrix_local.translation);direction=before[c].translation-before[n].translation
   original=ref.rotation_difference(direction);heading=(yaw@ref).rotation_difference(direction)@yaw
   q=heading@original.inverted()@before[n].to_quaternion();corrected[n]=Matrix.LocRotScale(before[n].translation,q,before[n].to_scale())
 for p in rig.pose.bones:set_world(rig,p.name,corrected.get(p.name,before[p.name]))

def turn_settle(rig,root,name,t,duration,idle,idle_z):
 """Last 15% returns to the exact native Idle pose in the turned root frame; bounded foot drift is audited."""
 if name not in ['TurnLeft','TurnRight']:return
 x=max(0,min(1,(t/duration-.85)/.15));x=x*x*(3-2*x)
 if not x:return
 import bpy
 from v05.blender_utils import pose_basis,restore_basis
 current=pose_basis(rig);mixed={}
 for n,v in current.items():
  q=Quaternion(v['q']).slerp(Quaternion(idle[n]['q']),x)
  mixed[n]={'p':list(Vector(v['p']).lerp(Vector(idle[n]['p']),x)),'q':list(q),'s':list(Vector(v['s']).lerp(Vector(idle[n]['s']),x))}
 restore_basis(rig,mixed);root.location.z+=(idle_z-root.location.z)*x;bpy.context.view_layer.update()
