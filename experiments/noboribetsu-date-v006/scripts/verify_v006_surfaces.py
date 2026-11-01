#!/usr/bin/env python3
"""Read back actual V006 GLB and verify no road triangles are below frozen V002 DEM."""
from pathlib import Path
import numpy as np,json,hashlib,trimesh,os,math
from scipy.spatial import cKDTree
root=Path(os.environ.get('DATE_V006_ROOT',Path(__file__).resolve().parent.parent))
geo_path=root/'baseline/scene_geometry.json'
assert hashlib.sha256(geo_path.read_bytes()).hexdigest()=='75d672d5296ac28bef25b03423da395027c4b29cf804652239f40e9fc73d408a'
geo=json.loads(geo_path.read_text());v=np.asarray(geo['terrain']['vertices']);f=np.asarray(geo['terrain']['triangles']);tree=cKDTree(v[f][:,:,:2].mean(axis=1))
def dem(x,z):
  _,ids=tree.query((x,-z),k=100)
  for id in np.atleast_1d(ids):
    a,b,c=v[f[id]];d=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1]);
    if abs(d)<1e-12:continue
    u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(-z-c[1]))/d;w=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(-z-c[1]))/d;t=1-u-w
    if min(u,w,t)>-1.e-7:return float(u*a[2]+w*b[2]+t*c[2])
  raise ValueError('Outside frozen DEM')
model=trimesh.load(root/'dist/assets/v006_tail_road.glb',force='scene',process=False)
report={'schema':'date-v006-surface-geometry-qa/1','source':'frozen V002 DEM (NOT road survey)','status':'FAIL','geometries':{},'not_surveyed':True}
for key,mesh in model.geometry.items():
  vertices=np.asarray(mesh.vertices);clear=np.array([p[1]-dem(p[0],p[2]) for p in vertices])
  report['geometries'][key]={'triangles':len(mesh.faces),'vertices_checked':len(vertices),'min_clearance_m':round(float(clear.min()),6),'max_clearance_m':round(float(clear.max()),6),'below_dem_count':int((clear<-.001).sum()),'suspicious_high_m_count':int((clear>.55).sum())}
# A seam should have small but nonnegative difference between V005 end and V006 start.
v005=json.loads((root/'baseline/scene_view_v005.json').read_text())['route'][-1]
v006=json.loads((root/'dist/scene_view.json').read_text())['route'];junction=v006[len(json.loads((root/'baseline/scene_view_v005.json').read_text())['route'])-1]
report['route_seam_m']=round(float(math.dist([junction[k] for k in ('x','y','z')],[v005[k] for k in ('x','y','z')])),9)
report['status']='PASS_STATIC_SURFACE_ONLY' if report['route_seam_m']<1e-7 and all(q['below_dem_count']==0 and q['suspicious_high_m_count']==0 for q in report['geometries'].values()) else 'FAIL'
(root/'evidence/V006_surface_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
if report['status']=='FAIL':raise RuntimeError('V006 surface test failed')