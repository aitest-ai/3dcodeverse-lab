"""Cold-open verified editable horse; re-export Walk/Gallop into a new candidate, preserving other clips."""
import bpy,sys,json,argparse,hashlib
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.blender_utils import Capture
from v07.overlay import ClipOverlay
from v06.geometry_guard import geometry_signature
p=argparse.ArgumentParser();p.add_argument('--id',choices=['horse-brown-grounded-review','horse-white-grounded-review'],required=True);p.add_argument('--mother');p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);F=R/'library-v10'/a.id/'0.1.0';meta=json.loads((F/'adaptation.json').read_text());dst=Path(a.output).resolve();h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if dst.exists():raise RuntimeError('Refuse overwriting existing export')
assert h(F/'model.blend')==meta['mother_sha256'];assert h(R/meta['source_glb'])==meta['source_glb_sha256'];bpy.ops.wm.open_mainfile(filepath=str(F/'model.blend'));guard=geometry_signature()
def action_signatures():
 return {x.name:hashlib.sha256(json.dumps([(fc.data_path,fc.array_index,[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in fc.keyframe_points]) for l in x.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves],sort_keys=True).encode()).hexdigest() for x in bpy.data.actions if x.name not in ['Walk','Gallop']}
untouched=action_signatures()
if a.mother:
 bpy.ops.wm.open_mainfile(filepath=str(Path(a.mother).resolve()))
 if action_signatures()!=untouched:raise RuntimeError('This exporter handles Walk/Gallop only; other native action edits require a separate clip export')
 if geometry_signature()!=guard:raise RuntimeError('Geometry/weights/rest/material/texture edits require full geometry export; refusing motion-only export')
rig=bpy.data.objects['AnimalArmature'];assert bpy.context.scene.render.fps==24 and max(abs(rig.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-6,'Native FPS/rig transform changed; separate export required';capture=Capture(rig,R/meta['source_glb']);overlay=ClipOverlay(R/meta['source_glb'])
for name in ['Walk','Gallop']:
 rig.animation_data.action=bpy.data.actions[name]
 if rig.animation_data.action.slots:rig.animation_data.action_slot=rig.animation_data.action.slots[0]
 duration=float(rig.animation_data.action.frame_range[1])/24;n=round(duration*120);frames=[]
 for i in range(n+1):
  f=duration*i/n*24;bpy.context.scene.frame_set(int(f),subframe=f%1);row=capture.frame(Matrix.Identity(4));row.pop(capture.wrapper);frames.append(row)
 overlay.replace_clip(name,[duration*i/n for i in range(n+1)],frames)
dst.parent.mkdir(parents=True,exist_ok=True);sha=overlay.save(dst);print(json.dumps({'sha256':sha,'output':str(dst),'status':'new motion export; independently verify browser/contacts; source other eleven clips retained'}))
