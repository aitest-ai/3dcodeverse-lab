"""Append WalkWorld to preserved v10 horses; immutable originals and candidate-only IDs."""
import bpy,sys,json,os,copy,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import *
from v05.overlay import Overlay
from v10.horse_solver import sample_native,bake_native_actions
from v11.world_walk import fix_feet
from v11.curve_recipe import load_recipe,compare_curve
h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=json.loads((R/'config-v11/walk-plan.json').read_text());OUT=Path(os.environ.get('STUDIO_V11_OUT',str(R/'library-v11'))).resolve();T=plan['duration_s'];v=plan['candidate_speed_m_s'];N=round(T*120)
for key in ['horse-brown','horse-white']:
 if os.environ.get('STUDIO_HORSE') and os.environ['STUDIO_HORSE']!=key:continue
 base=R/'inputs-v11/v10'/(key+'-grounded-review')/'0.1.0';source=base/'model.glb';mother=base/'model.blend';meta=json.loads((base/'adaptation.json').read_text());assert h(source)==meta['model_sha256'] and h(mother)==meta['mother_sha256'];diag=json.loads((R/'library-v09/horse-diagnostics'/(key+'.json')).read_text());cal=diag['display_calibration'];scale=cal['scale'];doc,_=read(source)
 bpy.ops.wm.open_mainfile(filepath=str(mother))
 for a in bpy.data.actions:a.use_fake_user=True
 rig=bpy.data.objects['AnimalArmature'];body=bpy.data.objects['Horse'];rig.animation_data_clear();rig.animation_data_create();sample_native(rig,bpy.data.actions['Idle'],0);idle={b.name:bone_world(rig,b.name).copy() for b in rig.pose.bones};walk=bpy.data.actions['Walk']
 for keyfoot,pfoot in plan['feet'].items():
  sample_native(rig,walk,((pfoot['phase']+pfoot['duty']/2)%1)*T);side=keyfoot[-1];front=keyfoot.startswith('Front')
  for n in [('IKFrontLeg.' if front else 'IKBackLeg.')+side,('FF.' if front else 'FFB.')+side,('FrontLowerLeg.' if front else 'BackLowerLeg.')+side]:idle[n]=bone_world(rig,n).copy()
 capture=Capture(rig,source);clips={};allframes={}
 for variant in ['translation-trial','world-review']:
  frames=[];bakes=[];audit=[]
  for i in range(N+1):
   t=T*i/N;pose=sample_native(rig,walk,t);rig.animation_data.action=None;restore_basis(rig,pose);feet=fix_feet(rig,body,diag['paws'],cal,plan,t,idle) if variant=='world-review' else None;root=Matrix.Translation((0,-v*t/scale,0));frames.append(capture.frame(root));bakes.append({'time':t,'pose':pose_basis(rig)});audit.append({'time':t,'feet':feet})
  for node in capture.map:frames[-1][node]=copy.deepcopy(frames[0][node])
  bakes[-1]['pose']=copy.deepcopy(bakes[0]['pose']);allframes[variant]=frames;clips[variant]=bakes
  out=OUT/(key+'-walk-'+variant)/'0.1.0';out.mkdir(parents=True,exist_ok=True)
  if (out/'model.glb').exists():raise RuntimeError('Refuse overwrite '+str(out))
  overlay=Overlay(source,{});overlay.doc['nodes'][overlay.wrapper]['name']='StudioTravelRoot_v11';recipe=load_recipe(R,overlay.doc)[variant];curve_error=compare_curve(frames,recipe['frames']);frames=recipe['frames'];overlay.animation('WalkWorld',[T*i/N for i in range(N+1)],frames);sha=overlay.save(out/'model.glb');(out/'motion-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(key,variant,sha,flush=True)
  if variant=='world-review':
   bake_native_actions(rig,{'WalkWorld':bakes});root=bpy.data.objects.new('StudioTravelRoot_v11',None);bpy.context.collection.objects.link(root)
   for ob in [rig,bpy.data.objects['ManeTail_IndividualWisps']]:
    if ob.parent is None:ob.parent=root
   root.animation_data_create();action=bpy.data.actions.new('WalkWorld_Root');action.use_fake_user=True;root.animation_data.action=action
   for t in [0,T]:root.location=(0,-v*t/scale,0);root.keyframe_insert(data_path='location',frame=t*24)
   for layer in action.layers:
    for strip in layer.strips:
     for bag in strip.channelbags:
      for fc in bag.fcurves:
       for kp in fc.keyframe_points:kp.interpolation='LINEAR'
   root.animation_data.action=None;root.location=(0,0,0);bpy.context.scene.frame_set(0);bpy.context.view_layer.update();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'))
  m={'asset_id':key+'-walk-'+variant,'version':'0.1.0','source_id':key,'source_glb':str(source.relative_to(R)),'source_glb_sha256':h(source),'source_mother':str(mother.relative_to(R)),'source_mother_sha256':h(mother),'model_sha256':sha,'mother_sha256':h(out/'model.blend') if variant=='world-review' else None,'display_calibration':cal,'solver_vs_frozen_curve_max_component':curve_error,'portable_motion_source':'motion-v11/horse-world-curves.json','added_clip':'WalkWorld','preserved_clips':[a['name'] for a in doc['animations']],'native_joints':50,'travel_wrapper':'StudioTravelRoot_v11','plan':plan,'art_approved':False,'game_ready':False,'comparison_note':'A is a new root-only trial using v10 Walk, not an old published world-walk animation; B applies native hoof planning.'};(out/'adaptation.json').write_text(json.dumps(m,indent=2)+'\n')
 (OUT/(key+'-curves.json')).write_text(json.dumps({'times':[T*i/N for i in range(N+1)],'frames':allframes},separators=(',',':'))+'\n')
