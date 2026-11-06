"""Export only the three new rig/root action pairs; preserve all original motion and scene."""
import argparse,bpy,hashlib,json,sys
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import Capture,read
from v07.overlay import ClipOverlay
from v14.smoothing import sample_times
from v06.geometry_guard import geometry_signature
p=argparse.ArgumentParser();p.add_argument('--id',choices=['horse-brown-locomotion-review','horse-white-locomotion-review'],required=True);p.add_argument('--mother');p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);F=R/'library-v15'/a.id/'0.1.0';m=json.loads((F/'adaptation.json').read_text());dst=Path(a.output).resolve();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if dst.exists():raise RuntimeError('Refuse overwriting export')
assert sha(F/'model.blend')==m['mother_sha256'] and sha(R/m['source_glb'])==m['source_glb_sha256']
allowed=m['added_clips'];allowed_actions=allowed+[n+'_Root' for n in allowed]
def guard():
    actions={a.name:hashlib.sha256(json.dumps([(fc.data_path,fc.array_index,[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in fc.keyframe_points]) for l in a.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves],sort_keys=True).encode()).hexdigest() for a in bpy.data.actions if a.name not in allowed_actions}
    parents={o.name:(o.parent.name if o.parent else None,list(o.matrix_basis),list(o.matrix_parent_inverse)) for o in bpy.data.objects if o.type in ['ARMATURE','MESH']}
    return geometry_signature(),actions,json.dumps(parents,sort_keys=True,default=list)
bpy.ops.wm.open_mainfile(filepath=str(F/'model.blend'));before=guard()
if a.mother:
    bpy.ops.wm.open_mainfile(filepath=str(Path(a.mother).resolve()))
    if guard()!=before:raise RuntimeError('Only three new rig/root pairs may change; original motion, geometry, rest, weights, textures, transforms or parents changed')
rig=bpy.data.objects['AnimalArmature'];root=bpy.data.objects['StudioTravelRoot_v11']
assert root.parent is None and bpy.context.scene.render.fps==24 and bpy.context.scene.render.fps_base==1
root.animation_data_create();root.animation_data.action=None;root.matrix_basis=Matrix.Identity(4)
capture=Capture(rig,R/m['source_glb']);overlay=ClipOverlay(R/m['source_glb']);T=m['walk_plan']['duration_s'];root_index=next(i for i,n in enumerate(capture.doc['nodes']) if n.get('name')=='StudioTravelRoot_v11')
for name in allowed:
    rig.animation_data.action=bpy.data.actions[name]
    if rig.animation_data.action.slots:rig.animation_data.action_slot=rig.animation_data.action.slots[0]
    root.animation_data.action=bpy.data.actions[name+'_Root']
    if root.animation_data.action.slots:root.animation_data.action_slot=root.animation_data.action.slots[0]
    duration=m['locomotion']['clips'][name]['duration']
    assert abs(float(bpy.data.actions[name].frame_range[1])/24-duration)<1e-6,'Duration edits require a new root/contact plan'
    frames=[];times=sample_times(duration,T)
    for t in times:
        f=t*24;bpy.context.scene.frame_set(int(f),subframe=f%1);row=capture.frame(root.matrix_basis.copy());row[root_index]=row.pop(capture.wrapper);frames.append(row)
    overlay.replace_clip(name,times,frames)
dst.parent.mkdir(parents=True,exist_ok=True);model_sha=overlay.save(dst)
print(json.dumps({'output':str(dst),'sha256':model_sha,'status':'unreviewed new locomotion export; repeat contact, seam and visual checks before use'}))
