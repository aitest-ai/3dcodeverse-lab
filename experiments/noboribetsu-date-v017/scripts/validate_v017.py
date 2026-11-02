#!/usr/bin/env python3
"""Check frozen V016 -> V017 only allowlisted changes and V017 geometry invariant."""
import json,hashlib,zipfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT/'V016_Runtime.zip';D=ROOT/'base';O=ROOT/'outputs'
with zipfile.ZipFile(BASE) as z:
 names=set(z.namelist());same=0;changed=[]
 for n in sorted(names):
  old=hashlib.sha256(z.read(n)).hexdigest();new=hashlib.sha256((D/n).read_bytes()).hexdigest()
  if old==new:same+=1
  else:changed.append(n)
assert len(names)==113 and same==109, (len(names),same)
assert changed==['dist/app.js','dist/index.html','dist/qa.json','dist/scene_view.json'],changed
extra=sorted(p.relative_to(D).as_posix() for p in D.rglob('*') if p.is_file() and p.relative_to(D).as_posix() not in names)
assert extra==['dist/README_V017.md','dist/v017_clearance_audit.json'],extra
source=json.loads((D/'dist/v017_clearance_audit.json').read_text());m=json.loads((D/'dist/scene_view.json').read_text())['clearance_v017']
assert m['sha256']==hashlib.sha256((D/'dist/v017_clearance_audit.json').read_bytes()).hexdigest()
assert m['default_visible'] is False and m['marker_count']==4
assert source['summary']['sample_count']==237 and source['summary']['walkable_centerline_pass']
assert source['summary']['minimum_capsule_margin_m']>0
assert len(source['markers'])==4
assert source['summary']['obstacle_count']==24
assert source['collision_changed'] is False and source['route_changed'] is False and source['original_architecture_modified'] is False
q=json.loads((O/'V017_webgl_qa.json').read_text());assert q['success'] and q['real_webgl2'] and q['loaded']=='true' and not q['page_errors'] and not q['missing']
assert q['toggle_observed']['initial']=='false' and q['toggle_observed']['on']=='true' and q['toggle_observed']['off']=='false'
assert q['metrics']['v015']['support_count']==8 and q['metrics']['v016']['sample_count']==4 and q['metrics']['v017']['sample_count']==237
report={'schema':'noboribetsu-date-v017-integrity/1','status':'SOURCE_QA_AND_ISOLATED_WEBGL2_PASS','v016_archive_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'v016_files':len(names),'unchanged_original_files':same,'modified_files':changed,'added_files':extra,'new_runtime_file_count':len(names)+len(extra),'geometry_sample_count':237,'minimum_margin_m':source['summary']['minimum_capsule_margin_m'],'webgl2':True,'b_scene_loaded':True,'qa_only_digest_adapter':True,'not_verified':['Native HTTPS/WebCrypto top level','private CDN/login','Android physical device','Blender native','surveyed doorway dimensions','physical egress/accessibility']}
(O/'V017_integrity_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))