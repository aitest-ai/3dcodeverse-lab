"""Append animation data to original GLB/VRM; original BIN prefix and model/VRM metadata stay intact."""
import copy,json,struct,hashlib
from pathlib import Path

def read(p):
 raw=Path(p).read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);binary=raw[28+n:];return doc,binary

def write(path,doc,binary):
 j=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode();j+=b' '*(-len(j)%4);binary+=b'\0'*(-len(binary)%4);raw=struct.pack('<4sII',b'glTF',2,28+len(j)+len(binary))+struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(binary),b'BIN\0')+binary;Path(path).write_bytes(raw);return hashlib.sha256(raw).hexdigest()

class Overlay:
 def __init__(self,path,wrapper):
  self.doc,self.binary=read(path);self.original_binary_sha256=hashlib.sha256(self.binary).hexdigest();self.original_binary_bytes=len(self.binary);self.wrapper=len(self.doc['nodes']);roots=self.doc['scenes'][self.doc.get('scene',0)]['nodes'];self.doc['nodes'].append({'name':'StudioRootMotion_v05','children':roots,**wrapper});self.doc['scenes'][self.doc.get('scene',0)]['nodes']=[self.wrapper];self.node_names={n.get('name'):i for i,n in enumerate(self.doc['nodes'])}
 def accessor(self,rows,typ):
  flat=[x for row in rows for x in row];data=struct.pack('<'+'f'*len(flat),*flat);offset=len(self.binary);self.binary+=data;view=len(self.doc.setdefault('bufferViews',[]));self.doc['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(data)});a={'bufferView':view,'componentType':5126,'count':len(rows),'type':typ}
  if typ=='SCALAR':a.update(min=[min(flat)],max=[max(flat)])
  index=len(self.doc.setdefault('accessors',[]));self.doc['accessors'].append(a);return index
 def animation(self,name,times,frames):
  time=self.accessor([[t] for t in times],'SCALAR');a={'name':name,'samplers':[],'channels':[]}
  for node in frames[0]:
   for prop,kind in [('translation','VEC3'),('rotation','VEC4'),('scale','VEC3')]:
    values=[f[node][prop] for f in frames]
    if prop=='rotation':
     for i in range(1,len(values)):
      if sum(x*y for x,y in zip(values[i-1],values[i]))<0:values[i]=[-x for x in values[i]]
    output=self.accessor(values,kind);sampler=len(a['samplers']);a['samplers'].append({'input':time,'output':output,'interpolation':'LINEAR'});a['channels'].append({'sampler':sampler,'target':{'node':int(node),'path':prop}})
  self.doc['animations']=[x for x in self.doc.get('animations',[]) if x.get('name')!=name]+[a]
 def save(self,path):
  self.doc['buffers']=[{'byteLength':len(self.binary)}];return write(path,self.doc,self.binary)
