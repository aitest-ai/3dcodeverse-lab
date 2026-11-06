"""Export edited new transitions; immutable v12 scene and all 14 clips retained."""
import argparse, bpy, hashlib, json, sys
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import Capture
from v07.overlay import ClipOverlay
from v06.geometry_guard import geometry_signature
p=argparse.ArgumentParser();p.add_argument('--id',choices=['horse-brown-walk-transition-review','horse-white-walk-transition-review'],required=True);p.add_argument('--mother');p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);F=R/'library-v13'/a.id/'0.1.0';m=json.loads((F/'adaptation.json').read_text());dst=Path(a.output).resolve();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if dst.exists():raise RuntimeError('Refuse overwriting export')
assert sha(F/'model.blend')==m['mother_sha256'] and sha(R/m['source_glb'])==m['source_glb_sha256']
allowed=m['added_clips']+['StartWalk_Root','StopWalk_Root']
def guard():
    actions={a.name:hashlib.sha256(json.dumps([(fc.data_path,fc.array_index,[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in fc.keyframe_points]) for l in a.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves],sort_keys=True).encode()).hexdigest() for a in bpy.data.actions if a.name not in allowed}
    parents={o.name:(o.parent.name if o.parent else None,list(o.matrix_basis),list(o.matrix_parent_inverse)) for o in bpy.data.objects if o.type in ['ARMATURE','MESH']}
    return geometry_signature(),actions,json.dumps(parents,sort_keys=True,default=list)
bpy.ops.wm.open_mainfile(filepath=str(F/'model.blend'));before=guard()
if a.mother:
    bpy.ops.wm.open_mainfile(filepath=str(Path(a.mother).resolve()))
    if guard()!=before:raise RuntimeError('Only new transition motion edits supported; original actions, geometry, rest, weights, textures, transforms or parents changed')
rig=bpy.data.objects['AnimalArmature'];root=bpy.data.objects['StudioTravelRoot_v11']
assert root.parent is None and bpy.context.scene.render.fps==24 and bpy.context.scene.render.fps_base==1
capture=Capture(rig,R/m['source_glb']);overlay=ClipOverlay(R/m['source_glb']);root_index=next(i for i,n in enumerate(overlay.doc['nodes']) if n.get('name')=='StudioTravelRoot_v11')
for name in m['added_clips']:
    root.animation_data.action=None;root.matrix_basis=Matrix.Identity(4)
    rig.animation_data.action=bpy.data.actions[name]
    if rig.animation_data.action.slots:rig.animation_data.action_slot=rig.animation_data.action.slots[0]
    if name in ['StartWalk','StopWalk']:
        root.animation_data.action=bpy.data.actions[name+'_Root']
        if root.animation_data.action.slots:root.animation_data.action_slot=root.animation_data.action.slots[0]
    duration=float(bpy.data.actions[name].frame_range[1])/24;N=round(duration*120)
    if N<1:raise RuntimeError('Transition duration must be positive')
    frames=[];times=[duration*i/N for i in range(N+1)]
    for t in times:
        f=t*24;bpy.context.scene.frame_set(int(f),subframe=f%1);row=capture.frame(root.matrix_world);row[root_index]=row.pop(capture.wrapper);frames.append(row)
    overlay.replace_clip(name,times,frames)
dst.parent.mkdir(parents=True,exist_ok=True);model_sha=overlay.save(dst)
print(json.dumps({'output':str(dst),'sha256':model_sha,'status':'new unreviewed motion export; regenerate schedule/root plan and recheck joins/contacts before use'}))
