#!/usr/bin/env python3
"""Offline replay V019 from an immutable V018 ZIP into a new empty project folder.
Source tree scripts build_v019.py + integrate_v019.py must be in this script directory.
Does not overwrite older releases.
Usage: python replay_v019.py /path/V018_Runtime.zip /path/new_v019_workspace
"""
from pathlib import Path
import json,hashlib,zipfile,sys,shutil,subprocess
SOURCE=Path(__file__).resolve().parent
KNOWN='99930d2271c9d059e5c724d597a4b01d82a1e6b7d942eb57b919873e1b81ea9e'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def replay(src,out):
 src=Path(src).resolve();out=Path(out).resolve()
 if out.exists():raise FileExistsError(f'Output exists (no overwrite): {out}')
 if not zipfile.is_zipfile(src) or sha(src)!=KNOWN:raise ValueError('V018 immutable Runtime ZIP SHA mismatch')
 with zipfile.ZipFile(src) as z:
  if z.testzip():raise ValueError('ZIP CRC failed')
  if any(Path(n).is_absolute() or '..' in Path(n).parts for n in z.namelist()):raise ValueError('Unsafe ZIP path')
  out.mkdir(parents=True);z.extractall(out/'runtime')
 for n in ('build_v019.py','integrate_v019.py'):
  shutil.copy2(SOURCE/n,out/n)
 subprocess.run([sys.executable,str(out/'build_v019.py')],cwd=out,check=True,capture_output=True)
 subprocess.run([sys.executable,str(out/'integrate_v019.py')],cwd=out,check=True,capture_output=True)
 subprocess.run(['node','--check',str(out/'runtime/dist/app.js')],check=True)
 with zipfile.ZipFile(src) as prior:
  old={n:hashlib.sha256(prior.read(n)).hexdigest() for n in prior.namelist()}
 changed=[n for n in old if sha(out/'runtime'/n)!=old[n]]
 assert sorted(changed)==sorted(['dist/app.js','dist/index.html','dist/qa.json','dist/scene_view.json','dist/style.css'])
 files={str(p.relative_to(out/'runtime')):sha(p) for p in (out/'runtime').rglob('*') if p.is_file()}
 return {'changed':changed,'total_files':len(files),'files_sha256':files}
if __name__=='__main__':
 if len(sys.argv)!=3:raise SystemExit(__doc__)
 result=replay(sys.argv[1],sys.argv[2]);print(json.dumps({'total_files':result['total_files'],'modified_existing':result['changed']},ensure_ascii=False,indent=2))