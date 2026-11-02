#!/usr/bin/env python3
"""Rebuild V016 from exact V015 Runtime and SourceQA archives (without modifying either)."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile,zipfile
from pathlib import Path
S=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--runtime',type=Path,default=Path('/mnt/data/Noboribetsu_Date_V015_R1_Runtime.zip'))
parser.add_argument('--sourceqa',type=Path,default=Path('/mnt/data/Noboribetsu_Date_V015_R1_SourceQA.zip'))
parser.add_argument('--expected-dist',type=Path,default=S/'base');parser.add_argument('--report',type=Path,default=S/'outputs/V016_clean_replay_qa.json')
a=parser.parse_args();assert a.runtime.is_file() and a.sourceqa.is_file()
with tempfile.TemporaryDirectory(prefix='v016-replay-') as td:
 p=Path(td)
 with zipfile.ZipFile(a.runtime) as z:z.extractall(p/'base')
 with zipfile.ZipFile(a.sourceqa) as z:z.extractall(p/'source')
 for n in ['build_v016_audit.py','integrate_v016.py']:
  shutil.copy2(S/n,p/n)
 # Preserve the exact V016 candidate integration adjustments, which apply only after generate.
 subprocess.run([sys.executable,str(p/'build_v016_audit.py')],check=True,capture_output=True,text=True)
 subprocess.run([sys.executable,str(p/'integrate_v016.py')],check=True,capture_output=True,text=True)
 # Authoring tweak: update a stale title and keep V015 toggle metadata accurate.
 html=p/'base/dist/index.html';s=html.read_text().replace('登別伊達時代村 V016 商家街中央石板候選','登別伊達時代村 V016 石基座接地診斷')
 s=s.replace('title="僅修補 8 處懸空柱腳，仍有 4 處埋入待人工處理"','title="V015 原有 8 處接地支撐；V016 另查核兩條連續石基座上的 4 個坡地取樣點"');html.write_text(s)
 def listing(base):return {str(f.relative_to(base)):hashlib.sha256(f.read_bytes()).hexdigest() for f in base.rglob('*') if f.is_file()}
 x=listing(p/'base');y=listing(a.expected_dist)
 assert x==y,(len(x),len(y),set(x)^set(y),[(k,x.get(k),y.get(k)) for k in set(x)&set(y) if x[k]!=y[k]][:3])
 result={'schema':'noboribetsu-date-v016-clean-replay/1','status':'PASS','matched_files':len(x),'total_files':len(y),'hash_mismatches':0,'v015_originals_not_overwritten':True,'sources':[str(a.runtime),str(a.sourceqa)]}
 a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('replay verified',len(x),'/',len(y))