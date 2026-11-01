#!/usr/bin/env python3
"""Extract a FRESH, verified V004 workspace from immutable V002 Complete + V003 R3 Runtime archives.

Usage:
 python prepare_v004_sources.py V002_Complete.zip V003_R3_Runtime.zip /safe/new/empty/workspace

The target must not already contain anything. Neither source archive nor websites are modified.
Reference-only images from V002 are never packaged into the workspace.
"""
from __future__ import annotations
import hashlib, json, shutil, sys, zipfile
from pathlib import Path

SOURCE_HASHES = {
 'authoring/date_v002_master.blend':'1d7637c7dd98642ffbfa03074fa6f3af50339a5e965afc2feb47e1ed86567ee1',
 'data/scene_geometry.json':'75d672d5296ac28bef25b03423da395027c4b29cf804652239f40e9fc73d408a',
 'data/collision.json':'52cea1f4b65e11a09f5504c48daef3f4eda7ef180312c1a39ab4db152a30e562',
 'models/scene_A.glb':'1400aff4bccb89fbc30bb2c931a71e91f8f6faf003e01bcb0c2347a14aa95a10',
 'models/scene_B.glb':'684b0917f3bf5c2edd87e05cfb2b6f670aab6fa574bb579f6bcaa01258d81314',
}

def stream_sha(z,name):
 h=hashlib.sha256()
 with z.open(name) as f:
  while chunk:=f.read(2*1024*1024):h.update(chunk)
 return h.hexdigest()

def prepare(v002,r3,dest):
 v002,r3,dest=Path(v002),Path(r3),Path(dest)
 if not v002.is_file() or not r3.is_file():raise FileNotFoundError('Source ZIP missing')
 if dest.exists() and any(dest.iterdir()):raise FileExistsError('V004 target must be empty: '+str(dest))
 report={'schema':'noboribetsu-date-v004-source-prepare/1','v002_zip':v002.name,'r3_zip':r3.name,'checks':{},'status':'FAIL'}
 with zipfile.ZipFile(v002) as z:
  prefix='Noboribetsu_Date_V002/'
  for relative,sha in SOURCE_HASHES.items():
   actual=stream_sha(z,prefix+relative)
   report['checks'][relative]={'sha256':actual,'expected':sha,'pass':actual==sha}
   if actual!=sha:raise ValueError('V002 frozen hash mismatch: '+relative)
  geom=z.read(prefix+'data/scene_geometry.json')
 with zipfile.ZipFile(r3) as z:
  original=json.loads(z.read('dist/scene_view.json'))
  if original['version']!='V003-candidate-r2' or abs(original['route'][-1]['s']-82.87701578450043)>.001:
   raise ValueError('V003 R3 immutable source contract mismatch')
  # R3 retains the R2 scene_view version; its boot script version is R3.
  if b"V003-candidate-r3" not in z.read('dist/app.js'):
   raise ValueError('R3 runtime app version unexpected')
  if original['models'][0]['sha256']!='3feac26ec59250494330974775bda07c089c0a4642eb4471dc18fd22b2ba6715':
   raise ValueError('R3 B scene descriptor mismatch')
  dest.mkdir(parents=True,exist_ok=True)
  # Only safe exact paths under dist/; cannot write outside target via Zip slip.
  for info in z.infolist():
   name=info.filename
   if info.is_dir() or not name.startswith('dist/'):continue
   rel=Path(name)
   if rel.is_absolute() or '..' in rel.parts:raise ValueError('Unsafe archive path: '+name)
   target=dest/'runtime'/rel;target.parent.mkdir(parents=True,exist_ok=True)
   with z.open(info) as source,target.open('wb') as target_io:shutil.copyfileobj(source,target_io)
  baseline=dest/'baseline';(baseline/'data').mkdir(parents=True,exist_ok=True)
  (baseline/'data/scene_geometry.json').write_bytes(geom)
  (baseline/'scene_view_R3.json').write_bytes(z.read('dist/scene_view.json'))
  (baseline/'app_R3_original.js').write_bytes(z.read('dist/app.js'))
  (baseline/'index_R3_original.html').write_bytes(z.read('dist/index.html'))
  report['R3_models']={a['stage']:a['sha256'] for a in original['models']}
  report['copied_R3_dist_files']=sum(1 for i in z.infolist() if i.filename.startswith('dist/') and not i.is_dir())
 report['status']='PASS_FROZEN_SOURCE_EXTRACTION'
 (dest/'V004_prepare_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return report

if __name__=='__main__':
 if len(sys.argv)!=4:raise SystemExit(__doc__)
 print(json.dumps(prepare(*sys.argv[1:]),ensure_ascii=False,indent=2))