"""New finite transition candidates; never modify source models or their 14 clips."""
import copy
import hashlib
import json
import os
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Quaternion

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R/'scripts'))
from v05.blender_utils import Capture, read, bone_world, set_world, restore_basis, pose_basis
from v07.overlay import ClipOverlay
from v10.horse_solver import sample_native, bake_native_actions
from v13.plan import body_weight, distance, speed, clip_specs, schedule
from v13.solver import fix_feet

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan = json.loads((R/'config-v12/walk-plan.json').read_text())
T = plan['duration_s']
OUT = Path(os.environ.get('STUDIO_V13_OUT', str(R/'library-v13'))).resolve()
authoring = os.environ.get('STUDIO_V13_AUTHORING') == '1'
if authoring and not OUT.is_relative_to(R/'work'):
    raise RuntimeError('Unfrozen authoring is restricted to work/')
locked = json.loads((R/'config-v12/horses.lock.json').read_text())['assets']


def root_action(root, name, times, start):
    a = bpy.data.actions.new(name+'_Root'); a.use_fake_user = True
    root.animation_data_create(); root.animation_data.action = a
    for t in times:
        root.location = (0, -(distance(start+t, plan)-distance(start, plan))/plan['display_calibration']['scale'], 0)
        root.keyframe_insert(data_path='location', frame=t*24)
    for layer in a.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for point in fc.keyframe_points: point.interpolation = 'LINEAR'
    root.animation_data.action = None; root.location = (0, 0, 0)


for key in ['horse-brown', 'horse-white']:
    if os.environ.get('STUDIO_HORSE') and os.environ['STUDIO_HORSE'] != key: continue
    base = R/'library-v12'/(key+'-walk-support-review')/'0.1.0'
    source, mother = base/'model.glb', base/'model.blend'
    srcmeta = json.loads((base/'adaptation.json').read_text())
    assert sha(source) == srcmeta['model_sha256'] == next(a['model_sha256'] for a in locked if a['asset_id'] == srcmeta['asset_id'])
    assert sha(mother) == srcmeta['mother_sha256']
    doc, _ = read(source)
    root_index = next(i for i,n in enumerate(doc['nodes']) if n.get('name') == 'StudioTravelRoot_v11')
    diag = json.loads((R/'library-v09/horse-diagnostics'/(key+'.json')).read_text())
    cal = diag['display_calibration']; scale = cal['scale']
    bpy.ops.wm.open_mainfile(filepath=str(mother))
    for a in bpy.data.actions: a.use_fake_user = True
    rig, body, root = [bpy.data.objects[n] for n in ['AnimalArmature', 'Horse', 'StudioTravelRoot_v11']]
    root.animation_data_clear(); root.matrix_basis = Matrix.Identity(4)
    walk = bpy.data.actions['Walk']; neutral = sample_native(rig, bpy.data.actions['Idle'], 0)
    idle = {}
    for foot,p in plan['feet'].items():
        sample_native(rig, walk, ((p['phase']+p['duty']/2)%1)*T)
        side = foot[-1]; front = foot.startswith('Front')
        for n in [('IKFrontLeg.' if front else 'IKBackLeg.')+side, ('FF.' if front else 'FFB.')+side, ('FrontLowerLeg.' if front else 'BackLowerLeg.')+side]:
            idle[n] = bone_world(rig,n).copy()
    capture = Capture(rig,source)
    data = {'baseline': {}, 'corrected': {}}
    bakes = {'baseline': {}, 'corrected': {}}
    audits = {}
    for name,(start,end) in clip_specs(plan).items():
        count = round((end-start)*120)
        times = [i/120 for i in range(count+1)] if count else [0., 1.]
        frames = {'baseline': [], 'corrected': []}
        pose_rows = {'baseline': [], 'corrected': []}; audit = []
        for local in times:
            t = start+local if count else start
            pose = sample_native(rig,walk,t%T); w = body_weight(t,plan)
            for n,d in pose.items():
                d['p'] = [(1-w)*a+w*b for a,b in zip(neutral[n]['p'],d['p'])]
                d['s'] = [(1-w)*a+w*b for a,b in zip(neutral[n]['s'],d['s'])]
                d['q'] = list(Quaternion(neutral[n]['q']).slerp(Quaternion(d['q']),w))
            rig.animation_data.action = None
            for variant in ['baseline','corrected']:
                restore_basis(rig,pose)
                if variant == 'corrected':
                    feet = fix_feet(rig,body,diag['paws'],cal,plan,t,idle)
                    audit.append({'time':local, 'global_time':t, 'distance_m':distance(t,plan)-distance(start,plan), 'speed_m_s':speed(t,plan), 'feet':feet})
                else:
                    # Comparison trial: identical body blend and root ramp, without contact solving.
                    for pb in rig.pose.bones:
                        if pb.parent is None:
                            m=bone_world(rig,pb.name).copy();m.translation.z-=plan['body_lowering_m']/scale;set_world(rig,pb.name,m)
                row=capture.frame(Matrix.Translation((0,-(distance(t,plan)-distance(start,plan))/scale,0)))
                row[root_index]=row.pop(capture.wrapper)
                frames[variant].append(row)
                pose_rows[variant].append({'time':local,'pose':pose_basis(rig)})
        for variant in frames:
            data[variant][name]={'times':times,'frames':frames[variant]}
            bakes[variant][name]=pose_rows[variant]
        audits[name]=audit
    if authoring:
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/(key+'-curves.json')).write_text(json.dumps(data,separators=(',',':'))+'\n')
    for variant in ['baseline','corrected']:
        asset_id=key+('-transition-baseline' if variant=='baseline' else '-walk-transition-review')
        out=OUT/asset_id/'0.1.0';out.mkdir(parents=True,exist_ok=True)
        if (out/'model.glb').exists(): raise RuntimeError('Refuse overwrite '+str(out))
        curve_error=None
        curves=data[variant]
        if not authoring:
            from v13.curve_recipe import load_recipe,compare_curve
            recipe=load_recipe(R,doc,variant)
            curve_error=max(compare_curve(curves[n]['frames'],recipe[n]['frames']) for n in curves)
            curves=recipe
        overlay=ClipOverlay(source)
        for name,c in curves.items(): overlay.replace_clip(name,c['times'],c['frames'])
        model_sha=overlay.save(out/'model.glb')
        bpy.ops.wm.open_mainfile(filepath=str(mother))
        for a in bpy.data.actions: a.use_fake_user=True
        rig=bpy.data.objects['AnimalArmature'];root=bpy.data.objects['StudioTravelRoot_v11']
        root.animation_data_clear();root.matrix_basis=Matrix.Identity(4)
        bake_native_actions(rig,bakes[variant])
        for name in ['StartWalk','StopWalk']:
            root_action(root,name,curves[name]['times'],clip_specs(plan)[name][0])
        root.animation_data.action=None;root.location=(0,0,0)
        bpy.context.scene.frame_set(0);bpy.context.view_layer.update();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'))
        meta={'asset_id':asset_id,'version':'0.1.0','variant':variant,'source_id':key,'source_asset_id':srcmeta['asset_id'],'source_version':'0.1.0','source_glb':str(source.relative_to(R)),'source_glb_sha256':sha(source),'source_mother':str(mother.relative_to(R)),'source_mother_sha256':sha(mother),'model_sha256':model_sha,'mother_sha256':sha(out/'model.blend'),'display_calibration':cal,'solver_vs_frozen_curve_max_component':curve_error,'portable_motion_source':'motion-v13/horse-transition-curves.json','added_clips':list(curves),'preserved_clips':[a['name'] for a in doc['animations']],'native_joints':50,'travel_wrapper':'StudioTravelRoot_v11','walk_plan':plan,'transition':{'duration_s':8*T,'start_duration_s':3*T,'stop_duration_s':3*T,'cruise_cycles':2,'total_distance_m':distance(8*T,plan),'ramp_duration_s':2*T,'body_blend_duration_s':T,'schedule':{k:schedule(plan,k) for k in plan['feet']},'clip_global_ranges':clip_specs(plan),'repeat_note':'Replay resets to the start; not an interruptible controller or a seamless stop-to-start loop.'},'minimum_reach_margin_m':min(f['reach_margin_m'] for a in audits.values() for row in a for f in row['feet'].values()),'art_approved':False,'game_ready':False,'comparison_note':'A is a newly constructed uncorrected transition experiment, NOT an approved v12 transition. B solves planted hoof anchors with the same body blend and root ramp.'}
        (out/'adaptation.json').write_text(json.dumps(meta,indent=2)+'\n')
        if variant=='corrected': (out/'motion-audit.json').write_text(json.dumps(audits,indent=2)+'\n')
        print('V13_BUILT',asset_id,model_sha,flush=True)
