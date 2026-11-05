"""Calibrated Shiba native-body animation with explicit four-paw contact reconstruction."""
import bpy,math,json,os,sys,hashlib,statistics
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import *
from v05.overlay import Overlay
OUT=Path(os.environ.get('STUDIO_V05_OUT',str(R/'work/v05-build'))).resolve()/'quaternius-shibainu-grounded-review'/'0.1.0';OUT.mkdir(parents=True,exist_ok=True)
original=R/'library-v04/quaternius-shibainu/1.0.0/model.glb';mother=R/'sources-v04/animals/ShibaInu.blend';bpy.ops.wm.open_mainfile(filepath=str(mother));sc=bpy.context.scene;rig=bpy.data.objects['AnimalArmature'];ob=bpy.data.objects['ShibaInu'];rig.animation_data_clear();weight_sync=sync_runtime_weights(ob,rig,original,0)
for p in rig.pose.bones:
 p.matrix_basis=Matrix.Identity(4)
 for c in p.constraints:c.mute=True
bpy.context.view_layer.update();v=vertices(ob);paws={}
for part in ['Front','Back']:
 for s in ['L','R']:
  ids=[i for i,p in enumerate(v) if p.z<.35 and p.x*(1 if s=='L' else -1)>0 and (p.y<0 if part=='Front' else p.y>0)];lo=min(v[i].z for i in ids);flat=[i for i in ids if v[i].z<lo+.025];paws[part+s]={'ids':ids,'flat':flat,'ik':'IK'+part+'Leg.'+s}
shoulder_y=statistics.mean(bone_world(rig,'FrontUpperLeg.'+s).translation.y for s in ['L','R']);withers=max(p.z for p in v if abs(p.x)<.25 and abs(p.y-shoulder_y)<.15);floor=min(p.z for p in v);scale=.40/(withers-floor);root=bpy.data.objects.new('StudioRootMotion_v05',None);sc.collection.objects.link(root);rig.parent=root;root.scale=(scale,)*3;root.location.z=.003-floor*scale;bpy.context.view_layer.update();rest=vertices(ob)
for k,p in paws.items():p['center']=list(sum((rest[i] for i in p['flat']),Vector())/len(p['flat']))
for p in rig.pose.bones:
 for c in p.constraints:c.mute=False
rig.animation_data_create();capture=Capture(rig,original);A=Overlay(original,{'scale':[scale]*3,'translation':[0,root.location.z,0]});C=Overlay(original,{'scale':[scale]*3,'translation':[0,root.location.z,0]});audit={};baked={};fps=60
plans={'Walk':{'stride':.36,'duty':.58,'phase':{'FrontL':0,'FrontR':.5,'BackL':.875,'BackR':.375},'lift':.028},'Gallop':{'stride':.56,'duty':.32,'phase':{'FrontL':.98,'FrontR':.18,'BackL':.43,'BackR':.55},'lift':.065}}
def sample(name,t,D,k):
 p=paws[k];center=Vector(p['center'])
 if name=='Idle':return center,0,True,0
 plan=plans[name];phase=t/D-plan['phase'][k];cycle=math.floor(phase);u=phase-cycle;duty=plan['duty'];stride=plan['stride'];start=(cycle+plan['phase'][k])*D
 anchor=Vector((center.x,center.y-stride*duty/2-stride*start/D,center.z))
 if u<duty:return anchor,0,True,cycle
 a=(u-duty)/(1-duty);ease=a*a*a*(10-15*a+6*a*a);anchor.y-=stride*ease;return anchor,plan['lift']*math.sin(math.pi*a)**2,False,cycle
for name in ['Idle','Walk','Gallop']:
 a=bpy.data.actions[name];rig.animation_data.action=a
 if a.slots:rig.animation_data.action_slot=a.slots[0]
 D=float(a.frame_range[1])/30;N=round(D*fps);af=[];cf=[];bf=[];rows=[]
 for i in range(N+1):
  t=i/fps;frame=t*30;sc.frame_set(int(frame),subframe=frame%1);root.location=(0,-plans[name]['stride']*t/D if name in plans else 0,.003-floor*scale);bpy.context.view_layer.update();af.append(capture.frame(root.matrix_world));targets={k:sample(name,t,D,k) for k in paws}
  # Native FK body/head/tail plus existing two-/four-segment IK; original master remains immutable.
  for _ in range(12):
   v=vertices(ob);error=0
   for k,p in paws.items():
    ref=sum((v[j] for j in p['flat']),Vector())/len(p['flat']);low=min(v[j].z for j in p['ids']);desired,lift,contact,cycle=targets[k];diff=Vector((desired.x-ref.x,desired.y-ref.y,.003+lift-low));error=max(error,diff.length);m=bone_world(rig,p['ik']);m.translation+=diff;set_world(rig,p['ik'],m)
   if error<.00002:break
  v=vertices(ob);cf.append(capture.frame(root.matrix_world));bf.append({'bones':pose_basis(rig),'root':{'p':list(root.location),'q':[1,0,0,0],'s':[scale]*3}});foot={}
  for k,p in paws.items():
   target,lift,contact,cycle=targets[k];ref=sum((v[j] for j in p['flat']),Vector())/len(p['flat']);foot[k]={'reference_m':list(ref),'minimum_z_m':min(v[j].z for j in p['ids']),'target_m':list(target),'clearance_m':lift,'contact':contact,'contact_id':cycle,'xy_error_m':math.hypot(ref.x-target.x,ref.y-target.y)}
  rows.append({'t':t,'root':list(root.location),'feet':foot})
 A.animation(name,[i/fps for i in range(N+1)],af);C.animation(name,[i/fps for i in range(N+1)],cf);audit[name]={'duration_s':D,'samples':rows};baked[name]=bf;print(name,'min',min(f['minimum_z_m'] for r in rows for f in r['feet'].values()),'xy',max(f['xy_error_m'] for r in rows for f in r['feet'].values()),flush=True)
A.save(OUT/'baseline.glb');sha=C.save(OUT/'model.glb');(OUT/'motion-audit.json').write_text(json.dumps({'fps':fps,'clips':audit},indent=2)+'\n');(OUT/'adaptation.json').write_text(json.dumps({'asset_id':'quaternius-shibainu-grounded-review','version':'0.1.0','target_source':str(original.relative_to(R)),'target_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'native_blender':str(mother.relative_to(R)),'native_blender_sha256':hashlib.sha256(mother.read_bytes()).hexdigest(),'editable_weight_sync':{k:v for k,v in weight_sync.items() if k!='maps'},'vertex_maps':weight_sync['maps'],'scale':scale,'chosen_withers_m':.40,'scale_note':'Uniform whole-character gameplay size, not measured biological accuracy; no anatomy or clothing resize.','native_rest_withers_z':withers,'native_rest_floor_z':floor,'paws':paws,'plans':plans,'body_head_tail':'native source motion; original topology, skin, material bytes preserved','motion_method':'New authored foot-contact targets matching native gait phase; existing native IK, world displacement, 60 Hz FK bake. Not new mocap/training.','corrected_clips':['Idle','Walk','Gallop'],'untouched_original_clips':'other 9 clips retain original sampler bytes under uniform scale; no contact approval','original_binary_prefix_sha256':C.original_binary_sha256,'original_binary_prefix_bytes':C.original_binary_bytes,'model_sha256':sha,'art_approved':False,'game_ready':False},indent=2)+'\n');bake_actions(rig,root,baked,fps);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'model.blend'),compress=True);print('SHIBA_COMPLETE',sha,flush=True)
