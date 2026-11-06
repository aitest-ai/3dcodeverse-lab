"""Append one Body elbow skin/garment morph plus a Run weight track; all original BIN bytes retained."""
import struct
from mathutils import Vector
from v05.blender_utils import G
from v17.sleeves import KEY
def values(o,index):
 a=o.doc['accessors'][index];v=o.doc['bufferViews'][a['bufferView']];n={'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']];fmt={5121:'B',5123:'H',5125:'I',5126:'f'}[a['componentType']];size=struct.calcsize(fmt)*n;offset=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',size)
 return [struct.unpack_from('<'+str(n)+fmt,o.binary,offset+i*stride) for i in range(a['count'])]
def accessor(o,rows,kind):
 flat=[x for row in rows for x in row];offset=len(o.binary);raw=struct.pack('<'+'f'*len(flat),*flat);o.binary+=raw;view=len(o.doc['bufferViews']);o.doc['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(raw)});a={'bufferView':view,'componentType':5126,'count':len(rows),'type':kind,'min':[min(row[j] for row in rows) for j in range(len(rows[0]))],'max':[max(row[j] for row in rows) for j in range(len(rows[0]))]};index=len(o.doc['accessors']);o.doc['accessors'].append(a);return index
def append(o,body,weights):
 mesh=o.doc['meshes'][1];assert all(not p.get('targets') for p in mesh['primitives']);ps={p['attributes']['POSITION'] for p in mesh['primitives']};ns={p['attributes']['NORMAL'] for p in mesh['primitives']};assert len(ps)==len(ns)==1
 positions=[Vector(v) for v in values(o,next(iter(ps)))];basis=body.data.shape_keys.key_blocks['Basis'];key=body.data.shape_keys.key_blocks[KEY];delta=[G.to_3x3()@(b.co-a.co) for a,b in zip(basis.data,key.data)];assert len(delta)==len(positions)
 triangles=[tuple(v[0] for v in inds[i:i+3]) for p in mesh['primitives'] for inds in [values(o,p['indices'])] for i in range(0,len(inds),3)]
 def normals(vs):
  sums=[Vector() for _ in vs]
  for a,b,c in triangles:
   n=(vs[b]-vs[a]).cross(vs[c]-vs[a])
   for i in [a,b,c]:sums[i]+=n
  return [v.normalized() for v in sums]
 old,new=normals(positions),normals([p+d for p,d in zip(positions,delta)]);normal_delta=[b-a for a,b in zip(old,new)];pos=accessor(o,[list(d) for d in delta],'VEC3');norm=accessor(o,[list(d) for d in normal_delta],'VEC3')
 for p in mesh['primitives']:p['targets']=[{'POSITION':pos,'NORMAL':norm}]
 mesh['weights']=[0];mesh.setdefault('extras',{})['targetNames']=[KEY]
 clip=next(a for a in o.doc['animations'] if a['name']=='Run');time=accessor(o,[[i/60] for i in range(43)],'SCALAR');out=accessor(o,[[w] for w in weights],'SCALAR');sampler=len(clip['samplers']);clip['samplers'].append({'input':time,'output':out,'interpolation':'LINEAR'});clip['channels'].append({'sampler':sampler,'target':{'node':next(i for i,n in enumerate(o.doc['nodes']) if n.get('mesh')==1),'path':'weights'}})
 return {'mesh':1,'target':KEY,'position_accessor':pos,'normal_accessor':norm,'default_weight':0,'run_weight_samples':weights,'normal_method':'Geometric area-weighted normal delta added to original authored normals; source normal bytes preserved'}
