"""Native fixed-length foot planner; Blender XYZ, explicit display calibration."""
import math,bpy
from mathutils import Vector,Matrix
from v05.blender_utils import bone_world,set_world,vertices
from v10.horse_solver import solve_two_link

def plan_foot(t,T,p,v):
 phase=t/T-p['phase'];cycle=math.floor(phase+1e-10);u=phase-cycle;d=p['duty'];s=max(0,min(1,(u-d)/(1-d)));w=10*s**3-15*s**4+6*s**5
 return {'cycle':cycle,'stance':u<=d,'phase':u,'x':p['source_stance_mean_m'][0],'y':p['source_stance_mean_m'][1]+v*T*(u-d/2-w),'sole':.003+p['source_max_lift_m']*math.sin(math.pi*s)**2,'rotation_blend':math.sin(math.pi*s)**2}

def fix_feet(rig,body,paws,calibration,plan,t,idle):
 scale=calibration['scale'];offset=calibration['offset_y'];T=plan['duration_s'];v=plan['candidate_speed_m_s']
 # A small explicit body-pose adaptation creates reach margin without stretching links.
 for pb in rig.pose.bones:
  if pb.parent is None:
   m=bone_world(rig,pb.name).copy();m.translation.z-=plan['body_lowering_m']/scale;set_world(rig,pb.name,m)
 source={b.name:bone_world(rig,b.name).copy() for b in rig.pose.bones};rows={}
 for key,defs in paws.items():
  side=key[-1];front=key.startswith('Front');lower=('FrontLowerLeg.' if front else 'BackLowerLeg.')+side;upper=lower.replace('Lower','Upper');ik=('IKFrontLeg.' if front else 'IKBackLeg.')+side;ff=('FF.' if front else 'FFB.')+side
  p=plan_foot(t,T,plan['feet'][key],v);w=p['rotation_blend'];origin=source[ik].translation.copy()
  for name in [ik,ff]:
   rel=(idle[name].translation-idle[ik].translation).lerp(source[name].translation-source[ik].translation,w);rot=idle[name].to_quaternion().slerp(source[name].to_quaternion(),w);set_world(rig,name,Matrix.LocRotScale(origin+rel,rot,source[name].to_scale()))
  points=vertices(body);center=sum((points[i] for i in defs['flat']),Vector())/len(defs['flat']);low=min(points[i].z for i in defs['ids']);delta=Vector((p['x']/scale-center.x,p['y']/scale-center.y,(p['sole']-offset)/scale-low))
  foot_matrices={name:bone_world(rig,name).copy() for name in [ik,ff]}
  for name in [ik,ff]:
   m=foot_matrices[name];m.translation+=delta;set_world(rig,name,m)
  end=lambda frames:frames[lower]@Vector((0,rig.data.bones[lower].length,0))-frames[ik].translation
  target=origin+end(idle).lerp(end(source),w)+delta
  try:sol=solve_two_link(rig,upper,lower,source,target)
  except RuntimeError as e:
   a=source[upper].translation;b=source[lower].translation;c=source[lower]@Vector((0,rig.data.bones[lower].length,0));raise RuntimeError(f'{key} t={t:.6f}, phase={p["phase"]:.4f} reach={(target-a).length:.6f} max={(b-a).length+(c-b).length:.6f} target={list(target)} old={list(c)} delta={list(delta)}: {e}') from e
  rows[key]={**p,**sol,'correction_m':list(delta*scale)}
 after=vertices(body)
 for key,defs in paws.items():
  rows[key]['minimum_sole_y_m']=min(after[i].z for i in defs['ids'])*scale+offset
  rows[key]['reference_m']=[sum(after[i][j] for i in defs['flat'])/len(defs['flat'])*scale+(offset if j==2 else 0) for j in range(3)]
 return rows
