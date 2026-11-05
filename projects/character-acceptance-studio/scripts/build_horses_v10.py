"""Reproducible candidate-only horse correction; source 2.3.0 remains immutable."""
import bpy,json,sys,os,hashlib,copy
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import *
from v07.overlay import ClipOverlay
from v06.geometry_guard import geometry_signature
from v10.horse_solver import *
from v10.curve_recipe import load_recipe,compare_curve
h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
OUT=Path(os.environ.get('STUDIO_V10_OUT',str(R/'library-v10'))).resolve();only=os.environ.get('STUDIO_HORSE')
for key,file in [('horse-brown','Horse_V23.blend'),('horse-white','Horse_White_V23.blend')]:
 if only and only!=key:continue
 diag=json.loads((R/'library-v09/horse-diagnostics'/(key+'.json')).read_text());original=R/'library-v04'/key/'2.3.0/model.glb';mother=R/diag['source_mother'];assert h(original)==diag['model_sha256'] and h(mother)==diag['source_mother_sha256'];out=OUT/(key+'-grounded-review')/'0.1.0';out.mkdir(parents=True,exist_ok=True)
 if (out/'model.glb').exists():raise RuntimeError('Refuse overwriting candidate '+str(out))
 bpy.ops.wm.open_mainfile(filepath=str(mother));
 for native_action in bpy.data.actions:native_action.use_fake_user=True
 rig=bpy.data.objects['AnimalArmature'];body=bpy.data.objects['Horse'];rig.animation_data_clear()
 for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
 bpy.context.view_layer.update();sync={};doc,_=read(original)
 for obj,mesh in [('Horse',0),('ManeTail_IndividualWisps',1)]:sync[obj]=sync_runtime_weights(bpy.data.objects[obj],rig,original,mesh)
 rig.animation_data_create();recipe=load_recipe(R,doc);capture=Capture(rig,original);overlay=ClipOverlay(original);paws=diag['paws'];scale=diag['display_calibration']['scale'];offset=diag['display_calibration']['offset_y'];clips={};audit={}
 for name in ['Walk','Gallop']:
  action=bpy.data.actions[name];duration=float(action.frame_range[1])/24;cyclic=CyclicNative(rig,action) if name=='Gallop' else None;n=round(duration*120);frames=[];bakes=[];rows=[]
  for i in range(n+1):
   t=duration*i/n;pose=cyclic.pose(t) if cyclic else sample_native(rig,action,t);rig.animation_data.action=None;restore_basis(rig,pose);feet=correct_ground(rig,body,paws,scale,offset);frame=capture.frame(Matrix.Identity(4));frame.pop(capture.wrapper);frames.append(frame);bakes.append({'time':t,'pose':pose_basis(rig)});rows.append({'time':t,'feet':feet})
  # Exact pose closure after independently solving every sampled frame.
  frames[-1]=copy.deepcopy(frames[0]);bakes[-1]['pose']=copy.deepcopy(bakes[0]['pose']);curve_error=compare_curve(frames,recipe[name]['frames']);overlay.replace_clip(name,recipe[name]['times'],recipe[name]['frames']);clips[name]=bakes;audit[name]={'duration_s':duration,'bake_hz':120,'solver_vs_frozen_curve_max_component':curve_error,'gallop_bridge_fraction':.12 if cyclic else 0,'samples':rows};print(key,name,'floor',min(f['minimum_sole_y_m'] for r in rows for f in r['feet'].values()),'maxlift',max(f['requested_lift_m'] for r in rows for f in r['feet'].values()),flush=True)
 sha=overlay.save(out/'model.glb');bake_native_actions(rig,clips);bpy.ops.file.pack_all();guard=geometry_signature();bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'))
 meta={'asset_id':key+'-grounded-review','version':'0.1.0','source_id':key,'source_version':'2.3.0','source_glb':str(original.relative_to(R)),'source_glb_sha256':h(original),'source_mother':str(mother.relative_to(R)),'source_mother_sha256':h(mother),'model_sha256':sha,'portable_motion_source':'motion-v10/horse-grounded-curves.json; fresh solver checked within 1e-5 component tolerance before frozen curve export','mother_sha256':h(out/'model.blend'),'geometry_signature':guard,'display_calibration':diag['display_calibration'],'source_profile':'library-v09/horse-diagnostics/'+key+'-skeleton-profile.json','corrected_clips':['Walk','Gallop'],'unchanged_clips':[a['name'] for a in doc['animations'] if a['name'] not in clips],'native_joints':50,'root_motion':'original in-place; no guessed world stride; world sliding not evaluated','solver':'native anterior two-link upper/lower; rear upper/lower below unchanged proximal BackLeg; original bend half-plane and instantaneous link lengths','gallop_loop':'Cubic Hermite bridge across last/first 12% in native local TRS; normalized quaternion curves; final sampled pose exact first','clearance':'2mm soft floor, 4mm transition width in explicit display scale; no rig/root lift','weights_in_editable_copy':{k:{a:b for a,b in v.items() if a!='maps'} for k,v in sync.items()},'art_approved':False,'game_ready':False}
 (out/'adaptation.json').write_text(json.dumps(meta,indent=2)+'\n');(out/'motion-audit.json').write_text(json.dumps({'clips':audit},indent=2)+'\n');print('BUILT',key,sha,flush=True)
