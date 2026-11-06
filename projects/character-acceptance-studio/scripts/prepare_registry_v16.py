"""Freeze the two independent native-rig hand candidates; never overwrite versions."""
import json,hashlib,shutil,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v06.motion_overlay import MotionOverlay
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
old=json.loads((R/'library-v08/catalog.json').read_text());entries=[]
for key,previous,version in [('vivi','0.3.0','0.4.0'),('vita','0.2.0','0.3.0')]:
 asset='vroid-'+key+'-motion-review';a=json.loads(json.dumps(next(e for e in old['entries'] if e['id']==asset+'@'+previous)));b=json.loads(json.dumps(a));folder=R/'library-v16'/asset/version
 if folder.exists():raise RuntimeError('Refuse overwrite '+str(folder))
 shutil.copytree(R/'work/v16-build'/asset/version,folder);meta=json.loads((folder/'adaptation.json').read_text());a.update(name=key.title()+' · 前版 '+previous,variant='before',pair_baseline=a['id'],pair_corrected=asset+'@'+version,default_clip='Run',warning='本階段固定比較基準。原有跑步手指姿態；其餘六段保留。')
 b.update(id=asset+'@'+version,version=version,name=key.title()+' · 跑步手型候選',variant='corrected',pair_baseline=a['id'],pair_corrected=asset+'@'+version,default_clip='Run',modifications=meta,warning='修改 Run 的 30 根手指與 2 根上臂旋轉；兩種原生身形分別適配。身形、衣鞋版型與其餘六段保留。人工美術／完整碰撞未核准。')
 profile=json.loads((R/a['profile'].removeprefix('../')).read_text());profile.update(version=version,model_sha256=h(folder/'model.glb'),editable_master_sha256=h(folder/'model.blend'),retargeting=meta,hand_fit=json.loads((folder/'hand-fit.json').read_text()));write(folder/'skeleton-profile.json',profile)
 b.update(model={'url':'../'+str((folder/'model.glb').relative_to(R)),'bytes':(folder/'model.glb').stat().st_size,'sha256':h(folder/'model.glb')},profile='../'+str((folder/'skeleton-profile.json').relative_to(R)),profile_sha256=h(folder/'skeleton-profile.json'),editable={'kind':'native FK baked working copy; upstream .vroid unavailable','path':str((folder/'model.blend').relative_to(R)),'sha256':h(folder/'model.blend'),'note':'自己的新版母檔；Sources ZIP 保留比較基準與原 VRM。'})
 write(folder/'asset_manifest.json',{'schema_version':1,'asset_id':asset,'version':version,'model_file':'model.glb','source_file':'model.blend','sha256':b['model']['sha256'],'unit':'meter','clips':[c['name'] for c in b['clips']],'min_animation_count':7,'requirements':{'skins':True,'animated':True,'visual_review':True},'source':b['source_url'],'license_note':'CC0 upstream; project-authored motion changes; THIRD_PARTY_V16.md','art_approved':False,'game_ready':False})
 entries.extend([a,b])
write(R/'library-v16/catalog.json',{'schema_version':1,'version':'0.16.0','entries':entries,'root_motion_policy':old['root_motion_policy']})
print('V16_CANDIDATES_FROZEN')
