#!/usr/bin/env python3
"""Build both gray candidates and validate them using a pinned bootstrap state."""
import argparse, json, os, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runtime',type=Path,default=Path('runtime'))
    p.add_argument('--outputs',type=Path,required=True)
    args=p.parse_args()
    state=json.loads((args.runtime/'bootstrap_state.json').read_text())
    if state.get('status')!='RUNTIME_READY_NOT_CHARACTER_APPROVAL':raise SystemExit('Run bootstrap.py first')
    out=args.outputs.resolve()
    if out.exists():raise SystemExit('Choose a new versioned outputs directory; existing output is preserved')
    out.mkdir(parents=True)
    env=os.environ.copy()
    for key in ('BLENDER_USER_CONFIG','BLENDER_USER_EXTENSIONS'):
        env[key]=state['environment'][key]
    if not env.get('GITHUB_SHA'):
        rev=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,capture_output=True)
        env['GITHUB_SHA']=rev.stdout.strip() if rev.returncode==0 else 'source-archive'
    blender=state['environment']['BLENDER_BIN'];assets=state['environment']['CHARACTER_STUDIO_ASSETS']
    def run(command):subprocess.run(command,cwd=ROOT,env=env,check=True)
    for cid in ('d03','d06'):
        folder=out/cid
        run([blender,'-b','--python-exit-code','1','--python','scripts/character_studio/build_gray.py','--',
             '--character',cid,'--assets',assets,'--out',str(folder)])
        run([sys.executable,'scripts/character_studio/inspect_glb.py',str(folder/(cid+'.glb')),'--out',str(folder/'glb_inspection.json')])
        run([sys.executable,'scripts/blender5/validate_glb.py',str(folder)])
    run([blender,'-b','--python-exit-code','1','--python','scripts/character_studio/compare_gray.py','--',
         '--d03',str(out/'d03/d03.blend'),'--d06',str(out/'d06/d06.blend'),'--out',str(out/'comparison.json')])
    print('GRAY_CANDIDATES_READY_FOR_VISUAL_REVIEW',out)
if __name__=='__main__':main()
