"""Immutable candidate ZIPs for Actions artifacts; new binary assets are not committed to Git."""
import json,hashlib,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'deliveries-v10';P='Character_Studio_0.10.0';h=lambda b:hashlib.sha256(b).hexdigest()
def files(folder):return [p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='.gitignore']
def make(name,paths,index):
 target=D/name
 if target.exists():raise RuntimeError('Refuse overwriting existing candidate archive')
 rows=[]
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(set(paths)):
   rel=str(p.relative_to(R));raw=p.read_bytes();z.writestr(P+'/'+rel,raw);rows.append(h(raw)+'  '+rel)
  z.writestr(P+'/'+index,'\n'.join(rows)+'\n')
 with zipfile.ZipFile(target) as z:assert z.testzip() is None
 return {'file':name,'bytes':target.stat().st_size,'sha256':h(target.read_bytes()),'index':index,'indexed_files':len(rows)}
if __name__=='__main__':
 D.mkdir(exist_ok=True);runtime=[p for p in files('library-v10') if p.suffix!='.blend']
 for key in ['horse-brown','horse-white']:runtime.extend(p for p in files('library-v04/'+key+'/2.3.0') if p.suffix!='.blend')
 for folder in ['library-v09/horse-diagnostics','web-v10','web/vendor','web-v04/vendor','evidence-v10','scripts/v05','scripts/v06','scripts/v07','scripts/v10','config-v10','motion-v10']:runtime.extend(files(folder))
 runtime.append(R/'library-v09/catalog.json');runtime.extend(p for p in (R/'scripts').glob('*v10*') if p.is_file())
 for file in ['START_STUDIO_V10.py','START_WINDOWS_V10.cmd','README_V10.md','THIRD_PARTY_V10.md','THIRD_PARTY_V04.md','THIRD_PARTY_NOTICES.md','docs/CHECKPOINT_V10.md','AGENTS.md']:runtime.append(R/file)
 sources=[p for p in files('library-v10') if p.suffix=='.blend'];sources.extend(files('sources-v04/horses'))
 for key in ['horse-brown','horse-white']:sources.append(R/'library-v04'/key/'2.3.0/model.blend')
 rows=[make(P+'_Runtime.zip',runtime,'RUNTIME_FILES_V10.sha256'),make(P+'_Sources.zip',sources,'SOURCE_FILES_V10.sha256')];(D/'receipt-v10.json').write_text(json.dumps({'version':'0.10.0','deliveries':rows,'distribution':'review-only Actions artifact; retention 90 days subject to repository policy, not official Release','source_lock':'config-v10/horses.lock.json'},indent=2)+'\n');print(json.dumps(rows,indent=2))
