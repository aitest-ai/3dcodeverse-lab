"""Exact source/clip preservation, version locks and recorded evidence; not human art approval."""
import json,hashlib,sys,struct,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from v05.overlay import read
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 catalog=json.loads((R/'library-v07/catalog.json').read_text());report=[]
 for key,ver in [('vivi','0.3.0'),('vita','0.1.0')]:
  F=R/'library-v07'/('vroid-'+key+'-motion-review')/ver;meta=json.loads((F/'adaptation.json').read_text());original=R/meta['base_model' if key=='vivi' else 'original_geometry'];a,ab=read(original)
  for file in ['model.glb']+(['baseline.glb'] if key=='vita' else []):
   b,bb=read(F/file);assert bb[:len(ab)]==ab,(key,'prefix')
   for k in ['meshes','skins','materials','textures','images','samplers','extensions','extensionsUsed','extensionsRequired']:assert a.get(k)==b.get(k),(key,k)
   for k in ['accessors','bufferViews']:assert b[k][:len(a[k])]==a[k]
   assert b['nodes']==a['nodes'] if key=='vivi' else b['nodes'][:-1]==a['nodes']
   if key=='vivi':
    for old,new in zip(a['animations'],b['animations']):
     if old['name']!='Run':assert old==new,old['name']
    assert len(b['animations'])==7
   else:assert [c['name'] for c in b['animations']]==['Idle','Walk','Run']
   for ac in b['accessors'][len(a['accessors']):]:
    n=ac['count']*{'SCALAR':1,'VEC3':3,'VEC4':4}[ac['type']];v=b['bufferViews'][ac['bufferView']];assert all(math.isfinite(x) for x in struct.unpack_from('<'+'f'*n,bb,v['byteOffset']))
  for row in json.loads((F/'files.json').read_text())['files']:assert h(F/row['file'])==row['sha256'],row['file']
  report.append({'id':meta['asset_id'],'version':ver,'sha256':h(F/'model.glb'),'source_binary_prefix_bytes':len(ab),'native_source_geometry_weights_materials_textures':'unchanged'})
 for e in catalog['entries']:
  for p,sha in [(e['model']['url'],e['model']['sha256']),(e['profile'],e['profile_sha256']),(e['editable']['path'],e['editable']['sha256'])]:assert h(R/p.removeprefix('../'))==sha,p
  assert not e['art_approved'] and not e['game_ready']
 E=R/'evidence-v07'
 for row in json.loads((E/'browser-contacts.json').read_text())['entries']:
  expected=next(e['model']['sha256'] for e in catalog['entries'] if e['asset_id']=='vroid-'+row['key']+'-motion-review' and e['variant']=='corrected');assert json.loads((E/(row['key']+'-'+row['clip']+'-contacts.json')).read_text())['model_sha256'][1]==expected
  s=row['summary'][1];assert s['minimum_sole_y_m']>=0 and s['maximum_stance_reference_xz_drift_m']<.005 and s['maximum_browser_vs_build_baked_m']<.00002
  if row['clip']=='Run':assert s['stance_knee_degrees']['mean']<row['summary'][0]['stance_knee_degrees']['mean']-10 and s['stance_knee_degrees']['min']>15 and s['maximum_absolute_torso_lean_degrees']<9
 for row in json.loads((E/'browser-crossings.json').read_text())['entries']:
  expected=next(e['model']['sha256'] for e in catalog['entries'] if e['asset_id']=='vroid-'+row['key']+'-motion-review' and e['variant']=='corrected');assert row['model_sha256'][1]==expected
  b=row['variants'][1];assert b['maximum_skirt_leg_pairs']==0 and max(b['maximum_hand_skin_self_pairs'].values())==0
 for row in json.loads((E/'browser-loops.json').read_text())['entries']:assert row['variants'][1]['maximum_world_vertex_jump_m']<.00003
 assert not json.loads((E/'browser-controls.json').read_text())['errors'];print(json.dumps({'status':'SOURCE_CLIP_PRESERVATION_AND_RECORDED_CHECKS_PASS_NOT_ART_APPROVAL','entries':report},indent=2))
if __name__=='__main__':verify()
