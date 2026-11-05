"""Blender motion-only exporter; create a separate candidate, reject changed geometry and frozen originals."""
import bpy,sys,argparse,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import Capture
from v06.motion_overlay import MotionOverlay
from v06.geometry_guard import geometry_signature
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--mother');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);folder=R/'library-v06/vroid-vivi-motion-review/0.2.0';meta=json.loads((folder/'adaptation.json').read_text());dest=Path(a.output).resolve()
if dest.exists():raise RuntimeError('Refuse overwrite: choose a new candidate filename')
frozen=folder/'model.blend'
if hashlib.sha256(frozen.read_bytes()).hexdigest()!=meta['mother_sha256']:raise RuntimeError('Frozen mother changed; restore it and edit a separate --mother copy')
bpy.ops.wm.open_mainfile(filepath=str(frozen));expected=geometry_signature()
if a.mother:
 bpy.ops.wm.open_mainfile(filepath=str(Path(a.mother).resolve()))
 if geometry_signature()!=expected:raise RuntimeError('Geometry/skin/rest/shapes/materials/textures changed. Motion-only export refuses silently discarding these edits; use a new geometry version/export pipeline.')
rig=bpy.data.objects['Armature'];root=bpy.data.objects['StudioRootMotion_v05'];capture=Capture(rig,R/meta['original_geometry']);overlay=MotionOverlay(R/meta['base_model'])
for name in meta['clips']:
 for ob in [rig,root]:
  for tr in ob.animation_data.nla_tracks:tr.mute=True
  action=bpy.data.actions[name if ob==rig else name+'_Root'];ob.animation_data.action=action
  if action.slots:ob.animation_data.action_slot=action.slots[0]
 N=round(rig.animation_data.action.frame_range[1]);frames=[]
 for i in range(N+1):bpy.context.scene.frame_set(i);frames.append(capture.frame(root.matrix_world))
 overlay.patch(name,frames,set(capture.map)|{capture.wrapper})
dest.parent.mkdir(parents=True,exist_ok=True);print(json.dumps({'file':str(dest),'sha256':overlay.save(dest),'status':'new candidate; not registered; requires new visual acceptance'}))
