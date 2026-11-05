"""Blender: --python this.py -- --asset <id> --output <NEW.glb>. Preserves the original skin/material/VRM BIN prefix."""
import bpy,sys,argparse,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import Capture
from v05.overlay import Overlay
p=argparse.ArgumentParser();p.add_argument('--asset',required=True);p.add_argument('--output',required=True);p.add_argument('--mother');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);folder=R/'library-v05'/a.asset/'0.1.0';meta=json.loads((folder/'adaptation.json').read_text());dest=Path(a.output).resolve()
if dest.exists():raise RuntimeError('Refuse overwrite: choose a new candidate filename')
def geometry_signature():
 def val(x):
  if isinstance(x,(str,int,float,bool)) or x is None:return x
  try:return list(x)
  except TypeError:return str(type(x))
 data={'meshes':[],'rigs':[],'materials':[],'images':[]}
 for o in sorted(bpy.data.objects,key=lambda o:o.name):
  if o.type=='MESH':data['meshes'].append({'name':o.name,'matrix':list(o.matrix_basis),'vertices':[list(v.co) for v in o.data.vertices],'faces':[(list(p.vertices),p.material_index) for p in o.data.polygons],'groups':[g.name for g in o.vertex_groups],'weights':[[(g.group,g.weight) for g in v.groups] for v in o.data.vertices],'shapes':{k.name:[list(v.co) for v in k.data] for k in o.data.shape_keys.key_blocks} if o.data.shape_keys else {},'materials':[m.name if m else None for m in o.data.materials]})
  if o.type=='ARMATURE':data['rigs'].append([(b.name,b.parent.name if b.parent else None,[list(r) for r in b.matrix_local],list(b.tail_local)) for b in o.data.bones])
 for m in sorted(bpy.data.materials,key=lambda m:m.name):
  nodes=[];links=[]
  if m.node_tree:
   nodes=[(n.name,n.type,[(i.name,val(i.default_value)) for i in n.inputs if hasattr(i,'default_value')],getattr(getattr(n,'image',None),'name',None)) for n in m.node_tree.nodes];links=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]
  data['materials'].append((m.name,list(m.diffuse_color),nodes,links))
 for im in sorted(bpy.data.images,key=lambda im:im.name):data['images'].append((im.name,None if im.packed_file else bpy.path.abspath(im.filepath),hashlib.sha256(im.packed_file.data).hexdigest() if im.packed_file else None))
 # matrix rows are mathutils.Vector; convert recursively via JSON default.
 return hashlib.sha256(json.dumps(data,sort_keys=True,default=lambda x:list(x)).encode()).hexdigest()
original=R/meta['target_source'];frozen=folder/'model.blend';locked=next(f['sha256'] for f in json.loads((folder/'files.json').read_text())['files'] if f['file']=='model.blend')
if hashlib.sha256(frozen.read_bytes()).hexdigest()!=locked:raise RuntimeError('Frozen mother changed. Restore it and use --mother with a separate edited copy.')
bpy.ops.wm.open_mainfile(filepath=str(frozen));expected=geometry_signature()
if a.mother:
 bpy.ops.wm.open_mainfile(filepath=str(Path(a.mother).resolve()))
 if geometry_signature()!=expected:raise RuntimeError('Geometry, skin, rest rig, shape keys, images or materials changed. This exporter only updates motion; create a new geometry-export pipeline/version instead of silently dropping these edits.')
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');root=bpy.data.objects['StudioRootMotion_v05'];capture=Capture(rig,original);overlay=Overlay(original,{})
clips=list(json.loads((folder/'motion-audit.json').read_text())['clips'])
for name in clips:
 for ob in [rig,root]:
  for tr in ob.animation_data.nla_tracks:tr.mute=True
  action=bpy.data.actions[name if ob==rig else name+'_Root'];ob.animation_data.action=action
  if action.slots:ob.animation_data.action_slot=action.slots[0]
 N=round(rig.animation_data.action.frame_range[1]);frames=[]
 for i in range(N+1):bpy.context.scene.frame_set(i);frames.append(capture.frame(root.matrix_world))
 overlay.animation(name,[i/bpy.context.scene.render.fps for i in range(N+1)],frames)
# Static fallback uses first Idle root pose. Unchanged source-only animal clips receive the calibrated scale.
for ob in [rig,root]:
 action=bpy.data.actions['Idle' if ob==rig else 'Idle_Root'];ob.animation_data.action=action
 if action.slots:ob.animation_data.action_slot=action.slots[0]
bpy.context.scene.frame_set(0);overlay.doc['nodes'][overlay.wrapper].update(capture.frame(root.matrix_world)[overlay.wrapper]);dest.parent.mkdir(parents=True,exist_ok=True);sha=overlay.save(dest);print(json.dumps({'file':str(dest),'sha256':sha,'status':'new candidate; not registered; requires browser/art recheck'}))
