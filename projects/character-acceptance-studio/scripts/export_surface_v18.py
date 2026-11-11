"""Export a packed local outline mask; refuse unsupported edits."""
import bpy,sys,argparse,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v06.motion_overlay import MotionOverlay
from v18.outline import append as mask_append,MASK_NAME
from v18.native_guard import state_signature

def export(key,mother,dst):
 folder=R/'library-v18'/('vroid-'+key+'-motion-review')/({'vivi':'0.6.0','vita':'0.5.0'}[key]);meta=json.loads((folder/'adaptation.json').read_text())
 if dst.exists():raise RuntimeError('Refuse overwrite '+str(dst))
 bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'));bpy.context.scene.frame_set(0);signature=state_signature()
 if mother:
  bpy.ops.wm.open_mainfile(filepath=str(mother));bpy.context.scene.frame_set(0)
  if state_signature()!=signature:raise RuntimeError('Only the packed outline mask is supported. Original geometry, rig, weights, UVs, other images, materials, setup and animation must remain unchanged.')
 im=bpy.data.images[MASK_NAME]
 if not im.packed_file or im.is_dirty or tuple(im.size)!=(2048,2048) or im.colorspace_settings.name!='Non-Color' or not bytes(im.packed_file.data).startswith(b'\x89PNG\r\n\x1a\n'):raise RuntimeError('Pack/save a 2048px PNG mask with Non-Color interpretation before export')
 o=MotionOverlay(R/meta['base_model']);mask_append(o,bytes(im.packed_file.data));dst.parent.mkdir(parents=True,exist_ok=True);sha=o.save(dst);return {'file':str(dst),'sha256':sha,'art_approved':False,'game_ready':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--character',choices=['vivi','vita'],required=True);p.add_argument('--mother',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);print(json.dumps(export(a.character,a.mother,a.output.resolve())))
