#!/usr/bin/env python3
"""V005 R1 extension: frozen V004 R1 -> two named OSM buildings + next OSM route segment.

No source edits. All facades/roof heights/materials/properties are ORIGINAL estimates,
not site survey or faithful reproduction. The model is intentionally exterior-only.
Coords: GLB & collision Three EUS (x east,y up,z south); OSM footprint has x east, north.
"""
from __future__ import annotations
import json,math,hashlib,random,os
from pathlib import Path
from collections import defaultdict
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual.texture import TextureVisuals
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(os.environ.get('DATE_V005_ROOT',str(Path(__file__).resolve().parent.parent/'runtime')))
DIST=ROOT/'dist'; ASSETS=DIST/'assets'
BASE_VIEW=json.loads((ROOT/'V004_source_view.json').read_text())
BASE_ROUTE=BASE_VIEW['route'];BUILDINGS={b['id']:b for b in BASE_VIEW['buildings']}
assert abs(BASE_ROUTE[-1]['s']-130.01461217900092)<1.e-6
assert abs(BASE_ROUTE[-1]['x']-42.12494461926742)<1.e-6
assert BASE_VIEW['version']=='V004-merchant-candidate-r1'
RNG=random.Random(2026110105)

# Full OSM centerline is kept in source geometry; these are its next frozen vertices.
start=BASE_ROUTE[-1];target={'x':101.7463863855061,'y':1.3101205339255984,'z':93.9859830694928}
# Height is from frozen V002 GSI DEM, not a straight-line approximation that sinks into hills.
profile_path=Path(__file__).resolve().parent/'v005_dem_profile.json'
profile=json.loads(profile_path.read_text())
assert profile['source_geom_sha256']=='75d672d5296ac28bef25b03423da395027c4b29cf804652239f40e9fc73d408a'
assert profile['schema']=='noboribetsu-date-v005-dem-road-profile/1'
N=len(profile['points'])-1
SEG=[];route=list(BASE_ROUTE)
for i,point in enumerate(profile['points']):
 t=i/N
 q={'x':point['x'],'y':point['center_y'],'z':point['z']}
 assert abs(q['x']-(start['x']*(1-t)+target['x']*t))<1e-6
 assert abs(q['z']-(start['z']*(1-t)+target['z']*t))<1e-6
 if i==0:q={'x':start['x'],'y':start['y'],'z':start['z'],'s':start['s']}
 else:
  q['s']=route[-1]['s']+math.hypot(q['x']-route[-1]['x'],q['z']-route[-1]['z'])
  route.append(q)
 SEG.append({**q,'_left_y':point['left_y'],'_right_y':point['right_y'],'_dem_cross':point['dem_transverse_y']})
assert 196<route[-1]['s']<200

# Colors are all authored locally; 8-bit conversion checked by export.
MATERIALS={
 'road_earth':((.373,.352,.323,1),.98),
 'road_cobbles':((.55,.52,.46,1),.94),
 'edge_patina':((.31,.35,.27,1),.98),
 'foundation_stone':((.42,.43,.40,1),.96),
 'plaster_warm':((.78,.735,.64,1),.98),
 'plaster_cool':((.76,.76,.71,1),.98),
 'plaster_lower':((.61,.57,.50,1),1.0),
 'wood_structure':((.22,.16,.115,1),.91),
 'wood_aged':((.15,.114,.083,1),.93),
 'wood_newer':((.33,.23,.17,1),.87),
 'wood_edges':((.38,.28,.19,1),.96),
 'window_black':((.071,.064,.059,1),.88),
 'shoji_paper':((.67,.657,.605,1),.99),
 'tile_dark':((.218,.24,.248,1),.91),
 'tile_mid':((.29,.305,.308,1),.92),
 'tile_light':((.343,.35,.33,1),.95),
 'tile_worn':((.260,.278,.276,1),.94),
 'ridge_cap':((.22,.24,.238,1),.90),
 'noren_blue':((.23,.315,.35,1),.96),
 'noren_stitch':((.64,.66,.61,1),.98),
 'lantern_wood':((.22,.16,.112,1),.90),
 'lantern_paper':((.63,.59,.46,1),.96),
 }

class Geometry:
 def __init__(self):self.g=defaultdict(lambda:{'v':[],'f':[]});self.objects=[]
 def poly(self,mat,verts,faces):
  s=self.g[mat];base=len(s['v']);s['v'].extend([tuple(float(c) for c in v) for v in verts]);s['f'].extend([tuple(base+int(i) for i in face) for face in faces])
 def quad(self,mat,a,b,c,d,two=False):
  self.poly(mat,[a,b,c,d],[(0,1,2),(0,2,3)]+([(2,1,0),(3,2,0)] if two else []))
 def tri(self,mat,a,b,c):self.poly(mat,[a,b,c],[(0,1,2)])
 def box(self,mat,x,y,z,dx,dy,dz):
  a,b,c=dx/2,dy/2,dz/2
  verts=[(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),
         (x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]
  self.poly(mat,verts,[(0,3,2),(0,2,1),(4,5,6),(4,6,7),(0,4,7),(0,7,3),(1,2,6),(1,6,5),(3,7,6),(3,6,2),(0,1,5),(0,5,4)])
 def put(self,p:tuple,u:tuple,v:tuple,lu:float,lz:float,y:float):
  return (p[0]+u[0]*lu+v[0]*lz,y,p[1]+u[1]*lu+v[1]*lz)
 def lbox(self,mat,p,u,v,lu,lz,y,du,dv,dy):
  a,b=du/2,dv/2;lo,hi=y-dy/2,y+dy/2
  verts=[self.put(p,u,v,lu+uu,lz+zz,yy) for uu,zz,yy in [(-a,-b,lo),(a,-b,lo),(a,-b,hi),(-a,-b,hi),(-a,b,lo),(a,b,lo),(a,b,hi),(-a,b,hi)]]
  self.poly(mat,verts,[(0,3,2),(0,2,1),(4,5,6),(4,6,7),(0,4,7),(0,7,3),(1,2,6),(1,6,5),(3,7,6),(3,6,2),(0,1,5),(0,5,4)])
 def lcylinder_u(self,mat,p,u,v,u0,u1,depth,y,r,n=10):
  def ring(t):return [self.put(p,u,v,t,depth+r*math.cos(math.tau*i/n),y+r*math.sin(math.tau*i/n)) for i in range(n)]
  verts=ring(u0)+ring(u1);faces=[]
  for i in range(n):j=(i+1)%n;faces.extend([(i,j,n+j),(i,n+j,n+i)])
  faces.extend([(0,k+1,k) for k in range(1,n-1)])
  faces.extend([(n,n+k,n+k+1) for k in range(1,n-1)])
  self.poly(mat,verts,faces)
 def save(self,p):
  scene=trimesh.Scene();stats={}
  for key,mesh in self.g.items():
   vv=np.asarray(mesh['v'],dtype=np.float32);ff=np.asarray(mesh['f'],dtype=np.int64)
   if not len(vv) or not len(ff):raise RuntimeError('Empty group: '+key)
   tri=trimesh.Trimesh(vertices=vv,faces=ff,process=False)
   rgba,rough=MATERIALS[key]
   tri.visual=TextureVisuals(material=PBRMaterial(name=key,baseColorFactor=[round(255*c) for c in rgba],metallicFactor=0.0,roughnessFactor=rough,doubleSided=True))
   scene.add_geometry(tri,geom_name=key,node_name=key)
   stats[key]={'triangles':len(ff),'vertices':len(vv)}
  p.write_bytes(scene.export(file_type='glb'))
  return stats

# V004 ends with a 6m wide road; use exactly matching width for the V005 seam.
road=Geometry();walk_v=[];walk_f=[]
def cross(p,dx,dz,dist,offset=0.0):
 l=math.hypot(dx,dz);nx,nz=-dz/l,dx/l
 surface=(p['_left_y'] if dist>0 else p['_right_y']) if abs(dist)>.01 else p['y']
 return (p['x']+nx*dist,surface+offset,p['z']+nz*dist)
for i,(a,b) in enumerate(zip(SEG,SEG[1:])):
 dx=b['x']-a['x'];dz=b['z']-a['z'];width=3.0
 q=[cross(a,dx,dz,width,.018),cross(a,dx,dz,-width,.018),cross(b,dx,dz,width,.018),cross(b,dx,dz,-width,.018)]
 # A seven-vertex transverse DEM mesh prevents the old two-edge plane from sinking into
 # the nonlinear frozen terrain. This is visual-only; collision keeps the same source top.
 offsets=profile['transverse_offsets_m']
 def visible_cross(p,side):
  dem=p['_dem_cross'][offsets.index(side)]
  # 3.8 cm render clearance (not measured road thickness) avoids z-fighting and terrain poke-through.
  return (p['x']-dz/math.hypot(dx,dz)*side, max(p['y'],dem)+.038,
          p['z']+dx/math.hypot(dx,dz)*side)
 for n in range(len(offsets)-1):
  q0=visible_cross(a,offsets[n]);q1=visible_cross(a,offsets[n+1])
  q2=visible_cross(b,offsets[n+1]);q3=visible_cross(b,offsets[n])
  road.quad('road_earth',q0,q1,q2,q3,two=True)
 for side in [-1,1]:
  q0=cross(a,dx,dz,side*(width-.08),.022);q1=cross(b,dx,dz,side*(width-.08),.022)
  q2=cross(b,dx,dz,side*(width+.19),.026);q3=cross(a,dx,dz,side*(width+.19),.026)
  road.quad('edge_patina',q0,q1,q2,q3,two=True)
  if i%3==0:
   mid={k:(a[k]+b[k])/2 for k in ('x','y','z','_left_y','_right_y')}
   pos=cross(mid,dx,dz,width-.05,.046)
   pos2=cross(mid,dx,dz,width+.15,.046)
   p0=(pos[0]-.15,pos[1],pos[2]-.02);p1=(pos[0]+.15,pos[1],pos[2]+.02)
   p2=(pos2[0]+.15,pos2[1],pos2[2]+.02);p3=(pos2[0]-.15,pos2[1],pos2[2]-.02)
   road.quad('road_cobbles',p0,p1,p2,p3)
 t=len(walk_v);walk_v.extend([cross(a,dx,dz,width),cross(a,dx,dz,-width),cross(b,dx,dz,width),cross(b,dx,dz,-width)])
 walk_f.extend([(t,t+1,t+2),(t+2,t+1,t+3)])
# Explicit circular junction patch; same elevation as previous path end (not a surveyed plaza).
center=SEG[0];t=len(walk_v);walk_v.append((center['x'],center['y'],center['z']))
for i in range(40):walk_v.append((center['x']+3.02*math.cos(math.tau*i/40),center['y'],center['z']+3.02*math.sin(math.tau*i/40)))
for i in range(40):walk_f.append((t,t+1+i,t+1+(i+1)%40))
# Omit the old flat render fan: it sat below the nonplanar V002 terrain and caused
# apparent grass cutouts. Only the original collision fan remains as a turning aid.
road_stats=road.save(ASSETS/'v005_east_road.glb')

# Choose footprint edge geometrically closest to confirmed road centerline, not by guessed cardinal direction.
def distance_to_segment(q,a,b):
 dx,dz=b[0]-a[0],b[1]-a[1];l=dx*dx+dz*dz
 t=max(0,min(1,((q[0]-a[0])*dx+(q[1]-a[1])*dz)/l))
 return math.hypot(q[0]-(a[0]+t*dx),q[1]-(a[1]+t*dz))
def near_route(p):return min(distance_to_segment(p,(a['x'],a['z']),(b['x'],b['z'])) for a,b in zip(SEG,SEG[1:]))
def orientation(building):
 poly=[(x,-north) for x,north in building['polygon']]
 candidates=[]
 cx=sum(p[0] for p in poly)/len(poly);cz=sum(p[1] for p in poly)/len(poly)
 for i in range(len(poly)):
  a,b=poly[i],poly[(i+1)%len(poly)];mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
  L=math.dist(a,b);candidates.append((near_route(mid),-L,i,a,b))
 distance,negL,i,a,b=min(candidates)
 u=((b[0]-a[0])/-negL,(b[1]-a[1])/-negL)
 n=(-u[1],u[0]);delta=(cx-(a[0]+b[0])/2,cz-(a[1]+b[1])/2)
 v=n if delta[0]*n[0]+delta[1]*n[1]>0 else (-n[0],-n[1])
 front=((a[0]+b[0])/2,(a[1]+b[1])/2)
 depth=max((p[0]-front[0])*v[0]+(p[1]-front[1])*v[1] for p in poly)
 return {'p':front,'u':u,'v':v,'length':-negL,'depth':depth,'front_edge':i,'front_to_route_m':distance}

houses=Geometry();signs=trimesh.Scene();posts=[];reports=[]
PLANS=[('way/283905573','わらじ屋','food'),('way/283905580','うつろい館','costume')]

def placard(name,role,p,u,v,lu,lz,y,front=True):
 fontpath='/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'
 if not Path(fontpath).is_file():raise FileNotFoundError('NotoSerifCJK needed only for authored Japanese sign texture')
 img=Image.new('RGBA',(320,720),(34,29,25,255));d=ImageDraw.Draw(img)
 d.rounded_rectangle((17,17,303,703),radius=14,fill=(202,162,102,255),outline=(52,42,32,255),width=14)
 d.rectangle((38,38,281,682),outline=(96,74,43,255),width=3)
 f=ImageFont.truetype(fontpath,84)
 vertical='\n'.join(list(name));bounds=d.multiline_textbbox((0,0),vertical,font=f,spacing=-2)
 th=bounds[3]-bounds[1];tw=bounds[2]-bounds[0]
 if th>590:
  f=ImageFont.truetype(fontpath,round(84*570/th));bounds=d.multiline_textbbox((0,0),vertical,font=f,spacing=-2);tw=bounds[2]-bounds[0];th=bounds[3]-bounds[1]
 d.multiline_text(((320-tw)/2-bounds[0],(720-th)/2-bounds[1]),vertical,font=f,fill=(34,32,27),spacing=-2)
 width=.63;height=1.5
 # two-sided face, front plane faces public road (away from building)
 vertices=[houses.put(p,u,v,lu-width/2,lz,y-height/2),houses.put(p,u,v,lu+width/2,lz,y-height/2),houses.put(p,u,v,lu+width/2,lz,y+height/2),houses.put(p,u,v,lu-width/2,lz,y+height/2)]
 uv=np.array([[0,0],[1,0],[1,1],[0,1]],dtype=np.float32)
 mesh=trimesh.Trimesh(vertices=vertices,faces=[[0,1,2],[0,2,3]],process=False,visual=TextureVisuals(uv=uv,material=PBRMaterial(name='V005_original_'+role+'_sign',baseColorTexture=img,metallicFactor=0.,roughnessFactor=.88,doubleSided=True)))
 signs.add_geometry(mesh,geom_name=role+'_sign')


def build_shop(building_id,name,role):
 building=BUILDINGS[building_id];o=orientation(building)
 p,u,v=o['p'],o['u'],o['v'];L=min(o['length'],12.5);D=o['depth'];Y=float(building['base'])
 # Real building footprints ~9m square, author estimates facade max 6m high plus roof.
 h_eave=4.65 if role=='food' else 5.02;h_ridge=h_eave+(1.28 if role=='food' else 1.42)
 plaster='plaster_warm' if role=='food' else 'plaster_cool'
 wood='wood_newer' if role=='food' else 'wood_structure'
 # Wall shell and foundation inset: no accessible interior.
 houses.lbox(plaster,p,u,v,0,D/2,Y+h_eave/2,L+.12,D,h_eave)
 houses.lbox('foundation_stone',p,u,v,0,D/2,Y+.34,L+.22,D+.16,.68)
 houses.lbox('plaster_lower',p,u,v,0,.14,Y+1.01,L+.21,.35,1.55)
 # Exterior framework, no doors on undocumented rear.
 for yy in [1.0,2.78,4.38]:houses.lbox('wood_structure',p,u,v,0,-.2,Y+yy,L+.10,.18,.11)
 for lu in np.linspace(-L/2+.15,L/2-.15,max(6,round(L/1.22))):
  houses.lbox(wood,p,u,v,lu,-.26,Y+2.43,.14,.20,4.32)
  houses.lbox('wood_edges',p,u,v,lu,-.374,Y+1.0,.065,.035,.10)
 # Ground floor: closed opaque doors, woven timber lattices and narrow shoji panes.
 bays=5 if role=='food' else 4
 for i in range(bays):
  segL=(L-.6)/bays;lu=-L/2+.3+(i+.5)*segL
  if i in ((bays//2,) if role=='food' else (1,2)):
   houses.lbox('wood_aged',p,u,v,lu,-.35,Y+1.57,segL-.14,.06,2.5)
   houses.lbox('wood_edges',p,u,v,lu,-.405,Y+1.57,.058,.045,2.47)
   houses.lbox('wood_edges',p,u,v,lu,-.41,Y+.42,segL-.2,.052,.09)
  else:
   houses.lbox('window_black',p,u,v,lu,-.35,Y+1.8,segL-.12,.05,1.88)
   houses.lbox('shoji_paper',p,u,v,lu,-.39,Y+1.82,segL-.24,.025,1.76)
   for k in range(5):
    xx=lu-(segL-.21)/2+k*(segL-.21)/4
    houses.lbox('wood_aged',p,u,v,xx,-.445,Y+1.8,.049,.035,1.86)
   for yy in (1.35,1.99,2.60):houses.lbox('wood_edges',p,u,v,lu,-.445,Y+yy,segL-.15,.05,.055)
 # Narrow upper street-front grill, with recessed black inset and cross-framing.
 houses.lbox('window_black',p,u,v,0,-.33,Y+3.75,L-.66,.04,.78)
 for lu in np.linspace(-L/2+.40,L/2-.40,max(12,round(L/.27))):
  houses.lbox('wood_aged',p,u,v,lu,-.385,Y+3.75,.052,.07,.85)
 houses.lbox('wood_edges',p,u,v,0,-.4,Y+3.32,L-.58,.10,.11)
 houses.lbox('wood_edges',p,u,v,0,-.4,Y+4.20,L-.58,.10,.12)
 # Blank rear face treatment: simple wood construction, no invented opening.
 for lu in np.linspace(-L/2+.22,L/2-.22,max(5,round(L/1.4))):
  houses.lbox(wood,p,u,v,lu,D+.22,Y+2.52,.13,.22,4.36)
 for yy in (1.03,2.77,4.35):houses.lbox('wood_structure',p,u,v,0,D+.20,Y+yy,L+.14,.19,.12)
 for side in [-1,1]:
  lu=side*(L/2+.105)
  for yy in (1.20,2.81,4.20):houses.lbox(wood,p,u,v,lu,D/2,Y+yy,.16,D+.14,.13)
  for zz in np.linspace(.4,D-.3,max(6,round(D/.85))):houses.lbox('wood_structure',p,u,v,lu,zz,Y+2.36,.15,.065,4.42)
 # Real two-plane gabled tiled roof: ridge on U axis, roof descends toward street/rear.
 d0=-.65;d1=D+.65;mid=(d0+d1)/2
 for zlo,zhi,ylo,yhi in ((d0,mid,h_eave,h_ridge),(mid,d1,h_ridge,h_eave)):
  houses.quad('wood_aged',houses.put(p,u,v,-L/2-.43,zlo,Y+ylo),houses.put(p,u,v,L/2+.43,zlo,Y+ylo),houses.put(p,u,v,L/2+.43,zhi,Y+yhi),houses.put(p,u,v,-L/2-.43,zhi,Y+yhi),True)
  nu=max(10,math.ceil((L+.86)/.32));nv=max(7,math.ceil(abs(zhi-zlo)/.35))
  for iu in range(nu):
   x0=-L/2-.43+(L+.86)*iu/nu;x1=-L/2-.43+(L+.86)*(iu+1)/nu
   for iv in range(nv):
    z0=zlo+(zhi-zlo)*iv/nv;z1=zlo+(zhi-zlo)*(iv+1)/nv
    yy0=Y+ylo+(yhi-ylo)*iv/nv+.020
    yy1=Y+ylo+(yhi-ylo)*(iv+1)/nv+.020
    variation=('tile_worn' if (iu*5+iv*17)%11==0 else RNG.choice(['tile_mid','tile_dark','tile_mid','tile_light']))
    xmid=(x0+x1)/2
    verts=[houses.put(p,u,v,x0,z0,yy0),houses.put(p,u,v,xmid,z0,yy0+.035),houses.put(p,u,v,x1,z0,yy0),
           houses.put(p,u,v,x0,z1,yy1),houses.put(p,u,v,xmid,z1,yy1+.032),houses.put(p,u,v,x1,z1,yy1)]
    houses.poly(variation,verts,[(0,3,4),(0,4,1),(1,4,5),(1,5,2)])
  houses.lcylinder_u('ridge_cap',p,u,v,-L/2-.43,L/2+.43,zlo,Y+ylo,.075,8)
 houses.lcylinder_u('ridge_cap',p,u,v,-L/2-.43,L/2+.43,mid,Y+h_ridge+.08,.17,10)
 for iu in np.linspace(-L/2-.38,L/2+.38,max(8,math.ceil(L/.46))):
  houses.lbox('ridge_cap',p,u,v,iu,mid,Y+h_ridge+.18,.15,.32,.15)
 # Triangular gables, back and front eaves accent.
 for lu in [-L/2-.43,L/2+.43]:
  houses.tri('plaster_lower',houses.put(p,u,v,lu,d0,Y+h_eave),houses.put(p,u,v,lu,mid,Y+h_ridge),houses.put(p,u,v,lu,d1,Y+h_eave))
  for v0 in np.linspace(d0+.35,d1-.35,max(8,round(D/.55))):
   yy=h_eave+(h_ridge-h_eave)*(1-abs(v0-mid)/max(.01,(d1-d0)/2))
   if yy-h_eave>.08:houses.lbox('wood_structure',p,u,v,lu,v0,Y+(h_eave+yy)/2,.10,.05,max(.1,yy-h_eave))
 # Arcade eave and real posts, intentionally outside the existing OSM obstacle.
 porch=-1.17;roof_out=-1.72
 houses.quad('wood_aged',houses.put(p,u,v,-L/2-.45,-.27,Y+3.49),houses.put(p,u,v,L/2+.45,-.27,Y+3.49),houses.put(p,u,v,L/2+.45,roof_out,Y+3.05),houses.put(p,u,v,-L/2-.45,roof_out,Y+3.05),True)
 nu=max(12,math.ceil((L+.9)/.29));nv=6
 for iu in range(nu):
  x0=-L/2-.45+(L+.9)*iu/nu;x1=-L/2-.45+(L+.9)*(iu+1)/nu
  for iv in range(nv):
   t0=iv/nv;t1=(iv+1)/nv
   z0=-.27+(roof_out+.27)*t0;z1=-.27+(roof_out+.27)*t1
   h0=Y+3.51-.44*t0;h1=Y+3.51-.44*t1
   mat='tile_worn' if (iu*9+iv*13)%9==0 else 'tile_mid'
   houses.quad(mat,houses.put(p,u,v,x0,z0,h0),houses.put(p,u,v,x1,z0,h0),houses.put(p,u,v,x1,z1,h1),houses.put(p,u,v,x0,z1,h1),True)
 houses.lcylinder_u('ridge_cap',p,u,v,-L/2-.47,L/2+.47,roof_out,Y+3.08,.092,9)
 nposts=5 if role=='food' else 4
 for i in range(nposts):
  lu=-L/2+.32+(L-.64)*i/(nposts-1)
  houses.lbox('foundation_stone',p,u,v,lu,porch,Y+.15,.39,.41,.30)
  houses.lbox('wood_structure',p,u,v,lu,porch,Y+1.66,.17,.17,3.25)
  houses.lbox('wood_newer',p,u,v,lu,porch,Y+3.28,.26,.28,.19)
  houses.lbox('wood_edges',p,u,v,lu,porch+.22,Y+3.04,.10,.57,.13)
  wx,wz=houses.put(p,u,v,lu,porch,Y) [::2] # x/z in world
  posts.append({'id':f'V005_{role}_porch_{i}','stage':'B','polygon':[[wx-.13,wz-.13],[wx+.13,wz-.13],[wx+.13,wz+.13],[wx-.13,wz+.13]],'minY':Y-.2,'maxY':Y+3.5,'source':'artist-estimated porch column (original GLB)'})
 # Brand distinction: cloth noren for food outlet, understated framed wood boards at costume house.
 if role=='food':
  npan=4;half=(L-1.)/(2*npan)
  for j in range(npan):
   midu=-L/2+.5+(j+.5)*(L-1)/npan
   lo=Y+2.30 + .045*(j%2);top=Y+3.15
   for k in range(8):
    a=midu-half+(2*half)*k/8;b=midu-half+(2*half)*(k+1)/8
    def cloth(x,y,phase):return houses.put(p,u,v,x,-.48+.034*math.sin((x-midu)*3.5+phase),y)
    houses.quad('noren_blue',cloth(a,top,0),cloth(b,top,0),cloth(b,lo,1.4),cloth(a,lo,1.4),True)
   houses.lbox('noren_stitch',p,u,v,midu,-.51,Y+3.16,2*half-.03,.03,.032)
 else:
  for lu in [-L*.31,L*.31]:
   houses.lbox('wood_newer',p,u,v,lu,-.54,Y+2.92,1.4,.12,.38)
   for s in (-.5,.5):houses.lbox('wood_edges',p,u,v,lu+s*.88,-.57,Y+2.92,.065,.07,.42)
 # Actual road-facing signage is original texture created here, NOT official copyrighted graphics.
 lu=(L/2-.70) if role=='food' else (-L/2+.70)
 houses.lbox('wood_structure',p,u,v,lu,-1.47,Y+3.04,.105,.13,1.92)
 houses.lbox('wood_newer',p,u,v,lu,-1.41,Y+4.05,.92,.16,.12)
 placard(name,role,p,u,v,lu,-1.54,Y+2.93)
 reports.append({'osm_id':building_id,'name':name,'use_verified':('food shop (2025 refit)' if role=='food' else 'period-costume photo/rental'),
                 'source':'V002 frozen OSM polygon + Edo-trip official facility usage; façade dimensions author-estimated',
                 'basis':{'front_edge':o['front_edge'],'front_to_route_m':o['front_to_route_m'],'footprint_long_edge_m':L,'depth_approx_m':D},
                 'height_estimated_m':h_ridge,'porch_posts':nposts,'interior':'NOT_BUILT',
                 'official_reference':'https://edo-trip.jp/facility/waraji-ya/' if role=='food' else 'https://edo-trip.jp/facility/utsuroi-kan/'})

for bid,name,role in PLANS:build_shop(bid,name,role)
facade_stats=houses.save(ASSETS/'v005_east_facades.glb')
(ASSETS/'v005_east_signs.glb').write_bytes(signs.export(file_type='glb'))

collision={
 'schema':'noboribetsu-date-v005-east-extension/1',
 'axes':'Three EUS',
 'walkable':[{'id':'V005_OSM_road_to_waypoint5','stage':'both','vertices':[list(v) for v in walk_v],'triangles':walk_f,
              'source':'Frozen V002 OSM centerline, endpoints GSI terrain estimates; 6m width estimated'}],
 'obstacles':posts,
 'untouched_v004_collision_sha256':hashlib.sha256((DIST/'extension_collision.json').read_bytes()).hexdigest(),
 'no_interiors':True,
 'route_status':'OSM snapped, V002 DEM-profiled, width estimated; not surveyed accessibility'
}
(DIST/'v005_collision.json').write_text(json.dumps(collision,ensure_ascii=False,separators=(',',':'))+'\n')
models={}
for p in ['v005_east_road.glb','v005_east_facades.glb','v005_east_signs.glb']:
 file=ASSETS/p;models[p]={'path':'assets/'+p,'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
ext={
 'schema':'noboribetsu-date-v005-east/1',
 'base_version':'V004-merchant-candidate-r1',
 'status':'candidate_static_not_WebGL2_or_Blender_verified',
 'route_start_m':start['s'],'route_end_m':route[-1]['s'],'added_length_m':route[-1]['s']-start['s'],
 'route_end_eus':{k:target[k] for k in ('x','y','z')},
 'models':models,'known_buildings':reports,
 'geometry':{'road':road_stats,'facades':facade_stats},
 'collision':{'path':'v005_collision.json','sha256':hashlib.sha256((DIST/'v005_collision.json').read_bytes()).hexdigest(),
              'walkable_triangles':len(walk_f),'posts':len(posts)},
 'provenance':{'route':'OpenStreetMap snapshot 2026-10-31, © OpenStreetMap contributors, ODbL; V002 frozen',
               'location':'V002 frozen OSM footprints, not surveyed',
               'road_height':'Frozen V002 GSI DEM1A interpolated across seven road cross-section strips; rendered 3.8cm above terrain (visual only), collision from V002 DEM profile. Measured road height NOT claimed',
               'photos':'used as external reference only; no official or third-party photographs inside the model',
               'buildings':'artist-created generic Edo exterior, NOT a measured/photo-exact reconstruction',
               'source':'https://edo-trip.jp/map/ ; https://edo-trip.jp/facility/waraji-ya/ ; https://edo-trip.jp/facility/utsuroi-kan/'},
 'browser':'NOT_VERIFIED','Android':'NOT_VERIFIED','Blender_native':'NOT_RUN','private_site':'NOT_CHANGED'}
(DIST/'v005_manifest.json').write_text(json.dumps(ext,ensure_ascii=False,indent=2)+'\n')
view=dict(BASE_VIEW);view['version']='V005-east-candidate-r1';view['base_version']='V004-merchant-candidate-r1'
view['route']=route
view['extension_v005']={'manifest':'v005_manifest.json','collision':'v005_collision.json','models':models,'building_ids':[x[0] for x in PLANS],
                          'status':'original estimated exteriors; OSM named footprints; no interiors'}
view['scope']='V004 preserved + next contiguous OSM street leg; Waraji-ya/Utsuroi-kan authored facade candidates'
(DIST/'scene_view.json').write_text(json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n')
summary={'version':view['version'],'old_route_m':start['s'],'route_m':route[-1]['s'],'added_m':route[-1]['s']-start['s'],
         'new_route_points':len(route)-len(BASE_ROUTE),'models':models,'facade_triangles':sum(v['triangles'] for v in facade_stats.values()),
         'road_triangles':sum(v['triangles'] for v in road_stats.values()),'collision_triangles':len(walk_f),'new_obstacles':len(posts),'DEM_profile_sha256':hashlib.sha256(profile_path.read_bytes()).hexdigest(),
         'buildings':[name for _,name,_ in PLANS]}
(DIST/'v005_build_qa.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))