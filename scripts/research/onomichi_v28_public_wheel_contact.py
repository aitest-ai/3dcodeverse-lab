#!/usr/bin/env python3
"""V28 PUBLIC GSI/OSM wheel-contact math. Does NOT contain private V06 GLBs.
Private V28 package additionally verifies original 139 bicycle meshes and actor Cycle.
"""
import base64,hashlib,json,math,pathlib,struct,zlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
SRC=ROOT/"assets/setouchi/onomichi-v23-gsi-ground-sample.json"
OUTPUT=ROOT/"outputs/onomichi-v28/public-source-wheel-contact.json"
GRID_SHA="03726ce15167b760f6a738c1862097c258857299cae7a32353a84931c44cdbf1"
OSM_SHA="5adaecd750f1bea9517ddb9b0ebfabec11414b4f60309e98122d1434859ada76"
def main():
 d=json.loads(SRC.read_text())
 assert d["osm_way_id"]=="388716484" and d["osm_source_sha256"]==OSM_SHA
 raw=zlib.decompress(base64.b64decode(d["dem_ground_cm_int16_le_zlib_base64"]))
 assert hashlib.sha256(raw).hexdigest()==GRID_SHA
 z=struct.unpack("<3366h",raw);nx=51;ny=66
 def height(x,n):
  u=(x+50)/2;v=(n+66)/2
  i=max(0,min(49,math.floor(u)));j=max(0,min(64,math.floor(v)))
  a=max(0,min(1,u-i));b=max(0,min(1,v-j))
  h=lambda ix,iy:z[iy*nx+ix]/100
  return h(i,j)*(1-a)*(1-b)+h(i+1,j)*a*(1-b)+h(i,j+1)*(1-a)*b+h(i+1,j+1)*a*b
 lat0,lon0=d["origin_lat_lon"]
 pts=[((lon-lon0)*111320*math.cos(math.radians(lat0)),(lat-lat0)*111132) for lat,lon in d["osm_way_lat_lon"]]
 seg=[math.dist(pts[i],pts[i+1]) for i in range(3)];cuts=[0]
 for v in seg:cuts.append(cuts[-1]+v)
 length=cuts[-1];assert 74.32<length<74.40
 distances=[i*.2 for i in range(math.ceil(length/.2))]+[length]
 assert len(distances)==373
 def point(s):
  for j in range(3):
   if s<=cuts[j+1] or j==2:
    t=max(0,min(1,(s-cuts[j])/seg[j]))
    return tuple(pts[j][k]*(1-t)+pts[j+1][k]*t for k in (0,1))
 raw_pts=[point(s) for s in distances]
 weights=[math.exp(-k*k/8) for k in range(-8,9)];wtotal=sum(weights);weights=[w/wtotal for w in weights]
 smooth=[tuple(sum(weights[k+8]*raw_pts[max(0,min(len(raw_pts)-1,i+k))][axis] for k in range(-8,9)) for axis in (0,1)) for i in range(len(raw_pts))]
 smooth[0]=pts[0];smooth[-1]=pts[-1]
 heights=[];pitches=[]
 for i,(x,n) in enumerate(smooth):
  aa=smooth[max(0,i-1)];bb=smooth[min(len(smooth)-1,i+1)]
  dx,dn=bb[0]-aa[0],bb[1]-aa[1]
  ll=math.hypot(dx,dn);tx,tn=dx/ll,dn/ll
  front=height(x+tx*.54,n+tn*.54)
  rear=height(x-tx*.54,n-tn*.54)
  heights.append(front-rear)
  pitches.append(-math.degrees(math.asin(max(-1,min(1,(front-rear)/1.08)))))
 flags={key:False for key in ["real_road_surface","surveyed_road_width","legal_bicycle_rights","real_curb_collision","actual_actor_bike_contact","real_webgl2_or_android_gameplay","original_game_world_changed","public_repo_contains_private_bicycle_glb","site_deployed"]}
 result={"schema_version":1,"status":"PUBLIC_DERIVED_GSI_CONTACT_ONLY_NOT_RIDEABLE",
 "source_osm_way":"388716484","source_osm_sha256":OSM_SHA,"source_gsi_derived_sha256":GRID_SHA,
 "source_centerline_length_m":round(length,4),"sampled_positions":len(distances),
 "wheelbase_m_from_verified_private_metadata":1.08,
 "maximum_absolute_source_dem_pitch_deg":round(max(map(abs,pitches)),4),
 "maximum_front_to_rear_dem_difference_m":round(max(map(abs,heights)),4),
 "flags":flags,"note":"This public CI reads derived GSI sample only. Actual V06 139-mesh bicycle/actor is validated in the private full V28 ZIP."}
 OUTPUT.parent.mkdir(parents=True,exist_ok=True)
 OUTPUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(result,ensure_ascii=False))
if __name__=="__main__":main()
