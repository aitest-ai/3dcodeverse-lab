"""Source preservation, native solver bounds, locked distribution and actual-browser evidence."""
import hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v06.motion_overlay import MotionOverlay
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
lock=json.loads((R/'config-v15/horses.lock.json').read_text());catalog=json.loads((R/'library-v15/catalog.json').read_text());reports=[]
for e in catalog['entries']:
 F=R/e['model']['url'].removeprefix('../');m=json.loads((F.parent/'adaptation.json').read_text())
 assert sha(F)==e['model']['sha256']==m['model_sha256']==next(x for x in lock['assets']+lock['comparison_assets'] if x['asset_id']==m['asset_id'])['model_sha256']
 assert sha(F.parent/'model.blend')==m['mother_sha256']==e['editable']['sha256']
 profile=R/e['profile'].removeprefix('../');p=json.loads(profile.read_text());assert sha(profile)==e['profile_sha256'] and p['editable_master_sha256']==m['mother_sha256'] and p['model_sha256']==m['model_sha256']
 if e['variant']=='baseline':continue
 assert sha(R/m['source_glb'])==m['source_glb_sha256'] and sha(R/m['source_mother'])==m['source_mother_sha256']
 a=MotionOverlay(R/m['source_glb']);b=MotionOverlay(F)
 for key in a.doc:
  if key not in ['accessors','bufferViews','buffers','animations']:assert a.doc[key]==b.doc[key],key
 assert b.doc['accessors'][:len(a.doc['accessors'])]==a.doc['accessors'] and b.doc['bufferViews'][:len(a.doc['bufferViews'])]==a.doc['bufferViews'] and b.binary[:len(a.binary)]==a.binary
 assert len(a.doc['animations'])==18 and len(b.doc['animations'])==21 and b.doc['animations'][:18]==a.doc['animations']
 audit=json.loads((F.parent/'motion-audit.json').read_text());feet=[f for c in audit.values() for row in c for f in row['feet'].values()]
 # 15-degree turning needs slightly more reach than straight walking. No extension past link length allowed.
 assert max(f['link_length_error_native'] for f in feet)<1e-5 and min(f['reach_margin_m'] for f in feet)>.0015 and min(f['bend_dot'] for f in feet)>0
 reports.append({'asset_id':m['asset_id'],'model_sha256':m['model_sha256'],'source_glb_sha256':m['source_glb_sha256'],'preservation':'all 18 old clips and original scene/BIN prefix exact','added_clips':m['added_clips'],'minimum_reach_margin_m':min(f['reach_margin_m'] for f in feet),'max_link_length_error_native':max(f['link_length_error_native'] for f in feet)})
browser=json.loads((R/'evidence-v15/browser-diagnostics.json').read_text());assert len(browser['entries'])==2 and not browser['errors']
for r in browser['entries']:
 for m in r['motions']:
  assert m['stats']['max_patch_drift_m']<.001 and m['stats']['minimum_sole_m']>=0 and m['stats']['minimum_support']>=2
 assert r['cold'] and all(c['maximum_m']<.00003 for c in r['cold'])
(R/'evidence-v15/verification.json').write_text(json.dumps({'status':'passed preservation and sampled kinematic/contact checks','entries':reports,'physical_balance':'not-tested','same_body_two_colors':True,'art_approved':False,'game_ready':False},indent=2)+'\n');print('V15_PRESERVATION_AND_CONTACT_PASS')
