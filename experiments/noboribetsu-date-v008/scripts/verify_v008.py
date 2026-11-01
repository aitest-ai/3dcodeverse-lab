#!/usr/bin/env python3
"""Integrity of non-destructive V008 relative to exact V007 Runtime ZIP."""
from pathlib import Path
from collections import Counter
import hashlib,json,zipfile,sys,numpy as np,trimesh
work=Path(__file__).resolve().parent
root=work/'base';dist=root/'dist';old=Path('/mnt/data/Noboribetsu_Date_V007_R1_Runtime.zip')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with zipfile.ZipFile(old) as z:
    corrupted=z.testzip();assert corrupted is None,corrupted
    oldhash={i.filename:hashlib.sha256(z.read(i.filename)).hexdigest() for i in z.infolist() if not i.is_dir()}
unchanged=[k for k,h in oldhash.items() if (root/k).is_file() and sha(root/k)==h]
changed=[k for k in oldhash if k not in unchanged]
assert set(changed)=={'dist/app.js','dist/index.html','dist/qa.json','dist/scene_view.json'},changed
assert len(unchanged)==len(oldhash)-4
view=json.loads((dist/'scene_view.json').read_text());previous=json.loads(zipfile.ZipFile(old).read('dist/scene_view.json'))
assert view['version']=='V008-structure-candidate-r1';assert len(view['route'])==472
assert view['route']==previous['route'] and view['buildings']==previous['buildings']
assert view['models']==previous['models']
model=dist/'assets/v008_waraji_architecture.glb';contract=json.loads((dist/'v008_architecture_manifest.json').read_text());qa=json.loads((work/'outputs/v008_model_qa.json').read_text())
assert sha(model)==qa['v008_glb_sha256']==contract['model']['sha256']
original=trimesh.load(dist/'assets/v007_east_facades.glb',force='scene',process=False)
added=trimesh.load(model,force='scene',process=False)
assert len(original.geometry)==17 and len(added.geometry)==21
assert set(original.geometry).issubset(set(added.geometry))
maxdelta=0
for k,m in original.geometry.items():
 n=added.geometry[k]
 assert len(m.faces)==len(n.faces) and len(m.vertices)==len(n.vertices)
 assert np.array_equal(m.faces,n.faces),k
 d=np.max(np.linalg.norm(m.vertices-n.vertices,axis=1))
 maxdelta=max(maxdelta,float(d));assert d<8e-6,(k,d)
assert sum(len(m.faces) for m in added.geometry.values())==17008
assert sum(len(m.faces) for m in original.geometry.values())==14888
critical=['dist/collision.json','dist/extension_collision.json','dist/v005_collision.json','dist/v006_collision.json',
'dist/assets/scene_A.glb','dist/assets/v006_tail_road.glb','dist/assets/v005_east_road.glb',
'dist/assets/v005_east_facades.glb','dist/assets/v007_east_facades.glb','dist/navigation.js','dist/controls.js','dist/vendor/three.module.js']
assert all(k in unchanged for k in critical)
nav=json.loads((root/'evidence/V008_navigation_qa.json').read_text());node=json.loads((work/'evidence/V008_node_contract.json').read_text());browser=json.loads((work/'evidence/V008_browser_fallback_qa.json').read_text())
assert nav['status']=='PASS_STATIC_NAVIGATION_ONLY' and nav['checks']==944
assert node['status']=='PASS_NODE_LOGIC_NO_GPU' and node['archived_model_bytes_not_downloaded_on_initial_boot']==1027648
assert browser['status']=='PASS_DOM_FALLBACK_ONLY' and browser['fallback_images_loaded']==3
result={'schema':'noboribetsu-date-v008-integrity/1','status':'PASS_OFFLINE_SOURCE_GLTF_AND_LOGIC_ONLY',
  'original_files':len(oldhash),'unchanged_files':len(unchanged),'changed_existing':changed,
  'new_glb_sha256':sha(model),'new_glb_bytes':model.stat().st_size,'new_triangles':2120,
  'original_meshes_unchanged':17,'original_geometry_max_delta_m':maxdelta,'route_points':len(view['route']),
  'route_length_m':view['route'][-1]['s'],'collision_unchanged':True,
  'two_skipped_hidden_glbs_bytes':node['archived_model_bytes_not_downloaded_on_initial_boot'],
  'chromium_no_webgl_fallback':'PASS_DOM_ONLY','actual_webgl':'NOT_TESTED','android':'NOT_TESTED',
  'blender_native':'NOT_RUN','private_site':'UNCHANGED'}
(work/'evidence/V008_integrity.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))