"""Re-export edited WalkWorld only; immutable source clips/geometry/rest retained, new SHA required."""
import bpy,sys,json,argparse,hashlib
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import Capture
from v05.overlay import Overlay
from v06.geometry_guard import geometry_signature
p=argparse.ArgumentParser();p.add_argument('--id',choices=['horse-brown-walk-world-review','horse-white-walk-world-review'],required=True);p.add_argument('--mother');p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);F=R/'library-v11'/a.id/'0.1.0';m=json.loads((F/'adaptation.json').read_text());dst=Path(a.output).resolve();h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if dst.exists():raise RuntimeError('Refuse overwriting export')
assert h(F/'model.blend')==m['mother_sha256'] and h(R/m['source_glb'])==m['source_glb_sha256'];bpy.ops.wm.open_mainfile(filepath=str(F/'model.blend'))
def guard():
 actions={a.name:hashlib.sha256(json.dumps([(fc.data_path,fc.array_index,[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in fc.keyframe_points]) for l in a.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves],sort_keys=True).encode()).hexdigest() for a in bpy.data.actions if a.name not in ['WalkWorld','WalkWorld_Root']}
 parents={o.name:(o.parent.name if o.parent else None,list(o.matrix_basis),list(o.matrix_parent_inverse)) for o in bpy.data.objects if o.type in ['ARMATURE','MESH']}
 return geometry_signature(),actions,json.dumps(parents,sort_keys=True,default=list)
before=guard()
if a.mother:
 bpy.ops.wm.open_mainfile(filepath=str(Path(a.mother).resolve()))
 if guard()!=before:raise RuntimeError('Only WalkWorld/root motion edits supported; other actions, geometry, rest, weights, textures, object transforms or parents changed')
rig=bpy.data.objects['AnimalArmature'];root=bpy.data.objects['StudioTravelRoot_v11'];assert root.parent is None and bpy.context.scene.render.fps==24 and bpy.context.scene.render.fps_base==1
for ob,name in [(rig,'WalkWorld'),(root,'WalkWorld_Root')]:
 ob.animation_data.action=bpy.data.actions[name]
 if ob.animation_data.action.slots:ob.animation_data.action_slot=ob.animation_data.action.slots[0]
T=float(bpy.data.actions['WalkWorld'].frame_range[1])/24;N=round(T*120);capture=Capture(rig,R/m['source_glb']);overlay=Overlay(R/m['source_glb'],{});overlay.doc['nodes'][overlay.wrapper]['name']='StudioTravelRoot_v11';frames=[]
for i in range(N+1):
 f=T*i/N*24;bpy.context.scene.frame_set(int(f),subframe=f%1);frames.append(capture.frame(root.matrix_world))
overlay.animation('WalkWorld',[T*i/N for i in range(N+1)],frames);dst.parent.mkdir(parents=True,exist_ok=True);sha=overlay.save(dst);print(json.dumps({'output':str(dst),'sha256':sha,'status':'new unreviewed motion export; recheck root speed/phase/contacts before use'}))
