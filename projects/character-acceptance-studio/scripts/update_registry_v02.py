"""Publish selected v0.2 candidates without overwriting v0.1 or a different frozen v0.2."""
import argparse,hashlib,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--build-root',type=Path,default=R/'work/v02-build');p.add_argument('--publish',action='store_true');a=p.parse_args()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def asset(path,label):return {'url':'../'+str(path.relative_to(R)),'bytes':path.stat().st_size,'sha256':sha(path),'label':label}
old=json.loads((R/'assets/registry.json').read_text());entries=[]
for c in old['characters']:
    folder=a.build_root/c['id']/'0.2.0'
    if not (folder/'asset_manifest.json').exists():continue
    if a.publish:
        dest=R/'assets'/c['id']/'0.2.0'
        if dest.exists():
            previous=json.loads((dest/'asset_manifest.json').read_text());new=json.loads((folder/'asset_manifest.json').read_text())
            if previous['sha256']!=new['sha256']:raise SystemExit('Frozen version differs; use a new version directory')
        else:shutil.copytree(folder,dest,ignore=shutil.ignore_patterns('*.blend1','__pycache__'))
        folder=dest
    m=json.loads((folder/'asset_manifest.json').read_text());audit=json.loads((folder/'motion-audit.json').read_text());new=json.loads(json.dumps(c));new['version']='0.2.0';new['fps']=60;new['source']={**c['candidate'],'label':'v0.1 修正候選（基準）','version':'0.1.0','motion_kind':'in-place','motions':c['motions'],'profile':c['profile'],'profile_sha256':c['profile_sha256']};new['candidate']=asset(folder/m['model_file'],'v0.2 支撐腳／根位移候選');new['candidate']['version']='0.2.0';new['candidate']['motion_kind']='root-motion';motions={}
    for name,d in audit['clips'].items():
        motions[name]={'duration_s':d['duration_s'],'speed_mps':d['speed_mps'],'note':'實際根位移＋鞋底支撐點烘焙候選；尚待完整服裝與人工美術驗收。','trajectory':[{'time_s':s['time_s'],'x':s['root_m'][0],'z':-s['root_m'][1],'yaw':s['heading_rad']} for s in d['samples']]}
    new['candidate']['motions']=motions;new['motions']=motions;new['profile']='../'+str((folder/'skeleton-profile.json').relative_to(R));new['profile_sha256']=sha(folder/'skeleton-profile.json');new['candidate']['profile']=new['profile'];new['candidate']['profile_sha256']=new['profile_sha256'];new['profileSummary']=c['profileSummary']+' · 60fps接地烘焙';new['provenance']={'base_pr':142,'base_commit':'9c769f52b9d042327b92fc1ba7b64c6e476c07d6','base_asset_sha256':c['candidate']['sha256'],'source':c['provenance'],'revision':'0.2 authored world-space step/contact plans; same per-character editable mesh/skin/texture'};new['warnings']=['本版仍未人工美術核准','支撐點約束不等於完整布料碰撞或地面反作用力','A為v0.1原地片段，B為原生根位移；可切換跟隨／世界座標','串接播放不使用混合補縫，供檢查真實clip邊界'];entries.append(new)
(R/'assets/registry-v02.json').write_text(json.dumps({'schema_version':1,'version':'0.2.0','characters':entries,'art_approved':False,'game_ready':False},ensure_ascii=False,indent=2)+'\n');print('Registry v0.2',[(c['id'],c['candidate']['sha256']) for c in entries])
