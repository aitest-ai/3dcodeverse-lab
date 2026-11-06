"""Three new native clips for queued, world-continuous locomotion. Source 18 clips immutable."""
import hashlib,json,os,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Quaternion,Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import Capture,read,bone_world,restore_basis,pose_basis
from v07.overlay import ClipOverlay
from v10.horse_solver import sample_native
from v13.plan import body_weight,distance
from v14.native_bake import bake_body_actions
from v14.smoothing import CyclicWalk,sample_times
from v15.plan import TurnPath,restart_foot,specs
from v15.solver import fix_feet
from v15.native_root import bake_roots
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=json.loads((R/'config-v12/walk-plan.json').read_text());T=plan['duration_s'];definitions=specs(plan)
OUT=Path(os.environ.get('STUDIO_V15_OUT',str(R/'library-v15'))).resolve();authoring=os.environ.get('STUDIO_V15_AUTHORING')=='1'
if authoring and not OUT.is_relative_to(R/'work'):raise RuntimeError('Unfrozen trials must remain under work/')
locked=json.loads((R/'config-v14/horses.lock.json').read_text())['assets']
for key in ['horse-brown','horse-white']:
    if os.environ.get('STUDIO_HORSE') and os.environ['STUDIO_HORSE']!=key:continue
    base=R/'library-v14'/(key+'-walk-smooth-review')/'0.1.0';source,mother=base/'model.glb',base/'model.blend';src=json.loads((base/'adaptation.json').read_text());doc,_=read(source)
    assert sha(source)==src['model_sha256']==next(a['model_sha256'] for a in locked if a['asset_id']==src['asset_id']) and sha(mother)==src['mother_sha256']
    assert not set(definitions)&{a['name'] for a in doc['animations']}
    root_index=next(i for i,n in enumerate(doc['nodes']) if n.get('name')=='StudioTravelRoot_v11')
    bpy.ops.wm.open_mainfile(filepath=str(mother))
    for a in bpy.data.actions:a.use_fake_user=True
    rig,body,root=[bpy.data.objects[n] for n in ['AnimalArmature','Horse','StudioTravelRoot_v11']];root.animation_data_clear();root.matrix_basis=Matrix.Identity(4)
    diag=json.loads((R/'library-v09/horse-diagnostics'/(key+'.json')).read_text());cal=diag['display_calibration'];scale=cal['scale']
    walk=bpy.data.actions['Walk'];neutral=sample_native(rig,bpy.data.actions['Idle'],0);cyclic=CyclicWalk(rig,walk);idle={}
    for foot,p in plan['feet'].items():
        sample_native(rig,walk,((p['phase']+p['duty']/2)%1)*T);side=foot[-1];front=foot.startswith('Front')
        for n in [('IKFrontLeg.' if front else 'IKBackLeg.')+side,('FF.' if front else 'FFB.')+side,('FrontLowerLeg.' if front else 'BackLowerLeg.')+side]:idle[n]=bone_world(rig,n).copy()
    capture=Capture(rig,source);curves={};bakes={};root_bakes={};audits={}
    for name,spec in definitions.items():
        times=sample_times(spec['duration'],T);path=TurnPath(plan,spec['sign']) if spec['kind']=='turn' else None
        frames=[];poses=[];roots=[];audit=[]
        for t in times:
            pose=cyclic.pose((3*T+t)%T);w=body_weight(t,plan) if path is None else 1.
            for n,d in pose.items():
                d['p']=[(1-w)*a+w*b for a,b in zip(neutral[n]['p'],d['p'])];d['s']=[(1-w)*a+w*b for a,b in zip(neutral[n]['s'],d['s'])];d['q']=list(Quaternion(neutral[n]['q']).slerp(Quaternion(d['q']),w))
            rig.animation_data.action=None;restore_basis(rig,pose)
            targets={k:path.foot(t,k) if path else restart_foot(t,plan,k) for k in plan['feet']}
            feet=fix_feet(rig,body,diag['paws'],cal,plan,t,idle,targets)
            xy,yaw=path.at(t) if path else ([0.,-distance(t,plan)],0.)
            position=Vector((xy[0]/scale,xy[1]/scale,0));rotation=Quaternion((0,0,1),yaw)
            matrix=Matrix.LocRotScale(position,rotation,Vector((1,1,1)));row=capture.frame(matrix);row[root_index]=row.pop(capture.wrapper);frames.append(row)
            poses.append({'time':t,'pose':pose_basis(rig)});roots.append({'time':t,'location':list(position),'rotation_quaternion':list(rotation),'scale':[1.,1.,1.]})
            audit.append({'time':t,'root':{'x':xy[0],'z':-xy[1],'yaw':yaw},'feet':feet})
        curves[name]={'times':times,'frames':frames};bakes[name]=poses;root_bakes[name]=roots;audits[name]=audit
        print('V15_SOLVED',key,name,len(times),flush=True)
    if authoring:
        OUT.mkdir(parents=True,exist_ok=True)
        for name,c in curves.items():(OUT/(key+'-'+name+'-curves.json')).write_text(json.dumps(c,separators=(',',':'))+'\n')
    error=None
    if not authoring:
        from v15.curve_recipe import load_recipe,compare_curve
        recipe=load_recipe(R,doc);error=max(compare_curve(curves[n]['frames'],recipe[n]['frames']) for n in curves);curves=recipe
    asset_id=key+'-locomotion-review';out=OUT/asset_id/'0.1.0';out.mkdir(parents=True,exist_ok=True)
    if (out/'model.glb').exists():raise RuntimeError('Refuse overwrite '+str(out))
    overlay=ClipOverlay(source)
    for name,c in curves.items():overlay.replace_clip(name,c['times'],c['frames'])
    model_sha=overlay.save(out/'model.glb')
    bpy.ops.wm.open_mainfile(filepath=str(mother))
    for a in bpy.data.actions:a.use_fake_user=True
    rig=bpy.data.objects['AnimalArmature'];root=bpy.data.objects['StudioTravelRoot_v11'];root.animation_data_clear();root.matrix_basis=Matrix.Identity(4)
    bake_body_actions(rig,bakes);bake_roots(root,root_bakes)
    bpy.context.scene.frame_set(0);bpy.context.view_layer.update();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'))
    meta={**src,'asset_id':asset_id,'source_asset_id':src['asset_id'],'source_version':'0.1.0','source_glb':str(source.relative_to(R)),'source_glb_sha256':sha(source),'source_mother':str(mother.relative_to(R)),'source_mother_sha256':sha(mother),'model_sha256':model_sha,'mother_sha256':sha(out/'model.blend'),'solver_vs_frozen_curve_max_component':error,'portable_motion_source':'motion-v15/','added_clips':list(curves),'replaced_clips':[],'preserved_clips':[a['name'] for a in doc['animations']],'locomotion':{'clips':definitions,'turn_angle_degrees':15,'turn_lead_in_cycles':1,'turn_lead_out_cycles':1,'turn_yaw_convention':'native L bones lie at +X; positive glTF Y yaw turns toward native L','controller':'Intent queue consumed at complete clip/stride boundaries; no arbitrary-phase blend or emergency stop','restart':'StandStopped -> RestartWalk -> WalkWorld, retaining accumulated world transform'},'minimum_reach_margin_m':min(f['reach_margin_m'] for rows in audits.values() for row in rows for f in row['feet'].values()),'comparison_note':'A is the exact v14 candidate with 18 clips. New restart/turn/controller modes use B only; no fabricated v14 counterpart.'}
    (out/'adaptation.json').write_text(json.dumps(meta,indent=2)+'\n');(out/'motion-audit.json').write_text(json.dumps(audits,indent=2)+'\n');print('V15_BUILT',asset_id,model_sha,flush=True)
