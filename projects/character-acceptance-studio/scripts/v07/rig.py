"""World-space, native-length leg IK and measured shoe contacts. No cross-rig local quaternion copy."""
import math,statistics,bpy
from mathutils import Vector,Quaternion,Matrix
from v05.blender_utils import bone_world,set_world,set_q,vertices
from gait_plan_v02 import rot

def bn(side,part):return 'J_Bip_'+side.upper()+'_'+part
class Legs:
 def __init__(self,rig,body,root,ids,sets,flat):
  self.rig,self.body,self.root=rig,body,root;self.ids,self.sets,self.flat=ids,sets,{s:Quaternion(q) for s,q in flat.items()};v=vertices(body)
  self.offsets={s:{k:self.mean(v,sets[s][k])-self.mean(v,sets[s]['flat']) for k in ['heel','toe']} for s in ids}
  self.ankles={s:bone_world(rig,bn(s,'Foot')).translation.z-min(v[i].z for i in ids[s])+.003 for s in ids}
  self.lengths={s:[(rig.data.bones[bn(s,a)].head_local-rig.data.bones[bn(s,b)].head_local).length for a,b in [('UpperLeg','LowerLeg'),('LowerLeg','Foot')]] for s in ids};self.leg=statistics.mean(sum(x) for x in self.lengths.values())
 @staticmethod
 def mean(v,ids):return sum((v[i] for i in ids),Vector())/len(ids)
 def solve(self,s,target,q,heading):
  rig=self.rig;n=[bn(s,k) for k in ['UpperLeg','LowerLeg','Foot']];H,K,A=[bone_world(rig,b).translation.copy() for b in n];Q=[bone_world(rig,b).to_quaternion() for b in n[:2]];l1,l2=self.lengths[s];v=target-H;dist=min(max(v.length,.0001),l1+l2-.00001);u=v.normalized();a=(l1*l1-l2*l2+dist*dist)/(2*dist);pole=Vector(rot((.04 if s=='l' else -.04,-1,0),heading));bend=pole-u*pole.dot(u);nk=H+u*a+bend.normalized()*math.sqrt(max(0,l1*l1-a*a));na=H+u*dist
  set_q(rig,n[0],(K-H).rotation_difference(nk-H)@Q[0]);set_q(rig,n[1],(A-K).rotation_difference(na-nk)@Q[1]);set_world(rig,n[2],Matrix.LocRotScale(na,q,Vector((1,1,1))));return (na-target).length
 def correct(self,plan,iterations=10):
  error=residual=0
  for s,f in plan['feet'].items():set_q(self.rig,bn(s,'Foot'),Quaternion((0,0,1),f['yaw'])@Quaternion((1,0,0),f['pitch'])@self.flat[s])
  for _ in range(iterations):
   error=0;v=vertices(self.body)
   for s,f in plan['feet'].items():
    pivot=f['pivot'] if f['contact'] else 'flat';ref=self.mean(v,self.sets[s][pivot]);q=Quaternion((0,0,1),f['yaw']);wanted=Vector(f['P'])
    if f['contact']:wanted+=q@self.offsets[s].get(pivot,Vector())
    else:
     off=self.offsets[s]['toe'].lerp(self.offsets[s]['heel'],f['pivot_blend']);wanted+=q@(off-Quaternion((1,0,0),f['pitch'])@off)
    diff=Vector((wanted.x-ref.x,wanted.y-ref.y,.003+f['clearance']-min(v[i].z for i in self.ids[s])));error=max(error,diff.length);residual=max(residual,self.solve(s,bone_world(self.rig,bn(s,'Foot')).translation+diff,q@Quaternion((1,0,0),f['pitch'])@self.flat[s],plan['yaw']))
   if error<.000015:break
  return {'final_contact_target_error_m':error,'maximum_ik_reach_residual_m':residual}
 def pelvis(self,phase,midstance=.16,center=.94,amplitude=.01):
  ratio=center-amplitude*math.cos(4*math.pi*(phase-midstance));current=statistics.mean(bone_world(self.rig,bn(s,'UpperLeg')).translation.z for s in self.ids);target=statistics.mean(self.ankles.values())+self.leg*ratio;self.root.location.z+=target-current;bpy.context.view_layer.update();return ratio
 def audit(self,plan):
  v=vertices(self.body);feet={};knees={}
  for s,f in plan['feet'].items():
   ids=self.sets[s][f['pivot'] if f['contact'] else 'flat'];feet[s]={**f,'reference_m':list(self.mean(v,ids)),'minimum_z_m':min(v[i].z for i in self.ids[s])};H,K,A=[bone_world(self.rig,bn(s,p)).translation for p in ['UpperLeg','LowerLeg','Foot']];knees[s]=180-math.degrees((H-K).angle(A-K))
  hips=bone_world(self.rig,'J_Bip_C_Hips').translation;neck=bone_world(self.rig,'J_Bip_C_Neck').translation;forward=Quaternion((0,0,1),plan['yaw'])@Vector((0,-1,0));v=neck-hips
  return {'feet':feet,'knee_flexion_degrees':knees,'hips_height_m':hips.z,'torso_lean_degrees':math.degrees(math.atan2(v.dot(forward),v.z))}

def skirt(rig,rest,plan,ease=.07):
 yaw=Quaternion((0,0,1),plan['yaw']);hip=bone_world(rig,'J_Bip_C_Hips');delta=hip@rest['J_Bip_C_Hips'].inverted()
 for s in ['l','r']:
  v=yaw.inverted()@(bone_world(rig,bn(s,'LowerLeg')).translation-bone_world(rig,bn(s,'UpperLeg')).translation);pitch=math.atan2(v.y,-v.z)
  for part in ['Front','Back','Side']:
   n='J_Sec_'+s.upper()+'_Skirt'+part+'0'
   if n not in rig.pose.bones:continue
   # Reset the entire native chain before solving; the input can already contain a baked skirt pose.
   for p in rig.pose.bones:
    if p.name.startswith(n[:-1]):set_world(rig,p.name,delta@rest[p.name])
   m=delta@rest[n]
   if part=='Front':m.translation+=(yaw@Vector((0,-1,0)))*ease*max(0,-pitch)
   set_world(rig,n,m);n1=n[:-1]+'1'
   if n1 not in rig.pose.bones:continue
   q=bone_world(rig,n1).to_quaternion();angle=min(0,pitch)*1.25 if part=='Front' else max(0,pitch)*1.10 if part=='Back' else (-.08 if s=='l' else .08);axis=yaw@Vector((0,1,0) if part=='Side' else (1,0,0));set_q(rig,n1,Quaternion(axis,angle)@q)
