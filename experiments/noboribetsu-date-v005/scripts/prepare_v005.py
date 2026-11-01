#!/usr/bin/env python3
"""Prepare V005 from the immutable V004 R1 Runtime ZIP; never overwrites predecessors."""
from pathlib import Path
import hashlib, json, zipfile, shutil, sys

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  while t:=f.read(1<<20):h.update(t)
 return h.hexdigest()

def prepare(src,dest):
 src=Path(src);dest=Path(dest)
 if (dest/'dist').exists():raise FileExistsError('V005 runtime/dist exists; refuse overwrite')
 with zipfile.ZipFile(src) as z:
  manifest=json.loads(z.read('dist/extension_manifest.json'))
  version=json.loads(z.read('dist/scene_view.json'))
  assert manifest['schema']=='noboribetsu-date-v004-merchant/1'
  assert abs(version['route'][-1]['s']-130.014612179)<0.0001
  for name,model in manifest['models'].items():
   blob=z.read('dist/'+model['path'])
   if hashlib.sha256(blob).hexdigest()!=model['sha256']:
    raise ValueError('V004 GLB differs from frozen description: '+name)
  for info in z.infolist():
   p=Path(info.filename)
   if info.is_dir() or not p.parts or p.parts[0]!='dist':continue
   if '..' in p.parts or p.is_absolute():raise ValueError('ZIP-slip path')
   target=dest/p;target.parent.mkdir(parents=True,exist_ok=True)
   with z.open(info) as f,open(target,'wb') as out:shutil.copyfileobj(f,out)
  (dest/'V004_source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
  (dest/'V004_source_view.json').write_text(json.dumps(version,ensure_ascii=False,indent=2)+'\n')
  (dest/'V004_source_app.js').write_bytes(z.read('dist/app.js'))
  (dest/'V004_source_index.html').write_bytes(z.read('dist/index.html'))
  (dest/'V004_source_qa.json').write_bytes(z.read('dist/qa.json'))
  old={p:sha(dest/p) for p in ('dist/app.js','dist/index.html','dist/scene_view.json','dist/qa.json','dist/extension_manifest.json','dist/extension_collision.json')}
  (dest/'V004_FROZEN_AUDIT.json').write_text(json.dumps({'source':src.name,'version':'V004-R1','sha256':old,'v004_models_verified':len(manifest['models'])},indent=2)+'\n')
  return {'copied_dist_files':len([x for x in z.namelist() if x.startswith('dist/')]),'frozen_glbs':len(manifest['models'])}
if __name__=='__main__':
 print(json.dumps(prepare(sys.argv[1],sys.argv[2]),indent=2))