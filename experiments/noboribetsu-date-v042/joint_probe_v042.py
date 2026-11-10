#!/usr/bin/env python3
"""V042 read-only geometry probe. Usage: python joint_probe_v042.py H.glb
Exposes cap centres, centre-ray hits and nearest distances. Requires trimesh/numpy.
Do not interpret model coordinates as surveyed building dimensions.
"""
from pathlib import Path
import hashlib,sys, numpy as np, trimesh, json
H_SHA="9d6ec28e7844c3b522b6b1453426334f36da580808ad78bd4bc3e7c5969463f4"
CAPS=((20,21),(32,33),(44,45),(56,57))
def vertical_hits(tris,x,z,low_y):
 a=tris[:,0];b=tris[:,1];c=tris[:,2]
 dx=b[:,[0,2]]-a[:,[0,2]];dz=c[:,[0,2]]-a[:,[0,2]]
 dp=np.array([x,z])-a[:,[0,2]]
 den=dx[:,0]*dz[:,1]-dx[:,1]*dz[:,0];valid=np.abs(den)>1e-10
 den=np.where(valid,den,1)
 u=(dp[:,0]*dz[:,1]-dp[:,1]*dz[:,0])/den
 v=(dx[:,0]*dp[:,1]-dx[:,1]*dp[:,0])/den
 y=a[:,1]+u*(b[:,1]-a[:,1])+v*(c[:,1]-a[:,1])
 return np.sort(y[valid & (u>=-1e-6) & (v>=-1e-6) & (u+v<=1+1e-6) & (y>=low_y-1e-5)])
def nearest(point,mesh):
 triangles=mesh.triangles
 low=triangles[:,:,[0,2]].min(axis=1);high=triangles[:,:,[0,2]].max(axis=1)
 horiz=np.linalg.norm(np.maximum(np.maximum(low-point[[0,2]],point[[0,2]]-high),0),axis=1)
 candidates=(horiz<2)&(triangles[:,:,1].max(axis=1)>=point[1]-.01)
 cut=triangles[candidates]
 projected=trimesh.triangles.closest_point(cut,np.repeat(point[None,:],len(cut),axis=0))
 dist=np.linalg.norm(projected-point,axis=1)
 k=np.argmin(dist)
 return {'distance':float(dist[k]),'closest_point':projected[k].tolist()}
def main(glb):
 blob=Path(glb).read_bytes();assert hashlib.sha256(blob).hexdigest()==H_SHA
 meshes=trimesh.load(glb,force="scene").geometry;assert len(meshes)==17
 result=[]
 for i,pair in enumerate(CAPS,1):
  t=meshes["wood_dark"].triangles[list(pair)].reshape(-1,3)
  p=(t.min(axis=0)+t.max(axis=0))/2
  plaster=vertical_hits(meshes["plaster_offwhite"].triangles,p[0],p[2],p[1])
  wood={}
  for name in ("wood_lintel","wood_timber"):
   wood[name]={**nearest(p,meshes[name]),"direct_center_overhead":bool(len(vertical_hits(meshes[name].triangles,p[0],p[2],p[1])))}
  assert len(plaster) and abs(float(plaster[0]-p[1])-.05)<1e-4
  assert all(not v["direct_center_overhead"] for v in wood.values())
  result.append({'post':f'P{i}','center':p.tolist(),'plaster_gap':float(plaster[0]-p[1]),'wood':wood})
 print(json.dumps({'pass':True,'author_model_units_only':True,'result':result},ensure_ascii=False,indent=2))
if __name__=="__main__":
 if len(sys.argv)!=2:raise SystemExit(__doc__)
 main(sys.argv[1])
