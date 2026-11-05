"""Patch selected animation outputs while preserving the entire previous GLB BIN and all other channels."""
import copy,struct,hashlib
from v05.overlay import read,write
class MotionOverlay:
 def __init__(self,source):
  self.doc,self.binary=read(source);self.prefix_bytes=len(self.binary);self.prefix_sha256=hashlib.sha256(self.binary).hexdigest();self.changed=[]
 def values(self,index):
  a=self.doc['accessors'][index];v=self.doc['bufferViews'][a['bufferView']];size={'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']];offset=v.get('byteOffset',0)+a.get('byteOffset',0);return [list(struct.unpack_from('<'+'f'*size,self.binary,offset+i*size*4)) for i in range(a['count'])]
 def patch(self,name,frames,nodes,properties=('translation','rotation','scale'),threshold=2e-6):
  animation=next(a for a in self.doc['animations'] if a['name']==name)
  for c in animation['channels']:
   node=c['target']['node'];prop=c['target']['path']
   if node not in nodes or prop not in properties:continue
   sampler=animation['samplers'][c['sampler']];old_output=sampler['output'];previous=self.values(sampler['output']);values=[f[node][prop] for f in frames];assert len(values)==len(previous)
   if prop=='rotation':
    if sum(x*y for x,y in zip(values[0],previous[0]))<0:values[0]=[-x for x in values[0]]
    for i in range(1,len(values)):
     if sum(x*y for x,y in zip(values[i-1],values[i]))<0:values[i]=[-x for x in values[i]]
   error=max(abs(x-y) for a,b in zip(values,previous) for x,y in zip(a,b))
   if error<threshold:continue
   offset=len(self.binary);flat=[v for row in values for v in row];data=struct.pack('<'+'f'*len(flat),*flat);self.binary+=data;view=len(self.doc['bufferViews']);self.doc['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(data)});index=len(self.doc['accessors']);self.doc['accessors'].append({'bufferView':view,'componentType':5126,'count':len(values),'type':'VEC4' if prop=='rotation' else 'VEC3'});sampler['output']=index;self.changed.append({'clip':name,'node':node,'bone':self.doc['nodes'][node]['name'],'path':prop,'previous_output':old_output,'maximum_component_change':error})
 def save(self,path):self.doc['buffers'][0]['byteLength']=len(self.binary);return write(path,self.doc,self.binary)
