"""Bounded proper triangle crossings on actual Chromium vertex streams, not offline replacements."""
import sys,json,array
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from v06.collision import crossings
E=R/'evidence-v08';W=R/'work/v08-qa';index=json.loads((W/'regions-index.json').read_text());entries=[]
for row in index['files']:
 F=R/'library-v08'/('vroid-'+row['key']+'-motion-review')/row['version'];r=json.loads((F/'collision-regions.json').read_text());remap={v:i for i,v in enumerate(row['ids'])};tri=lambda ts:[tuple(remap[i] for i in t) for t in ts];cloth,legs=tri(r['cloth_triangles']),tri(r['leg_triangles']);hands={s:tri(t) for s,t in r['hand_triangles'].items()};f=array.array('f');f.frombytes((W/row['file']).read_bytes());N=row['vertices'];assert sys.byteorder=='little' and len(f)==row['samples']*row['slots']*N*3;variants=[]
 for slot in range(row['slots']):
  samples=[]
  for i in range(row['samples']):
   offset=(i*row['slots']+slot)*N*3;vs=[Vector(f[offset+j*3:offset+j*3+3]) for j in range(N)];samples.append({'t_B_s':i/120,'skirt_leg_pairs':len(crossings(vs,cloth,legs)),'hand_skin_self_pairs':{s:len(crossings(vs,ts)) for s,ts in hands.items()}})
  variants.append({'variant':'corrected','maximum_skirt_leg_pairs':max(x['skirt_leg_pairs'] for x in samples),'maximum_hand_skin_self_pairs':{s:max(x['hand_skin_self_pairs'][s] for x in samples) for s in hands},'samples':samples})
 entries.append({'model_sha256':row['model_sha256'],'key':row['key'],'clip':row['clip'],'hz':120,'samples_per_variant':row['samples'],'regions':{'cloth_triangles':len(cloth),'leg_triangles':len(legs),'hand_skin_triangles':{s:len(t) for s,t in hands.items()},'leg_region':r['leg_region']},'variants':variants});print(row['key'],row['clip'],[(v['variant'],v['maximum_skirt_leg_pairs'],v['maximum_hand_skin_self_pairs']) for v in variants],flush=True)
report={'method':'Actual browser float32 vertex streams; BVH plus six proper edge/triangle tests. Shared/coincident seam vertices excluded. Not full-body containment/coplanar contact/thickness/cloth self-contact approval.','native_nails':'Original disconnected 32-vertex distal-finger nail pieces retain original nail/skin attachments; separated from hand Skin self-crossing.','entries':entries,'art_approved':False};(E/'browser-crossings.json').write_text(json.dumps(report,indent=2)+'\n');assert len(entries)==4
for e in entries:
 b=e['variants'][0];assert b['maximum_skirt_leg_pairs']==0 and max(b['maximum_hand_skin_self_pairs'].values())==0,(e['key'],e['clip'])
print('V08_BOUNDED_CROSSINGS_PASS')
