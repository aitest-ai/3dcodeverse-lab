"""Complete standalone runtime + native source pair; no new binaries committed to Git."""
import json,hashlib,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'deliveries-v11';P='Character_Studio_0.11.0';h=lambda b:hashlib.sha256(b).hexdigest()
def files(folder):return [p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='.gitignore']
def make(name,paths,index):
 target=D/name
 if target.exists():raise RuntimeError('Refuse overwriting archive')
 rows=[]
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(set(paths)):
   rel=str(p.relative_to(R));raw=p.read_bytes();z.writestr(P+'/'+rel,raw);rows.append(h(raw)+'  '+rel)
  z.writestr(P+'/'+index,'\n'.join(rows)+'\n')
 with zipfile.ZipFile(target) as z:assert z.testzip() is None
 return {'file':name,'bytes':target.stat().st_size,'sha256':h(target.read_bytes()),'index':index,'indexed_files':len(rows)}
if __name__=='__main__':
 D.mkdir(exist_ok=True);runtime=[];sources=[]
 for folder in ['library-v11','inputs-v11']:
  for p in files(folder):
   if p.name.endswith('-curves.json'):continue
   (sources if p.suffix=='.blend' else runtime).append(p)
 for key in ['horse-brown','horse-white']:runtime.extend(p for p in files('library-v04/'+key+'/2.3.0') if p.suffix!='.blend')
 for folder in ['library-v09/horse-diagnostics','web-v11','web/vendor','web-v04/vendor','evidence-v11','scripts/v05','scripts/v06','scripts/v07','scripts/v10','scripts/v11','config-v11','motion-v10','motion-v11']:runtime.extend(files(folder))
 runtime.append(R/'library-v09/catalog.json');runtime.extend(p for p in (R/'scripts').glob('*v11*') if p.is_file());runtime.append(R/'scripts/build_horses_v10.py')
 for file in ['START_STUDIO_V11.py','START_WINDOWS_V11.cmd','README_V11.md','THIRD_PARTY_V11.md','THIRD_PARTY_V10.md','THIRD_PARTY_V04.md','THIRD_PARTY_NOTICES.md','docs/CHECKPOINT_V11.md','AGENTS.md']:runtime.append(R/file)
 sources.extend(files('sources-v04/horses'));rows=[make(P+'_Runtime.zip',runtime,'RUNTIME_FILES_V11.sha256'),make(P+'_Sources.zip',sources,'SOURCE_FILES_V11.sha256')];(D/'receipt-v11.json').write_text(json.dumps({'version':'0.11.0','deliveries':rows,'distribution':'review-only Actions artifact; retention 90 days subject to repo policy; no official Release','source_lock':'config-v11/horses.lock.json'},indent=2)+'\n');print(json.dumps(rows,indent=2))
