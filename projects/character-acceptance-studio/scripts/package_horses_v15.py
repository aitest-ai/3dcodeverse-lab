"""Standalone v15 runtime and complete native sources; no newly generated binaries in Git."""
import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'deliveries-v15';P='Character_Studio_0.15.0';sha=lambda b:hashlib.sha256(b).hexdigest()
def files(folder):return [p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='.gitignore']
def make(name,paths,index):
 target=D/name
 if target.exists():raise RuntimeError('Refuse overwriting archive')
 rows=[]
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(set(paths)):
   rel=str(p.relative_to(R));raw=p.read_bytes();z.writestr(P+'/'+rel,raw);rows.append(sha(raw)+'  '+rel)
  z.writestr(P+'/'+index,'\n'.join(rows)+'\n')
 with zipfile.ZipFile(target) as z:assert z.testzip() is None
 return {'file':name,'bytes':target.stat().st_size,'sha256':sha(target.read_bytes()),'index':index,'indexed_files':len(rows)}
if __name__=='__main__':
 D.mkdir(exist_ok=True);runtime=[];sources=[]
 for folder in ['library-v15','library-v14/horse-brown-walk-smooth-review/0.1.0','library-v14/horse-white-walk-smooth-review/0.1.0']:
  for p in files(folder):(sources if p.suffix=='.blend' else runtime).append(p)
 runtime.append(R/'library-v14/catalog.json')
 for key in ['horse-brown','horse-white']:runtime.extend(p for p in files('library-v04/'+key+'/2.3.0') if p.suffix!='.blend')
 for folder in ['library-v09/horse-diagnostics','web-v15','web/vendor','web-v04/vendor','evidence-v15','scripts/v05','scripts/v06','scripts/v07','scripts/v10','scripts/v13','scripts/v14','scripts/v15','config-v12','config-v14','config-v15','motion-v15']:runtime.extend(files(folder))
 runtime.append(R/'library-v09/catalog.json');runtime.extend(p for p in (R/'scripts').glob('*v15*') if p.is_file())
 for file in ['START_STUDIO_V15.py','START_WINDOWS_V15.cmd','README_V15.md','THIRD_PARTY_V15.md','THIRD_PARTY_V14.md','THIRD_PARTY_V13.md','THIRD_PARTY_V12.md','THIRD_PARTY_V11.md','THIRD_PARTY_V10.md','THIRD_PARTY_V04.md','THIRD_PARTY_NOTICES.md','docs/CHECKPOINT_V15.md','AGENTS.md']:runtime.append(R/file)
 sources.extend(files('sources-v04/horses'))
 rows=[make(P+'_Runtime.zip',runtime,'RUNTIME_FILES_V15.sha256'),make(P+'_Sources.zip',sources,'SOURCE_FILES_V15.sha256')]
 (D/'receipt-v15.json').write_text(json.dumps({'version':'0.15.0','deliveries':rows,'distribution':'review-only Actions artifact; retention 90 days subject to repo policy; no official Release','source_lock':'config-v15/horses.lock.json','rebuild_scope':'Standalone v15 from complete direct v14 inputs; full historical pipeline requires repository.'},indent=2)+'\n');print(json.dumps(rows,indent=2))
