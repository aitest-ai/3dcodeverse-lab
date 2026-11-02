#!/usr/bin/env python3
"""Source-grounded, read-only V004 pedestrian route audit for Date Jidaimura V017.
Requires numpy and shapely; reads V016 frozen runtime, never edits it.
No 'door threshold' is inferred from OSM; shop interiors remain closed.
"""
import hashlib,json,zipfile,math
from pathlib import Path
import numpy as np
from shapely.geometry import Point,Polygon
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parent
ARCHIVE=ROOT/'V016_Runtime.zip'; OUT=ROOT/'outputs';OUT.mkdir(exist_ok=True)
with zipfile.ZipFile(ARCHIVE) as z:
 manifest=json.loads(z.read('dist/scene_view.json'))
 collision=json.loads(z.read('dist/collision.json'))
 v004=json.loads(z.read('dist/extension_collision.json'))
 archive_hash=hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
 sources={k:hashlib.sha256(z.read(k)).hexdigest() for k in ['dist/scene_view.json','dist/extension_collision.json','dist/collision.json','dist/assets/v004_merchant_facades.glb','dist/v015_post_grounding.json','dist/v016_grade_inspection.json']}
 assert len(z.namelist())==113, 'Unexpected V016 baseline; stop'
assert abs(manifest['route'][-1]['s']-231.56641497226084)<1e-4
assert collision['player']['radius_m']==0.26
assert v004['schema']=='noboribetsu-date-v004-merchant-extension/1'
assert len(v004['obstacles'])==24
vv=np.asarray(v004['walkable'][0]['vertices'],dtype=float)
tri=v004['walkable'][0]['triangles']
walkable=unary_union([Polygon(vv[t][:,[0,2]]) for t in tri])
assert walkable.is_valid and walkable.area>250
polygons=[(o['id'],Polygon(o['polygon'])) for o in v004['obstacles'] if o['stage'] in ('B','both')]
for name,g in polygons: assert g.is_valid and g.area>0
radius=collision['player']['radius_m']
route=manifest['route'];start=82.877;end=130.0146
samples=[]
for ss in np.linspace(start,end,math.ceil((end-start)/0.2)+1):
 j=next(i for i in range(1,len(route)) if route[i]['s']>=ss)
 p,q=route[j-1],route[j];t=(ss-p['s'])/(q['s']-p['s']);x=p['x']*(1-t)+q['x']*t;z=p['z']*(1-t)+q['z']*t;y=p['y']*(1-t)+q['y']*t
 dx=q['x']-p['x'];dz=q['z']-p['z']; norm=math.hypot(dx,dz);nx=-dz/norm;nz=dx/norm
 pt=Point(x,z);dist,name=min((poly.distance(pt),name) for name,poly in polygons)
 # The traversability check is strictly 2D, not a doorway/interior or human egress certification.
 side=[]
 for offset in (-1.5,-1.0,-.5,0,.5,1.0,1.5):
  probe=Point(x+nx*offset,z+nz*offset)
  side.append({'offset_m':offset,'walkable':bool(walkable.covers(probe)),'horizontal_obstacle_clearance_m':round(min(poly.distance(probe) for _,poly in polygons)-radius,4)})
 samples.append({'s_m':round(float(ss),4),'x':round(x,5),'y':round(y,5),'z':round(z,5),'nearest_obstacle':name,'nearest_obstacle_distance_m':round(dist,5),'capsule_horizontal_margin_m':round(dist-radius,5),'inside_v004_walkable':walkable.covers(pt),'slices':side})
# summarize identifiable caution locations at distinct obstacle centers
per_obstacle={}
for p in samples:
 name=p['nearest_obstacle']
 if name not in per_obstacle or p['capsule_horizontal_margin_m']<per_obstacle[name]['capsule_horizontal_margin_m']:
  per_obstacle[name]=p
margins=[p['capsule_horizontal_margin_m'] for p in samples]
slopes=[abs((b['y']-a['y'])/(b['s_m']-a['s_m'])) for a,b in zip(samples,samples[1:])]
# select six closest route segments, non-adjacent >= 1.2m
selected=[]
for p in sorted(samples,key=lambda d:d['capsule_horizontal_margin_m']):
 if p['capsule_horizontal_margin_m']>.55: break
 if all(abs(p['s_m']-q['s_m'])>=1.2 for q in selected): selected.append(p)
 if len(selected)==10:break
selected=sorted(selected,key=lambda d:d['s_m'])
assert len(selected)>=3
summary={'source_snapshot':'V016 R1 sealed runtime','site_section':'V004 merchant lane centerline only','route_start_s_m':start,'route_end_s_m':end,'sample_interval_max_m':round(max(b['s_m']-a['s_m'] for a,b in zip(samples,samples[1:])),4),'sample_count':len(samples),'walkable_centerline_pass':all(p['inside_v004_walkable'] for p in samples),'player_radius_m':radius,'minimum_capsule_margin_m':round(min(margins),5),'minimum_margin_at_s_m':min(samples,key=lambda p:p['capsule_horizontal_margin_m'])['s_m'],'maximum_centerline_grade_percent':round(100*max(slopes),3),'obstacle_count':len(polygons),'v004_walkable_triangle_count':len(tri),'offset_probe_sample_count':len(samples)*7,'diagnostic_marker_count':len(selected),'no_interiors_verified':True,'door_threshold_surveyed':False,'collision_or_navigation_modified':False}
source={'schema':'noboribetsu-date-v017-clearance-audit/1','stage':'B','visual_diagnostic_only':True,'default_visible':False,'collision_changed':False,'route_changed':False,'original_architecture_modified':False,'player_radius_m':radius,'summary':summary,'markers':[{'s_m':p['s_m'],'x':p['x'],'y':p['y']+.04,'z':p['z'],'margin_m':p['capsule_horizontal_margin_m'],'obstacle_id':p['nearest_obstacle']} for p in selected],'sources_sha256':sources,'limitations':['V004 route centerline and 2D obstacle polygons only, not door threshold height or human egress','original OSM/site exterior is partly author-estimated','no interiors, no Android physical device, no onsite surveying']}
raw=(json.dumps(source,ensure_ascii=False,separators=(',',':'))+'\n').encode();(OUT/'v017_clearance_audit.json').write_bytes(raw)
qa={'schema':'noboribetsu-date-v017-static-clearance-qa/1','status':'STATIC_GEOMETRY_PASS_RENDER_PENDING','sha256':hashlib.sha256(raw).hexdigest(),'source_runtime_zip_sha256':archive_hash,'summary':summary,'closest_per_obstacle':[{k:v for k,v in p.items() if k not in ('slices',)} for p in sorted(per_obstacle.values(),key=lambda d:d['capsule_horizontal_margin_m'])[:24]],'lateral_sample_offsets_m':[-1.5,-1,-.5,0,.5,1,1.5],'side_offsets_not_certified':True,'route_or_collision_changed':False,'fixed_threshold_interpretation':False}
(OUT/'V017_clearance_qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
# Provide compact route samples for offline inspection, no unbounded JSON in runtime
(OUT/'V017_route_samples.json').write_text(json.dumps({'schema':'v017-route-centerline-samples/1','samples':samples},ensure_ascii=False,separators=(',',':'))+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))