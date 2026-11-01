#!/usr/bin/env python3
"""Extract a non-survey DEM elevation profile on V005 route and road edges from frozen V002 geometry.

The terrain source is checked against V002 SHA256; no DEM tiles/images are embedded in runtime.
The ~6m walkable width is ARTIST ESTIMATE; not official accessible route evidence.
"""
from pathlib import Path
import json,math,hashlib,sys,numpy as np
from scipy.spatial import cKDTree
SOURCE=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent.parent/'baseline/data/scene_geometry.json'
OUT=Path(sys.argv[2]) if len(sys.argv)>2 else Path(__file__).resolve().parent/'v005_dem_profile.json'
expected='75d672d5296ac28bef25b03423da395027c4b29cf804652239f40e9fc73d408a'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==expected
geo=json.loads(SOURCE.read_text());v=np.asarray(geo['terrain']['vertices'],dtype=np.float64);tri=np.asarray(geo['terrain']['triangles'],dtype=np.int32)
centroid=v[tri][:,:,:2].mean(axis=1);tree=cKDTree(centroid)
def ground(x,z):
 # OSM snapshot east/north z=-north, GSI terrain V002 ENU
 xy=(x,-z)
 d,ids=tree.query(xy,k=100)
 for j in np.atleast_1d(ids):
  a,b,c=v[tri[int(j)]]
  den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(den)<1e-12:continue
  u=((b[1]-c[1])*(xy[0]-c[0])+(c[0]-b[0])*(xy[1]-c[1]))/den
  vv=((c[1]-a[1])*(xy[0]-c[0])+(a[0]-c[0])*(xy[1]-c[1]))/den;w=1-u-vv
  if min(u,vv,w)>=-1.e-7:return float(u*a[2]+vv*b[2]+w*c[2])
 raise RuntimeError('DEM outside triangle cover')
start={'x':42.12494461926742,'y':1.5008070047490634,'z':61.89492582438763}
end={'x':101.7463863855061,'y':1.3101205339255984,'z':93.9859830694928}
length=math.hypot(end['x']-start['x'],end['z']-start['z']);N=math.ceil(length/.50);dx=(end['x']-start['x'])/length;dz=(end['z']-start['z'])/length;nx,nz=-dz,dx
offsets=[-3.0,-2.0,-1.0,0.0,1.0,2.0,3.0]
points=[]
for i in range(N+1):
 t=i/N;x=start['x']+(end['x']-start['x'])*t;z=start['z']+(end['z']-start['z'])*t
 dem=[ground(x+n*nx,z+n*nz) for n in (0,3,-3)]
 transverse=[ground(x+n*nx,z+n*nz) for n in offsets]
 elapsed=t*length;blend=min(1,elapsed/4.0)
 h0=(1-blend)*start['y']+blend*dem[0]
 hleft=(1-blend)*start['y']+blend*dem[1]
 hright=(1-blend)*start['y']+blend*dem[2]
 if i==0: h0=hleft=hright=start['y']
 points.append({'x':x,'z':z,'center_y':h0,'left_y':hleft,'right_y':hright,'dem_center_y':dem[0], 'dem_transverse_y':transverse})
assert abs(points[0]['center_y']-start['y'])<1e-9
assert abs(points[-1]['center_y']-end['y'])<.05
out={'schema':'noboribetsu-date-v005-dem-road-profile/1','source_geom_sha256':expected,'source':'frozen V002 GSI DEM1A terrain interpolated; not survey','width_m_estimate':6.0,'transverse_offsets_m':offsets,'points':points,
     'note':'First 4m blends from V004 road edge to DEM; horizontal route is frozen OSM vertex interpolation'}
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=1)+'\n')
print('PROFILE',len(points),'height range',min(q['center_y'] for q in points),max(q['center_y'] for q in points), 'sha',hashlib.sha256(OUT.read_bytes()).hexdigest())