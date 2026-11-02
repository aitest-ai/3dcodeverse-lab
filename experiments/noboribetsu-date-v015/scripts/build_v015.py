#!/usr/bin/env python3
"""V015 artist-estimated stone footers: targeted floating V004 porch posts only.
Frozen source inputs: V014 Runtime dist + V002 Complete scene_geometry + V004 facade/road.
No collision/route/old geometry modifications; fails on source hashes or unexpectedly changed targets.
"""
import hashlib,json, math,sys,zipfile,os
from pathlib import Path
from collections import defaultdict
import numpy as np
import trimesh
BASE=Path(__file__).parent
D=BASE/'base/dist';OUT=BASE/'outputs';OUT.mkdir(exist_ok=True)
SCENE=json.loads((D/'scene_view.json').read_text())
EXT=json.loads((D/'extension_manifest.json').read_text())
V002=Path(os.environ.get('NOBORIBETSU_V002_COMPLETE_ZIP',str(BASE/'Noboribetsu_Date_V002_Complete.zip')))
if not V002.is_file():raise FileNotFoundError('Pass a frozen V002 Complete archive via NOBORIBETSU_V002_COMPLETE_ZIP')
with zipfile.ZipFile(V002) as z: GEOM=json.loads(z.read('Noboribetsu_Date_V002/data/scene_geometry.json'))
assert GEOM['axes']=='Blender ENU; GLB EUS'
assert abs(SCENE['route'][-1]['s']-231.56641497226084)<1e-6
ROADSHA=EXT['models']['v004_merchant_road.glb']['sha256'];FACSHA=EXT['models']['v004_merchant_facades.glb']['sha256']
for name,sha in [('v004_merchant_road.glb',ROADSHA),('v004_merchant_facades.glb',FACSHA)]:
 assert hashlib.sha256((D/'assets'/name).read_bytes()).hexdigest()==sha,name
road=trimesh.load(D/'assets/v004_merchant_road.glb',force='scene').geometry['road_asphalt']
facade=trimesh.load(D/'assets/v004_merchant_facades.glb',force='scene')
assert len(facade.geometry)==17
T=road.vertices[road.faces]; X=T[:,:,[0,2]]
mins=X.min(axis=1);maxs=X.max(axis=1)
def road_height(x,z):
 inds=np.where((mins[:,0]-1e-8<=x)&(maxs[:,0]+1e-8>=x)&(mins[:,1]-1e-8<=z)&(maxs[:,1]+1e-8>=z))[0]
 hs=[]
 for i in inds:
  a,b,c=X[i];v0=b-a;v1=c-a;v=np.array([x,z])-a;det=v0[0]*v1[1]-v0[1]*v1[0]
  if abs(det)<1e-10:continue
  u=(v[0]*v1[1]-v[1]*v1[0])/det;t=(v0[0]*v[1]-v0[1]*v[0])/det
  if u>=-1e-6 and t>=-1e-6 and u+t<=1.000001:hs.append(T[i,0,1]+u*(T[i,1,1]-T[i,0,1])+t*(T[i,2,1]-T[i,0,1]))
 return max(map(float,hs)) if hs else None
terrain=GEOM['terrain']['vertices'];terrain_heights={(round(a,5),round(-b,5)):float(c) for a,b,c in terrain}
def terrain_height(x,z):
 x0=math.floor((x+160)/2)*2-160;z0=math.floor((z+240)/2)*2-240
 v=[terrain_heights.get((x0,z0)),terrain_heights.get((x0+2,z0)),terrain_heights.get((x0,z0+2)),terrain_heights.get((x0+2,z0+2))]
 if any(t is None for t in v):return None
 tx=(x-x0)/2;tz=(z-z0)/2
 return (1-tx)*(1-tz)*v[0]+tx*(1-tz)*v[1]+(1-tx)*tz*v[2]+tx*tz*v[3]
# Each block is built at the actual post location, and never on top of an embedded post.
# A small undercut below the road avoids a new visible gap due to float precision.
verts=[];colors=[];faces=[];placements=[];flags=[]
matcolors={'way/283905599':(.45,.43,.395),'way/283905598':(.49,.465,.425),'way/283905593':(.46,.45,.41)}
BOX_FACE=[(0,1,2),(0,2,3),(4,6,5),(4,7,6),(0,4,5),(0,5,1),(1,5,6),(1,6,2),(2,6,7),(2,7,3),(3,7,4),(3,4,0)]
for b in EXT['known_buildings']:
 poly=b['footprint_enu_m'];xmin=min(v[0] for v in poly);xmax=max(v[0] for v in poly)
 zmin=min(-v[1] for v in poly);zmax=max(-v[1] for v in poly)
 sg=1 if b['road_facing_side']=='south' else -1
 z=(zmax if sg==1 else zmin)+sg*1.56;base=float(b['floor_base_m'])
 n=max(3,round((xmax-xmin)/2.8));xs=np.linspace(xmin+.33,xmax-.33,n+1)
 for post,x in enumerate(xs):
  r=road_height(x,z);g=terrain_height(x,z)
  if g is None and r is None:raise RuntimeError('V004 post ground missing')
  surface=max(v for v in (r,g) if v is not None)
  oldbottom=base+.005
  gap=oldbottom-surface
  status='buried' if gap < -.035 else 'near-ground' if abs(gap)<=.035 else 'floating'
  row={'osm_id':b['osm_id'],'building':b['name'],'post_index':post,'position_x':round(float(x),5),'position_z':round(float(z),5),'road_y':None if r is None else round(r,5),'terrain_y':None if g is None else round(g,5),'visible_surface_y':round(surface,5),'original_plinth_bottom_y':round(oldbottom,5),'gap_m':round(gap,5),'status':status}
  flags.append(row)
  if not (gap>.035 and r is not None):continue  # do not place inferred stone where no verified road under post
  # A narrower sleeve below the historic foot stone, not an extra cap on the road.
  w=.38;d=.38;bottom=surface-.012;top=oldbottom+.012
  if top-bottom>.19:raise RuntimeError('Unexpected huge footing proposed')
  k=len(verts); color=matcolors[b['osm_id']]
  for y in [bottom,top]:
   for xx,zz in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]:
    verts.append([float(x+xx),float(y),float(z+zz)]);colors.extend(color)
  faces.extend([[k+a,k+b,k+c] for a,b,c in BOX_FACE])
  row['new_footing_height_m']=round(top-bottom,5)
  placements.append(row)
assert len(placements)==8,(len(placements),flags)
assert len(faces)==96
assert set(x['building'] for x in placements)=={'高等学問所','北京亭'}
# Zero-area / degenerate rejection.
v=np.array(verts);f=np.array(faces);area=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)/2
assert np.all(area>1e-5)
assert not np.isnan(v).any() and f.min()>=0 and f.max()<len(v)
obj={'schema':'noboribetsu-date-v015-v004-porch-foot-grounding/1','stage':'B','visual_only':True,'collision_changed':False,'route_changed':False,'original_geometry_unchanged':True,'author_estimated':True,'surveyed':False,'source_facades_sha256':FACSHA,'source_road_sha256':ROADSHA,'support_count':len(placements),'triangles':len(faces),'vertices':len(verts),'positions':np.round(v.reshape(-1),6).tolist(),'colors':np.round(np.array(colors),5).tolist(),'indices':f.reshape(-1).tolist(),'supports':placements,'all_original_posts_audit':flags,'notes':'Road/terrain-supported micro risers under originally floating stone feet; existing buried feet intentionally left unchanged; not surveyed.'}
raw=(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n').encode();(OUT/'v015_post_grounding.json').write_bytes(raw)
sha=hashlib.sha256(raw).hexdigest()
mesh=trimesh.Trimesh(vertices=v,faces=f,process=False)
scene=trimesh.Scene();scene.add_geometry(mesh,geom_name='V015_visual_foot_risers_only',node_name='V015_visual_foot_risers_only')
scene.export(OUT/'V015_V004_Post_Grounding.glb')
qa={'schema':'noboribetsu-date-v015-geometric-audit/1','frozen_sources_verified':True,'original_post_count':len(flags),'floating_posts_over_35mm':len([x for x in flags if x['status']=='floating']),'risers_added':len(placements),'buried_posts_beyond_35mm':len([x for x in flags if x['status']=='buried']),'near_ground':len([x for x in flags if x['status']=='near-ground']),'gap_extrema_m':[min(x['gap_m'] for x in flags),max(x['gap_m'] for x in flags)],'triangles':len(faces),'vertices':len(v),'min_triangle_area':float(area.min()),'all_triangles_valid':True,'status':'PATCH_CANDIDATE_GEOMETRY_PASS_NOT_VISUAL_ACCEPTED','source_road_sha256':ROADSHA,'source_facades_sha256':FACSHA,'patch_sha256':sha,'post_rows':flags}
(OUT/'V015_grounding_audit.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:qa[k] for k in ['original_post_count','floating_posts_over_35mm','risers_added','buried_posts_beyond_35mm','near_ground','gap_extrema_m','triangles','vertices','status']},ensure_ascii=False,indent=2))