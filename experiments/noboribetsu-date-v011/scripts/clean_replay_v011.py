#!/usr/bin/env python3
"""Rebuild V011 cleanly from original V010 zip; compare all output bytes."""
import hashlib,json,shutil,tempfile,sys
from pathlib import Path
from zipfile import ZipFile
from build_v011_terrain_patch import build_patch
from integrate_v011 import run

v010=Path(sys.argv[1]);finished=Path(sys.argv[2]);evidence=Path(sys.argv[3]);evidence.parent.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='date_v011_replay_') as t:
 root=Path(t);base=root/'baseline';
 with ZipFile(v010) as z:z.extractall(base)
 out=root/'new_patch.json';patch,qa=build_patch(base/'dist');out.write_text(json.dumps(patch,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
 delta=run(base/'dist',root/'fresh_dist',out)
 matched=[];mismatch=[]
 for f in sorted((root/'fresh_dist').rglob('*')):
  if not f.is_file():continue
  relative=f.relative_to(root/'fresh_dist');other=finished/'dist'/relative
  ok=other.is_file() and hashlib.sha256(f.read_bytes()).digest()==hashlib.sha256(other.read_bytes()).digest()
  (matched if ok else mismatch).append(str(relative))
 missing=[str(f.relative_to(finished/'dist')) for f in (finished/'dist').rglob('*') if f.is_file() and not (root/'fresh_dist'/f.relative_to(finished/'dist')).exists()]
 if mismatch or missing:raise ValueError('Clean replay differs: '+repr(mismatch[:3])+repr(missing[:3]))
 # Verify entire original V010 Runtime's unmodified files have been retained.
 before={str(f.relative_to(base)):hashlib.sha256(f.read_bytes()).hexdigest() for f in base.rglob('*') if f.is_file()}
 after={str(f.relative_to(finished)):hashlib.sha256(f.read_bytes()).hexdigest() for f in finished.rglob('*') if f.is_file()}
 changed=[k for k,v in before.items() if after.get(k)!=v]
 added=sorted(set(after)-set(before))
 if set(changed)!={'dist/app.js','dist/index.html','dist/qa.json','dist/scene_view.json'}:raise ValueError('Unexpected V010 changes '+str(changed))
 if set(added)!={'dist/v011_terrain_gap_patch.json','README_V011.md','start_v011_local.py'}:raise ValueError('Unexpected additions '+str(added))
 report={'schema':'noboribetsu-v011-clean-replay/1','status':'PASS',
         'original_v010_files':len(before),'unchanged_v010_files':len(before)-len(changed),
         'modified_old_files':sorted(changed),'new_files':added,'final_runtime_files':len(after),
         'regenerated_dist_files_matched':len(matched),'regenerated_dist_mismatches':mismatch,
         'v010_archive_sha256':hashlib.sha256(v010.read_bytes()).hexdigest(),
         'patch_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
         'source_b_sha256':patch['source_b_sha256'],
         'old_GLBS_and_collisions_preserved':True}
 evidence.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False))