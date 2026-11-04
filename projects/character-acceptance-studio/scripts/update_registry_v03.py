"""Publish a selected v0.3 candidate into a new version, or view work builds without freezing."""
import argparse,hashlib,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--build-root',type=Path,default=R/'work/v03-build');p.add_argument('--publish',action='store_true');a=p.parse_args();old=json.loads((R/'assets/registry-v02.json').read_text());entries=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for c in old['characters']:
    folder=a.build_root/c['id']/'0.3.0'
    if not (folder/'asset_manifest.json').exists():continue
    if a.publish:
        dest=R/'assets'/c['id']/'0.3.0'
        if dest.exists():
            if sha(dest/(c['id']+'.glb'))!=sha(folder/(c['id']+'.glb')):raise SystemExit('Frozen 0.3 differs; choose another version')
        else:shutil.copytree(folder,dest,ignore=shutil.ignore_patterns('*.blend1','*.blend2'))
        folder=dest
    n=json.loads(json.dumps(c));n['version']='0.3.0';n['source']={**c['candidate'],'label':'v0.2 支撐腳候選（修改前）'};n['candidate']={**c['candidate'],'url':'../'+str((folder/(c['id']+'.glb')).relative_to(R)),'bytes':(folder/(c['id']+'.glb')).stat().st_size,'sha256':sha(folder/(c['id']+'.glb')),'label':'v0.3 服裝／姿態修正候選','version':'0.3.0'};n['profile']='../'+str((folder/'skeleton-profile.json').relative_to(R));n['profile_sha256']=sha(folder/'skeleton-profile.json');n['candidate'].update(profile=n['profile'],profile_sha256=n['profile_sha256']);n['provenance']={'base_pr':145,'base_commit':'30d0165b7d387442befc02aca5b4207e305bf69d','base_asset_sha256':c['candidate']['sha256'],'source':c['provenance'],'revision':'Local editable garment fit and measured spine/head pitch correction; same native root/leg motion'};n['warnings']=['候選，未人工美術核准','A為0.2修改前，B為0.3；同動作同鏡位','本輪未做物理布料模擬或全身連續碰撞認證','姿態與服裝仍需逐格實際畫面驗收'];entries.append(n)
(R/'assets/registry-v03.json').write_text(json.dumps({'schema_version':1,'version':'0.3.0','characters':entries,'art_approved':False,'game_ready':False},ensure_ascii=False,indent=2)+'\n');print('v0.3 registry',[(c['id'],c['candidate']['sha256']) for c in entries])
