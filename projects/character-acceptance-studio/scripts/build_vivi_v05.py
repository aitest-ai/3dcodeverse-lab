"""Vivi native-rig motion adaptation. Blender background; raw VRM geometry/materials retained by overlay."""
import bpy,math,json,os,sys,hashlib,statistics
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import *
from v05.overlay import Overlay
from gait_plan_v02 import Planner,rot,smooth
OUT=Path(os.environ.get('STUDIO_V05_OUT',str(R/'work/v05-build'))).resolve()/'vroid-vivi-motion-review'/'0.1.0';OUT.mkdir(parents=True,exist_ok=True);FPS=60;GROUND=.003
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(name,d):(OUT/name).write_text(json.dumps(d,indent=2)+'\n')
source=R/'assets/harbor-courier-review/0.3.0/harbor-courier-review.blend';original=R/'library-v04/vroid-vivi/1.0.0/model.glb';mother=R/'library-v04/vroid-vivi/1.0.0/model.blend'
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
leg=sum((world(bn('l',a)).translation-world(bn('l',b)).translation).length for a,b in [('UpperLeg','LowerLeg'),('LowerLeg','Foot')]);width=.075
planner=Planner(leg,width,1.3333333333333333,.9333333333333333);planner.strides={'Walk':leg*.95,'Run':leg*1.65};planner.duration={n:(len(f)-1)/FPS for n,f in native.items()}
bodymap={'J_Bip_C_Hips':'pelvis','J_Bip_C_Spine':'spine_01','J_Bip_C_Chest':'spine_02','J_Bip_C_UpperChest':'spine_03','J_Bip_C_Neck':'neck_01','J_Bip_C_Head':'Head'}
if 'Head' not in source_rest:bodymap['J_Bip_C_Head']='head'

def base(name,t,plan):
 restore_basis(rig,rest_basis);root.location=plan['root'];root.rotation_quaternion=Quaternion((0,0,1),math.pi+plan['yaw']);root.scale=(1,1,1);bpy.context.view_layer.update();yaw=Quaternion((0,0,1),plan['yaw']);f=native[name][min(len(native[name])-1,round(t*FPS))]
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

def solve(s,target,q,heading):
 n=[bn(s,k) for k in ['UpperLeg','LowerLeg','Foot']];H,K,A=[world(b).translation.copy() for b in n];Q=[qw(b) for b in n[:2]];l1=(K-H).length;l2=(A-K).length;v=target-H;dist=min(max(v.length,.0001),l1+l2-.00001);u=v.normalized();a=(l1*l1-l2*l2+dist*dist)/(2*dist);pole=Vector(rot((.04 if s=='l' else -.04,-1,0),heading));bend=pole-u*pole.dot(u);nk=H+u*a+bend.normalized()*math.sqrt(max(0,l1*l1-a*a));na=H+u*dist
 set_q(rig,n[0],(K-H).rotation_difference(nk-H)@Q[0]);set_q(rig,n[1],(A-K).rotation_difference(na-nk)@Q[1]);set_world(rig,n[2],Matrix.LocRotScale(na,q,Vector((1,1,1))));return (na-target).length

def cloth(plan):
 yaw=Quaternion((0,0,1),plan['yaw']);hip=world('J_Bip_C_Hips');delta=hip@rest_world['J_Bip_C_Hips'].inverted()
 for s in ['l','r']:
  v=yaw.inverted()@(world(bn(s,'LowerLeg')).translation-world(bn(s,'UpperLeg')).translation);pitch=math.atan2(v.y,-v.z)
  for part in ['Front','Back','Side']:
   n='J_Sec_'+sidekey[s]+'_Skirt'+part+'0'
   if n not in rig.pose.bones:continue
   set_world(rig,n,delta@rest_world[n]);n1=n[:-1]+'1';q=qw(n1)
   angle=min(0,pitch)*1.25 if part=='Front' else max(0,pitch)*1.10 if part=='Back' else (-.08 if s=='l' else .08)
   axis=yaw@Vector((0,1,0) if part=='Side' else (1,0,0));set_q(rig,n1,Quaternion(axis,angle)@q)

A=Overlay(original,{'rotation':[0,1,0,0]});C=Overlay(original,{'rotation':[0,1,0,0]});baked={};audit={}
requested=os.environ.get('STUDIO_CLIPS');selected=requested.split(',') if requested else list(planner.duration)
for name in selected:
 D=planner.duration[name];N=round(D*FPS);af=[];cf=[];bf=[];rows=[]
 for i in range(N+1):
  t=i/FPS;sc.frame_set(i);plan=planner.sample(name,t);lean=base(name,t,plan);af.append(capture.frame(root.matrix_world));residual=0
  for s,f in plan['feet'].items():set_q(rig,bn(s,'Foot'),Quaternion((0,0,1),f['yaw'])@Quaternion((1,0,0),f['pitch'])@flat[s])
  for _ in range(7):
   vs=vertices(body);error=0
   for s,f in plan['feet'].items():
    pivot=f['pivot'] if f['contact'] else 'flat';ids=sets[s][pivot];ref=sum((vs[j] for j in ids),Vector())/len(ids);q=Quaternion((0,0,1),f['yaw']);desired=Vector(f['P'])
    if f['contact']:desired+=q@offsets[s].get(pivot,Vector())
    else:
     off=offsets[s]['toe'].lerp(offsets[s]['heel'],f['pivot_blend']);desired+=q@(off-Quaternion((1,0,0),f['pitch'])@off)
    low=min(vs[j].z for j in footids[s]);diff=Vector((desired.x-ref.x,desired.y-ref.y,GROUND+f['clearance']-low));error=max(error,diff.length);residual=max(residual,solve(s,world(bn(s,'Foot')).translation+diff,q@Quaternion((1,0,0),f['pitch'])@flat[s],plan['yaw']))
   if error<.00002:break
  cloth(plan);vs=vertices(body);feet={}
  for s,f in plan['feet'].items():
   ids=sets[s][f['pivot'] if f['contact'] else 'flat'];ref=sum((vs[j] for j in ids),Vector())/len(ids);feet[s]={**f,'reference_m':list(ref),'minimum_z_m':min(vs[j].z for j in footids[s])}
  rows.append({'t':t,'root':list(root.location),'heading':plan['yaw'],'feet':feet,'ik_reach_residual_m':residual,'points':{n:list(world(n).translation) for n in ['J_Bip_C_Hips','J_Bip_C_Neck']+[bn(s,k) for s in ['l','r'] for k in ['UpperArm','LowerArm','Hand','UpperLeg','LowerLeg','Foot']]}});cf.append(capture.frame(root.matrix_world));bf.append({'bones':pose_basis(rig),'root':{'p':list(root.location),'q':list(root.rotation_quaternion),'s':list(root.scale)}})
 A.animation(name,[i/FPS for i in range(N+1)],af);C.animation(name,[i/FPS for i in range(N+1)],cf);baked[name]=bf;audit[name]={'duration_s':D,'samples':rows};print(name,'min shoe',min(f['minimum_z_m'] for row in rows for f in row['feet'].values()),'reach',max(row['ik_reach_residual_m'] for row in rows),flush=True)
A.save(OUT/'baseline.glb');hash=C.save(OUT/'model.glb');js('motion-audit.json',{'fps':FPS,'clips':audit,'method':'Target leg lengths + world anchors + 2-bone knees-forward IK, original shoe vertices, bounded native skirt-chain response; not cloth simulation.'});js('adaptation.json',{'asset_id':'vroid-vivi-motion-review','version':'0.1.0','target_source':str(original.relative_to(R)),'target_sha256':sha(original),'source_motion':str(source.relative_to(R)),'source_motion_sha256':sha(source),'source_motion_status':'existing project-authored candidate, not mocap or art-approved template','original_binary_prefix_sha256':C.original_binary_sha256,'original_binary_prefix_bytes':C.original_binary_bytes,'model_sha256':hash,'runtime_geometry_weights_materials_and_vrm_metadata':'unchanged','editable_weight_sync':{k:{x:y for x,y in v.items() if x!='maps'} for k,v in weight_sync.items()},'target_leg_length_m':leg,'walk_stride_m':planner.strides['Walk'],'run_stride_m':planner.strides['Run'],'foot_vertex_ids':footids,'contact_sets':sets,'flat_foot_world_quaternions':{s:list(q) for s,q in flat.items()},'source_body_map':bodymap,'arm_rest_pose_method':'World segment directions with native T-pose reference; gait-phase opposition and explicit forward elbow flex; never copied local rotations between rigs.','root':'New common parent; native VRM facing -Z corrected by Y pi into +Z; root translation and heading baked.','art_approved':False,'game_ready':False})
bake_actions(rig,root,baked,FPS);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'model.blend'),compress=True);print('VIVI_COMPLETE',hash,flush=True)
