"""Bounded crossings from actual browser hand/garment vertices, both variants."""
import json,array,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v06.collision import crossings
W=R/'work/v16-qa';E=R/'evidence-v16';rows=[]
for row in json.loads((W/'regions-index.json').read_text())['files']:
 F=R/'library-v16'/('vroid-'+row['key']+'-motion-review')/row['version'];regions=json.loads((F/'collision-regions.json').read_text());remap={v:i for i,v in enumerate(row['ids'])};tri=lambda ts:[tuple(remap[i] for i in t) for t in ts];hands={s:tri(t) for s,t in regions['hand_triangles'].items()};cloth=tri(regions['cloth_triangles']);f=array.array('f');f.frombytes((W/row['file']).read_bytes());N=row['vertices'];assert sys.byteorder=='little' and len(f)==row['samples']*2*N*3
 variants=[]
 for slot in range(2):
  samples=[]
  for i in range(row['samples']):
   offset=(i*2+slot)*N*3;vs=[Vector(f[offset+j*3:offset+j*3+3]) for j in range(N)];samples.append({'t':i/120,'hand_skin_self_pairs':{s:len(crossings(vs,ts)) for s,ts in hands.items()},'hand_skirt_pairs':{s:len(crossings(vs,ts,cloth)) for s,ts in hands.items()}})
  variants.append({'variant':'before' if slot==0 else 'corrected','model_sha256':row['sha256'][slot],'maximum_hand_skin_self_pairs':max(v for s in samples for v in s['hand_skin_self_pairs'].values()),'maximum_hand_skirt_pairs':max(v for s in samples for v in s['hand_skirt_pairs'].values()),'samples':samples})
 rows.append({'key':row['key'],'hz':120,'variants':variants});assert variants[1]['maximum_hand_skin_self_pairs']==0;assert variants[1]['maximum_hand_skirt_pairs']==0;print(row['key'],[(v['variant'],v['maximum_hand_skin_self_pairs'],v['maximum_hand_skirt_pairs']) for v in variants],flush=True)
(E/'browser-crossings.json').write_text(json.dumps({'method':'Actual Chromium skin vertices, proper triangle edge crossings; shared/seam vertices and original nail components excluded. Not containment, coplanar, garment thickness, sleeves, full-body collision, or human art approval.','entries':rows,'art_approved':False},indent=2)+'\n')
