"""Read-only source diagnosis using disposable Blender copies. No horse animation or released bytes changed."""
import bpy,json,sys,hashlib,statistics
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from v05.blender_utils import *
OUT=R/'work/v09-horses';OUT.mkdir(parents=True,exist_ok=True)
for key,file in [('horse-brown','Horse_V23.blend'),('horse-white','Horse_White_V23.blend')]:
 F=R/'library-v04'/key/'2.3.0';original=F/'model.glb';source=R/'sources-v04/horses'/key/file;bpy.ops.wm.open_mainfile(filepath=str(source));rig=bpy.data.objects['AnimalArmature'];ob=bpy.data.objects['Horse'];rig.animation_data_clear()
 for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
 bpy.context.view_layer.update();sync=sync_runtime_weights(ob,rig,original,0);vs=vertices(ob);floor=min(p.z for p in vs);shoulder=statistics.mean(bone_world(rig,'FrontUpperLeg.'+s).translation.y for s in ['L','R']);section=max(p.z for p in vs if abs(p.x)<.3 and abs(p.y-shoulder)<.2);scale=1.5/(section-floor);paws={}
 for part in ['Front','Back']:
  for s in ['L','R']:
   ids=[i for i,p in enumerate(vs) if p.z<floor+.38 and p.x*(1 if s=='L' else -1)>0 and (p.y<0 if part=='Front' else p.y>0)];low=min(vs[i].z for i in ids);flat=[i for i in ids if vs[i].z<low+.025];paws[part+s]={'ids':ids,'flat':flat,'center':list(sum((vs[i] for i in flat),Vector())/len(flat))}
 maps=[{'node_name':'Horse','primitive':i,'indices':{str(n):j for j,n in enumerate(m['native_ids'])}} for i,m in enumerate(sync['maps'])];rig.animation_data_create();probes={}
 for name in ['Idle','Walk','Gallop']:
  action=bpy.data.actions[name];rig.animation_data.action=action
  if action.slots:rig.animation_data.action_slot=action.slots[0]
  bpy.context.scene.frame_set(0);v=vertices(ob);probes[name]={'Body':[[p.x*scale,(p.z-floor)*scale+.003,-p.y*scale] for p in v]}
 data={'asset_id':key,'version':'2.3.0','model_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'source_mother':str(source.relative_to(R)),'source_mother_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'display_calibration':{'scale':scale,'offset_y':.003-floor*scale,'method':'Uniform framing scale from a narrow front-shoulder/neck section, chosen section height 1.50m; not true withers measurement or biological size certification. Original GLB unchanged.','native_section_height':section-floor},'paws':paws,'vertex_maps':maps,'diagnostic_copy_weight_sync':{k:v for k,v in sync.items() if k!='maps'},'native_IK_constraints':sum(len(p.constraints) for p in rig.pose.bones),'contact_status':'Not calibrated. In-place gait; horizontal motion is not judged as world foot sliding without a speed/root plan.','art_approved':False,'game_ready':False}
 (OUT/(key+'.json')).write_text(json.dumps(data,indent=2)+'\n');(OUT/(key+'-cold.json')).write_text(json.dumps(probes)+'\n');print(key,'source read, maps',len(maps),'constraints',data['native_IK_constraints'],flush=True)
