"""Install one exact candidate for isolated review; fail closed on identity/hash/overwrite.
This studio has no art-approved production assets. This tool never updates a map automatically.
"""
import argparse,json,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pull(asset_id,version,wanted,dest,allow_candidate=False):
    registry=json.loads((ROOT/'assets/registry-v02.json').read_text())
    found=[c for c in registry['characters'] if c['id']==asset_id and c['version']==version]
    if len(found)!=1:raise ValueError('Exact character ID + version not found; no latest fallback')
    c=found[0]
    if not allow_candidate:raise ValueError('art_approved=false / game_ready=false. Only isolated review is allowed with --candidate-review')
    if wanted!=c['candidate']['sha256']:raise ValueError('Pinned SHA-256 does not match registry')
    dest=Path(dest)
    if dest.exists():raise ValueError('Destination already exists; refusing to overwrite')
    model=(ROOT/'web'/c['candidate']['url']).resolve();profile=(ROOT/'web'/c['profile']).resolve()
    if sha(model)!=wanted or model.stat().st_size!=c['candidate']['bytes']:raise ValueError('Model bytes/hash mismatch')
    if sha(profile)!=c['profile_sha256']:raise ValueError('Skeleton profile hash mismatch')
    dest.mkdir(parents=True)
    shutil.copyfile(model,dest/model.name);shutil.copyfile(profile,dest/'skeleton-profile.json')
    lock={'schema_version':1,'asset_id':asset_id,'version':version,'sha256':wanted,'model_file':model.name,'profile_sha256':c['profile_sha256'],'source':c['provenance'],'license':c['license'],'purpose':'isolated_review_only','art_approved':False,'game_ready':False,'automatic_update':False,'motion_kind':c['candidate']['motion_kind'],'root_motion_note':'Native root translation/yaw; extract deltas or use embedded motion, avoid double translation. Map integration untested.'}
    (dest/'asset-lock.json').write_text(json.dumps(lock,ensure_ascii=False,indent=2)+'\n')
    return lock
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--id',required=True);p.add_argument('--version',required=True);p.add_argument('--sha256',required=True);p.add_argument('--dest',required=True);p.add_argument('--candidate-review',action='store_true');a=p.parse_args()
    try:print(json.dumps(pull(a.id,a.version,a.sha256,a.dest,a.candidate_review),ensure_ascii=False,indent=2))
    except ValueError as e:p.exit(2,str(e)+'\n')
