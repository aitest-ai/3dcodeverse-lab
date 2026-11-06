"""Independent bounded collision checks on actual Chromium evaluated surfaces."""
import json,array,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v06.collision import crossings
W=R/'work/v17-qa';E=R/'evidence-v17';rows=[]
for row in json.loads((W/'regions-index.json').read_text())['files']:
 F=R/'library-v17'/('vroid-'+row['key']+'-motion-review')/row['version'];regions=json.loads((F/'collision-regions.json').read_text());remap={v:i for i,v in enumerate(row['ids'])};tri=lambda ts:[tuple(remap[i] for i in t) for t in ts];hands={s:tri(t) for s,t in regions['hand_triangles'].items()};cloth=tri(regions['cloth_triangles']);skin=tri([t for a in regions['arms'].values() for t in a['skin_triangles']]);sleeve=tri([t for a in regions['arms'].values() for t in a['sleeve_triangles']]);f=array.array('f');f.frombytes((W/row['file']).read_bytes());N=row['vertices'];assert sys.byteorder=='little' and len(f)==row['samples']*2*N*3
 variants=[];base_pairs=[]
 for slot in range(2):
  samples=[]
  for i in range(row['samples']):
   offset=(i*2+slot)*N*3;vs=[Vector(f[offset+j*3:offset+j*3+3]) for j in range(N)];pairs=set(crossings(vs,skin))
   if slot==0:base_pairs.append(pairs)
   samples.append({'t':i/120,'hand_skin_self_pairs':max(len(crossings(vs,ts)) for ts in hands.values()),'hand_skirt_pairs':max(len(crossings(vs,ts,cloth)) for ts in hands.values()),'sleeve_skin_pairs':len(crossings(vs,sleeve,skin)),'sleeve_self_pairs':len(crossings(vs,sleeve)),'arm_skin_self_pairs':len(pairs),'new_arm_skin_self_pairs':len(pairs-base_pairs[i])})
  variants.append({'variant':'before' if slot==0 else 'corrected','model_sha256':row['sha256'][slot],**{'maximum_'+k:max(s[k] for s in samples) for k in samples[0] if k!='t'},'samples':samples})
 rows.append({'key':row['key'],'hz':120,'variants':variants});print(row['key'],[{k:v for k,v in x.items() if k!='samples'} for x in variants],flush=True)
result={'method':'Actual Chromium skin/morph vertices, proper triangle edge crossings. Same-phase baseline pair sets distinguish retained source skin folds from new crossings. Shared/seam vertices and isolated nails excluded. Not containment, coplanar overlap, cloth thickness or full-body approval.','entries':rows,'art_approved':False}
(E/'browser-crossings.json').write_text(json.dumps(result,indent=2)+'\n')
for r in rows:
 b=r['variants'][1]
 for k in ['hand_skin_self_pairs','hand_skirt_pairs','sleeve_skin_pairs','sleeve_self_pairs','new_arm_skin_self_pairs']:assert b['maximum_'+k]==0,(r['key'],k,b['maximum_'+k])
print('V17_BOUNDED_CROSSINGS_PASS')
