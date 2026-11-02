#!/usr/bin/env python3
"""Recheck the original V18 DEM5A tile against 22 OSM nodes. Research, not navigation."""
import argparse,hashlib,json,math
from pathlib import Path
from PIL import Image
TILE_SHA="79dc9e009a448aec5726ee1c13906270fef196e92c36286075e5474310318e9c"
def pixel_elevation(img,lat,lon):
 n=2**15;x=(lon+180)/360*n
 y=(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n
 ix,iy=int(x),int(y)
 if (ix,iy)!=(28508,13045):raise ValueError("Missing original locked tile for this coordinate")
 r,g,b=img.getpixel((min(255,int((x-ix)*256)),min(255,int((y-iy)*256))))[:3]
 val=r*65536+g*256+b
 return None if val==8388608 else round((val if val<8388608 else val-16777216)*.01,2)
def main():
 p=argparse.ArgumentParser();p.add_argument("--tile",type=Path,required=True);p.add_argument("--registry",type=Path,default=Path("assets/setouchi/onomichi-v18-dem-evidence.json"))
 a=p.parse_args()
 if hashlib.sha256(a.tile.read_bytes()).hexdigest()!=TILE_SHA:raise ValueError("GSI source SHA does not match V18")
 data=json.loads(a.registry.read_text())
 assert data["road"]["osm_way_id"]=="114435640"
 img=Image.open(a.tile).convert("RGB");assert img.size==(256,256)
 rows=data["road"]["wgs84_nodes_and_dem_m"]
 assert len(rows)==22
 for row in rows:
  assert pixel_elevation(img,row["lat"],row["lon"])==row["gsi_dem_ground_m"],row["node_id"]
  assert row["road_surface_height_verified"] is False
 assert data["approvals"]["approved_cycling_route"] is False
 print("V18 PASS 22/22 original GSI DEM pixels (NOT surveyed roadway or navigation)")
if __name__=="__main__":main()
