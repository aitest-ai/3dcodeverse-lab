"""Vita native-rig body adaptation. Adapted from build_vivi_v05.py at d58ec884; no Vivi local tracks copied. Blender background; raw VRM geometry/materials retained by overlay."""
import bpy,math,json,os,sys,hashlib,statistics
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import *
from v05.overlay import Overlay
from gait_plan_v02 import Planner,rot,smooth
FPS=60;GROUND=.003
source=R/'assets/harbor-courier-review/0.3.0/harbor-courier-review.blend';original=R/'library-v04/vroid-vita/1.0.0/model.glb';mother=R/'library-v04/vroid-vita/1.0.0/model.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));sc=bpy.context.scene;srig=next(o for o in bpy.data.objects if o.type=='ARMATURE');source_rest={p.name:p.bone.matrix_local.to_quaternion().copy() for p in srig.pose.bones};native={}
for tr in srig.animation_data.nla_tracks:tr.mute=True
for name in ['Idle','Walk','Run','Start','Stop','TurnLeft','TurnRight']:
 a=bpy.data.actions[name];srig.animation_data.action=a
 if a.slots:srig.animation_data.action_slot=a.slots[0]
 count=round(a.frame_range[1]);native[name]=[]
 for i in range(count+1):
  sc.frame_set(i);native[name].append({p.name:{'q':list(p.matrix.to_quaternion()),'p':list(p.matrix.translation)} for p in srig.pose.bones})
bpy.ops.wm.open_mainfile(filepath=str(mother));sc=bpy.context.scene;rig=bpy.data.objects['Armature'];body=bpy.data.objects['Body'];weight_sync={o:sync_runtime_weights(bpy.data.objects[o],rig,original,i,identity=True) for o,i in [('Face',0),('Body',1),('Hair001',2)]};root=bpy.data.objects.new('StudioRootMotion_v05',None);sc.collection.objects.link(root);rig.parent=root;root.rotation_mode='QUATERNION';root.rotation_quaternion=Quaternion((0,0,1),math.pi);bpy.context.view_layer.update();capture=Capture(rig,original)
rest_basis=pose_basis(rig);rest_world={p.name:bone_world(rig,p.name).copy() for p in rig.pose.bones};names=list(rig.pose.bones.keys());sidekey={'l':'L','r':'R'}
def bn(s,k):return 'J_Bip_'+sidekey[s]+'_'+k
world=lambda n:bone_world(rig,n)
qw=lambda n:world(n).to_quaternion()
# Identify complete original shoe material, retaining native topology/weights and original vertex IDs.
shoeids=set(i for f in body.data.polygons if 'Shoes' in body.data.materials[f.material_index].name for i in f.vertices)
raw=vertices(body);footids={s:[i for i in shoeids if raw[i].x*(1 if s=='l' else -1)>0] for s in ['l','r']};sets={};offsets={};flat={};ankles={}
for s in ['l','r']:
 raw=vertices(body);ys=sorted(raw[i].y for i in footids[s]);regions={'heel':[i for i in footids[s] if raw[i].y>=ys[len(ys)*3//4]],'toe':[i for i in footids[s] if raw[i].y<=ys[len(ys)//4]]};q=qw(bn(s,'Foot'))
 for _ in range(3):
  set_q(rig,bn(s,'Foot'),q);v=vertices(body);h=min(v[i].z for i in regions['heel']);f=min(v[i].z for i in regions['toe']);dy=statistics.mean(v[i].y for i in regions['heel'])-statistics.mean(v[i].y for i in regions['toe']);q=Quaternion((1,0,0),math.atan2(f-h,dy))@q
 set_q(rig,bn(s,'Foot'),q);flat[s]=q.copy();v=vertices(body);low=min(v[i].z for i in footids[s]);sets[s]={'flat':[i for i in footids[s] if v[i].z<low+.003]}
 for k,ids in regions.items():lo=min(v[i].z for i in ids);sets[s][k]=[i for i in ids if v[i].z<lo+.003]
 mean={k:sum((v[i] for i in ids),Vector())/len(ids) for k,ids in sets[s].items()};offsets[s]={k:mean[k]-mean['flat'] for k in ['heel','toe']};ankles[s]=world(bn(s,'Foot')).translation.z-low+GROUND
leg=sum((world(bn('l',a)).translation-world(bn('l',b)).translation).length for a,b in [('UpperLeg','LowerLeg'),('LowerLeg','Foot')]);width=statistics.mean(abs(statistics.mean(vertices(body)[i].x for i in sets[s]['flat'])) for s in ['l','r'])
planner=Planner(leg,width,1.3333333333333333,.7);planner.strides={'Walk':leg*.95,'Run':leg*1.65};planner.duration={n:(len(f)-1)/FPS for n,f in native.items()};planner.duration['Run']=.7
bodymap={'J_Bip_C_Hips':'pelvis','J_Bip_C_Spine':'spine_01','J_Bip_C_Chest':'spine_02','J_Bip_C_UpperChest':'spine_03','J_Bip_C_Neck':'neck_01','J_Bip_C_Head':'Head'}
if 'Head' not in source_rest:bodymap['J_Bip_C_Head']='head'

def base(name,t,plan):
 restore_basis(rig,rest_basis);root.location=plan['root'];root.rotation_quaternion=Quaternion((0,0,1),math.pi+plan['yaw']);root.scale=(1,1,1);bpy.context.view_layer.update();yaw=Quaternion((0,0,1),plan['yaw']);f=native[name][min(len(native[name])-1,round(plan['phase']*(len(native[name])-1)) if name=='Run' else round(t*FPS))]
 for target,s in bodymap.items():
  delta=Quaternion(f[s]['q'])@source_rest[s].inverted();q=yaw@delta@rest_world[target].to_quaternion();set_q(rig,target,q)
 # Source upper-body poses are adapted in world rest frames; actual target pelvis-neck lean is bounded.
 forward=yaw@Vector((0,-1,0));axis=yaw@Vector((1,0,0))
 for _ in range(8):
  v=world('J_Bip_C_Neck').translation-world('J_Bip_C_Hips').translation;lean=math.atan2(v.dot(forward),v.z);limit=math.radians(8 if name=='Run' else 5);delta=max(0,lean-limit)
  if delta<.00005:break
  set_q(rig,'J_Bip_C_Spine',Quaternion(axis,-delta*1.2)@qw('J_Bip_C_Spine'))
 # Matched gait phase keeps arm/leg opposition; moderate source-derived style instead of T-pose channel copying.
 moving=1 if name in ['Walk','Run'] else plan['walk_blend'] if name in ['Start','Stop'] else 0
 for s in ['l','r']:
  sign=1 if s=='l' else -1;wave=math.cos(math.tau*plan['phase'])*sign;u=Vector((sign*.12,(.37 if name=='Run' else .22)*wave*moving+.018*math.sin(math.tau*plan['phase'])*(1-moving),-1)).normalized();flex=(1.10 if name=='Run' else .32)*moving+.16*(1-moving);low=Quaternion((1,0,0),-flex)@u
  for a,b,direction in [('UpperArm','LowerArm',u),('LowerArm','Hand',low)]:
   n,c=bn(s,a),bn(s,b);ref=rest_world[c].translation-rest_world[n].translation;q=ref.rotation_difference(yaw@direction)@rest_world[n].to_quaternion();set_q(rig,n,q)
  # Native palm plane from finger roots; roll forearm so palms face inward, not a tray-carrying pose.
  hand=rest_world[bn(s,'Hand')].translation;along=rest_world[bn(s,'Middle1')].translation-hand;across=rest_world[bn(s,'Index1')].translation-rest_world[bn(s,'Little1')].translation;palm=along.cross(across).normalized()
  if palm.z>0:palm=-palm
  n=qw(bn(s,'LowerArm'))@rest_world[bn(s,'LowerArm')].to_quaternion().inverted()@palm;axis=yaw@low;target=yaw@Vector((-sign,0,0));n=(n-axis*n.dot(axis)).normalized();target=(target-axis*target.dot(axis)).normalized();roll=math.atan2(axis.dot(n.cross(target)),n.dot(target));set_q(rig,bn(s,'LowerArm'),Quaternion(axis,roll)@qw(bn(s,'LowerArm')))
  q=qw(bn(s,'LowerArm'))@rest_world[bn(s,'LowerArm')].to_quaternion().inverted()@rest_world[bn(s,'Hand')].to_quaternion();set_q(rig,bn(s,'Hand'),q)
 # Keep the source limb rest lengths, with a smooth target-specific pelvis envelope.
 ratio=.84 if name=='Run' else .93 if name=='Walk' else .99+(.93-.99)*moving
 target_height=statistics.mean(ankles.values())+leg*ratio+(.006 if name=='Run' else .002)*math.sin(4*math.pi*plan['phase'])*moving
 hips=statistics.mean(world(bn(s,'UpperLeg')).translation.z for s in ['l','r']);root.location.z+=target_height-hips;bpy.context.view_layer.update()
 # Coherent FK-only draft for before/after: target-native arm/torso and source leg directions, no world contact or skirt adjustment.
 for s in ['l','r']:
  for a,b,sa,sb in [('UpperLeg','LowerLeg','thigh_'+s,'calf_'+s),('LowerLeg','Foot','calf_'+s,'foot_'+s)]:
   direction=(Vector(f[sb]['p'])-Vector(f[sa]['p'])).normalized();n,c=bn(s,a),bn(s,b);ref=rest_world[c].translation-rest_world[n].translation;set_q(rig,n,ref.rotation_difference(yaw@direction)@rest_world[n].to_quaternion())
  set_q(rig,bn(s,'Foot'),yaw@flat[s])
 return lean
