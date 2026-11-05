"""Append curved walking turns; retain every v05 clip and source geometry byte. Separate A trial/B correction mothers."""
import bpy,math,json,os,sys,hashlib
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import *
from v07.overlay import ClipOverlay
from v09.quadruped_plan import CurvedWalk
BASE=R/'library-v05/quaternius-shibainu-grounded-review/0.1.0';OUT=Path(os.environ.get('STUDIO_V09_OUT',str(R/'work/v09-build'))).resolve()/'quaternius-shibainu-grounded-review/0.2.0';OUT.mkdir(parents=True,exist_ok=True)
if (OUT/'model.glb').exists():raise RuntimeError('Refuse overwriting existing output; choose a new STUDIO_V09_OUT folder')
hashfile=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();meta=json.loads((BASE/'adaptation.json').read_text())
assert hashfile(BASE/'model.glb')==meta['model_sha256'];original=R/meta['target_source'];native_mother=R/meta['native_blender'];assert hashfile(original)==meta['target_sha256'] and hashfile(native_mother)==meta['native_blender_sha256']
bpy.ops.wm.open_mainfile(filepath=str(BASE/'model.blend'));rig=bpy.data.objects['AnimalArmature'];root=bpy.data.objects['StudioRootMotion_v05'];old={}
for name in ['Idle','Walk','Gallop']:
 for ob in [rig,root]:
  for tr in ob.animation_data.nla_tracks:tr.mute=True
  a=bpy.data.actions[name if ob==rig else name+'_Root'];ob.animation_data.action=a
  if a.slots:ob.animation_data.action_slot=a.slots[0]
 rows=[]
 for i in range(round(rig.animation_data.action.frame_range[1])+1):
  bpy.context.scene.frame_set(i);rows.append({'bones':pose_basis(rig),'root':{'p':list(root.location),'q':list(root.rotation_quaternion),'s':list(root.scale)}})
 old[name]=rows
bpy.ops.wm.open_mainfile(filepath=str(native_mother));sc=bpy.context.scene;rig=bpy.data.objects['AnimalArmature'];ob=bpy.data.objects['ShibaInu'];rig.animation_data_clear();weight_sync=sync_runtime_weights(ob,rig,original,0)
root=bpy.data.objects.new('StudioRootMotion_v05',None);sc.collection.objects.link(root);rig.parent=root;root.rotation_mode='QUATERNION';root.scale=(meta['scale'],)*3;rootz=old['Walk'][0]['root']['p'][2];paws=meta['paws'];period=(len(old['Walk'])-1)/60;planner=CurvedWalk(paws,meta['plans']['Walk'],period);rig.animation_data_create();action=bpy.data.actions['Walk'];capture=Capture(rig,original);A=ClipOverlay(BASE/'model.glb');B=ClipOverlay(BASE/'model.glb');bakedA=dict(old);bakedB=dict(old);audit={};baseline_audit={}
constraints=[c for p in rig.pose.bones for c in p.constraints];N=round(planner.duration*60)
root.location=(0,0,rootz);root.rotation_quaternion=Quaternion((1,0,0,0));rig.animation_data.action=bpy.data.actions['Idle']
if rig.animation_data.action.slots:rig.animation_data.action_slot=rig.animation_data.action.slots[0]
sc.frame_set(0);bpy.context.view_layer.update();paw_rest={}
for key,p in paws.items():
 distal=('FF.' if key.startswith('Front') else 'FFB.')+key[-1];paw_rest[key]={n:bone_world(rig,n).to_quaternion().copy() for n in [p['ik'],distal]}

for name,sign in [('WalkTurnLeft',1),('WalkTurnRight',-1)]:
 frames={'A':[],'B':[]};poses={'A':[],'B':[]};rows={'A':[],'B':[]}
 for i in range(N+1):
  t=i/60;position,yaw=planner.path(t,sign);targets={k:planner.sample(t,k,sign) for k in paws};phase=(i%(len(old['Walk'])-1))/(len(old['Walk'])-1)
  for variant in ['A','B']:
   root.location=(position[0],position[1],rootz);root.rotation_quaternion=Quaternion((0,0,1),yaw);root.scale=(meta['scale'],)*3
   for c in constraints:c.mute=variant=='A'
   if variant=='A':rig.animation_data.action=None;restore_basis(rig,old['Walk'][i%(len(old['Walk'])-1)]['bones'])
   else:
    rig.animation_data.action=action
    if action.slots:rig.animation_data.action_slot=action.slots[0]
    frame=phase*float(action.frame_range[1]);sc.frame_set(int(frame),subframe=frame%1);bpy.context.view_layer.update()
    for k,p in paws.items():
     f=targets[k];u=(t/period-meta['plans']['Walk']['phase'][k])%1;duty=meta['plans']['Walk']['duty'];swing=0 if f['contact'] else math.sin(math.pi*(u-duty)/(1-duty))**2
     for n,flat_q in paw_rest[k].items():
      m=bone_world(rig,n);native_q=Quaternion((0,0,1),-yaw)@m.to_quaternion();q=Quaternion((0,0,1),f['yaw'])@flat_q.slerp(native_q,swing);set_world(rig,n,Matrix.LocRotScale(m.translation,q,m.to_scale()))
    for _ in range(16):
     v=vertices(ob);error=0
     for k,p in paws.items():
      target=targets[k];ref=sum((v[j] for j in p['flat']),Vector())/len(p['flat']);low=min(v[j].z for j in p['ids']);diff=Vector((target['P'][0]-ref.x,target['P'][1]-ref.y,.003+target['clearance']-low));error=max(error,diff.length);m=bone_world(rig,p['ik']);m.translation+=diff;set_world(rig,p['ik'],m)
     if error<.00001:break
   bpy.context.view_layer.update();v=vertices(ob);frames[variant].append(capture.frame(root.matrix_world));poses[variant].append({'bones':pose_basis(rig),'root':{'p':list(root.location),'q':list(root.rotation_quaternion),'s':list(root.scale)}});feet={}
   for k,p in paws.items():
    ref=sum((v[j] for j in p['flat']),Vector())/len(p['flat']);f=targets[k];feet[k]={**f,'reference_m':list(ref),'minimum_z_m':min(v[j].z for j in p['ids']),'xy_error_m':math.hypot(ref.x-f['P'][0],ref.y-f['P'][1])}
   rows[variant].append({'t':t,'root':list(root.location),'heading':yaw,'feet':feet})
 for overlay,key in [(A,'A'),(B,'B')]:overlay.replace_clip(name,[i/60 for i in range(N+1)],frames[key])
 bakedA[name]=poses['A'];bakedB[name]=poses['B'];audit[name]={'duration_s':planner.duration,'samples':rows['B']};baseline_audit[name]={'duration_s':planner.duration,'samples':rows['A']};print(name,'floor',min(f['minimum_z_m'] for r in rows['B'] for f in r['feet'].values()),'target error',max(f['xy_error_m'] for r in rows['B'] for f in r['feet'].values()),flush=True)
asha=A.save(OUT/'baseline.glb');bsha=B.save(OUT/'model.glb');bake_actions(rig,root,bakedA,60);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'baseline.blend'),compress=True);bake_actions(rig,root,bakedB,60);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'model.blend'),compress=True)
meta.update(version='0.2.0',base_model=str((BASE/'model.glb').relative_to(R)),base_model_sha256=hashfile(BASE/'model.glb'),base_mother=str((BASE/'model.blend').relative_to(R)),base_mother_sha256=hashfile(BASE/'model.blend'),model_sha256=bsha,mother_sha256=hashfile(OUT/'model.blend'),baseline_sha256=asha,baseline_mother_sha256=hashfile(OUT/'baseline.blend'),baseline_status='New root-only arc trial using previous corrected straight Walk; not a previous published turn or approved motion',turns={'cycles_per_quarter_turn':4,'walk_period_s':period,'duration_s':planner.duration,'radius_m':planner.radius,'angle_radians':math.pi/2,'paw_orientation':'Native Idle IK/FF orientation held throughout stance; native swing orientation eases in and out; original skin weights retained.','contact_policy':'Native four-paw phase offsets; world anchor fixed during each stance; smooth swing between successive curved-path anchors; foot heading held to midstance heading.'},changed_clips=list(audit),unchanged_clips=[c['name'] for c in B.doc['animations'] if c['name'] not in audit],original_binary_prefix_bytes=B.prefix_bytes,original_binary_prefix_sha256=B.prefix_sha256,art_approved=False,game_ready=False)
for n,x in [('adaptation.json',meta),('motion-audit.json',{'fps':60,'clips':audit,'baseline_clips':baseline_audit})]:(OUT/n).write_text(json.dumps(x,indent=2)+'\n')
print('SHIBA_V09_COMPLETE',bsha,flush=True)
