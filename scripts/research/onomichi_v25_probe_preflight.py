#!/usr/bin/env python3
"""Recalculate V25 GSI DEM ground probes. Not pavement / navigation certification."""
import json,hashlib,zlib,base64,struct,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"assets/setouchi/onomichi-v23-gsi-ground-sample.json"
OUT=ROOT/"outputs/onomichi-v25/public-probe-report.json"
SHA="03726ce15167b760f6a738c1862097c258857299cae7a32353a84931c44cdbf1"
OSM_SHA="5adaecd750f1bea9517ddb9b0ebfabec11414b4f60309e98122d1434859ada76"
def main():
 d=json.loads(SRC.read_text())
 assert d["osm_source_sha256"]==OSM_SHA and d["osm_way_id"]=="388716484"
 b=zlib.decompress(base64.b64decode(d["dem_ground_cm_int16_le_zlib_base64"]))
 assert hashlib.sha256(b).hexdigest()==SHA
 h=struct.unpack("<3366h",b)
 xmin,xmax,dx=d["x_m"];ymin,ymax,dy=d["north_m"]
 nx=round((xmax-xmin)/dx)+1;ny=round((ymax-ymin)/dy)+1
 assert (nx,ny)==(51,66)
 def terrain(x,y):
  fx=(x-xmin)/dx;fy=(y-ymin)/dy
  i=max(0,min(nx-2,int(math.floor(fx))));j=max(0,min(ny-2,int(math.floor(fy))))
  u=max(0,min(1,fx-i));v=max(0,min(1,fy-j))
  z=lambda a,c:h[c*nx+a]*.01
  return z(i,j)*(1-u)*(1-v)+z(i+1,j)*u*(1-v)+z(i,j+1)*(1-u)*v+z(i+1,j+1)*u*v
 lat0,lon0=d["origin_lat_lon"]
 m_e=111320*math.cos(math.radians(lat0))
 pts=[((lon-lon0)*m_e,(lat-lat0)*111132) for lat,lon in d["osm_way_lat_lon"]]
 cent=[];distance=0
 for a,c in zip(pts,pts[1:]):
  segment=math.dist(a,c);count=math.ceil(segment)
  ux=-(c[1]-a[1])/segment;uy=(c[0]-a[0])/segment
  for i in range(count):
   f=i/count;x=a[0]*(1-f)+c[0]*f;y=a[1]*(1-f)+c[1]*f
   cent.append((x,y,ux,uy))
  distance+=segment
 a,c=pts[-2:];L=math.dist(a,c)
 cent.append((c[0],c[1],-(c[1]-a[1])/L,(c[0]-a[0])/L))
 assert len(cent)==77 and 74.32<distance<74.4
 offsets={}
 for delta in (.5,.75,1.,1.25,1.5,2.,2.5):
  diffs=[abs(terrain(x+delta*u,y+delta*v)-terrain(x-delta*u,y-delta*v)) for x,y,u,v in cent]
  offsets[str(delta)]={"max_ground_difference_m":round(max(diffs),4),
   "p95_ground_difference_m":round(sorted(diffs)[int(.95*(len(diffs)-1))],4),
   "observed_real_road_width_m":None}
 assert offsets["1.5"]["max_ground_difference_m"]==.2062
 out={"schema_version":1,"source_grid_sha256":SHA,"source_osm_sha256":OSM_SHA,
  "osm_way_id":"388716484","centerline_m":round(distance,4),
  "samples":len(cent),"offsets":offsets,"road_width_measured_m":None,
  "road_surface_height_measured_m":None,
  "user_private_original_GLBS_in_public_ci":False,
  "approvals":{"field_bicycle_access":False,"curbs_measured":False,"pavement_height":False,
  "swept_collision":False,"original_world_changed":False,
  "desktop_webgl2_playtest":False,"android_playtest":False},
  "warning":"± offsets are DEM probe distances, not lanes, road edges, or safe bike clearances."}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
 print("V25 PUBLIC DERIVED DEM PROBE PASS (not navigation)",len(cent),round(distance,4),offsets)
if __name__=="__main__":main()
