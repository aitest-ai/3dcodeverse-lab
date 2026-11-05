"""Motion-only Shiba export into a new file. Geometry/rest/material edits must use a separate geometry export workflow."""
import bpy,sys,argparse,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import Capture
from v07.overlay import ClipOverlay
from v06.geometry_guard import geometry_signature
p=argparse.ArgumentParser();p.add_argument('--mother');p.add_argument('--variant',choices=['model','baseline'],default='model');p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);F=R/'library-v09/quaternius-shibainu-grounded-review/0.2.0';meta=json.loads((F/'adaptation.json').read_text());dst=Path(a.output).resolve()
if dst.exists():raise RuntimeError('Refuse overwrite: choose a new candidate filename')
frozen=F/(a.variant+'.blend');expected=meta['mother_sha256' if a.variant=='model' else 'baseline_mother_sha256']
if hashlib.sha256(frozen.read_bytes()).hexdigest()!=expected:raise RuntimeError('Frozen mother changed; restore and edit a separate copy')
bpy.ops.wm.open_mainfile(filepath=str(frozen));signature=geometry_signature()
if a.mother:
 bpy.ops.wm.open_mainfile(filepath=str(Path(a.mother).resolve()))
 if geometry_signature()!=signature:raise RuntimeError('Geometry/skin/rest/shapes/materials/textures changed: motion-only export refuses silently dropping these edits')
rig=bpy.data.objects['AnimalArmature'];root=bpy.data.objects['StudioRootMotion_v05'];capture=Capture(rig,R/meta['target_source']);overlay=ClipOverlay(R/meta['base_model'])
for name in ['Idle','Walk','Gallop','WalkTurnLeft','WalkTurnRight']:
 for o in [rig,root]:
  for tr in o.animation_data.nla_tracks:tr.mute=True
  action=bpy.data.actions[name if o==rig else name+'_Root'];o.animation_data.action=action
  if action.slots:o.animation_data.action_slot=action.slots[0]
 N=round(rig.animation_data.action.frame_range[1]);frames=[]
 for i in range(N+1):bpy.context.scene.frame_set(i);frames.append(capture.frame(root.matrix_world))
 overlay.replace_clip(name,[i/60 for i in range(N+1)],frames)
dst.parent.mkdir(parents=True,exist_ok=True);print(json.dumps({'file':str(dst),'sha256':overlay.save(dst),'status':'new motion candidate; new hash, requires browser and art review; other nine source clips unchanged'}))
