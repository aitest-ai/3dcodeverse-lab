"""Conservative base-texture alpha bounds; never a full collision/LOD certificate."""
import bpy,numpy as np,hashlib,math
from v18.accessors import values

def triangles(overlay):
 result=[]
 for p in overlay.doc['meshes'][1]['primitives']:
  ids=[x[0] for x in values(overlay,p['indices'])]
  result.extend({'vertices':ids[i:i+3],'material':p['material']} for i in range(0,len(ids),3))
 return result

def alpha_bounds(overlay,halo=2):
 images={hashlib.sha256(im.packed_file.data).hexdigest():im for im in bpy.data.images if im.packed_file};cache={};uv=values(overlay,overlay.doc['meshes'][1]['primitives'][0]['attributes']['TEXCOORD_0']);rows=[]
 for t in triangles(overlay):
  mi=t['material'];mat=overlay.doc['extensions']['VRM']['materialProperties'][mi];blend=mat['floatProperties'].get('_BlendMode',0);cutoff=mat['floatProperties'].get('_Cutoff',.5) if blend==1 else 0.
  if blend==0:rows.append({'max_alpha':1.,'potentially_visible':True,'mode':'opaque'});continue
  if mi not in cache:
   tex=mat['textureProperties']['_MainTex'];im=overlay.doc['images'][overlay.doc['textures'][tex]['source']];v=overlay.doc['bufferViews'][im['bufferView']];raw=overlay.binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];native=images[hashlib.sha256(raw).hexdigest()];w,h=native.size;a=np.empty(w*h*4,dtype=np.float32);native.pixels.foreach_get(a);cache[mi]=a.reshape(h,w,4)[::-1,:,3].copy()
  a=cache[mi];h,w=a.shape;vs=np.array([uv[i] for i in t['vertices']]);lo=vs.min(axis=0);hi=vs.max(axis=0)
  if np.any(lo<0) or np.any(hi>1):rows.append({'max_alpha':1.,'potentially_visible':True,'mode':'UV outside base tile; conservatively visible'});continue
  x0=max(0,math.floor(lo[0]*w)-halo);x1=min(w,math.ceil(hi[0]*w)+halo+1);y0=max(0,math.floor(lo[1]*h)-halo);y1=min(h,math.ceil(hi[1]*h)+halo+1);m=float(a[y0:y1,x0:x1].max());rows.append({'max_alpha':m,'potentially_visible':m>=cutoff if blend==1 else m>0,'mode':'cutout' if blend==1 else 'blend','cutoff':cutoff,'bbox_pixels':[x0,y0,x1,y1]})
 return rows

class SurfaceAlpha:
 """Sample original material alpha along actual triangle intersection segments.
 Uses base-level bilinear alpha at <=0.25 texel intervals; finite, not a solid-volume certificate.
 """
 def __init__(self,overlay):
  self.tris=triangles(overlay);self.uv=np.array(values(overlay,overlay.doc['meshes'][1]['primitives'][0]['attributes']['TEXCOORD_0']));self.materials={};packed={hashlib.sha256(im.packed_file.data).hexdigest():im for im in bpy.data.images if im.packed_file}
  for mi in {t['material'] for t in self.tris}:
   m=overlay.doc['extensions']['VRM']['materialProperties'][mi];blend=m['floatProperties'].get('_BlendMode',0);cutoff=m['floatProperties'].get('_Cutoff',.5) if blend==1 else 0.;a=None
   if blend!=0:
    tex=m['textureProperties']['_MainTex'];im=overlay.doc['images'][overlay.doc['textures'][tex]['source']];view=overlay.doc['bufferViews'][im['bufferView']];raw=overlay.binary[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']];native=packed[hashlib.sha256(raw).hexdigest()];w,h=native.size;pixels=np.empty(w*h*4,dtype=np.float32);native.pixels.foreach_get(pixels);a=pixels.reshape(h,w,4)[::-1,:,3].copy()
   self.materials[mi]=(blend,cutoff,a)
 def opaque(self,mi,uv):
  blend,cutoff,a=self.materials[mi]
  if blend==0:return np.ones(len(uv),dtype=bool)
  h,w=a.shape;x=np.clip(uv[:,0]*w-.5,0,w-1);y=np.clip(uv[:,1]*h-.5,0,h-1);x0=np.floor(x).astype(int);y0=np.floor(y).astype(int);x1=np.minimum(w-1,x0+1);y1=np.minimum(h-1,y0+1);dx=x-x0;dy=y-y0;value=(1-dy)*((1-dx)*a[y0,x0]+dx*a[y0,x1])+dy*((1-dx)*a[y1,x0]+dx*a[y1,x1]);return value>=cutoff if blend==1 else value>0
 def crossing_visible(self,vs,ia,ib):
  from mathutils.geometry import intersect_ray_tri,barycentric_transform
  from mathutils import Vector
  ta,tb=self.tris[ia],self.tris[ib];a,b=ta['vertices'],tb['vertices'];points=[]
  for first,second in [(a,b),(b,a)]:
   tri=[vs[i] for i in second]
   for j in range(3):
    p,q=vs[first[j]],vs[first[(j+1)%3]];d=q-p
    if d.length_squared<1e-16:continue
    hit=intersect_ray_tri(*tri,d,p,True)
    if hit is not None and -1e-6<=(hit-p).dot(d)/d.length_squared<=1+1e-6 and all((hit-r).length_squared>1e-16 for r in points):points.append(hit)
  if not points:return False
  endpoints=max(((x,y) for x in points for y in points),key=lambda p:(p[0]-p[1]).length_squared);uv=[];density=0
  for t in [ta,tb]:
   ids=t['vertices'];src=[vs[i] for i in ids];dst=[Vector((*self.uv[i],0)) for i in ids];coords=np.array([list(barycentric_transform(p,*src,*dst))[:2] for p in endpoints]);uv.append(coords);im=self.materials[t['material']][2]
   if im is not None:density=max(density,float(np.linalg.norm((coords[1]-coords[0])*np.array([im.shape[1],im.shape[0]]))))
  n=max(3,math.ceil(density*4)+1);t=np.linspace(0,1,n)[:,None];ua=uv[0][0]+t*(uv[0][1]-uv[0][0]);ub=uv[1][0]+t*(uv[1][1]-uv[1][0]);return bool(np.any(self.opaque(ta['material'],ua)&self.opaque(tb['material'],ub)))
