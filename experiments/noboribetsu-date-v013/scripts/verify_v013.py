#!/usr/bin/env python3
"""Read-only V013 asset, geometry, and freeze invariant verification."""
import json,zipfile,hashlib,sys
from pathlib import Path
import numpy as np,trimesh

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def go(before,after,patch,glb,qa_dir):
 before=Path(before);after=Path(after);qa_dir=Path(qa_dir);qa_dir.mkdir(exist_ok=True,parents=True)
 obj=json.loads(Path(patch).read_text());assert obj['triangles']==2436 and obj['vertices']==1688
 vertex=np.array(obj['positions'],dtype=float).reshape(-1,3);idx=np.array(obj['indices'],dtype=int).reshape(-1,3)
 assert len(vertex)==1688 and idx.min()>=0 and idx.max()<len(vertex)
 geo=trimesh.Trimesh(vertices=vertex,faces=idx,process=False)
 assert len(geo.faces)==2436 and float(geo.area_faces.min())>1.e-5
 scene=trimesh.load(glb,force='scene',process=False);assert sum(len(g.faces) for g in scene.geometry.values())==2436
 pb=before/'dist';pa=after/'dist';v1=json.loads((pb/'scene_view.json').read_text());v2=json.loads((pa/'scene_view.json').read_text())
 assert len(v1['route'])==len(v2['route'])==472
 assert v1['route']==v2['route'] and v1['raw_route']==v2['raw_route']
 for k in ('terrain_gap_v011','transition_v012','extension','extension_v005','extension_v006'):
  assert v1[k]==v2[k],k
 unchanged=['dist/collision.json','dist/v011_terrain_gap_patch.json','dist/v012_road_grass_transition.json','dist/walk-session.js','dist/input-events.js','dist/assets/scene_A.glb','dist/assets/v004_merchant_road.glb','dist/assets/v005_east_road.glb']
 for k in unchanged:assert sha(before/k)==sha(after/k),k
 pre={str(p.relative_to(before)):sha(p) for p in before.rglob('*') if p.is_file()}
 new={str(p.relative_to(after)):sha(p) for p in after.rglob('*') if p.is_file()}
 changed=sorted(k for k in pre if new.get(k)!=pre[k]);added=sorted(set(new)-set(pre))
 assert changed==['dist/app.js','dist/index.html','dist/qa.json','dist/scene_view.json']
 assert added==['README_V013.md','V013_delta_qa.json','dist/v013_selective_road_grass.json']
 qa={'schema':'noboribetsu-date-v013-integrity/1','status':'PASS','original_files':len(pre),'unchanged_original_files':len(pre)-len(changed),'changed_original_files':changed,'new_files':added,'V011_gap_sha256':sha(after/'dist/v011_terrain_gap_patch.json'),'V012_edge_sha256':sha(after/'dist/v012_road_grass_transition.json'),'v013_json_sha256':sha(patch),'v013_glb_sha256':sha(glb),'triangles':len(geo.faces),'triangles_with_zero_area':int(np.sum(geo.area_faces<1e-5)),'route_m':v2['route'][-1]['s'],'model_and_collision_unchanged':True,'blender_native_tested':False,'android_hardware_tested':False}
 (qa_dir/'V013_integrity_qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(qa,ensure_ascii=False,indent=2))
if __name__=='__main__':go(*sys.argv[1:])