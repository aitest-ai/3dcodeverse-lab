"""Freeze exact V17 baselines and new V18 candidates, without implicit replacements."""
import json,hashlib,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
old=json.loads((R/'inputs-v18/library-v17/catalog.json').read_text());entries=[]
for key,previous,version in [('vivi','0.5.0','0.6.0'),('vita','0.4.0','0.5.0')]:
 asset='vroid-'+key+'-motion-review';a=json.loads(json.dumps(next(e for e in old['entries'] if e['id']==asset+'@'+previous)));a['model']['url']=a['model']['url'].replace('../library-v17/','../inputs-v18/library-v17/');a['profile']=a['profile'].replace('../library-v17/','../inputs-v18/library-v17/');a['editable']['path']='inputs-v18/'+a['editable']['path'];b=json.loads(json.dumps(a));folder=R/'library-v18'/asset/version
 if folder.exists():raise RuntimeError('Refuse overwrite '+str(folder))
 shutil.copytree(R/'work/v18-build'/asset/version,folder);meta=json.loads((folder/'adaptation.json').read_text());a.update(name=key.title()+' · V17 來源 '+previous,variant='before',pair_baseline=a['id'],pair_corrected=asset+'@'+version,default_clip='Run',warning='固定 V17 比較基準；肩腋描邊暗塊、幾何摺疊與袖口粗折線仍存在。')
 b.update(id=asset+'@'+version,version=version,name=key.title()+' · 肩腋描邊修正候選',variant='corrected',pair_baseline=a['id'],pair_corrected=asset+'@'+version,default_clip='Run',modifications=meta,warning='局部描邊遮罩；所有幾何與七段動作保留。袖口細分試作未通過，保留 V17 袖口。肩腋幾何摺疊及皮膚交叉仍待修，未通過人工美術驗收。')
 profile=json.loads((R/a['profile'].removeprefix('../')).read_text());profile.update(version=version,model_sha256=h(folder/'model.glb'),editable_master_sha256=h(folder/'model.blend'),surface_adaptation=meta,outline_mask=json.loads((folder/'outline-mask.json').read_text()));write(folder/'skeleton-profile.json',profile)
 b.update(model={'url':'../'+str((folder/'model.glb').relative_to(R)),'bytes':(folder/'model.glb').stat().st_size,'sha256':h(folder/'model.glb')},profile='../'+str((folder/'skeleton-profile.json').relative_to(R)),profile_sha256=h(folder/'skeleton-profile.json'),editable={'kind':'native rig and packed images; upstream .vroid unavailable','path':str((folder/'model.blend').relative_to(R)),'sha256':h(folder/'model.blend'),'note':'packed outline mask 可編輯；匯出器拒絕其他幾何／動作修改。'})
 write(folder/'asset_manifest.json',{'schema_version':1,'asset_id':asset,'version':version,'model_file':'model.glb','source_file':'model.blend','sha256':b['model']['sha256'],'unit':'meter','clips':[c['name'] for c in b['clips']],'min_animation_count':7,'requirements':{'skins':True,'animated':True,'visual_review':True},'source':b['source_url'],'license_note':'CC0 upstream; project modifications; THIRD_PARTY_V18.md','art_approved':False,'game_ready':False});entries.extend([a,b])
write(R/'library-v18/catalog.json',{'schema_version':1,'version':'0.18.0','entries':entries,'root_motion_policy':old['root_motion_policy']});print('V18_CANDIDATES_FROZEN')
