"""Structure/source preservation and independent recorded evidence. Not art or gameplay approval."""
import json,hashlib,sys,math,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from v05.overlay import read
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def values(d,b,index):
 a=d['accessors'][index];v=d['bufferViews'][a['bufferView']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];fmt={5121:'B',5123:'H',5125:'I',5126:'f'}[a['componentType']];size=struct.calcsize(fmt)*n;offset=v.get('byteOffset',0)+a.get('byteOffset',0);return [struct.unpack_from('<'+str(n)+fmt,b,offset+i*v.get('byteStride',size)) for i in range(a['count'])]
def body_signature(d,b,key):
 maps=json.loads((R/'library-v09/horse-diagnostics'/(key+'.json')).read_text())['vertex_maps'];body={};faces=[]
 for mapping in maps:
  p=d['meshes'][0]['primitives'][mapping['primitive']];native={int(v):int(k) for k,v in mapping['indices'].items()};pos=values(d,b,p['attributes']['POSITION']);joints=values(d,b,p['attributes']['JOINTS_0']);weights=values(d,b,p['attributes']['WEIGHTS_0'])
  for glb,idx in native.items():body[idx]={'position':pos[glb],'weights':sorted((d['nodes'][d['skins'][0]['joints'][j]]['name'],w) for j,w in zip(joints[glb],weights[glb]) if w>0)}
  # Primitive seams can duplicate native vertices; canonical triangle topology is checked in Blender, not inferred here.
 return {tuple(v['position']):dict(v['weights']) for v in body.values()}
rows=[];signatures=[]
for key in ['horse-brown','horse-white']:
 F=R/'library-v10'/(key+'-grounded-review')/'0.1.0';meta=json.loads((F/'adaptation.json').read_text());profile=json.loads((F/'skeleton-profile.json').read_text());assert profile['editable_master_sha256']==meta['mother_sha256'] and profile['model_sha256']==meta['model_sha256'] and profile['version']==meta['version'];a,ab=read(R/meta['source_glb']);d,b=read(F/'model.glb');assert h(R/meta['source_glb'])==meta['source_glb_sha256'];assert h(R/meta['source_mother'])==meta['source_mother_sha256'];assert h(F/'model.glb')==meta['model_sha256'];assert meta['model_sha256']==next(x['model_sha256'] for x in json.loads((R/'config-v10/horses.lock.json').read_text())['assets'] if x['source_id']==key);assert h(F/'model.blend')==meta['mother_sha256'];assert b[:len(ab)]==ab
 for field in ['nodes','meshes','skins','materials','textures','images','samplers','extensions','extensionsUsed','extensionsRequired']:assert a.get(field)==d.get(field),field
 for field in ['accessors','bufferViews']:assert d[field][:len(a[field])]==a[field]
 assert len(d['animations'])==13 and len(d['skins'][0]['joints'])==50
 for old,new in zip(a['animations'],d['animations']):
  assert old['name']==new['name']
  if new['name'] not in ['Walk','Gallop']:assert old==new
  else:
   for sampler in new['samplers']:
    ts=values(d,b,sampler['input']);vs=values(d,b,sampler['output']);assert ts[0][0]==0 and all(x[0]<y[0] for x,y in zip(ts,ts[1:]));assert all(math.isfinite(v) for row in vs for v in row)
   for ch in new['channels']:
    vs=values(d,b,new['samplers'][ch['sampler']]['output']);error=max(abs(x-y) for x,y in zip(vs[0],vs[-1]));qerr=max(abs(x+y) for x,y in zip(vs[0],vs[-1]));assert min(error,qerr if ch['target']['path']=='rotation' else error)<1e-6
 signatures.append(body_signature(a,ab,key));rows.append({'asset_id':meta['asset_id'],'model_sha256':meta['model_sha256'],'original_binary_and_geometry':'exactly preserved','unchanged_clips':11,'corrected_clips':['Walk','Gallop']})
a,b=signatures;shared=a.keys()&b.keys();unmatched=set(b)-set(a);pairs=[(x,x) for x in shared]
for x in sorted(set(a)-set(b)):
 y=min(unmatched,key=lambda y:math.dist(x,y));assert math.dist(x,y)<2e-6,'Different body shape requires new fitting';unmatched.remove(y);pairs.append((x,y))
assert not unmatched and len(pairs)==6548
position_error=max(math.dist(x,y) for x,y in pairs);weight_error=max(abs(a[x].get(k,0)-b[y].get(k,0)) for x,y in pairs for k in a[x].keys()|b[y].keys());assert weight_error<1e-6
src_a,_=read(R/'library-v04/horse-brown/2.3.0/model.glb');src_b,_=read(R/'library-v04/horse-white/2.3.0/model.glb');assert src_a['nodes']==src_b['nodes']
correspondence={'vertices':6548,'exact_positions':len(shared),'maximum_native_position_difference':position_error,'maximum_weight_difference':weight_error,'node_rest_definitions_equal':True,'note':'Native vertex order and material primitive partition differ; matching uses spatial positions and named bone weights.'}
E=R/'evidence-v10';diagnostics=json.loads((E/'horse-diagnostics.json').read_text())['entries'];assert len(diagnostics)==4
for row in diagnostics:assert row['summary'][1]['minimum_sole_y_m']>=0 and row['summary'][1]['loop_seam_m']<.0001 and row['summary'][1]['maximum_cold_body_surface_error_m']<.00003
report={'status':'source preservation + recorded browser contact/loop + cold body parity passed','entries':rows,'brown_white_body_correspondence':correspondence,'material_partitions_and_mane_geometry':'different source variants retained independently','adaptation_scope':'same body surface/weights after spatial correspondence (native vertex order differs) and joint rest; different material partition and mane geometry preserved; not a second anatomical body shape','art_approved':False,'game_ready':False};(E/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
