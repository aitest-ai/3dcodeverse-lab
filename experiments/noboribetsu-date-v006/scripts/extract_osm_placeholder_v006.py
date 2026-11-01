#!/usr/bin/env python3
"""Read frozen V003 B GLB from untouched gzip fragments and extract OSM-mass mesh.
The full 188 MB B GLB is temporary; private model bytes are never committed to GitHub.
"""
from pathlib import Path
import json,os,hashlib,struct,gzip,tempfile,numpy as np
root=Path(os.environ.get('DATE_V006_ROOT',Path(__file__).resolve().parent.parent));d=root/'dist';v=json.loads((d/'scene_view.json').read_text());B=next(m for m in v['models'] if m['stage']=='B')
sha=hashlib.sha256();out=root/'evidence/OSM_mass_extract_temp.glb'
try:
 with out.open('wb') as w:
  for part in B['parts']:
   with gzip.open(d/part,'rb') as f:
    while c:=f.read(4*1024*1024):sha.update(c);w.write(c)
 if out.stat().st_size!=B['bytes'] or sha.hexdigest()!=B['sha256']:raise RuntimeError('Original V003 B hash mismatch')
 with out.open('rb') as f:
  header=f.read(20);assert header[:4]==b'glTF';jl=struct.unpack_from('<I',header,12)[0]
  gj=json.loads(f.read(jl));binbase=20+jl+8
  prim=[p for mesh in gj['meshes'] for p in mesh['primitives'] if gj['materials'][p['material']]['name']=='Unrefined_OSM_mass']
  if len(prim)!=1:raise RuntimeError('Expected exactly one placeholder primitive')
  p=prim[0]
  def attr(index):
   a=gj['accessors'][index];bv=gj['bufferViews'][a['bufferView']];n={'SCALAR':1,'VEC3':3}[a['type']]
   dt={5126:np.dtype('<f4'),5123:np.dtype('<u2'),5125:np.dtype('<u4')}[a['componentType']]
   f.seek(binbase+bv.get('byteOffset',0)+a.get('byteOffset',0));arr=np.frombuffer(f.read(a['count']*n*dt.itemsize),dtype=dt).copy()
   return arr.reshape(-1,n) if n>1 else arr
  points=attr(p['attributes']['POSITION']);indices=attr(p['indices']).astype(np.uint32)
  assert len(indices)//3==368
 mesh={'positions':points.astype(float).tolist(),'indices':indices.astype(int).tolist(),'sha256_frozen_B':sha.hexdigest(),'triangles':len(indices)//3}
 (root/'evidence/osm_primitive.json').write_text(json.dumps(mesh,separators=(',',':'))+'\n')
 print(json.dumps({'source_sha256':sha.hexdigest(),'vertices':len(points),'triangles':len(indices)//3,'output_bytes':(root/'evidence/osm_primitive.json').stat().st_size}))
finally:
 if out.exists():out.unlink()