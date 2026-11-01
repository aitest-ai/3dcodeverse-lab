#!/usr/bin/env python3
"""Package reproducible frozen candidate, include source+QA and exact SHA manifest."""
import hashlib,json,shutil,zipfile
from pathlib import Path
w=Path(__file__).parent;dest=w.parent
basename='Noboribetsu_Date_V009_R1_'
qa_names={'model':'outputs/v009_model_qa.json','runtime':'evidence/v009_runtime_contract.json',
 'navigation':'runtime/evidence/V009_navigation_qa.json','review':'evidence/review_dom_qa.json',
 'http':'evidence/http_qa.json','webgl':'evidence/webgl_context_qa.json',
 'replay':'evidence/replay_sha.json','integrity':'evidence/integrity_qa.json'}
q={k:json.loads((w/f).read_text()) for k,f in qa_names.items()}
assert all(q[t]['status'].startswith('PASS') for t in ('runtime','navigation','review','http','replay','integrity'))
assert q['model']['status']=='GLB_RELOADED_STRUCTURAL_REPAIR_VERIFIED'
assert q['webgl']['status']=='UNAVAILABLE_IN_CURRENT_CONTAINER'
validation={'schema':'noboribetsu-date-v009-validation/1','status':'CANDIDATE_PASS_STATIC_AND_SOURCE_ONLY',
 'version':'V009-utsuroi-candidate-r1','checks':{k:{'status':v['status']} for k,v in q.items()},
 'metrics':{'route_m':231.56641497226084,'route_points':472,'A_B_route_checks':944,
   'original_faces':17008,'removed_side_wood_boxes':20,'removed_faces':240,
   'added_faces':336,'final_faces':17104,'source_unchanged_files':68,
   'original_v008_dist_files':72,'new_v009_dist_files':83,
   'archived_facade_model_bytes_deferred':1702296},
 'model_sha256':q['model']['glb_v009_sha256'],
 'not_tested':['actual Three.js WebGL2 scene and FPS','Android hardware','private website CDN/login',
   'Blender 5.2.3 .blend and Cycles','current 2026 Utsuroi-kan front elevation'],
 'official_use_reference':'https://edo-trip.jp/facility/utsuroi-kan/',
 'visualization':'VTK fixed camera GLB comparison (NOT actual Three.js screenshot)',
 'source_archive_required':'Noboribetsu_Date_V008_R1_Runtime.zip'
}
(d:=dest/(basename+'Validation.json')).write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
shutil.copy2(w/'DELIVERY_REPORT.md',dest/(basename+'Delivery_Report.md'))
shutil.copy2(w/'outputs/Noboribetsu_Date_V009_R1_Review.html',dest/(basename+'Review.html'))
shutil.copy2(w/'outputs/v009_utsuroi_facade.glb',dest/(basename+'Utsuroi_Facade.glb'))
# Runtime entire V008 assets unchanged except four files, plus derived V009 and QA.
root=w/'runtime'
shutil.copy2(w/'README.md',root/'README.md')
shutil.copy2(w/'START_HERE_V009.md',root/'START_HERE_V009.md')
shutil.copy2(w/'start_v009_local.py',root/'start_v009_local.py')
shutil.copy2(w/'DELIVERY_REPORT.md',root/'V009_Delivery_Report.md')
shutil.copy2(d,root/'V009_R1_Validation.json')
rt=dest/(basename+'Runtime.zip')
with zipfile.ZipFile(rt,'w',allowZip64=True) as z:
 for f in sorted(root.rglob('*')):
  if f.is_file():
   name=f.relative_to(root).as_posix()
   # ZIP compression is lossless; preserve the same full-resolution source files.
   z.write(f,arcname=name,compress_type=zipfile.ZIP_DEFLATED,compresslevel=5)
# Source, tests, glb and diagnostic images are self-contained except frozen V008 input.
source=dest/(basename+'SourceQA.zip')
files=['README.md','DELIVERY_REPORT.md','START_HERE_V009.md','build_v009_utsuroi.py',
 'integrate_v009.py','render_v009_compare.py','v009_vtk_actor.py','make_v009_review.py',
 'test_v009_runtime.mjs','test_v009_navigation.mjs','test_v009_review.py',
 'test_v009_http.py','verify_v009_delivery.py','probe_v009_webgl.py',
 'blender_v009_extension_import.py','package_v009.py']
with zipfile.ZipFile(source,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7,allowZip64=True) as z:
 for name in files:z.write(w/name,arcname=name)
 z.write(w/'outputs/v009_utsuroi_facade.glb',arcname='outputs/v009_utsuroi_facade.glb')
 z.write(d,arcname=d.name)
 for f in sorted((w/'evidence').rglob('*')):
  if f.is_file():z.write(f,arcname='evidence/'+f.name)
 z.write(w/'runtime/evidence/V009_navigation_qa.json',arcname='evidence/V009_navigation_qa.json')
 for f in sorted((w/'outputs').glob('*.png')):z.write(f,arcname='outputs/'+f.name)
 z.write(w/'outputs/Noboribetsu_Date_V009_R1_Review.html',arcname='outputs/Noboribetsu_Date_V009_R1_Review.html')

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
artifacts=[dest/(basename+suffix) for suffix in ('Runtime.zip','SourceQA.zip','Review.html','Delivery_Report.md','Validation.json','Utsuroi_Facade.glb')]
for zf in (rt,source):
 with zipfile.ZipFile(zf) as z:
  bad=z.testzip()
  if bad:raise RuntimeError('Invalid ZIP member '+bad)
entries=[{'filename':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in artifacts]
manifest={'schema':'noboribetsu-date-v009-delivery-manifest/1','status':'ZIP_CRC_AND_HASHES_VERIFIED',
 'artifacts':entries,'original_v008_archive_retained':True,'no_web_deployment':True}
(dest/(basename+'SHA256.json')).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':manifest['status'],'files':[(e['filename'],e['bytes']) for e in entries]},ensure_ascii=False,indent=2))