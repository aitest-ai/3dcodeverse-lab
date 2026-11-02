#!/usr/bin/env python3
"""Read-only V009 model integrity preflight; prints independent true SHA-256 hashes."""
from pathlib import Path
import gzip,hashlib,json
import os
ROOT=Path(os.environ.get('DATE_DIST_ROOT',str(Path(__file__).resolve().parents[2]/'runtime'/'dist')))

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(2*1024*1024),b''):h.update(block)
 return h.hexdigest()

def descriptor_objects():
 v=json.loads((ROOT/'scene_view.json').read_text())
 yield from v['models']
 for m in ['extension_manifest.json','v005_manifest.json','v006_manifest.json','v009_facade_manifest.json']:
  o=json.loads((ROOT/m).read_text())
  if 'models' in o:
   yield from o['models'].values()
  if 'model' in o:
   yield o['model']

def verify():
 seen=set();records=[]
 for d in descriptor_objects():
  name=d.get('stage') or d.get('path') or repr(d.get('parts'))
  if name in seen:continue
  seen.add(name)
  if d.get('compression')=='gzip':
   h=hashlib.sha256();total=0
   for part in d['parts']:
    with gzip.open(ROOT/part,'rb') as f:
     for block in iter(lambda:f.read(1024*1024),b''):
      h.update(block);total+=len(block)
   actual=h.hexdigest()
  else:
   p=ROOT/d['path'];actual=sha(p);total=p.stat().st_size
  records.append({'name':name,'bytes':total,'sha256':actual,'expected':d['sha256'],'pass':actual==d['sha256'] and total==d['bytes']})
 if not all(r['pass'] for r in records):raise RuntimeError('Model integrity failure: '+repr(records))
 return records
if __name__=='__main__':
 rec=verify()
 out={'schema':'noboribetsu-v010-independent-asset-hash-1','all_pass':all(r['pass'] for r in rec),'models':rec}
 Path(os.environ.get('DATE_QA_OUT','asset_preflight.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(out,ensure_ascii=False,indent=2))