"""Two immutable, independently hashed delivery ZIPs. Both extract into the same folder."""
import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'deliveries';D.mkdir(exist_ok=True);prefix='Character_Studio_0.5.0'
h=lambda b:hashlib.sha256(b).hexdigest()
def files(folder):return [p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
def make(name,paths,index):
 target=D/name
 if target.exists():raise RuntimeError('Immutable archive exists: '+str(target))
 rows=[]
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(set(paths)):
   raw=p.read_bytes();relative=str(p.relative_to(R));z.writestr(prefix+'/'+relative,raw);rows.append(h(raw)+'  '+relative)
  z.writestr(prefix+'/'+index,'\n'.join(rows)+'\n')
 with zipfile.ZipFile(target) as z:assert z.testzip() is None
 return {'file':name,'bytes':target.stat().st_size,'sha256':h(target.read_bytes()),'indexed_files':len(rows),'index':index}
if __name__=='__main__':
 runtime=[p for p in files('library-v05') if p.suffix!='.blend'];sources=[p for p in files('library-v05') if p.suffix=='.blend'];inputs=[]
 for id in ['vroid-vivi','quaternius-shibainu']:
  runtime.extend(R/'library-v04'/id/'1.0.0'/n for n in ['model.glb','skeleton-profile.json'])
  sources.extend(p for p in files('library-v04/'+id+'/1.0.0') if p.suffix=='.blend' or 'textures' in p.parts)
 runtime.append(R/'library-v04/catalog.json')
 for rel in ['sources-v04/vroid/Vivi.vrm','sources-v04/animals/ShibaInu.blend','sources-v04/animals/ShibaInu.gltf','sources-v04/animals/License.txt','sources-v04/license-evidence/vroid2.html','sources-v04/license-evidence/animals.html','assets/harbor-courier-review/0.3.0/harbor-courier-review.blend','assets/harbor-courier-review/0.3.0/asset_manifest.json']:
  sources.append(R/rel)
 sources.extend(files('sources/harbor-v02/assets/licenses'))
 sources.extend(files('assets/harbor-courier-review/0.3.0/textures'))
 for folder in ['web-v05','web/vendor','web-v04/vendor','evidence-v05','scripts/v05']:runtime.extend(files(folder))
 runtime.extend(p for p in (R/'scripts').glob('*v05*') if p.is_file());runtime.append(R/'scripts/gait_plan_v02.py')
 for name in ['START_STUDIO_V05.py','START_WINDOWS_V05.cmd','README_V05.md','THIRD_PARTY_V05.md','THIRD_PARTY_V04.md','THIRD_PARTY_NOTICES.md','docs/CHECKPOINT_V05.md','AGENTS.md']:runtime.append(R/name)
 receipts=[make('Character_Studio_0.5.0_Runtime.zip',runtime,'RUNTIME_FILES_V05.sha256'),make('Character_Studio_0.5.0_Sources.zip',sources,'SOURCES_FILES_V05.sha256')];(D/'receipt-v05.json').write_text(json.dumps({'version':'0.5.0','deliveries':receipts,'usage':'Extract both ZIPs into the same Character_Studio_0.5.0 folder. Runtime alone plays; Sources supplies editable mothers, original inputs and original-resolution texture files.'},indent=2)+'\n');print(json.dumps(receipts,indent=2))
