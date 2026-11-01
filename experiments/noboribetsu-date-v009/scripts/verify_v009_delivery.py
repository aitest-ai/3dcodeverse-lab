#!/usr/bin/env python3
"""Immutable V008 vs V009 file inventory, GLB header and version contract check."""
import hashlib,json,struct
from pathlib import Path
BASE=Path(__file__).parent
OLD=BASE/'base/dist';NEW=BASE/'runtime/dist'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(2**20),b''):h.update(c)
 return h.hexdigest()
def inventory(folder):return {p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file()}
a,b=inventory(OLD),inventory(NEW)
changed=sorted([x for x in a if b.get(x)!=a[x]])
added=sorted(set(b)-set(a))
assert changed==['app.js','index.html','qa.json','scene_view.json'],changed
assert len(a)-len(changed)==68,len(a)
assert 'assets/v009_utsuroi_facade.glb' in added
assert b['assets/v008_waraji_architecture.glb']==a['assets/v008_waraji_architecture.glb']
assert b['assets/v007_east_facades.glb']==a['assets/v007_east_facades.glb']
assert b['assets/v005_east_facades.glb']==a['assets/v005_east_facades.glb']
assert b['collision.json']==a['collision.json'] and b['navigation.js']==a['navigation.js']
assert b['assets/scene_A.glb']==a['assets/scene_A.glb']
view=json.loads((NEW/'scene_view.json').read_text());oldview=json.loads((OLD/'scene_view.json').read_text())
assert view['route']==oldview['route'] and len(view['route'])==472
assert abs(view['route'][-1]['s']-231.56641497226084)<.000001
oldcol=json.loads((OLD/'collision.json').read_text());newcol=json.loads((NEW/'collision.json').read_text());assert oldcol==newcol
manifest=json.loads((NEW/'v009_facade_manifest.json').read_text());desc=view['extension_v009']['model']
assert desc==manifest['model']
model=NEW/desc['path'];size=model.stat().st_size
assert desc['bytes']==size and sha(model)==desc['sha256']
with model.open('rb') as f:header=f.read(12)
assert header[:4]==b'glTF' and struct.unpack('<II',header[4:])==(2,size)
assert manifest['geometry']['total_triangles']==17104
assert manifest['geometry']['removed_side_grid_boxes']==20
q=json.loads((BASE/'outputs/v009_model_qa.json').read_text());assert q['glb_v009_sha256']==desc['sha256']
report={'schema':'date-v009-integrity-diff/1','status':'PASS_SOURCE_AND_ASSET_BYTES_ONLY',
 'v008_files':len(a),'v009_files':len(b),'unchanged_existing_files':len(a)-len(changed),
 'changed_existing_files':changed,'added_files':added,
 'frozen_original_geometry_assets_unchanged':True,'collision_and_route_unchanged':True,
 'route_length_m':view['route'][-1]['s'],'route_points':len(view['route']),
 'new_model_sha256':desc['sha256'],'new_model_bytes':size,
 'initial_skipped_archived_model_bytes':sum((NEW/'assets'/n).stat().st_size for n in ('v005_east_facades.glb','v007_east_facades.glb','v008_waraji_architecture.glb')),
 'browser_real_webgl2_verified':False,'blender_native_verified':False}
(BASE/'evidence/integrity_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('status','v008_files','v009_files','unchanged_existing_files','changed_existing_files','route_length_m','new_model_sha256')},ensure_ascii=False,indent=2))