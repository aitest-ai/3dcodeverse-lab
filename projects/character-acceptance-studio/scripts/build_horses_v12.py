"""Replace only WalkWorld in a new candidate; original v11 models and native rest remain immutable."""
import bpy,sys,json,os,copy,hashlib
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import Capture,read,bone_world,restore_basis,pose_basis
from v07.overlay import ClipOverlay
from v10.horse_solver import sample_native,bake_native_actions
from v12.world_walk import fix_feet
h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=json.loads((R/'config-v12/walk-plan.json').read_text());OUT=Path(os.environ.get('STUDIO_V12_OUT',str(R/'library-v12'))).resolve();T=plan['duration_s'];v=plan['candidate_speed_m_s'];N=round(T*120)
locked=json.loads((R/'config-v11/horses.lock.json').read_text())['assets']
authoring=os.environ.get('STUDIO_V12_AUTHORING')=='1'
if authoring and not OUT.is_relative_to(R/'work'):raise RuntimeError('Unfrozen authoring output is restricted to work/')
for key in ['horse-brown','horse-white']:
 if os.environ.get('STUDIO_HORSE') and os.environ['STUDIO_HORSE']!=key:continue
 base=R/'library-v11'/(key+'-walk-world-review')/'0.1.0';source=base/'model.glb';mother=base/'model.blend';srcmeta=json.loads((base/'adaptation.json').read_text());assert h(source)==srcmeta['model_sha256']==next(a['model_sha256'] for a in locked if a['asset_id']==srcmeta['asset_id']);assert h(mother)==srcmeta['mother_sha256'];diag=json.loads((R/'library-v09/horse-diagnostics'/(key+'.json')).read_text());cal=diag['display_calibration'];scale=cal['scale'];doc,_=read(source);root_index=next(i for i,n in enumerate(doc['nodes']) if n.get('name')=='StudioTravelRoot_v11');out=OUT/(key+'-walk-support-review')/'0.1.0';out.mkdir(parents=True,exist_ok=True)
 if (out/'model.glb').exists():raise RuntimeError('Refuse overwrite '+str(out))
 bpy.ops.wm.open_mainfile(filepath=str(mother))
 for a in bpy.data.actions:a.use_fake_user=True
 rig=bpy.data.objects['AnimalArmature'];body=bpy.data.objects['Horse'];root=bpy.data.objects['StudioTravelRoot_v11'];root.animation_data_clear();root.matrix_basis=Matrix.Identity(4);rig.animation_data_clear();rig.animation_data_create();walk=bpy.data.actions['Walk'];idle={}
 for foot,p in plan['feet'].items():
  sample_native(rig,walk,((p['phase']+p['duty']/2)%1)*T);side=foot[-1];front=foot.startswith('Front')
  for n in [('IKFrontLeg.' if front else 'IKBackLeg.')+side,('FF.' if front else 'FFB.')+side,('FrontLowerLeg.' if front else 'BackLowerLeg.')+side]:idle[n]=bone_world(rig,n).copy()
 capture=Capture(rig,source);frames=[];bakes=[];audit=[]
 for i in range(N+1):
  t=T*i/N;pose=sample_native(rig,walk,t);rig.animation_data.action=None;restore_basis(rig,pose);feet=fix_feet(rig,body,diag['paws'],cal,plan,t,idle);row=capture.frame(Matrix.Translation((0,-v*t/scale,0)));row[root_index]=row.pop(capture.wrapper);frames.append(row);bakes.append({'time':t,'pose':pose_basis(rig)});audit.append({'time':t,'feet':feet})
 for node in capture.map:frames[-1][node]=copy.deepcopy(frames[0][node])
 bakes[-1]['pose']=copy.deepcopy(bakes[0]['pose']);times=[T*i/N for i in range(N+1)];curve_error=None
 if authoring:(OUT/(key+'-curves.json')).write_text(json.dumps({'times':times,'frames':frames},separators=(',',':'))+'\n')
 else:
  from v12.curve_recipe import load_recipe,compare_curve
  recipe=load_recipe(R,doc)['WalkWorld'];curve_error=compare_curve(frames,recipe['frames']);frames=recipe['frames']
 overlay=ClipOverlay(source);overlay.replace_clip('WalkWorld',times,frames);sha=overlay.save(out/'model.glb');bake_native_actions(rig,{'WalkWorld':bakes});old=bpy.data.actions.get('WalkWorld_Root')
 if old:bpy.data.actions.remove(old)
 root.animation_data_create();a=bpy.data.actions.new('WalkWorld_Root');a.use_fake_user=True;root.animation_data.action=a
 for t in [0,T]:root.location=(0,-v*t/scale,0);root.keyframe_insert(data_path='location',frame=t*24)
 for layer in a.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for point in fc.keyframe_points:point.interpolation='LINEAR'
 root.animation_data.action=None;root.location=(0,0,0);bpy.context.scene.frame_set(0);bpy.context.view_layer.update();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'))
 m={'asset_id':key+'-walk-support-review','version':'0.1.0','source_id':key,'source_asset_id':srcmeta['asset_id'],'source_version':'0.1.0','source_glb':str(source.relative_to(R)),'source_glb_sha256':h(source),'source_mother':str(mother.relative_to(R)),'source_mother_sha256':h(mother),'model_sha256':sha,'mother_sha256':h(out/'model.blend'),'display_calibration':cal,'solver_vs_frozen_curve_max_component':curve_error,'portable_motion_source':'motion-v12/horse-support-curves.json','replaced_clip':'WalkWorld','preserved_clips':[a['name'] for a in doc['animations'] if a['name']!='WalkWorld'],'native_joints':50,'travel_wrapper':'StudioTravelRoot_v11','plan':plan,'minimum_reach_margin_m':min(f['reach_margin_m'] for s in audit for f in s['feet'].values()),'maximum_required_body_lowering_m':max(f['minimum_body_lowering_m'] for s in audit for f in s['feet'].values()),'art_approved':False,'game_ready':False,'comparison_note':'A exact v11 world-review; B equal-quarter lateral sequence. Each has its own planned stance phases, same speed/root path and body lowering.'};(out/'adaptation.json').write_text(json.dumps(m,indent=2)+'\n');(out/'motion-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print('V12_BUILT',key,sha,flush=True)
