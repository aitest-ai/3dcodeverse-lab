"""Smooth native Walk wrap before the existing fixed-length hoof solver.
Only three body clips change; all travel curves and fifteen other clips stay exact.
"""
import copy, hashlib, json, os, sys
from pathlib import Path
import bpy
from mathutils import Matrix, Quaternion
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import Capture, read, bone_world, restore_basis, pose_basis
from v10.horse_solver import sample_native
from v13.plan import body_weight, distance, speed
from v13.solver import fix_feet
from v14.overlay import BodyOverlay
from v14.native_bake import bake_body_actions
from v14.smoothing import CyclicWalk,sample_times
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=json.loads((R/'config-v12/walk-plan.json').read_text());T=plan['duration_s'];HZ=240
OUT=Path(os.environ.get('STUDIO_V14_OUT',str(R/'library-v14'))).resolve()
authoring=os.environ.get('STUDIO_V14_AUTHORING')=='1'
if authoring and not OUT.is_relative_to(R/'work'):raise RuntimeError('Unfrozen trial must remain under work/')
locked=json.loads((R/'config-v13/horses.lock.json').read_text())['assets']
specs={'WalkWorld':(3*T,4*T),'StartWalk':(0.,3*T),'StopWalk':(5*T,8*T)}
for key in ['horse-brown','horse-white']:
    if os.environ.get('STUDIO_HORSE') and os.environ['STUDIO_HORSE']!=key:continue
    base=R/'library-v13'/(key+'-walk-transition-review')/'0.1.0'
    source,mother=base/'model.glb',base/'model.blend';src=json.loads((base/'adaptation.json').read_text());doc,_=read(source)
    assert sha(source)==src['model_sha256']==next(a['model_sha256'] for a in locked if a['asset_id']==src['asset_id'])
    assert sha(mother)==src['mother_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(mother))
    for a in bpy.data.actions:a.use_fake_user=True
    rig,body,root=[bpy.data.objects[n] for n in ['AnimalArmature','Horse','StudioTravelRoot_v11']]
    root.animation_data_clear();root.matrix_basis=Matrix.Identity(4)
    diag=json.loads((R/'library-v09/horse-diagnostics'/(key+'.json')).read_text());cal=diag['display_calibration']
    walk=bpy.data.actions['Walk'];neutral=sample_native(rig,bpy.data.actions['Idle'],0);cyclic=CyclicWalk(rig,walk)
    assert abs(cyclic.duration-T)<1e-6
    idle={}
    for foot,p in plan['feet'].items():
        sample_native(rig,walk,((p['phase']+p['duty']/2)%1)*T)
        side=foot[-1];front=foot.startswith('Front')
        for n in [('IKFrontLeg.' if front else 'IKBackLeg.')+side,('FF.' if front else 'FFB.')+side,('FrontLowerLeg.' if front else 'BackLowerLeg.')+side]:idle[n]=bone_world(rig,n).copy()
    capture=Capture(rig,source);curves={};bakes={};audits={}
    for name,(start,end) in specs.items():
        times=sample_times(end-start,T);frames=[];poses=[];audit=[]
        for local in times:
            t=start+local;pose=cyclic.pose(t%T);w=body_weight(t,plan)
            for n,d in pose.items():
                d['p']=[(1-w)*a+w*b for a,b in zip(neutral[n]['p'],d['p'])]
                d['s']=[(1-w)*a+w*b for a,b in zip(neutral[n]['s'],d['s'])]
                d['q']=list(Quaternion(neutral[n]['q']).slerp(Quaternion(d['q']),w))
            rig.animation_data.action=None;restore_basis(rig,pose)
            feet=fix_feet(rig,body,diag['paws'],cal,plan,t,idle)
            row=capture.frame(Matrix.Identity(4));row.pop(capture.wrapper);frames.append(row)
            poses.append({'time':local,'pose':pose_basis(rig)})
            audit.append({'time':local,'global_time':t,'feet':feet})
        if name=='WalkWorld':
            frames[-1]=copy.deepcopy(frames[0]);poses[-1]['pose']=copy.deepcopy(poses[0]['pose'])
        curves[name]={'times':times,'frames':frames};bakes[name]=poses;audits[name]=audit
        print('V14_SOLVED',key,name,len(times),flush=True)
    if authoring:
        OUT.mkdir(parents=True,exist_ok=True);(OUT/(key+'-curves.json')).write_text(json.dumps(curves,separators=(',',':'))+'\n')
    error=None
    if not authoring:
        from v14.curve_recipe import load_recipe,compare_curve
        recipe=load_recipe(R,doc);error=max(compare_curve(curves[n]['frames'],recipe[n]['frames']) for n in curves);curves=recipe
    asset_id=key+'-walk-smooth-review';out=OUT/asset_id/'0.1.0';out.mkdir(parents=True,exist_ok=True)
    if (out/'model.glb').exists():raise RuntimeError('Refuse overwrite '+str(out))
    overlay=BodyOverlay(source)
    for name,c in curves.items():overlay.replace_body(name,c['times'],c['frames'])
    model_sha=overlay.save(out/'model.glb')
    bpy.ops.wm.open_mainfile(filepath=str(mother))
    for a in bpy.data.actions:a.use_fake_user=True
    rig=bpy.data.objects['AnimalArmature'];root=bpy.data.objects['StudioTravelRoot_v11']
    root.animation_data_clear();root.matrix_basis=Matrix.Identity(4);bake_body_actions(rig,bakes)
    bpy.context.scene.frame_set(0);bpy.context.view_layer.update();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'))
    meta={**src,'asset_id':asset_id,'variant':'corrected','source_asset_id':src['asset_id'],'source_version':'0.1.0','source_glb':str(source.relative_to(R)),'source_glb_sha256':sha(source),'source_mother':str(mother.relative_to(R)),'source_mother_sha256':sha(mother),'model_sha256':model_sha,'mother_sha256':sha(out/'model.blend'),'solver_vs_frozen_curve_max_component':error,'portable_motion_source':'motion-v14/horse-smooth-curves.json','added_clips':[],'replaced_clips':list(curves),'preserved_clips':[a['name'] for a in doc['animations'] if a['name'] not in curves],'smoothing':{'method':'Native Walk local TRS Hermite wrap with seam-pose-preserving quartic correction, quaternion normalization, then existing fixed-length contact solver','window_each_side_s':cyclic.window,'native_derivative_step_s':cyclic.step,'base_bake_hz':HZ,'wrap_bake_hz':2400,'dense_guard_s':T*.015+1/240,'runtime_interpolation':'LINEAR; finite baked derivative breaks remain and must be measured','root_motion':'All original root channels and native root actions preserved'},'minimum_reach_margin_m':min(f['reach_margin_m'] for rows in audits.values() for row in rows for f in row['feet'].values()),'comparison_note':'A is the exact v13 corrected candidate. B changes only WalkWorld/StartWalk/StopWalk body curves. Same body in two colors; not a new body fit.'}
    (out/'adaptation.json').write_text(json.dumps(meta,indent=2)+'\n');(out/'motion-audit.json').write_text(json.dumps(audits,indent=2)+'\n')
    print('V14_BUILT',asset_id,model_sha,flush=True)
