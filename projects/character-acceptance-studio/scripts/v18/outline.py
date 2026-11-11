"""Local MToon outline-width mask. Geometry defects remain separate evidence."""
import math,struct,zlib,json
MASK_NAME='V18_Shoulder_Outline_Width'
def png_mask(uv_triangles,size=2048,feather=10):
 pixels=bytearray([255])*(size*size)
 def segment_distance(px,py,a,b):
  dx,dy=b[0]-a[0],b[1]-a[1];u=max(0,min(1,((px-a[0])*dx+(py-a[1])*dy)/(dx*dx+dy*dy+1e-12)));return math.hypot(px-a[0]-u*dx,py-a[1]-u*dy)
 for uv in uv_triangles:
  points=[(u*size,v*size) for u,v in uv];a,b,c=points
  for y in range(max(0,math.floor(min(p[1] for p in points)-feather)),min(size,math.ceil(max(p[1] for p in points)+feather))):
   for x in range(max(0,math.floor(min(p[0] for p in points)-feather)),min(size,math.ceil(max(p[0] for p in points)+feather))):
    px,py=x+.5,y+.5;signs=[(q[0]-p[0])*(py-p[1])-(q[1]-p[1])*(px-p[0]) for p,q in [(a,b),(b,c),(c,a)]];inside=min(signs)>=0 or max(signs)<=0;distance=0 if inside else min(segment_distance(px,py,p,q) for p,q in [(a,b),(b,c),(c,a)]);t=min(1,distance/feather);value=round(255*t*t*(3-2*t));i=y*size+x;pixels[i]=min(pixels[i],value)
 def chunk(name,data):return struct.pack('>I',len(data))+name+data+struct.pack('>I',zlib.crc32(name+data)&0xffffffff)
 # Grayscale PNG: all sampled color channels carry the same multiplier.
 scan=b''.join(b'\0'+bytes(pixels[y*size:(y+1)*size]) for y in range(size));png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',size,size,8,0,0,0,0))+chunk(b'IDAT',zlib.compress(scan,9))+chunk(b'IEND',b'')
 return png,{'width':size,'height':size,'feather_pixels':feather,'modified_pixels':sum(x<255 for x in pixels),'coverage_fraction':sum(x<255 for x in pixels)/len(pixels),'method':'Feathered UV patch over audited internal shoulder folds; original color textures and outline width preserved elsewhere','geometry_collision_status':'unchanged by this material correction'}
def append(overlay,png):
 padding=(-len(overlay.binary))%4;overlay.binary+=b'\0'*padding;offset=len(overlay.binary);overlay.binary+=png;overlay.binary+=b'\0'*((-len(overlay.binary))%4);view=len(overlay.doc['bufferViews']);overlay.doc['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(png)});im=len(overlay.doc['images']);overlay.doc['images'].append({'name':MASK_NAME,'mimeType':'image/png','bufferView':view});sampler=len(overlay.doc.setdefault('samplers',[]));overlay.doc['samplers'].append({'magFilter':9729,'minFilter':9987,'wrapS':33071,'wrapT':33071});tex=len(overlay.doc['textures']);overlay.doc['textures'].append({'source':im,'sampler':sampler,'name':MASK_NAME});changed=[]
 for i,m in enumerate(overlay.doc['extensions']['VRM']['materialProperties']):
  if 'Tops' in m['name']:
   assert '_OutlineWidthTexture' not in m['textureProperties'];m['textureProperties']['_OutlineWidthTexture']=tex;changed.append(i)
 assert changed
 return {'image_index':im,'texture_index':tex,'materials':changed,'native_image':MASK_NAME}
