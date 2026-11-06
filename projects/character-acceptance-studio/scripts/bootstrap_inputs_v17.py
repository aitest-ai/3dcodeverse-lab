"""Acquire immutable V16 inputs. Offline bundles already contain these files.

Use --artifact with the saved V16 outer ZIP. Fresh CI may download the pinned
same-repository artifact through its existing GitHub token; no new credential.
"""
import argparse,json,hashlib,zipfile,io,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];ROOT=R/'inputs-v17';OUTER_SHA='0345d206c57efe474c251c4444dc3c27f6f2007269f30adc0345902e3bc83ad3';PREFIX='Character_Studio_0.16.0/'
LOCK={'vroid-vivi-motion-review/0.4.0':{'model.glb':'32f0b07488bf043078b262b8991225e5052da9588f8d176dc885e42e2df704d2','model.blend':'08125f86ff603e8cdcf45cfdff67182b18a4ad823ab27b2d989e779ce427e26e','skeleton-profile.json':'25c499d5bf7a90ef247924e73247e842deb13993ebc4b3807e2f99d54c067318'},'vroid-vita-motion-review/0.3.0':{'model.glb':'bb2b70d549486af00d1a155e20f03550de203d3b3424d053e6dd4b18ea17415a','model.blend':'b1b49499ca3be7b6e85c235b4398dfdb06de46e075bce6af894659a014e64fb3','skeleton-profile.json':'d90f6e169c011f544ec9bd0117558a74fa599e6974033149f43652d0db358059'}}
def verify():
 for folder,files in LOCK.items():
  for name,sha in files.items():assert hashlib.sha256((ROOT/'library-v16'/folder/name).read_bytes()).hexdigest()==sha,(folder,name)
 cat=json.loads((ROOT/'library-v16/catalog.json').read_text())
 for e in cat['entries']:
  if e['variant']=='corrected':
   folder=e['asset_id']+'/'+e['version'];assert e['model']['sha256']==LOCK[folder]['model.glb'] and e['editable']['sha256']==LOCK[folder]['model.blend']
 print('V17_PINNED_INPUTS_PASS')
def main():
 p=argparse.ArgumentParser();p.add_argument('--artifact',type=Path);a=p.parse_args()
 if (ROOT/'library-v16/catalog.json').exists():verify();return
 archive=a.artifact or R/'work/v17/v16-source-artifact.zip'
 if not archive.exists():
  archive.parent.mkdir(parents=True,exist_ok=True)
  with archive.open('wb') as f:subprocess.run(['gh','api','repos/aitest-ai/3dcodeverse-lab/actions/artifacts/13484651685/zip'],stdout=f,check=True)
 assert hashlib.sha256(archive.read_bytes()).hexdigest()==OUTER_SHA,'Pinned V16 artifact mismatch'
 with zipfile.ZipFile(archive) as outer:
  receipt=json.loads(outer.read('receipt-v16.json'))
  for row in receipt['deliveries']:
   raw=outer.read(row['file']);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
   with zipfile.ZipFile(io.BytesIO(raw)) as z:
    for line in z.read(PREFIX+row['index']).decode().splitlines():
     sha,name=line.split('  ',1)
     if not name.startswith('library-v16/'):continue
     assert not Path(name).is_absolute() and '..' not in Path(name).parts;data=z.read(PREFIX+name);assert hashlib.sha256(data).hexdigest()==sha;target=ROOT/name;target.parent.mkdir(parents=True,exist_ok=True)
     if target.exists():assert target.read_bytes()==data,'Refuse conflicting input overwrite'
     else:target.write_bytes(data)
 verify()
if __name__=='__main__':main()
