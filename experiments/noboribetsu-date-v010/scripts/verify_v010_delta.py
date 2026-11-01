#!/usr/bin/env python3
"""Verify V010 changes only four existing runtime files; all world assets stay byte-identical."""
import argparse,hashlib,json,zipfile
from pathlib import Path
CHANGED={'dist/app.js','dist/input-events.js','dist/index.html','dist/qa.json'}
ADDED={'start_v010_local.py','README_V010.md'}
def filemap(source):
 p=Path(source)
 if p.is_dir():
  return {str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file()}
 with zipfile.ZipFile(p) as z:
  return {i.filename:hashlib.sha256(z.read(i.filename)).hexdigest() for i in z.infolist() if not i.is_dir()}
def verify(old,new):
 a=filemap(old);b=filemap(new)
 unexpected=[k for k in sorted(a.keys()|b.keys()) if k not in CHANGED|ADDED and a.get(k)!=b.get(k)]
 changed={k:dict(v009=a.get(k),v010=b.get(k)) for k in CHANGED}
 added=sorted(b.keys()-a.keys())
 passing=not unexpected and all(a.get(k) and b.get(k) and a[k]!=b[k] for k in CHANGED) and set(added)==ADDED
 return {'schema':'v010-delta-1','pass':passing,'old_files':len(a),'new_files':len(b),'expected_changed':changed,'added':added,'unexpected_changes':unexpected,'unchanged_original_files':sum(a.get(k)==b.get(k) for k in a)}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('v009');ap.add_argument('v010');ap.add_argument('--output')
 args=ap.parse_args();r=verify(args.v009,args.v010)
 if args.output:Path(args.output).write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps(r,indent=2,ensure_ascii=False))
 raise SystemExit(0 if r['pass'] else 1)