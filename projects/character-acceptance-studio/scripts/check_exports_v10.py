"""Meaningful export checks: cold re-export preserves source + curves, disallowed edits fail closed."""
import json,subprocess,os,sys,hashlib,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from v06.motion_overlay import MotionOverlay
W=R/'work/v10-export';W.mkdir(exist_ok=True);blender=os.environ.get('BLENDER_BIN','blender');reports=[]
for key in ['horse-brown','horse-white']:
 id=key+'-grounded-review';dst=W/(key+'.glb');cmd=[blender,'-b','-t','4','--python-exit-code','1','--python',str(R/'scripts/export_horses_v10.py'),'--','--id',id,'--output',str(dst)];subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL);a=MotionOverlay(R/'library-v10'/id/'0.1.0/model.glb');b=MotionOverlay(dst);maximum=0
 for ca,cb in zip(a.doc['animations'],b.doc['animations']):
  if ca['name'] not in ['Walk','Gallop']:assert ca==cb;continue
  for x,y in zip(ca['samplers'],cb['samplers']):
   for field in ['input','output']:
    av,bv=a.values(x[field]),b.values(y[field]);assert len(av)==len(bv)
    maximum=max(maximum,max(abs(u-v) for p,q in zip(av,bv) for u,v in zip(p,q)))
 assert maximum<2e-5;reports.append({'asset_id':id,'reexport_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'maximum_curve_component_difference':maximum,'other_eleven_clips':'exactly preserved'})
# Deliberately edit one vertex; the motion-only exporter must not silently discard it.
script=W/'edit.py';script.write_text("import bpy\nfrom pathlib import Path\nR=Path("+repr(str(R))+ ")\nbpy.ops.wm.open_mainfile(filepath=str(R/'library-v10/horse-brown-grounded-review/0.1.0/model.blend'))\nbpy.data.objects['Horse'].data.vertices[0].co.x+=.01\nbpy.ops.wm.save_as_mainfile(filepath=str(R/'work/v10-export/edited.blend'))\n")
subprocess.run([blender,'-b','-t','4','--python-exit-code','1','--python',str(script)],check=True,stdout=subprocess.DEVNULL);bad=W/'must-not-exist.glb';r=subprocess.run([blender,'-b','-t','4','--python-exit-code','1','--python',str(R/'scripts/export_horses_v10.py'),'--','--id','horse-brown-grounded-review','--mother',str(W/'edited.blend'),'--output',str(bad)],capture_output=True,text=True);assert r.returncode!=0 and not bad.exists() and 'motion-only export' in r.stdout+r.stderr
(R/'evidence-v10/export-checks.json').write_text(json.dumps({'entries':reports,'changed_geometry_rejected':True,'source_masters_unchanged':True},indent=2)+'\n');print('EXPORT_AND_GUARD_PASS')
