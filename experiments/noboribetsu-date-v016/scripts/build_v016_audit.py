#!/usr/bin/env python3
"""Validate V015 grounded facade with actual continuous plinth meshes.
V016 intentionally adds inspection markers, not speculative footing repairs.
Run after a fresh extraction of V015 Runtime.zip and SourceQA.zip.
"""
import json,hashlib,sys,zipfile
from pathlib import Path
import numpy as np,trimesh
ROOT=Path(__file__).resolve().parent
D=ROOT/'base/dist';O=ROOT/'outputs';O.mkdir(exist_ok=True)
QA=json.loads((ROOT/'source/evidence/V015_grounding_audit.json').read_text())
facade_path=D/'assets/v004_merchant_facades.glb'
facade=trimesh.load(facade_path,force='scene')
stone=facade.geometry['stone_foot']
assert hashlib.sha256(facade_path.read_bytes()).hexdigest()==QA['source_facades_sha256']
assert len(stone.vertices)==40 and len(stone.faces)==60, 'Expected 5 continuous source stone components'
# Each 8-vertex block is one source plinth, not an independent sampled post.
blocks=[]
for i in range(len(stone.vertices)//8):
 pts=np.asarray(stone.vertices)[i*8:(i+1)*8]
 bounds=pts.min(axis=0),pts.max(axis=0)
 blocks.append({'index':i,'min':np.round(bounds[0],6).tolist(),'max':np.round(bounds[1],6).tolist(),'height_m':round(float(bounds[1][1]-bounds[0][1]),6)})
assert abs(blocks[0]['height_m']-.55)<1e-4 and abs(blocks[1]['height_m']-.55)<1e-4
buried=[x for x in QA['post_rows'] if x['status']=='buried']
assert len(buried)==4
rows=[]
for row in buried:
 x,z=row['position_x'],row['position_z'];y=row['visible_surface_y'];floor=row['original_plinth_bottom_y']
 matches=[b for b in blocks if b['min'][0]-.1<=x<=b['max'][0]+.1 and b['min'][2]-.5<=z<=b['max'][2]+2]
 # Expected original horizontal stone base is at z about 0.29-1.47 m behind sample line;
 # assign the building's 0/1 known continuous base rather than guessing independent posts.
 idx=0 if row['osm_id']=='way/283905599' else 1
 b=blocks[idx];assert b['min'][0]<=x<=b['max'][0]+1e-3
 assert abs(floor-b['min'][1])<2e-4
 bury=y-floor;remain=b['height_m']-bury
 assert .04<bury<.12 and remain>.4
 rows.append({'building':row['building'],'osm_id':row['osm_id'],'sample_index':row['post_index'],
 'x':x,'z':z,'surface_y':y,'plinth_bottom_y':floor,'burial_depth_m':round(bury,5),
 'remaining_exposed_height_m':round(remain,5),'remaining_exposed_fraction':round(remain/b['height_m'],4),
 'continuous_plinth_block':idx,'marker_y':round(y+.025,5)})
obj={'schema':'noboribetsu-date-v016-grade-inspection/1','stage':'B','diagnostic_only':True,
 'default_visible':False,'original_geometry_modified':False,'route_changed':False,'collision_changed':False,
 'new_architecture':False,'author_estimated':True,'sample_count':4,
 'original_plinth_blocks':blocks[:2], 'burial_samples':rows,
 'interpretation':'Four buried readings are SAMPLE LOCATIONS along two continuous 0.55m stone plinths, not four separate stone posts. Existing stone visible above grade 0.442-0.488m. Do not blindly add four stones or raise whole buildings.',
 'source_facades_sha256':QA['source_facades_sha256'],'source_v015_patch_sha256':QA['patch_sha256'],
 'notes':'Surface estimates are inherited from V015 road/terrain audit, not on-site surveying.'}
raw=(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n').encode()
(O/'v016_grade_inspection.json').write_bytes(raw)
obj_qa={'schema':'noboribetsu-date-v016-audit/1','status':'SOURCE_GEOMETRY_PASS_VISUAL_PENDING','sample_count':len(rows),'distinct_original_plinths':2,
 'preserved_base_components':len(blocks),'exposed_height_min_m':min(x['remaining_exposed_height_m'] for x in rows),
 'exposed_height_max_m':max(x['remaining_exposed_height_m'] for x in rows),
 'original_facade_mesh_sha256':QA['source_facades_sha256'],
 'v016_json_sha256':hashlib.sha256(raw).hexdigest(),
 'false_independent_post_assumption_corrected':True,'no_new_footing_geometry':True,
 'source_road_sha256':QA['source_road_sha256'],
 'source_v015_supports_intact':True}
(O/'V016_audit_qa.json').write_text(json.dumps(obj_qa,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(obj_qa,ensure_ascii=False,indent=2))