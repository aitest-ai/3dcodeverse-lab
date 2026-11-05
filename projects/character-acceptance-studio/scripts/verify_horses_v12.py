"""Preserve exact source geometry/rest/clips and verify recorded geometric support checks."""
import json,hashlib,sys,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from v06.motion_overlay import MotionOverlay
h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rows=[];assets=[]
for key in ['horse-brown','horse-white']:
 F=R/'library-v12'/(key+'-walk-support-review')/'0.1.0';m=json.loads((F/'adaptation.json').read_text());profile=json.loads((F/'skeleton-profile.json').read_text());a=MotionOverlay(R/m['source_glb']);d=MotionOverlay(F/'model.glb');assert h(R/m['source_glb'])==m['source_glb_sha256'] and h(R/m['source_mother'])==m['source_mother_sha256'];assert h(F/'model.glb')==m['model_sha256'];assert profile['model_sha256']==m['model_sha256'] and profile['editable_master_sha256']==m['mother_sha256'];assert d.binary[:len(a.binary)]==a.binary
 for field in ['nodes','scenes','scene','meshes','skins','materials','textures','images','samplers','extensions','extensionsUsed','extensionsRequired']:assert a.doc.get(field)==d.doc.get(field),field
 for field in ['accessors','bufferViews']:assert d.doc[field][:len(a.doc[field])]==a.doc[field],field
 assert len(d.doc['animations'])==14 and len(d.doc['skins'][0]['joints'])==50
 for old,new in zip(a.doc['animations'],d.doc['animations']):
  assert old['name']==new['name']
  if old['name']!='WalkWorld':assert old==new
 root=next(i for i,n in enumerate(d.doc['nodes']) if n.get('name')=='StudioTravelRoot_v11')
 for channel in d.doc['animations'][-1]['channels']:
  sampler=d.doc['animations'][-1]['samplers'][channel['sampler']];ts=d.values(sampler['input']);vs=d.values(sampler['output']);assert ts[0][0]==0 and all(t[0]<u[0] for t,u in zip(ts,ts[1:]));assert all(math.isfinite(v) for row in vs for v in row)
  if channel['target']['node']==root:
   original=next(c for c in a.doc['animations'][-1]['channels'] if c['target']==channel['target']);old_sampler=a.doc['animations'][-1]['samplers'][original['sampler']];assert vs==a.values(old_sampler['output']),'Root trajectory changed'
  else:assert min(max(abs(x-y) for x,y in zip(vs[0],vs[-1])),max(abs(x+y) for x,y in zip(vs[0],vs[-1])) if channel['target']['path']=='rotation' else 999)<1e-6
 assert h(F/'model.blend')==m['mother_sha256'];audit=json.loads((F/'motion-audit.json').read_text());assert min(f['minimum_sole_y_m'] for s in audit for f in s['feet'].values())>=0;assert max(f['link_length_error_native'] for s in audit for f in s['feet'].values())<1e-5;assert min(f['reach_margin_m'] for s in audit for f in s['feet'].values())>.002
 assets.append({'asset_id':m['asset_id'],'version':'0.1.0','source_id':key,'model_sha256':m['model_sha256']});rows.append({'asset_id':m['asset_id'],'source_glb_sha256':m['source_glb_sha256'],'model_sha256':m['model_sha256'],'thirteen_other_clips_binary_prefix_nodes_rest_geometry_textures':'exactly preserved','root_trajectory':'exact same float32 samples','native_bones':50,'changed_clip':'WalkWorld'})
lock=R/'config-v12/horses.lock.json'
if lock.exists():assert json.loads(lock.read_text())['assets']==assets,'Pinned model changed'
else:lock.write_text(json.dumps({'version':'0.12.0','assets':assets},indent=2)+'\n')
E=R/'evidence-v12';browser=json.loads((E/'world-diagnostics.json').read_text())['entries'];assert len(browser)==2
for row in browser:
 a,b=row['summary'];assert a['minimum_support']==1 and b['minimum_support']==2;assert b['minimum_sole_y_m']>=0 and b['maximum_stance_patch_drift_m']<.001 and b['loop_seam_m']<.0001 and row['cold_body_max_m']<.00003 and b['planned_sole_height_max_error_m']<.0003
report={'status':'passed preservation and recorded geometric-support checks','entries':rows,'same_body_two_colors':True,'physical_balance':'not-tested; unweighted trunk projection is not COM','art_approved':False,'game_ready':False};(E/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print('V12_PRESERVATION_AND_SUPPORT_PASS')
