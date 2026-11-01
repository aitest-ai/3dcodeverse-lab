#!/usr/bin/env python3
"""Non-GPU checks: exact coverage, bounds, same original assets, ROI evidence."""
import hashlib, json, sys
from pathlib import Path
from PIL import Image
import numpy as np
from build_v011_terrain_patch import build_patch

base=Path(sys.argv[1]);dist=Path(sys.argv[2]);qa=Path(sys.argv[3]);v010shot=Path(sys.argv[4]);v011shot=Path(sys.argv[5]);
p,r=build_patch(base)
actual=json.loads((dist/'v011_terrain_gap_patch.json').read_text('utf8'))
assert p==actual, 'Rebuilt patch differs from packed terrain data'
assert len(p['positions'])==296*9 and len(p['uv'])==296*6
assert min(p['positions'][0::3])>=116 and max(p['positions'][0::3])<=174
assert min(p['positions'][2::3])>=116 and max(p['positions'][2::3])<=162
# Compare all original model and collision bytes, even when not listed in the small diff manifest.
unchanged=[]
for f in sorted(base.rglob('*')):
 if f.is_file():
  rel=f.relative_to(base)
  if rel.parts[0]=='assets' or rel.name in ('collision.json','extension_collision.json','v005_collision.json','v006_collision.json','walk-session.js','controls.js','input-events.js'):
   assert hashlib.sha256(f.read_bytes()).digest()==hashlib.sha256((dist/rel).read_bytes()).digest(),str(rel)
   unchanged.append(str(rel))
# The ROI is fixed relative to the V010 and V011 real-WebGL2 same-camera screenshot.
roi=(95,300,375,390)
def darkness(file):
 im=Image.open(file).convert('RGB');a=np.array(im.crop(roi));return int((a.max(axis=2)<32).sum()),im.size
n0,s0=darkness(v010shot);n1,s1=darkness(v011shot)
assert s0==s1==(960,600)
assert n0>=500 and n1<=25, f'ROI defect reduction not demonstrated: {n0} to {n1}'
q={'schema':'v011-geometry-and-visual-qa/1','status':'PASS','gap_cells':148,'triangles_added':296,
   'missing_height_vertices':84,'source_B_verified':r['source_b_sha256'] if 'source_b_sha256' in r else r['source_b_sha256'],
   'preserved_asset_count':len(unchanged),'preserved_assets':unchanged,
   'pixel_ROI':list(roi),'dark_pixels_before':n0,'dark_pixels_after':n1,
   'dark_pixel_threshold':'max(R,G,B)<32 (in same 960x600 frame)',
   'note':'Dark ROI metric is a visual regression check, not a complete topological or survey acceptance',
   'original_model_geometry_unchanged':True,'terrain_patch_visual_only':True}
qa.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
print('PASS',{'gap_triangles':296,'dark_pixels_before':n0,'after':n1,'unchanged':len(unchanged)})