#!/usr/bin/env python3
"""Reproducible V24 centreline-to-DEM ground comparison; NOT pavement or navigation.

Uses only the SHA-locked V23 *derived* GSI grid and OSM points from this repo.
Private original V06 character/bicycle are NOT available in public GitHub CI.
"""
import base64,hashlib,json,math,struct,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"assets/setouchi/onomichi-v23-gsi-ground-sample.json"
OUT=ROOT/"outputs/onomichi-v24/V24_Public_Terrain_Contact.json"
SOURCE_CM_SHA="03726ce15167b760f6a738c1862097c258857299cae7a32353a84931c44cdbf1"
def audit():
 d=json.loads(SOURCE.read_text())
 x0,x1,dx=d["x_m"];n0,n1,dn=d["north_m"]
 nx=round((x1-x0)/dx)+1;ny=round((n1-n0)/dn)+1
 raw=zlib.decompress(base64.b64decode(d["dem_ground_cm_int16_le_zlib_base64"]))
 if (nx,ny)!=(51,66) or len(raw)!=nx*ny*2:raise ValueError("Terrain grid resolution changed")
 if hashlib.sha256(raw).hexdigest()!=SOURCE_CM_SHA:raise ValueError("Derived GSI height source changed")
 heights=struct.unpack("<%dh"%(nx*ny),raw)
 height=lambda ix,iy:heights[iy*nx+ix]*.01
 def bilinear(x,n):
  fx=(x-x0)/dx;fy=(n-n0)/dn
  i=max(0,min(nx-2,math.floor(fx)))
  j=max(0,min(ny-2,math.floor(fy)))
  u=max(0,min(1,fx-i));v=max(0,min(1,fy-j))
  return height(i,j)*(1-u)*(1-v)+height(i+1,j)*u*(1-v)+height(i,j+1)*(1-u)*v+height(i+1,j+1)*u*v
 origin_lat,origin_lon=d["origin_lat_lon"]
 xscale=111320*math.cos(math.radians(origin_lat));nscale=111132
 points=[((lon-origin_lon)*xscale,(lat-origin_lat)*nscale) for lat,lon in d["osm_way_lat_lon"]]
 if d["osm_nodes"]!=["1296327682","3918810183","3918810175","3918269426"]:raise ValueError("OSM source node drift")
 direct=[2.81,2.70,2.80,2.48]
 interpolated=[bilinear(x,n) for x,n in points]
 cross={str(w):[] for w in (.75,1.5,2.5)}
 centre=[];length=0.
 for a,b in zip(points,points[1:]):
  segment=math.dist(a,b);steps=max(2,math.ceil(segment))
  ux=-(b[1]-a[1])/segment;un=(b[0]-a[0])/segment
  for i in range(steps):
   t=i/steps;x=a[0]*(1-t)+b[0]*t;n=a[1]*(1-t)+b[1]*t
   centre.append(bilinear(x,n))
   for w in (.75,1.5,2.5):
    cross[str(w)].append(abs(bilinear(x+w*ux,n+w*un)-bilinear(x-w*ux,n-w*un)))
  length+=segment
 centre.append(bilinear(*points[-1]))
 if not 74.32<length<74.40:raise ValueError("Centreline source drift")
 report={
 "schema_version":1,"asset_id":"onomichi-v24-terrain-width-diagnostic-not-a-road",
 "original_derived_grid_sha256":SOURCE_CM_SHA,
 "gsi_original_source_png_sha256":d["gsi_tile_sha256"],
 "osm_original_source_sha256":d["osm_source_sha256"],
 "osm_way_id":d["osm_way_id"],"osm_nodes":d["osm_nodes"],
 "centreline_length_m":round(length,3),"centreline_ground_samples":len(centre),
 "sampled_grid_extent_m":[100,130],"grid_vertices":nx*ny,
 "original_gsi_node_ground_m":direct,
 "interpolated_2m_grid_ground_at_original_nodes_m":[round(n,4) for n in interpolated],
 "interpolation_difference_m":[round(n-direct[i],4) for i,n in enumerate(interpolated)],
 "centreline_ground_min_max_m":[round(min(centre),4),round(max(centre),4)],
 "lateral_ground_height_difference_only_not_lane_width":{
    k:{"max_m":round(max(v),4),"p95_m":round(sorted(v)[int(.95*(len(v)-1))],4)} for k,v in cross.items()},
 "actual_road_width_m":None,"actual_road_surface_height_m":None,
 "original_v06_character_and_bike_binary_available_in_this_public_CI":False,
 "private_v06_actor_m":{"height":1.75401,"width":1.12162},
 "private_v06_bicycle_m":{"length":1.77699,"width":.59478,"height":1.10413},
 "private_asset_dimensions_local_verified_in_user_owned_v23_runtime":True,
 "critical_approvals":{"road_width_surveyed":False,"curbs_field_verified":False,
 "traffic_signs_verified":False,"legal_bicycle_access":False,"road_grade_verified":False,
 "true_collision_tested":False,"actual_runtime_modified":False,
 "browser_webgl2_tested":False,"android_tested":False},
 "warning":"Side offsets at +/-0.75/1.5/2.5 m are diagnostic probes, NOT observed lane widths, sidewalk edges or bicycle clearances."}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({"status":"PUBLIC_DERIVED_GSI_PRECHECK_NOT_ROAD",
    "centerline_m":report["centreline_length_m"],
    "sample_count":report["centreline_ground_samples"],
    "lateral_1_5m_max":report["lateral_ground_height_difference_only_not_lane_width"]["1.5"]["max_m"],
    "interpolation_differences":report["interpolation_difference_m"]}))
if __name__=="__main__":audit()
