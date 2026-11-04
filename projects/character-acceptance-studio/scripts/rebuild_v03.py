"""Portable two-character rebuild. Each Blender runs in its own process, output never goes to assets."""
import argparse,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--blender',required=True,type=Path);p.add_argument('--output',type=Path,default=R/'work/v03-build');a=p.parse_args()
for role in ['harbor-courier-review','taiwan-oldman-review']:
    env=os.environ.copy();env['STUDIO_CHARACTER']=role;env['STUDIO_V03_OUT']=str(a.output.resolve())
    subprocess.run([str(a.blender.resolve()),'-b','--threads','2','--python-exit-code','1','--python',str(R/'scripts/build_character_v03.py')],env=env,check=True)
