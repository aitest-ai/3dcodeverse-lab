"""Freeze the two independent native-rig arm candidates; never overwrite versions."""
import json,hashlib,shutil,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v06.motion_overlay import MotionOverlay
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
old=json.loads((R/'inputs-v17/library-v16/catalog.json').read_text());entries=[]
for key,previous,version in [('vivi','0.4.0','0.5.0'),('vita','0.3.0','0.4.0')]:
 asset='vroid-'+key+'-motion-review';a=json.loads(json.dumps(next(e for e in old['entries'] if e['id']==asset+'@'+previous)));a['model']['url']=a['model']['url'].replace('../library-v16/','../inputs-v17/library-v16/');a['profile']=a['profile'].replace('../library-v16/','../inputs-v17/library-v16/');a['editable']['path']='inputs-v17/'+a['editable']['path'];b=json.loads(json.dumps(a));folder=R/'library-v17'/asset/version
 if folder.exists():raise RuntimeError('Refuse overwrite '+str(folder))
 shutil.copytree(R/'work/v17-build'/asset/version,folder);meta=json.loads((folder/'adaptation.json').read_text());a.update(name=key.title()+' · 前版 '+previous,variant='before',pair_baseline=a['id'],pair_corrected=asset+'@'+version,default_clip='Run',warning='本階段固定比較基準。V16 手型與上臂避裙版本；肘角約固定 62.5°；其餘六段保留。')
 b.update(id=asset+'@'+version,version=version,name=key.title()+' · 跑步肘角候選',variant='corrected',pair_baseline=a['id'],pair_corrected=asset+'@'+version,default_clip='Run',modifications=meta,warning='Run 的 2 根前臂旋轉＋肘窩皮膚與衣料修正；兩種原生身形分別適配。保留手型、上臂避裙、腿、根位移及六段其餘動作。人工美術／完整碰撞未核准。')
 doc=MotionOverlay(folder/'model.glb').doc;b['clips']=[{'name':c['name'],'duration_s':max(doc['accessors'][x['input']]['max'][0] for x in c['samplers']),'channels':len(c['channels']),'status':'candidate; not art-approved'} for c in doc['animations']];profile=json.loads((R/a['profile'].removeprefix('../')).read_text());profile.update(version=version,clips=b['clips'],model_sha256=h(folder/'model.glb'),editable_master_sha256=h(folder/'model.blend'),retargeting=meta,arm_fit=json.loads((folder/'arm-fit.json').read_text()),pose_corrective=json.loads((folder/'pose-corrective.json').read_text()));write(folder/'skeleton-profile.json',profile)
 b.update(model={'url':'../'+str((folder/'model.glb').relative_to(R)),'bytes':(folder/'model.glb').stat().st_size,'sha256':h(folder/'model.glb')},profile='../'+str((folder/'skeleton-profile.json').relative_to(R)),profile_sha256=h(folder/'skeleton-profile.json'),editable={'kind':'native FK baked working copy; upstream .vroid unavailable','path':str((folder/'model.blend').relative_to(R)),'sha256':h(folder/'model.blend'),'note':'自己的新版母檔；Sources ZIP 保留比較基準與原 VRM。'})
 write(folder/'asset_manifest.json',{'schema_version':1,'asset_id':asset,'version':version,'model_file':'model.glb','source_file':'model.blend','sha256':b['model']['sha256'],'unit':'meter','clips':[c['name'] for c in b['clips']],'min_animation_count':7,'requirements':{'skins':True,'animated':True,'visual_review':True},'source':b['source_url'],'license_note':'CC0 upstream; project-authored motion changes; THIRD_PARTY_V17.md','art_approved':False,'game_ready':False})
 entries.extend([a,b])
write(R/'library-v17/catalog.json',{'schema_version':1,'version':'0.17.0','entries':entries,'root_motion_policy':old['root_motion_policy']})
print('V17_CANDIDATES_FROZEN')
