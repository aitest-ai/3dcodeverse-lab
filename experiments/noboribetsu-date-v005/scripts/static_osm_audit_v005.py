#!/usr/bin/env python3
"""Read-only static inspection of original frozen V003 B GLB OSM placeholder triangles and V004 OSM footprints.
This does not replace runtime browser acceptance; it confirms expected geometry is within target polygons.
"""
import gzip, hashlib,json,struct,numpy as np,os
from pathlib import Path
p=Path(os.environ.get('DATE_V005_ROOT', str(Path(__file__).resolve().parent.parent/'runtime')))
assets=p/'dist/assets'
scene=json.loads((p/'dist/scene_view.json').read_text())
out=p/'base_R3_sceneB_for_audit_TEMP.glb'
model=next(x for x in scene['models'] if x['stage']=='B')
sha=hashlib.sha256()
with out.open('wb') as w:
 for part in model['parts']:
  with gzip.open(assets/Path(part).name,'rb') as f:
   while b:=f.read(4*1024*1024):sha.update(b);w.write(b)
assert out.stat().st_size==model['bytes']
assert sha.hexdigest()==model['sha256']
with out.open('rb') as f:
 header=f.read(20);assert header[:4]==b'glTF'
 jsonlen=struct.unpack_from('<I',header,12)[0]
 gltf=json.loads(f.read(jsonlen))
 binstart=20+jsonlen+8
 matname=lambda prim:gltf['materials'][prim['material']]['name']
 prim=[pr for pr in gltf['meshes'][0]['primitives'] if matname(pr)=='Unrefined_OSM_mass']
 assert len(prim)==1
 prim=prim[0]
 def accessor(name):
  a=gltf['accessors'][prim['attributes'][name] if name in prim['attributes'] else prim[name]]
  v=gltf['bufferViews'][a['bufferView']]
  f.seek(binstart+v['byteOffset']+a.get('byteOffset',0))
  comps={'VEC3':3,'SCALAR':1}[a['type']]
  dtype={5126:np.float32,5123:np.uint16,5125:np.uint32}[a['componentType']]
  return np.frombuffer(f.read(a['count']*comps*np.dtype(dtype).itemsize),dtype=dtype).reshape(-1,comps).copy()
 xyz=accessor('POSITION');indices=accessor('indices').reshape(-1,3)
cent=xyz[indices].mean(axis=1)
def inside(x,z,poly):
 yes=False
 for i in range(len(poly)):
  xi,zi=poly[i];xj,zj=poly[i-1]
  if (zi>z)!=(zj>z) and x<(xj-xi)*(z-zi)/(zj-zi)+xi:yes=not yes
 return yes
ids=scene['extension']['building_ids']+scene['extension_v005']['building_ids']
by={b['id']:b for b in scene['buildings']}
results={}
for id in ids:
 poly=[(x,-north) for x,north in by[id]['polygon']]
 idx=[i for i,(x,y,z) in enumerate(cent) if inside(x,z,poly)]
 results[id]={'name':by[id]['name'],'triangles_at_centroid':len(idx)}
assert all(a['triangles_at_centroid']>0 for a in results.values()),results
assert sum(results[q]['triangles_at_centroid'] for q in scene['extension_v005']['building_ids'])>0
qa={'sha256_original_sceneB':sha.hexdigest(),'total_osm_mass_triangles':len(indices),'target_footprints':results,'stage_B_gltf_material':'Unrefined_OSM_mass','status':'V004_AND_V005_STATIC_REPLACEMENTS_PRESENT_BROWSER_UNTESTED'}
(p/'V005_osm_placeholder_audit.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(qa,ensure_ascii=False,indent=2))
out.unlink()