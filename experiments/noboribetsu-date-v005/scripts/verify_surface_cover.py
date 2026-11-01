"""Check sampled road visual clearance against original frozen V002 DEM; diagnostic, not site measurement."""
from pathlib import Path
import json,hashlib,math,os, numpy as np,trimesh
from scipy.spatial import cKDTree
ROOT=Path(os.environ.get('DATE_V005_PROJECT_ROOT',str(Path(__file__).resolve().parent.parent)))
SRC=Path(os.environ.get('DATE_V002_GEOMETRY',str(ROOT/'baseline/data/scene_geometry.json')))
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='75d672d5296ac28bef25b03423da395027c4b29cf804652239f40e9fc73d408a'
G=json.loads(SRC.read_text())
terr=np.asarray(G['terrain']['vertices'],dtype=np.float64);trif=np.asarray(G['terrain']['triangles'],dtype=np.int64)
# terr is ENU, map x-east z=-north; 3D render is EUS.
terr[:,1]*=-1
terr=terr[:,[0,2,1]]
T=terr[trif];tree=cKDTree(T[:,:,[0,2]].mean(axis=1))
R=trimesh.load(str(ROOT/'runtime/dist/assets/v005_east_road.glb'),force='scene',process=False)
road=np.concatenate([m.vertices[m.faces] for m in R.geometry.values() if getattr(getattr(m.visual,'material',None),'name','')=='road_earth'],axis=0).astype(np.float64)
rtree=cKDTree(road[:,:,[0,2]].mean(axis=1))
def height(pos,vtx,search):
 _,ids=search.query(pos,k=min(80,len(vtx)))
 x,z=pos
 for idx in np.atleast_1d(ids):
  a,b,c=vtx[int(idx)]
  den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
  if abs(den)<1.e-10:continue
  u=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/den
  v=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/den;w=1-u-v
  if min(u,v,w)>-2.e-5:return float(u*a[1]+v*b[1]+w*c[1])
 return None
view=json.loads((ROOT/'runtime/dist/scene_view.json').read_text());r=view['route'];ext=[p for p in r if p['s']>=130.014612-1.e-6]
checks=[]
for i,p in enumerate(ext[:-1]):
 a,b=ext[i],ext[i+1];dx,dz=b['x']-a['x'],b['z']-a['z'];l=math.hypot(dx,dz)
 if l<1.e-6:continue
 nx,nz=-dz/l,dx/l
 for side in (-2.6,-1.4,0,1.4,2.6):
  x=p['x']+nx*side;z=p['z']+nz*side
  dem=height((x,z),T,tree);roady=height((x,z),road,rtree)
  if dem is None or roady is None:continue
  checks.append({'s':p['s'],'side':side,'clearance':roady-dem})
vals=[a['clearance'] for a in checks]
report={'schema':'noboribetsu-date-v005-visual-road-over-DEM/1','samples':len(vals),
        'min_clearance_m':min(vals),'max_clearance_m':max(vals),'mean_clearance_m':sum(vals)/len(vals),
        'below_dem_count':sum(t<-.001 for t in vals),
        'worst_10':sorted(checks,key=lambda v:v['clearance'])[:10],
        'status':'VISUAL_SURFACE_DIAGNOSTIC_ONLY'}
(ROOT/'V005_surface_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2)[:4500])