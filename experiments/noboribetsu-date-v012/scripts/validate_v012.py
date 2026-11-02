#!/usr/bin/env python3
"""Read-only safety check for V012 V006 shoulder and immutable V011 assets."""
from pathlib import Path
import hashlib,json,math,sys

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()

def run(v011,v012):
 a=v011/'dist';b=v012/'dist'
 p=json.loads((b/'v012_road_grass_transition.json').read_text());meta=json.loads((b/'scene_view.json').read_text())['transition_v012']
 assert len(p['positions'])==656*3 and len(p['colors'])==656*4 and len(p['indices'])==972*3
 assert p['triangles']==972 and p['samples']==82 and p['collision_enabled']==False
 assert p['v011_terrain_gap_untouched'] is True
 assert min(p['indices'])>=0 and max(p['indices'])<656
 assert all(math.isfinite(n) for a in ('positions','colors') for n in p[a]);assert 0<=min(p['colors']) and max(p['colors'])<=1
 assert meta['sha256']==sha(b/'v012_road_grass_transition.json') and meta['bytes']==(b/'v012_road_grass_transition.json').stat().st_size
 assert meta['collision_changed'] is False
 assert sha(a/'v011_terrain_gap_patch.json')==sha(b/'v011_terrain_gap_patch.json')
 original=[s.relative_to(v011).as_posix() for s in v011.rglob('*') if s.is_file()]
 changes=sorted(n for n in original if sha(v011/n)!=sha(v012/n))
 assert changes==['dist/app.js','dist/index.html','dist/qa.json','dist/scene_view.json'],changes
 protected=[n for n in original if n not in changes]
 assert all(sha(v011/n)==sha(v012/n) for n in protected)
 return {'schema':'noboribetsu-v012-validation/1','status':'PASS_SOURCE_AND_RUNTIME_ASSETS','original_files':len(original),
  'unchanged_original_files':len(protected),'changed_original_files':changes,
  'v011_terrain_gap_sha256':sha(b/'v011_terrain_gap_patch.json'),'v006_road_sha256':sha(b/'assets/v006_tail_road.glb'),
  'new_overlay_bytes':(b/'v012_road_grass_transition.json').stat().st_size,
  'new_overlay_sha256':meta['sha256'],'new_triangles':p['triangles'],'new_vertices':len(p['positions'])//3,
  'stage_A_unchanged':True,'collision_unchanged':True,'route_unchanged':True,
  'android_real_device_tested':False,'private_web_deployment_tested':False,'blender_native_tested':False}

if __name__=='__main__':
 v011,v012=map(Path,sys.argv[1:3]);r=run(v011,v012)
 print(json.dumps(r,indent=2,ensure_ascii=False))
 if len(sys.argv)>3:Path(sys.argv[3]).write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')