#!/usr/bin/env python3
"""Generate non-colliding B-only porch guidance from frozen V018 runtime; preserves originals."""
import json,hashlib,pathlib,math,sys
ROOT=pathlib.Path(__file__).resolve().parent
D=ROOT/'runtime'/'dist'
assert D.exists()
manifest_path=D/'scene_view.json'
orig=json.loads(manifest_path.read_text())
assert orig['route'][-1]['s']>231.5
assert len(orig['route'])>470
src_scene_hash=hashlib.sha256(manifest_path.read_bytes()).hexdigest()
V017=json.loads((D/'v017_clearance_audit.json').read_text())
assert abs(V017['summary']['minimum_capsule_margin_m']-.23203)<.00001
route=orig['route']
def sample(s):
 for a,b in zip(route,route[1:]):
  if a['s']<=s<=b['s']:
   t=(s-a['s'])/(b['s']-a['s']);return {k:round(a[k]+t*(b[k]-a[k]),7) for k in ('x','y','z')}
 raise ValueError(s)
samples=[]
for i in range(13):
 s=85+i*1.5
 samples.append({'s_m':s,**sample(s)})
patch={'schema':'noboribetsu-date-v019-porch-centerline-guide/1','stage':'B','default_visible':True,'diagnostic_not_surveyed':True,'collision_changed':False,'route_changed':False,'geometry_changed':False,'B_only':True,'player_radius_m':.26,'source_scene_v018_sha256':src_scene_hash,'source_v017_clearance_sha256':hashlib.sha256((D/'v017_clearance_audit.json').read_bytes()).hexdigest(),'route_start_s_m':85,'route_end_s_m':103,'warning_range_s_m':[84.5,105], 'lateral_warning_offset_m':-.45,'samples':samples,'point_memo':'Model-derived route centerline markers only; not safe doorway/evacuation route; no physical survey','limitations':['V004 buildings are author-estimated','Only centerline was cleared by CollisionWorld; left offset probes block','No physical accessibility or passage certification']}
p= D/'v019_porch_guide.json';p.write_text(json.dumps(patch,ensure_ascii=False,indent=2)+'\n')
sha=hashlib.sha256(p.read_bytes()).hexdigest()
orig['porch_guide_v019']={'schema':patch['schema'],'path':p.name,'sha256':sha,'bytes':p.stat().st_size,'stage':'B','default_visible':True,'sample_count':len(samples),'collision_changed':False,'route_changed':False,'source_scene_v018_sha256':src_scene_hash,'warning_not_certification':True}
manifest_path.write_text(json.dumps(orig,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'sha':sha,'bytes':p.stat().st_size,'samples':len(samples),'first':samples[0],'last':samples[-1],'sceneV018SHA':src_scene_hash},ensure_ascii=False,indent=2))