"""Reproducible, read-only V015 contract check; no assertion of full artistic acceptance."""
import hashlib,json,zipfile,sys,subprocess,tempfile,os,shutil
from pathlib import Path
R=Path(__file__).resolve().parent;BASE=R/'base/dist';OUT=R/'outputs'
PATCH=OUT/'v015_post_grounding.json';D=json.loads(PATCH.read_text());V=json.loads((BASE/'scene_view.json').read_text())
assert V['grounding_v015']['sha256']==hashlib.sha256(PATCH.read_bytes()).hexdigest()
assert D['support_count']==8 and D['triangles']==96 and D['vertices']==64
assert len(D['indices'])==288 and len(D['positions'])==192 and len(D['colors'])==192
assert all(0<=i<64 for i in D['indices'])
assert D['collision_changed'] is False and D['route_changed'] is False
frozen=Path(os.environ.get('NOBORIBETSU_V014_RUNTIME_ZIP',str(R/'Noboribetsu_Date_V014_R1_Runtime.zip')))
if not frozen.exists():raise FileNotFoundError(frozen)
with zipfile.ZipFile(frozen) as z:
 old={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}
new={str(f.relative_to(R/'base')):hashlib.sha256(f.read_bytes()).hexdigest() for f in (R/'base').rglob('*') if f.is_file()}
assert set(old)<=set(new)
changed=sorted(n for n in old if old[n]!=new[n]);added=sorted(set(new)-set(old))
assert changed==['dist/app.js','dist/index.html','dist/qa.json','dist/scene_view.json'],changed
assert added==['dist/v015_post_grounding.json'],added
out={'schema':'noboribetsu-date-v015-audit/1','old_files':len(old),'new_files':len(new),'unchanged':len(old)-len(changed),'changed':changed,'added':added,'patch_sha256':V['grounding_v015']['sha256'],'geometry_audit':json.loads((OUT/'V015_grounding_audit.json').read_text()),'browser_observed':'Chromium WebGL2 context=true; scene.loaded=true; metrics contained V015 support_count=8; before screenshot captured; after-image timed out','browser_full_visual_pass':False,'android_real_device':False,'private_cdn_tested':False,'blender_native_tested':False,'status':'candidate_static_and_webgl_load_verified_partial_visual'}
(OUT/'V015_integrity_qa.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'old':len(old),'new':len(new),'unchanged':len(old)-len(changed),'changed':changed,'added':added,'status':out['status']},ensure_ascii=False))