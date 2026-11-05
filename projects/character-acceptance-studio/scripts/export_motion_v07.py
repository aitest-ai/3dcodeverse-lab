"""Motion-only export to a NEW file; strict native geometry/weights/rest/material guard."""
import bpy,sys,argparse,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import Capture
from v05.overlay import Overlay
from v07.overlay import ClipOverlay
from v06.geometry_guard import geometry_signature
p=argparse.ArgumentParser();p.add_argument('--character',choices=['vivi','vita'],required=True);p.add_argument('--mother');p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);ver='0.3.0' if a.character=='vivi' else '0.1.0';F=R/'library-v07'/('vroid-'+a.character+'-motion-review')/ver;meta=json.loads((F/'adaptation.json').read_text());dst=Path(a.output).resolve()
if dst.exists():raise RuntimeError('Refuse overwrite: choose a new candidate filename')
frozen=F/'model.blend'
if hashlib.sha256(frozen.read_bytes()).hexdigest()!=meta['mother_sha256']:raise RuntimeError('Frozen mother changed; restore and edit a separate copy')
bpy.ops.wm.open_mainfile(filepath=str(frozen));signature=geometry_signature()
if a.mother:
 bpy.ops.wm.open_mainfile(filepath=str(Path(a.mother).resolve()))
 if geometry_signature()!=signature:raise RuntimeError('Geometry/skin/rest/shapes/materials/textures changed: motion-only export refuses silently dropping these edits')
rig=bpy.data.objects['Armature'];root=bpy.data.objects['StudioRootMotion_v05'];original=R/meta['original_geometry'];capture=Capture(rig,original);overlay=ClipOverlay(R/meta['base_model']) if a.character=='vivi' else Overlay(original,{'rotation':[0,1,0,0]});clips=json.loads((F/'asset_manifest.json').read_text())['clips']
for name in clips:
 for ob in [rig,root]:
  for tr in ob.animation_data.nla_tracks:tr.mute=True
  action=bpy.data.actions[name if ob==rig else name+'_Root'];ob.animation_data.action=action
  if action.slots:ob.animation_data.action_slot=action.slots[0]
 N=round(rig.animation_data.action.frame_range[1]);frames=[]
 for i in range(N+1):bpy.context.scene.frame_set(i);frames.append(capture.frame(root.matrix_world))
 times=[i/bpy.context.scene.render.fps for i in range(N+1)]
 if a.character=='vivi':overlay.replace_clip(name,times,frames)
 else:overlay.animation(name,times,frames)
dst.parent.mkdir(parents=True,exist_ok=True);print(json.dumps({'file':str(dst),'sha256':overlay.save(dst),'status':'new candidate, new hash, requires browser and art review'}))
