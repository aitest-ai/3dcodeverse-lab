"""Prove bounded changes and pins. Browser/art evidence are separate categories."""
import json,hashlib,sys,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.overlay import read
from v06.motion_overlay import MotionOverlay
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[];cat=json.loads((R/'library-v16/catalog.json').read_text())
for e in cat['entries']:
 for p,sha in [(e['model']['url'],e['model']['sha256']),(e['profile'],e['profile_sha256']),(e['editable']['path'],e['editable']['sha256'])]:assert h(R/p.removeprefix('../'))==sha,p
 assert not e['art_approved'] and not e['game_ready']
 if e['variant']!='corrected':continue
 F=(R/e['model']['url'].removeprefix('../')).parent;m=json.loads((F/'adaptation.json').read_text());assert h(R/m['base_model'])==m['base_model_sha256'];assert h(R/m['base_mother'])==m['base_mother_sha256'];a,ab=read(R/m['base_model']);b,bb=read(F/'model.glb');assert bb[:len(ab)]==ab
 for k in ['nodes','meshes','skins','materials','images','textures','samplers','extensions','extensionsUsed','extensionsRequired','scenes','scene']:assert a.get(k)==b.get(k),k
 for k in ['accessors','bufferViews']:assert a[k]==b[k][:len(a[k])],k
 assert len(a['animations'])==len(b['animations'])==7;changed=[]
 ao=MotionOverlay(R/m['base_model']);bo=MotionOverlay(F/'model.glb')
 for ac,bc in zip(a['animations'],b['animations']):
  assert ac['name']==bc['name'] and ac['channels']==bc['channels']
  if ac['name']!='Run':assert ac==bc;continue
  for c in ac['channels']:
   sa=ac['samplers'][c['sampler']];sb=bc['samplers'][c['sampler']]
   if sa!=sb:
    n=b['nodes'][c['target']['node']]['name'];assert c['target']['path']=='rotation' and (n in ['J_Bip_L_UpperArm','J_Bip_R_UpperArm'] or any(n=='J_Bip_'+s+'_'+d+str(i) for s in ['L','R'] for d in ['Index','Middle','Ring','Little','Thumb'] for i in range(1,4)));assert sa['input']==sb['input'] and sa['interpolation']==sb['interpolation'];values=bo.values(sb['output']);assert all(math.isfinite(x) for row in values for x in row);assert all(abs(sum(x*x for x in q)-1)<1e-5 for q in values);changed.append(n)
 assert len(changed)==32
 rows.append({'id':e['id'],'sha256':h(F/'model.glb'),'unchanged_clips':m['preserved_clips'],'only_changed_tracks':'30 Run finger + 2 upper-arm rotations','old_binary_bytes_preserved':len(ab)})
E=R/'evidence-v16';E.mkdir(exist_ok=True);(E/'source-preservation.json').write_text(json.dumps({'entries':rows},indent=2)+'\n');print('V16_SOURCE_PRESERVATION_PASS')
