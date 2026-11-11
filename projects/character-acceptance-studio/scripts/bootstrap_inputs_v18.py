"""Acquire immutable V17 inputs. Offline bundles already contain these files.

Use --artifact with the saved V17 outer ZIP. Fresh CI may download the pinned
same-repository artifact through its existing GitHub token; no new credential.
"""
import argparse,json,hashlib,zipfile,io,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];ROOT=R/'inputs-v18';OUTER_SHA='5890011f79b2120f6d57727bd92c1e063a75ebaf56298f01383547ea899219ec';PREFIX='Character_Studio_0.17.0/'
LOCK={'vroid-vivi-motion-review/0.5.0': {'model.glb': '889020f363d0693094bc11b36b1e1302b2bfbecd88ae0698e0fd14797ac79bdc', 'model.blend': '869897cd663d986b14baf3915ba49b5209fadcb18d92565d542915197bbe1db2', 'skeleton-profile.json': '9caa012f7825c670e8e83c615762afdc8697d6748e3348c2bb9fe2caa85182c8'}, 'vroid-vita-motion-review/0.4.0': {'model.glb': '5ab09cbc3ebdd48fa21b31bf12c3944672fcfb0b592b19b2ce3ab610f2db1568', 'model.blend': '0b77eab63cb41e32cb681d7dd9909b61dc1b2d6d227ba3f088d6ee7ad17f7f25', 'skeleton-profile.json': 'c64e2fe171e39806f724f0c50bd25d18d6a7fe65ed38186894f46b996a63495b'}}
def verify():
 for folder,files in LOCK.items():
  for name,sha in files.items():assert hashlib.sha256((ROOT/'library-v17'/folder/name).read_bytes()).hexdigest()==sha,(folder,name)
 cat=json.loads((ROOT/'library-v17/catalog.json').read_text())
 for e in cat['entries']:
  if e['variant']=='corrected':
   folder=e['asset_id']+'/'+e['version'];assert e['model']['sha256']==LOCK[folder]['model.glb'] and e['editable']['sha256']==LOCK[folder]['model.blend']
 print('V18_PINNED_INPUTS_PASS')
def main():
 p=argparse.ArgumentParser();p.add_argument('--artifact',type=Path);a=p.parse_args()
 if (ROOT/'library-v17/catalog.json').exists() and (R/'sources-v04/vroid/Vita.vrm').exists():verify();return
 archive=a.artifact or R/'work/v18/v17-source-artifact.zip'
 if not archive.exists():
  archive.parent.mkdir(parents=True,exist_ok=True)
  with archive.open('wb') as f:subprocess.run(['gh','api','repos/aitest-ai/3dcodeverse-lab/actions/artifacts/13488354383/zip'],stdout=f,check=True)
 assert hashlib.sha256(archive.read_bytes()).hexdigest()==OUTER_SHA,'Pinned V17 artifact mismatch'
 with zipfile.ZipFile(archive) as outer:
  receipt=json.loads(outer.read('receipt-v17.json'))
  for row in receipt['deliveries']:
   raw=outer.read(row['file']);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
   with zipfile.ZipFile(io.BytesIO(raw)) as z:
    for line in z.read(PREFIX+row['index']).decode().splitlines():
     sha,name=line.split('  ',1)
     if not name.startswith(('library-v17/','library-v04/','sources-v04/')):continue
     assert not Path(name).is_absolute() and '..' not in Path(name).parts;data=z.read(PREFIX+name);assert hashlib.sha256(data).hexdigest()==sha;target=(ROOT if name.startswith('library-v17/') else R)/name;target.parent.mkdir(parents=True,exist_ok=True)
     if target.exists():assert target.read_bytes()==data,'Refuse conflicting input overwrite'
     else:target.write_bytes(data)
 verify()
if __name__=='__main__':main()
