"""Source immutability, full native provenance, and actual browser acceptance gates."""
import hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v06.motion_overlay import MotionOverlay
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
lock=json.loads((R/'config-v13/horses.lock.json').read_text());catalog=json.loads((R/'library-v13/catalog.json').read_text());reports=[]
for e in catalog['entries']:
    F=R/e['model']['url'].removeprefix('../');m=json.loads((F.parent/'adaptation.json').read_text());a=MotionOverlay(R/m['source_glb']);b=MotionOverlay(F)
    assert sha(F)==e['model']['sha256']==m['model_sha256']==next(x for x in lock['assets']+lock['comparison_assets'] if x['asset_id']==m['asset_id'])['model_sha256']
    assert sha(R/m['source_glb'])==m['source_glb_sha256'] and sha(R/m['source_mother'])==m['source_mother_sha256']
    assert sha(F.parent/'model.blend')==m['mother_sha256']==e['editable']['sha256']
    profile_path=R/e['profile'].removeprefix('../');profile=json.loads(profile_path.read_text());assert sha(profile_path)==e['profile_sha256'] and profile['editable_master_sha256']==m['mother_sha256'] and profile['model_sha256']==m['model_sha256']
    for key in a.doc:
        if key not in ['accessors','bufferViews','buffers','animations']:assert a.doc[key]==b.doc[key],key
    assert b.doc['accessors'][:len(a.doc['accessors'])]==a.doc['accessors'] and b.doc['bufferViews'][:len(a.doc['bufferViews'])]==a.doc['bufferViews']
    assert b.binary[:len(a.binary)]==a.binary
    assert b.doc['animations'][:14]==a.doc['animations'] and len(a.doc['animations'])==14 and len(b.doc['animations'])==18
    if m['variant']=='corrected':
        audit=json.loads((F.parent/'motion-audit.json').read_text());feet=[f for c in audit.values() for row in c for f in row['feet'].values()]
        assert max(f['link_length_error_native'] for f in feet)<1e-5 and min(f['reach_margin_m'] for f in feet)>.002
        assert min(f['bend_dot'] for f in feet)>0
    reports.append({'asset_id':m['asset_id'],'model_sha256':m['model_sha256'],'source_glb_sha256':m['source_glb_sha256'],'all_14_source_animations_nodes_rest_geometry_weights_textures_binary_prefix':'exactly preserved','native_bones':50,'added_clips':m['added_clips'],'variant':m['variant']})
browser=json.loads((R/'evidence-v13/transition-diagnostics.json').read_text())['entries'];assert len(browser)==2
for row in browser:
    a,b=row['summary'];assert a['maximum_stance_patch_drift_m']>.05 and b['maximum_stance_patch_drift_m']<.001 and b['minimum_sole_y_m']>=0
    assert b['endpoint_support']==[4,4] and b['minimum_support']>=2
    assert all(s['max_surface_gap_m'][1]<.00005 for s in row['seams']) and all(s['maximum_m']<.00003 for s in row['cold_body'])
(R/'evidence-v13/verification.json').write_text(json.dumps({'status':'passed source preservation and recorded kinematic/contact checks','entries':reports,'physical_balance':'not-tested','same_body_two_colors':True,'art_approved':False,'game_ready':False},indent=2)+'\n');print('V13_PRESERVATION_AND_TRANSITION_PASS')
