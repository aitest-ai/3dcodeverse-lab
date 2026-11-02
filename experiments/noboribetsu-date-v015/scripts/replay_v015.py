"""Build V015 from a frozen V014 ZIP + a frozen V002 Complete ZIP into a new temporary folder."""
import os,sys,tempfile,hashlib,zipfile,shutil,subprocess,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
v014=Path(os.environ.get('NOBORIBETSU_V014_RUNTIME_ZIP','/mnt/data/Noboribetsu_Date_V014_R1_Runtime.zip'))
v002=Path(os.environ.get('NOBORIBETSU_V002_COMPLETE_ZIP','/mnt/data/files/Noboribetsu_Date_V002_Complete.zip'))
assert v014.is_file() and v002.is_file()
with tempfile.TemporaryDirectory(prefix='v015_fresh_replay_') as t:
 t=Path(t);(t/'base').mkdir()
 with zipfile.ZipFile(v014) as z:z.extractall(t/'base')
 for src in ['build_v015.py','integrate_v015.py']:
  shutil.copyfile(ROOT/src,t/src)
 e=os.environ.copy();e['NOBORIBETSU_V002_COMPLETE_ZIP']=str(v002)
 for src in ['build_v015.py','integrate_v015.py']:
  p=subprocess.run([sys.executable,str(t/src)],cwd=t,env=e,capture_output=True,text=True)
  if p.returncode:raise RuntimeError(src+': '+p.stderr[-2000:])
 n1={p.relative_to(ROOT/'base').as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'base').rglob('*') if p.is_file()}
 n2={p.relative_to(t/'base').as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (t/'base').rglob('*') if p.is_file()}
 result={'schema':'noboribetsu-date-v015-replay/1','base_input_files':111,'output_files':len(n1),'matched':len([k for k in n1 if n1.get(k)==n2.get(k)]),'unexpected':sorted(set(n1)^set(n2)),'bitwise_identical':n1==n2}
 if n1!=n2:result['mismatch']=[n for n in n1 if n1[n]!=n2.get(n)]
 (ROOT/'outputs/V015_clean_replay_qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(result)
 assert result['bitwise_identical']