"""Byte-preservation and candidate-lock checks. No art/locomotion verdict is inferred."""
import hashlib,json,sys,struct,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from v05.overlay import read
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 catalog=json.loads((R/'library-v05/catalog.json').read_text());checked=[]
 for e in catalog['entries']:
  model=R/e['model']['url'].removeprefix('../');folder=model.parent;meta=json.loads((folder/'adaptation.json').read_text());src=R/meta['target_source'];original,before=read(src);doc,after=read(model)
  assert sha(model)==e['model']['sha256'] and model.stat().st_size==e['model']['bytes'];assert sha(src)==meta['target_sha256'];assert after[:len(before)]==before
  for key in ['meshes','skins','materials','textures','images','samplers','extensions','extensionsUsed','extensionsRequired']:assert doc.get(key)==original.get(key),(e['id'],key)
  assert doc['nodes'][:-1]==original['nodes'];assert doc['accessors'][:len(original['accessors'])]==original['accessors'];assert doc['bufferViews'][:len(original['bufferViews'])]==original['bufferViews'];assert len(doc['nodes'])==len(original['nodes'])+1
  assert not e['art_approved'] and not e['game_ready'];assert sha(R/e['profile'].removeprefix('../'))==e['profile_sha256']
  for a in doc['accessors'][len(original['accessors']):]:
   v=doc['bufferViews'][a['bufferView']];count=a['count']*{'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']];values=struct.unpack_from('<'+'f'*count,after,v['byteOffset']);assert all(math.isfinite(x) for x in values)
  for row in json.loads((folder/'files.json').read_text())['files']:assert sha(folder/row['file'])==row['sha256'],row['file']
  checked.append({'id':e['id'],'sha256':sha(model),'source_geometry_skin_material_texture_vrm_bytes':'identical','clips':len(doc['animations'])})
 evidence=R/'evidence-v05/browser-contacts.json'
 if evidence.exists():
  for row in json.loads(evidence.read_text())['entries']:
   fixed=row['summary'][1];assert fixed['minimum_sole_y_m']>=0,(row['key'],row['clip'],'ground');assert fixed['maximum_browser_vs_blender_at_baked_frames_m']<.0001,(row['key'],row['clip'],'runtime mismatch')
 print(json.dumps({'status':'STRUCTURAL_SOURCE_AND_LOCK_CHECKS_PASS_NOT_ART_APPROVAL','entries':checked},indent=2))
if __name__=='__main__':verify()
