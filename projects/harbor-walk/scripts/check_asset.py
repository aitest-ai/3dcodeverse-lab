"""Validate binary buffers, normalized skinning weights, nonconstant bone animation, morphs and asset digest."""
from pathlib import Path
import struct,json,math,hashlib
R=Path(__file__).resolve().parents[1];p=R/'public/models/harbor-courier.glb';b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);binary=b[28+n:];manifest=json.loads((R/'assets/asset_manifest.json').read_text());assert hashlib.sha256(b).hexdigest()==manifest['sha256']
types={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16};ct={5120:'b',5121:'B',5122:'h',5123:'H',5125:'I',5126:'f'}
def values(idx):
 a=d['accessors'][idx];v=d['bufferViews'][a['bufferView']];count=types[a['type']];fmt='<'+ct[a['componentType']]*count;size=struct.calcsize(fmt);start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',size)
 assert start+(a['count']-1)*stride+size<=len(binary)
 return [struct.unpack_from(fmt,binary,start+i*stride) for i in range(a['count'])]
weighted=0;maxerror=0
for m in d['meshes']:
 for pr in m['primitives']:
  at=pr['attributes']
  if 'WEIGHTS_0' not in at:continue
  weights=values(at['WEIGHTS_0']);joints=values(at['JOINTS_0']);assert len(weights)==len(joints)
  for w,j in zip(weights,joints):
   assert all(math.isfinite(x) and x>=0 for x in w);err=abs(sum(w)-1);maxerror=max(maxerror,err);assert err<1e-4;assert max(j)<len(d['skins'][0]['joints']);weighted+=1
motion={}
for a in d['animations']:
 nonconstant=0
 for ch in a['channels']:
  s=a['samplers'][ch['sampler']];v=values(s['output'])
  if v and any(any(abs(x-y)>1e-5 for x,y in zip(v[0],q)) for q in v[1:]):nonconstant+=1
 motion[a['name']]={'channels':len(a['channels']),'nonconstant_channels':nonconstant};assert nonconstant>0
assert all(x in motion for x in manifest['clips'])
morphs=sum(len(pr.get('targets',[])) for m in d['meshes'] for pr in m['primitives']);assert morphs>0
result={'status':'PASS','sha256':manifest['sha256'],'bytes':len(b),'skin_count':len(d['skins']),'bones':len(d['skins'][0]['joints']),'weighted_vertices':weighted,'maximum_weight_sum_error':maxerror,'morph_targets':morphs,'animations':motion,'limitations':['Does not certify anatomy, skin deformation, foot slip, facial quality or hardware performance.']}
(R/'evidence/asset-deep-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
