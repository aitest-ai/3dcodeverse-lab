"""Verify real GLB structures, collision/route, frozen predecessor assets and project boundaries."""
import json,hashlib,os,sys
from pathlib import Path
import numpy as np,trimesh

ROOT=Path(os.environ.get('DATE_V005_ROOT',str(Path(__file__).resolve().parent.parent/'runtime')))
D=ROOT/'dist';V4=ROOT/'V004_source_manifest.json';info=json.loads((D/'v005_manifest.json').read_text());view=json.loads((D/'scene_view.json').read_text())
prev=json.loads(V4.read_text());baseview=json.loads((ROOT/'V004_source_view.json').read_text())
assert view['route'][:len(baseview['route'])]==baseview['route'],'Entire V004 route must be unchanged'
assert view['extension_v005']['building_ids']==['way/283905573','way/283905580']
assert len(view['route'])>len(baseview['route'])
assert (D/'v005_collision.json').exists()
assert info['collision']['sha256']==hashlib.sha256((D/'v005_collision.json').read_bytes()).hexdigest()
assert view['extension']['collision_sha256_v004']==hashlib.sha256((D/'extension_collision.json').read_bytes()).hexdigest()
assert view['extension_v005']['models']==info['models']
assert view['extension']=={**baseview['extension'],'collision_sha256_v004':view['extension']['collision_sha256_v004']}
assert info['collision']['posts']==9
log={'version':'V005-east-candidate-r1','route_old_m':baseview['route'][-1]['s'],'route_new_m':view['route'][-1]['s'],
     'legacy_file_changes':[],'legacy_file_unchanged':[],'models':{},'ok':True}
# Frozen file manifest copied from original R1. Only expected source files differ.
import zipfile
original=Path(os.environ.get('V004_RUNTIME_ZIP','/mnt/data/Noboribetsu_Date_V004_R1_Runtime.zip'))
with zipfile.ZipFile(original) as z:
 for n in z.namelist():
  if not n.startswith('dist/') or n.endswith('/'):continue
  local=D/Path(n).relative_to('dist')
  assert local.is_file(),n
  hashmatch=hashlib.sha256(local.read_bytes()).digest()==hashlib.sha256(z.read(n)).digest()
  (log['legacy_file_unchanged'] if hashmatch else log['legacy_file_changes']).append(n)
assert set(log['legacy_file_changes'])<=set(['dist/app.js','dist/index.html','dist/qa.json','dist/scene_view.json'])
for name,item in info['models'].items():
 file=D/item['path'];buf=file.read_bytes()
 assert len(buf)==item['bytes'] and hashlib.sha256(buf).hexdigest()==item['sha256']
 scene=trimesh.load(file,force='scene',process=False)
 assert len(scene.geometry)>0
 triangles=sum(len(mesh.faces) for mesh in scene.geometry.values())
 assert triangles>0
 assert np.all(np.isfinite(scene.bounds))
 missing_uv=sum(1 for mesh in scene.geometry.values() if name.endswith('signs.glb') and (getattr(mesh.visual,'uv',None) is None or len(mesh.visual.uv)!=len(mesh.vertices)))
 assert missing_uv==0
 log['models'][name]={'sha256':item['sha256'],'bytes':item['bytes'],'meshes':len(scene.geometry),'triangles':triangles,
                      'bounds':[list(map(float,r)) for r in scene.bounds]}
assert len(log['legacy_file_changes'])==4
log['status']='PASS_STATIC_ASSETS_NOT_REAL_BROWSER'
(ROOT/'V005_assets_qa.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(log,ensure_ascii=False,indent=2))