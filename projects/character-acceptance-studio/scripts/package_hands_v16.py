"""Self-contained runtime and native sources; original image dimensions retained."""
import json,hashlib,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'deliveries-v16';D.mkdir(exist_ok=True);prefix='Character_Studio_0.16.0'
def files(p):return [f for f in (R/p).rglob('*') if f.is_file() and '__pycache__' not in f.parts and f.name not in ['.gitignore','README.md']]
def make(kind,paths):
 dst=D/(prefix+'_'+kind+'.zip')
 if dst.exists():raise RuntimeError('Immutable archive exists '+str(dst))
 rows=[]
 with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(set(paths)):
   raw=p.read_bytes();rel=str(p.relative_to(R));z.writestr(prefix+'/'+rel,raw);rows.append(hashlib.sha256(raw).hexdigest()+'  '+rel)
  index=kind.upper()+'_FILES_V16.sha256';z.writestr(prefix+'/'+index,'\n'.join(rows)+'\n')
 with zipfile.ZipFile(dst) as z:assert z.testzip() is None
 return {'file':dst.name,'bytes':dst.stat().st_size,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'indexed_files':len(rows),'index':index}
cat=json.loads((R/'library-v16/catalog.json').read_text());runtime=[R/'library-v16/catalog.json'];sources=[]
for e in cat['entries']:
 folder=(R/e['model']['url'].removeprefix('../')).parent;runtime.extend(p for p in folder.iterdir() if p.is_file() and p.suffix not in ['.blend','.blend1']);sources.append(R/e['editable']['path'])
for folder in ['web-v16','web/vendor','web-v04/vendor','evidence-v16','scripts/v05','scripts/v06','scripts/v07','scripts/v16']:runtime.extend(files(folder))
runtime.extend(p for p in (R/'scripts').glob('*v16*') if p.is_file())
for name in ['START_STUDIO_V16.py','START_WINDOWS_V16.cmd','README_V16.md','THIRD_PARTY_V16.md','THIRD_PARTY_V08.md','THIRD_PARTY_V07.md','THIRD_PARTY_V06.md','THIRD_PARTY_V05.md','THIRD_PARTY_V04.md','THIRD_PARTY_NOTICES.md','docs/CHECKPOINT_V16.md','docs/TRIALS_V16.json','docs/UPSTREAM_V16.json','AGENTS.md']:runtime.append(R/name)
for key in ['vivi','vita']:
 sources.extend(p for p in files('library-v04/vroid-'+key+'/1.0.0') if p.suffix in ['.blend','.glb'] or 'textures' in p.parts);sources.append(R/'sources-v04/vroid'/(key.title()+'.vrm'));sources.append(R/'sources-v04/license-evidence'/('vroid2.html' if key=='vivi' else 'vroid3.html'))
receipt={'version':'0.16.0','deliveries':[make('Runtime',runtime),make('Sources',sources)],'usage':'Extract both archives into the same Character_Studio_0.16.0 directory. Runtime alone supports browser review; both support clean Blender reconstruction.','art_approved':False,'game_ready':False};(D/'receipt-v16.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
