"""Verify source prefix, all 13 native clips, profiles and actual world-space evidence."""
import json,hashlib,sys,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from v06.motion_overlay import MotionOverlay
h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rows=[];assets=[]
for key in ['horse-brown','horse-white']:
 for variant in ['translation-trial','world-review']:
  F=R/'library-v11'/(key+'-walk-'+variant)/'0.1.0';m=json.loads((F/'adaptation.json').read_text());profile=json.loads((F/'skeleton-profile.json').read_text());a=MotionOverlay(R/m['source_glb']);d=MotionOverlay(F/'model.glb');assert h(R/m['source_glb'])==m['source_glb_sha256'] and h(R/m['source_mother'])==m['source_mother_sha256'];assert h(F/'model.glb')==m['model_sha256'];assert profile['model_sha256']==m['model_sha256'];assert profile['editable_master_sha256']==(m['mother_sha256'] or m['source_mother_sha256']);assert d.binary[:len(a.binary)]==a.binary
  for field in ['meshes','skins','materials','textures','images','samplers','extensions','extensionsUsed','extensionsRequired']:assert a.doc.get(field)==d.doc.get(field),field
  for field in ['nodes','accessors','bufferViews','animations']:assert d.doc[field][:len(a.doc[field])]==a.doc[field],field
  assert len(d.doc['animations'])==14 and len(d.doc['skins'][0]['joints'])==50 and len(d.doc['nodes'])==len(a.doc['nodes'])+1
  root=len(a.doc['nodes']);assert d.doc['nodes'][root]=={'name':'StudioTravelRoot_v11','children':a.doc['scenes'][a.doc.get('scene',0)]['nodes']};assert d.doc['scenes'][d.doc.get('scene',0)]['nodes']==[root]
  for channel in d.doc['animations'][-1]['channels']:
   sampler=d.doc['animations'][-1]['samplers'][channel['sampler']];ts=d.values(sampler['input']);vs=d.values(sampler['output']);assert ts[0][0]==0 and all(t[0]<u[0] for t,u in zip(ts,ts[1:]));assert all(math.isfinite(v) for row in vs for v in row)
   if channel['target']['node']==root and channel['target']['path']=='translation':assert abs((vs[-1][2]-vs[0][2])*m['display_calibration']['scale']-m['plan']['candidate_stride_m'])<1e-6
   elif channel['target']['node']!=root:assert min(max(abs(x-y) for x,y in zip(vs[0],vs[-1])),max(abs(x+y) for x,y in zip(vs[0],vs[-1])) if channel['target']['path']=='rotation' else 999)<1e-6
  if variant=='world-review':
   assert h(F/'model.blend')==m['mother_sha256'];audit=json.loads((F/'motion-audit.json').read_text());assert min(f['minimum_sole_y_m'] for s in audit for f in s['feet'].values())>=0;assert max(f['link_length_error_native'] for s in audit for f in s['feet'].values())<1e-5
  assets.append({'asset_id':m['asset_id'],'version':'0.1.0','source_id':key,'model_sha256':m['model_sha256']});rows.append({'asset_id':m['asset_id'],'all_13_v10_clips_and_binary_prefix':'byte-preserved','original_meshes_skins_rest_textures':'byte-preserved','native_bones':50,'new_clip':'WalkWorld','new_travel_wrapper':True})
lock=R/'config-v11/horses.lock.json'
if lock.exists():assert json.loads(lock.read_text())['assets']==assets,'Pinned model changed'
else:lock.write_text(json.dumps({'version':'0.11.0','assets':assets},indent=2)+'\n')
E=R/'evidence-v11';browser=json.loads((E/'world-diagnostics.json').read_text())['entries'];assert len(browser)==2
for row in browser:
 b=row['summary'][1];assert b['minimum_sole_y_m']>=0 and b['maximum_stance_patch_drift_m']<.001 and b['loop_seam_m']<.0001 and row['cold_body_max_m']<.00003
report={'status':'passed structural and recorded world-space checks','entries':rows,'same_body_two_colors':'brown and white share native shape/weights; different vertex order/material partitions/mane retained. NOT a second body shape.','art_approved':False,'game_ready':False};(E/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print('V11_STRUCTURE_AND_WORLD_PASS')
