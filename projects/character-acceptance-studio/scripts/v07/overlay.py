"""Replace only explicitly named clips; retain every old binary byte and all non-animation scene definitions."""
import struct
from v06.motion_overlay import MotionOverlay
class ClipOverlay(MotionOverlay):
 def accessor(self,values,kind):
  flat=[v for row in values for v in row];raw=struct.pack('<'+'f'*len(flat),*flat);offset=len(self.binary);self.binary+=raw;view=len(self.doc['bufferViews']);self.doc['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(raw)});a={'bufferView':view,'componentType':5126,'count':len(values),'type':kind}
  if kind=='SCALAR':a.update(min=[min(flat)],max=[max(flat)])
  self.doc['accessors'].append(a);return len(self.doc['accessors'])-1
 def replace_clip(self,name,times,frames):
  time=self.accessor([[t] for t in times],'SCALAR');a={'name':name,'samplers':[],'channels':[]}
  for node in frames[0]:
   for prop,kind in [('translation','VEC3'),('rotation','VEC4'),('scale','VEC3')]:
    values=[f[node][prop][:] for f in frames]
    if prop=='rotation':
     for i in range(1,len(values)):
      if sum(x*y for x,y in zip(values[i-1],values[i]))<0:values[i]=[-v for v in values[i]]
    out=self.accessor(values,kind);a['channels'].append({'sampler':len(a['samplers']),'target':{'node':node,'path':prop}});a['samplers'].append({'input':time,'output':out,'interpolation':'LINEAR'})
  animations=self.doc.setdefault('animations',[]);idx=next((i for i,c in enumerate(animations) if c['name']==name),None)
  if idx is None:animations.append(a)
  else:animations[idx]=a
