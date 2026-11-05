"""Blender BVH + proper edge/triangle intersections on ACTUAL BROWSER vertices, sampled at 120 Hz."""
import sys,json,array
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from v06.collision import crossings
E=R/'evidence-v06';W=R/'work/v06-qa';r=json.loads((E/'collision-regions.json').read_text());index=json.loads((W/'regions-index.json').read_text());remap={v:i for i,v in enumerate(index['ids'])};tri=lambda ts:[tuple(remap[i] for i in t) for t in ts];cloth,legs=tri(r['cloth_triangles']),tri(r['leg_triangles']);hands={s:tri(ts) for s,ts in r['hand_triangles'].items()};entries=[]
for row in index['files']:
 f=array.array('f');f.frombytes((W/row['file']).read_bytes());assert sys.byteorder=='little';N=row['vertices'];assert len(f)==row['samples']*2*N*3;variants=[]
 for slot in range(2):
  samples=[]
  for i in range(row['samples']):
   offset=(i*2+slot)*N*3;vs=[Vector(f[offset+j*3:offset+j*3+3]) for j in range(N)];samples.append({'t':i/120,'skirt_leg_pairs':len(crossings(vs,cloth,legs)),'hand_skin_self_pairs':{s:len(crossings(vs,ts)) for s,ts in hands.items()}})
  variants.append({'version':'0.2.0' if slot else '0.1.0','maximum_skirt_leg_pairs':max(x['skirt_leg_pairs'] for x in samples),'maximum_hand_skin_self_pairs':{s:max(x['hand_skin_self_pairs'][s] for x in samples) for s in hands},'samples':samples})
 entries.append({'clip':row['clip'],'samples_per_version':row['samples'],'hz':120,'variants':variants});print(row['clip'],[(v['version'],v['maximum_skirt_leg_pairs'],v['maximum_hand_skin_self_pairs']) for v in variants],flush=True)
report={'method':'Actual Chromium Three.js Bodybaked vertices; BVH broad phase + six proper segment/triangle crossing tests; excludes shared/coincident seam vertices. Not solid containment/coplanar contact/full-body collision/cloth simulation.','regions':{'skirt_triangles':len(cloth),'leg_triangles':len(legs),'hand_skin_triangles':{s:len(t) for s,t in hands.items()}},'retained_source_nail_attachments':'Five disconnected 32-vertex nail pieces per hand, each fully bound to its matching distal finger; original nail/skin overlaps are retained and separately identified in collision-regions.json, excluded from skin-to-skin self-crossing.','entries':entries,'human_art':'not-tested'};(E/'browser-crossings.json').write_text(json.dumps(report,indent=2)+'\n')
assert len(entries)==7
for e in entries:
 b=e['variants'][1];assert b['maximum_skirt_leg_pairs']==0 and max(b['maximum_hand_skin_self_pairs'].values())==0,(e['clip'],b)
print('BOUNDED_BROWSER_CROSSINGS_PASS',flush=True)
