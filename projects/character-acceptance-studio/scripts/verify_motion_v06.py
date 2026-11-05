"""Immutable source/animation-scope/registry/evidence checks. Never grants visual approval."""
import hashlib,json,sys,struct,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from v05.overlay import read
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 C=json.loads((R/'library-v06/catalog.json').read_text());B=R/'library-v05/vroid-vivi-motion-review/0.1.0/model.glb';F=R/'library-v06/vroid-vivi-motion-review/0.2.0';a,ab=read(B);b,bb=read(F/'model.glb');meta=json.loads((F/'adaptation.json').read_text());assert h(B)==meta['base_model_sha256'];assert bb[:len(ab)]==ab
 for key in a:
  if key not in ['animations','buffers','bufferViews','accessors']:assert a[key]==b[key],key
 for key in ['bufferViews','accessors']:assert b[key][:len(a[key])]==a[key],key
 assert len(a['animations'])==len(b['animations'])==7
 changed=[]
 for ac,bc in zip(a['animations'],b['animations']):
  assert ac['name']==bc['name'] and ac['channels']==bc['channels'];assert len(ac['samplers'])==len(bc['samplers'])
  for channel in ac['channels']:
   before=ac['samplers'][channel['sampler']];after=bc['samplers'][channel['sampler']];assert {k:v for k,v in before.items() if k!='output'}=={k:v for k,v in after.items() if k!='output'}
   if before['output']!=after['output']:
    bone=a['nodes'][channel['target']['node']]['name'];assert ac['name'].startswith('Turn') or any(p in bone for p in ['_Index','_Middle','_Ring','_Little','_Thumb']) or bone in ['J_Sec_L_SkirtFront0','J_Sec_R_SkirtFront0'];changed.append((ac['name'],bone,channel['target']['path']))
 assert len(changed)==len(meta['changed_channels'])
 for e in C['entries']:
  for path,sha in [(e['model']['url'],e['model']['sha256']),(e['profile'],e['profile_sha256']),(e['editable']['path'],e['editable']['sha256'])]:assert h(R/path.removeprefix('../'))==sha,path
  assert e['asset_id']=='vroid-vivi-motion-review' and not e['art_approved'] and not e['game_ready'];assert e['version'] in ['0.1.0','0.2.0']
 for row in json.loads((F/'files.json').read_text())['files']:assert h(F/row['file'])==row['sha256'],row['file']
 for accessor in b['accessors'][len(a['accessors']):]:
  view=b['bufferViews'][accessor['bufferView']];n=accessor['count']*{'VEC3':3,'VEC4':4}[accessor['type']];assert all(math.isfinite(v) for v in struct.unpack_from('<'+'f'*n,bb,view['byteOffset']))
 E=R/'evidence-v06'
 for row in json.loads((E/'browser-contacts.json').read_text())['entries']:
  s=row['summary'][1];assert s['minimum_sole_y_m']>=0 and s['maximum_browser_vs_blender_baked_m']<.00002
 for row in json.loads((E/'browser-crossings.json').read_text())['entries']:
  s=row['variants'][1];assert s['maximum_skirt_leg_pairs']==0 and max(s['maximum_hand_skin_self_pairs'].values())==0
 for row in json.loads((E/'browser-sequences.json').read_text())['entries']:
  assert row['repeated_same_seek_60_times_maximum_change_m']<1e-8
  for seam in row['seams']:assert seam['variants'][1]['maximum_world_vertex_jump_m']<.00002
 for row in json.loads((E/'browser-loops.json').read_text())['entries']:assert row['variants'][1]['maximum_world_vertex_jump_m']<.00002
 assert not json.loads((E/'browser-controls.json').read_text())['errors']
 print(json.dumps({'status':'SOURCE_BYTES_SCOPE_LOCKS_AND_RECORDED_BROWSER_CHECKS_PASS_NOT_ART_APPROVAL','model_sha256':h(F/'model.glb'),'changed_channels':len(changed),'preserved_base_binary_bytes':len(ab)},indent=2))
if __name__=='__main__':verify()
