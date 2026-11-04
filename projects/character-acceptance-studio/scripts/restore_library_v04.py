#!/usr/bin/env python3
"""Restore duplicate raw sources and exact embedded texture bytes from runtime GLBs.
No image encoding, retargeting, mesh editing or resolution change. Optional source pack supplies mothers.
"""
import hashlib,json,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def safe_write(p,data,expected=None):
 if expected and hashlib.sha256(data).hexdigest()!=expected:raise ValueError('SHA mismatch: '+str(p))
 if p.exists():
  if p.read_bytes()!=data:raise ValueError('Existing file differs; refuse overwrite: '+str(p))
  return 0
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);return 1

def restore():
 c=json.loads((R/'library-v04/catalog.json').read_text());count=0
 for line in (R/'sources-v04/SOURCE_FILES.sha256').read_text().splitlines():
  h,p=line.split('  ',1);f=R/p
  if f.exists() and hashlib.sha256(f.read_bytes()).hexdigest()!=h:raise ValueError('Source modified; refuse restore: '+p)
 for e in c['entries']:
  dest=R/'library-v04'/e['id']/e['version'];model=dest/'model.glb';b=model.read_bytes()
  if hashlib.sha256(b).hexdigest()!=e['model']['sha256']:raise ValueError('Runtime model SHA mismatch: '+e['id'])
  n=struct.unpack_from('<I',b,12)[0];doc=json.loads(b[20:20+n]);binary=b[28+n:]
  if e['source'].endswith(('.glb','.vrm')):count+=safe_write(R/e['source'],b,e['source_sha256'])
  for im,tex in zip(doc.get('images',[]),e['textures']):
   v=doc['bufferViews'][im['bufferView']];data=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];count+=safe_write(dest/tex['file'],data,tex['sha256'])
  master=R/e['editable']['path']
  if e['editable']['original_blend_available'] and master.exists():count+=safe_write(dest/'model.blend',master.read_bytes())
 print('Restored',count,'exact duplicate source/texture files; no quality conversion.')
 return count
if __name__=='__main__':restore()
