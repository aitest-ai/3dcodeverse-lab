#!/usr/bin/env python3
"""Unpack immutable V012 Runtime ZIP and rebuild V013 in a new empty workspace; compare SHA-256 every file."""
from pathlib import Path
import sys,hashlib,json,zipfile,tempfile
from build_v013 import do as build
from integrate_v013 import go as integrate

def hash_file(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for chunk in iter(lambda:f.read(2*1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def run(v012zip,v002zip,comparison,output):
 with tempfile.TemporaryDirectory(prefix='date-v013-fresh-') as td:
  td=Path(td);v012=td/'v012';v012.mkdir();v013=td/'v013';patch=td/'rebuilt_patch.json'
  with zipfile.ZipFile(v012zip) as z:z.extractall(v012)
  build(v002zip,v012,patch);integrate(v012,v013,patch)
  expected={str(p.relative_to(comparison)):hash_file(p) for p in Path(comparison).rglob('*') if p.is_file()}
  actual={str(p.relative_to(v013)):hash_file(p) for p in v013.rglob('*') if p.is_file()}
  mismatches=[k for k in sorted(set(expected)|set(actual)) if expected.get(k)!=actual.get(k)]
  result={'schema':'noboribetsu-date-v013-replay/1','status':'PASS' if not mismatches else 'FAIL','original_zip_sha256':hash_file(v012zip),'replayed_files':len(actual),'matching_files':len(actual)-len(mismatches),'mismatches':mismatches,'patch_sha256':hash_file(patch)}
  Path(output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
  print(json.dumps(result,ensure_ascii=False,indent=2))
  if mismatches:raise RuntimeError('Clean replay mismatch')
if __name__=='__main__':run(*map(Path,sys.argv[1:]))