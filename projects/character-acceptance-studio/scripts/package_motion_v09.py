"""Standalone runtime and original full-quality sources. No new horse version or release is produced."""
import json,hashlib,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'deliveries';prefix='Character_Studio_0.9.0';h=lambda b:hashlib.sha256(b).hexdigest()
def files(folder):return [p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
def make(name,paths,index):
 target=D/name
 if target.exists():raise RuntimeError('Immutable archive exists: '+str(target))
 rows=[]
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(set(paths)):
   raw=p.read_bytes();rel=str(p.relative_to(R));z.writestr(prefix+'/'+rel,raw);rows.append(h(raw)+'  '+rel)
  z.writestr(prefix+'/'+index,'\n'.join(rows)+'\n')
 with zipfile.ZipFile(target) as z:assert z.testzip() is None
 return {'file':name,'bytes':target.stat().st_size,'sha256':h(target.read_bytes()),'indexed_files':len(rows),'index':index}
if __name__=='__main__':
 runtime=[p for p in files('library-v09') if p.suffix!='.blend']
 for key in ['horse-brown','horse-white']:runtime.extend(p for p in files('library-v04/'+key+'/2.3.0') if p.suffix!='.blend')
 for folder in ['web-v09','web/vendor','web-v04/vendor','evidence-v09','scripts/v05','scripts/v06','scripts/v07','scripts/v09']:runtime.extend(files(folder))
 runtime.extend(p for p in (R/'scripts').glob('*v09*') if p.is_file())
 for name in ['START_STUDIO_V09.py','START_WINDOWS_V09.cmd','README_V09.md','THIRD_PARTY_V09.md','THIRD_PARTY_V08.md','THIRD_PARTY_V07.md','THIRD_PARTY_V06.md','THIRD_PARTY_V05.md','THIRD_PARTY_V04.md','THIRD_PARTY_NOTICES.md','docs/CHECKPOINT_V09.md','AGENTS.md']:runtime.append(R/name)
 receipts=[make(prefix+'_Runtime.zip',runtime,'RUNTIME_FILES_V09.sha256')]
 sources=[p for p in files('library-v09') if p.suffix=='.blend'];sources.extend(files('library-v05/quaternius-shibainu-grounded-review/0.1.0'));sources.extend(files('library-v04/quaternius-shibainu/1.0.0'))
 for key in ['horse-brown','horse-white']:sources.append(R/'library-v04'/key/'2.3.0/model.blend')
 sources.extend(files('sources-v04/horses'));sources.extend(R/'sources-v04/animals'/n for n in ['ShibaInu.blend','ShibaInu.gltf','License.txt']);sources.extend([R/'sources-v04/license-evidence/animals.html',R/'sources-v04/license-evidence/quaternius-index.html']);receipts.append(make(prefix+'_Sources.zip',sources,'SOURCE_FILES_V09.sha256'));(D/'receipt-v09.json').write_text(json.dumps({'version':'0.9.0','deliveries':receipts,'usage':'Runtime plays Shiba, brown horse and white horse. Sources extracts into the same Character_Studio_0.9.0 folder for native editing and standalone Shiba arc rebuild. Horse release files are unchanged.'},indent=2)+'\n');print(json.dumps(receipts,indent=2))
