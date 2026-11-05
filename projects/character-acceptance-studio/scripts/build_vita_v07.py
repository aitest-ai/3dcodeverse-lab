"""Vita native-rig body adaptation. Adapted from build_vivi_v05.py at d58ec884; no Vivi local tracks copied. Blender background; raw VRM geometry/materials retained by overlay."""
import bpy,math,json,os,sys,hashlib,statistics
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import *
from v05.overlay import Overlay
from gait_plan_v02 import Planner,rot,smooth
OUT=Path(os.environ.get('STUDIO_V07_OUT',str(R/'work/v07-build'))).resolve()/'vroid-vita-motion-review'/'0.1.0';OUT.mkdir(parents=True,exist_ok=True);FPS=60;GROUND=.003
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(name,d):(OUT/name).write_text(json.dumps(d,indent=2)+'\n')
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


# Explicit per-character working-copy calibration and source locks; preserve original runtime geometry/VRM bytes.
from v07.rig import Legs,skirt
from v06.refine import relaxed_fingers
from v06.collision import regions,crossings
legs=Legs(rig,body,root,footids,sets,{s:list(q) for s,q in flat.items()})
A=Overlay(original,{'rotation':[0,1,0,0]});C=Overlay(original,{'rotation':[0,1,0,0]});bakedA={};bakedB={};auditA={};auditB={}
for name in ['Idle','Walk','Run']:
 D=planner.duration[name];N=round(D*FPS);framesA=[];framesB=[];posesA=[];posesB=[];rowsA=[];rowsB=[]
 for i in range(N+1):
  t=i/FPS;sc.frame_set(i);plan=planner.sample(name,t)
  for variant in ['A','B']:
   base(name,t,plan)
   if variant=='B' and name=='Run':legs.pelvis(plan['phase'])
   if variant=='B' and name=='Walk':legs.pelvis(plan['phase'],midstance=.30,center=.96,amplitude=-.02)
   solve_data=legs.correct(plan)
   skirt(rig,rest_world,plan,.04 if name=='Run' else 0)
   relaxed_fingers(rig,name,t,D)
   f=capture.frame(root.matrix_world);pose={'bones':pose_basis(rig),'root':{'p':list(root.location),'q':list(root.rotation_quaternion),'s':list(root.scale)}};row={'t':t,'root':list(root.location),'heading':plan['yaw'],**solve_data,**legs.audit(plan)}
   (framesA if variant=='A' else framesB).append(f);(posesA if variant=='A' else posesB).append(pose);(rowsA if variant=='A' else rowsB).append(row)
 A.animation(name,[i/FPS for i in range(N+1)],framesA);C.animation(name,[i/FPS for i in range(N+1)],framesB);bakedA[name]=posesA;bakedB[name]=posesB;auditA[name]={'duration_s':D,'samples':rowsA};auditB[name]={'duration_s':D,'samples':rowsB};print('Vita',name,'complete',flush=True)
A.save(OUT/'baseline.glb');modelsha=C.save(OUT/'model.glb');bake_actions(rig,root,bakedA,60);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'baseline.blend'),compress=True);bake_actions(rig,root,bakedB,60);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'model.blend'),compress=True)
js('motion-audit.json',{'fps':60,'clips':auditB,'baseline_clips':auditA});js('adaptation.json',{'asset_id':'vroid-vita-motion-review','version':'0.1.0','original_geometry':str(original.relative_to(R)),'original_geometry_sha256':sha(original),'original_mother':str(mother.relative_to(R)),'original_mother_sha256':sha(mother),'source_motion':str(source.relative_to(R)),'source_motion_sha256':sha(source),'model_sha256':modelsha,'mother_sha256':sha(OUT/'model.blend'),'baseline_sha256':sha(OUT/'baseline.glb'),'baseline_mother_sha256':sha(OUT/'baseline.blend'),'baseline_status':'new native-rig low-pelvis experiment, not original Vita animation, not approved','source_motion_status':'project-authored Harbor reference directions, not mocap/trained AI','editable_weight_sync':weight_sync,'target_leg_length_m':leg,'stance_half_width_m':width,'run_period_s':.7,'run_stride_m':planner.strides['Run'],'run_speed_m_s':planner.strides['Run']/.7,'pelvis_ratio_center':.94,'pelvis_ratio_amplitude':.01,'walk_pelvis_ratio_center':.96,'walk_pelvis_ratio_amplitude':.02,'walk_pelvis_peak_phase':.30,'foot_vertex_ids':footids,'contact_sets':sets,'flat_foot_world_quaternions':{s:list(q) for s,q in flat.items()},'changed_clips':['Idle','Walk','Run'],'skirt_forward_ease_m_per_radian':.04,'runtime_geometry_weights_materials_and_vrm_metadata':'original bytes retained','art_approved':False,'game_ready':False});print('VITA_COMPLETE',modelsha,flush=True)
