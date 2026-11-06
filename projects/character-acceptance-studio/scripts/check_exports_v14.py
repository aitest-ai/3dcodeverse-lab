"""Cold re-export with independent curve interpolation and a destructive-edit counterexample."""
import bisect, hashlib, json, math, os, subprocess, sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v06.motion_overlay import MotionOverlay
W=R/'work/v14-export';W.mkdir(exist_ok=True);blender=os.environ.get('BLENDER_BIN','blender');reports=[]
def interpolate(times,values,t,rotation=False):
    i=max(0,min(len(times)-2,bisect.bisect_right(times,t)-1));u=(t-times[i])/(times[i+1]-times[i])
    a,b=values[i],values[i+1]
    if rotation:
        dot=sum(x*y for x,y in zip(a,b))
        if dot<0:b=[-x for x in b];dot=-dot
        if dot<.9995:
            angle=math.acos(max(-1,min(1,dot)));sa=math.sin((1-u)*angle)/math.sin(angle);sb=math.sin(u*angle)/math.sin(angle)
            return [sa*x+sb*y for x,y in zip(a,b)]
    out=[x*(1-u)+y*u for x,y in zip(a,b)]
    if rotation:
        length=math.sqrt(sum(x*x for x in out));out=[x/length for x in out]
    return out
for key in ['horse-brown','horse-white']:
    asset=key+'-walk-smooth-review';dst=W/(key+'.glb')
    subprocess.run([blender,'-b','-t','4','--python-exit-code','1','--python',str(R/'scripts/export_horses_v14.py'),'--','--id',asset,'--output',str(dst)],check=True,stdout=subprocess.DEVNULL)
    a=MotionOverlay(R/'library-v14'/asset/'0.1.0/model.glb');b=MotionOverlay(dst);maximum=0
    assert len(a.doc['animations'])==len(b.doc['animations'])==18
    for ca,cb in zip(a.doc['animations'],b.doc['animations']):
        assert ca['name']==cb['name']
        if ca['name'] not in ['WalkWorld','StartWalk','StopWalk']:assert ca==cb;continue
        for c,d in zip(ca['channels'],cb['channels']):
            assert c['target']==d['target'];x=ca['samplers'][c['sampler']];y=cb['samplers'][d['sampler']]
            ta=[v[0] for v in a.values(x['input'])];tb=[v[0] for v in b.values(y['input'])];va=a.values(x['output']);vb=b.values(y['output']);rotation=c['target']['path']=='rotation'
            for t,v in zip(tb,vb):
                ref=interpolate(ta,va,t,rotation);err=max(abs(u-w) for u,w in zip(ref,v))
                if rotation:err=min(err,max(abs(u+w) for u,w in zip(ref,v)))
                maximum=max(maximum,err)
    assert maximum<2e-5,maximum
    reports.append({'asset_id':asset,'reexport_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'maximum_curve_component_difference':maximum,'all_fifteen_other_clips':'exactly preserved'})
script=W/'edit.py';script.write_text("import bpy\nfrom pathlib import Path\nR=Path("+repr(str(R))+")\nbpy.ops.wm.open_mainfile(filepath=str(R/'library-v14/horse-brown-walk-smooth-review/0.1.0/model.blend'))\nbpy.data.objects['Horse'].data.vertices[0].co.x+=.01\nbpy.ops.wm.save_as_mainfile(filepath=str(R/'work/v14-export/edited.blend'))\n")
subprocess.run([blender,'-b','-t','4','--python-exit-code','1','--python',str(script)],check=True,stdout=subprocess.DEVNULL)
bad=W/'must-not-exist.glb';r=subprocess.run([blender,'-b','-t','4','--python-exit-code','1','--python',str(R/'scripts/export_horses_v14.py'),'--','--id','horse-brown-walk-smooth-review','--mother',str(W/'edited.blend'),'--output',str(bad)],capture_output=True,text=True)
assert r.returncode!=0 and not bad.exists() and 'Only three body motion edits supported' in r.stdout+r.stderr
root_script=W/'edit-root.py';root_script.write_text("import bpy\nfrom pathlib import Path\nR=Path("+repr(str(R))+")\nbpy.ops.wm.open_mainfile(filepath=str(R/'library-v14/horse-brown-walk-smooth-review/0.1.0/model.blend'))\na=bpy.data.actions['WalkWorld_Root']\nfc=next(fc for l in a.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves)\nfc.keyframe_points[0].co.y+=.1\nbpy.ops.wm.save_as_mainfile(filepath=str(R/'work/v14-export/root-edited.blend'))\n")
subprocess.run([blender,'-b','-t','4','--python-exit-code','1','--python',str(root_script)],check=True,stdout=subprocess.DEVNULL)
root_bad=W/'root-must-not-exist.glb';r=subprocess.run([blender,'-b','-t','4','--python-exit-code','1','--python',str(R/'scripts/export_horses_v14.py'),'--','--id','horse-brown-walk-smooth-review','--mother',str(W/'root-edited.blend'),'--output',str(root_bad)],capture_output=True,text=True)
assert r.returncode!=0 and not root_bad.exists() and 'Only three body motion edits supported' in r.stdout+r.stderr
(R/'evidence-v14/export-checks.json').write_text(json.dumps({'entries':reports,'changed_geometry_rejected':True,'changed_root_motion_rejected':True,'source_masters_unchanged':True},indent=2)+'\n');print('V14_EXPORT_AND_GUARD_PASS')
