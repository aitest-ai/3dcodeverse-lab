#!/usr/bin/env python3
"""Verify complete V007 runtime against immutable V006 ZIP and model geometry."""
from pathlib import Path
from collections import Counter
import json, hashlib, zipfile,sys
import numpy as np,trimesh
root=Path(__file__).resolve().parent
runtime=root/'base';dist=runtime/'dist';old=Path('/mnt/data/Noboribetsu_Date_V006_R1_Runtime.zip')
def sha(b):return hashlib.sha256(b).hexdigest()
def file_sha(p):return sha(p.read_bytes())
with zipfile.ZipFile(old) as z:
 orig={i.filename:sha(z.read(i.filename)) for i in z.infolist() if not i.is_dir()}
 statuses={k:file_sha(runtime/k) if (runtime/k).exists() else 'MISSING' for k in orig}
 unchanged=[k for k,v in statuses.items() if v==orig[k]]
 changed=[k for k,v in statuses.items() if v!=orig[k]]
 if set(changed)!={'dist/app.js','dist/index.html','dist/qa.json','dist/scene_view.json'}:
  raise AssertionError('Unexpected V006 file changes '+str(changed))
 if any(v=='MISSING' for v in statuses.values()):raise AssertionError('Missing old file')
 if len(unchanged)!=len(orig)-4:raise AssertionError('Unchanged count wrong')
route_old=json.loads(zipfile.ZipFile(old).read('dist/scene_view.json'))['route']
view=json.loads((dist/'scene_view.json').read_text());assert view['route']==route_old
assert view['version']=='V007-facade-candidate-r1';assert len(view['route'])==472
m=json.loads((dist/'v007_facade_manifest.json').read_text());assert m['schema']=='noboribetsu-date-v007-facade/1'
new=dist/m['model']['path'];assert file_sha(new)==m['model']['sha256']
old_model=trimesh.load(dist/'assets/v005_east_facades.glb',force='scene',process=False)
new_model=trimesh.load(new,force='scene',process=False)
assert set(old_model.geometry)==set(new_model.geometry)
no,nn=0,0;largest=0;unchanged_meshes=[]
for name,a in old_model.geometry.items():
 b=new_model.geometry[name]
 assert len(a.faces)==len(b.faces) and len(a.vertices)==len(b.vertices)
 no+=len(a.faces);nn+=len(b.faces)
 diff=np.max(np.linalg.norm(a.vertices-b.vertices,axis=1));largest=max(largest,float(diff))
 if name!='noren_blue':
  assert diff<.00001,(name,diff)
  unchanged_meshes.append(name)
 else:assert 0<diff<.019
assert no==nn==14888 and len(unchanged_meshes)==16
color_tex=[k for k,v in new_model.geometry.items() if getattr(v.visual.material,'baseColorTexture',None) is not None and k not in ('noren_blue',)]
assert set(color_tex)>=set(['wood_structure','wood_aged','wood_newer','wood_edges','plaster_warm','plaster_cool','plaster_lower'])
# Key V006 terrain/OSM assets and navigation are exactly the same files.
required=['dist/collision.json','dist/extension_collision.json','dist/v005_collision.json','dist/v006_collision.json','dist/assets/v006_tail_road.glb','dist/assets/v005_east_road.glb', 'dist/assets/v005_east_facades.glb','dist/assets/v005_east_signs.glb']
assert all(key in unchanged for key in required)
qa_dir=root/'v007_outputs'
node=json.loads((qa_dir/'runtime_contract_qa.json').read_text());nav=json.loads((runtime/'evidence/V007_navigation_qa.json').read_text());browser=json.loads((qa_dir/'browser_fallback_qa.json').read_text())
assert node['status'].startswith('PASS_') and nav['status'].startswith('PASS_') and browser['status'].startswith('PASS_')
assert nav['checks']==944 and not nav['failures']
result={'schema':'noboribetsu-date-v007-integrity/1','status':'PASS_SOURCE_AND_STATIC_TESTS_ONLY',
 'old_runtime_files':len(orig),'unchanged_old_files':len(unchanged),'modified_old_files':changed,
 'added_model_sha256':file_sha(new),'added_model_size_bytes':new.stat().st_size,
 'unchanged_facade_meshes':len(unchanged_meshes),'total_facade_meshes':len(new_model.geometry),
 'triangles':nn,'noren_max_displacement_m':largest,'new_procedural_textured_materials':sorted(color_tex),
 'route_length_m':view['route'][-1]['s'],'route_points':len(view['route']),
 'navigation_checks':nav['checks'],'browser_fallback_status':browser['status'],
 'webgl2_actual_scene':'NOT_TESTED','android':'NOT_TESTED','blender_native':'NOT_EXECUTED',
 'private_preview':'UNCHANGED','baseline_original_GLB_and_collision':'BYTE_IDENTICAL'}
(qa_dir/'v007_integrity_qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))