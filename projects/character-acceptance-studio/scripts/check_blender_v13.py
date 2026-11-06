"""Cold native mothers, paired travel actions and evaluated surface probes."""
import bpy, hashlib, json, os, sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import vertices
from mathutils import Matrix
W=R/'work/v13-cold';W.mkdir(parents=True,exist_ok=True);E=R/'evidence-v13';E.mkdir(exist_ok=True);reports=[]
for key in ['horse-brown','horse-white']:
    if os.environ.get('STUDIO_HORSE') and os.environ['STUDIO_HORSE']!=key:continue
    for suffix in ['transition-baseline','walk-transition-review']:
        F=R/'library-v13'/(key+'-'+suffix)/'0.1.0';m=json.loads((F/'adaptation.json').read_text())
        assert hashlib.sha256((F/'model.blend').read_bytes()).hexdigest()==m['mother_sha256']
        bpy.ops.wm.open_mainfile(filepath=str(F/'model.blend'))
        rig=bpy.data.objects['AnimalArmature'];root=bpy.data.objects['StudioTravelRoot_v11'];body=bpy.data.objects['Horse']
        assert len(rig.data.bones)==50 and len(bpy.data.actions)==21
        poses=[]
        for name in m['added_clips']:
            root.animation_data.action=None;root.matrix_basis=Matrix.Identity(4)
            rig.animation_data.action=bpy.data.actions[name]
            if rig.animation_data.action.slots:rig.animation_data.action_slot=rig.animation_data.action.slots[0]
            if name in ['StartWalk','StopWalk']:
                root.animation_data.action=bpy.data.actions[name+'_Root']
                if root.animation_data.action.slots:root.animation_data.action_slot=root.animation_data.action.slots[0]
            duration=float(bpy.data.actions[name].frame_range[1])/24
            for phase in ([0,.25,.5,.75,1] if name in ['StartWalk','StopWalk'] else [0,1]):
                t=phase*duration;f=t*24;bpy.context.scene.frame_set(int(f),subframe=f%1)
                scale=m['display_calibration']['scale'];offset=m['display_calibration']['offset_y']
                poses.append({'clip':name,'time_s':t,'body':[[v.x*scale,v.z*scale+offset,-v.y*scale] for v in vertices(body)]})
        (W/(m['asset_id']+'.json')).write_text(json.dumps(poses))
        reports.append({'asset_id':m['asset_id'],'model_sha256':m['model_sha256'],'mother_sha256':m['mother_sha256'],'bones':50,'editable_rig_actions':18,'paired_root_actions':3,'body_vertices':len(body.data.vertices),'cold_samples':len(poses),'offline_render':'not-rendered','human_art':'not-tested'})
(E/'blender-cold.json').write_text(json.dumps({'blender':bpy.app.version_string,'entries':reports},indent=2)+'\n');print('V13_COLD_SURFACES_PASS')
