"""Cold native mothers, paired travel actions and evaluated surface probes."""
import bpy, hashlib, json, os, sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import vertices
from v14.smoothing import sample_times
from v06.geometry_guard import geometry_signature
from mathutils import Matrix
W=R/'work/v14-cold';W.mkdir(parents=True,exist_ok=True);E=R/'evidence-v14';E.mkdir(exist_ok=True);reports=[];source_signatures={}
for key in ['horse-brown','horse-white']:
    if os.environ.get('STUDIO_HORSE') and os.environ['STUDIO_HORSE']!=key:continue
    for suffix in ['walk-transition-review','walk-smooth-review']:
        F=R/('library-v13' if suffix=='walk-transition-review' else 'library-v14')/(key+'-'+suffix)/'0.1.0';m=json.loads((F/'adaptation.json').read_text())
        assert hashlib.sha256((F/'model.blend').read_bytes()).hexdigest()==m['mother_sha256']
        bpy.ops.wm.open_mainfile(filepath=str(F/'model.blend'))
        rig=bpy.data.objects['AnimalArmature'];root=bpy.data.objects['StudioTravelRoot_v11'];body=bpy.data.objects['Horse']
        preserved={a.name:hashlib.sha256(json.dumps([(fc.data_path,fc.array_index,[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in fc.keyframe_points]) for l in a.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves],sort_keys=True).encode()).hexdigest() for a in bpy.data.actions if a.name not in ['WalkWorld','StartWalk','StopWalk']}
        signature=(geometry_signature(),preserved)
        if suffix=='walk-transition-review':source_signatures[key]=signature
        else:assert signature==source_signatures[key],'Native source scene or preserved actions changed'
        root.animation_data_create()
        assert len(rig.data.bones)==50 and len(bpy.data.actions)==21
        key_counts={}
        for name in m.get('replaced_clips',[]):
            action=bpy.data.actions[name];expected=len(sample_times(float(action.frame_range[1])/24,m['walk_plan']['duration_s']))
            counts=[len(fc.keyframe_points) for l in action.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves]
            assert len(counts)==500 and all(n==expected for n in counts),'Dense native keys lost'
            key_counts[name]={'curves':len(counts),'keys_per_curve':expected}
        poses=[]
        for name in ['WalkWorld','StartWalk','StopWalk']:
            root.animation_data.action=None;root.matrix_basis=Matrix.Identity(4)
            rig.animation_data.action=bpy.data.actions[name]
            if rig.animation_data.action.slots:rig.animation_data.action_slot=rig.animation_data.action.slots[0]
            if name in ['WalkWorld','StartWalk','StopWalk']:
                root.animation_data.action=bpy.data.actions[name+'_Root']
                if root.animation_data.action.slots:root.animation_data.action_slot=root.animation_data.action.slots[0]
            duration=float(bpy.data.actions[name].frame_range[1])/24
            for phase in [0,1/560,.25,.5,.75,559/560,1]:
                t=phase*duration;f=t*24;bpy.context.scene.frame_set(int(f),subframe=f%1)
                scale=m['display_calibration']['scale'];offset=m['display_calibration']['offset_y']
                poses.append({'clip':name,'time_s':t,'body':[[v.x*scale,v.z*scale+offset,-v.y*scale] for v in vertices(body)]})
        (W/(m['asset_id']+'.json')).write_text(json.dumps(poses))
        reports.append({'asset_id':m['asset_id'],'model_sha256':m['model_sha256'],'mother_sha256':m['mother_sha256'],'bones':50,'editable_rig_actions':18,'paired_root_actions':3,'body_vertices':len(body.data.vertices),'native_scene_and_18_other_actions_preserved':suffix=='walk-smooth-review','dense_native_keys':key_counts,'cold_samples':len(poses),'offline_render':'not-rendered','human_art':'not-tested'})
(E/'blender-cold.json').write_text(json.dumps({'blender':bpy.app.version_string,'entries':reports},indent=2)+'\n');print('V14_COLD_SURFACES_PASS')
