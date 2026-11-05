#!/usr/bin/env python3
"""Explicit, version-pinned review export. Reject all implicit production uses."""
import argparse,hashlib,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def pin(a):
 if not a.review_candidate:raise ValueError('All library v0.7 assets are candidates. Use --review-candidate only for an isolated review; no production approval.')
 c=json.loads((R/'library-v07/catalog.json').read_text());e=next((x for x in c['entries'] if x['asset_id']==a.id and x['version']==a.version),None)
 if not e:raise ValueError('Unknown exact ID/version')
 if e['model']['sha256']!=a.sha256:raise ValueError('Requested SHA-256 does not match the locked version')
 src=R/e['model']['url'].removeprefix('../');profile=R/e['profile'].removeprefix('../')
 for p,sha in [(src,a.sha256),(profile,e['profile_sha256'])]:
  if hashlib.sha256(p.read_bytes()).hexdigest()!=sha:raise ValueError('File SHA-256 mismatch: '+p.name)
 dest=Path(a.dest)
 if dest.exists():raise ValueError('Destination exists; refuse overwrite')
 dest.mkdir(parents=True);shutil.copy2(src,dest/'model.glb');shutil.copy2(profile,dest/'skeleton-profile.json');(dest/'pin.json').write_text(json.dumps({'id':e['asset_id'],'version':e['version'],'sha256':a.sha256,'profile_sha256':e['profile_sha256'],'author':e['author'],'license':e['license'],'source_url':e['source_url'],'source_version':e['upstream_version'],'editable':e['editable'],'warning':e['warning'],'art_approved':False,'game_ready':False,'purpose':'isolated candidate review'},ensure_ascii=False,indent=2)+'\n')

 for name in ['THIRD_PARTY_V07.md','THIRD_PARTY_V06.md','THIRD_PARTY_V05.md','THIRD_PARTY_V04.md','THIRD_PARTY_NOTICES.md']:shutil.copy2(R/name,dest/name)
 shutil.copy2(src.parent/'adaptation.json',dest/'adaptation.json');print(dest)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--id',required=True);p.add_argument('--version',required=True);p.add_argument('--sha256',required=True);p.add_argument('--dest',required=True);p.add_argument('--review-candidate',action='store_true');a=p.parse_args()
 try:pin(a)
 except (ValueError,OSError) as e:p.exit(2,str(e)+'\n')
