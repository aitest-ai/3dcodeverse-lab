"""Pinned sources, byte-preserved old clips, per-character root plans, and recorded browser checks. Not art approval."""
import json,hashlib,sys,math,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v05.overlay import read
from v06.motion_overlay import MotionOverlay
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 F=R/'library-v08/vroid-vita-motion-review/0.2.0';m=json.loads((F/'adaptation.json').read_text());a,ab=read(R/m['base_model']);b,bb=read(F/'model.glb');assert h(R/m['base_model'])==m['base_model_sha256'];assert h(R/m['base_mother'])==m['base_mother_sha256'];assert h(F/'model.glb')==m['model_sha256'];assert h(F/'model.blend')==m['mother_sha256'];assert bb[:len(ab)]==ab
 for key in ['nodes','meshes','skins','materials','images','textures','samplers','extensions','extensionsUsed','extensionsRequired']:assert a.get(key)==b.get(key),key
 for key in ['accessors','bufferViews']:assert a[key]==b[key][:len(a[key])],key
 assert a['animations']==b['animations'][:3];assert [c['name'] for c in b['animations']]==['Idle','Walk','Run','Start','Stop','TurnLeft','TurnRight']
 for ac in b['accessors'][len(a['accessors']):]:
  n=ac['count']*{'SCALAR':1,'VEC3':3,'VEC4':4}[ac['type']];v=b['bufferViews'][ac['bufferView']];assert all(math.isfinite(x) for x in struct.unpack_from('<'+'f'*n,bb,v['byteOffset']))
 for row in json.loads((F/'files.json').read_text())['files']:assert h(F/row['file'])==row['sha256'],row['file']
 cat=json.loads((R/'library-v08/catalog.json').read_text());assert 'root_clips' not in cat
 for e in cat['entries']:
  for p,sha in [(e['model']['url'],e['model']['sha256']),(e['profile'],e['profile_sha256']),(e['editable']['path'],e['editable']['sha256'])]:assert h(R/p.removeprefix('../'))==sha,p
  assert not e['art_approved'] and not e['game_ready'];o=MotionOverlay(R/e['model']['url'].removeprefix('../'));node=next(i for i,n in enumerate(o.doc['nodes']) if n.get('name')=='StudioRootMotion_v05')
  for c in o.doc['animations']:
   tr=next(c['samplers'][x['sampler']] for x in c['channels'] if x['target']=={'node':node,'path':'translation'});p=o.values(tr['output']);d=max(o.doc['accessors'][s['input']]['max'][0] for s in c['samplers']);plan=e['root_clips'][c['name']];assert plan['duration']==d
   for i,key in [(0,'start'),(-1,'end')]:assert plan[key]['x']==p[i][0] and plan[key]['z']==p[i][2]
 E=R/'evidence-v08';contacts=json.loads((E/'browser-contacts.json').read_text())['entries'];assert len(contacts)==4
 for row in contacts:
  assert row['model_sha256']==m['model_sha256'];s=row['summary'];assert s['minimum_sole_y_m']>=0 and s['maximum_stance_reference_xz_drift_m']<.005 and s['maximum_browser_vs_build_baked_m']<.00002
 cross=json.loads((E/'browser-crossings.json').read_text())['entries'];assert len(cross)==4
 for row in cross:
  assert row['model_sha256']==m['model_sha256'];v=row['variants'][0];assert v['maximum_skirt_leg_pairs']==0 and max(v['maximum_hand_skin_self_pairs'].values())==0
 joins=json.loads((E/'browser-sequence-joins.json').read_text())['entries'];assert len(joins)==22
 for row in joins:assert row['maximum_world_surface_jump_m']<.00003
 for row in json.loads((E/'browser-blender-parity.json').read_text())['entries']:assert row['maximum_browser_vs_cold_blender_m']<.00002
 assert not json.loads((E/'browser-controls.json').read_text())['errors'];print(json.dumps({'status':'SOURCE_CLIP_ROOT_PLANS_AND_RECORDED_CHECKS_PASS_NOT_ART_APPROVAL','asset_id':m['asset_id'],'version':m['version'],'sha256':m['model_sha256'],'old_binary_bytes_preserved':len(ab),'unchanged_clips':['Idle','Walk','Run']},indent=2))
if __name__=='__main__':verify()
