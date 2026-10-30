"""Offline fixture -> existing real V17 rig -> Blender -> GLB -> fresh reimport.
No API key or user video is read by this test. All outputs are explicitly synthetic.
"""
import argparse,json,subprocess,sys
from pathlib import Path
from pose_io import sha256

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--blender',default='blender');a=p.parse_args()
    scripts=Path(__file__).resolve().parent
    sources={p.name:p for p in a.input.rglob('*.glb')}
    cases=[('boss','boss_v17_ponytail01.glb','in-place'),('jie','jie_v17_main.glb','keep')]
    results=[]
    for name,filename,root_mode in cases:
        if filename not in sources:raise FileNotFoundError(filename)
        source=sources[filename];before=sha256(source);out=a.output/name
        subprocess.run([a.blender,'-b','--factory-startup','--python-exit-code','1','--python',str(scripts/'retarget_blender.py'),'--','--asset',str(source.resolve()),'--output',str(out.resolve()),'--fixture','--root-motion',root_mode,'--render'],check=True)
        subprocess.run([a.blender,'-b','--factory-startup','--python-exit-code','1','--python',str(scripts/'verify_blender.py'),'--',str((out/'report.json').resolve())],check=True)
        # Preserve the detailed accessor audit before running the repository's own gate.
        (out/'pose_validation.json').write_text((out/'validation.json').read_text())
        validator=scripts.parent/'blender5'/'validate_glb.py'
        subprocess.run([sys.executable,str(validator),str(out)],check=True)
        assert sha256(source)==before
        r=json.loads((out/'report.json').read_text());v=json.loads((out/'roundtrip.json').read_text())
        results.append({'character':name,'status':r['status'],'bones':r['source_bones'],'mapped_rotation_bones':len(r['rotation_mapped_bones']),'frames':r['frames'],'root_mode':root_mode,'left_hand_relative_displacement_m':r['left_hand_relative_displacement_m'],'right_hand_relative_displacement_m':r['right_hand_relative_displacement_m'],'root_displacement_m':r['root_displacement_m'],'roundtrip':v,'glb':str(Path(name)/r['glb'])})
    summary={'status':'SYNTHETIC_RETARGET_INTEGRATION_PASS','live_nvidia_inference':False,'video_to_pose_verified':False,'art_approved':False,'characters':results,'limitations':['No real video/API key supplied','Position-based retarget only; full local quaternion/twist solve deferred','Foot contact and clothing QA pending','Three.js/Unity runtime playback not tested']}
    (a.output/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
