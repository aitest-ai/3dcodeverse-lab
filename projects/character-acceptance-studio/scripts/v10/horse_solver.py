"""Native-horse cyclic pose bridge and length-preserving two-link correction.
No biped transfer, added deform bones, root lift, or guessed forward velocity.
"""
import math
import bpy
from mathutils import Vector,Quaternion,Matrix
from v05.blender_utils import pose_basis,restore_basis,bone_world,set_world,vertices

def sample_native(rig,action,t):
 rig.animation_data.action=action
 if action.slots:rig.animation_data.action_slot=action.slots[0]
 f=t*24;bpy.context.scene.frame_set(int(f),subframe=f%1)
 return pose_basis(rig)

def align(q,reference):return [-v for v in q] if sum(a*b for a,b in zip(q,reference))<0 else list(q)
def hermite(a,b,da,db,u,length):
 return [(2*u**3-3*u*u+1)*x+(u**3-2*u*u+u)*length*dx+(-2*u**3+3*u*u)*y+(u**3-u*u)*length*dy for x,y,dx,dy in zip(a,b,da,db)]
class CyclicNative:
 def __init__(self,rig,action):
  self.rig,self.action=rig,action;self.duration=float(action.frame_range[1])/24;self.window=self.duration*.12;self.step=1/2400
  self.bridge={}
  a,b=self.duration-self.window,self.window;dt=self.step
  samples=[sample_native(rig,action,t) for t in [a-dt,a,a+dt,b-dt,b,b+dt]]
  for name in samples[0]:
   out={}
   for prop in ['p','q','s']:
    vals=[s[name][prop] for s in samples]
    if prop=='q':vals=[align(v,vals[1]) for v in vals]
    out[prop]=(vals[1],vals[4],[(c-d)/(2*dt) for c,d in zip(vals[2],vals[0])],[(c-d)/(2*dt) for c,d in zip(vals[5],vals[3])])
   self.bridge[name]=out
 def pose(self,t):
  D,w=self.duration,self.window
  if w<t<D-w:return sample_native(self.rig,self.action,t)
  u=((t-D) if t>D-w else t)+w;u/=2*w
  out={}
  for name,props in self.bridge.items():
   out[name]={k:hermite(*args,u,2*w) for k,args in props.items()};out[name]['q']=list(Quaternion(out[name]['q']).normalized())
  return out

def solve_two_link(rig,upper,lower,source,target):
 """Keep original bend half-plane and instantaneous link lengths, including baked source offsets."""
 U,L=source[upper],source[lower];a=U.translation;b=L.translation;c=L@Vector((0,rig.data.bones[lower].length,0));l1=(b-a).length;l2=(c-b).length;line=target-a;dist=line.length
 if not abs(l1-l2)+1e-6<dist<l1+l2-1e-6:raise RuntimeError('Unreachable native leg correction: '+lower)
 axis=line.normalized();old_axis=(c-a).normalized();bend=(b-a)-old_axis*(b-a).dot(old_axis);bend-=axis*bend.dot(axis)
 if bend.length<1e-7:raise RuntimeError('Degenerate native bend plane: '+lower)
 bend.normalize();along=(l1*l1-l2*l2+dist*dist)/(2*dist);height=math.sqrt(max(0,l1*l1-along*along));joint=a+axis*along+bend*height
 urot=(b-a).rotation_difference(joint-a)@U.to_quaternion();lrot=(c-b).rotation_difference(target-joint)@L.to_quaternion()
 set_world(rig,upper,Matrix.LocRotScale(a,urot,U.to_scale()));set_world(rig,lower,Matrix.LocRotScale(joint,lrot,L.to_scale()))
 return {'link_length_error_native':max(abs((joint-a).length-l1),abs((target-joint).length-l2)),'bend_dot':height,'endpoint_error_native':((rig.matrix_world@rig.pose.bones[lower].tail)-target).length}

def correct_ground(rig,body,paws,scale,offset):
 source={p.name:bone_world(rig,p.name).copy() for p in rig.pose.bones};before=vertices(body);rows={}
 for key,p in paws.items():
  lower=('FrontLowerLeg.' if key.startswith('Front') else 'BackLowerLeg.')+key[-1];upper=lower.replace('Lower','Upper');ik=('IKFrontLeg.' if key.startswith('Front') else 'IKBackLeg.')+key[-1];ff=('FF.' if key.startswith('Front') else 'FFB.')+key[-1]
  low=min(before[i].z for i in p['ids'])*scale+offset;target=.002;eps=.004;x=low-target;delta=0 if x>=eps else -x if x<=-eps else (eps-x)**2/(4*eps);dz=delta/scale;sol=None
  if delta>1e-9:
   # Foot controls are independent native deform bones; translate both without changing orientation.
   for n in [ik,ff]:
    m=source[n].copy();m.translation.z+=dz;set_world(rig,n,m)
   end=source[lower]@Vector((0,rig.data.bones[lower].length,0));end.z+=dz;sol=solve_two_link(rig,upper,lower,source,end)
  rows[key]={'source_sole_y_m':low,'requested_lift_m':delta,'solver':sol}
 after=vertices(body)
 for key,p in paws.items():
  rows[key]['minimum_sole_y_m']=min(after[i].z for i in p['ids'])*scale+offset
  rows[key]['reference_m']=[sum(after[i][j] for i in p['flat'])/len(p['flat'])*scale+(offset if j==2 else 0) for j in range(3)]
 return rows

def bake_native_actions(rig,clips):
 """Replace only Walk/Gallop, preserving eleven native editable actions and native 24 fps timebase."""
 rig.animation_data_clear();rig.animation_data_create()
 for name,rows in clips.items():
  old=bpy.data.actions.get(name)
  if old:bpy.data.actions.remove(old)
  a=bpy.data.actions.new(name);a.use_fake_user=True;rig.animation_data.action=a
  for row in rows:
   restore_basis(rig,row['pose'])
   for p in rig.pose.bones:
    for prop in ['location','rotation_quaternion','scale']:p.keyframe_insert(data_path=prop,frame=row['time']*24,group=p.name)
  for layer in a.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      for point in fc.keyframe_points:point.interpolation='LINEAR'
 rig.animation_data.action=bpy.data.actions['Idle']
 if rig.animation_data.action.slots:rig.animation_data.action_slot=rig.animation_data.action.slots[0]
 bpy.context.scene.render.fps=24;bpy.context.scene.frame_set(0)
