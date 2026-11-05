"""Source preservation, exact ID/version/hash, and recorded diagnostics. Horse failures remain failures."""
import json,hashlib,sys,math,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from v05.overlay import read
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 F=R/'library-v09/quaternius-shibainu-grounded-review/0.2.0';m=json.loads((F/'adaptation.json').read_text());a,ab=read(R/m['base_model']);assert h(R/m['base_model'])==m['base_model_sha256'] and h(R/m['base_mother'])==m['base_mother_sha256']
 for name in ['model','baseline']:
  b,bb=read(F/(name+'.glb'));assert bb[:len(ab)]==ab
  for key in ['nodes','meshes','skins','materials','images','textures','samplers','extensions','extensionsUsed','extensionsRequired']:assert a.get(key)==b.get(key),key
  for key in ['accessors','bufferViews']:assert a[key]==b[key][:len(a[key])]
  assert a['animations']==b['animations'][:len(a['animations'])];assert len(b['animations'])==14
  for ac in b['accessors'][len(a['accessors']):]:
   n=ac['count']*{'SCALAR':1,'VEC3':3,'VEC4':4}[ac['type']];v=b['bufferViews'][ac['bufferView']];assert all(math.isfinite(x) for x in struct.unpack_from('<'+'f'*n,bb,v['byteOffset']))
 for row in json.loads((F/'files.json').read_text())['files']:assert h(F/row['file'])==row['sha256'],row['file']
 cat=json.loads((R/'library-v09/catalog.json').read_text())
 for e in cat['entries']:
  for p,sha in [(e['model']['url'],e['model']['sha256']),(e['profile'],e['profile_sha256']),(e['editable']['path'],e['editable']['sha256'])]:assert h(R/p.removeprefix('../'))==sha,p
  assert not e['art_approved'] and not e['game_ready']
  if e['variant']=='source':assert not e['root_clips'] and e['model']['sha256']==h(R/'sources-v04/horses'/(e['asset_id']+'-v2.3.glb'));assert h(R/e['diagnostic_profile'].removeprefix('../'))==e['diagnostic_profile_sha256']
 E=R/'evidence-v09';rows=json.loads((E/'browser-contacts.json').read_text())['entries'];assert len(rows)==2
 for r in rows:
  assert r['model_sha256']==[m['baseline_sha256'],m['model_sha256']];s=r['summary'][1];assert s['minimum_sole_y_m']>=0 and s['maximum_stance_center_xz_drift_m']<.003 and s['maximum_flat_patch_vertex_xz_drift_m']<.003 and s['maximum_browser_vs_build_baked_m']<.00002
 for r in json.loads((E/'browser-loops.json').read_text())['entries']:assert r['maximum_world_surface_jump_m'][1]<.0001
 for r in json.loads((E/'browser-blender-parity.json').read_text())['entries']:assert r['maximum_m']<.00003
 horses=json.loads((E/'horse-diagnostics.json').read_text())['entries'];assert len(horses)==26
 for r in horses:assert r['model_sha256']==next(e['model']['sha256'] for e in cat['entries'] if e['asset_id']==r['key'])
 assert all(r['minimum_sole_y_m']<0 for r in horses if r['clip'] in ['Walk','Gallop']);assert all(r['full_mesh_loop_seam_m']>.1 for r in horses if r['clip']=='Gallop');assert not json.loads((E/'browser-controls.json').read_text())['errors'];print(json.dumps({'status':'PRESERVATION_AND_RECORDED_DIAGNOSTICS_PASS_NOT_ART_APPROVAL','shiba_sha256':m['model_sha256'],'unchanged_shiba_clips':len(a['animations']),'horse_bytes':'unchanged v2.3.0','horse_walk_ground':'failed','horse_gallop_ground_and_loop':'failed','horse_world_sliding':'not-tested; no world speed plan'},indent=2))
if __name__=='__main__':verify()
