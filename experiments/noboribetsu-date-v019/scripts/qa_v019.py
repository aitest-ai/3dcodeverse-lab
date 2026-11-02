#!/usr/bin/env python3
import hashlib,json,sys,os,zipfile,math,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent;DIST=ROOT/'runtime'/'dist';O=ROOT/'qa';O.mkdir(exist_ok=True)
V018=Path(os.environ.get('V018_RUNTIME_ZIP','/mnt/data/Noboribetsu_Date_V018_R1_Runtime.zip'))
prior=zipfile.ZipFile(V018)
changed=[];unchanged=[]
for name in prior.namelist():
 data=prior.read(name)
 if (ROOT/'runtime'/name).read_bytes()==data:unchanged.append(name)
 else:changed.append(name)
assert sorted(changed)==sorted(['dist/app.js','dist/index.html','dist/qa.json','dist/scene_view.json','dist/style.css'])
assert len(unchanged)==len(prior.namelist())-5
manifest=json.loads((DIST/'scene_view.json').read_text());guide=json.loads((DIST/'v019_porch_guide.json').read_text());a=json.loads(prior.read('dist/scene_view.json'))
assert guide['source_scene_v018_sha256']==hashlib.sha256(prior.read('dist/scene_view.json')).hexdigest()
assert guide['source_v017_clearance_sha256']==hashlib.sha256(prior.read('dist/v017_clearance_audit.json')).hexdigest()
assert [p['s_m'] for p in guide['samples']]==[85+i*1.5 for i in range(13)]
for k in ['route','models','buildings','origin']:
 assert manifest[k]==a[k],k
for n in ['navigation.js','controls.js','walk-session.js','input-events.js','collision.json','extension_collision.json','v005_collision.json','v006_collision.json']:
 assert (DIST/n).read_bytes()==prior.read('dist/'+n)
assert manifest['porch_guide_v019']['sha256']==hashlib.sha256((DIST/'v019_porch_guide.json').read_bytes()).hexdigest()
assert 'import * as THREE' in (DIST/'app.js').read_text()
assert 'v019_guide' in (DIST/'app.js').read_text()
assert 'V019_PORCH_GUIDANCE_ONLY' in (DIST/'app.js').read_text()
assert 'porchGuideToggleButton' in (DIST/'index.html').read_text()
assert 'v019_porch_guide.json' in manifest['porch_guide_v019']['path']
subprocess.run(['node','--check',str(DIST/'app.js')],check=True)
qa={'schema':'noboribetsu-date-v019-source-contract-qa/1','pass':True,'v018_unchanged':len(unchanged),'v018_modified':changed,'v018_assets_unchanged':True,'v018_route_collision_unchanged':True,'v019_guide_markers':len(guide['samples']),'guide_sha256':manifest['porch_guide_v019']['sha256'],'v018_original_sha256':hashlib.sha256(V018.read_bytes()).hexdigest(),'blender_native_tested':False,'android_real_tested':False,'private_site_https_tested':False}
(O/'V019_source_qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n');print(json.dumps(qa,ensure_ascii=False,indent=2))