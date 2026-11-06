import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from export_arms_v17 import export
F=R/'library-v17/vroid-vivi-motion-review/0.5.0/model.blend';W=R/'work/v17';rows=[]
positive=export('vivi',F,W/'guard-positive.glb')
for test in ['geometry','uv','other-motion','modifier','shape-driver','shape-channel']:
 bpy.ops.wm.open_mainfile(filepath=str(F))
 if test=='geometry':bpy.data.objects['Body'].data.vertices[0].co.x+=.001
 elif test=='uv':bpy.data.objects['Body'].data.uv_layers[0].data[0].uv.x+=.01
 elif test=='shape-driver':bpy.data.objects['Body'].data.shape_keys.key_blocks['Run_ElbowSleeveCorrective'].driver_add('value')
 elif test=='shape-channel':
  from v17.sleeves import ACTION
  a=bpy.data.actions[ACTION];a.layers[0].strips[0].channelbags[0].fcurves[0].data_path='eval_time'
 elif test=='modifier':bpy.data.objects['Body'].modifiers.new('unsupported-test','SOLIDIFY')
 else:
  action=bpy.data.actions['Walk'];fc=action.layers[0].strips[0].channelbags[0].fcurves[0];fc.keyframe_points[0].co.y+=.01;fc.update()
 src=W/(test+'-guard.blend');bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);out=W/(test+'-must-not-export.glb')
 try:export('vivi',src,out)
 except RuntimeError as e:rows.append({'case':test,'rejected':True,'reason':str(e)})
 else:raise AssertionError('Unsafe export accepted '+test)
 assert not out.exists();src.unlink()
bpy.ops.wm.open_mainfile(filepath=str(F))
body=bpy.data.objects['Body'];body.data.shape_keys.key_blocks['Run_ElbowSleeveCorrective'].data[0].co.x+=.001
src=W/'corrective-edit.blend';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);edited=export('vivi',src,W/'corrective-edit.glb');assert edited['sha256']!=positive['sha256'];src.unlink()
from v06.motion_overlay import MotionOverlay
a=MotionOverlay(W/'guard-positive.glb');b=MotionOverlay(W/'corrective-edit.glb');delta=a.values(a.doc['meshes'][1]['primitives'][0]['targets'][0]['POSITION']);changed=b.values(b.doc['meshes'][1]['primitives'][0]['targets'][0]['POSITION']);assert abs(changed[0][0]-delta[0][0]-.001)<1e-7
rows.append({'case':'editable-corrective','exported':True,'edited_delta_verified':True,'receipt':edited})
(R/'evidence-v17/export-guard.json').write_text(json.dumps({'positive_export':positive,'entries':rows},indent=2)+'\n');print('V17_NEGATIVE_EXPORT_GUARDS_PASS')
