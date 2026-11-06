"""Copy a review candidate only by exact asset ID + version + SHA-256; never update an existing map."""
import argparse,json,hashlib,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--id',required=True);p.add_argument('--version',required=True);p.add_argument('--sha256',required=True);p.add_argument('--dest',required=True);p.add_argument('--review-candidate',action='store_true');p.add_argument('--include-mother',action='store_true');a=p.parse_args();dst=Path(a.dest).resolve()
if not a.review_candidate:raise SystemExit('Human art/gameplay approval pending. Pass --review-candidate for review use.')
if dst.exists():raise SystemExit('Refuse overwriting existing destination')
entries=json.loads((R/'library-v13/catalog.json').read_text())['entries'];e=next((x for x in entries if x['asset_id']==a.id and x['version']==a.version and x['variant']=='corrected'),None)
if not e or e['model']['sha256']!=a.sha256:raise SystemExit('Unknown ID/version/hash combination')
source=R/e['model']['url'].removeprefix('../');h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if h(source)!=a.sha256:raise SystemExit('Model SHA mismatch')
profile=R/e['profile'].removeprefix('../')
if h(profile)!=e['profile_sha256']:raise SystemExit('Profile SHA mismatch')
mother=R/e['editable']['path']
if a.include_mother and (not mother.exists() or h(mother)!=e['editable']['sha256']):raise SystemExit('Mother missing/mismatch; extract Sources alongside Runtime')
notices=[R/n for n in ['THIRD_PARTY_V13.md','THIRD_PARTY_V04.md','THIRD_PARTY_NOTICES.md']]
if not all(p.is_file() for p in notices):raise SystemExit('Required license notices missing')
dst.mkdir(parents=True);shutil.copyfile(source,dst/'model.glb');shutil.copyfile(profile,dst/'skeleton-profile.json');shutil.copyfile(source.parent/'adaptation.json',dst/'adaptation.json')
for name in ['THIRD_PARTY_V13.md','THIRD_PARTY_V04.md','THIRD_PARTY_NOTICES.md']:shutil.copyfile(R/name,dst/name)
if a.include_mother:shutil.copyfile(mother,dst/'model.blend')
(dst/'pin.json').write_text(json.dumps({'id':a.id,'version':a.version,'sha256':a.sha256,'profile_sha256':e['profile_sha256'],'art_approved':False,'game_ready':False,'display_calibration':e['display_calibration'],'root_motion':e['root_clips'],'transition':e['transition'],'walk_plan':e['walk_plan'],'phase_ranges':e['phase_ranges']},indent=2)+'\n');print(dst)
