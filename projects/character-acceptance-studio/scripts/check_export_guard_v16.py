import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from export_hands_v16 import export
F=R/'library-v16/vroid-vivi-motion-review/0.4.0/model.blend';W=R/'work/v16';rows=[]
positive=export('vivi',F,W/'guard-positive.glb')
for test in ['geometry','other-motion','modifier']:
 bpy.ops.wm.open_mainfile(filepath=str(F))
 if test=='geometry':bpy.data.objects['Body'].data.vertices[0].co.x+=.001
 elif test=='modifier':bpy.data.objects['Body'].modifiers.new('unsupported-test','SOLIDIFY')
 else:
  action=bpy.data.actions['Walk'];fc=action.layers[0].strips[0].channelbags[0].fcurves[0];fc.keyframe_points[0].co.y+=.01;fc.update()
 src=W/(test+'-guard.blend');bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);out=W/(test+'-must-not-export.glb')
 try:export('vivi',src,out)
 except RuntimeError as e:rows.append({'case':test,'rejected':True,'reason':str(e)})
 else:raise AssertionError('Unsafe export accepted '+test)
 assert not out.exists();src.unlink()
(R/'evidence-v16/export-guard.json').write_text(json.dumps({'positive_export':positive,'entries':rows},indent=2)+'\n');print('V16_NEGATIVE_EXPORT_GUARDS_PASS')
