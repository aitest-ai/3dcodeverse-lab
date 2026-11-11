"""Export localized cuff subdivision, retaining original arrays as exact prefixes."""
import struct
from mathutils import Vector
from v05.blender_utils import B,G
def values(o,index):
 a=o.doc['accessors'][index];v=o.doc['bufferViews'][a['bufferView']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];fmt={5121:'B',5123:'H',5125:'I',5126:'f'}[a['componentType']];size=struct.calcsize(fmt)*n;offset=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',size)
 return [struct.unpack_from('<'+fmt*n,o.binary,offset+i*stride) for i in range(a['count'])]
def accessor(o,rows,kind,component=5126):
 fmt={5126:'f',5123:'H',5125:'I'}[component];o.binary+=b'\0'*((-len(o.binary))%4);offset=len(o.binary);raw=struct.pack('<'+fmt*sum(len(r) for r in rows),*(x for r in rows for x in r));o.binary+=raw;o.binary+=b'\0'*((-len(o.binary))%4);view=len(o.doc['bufferViews']);o.doc['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(raw)});a={'bufferView':view,'componentType':component,'count':len(rows),'type':kind}
 if kind in ['VEC3','SCALAR']:a.update(min=[min(r[j] for r in rows) for j in range(len(rows[0]))],max=[max(r[j] for r in rows) for j in range(len(rows[0]))])
 i=len(o.doc['accessors']);o.doc['accessors'].append(a);return i
def append(o,body,mapping):
 me=body.data;me.calc_loop_triangles();mesh=o.doc['meshes'][1];attrs=mesh['primitives'][0]['attributes'];original_count=o.doc['accessors'][attrs['POSITION']]['count'];assert len(me.vertices)==original_count+len(mapping)
 assert set(attrs)=={'POSITION','NORMAL','TEXCOORD_0','JOINTS_0','WEIGHTS_0'}
 arrays={k:[list(r) for r in values(o,a)] for k,a in attrs.items()};new_normals=[]
 skin=o.doc['skins'][next(n['skin'] for n in o.doc['nodes'] if n.get('mesh')==1)];joints={o.doc['nodes'][n]['name']:i for i,n in enumerate(skin['joints'])}
 uv_by_id={}
 for poly in me.polygons:
  for vi,li in zip(poly.vertices,poly.loop_indices):
   uv=list(me.uv_layers.active.data[li].uv)
   if vi in uv_by_id:assert max(abs(a-b) for a,b in zip(uv,uv_by_id[vi]))<2e-6,'Export requires split UV seams'
   else:uv_by_id[vi]=uv
 direct=sum(abs(uv_by_id[i][1]-arrays['TEXCOORD_0'][i][1]) for i in range(original_count));flipped=sum(abs(1-uv_by_id[i][1]-arrays['TEXCOORD_0'][i][1]) for i in range(original_count));flip_y=flipped<direct
 for row in sorted(mapping,key=lambda r:r['vertex']):
  i=row['vertex'];a,b=row['parents'];assert i==len(arrays['POSITION']);arrays['POSITION'].append(list(G.to_3x3()@me.vertices[i].co));normal=(Vector(arrays['NORMAL'][a])+Vector(arrays['NORMAL'][b])).normalized();arrays['NORMAL'].append(list(normal));new_normals.append(list(B.to_3x3()@normal));uv=uv_by_id[i];arrays['TEXCOORD_0'].append([uv[0],1-uv[1] if flip_y else uv[1]])
  pairs=sorted([(joints[body.vertex_groups[g.group].name],g.weight) for g in me.vertices[i].groups if g.weight>0 and body.vertex_groups[g.group].name in joints],key=lambda x:(-x[1],x[0]));assert len(pairs)<=4 and abs(sum(w for j,w in pairs)-1)<1e-6;arrays['JOINTS_0'].append([j for j,w in pairs]+[0]*(4-len(pairs)));arrays['WEIGHTS_0'].append([w for j,w in pairs]+[0.]*(4-len(pairs)))
 out={k:accessor(o,a,{'POSITION':'VEC3','NORMAL':'VEC3','TEXCOORD_0':'VEC2','JOINTS_0':'VEC4','WEIGHTS_0':'VEC4'}[k],5123 if k=='JOINTS_0' else 5126) for k,a in arrays.items()}
 targets=[]
 for ti,target in enumerate(mesh['primitives'][0]['targets']):
  key=me.shape_keys.key_blocks[mesh['extras']['targetNames'][ti]];basis=me.shape_keys.key_blocks['Basis'];data={k:[list(r) for r in values(o,a)] for k,a in target.items()}
  for row in sorted(mapping,key=lambda r:r['vertex']):
   i=row['vertex'];a,b=row['parents'];data['POSITION'].append(list(G.to_3x3()@(key.data[i].co-basis.data[i].co)));data['NORMAL'].append([(x+y)*.5 for x,y in zip(data['NORMAL'][a],data['NORMAL'][b])])
  targets.append({k:accessor(o,rows,'VEC3') for k,rows in data.items()})
 for p in mesh['primitives']:
  name=o.doc['materials'][p['material']]['name'];p['attributes']=out.copy();p['targets']=targets
  if 'Tops' in name:
   mi=next(i for i,m in enumerate(me.materials) if m.name==name);indices=[[i] for t in me.loop_triangles if t.material_index==mi for i in t.vertices];assert indices;p['indices']=accessor(o,indices,'SCALAR',5123)
 return {'original_vertices':original_count,'vertices':len(me.vertices),'added_vertices':len(mapping),'attributes':out,'targets':targets,'uv_flip_y':flip_y,'old_attribute_prefixes_preserved':True}
