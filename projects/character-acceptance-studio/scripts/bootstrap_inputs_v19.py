"""Acquire immutable V18 inputs. Offline bundles already contain these files.

Use --artifact with the saved V18 outer ZIP. Fresh CI may download the pinned
same-repository artifact through its existing GitHub token; no new credential.
"""
import argparse,json,hashlib,zipfile,io,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];ROOT=R/'inputs-v19';OUTER_SHA='f6ba7b0d8405e20f0e8d5871d26057f324e64793aab1d82ea29b9aa739b661ee';PREFIX='Character_Studio_0.18.0/'
LOCK={'vroid-vivi-motion-review/0.6.0': {'model.glb': '9f7388ffde3a23a4ace8ae28012058fcdfc4b6aadac286c95555848ac545939b', 'model.blend': '539c532f574da3df9a70d9065e585ad2c3d89850772b07040acef73c2203bb94', 'skeleton-profile.json': 'cdb807ee9eea9133dac8a6648a06b56cb9c7fbf60813363ad411a77f115751d9'}, 'vroid-vita-motion-review/0.5.0': {'model.glb': '23ff3955af6e7e022ac79ec1cf1ecd5c1ba04c7d4e523da7b84750b8e9195874', 'model.blend': '5ebc0650ae90eb929fab81deaaa9223f13fd47ef7127a81a03b4ff431fa8db98', 'skeleton-profile.json': '6b4580cad64c347ed72f7bc24e13525b989e70dd117aa1fa1880c0d0ce66790d'}}
def verify():
 for folder,files in LOCK.items():
  for name,sha in files.items():assert hashlib.sha256((ROOT/'library-v18'/folder/name).read_bytes()).hexdigest()==sha,(folder,name)
 cat=json.loads((ROOT/'library-v18/catalog.json').read_text())
 for e in cat['entries']:
  if e['variant']=='corrected':
   folder=e['asset_id']+'/'+e['version'];assert e['model']['sha256']==LOCK[folder]['model.glb'] and e['editable']['sha256']==LOCK[folder]['model.blend']
 print('V19_PINNED_INPUTS_PASS')
def main():
 p=argparse.ArgumentParser();p.add_argument('--artifact',type=Path);a=p.parse_args()
 if (ROOT/'library-v18/catalog.json').exists() and (R/'sources-v04/vroid/Vita.vrm').exists():verify();return
 archive=a.artifact or R/'work/v19/v18-source-artifact.zip'
 if not archive.exists():
  archive.parent.mkdir(parents=True,exist_ok=True)
  with archive.open('wb') as f:subprocess.run(['gh','api','repos/aitest-ai/3dcodeverse-lab/actions/artifacts/13899702463/zip'],stdout=f,check=True)
 assert hashlib.sha256(archive.read_bytes()).hexdigest()==OUTER_SHA,'Pinned V18 artifact mismatch'
 with zipfile.ZipFile(archive) as outer:
  receipt=json.loads(outer.read('receipt-v18.json'))
  for row in receipt['deliveries']:
   raw=outer.read(row['file']);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
   with zipfile.ZipFile(io.BytesIO(raw)) as z:
    for line in z.read(PREFIX+row['index']).decode().splitlines():
     sha,name=line.split('  ',1)
     if not name.startswith(('library-v18/','library-v04/','sources-v04/')):continue
     assert not Path(name).is_absolute() and '..' not in Path(name).parts;data=z.read(PREFIX+name);assert hashlib.sha256(data).hexdigest()==sha;target=(ROOT if name.startswith('library-v18/') else R)/name;target.parent.mkdir(parents=True,exist_ok=True)
     if target.exists():assert target.read_bytes()==data,'Refuse conflicting input overwrite'
     else:target.write_bytes(data)
 verify()
if __name__=='__main__':main()
