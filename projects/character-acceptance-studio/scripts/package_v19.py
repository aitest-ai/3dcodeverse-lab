"""Immutable runtime and editable sources, every file indexed by SHA-256."""
import json,hashlib,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'deliveries-v19';D.mkdir(exist_ok=True);prefix='Character_Studio_0.19.0'
def files(folder):return [p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='.gitignore']
def make(kind,paths):
 dst=D/(prefix+'_'+kind+'.zip')
 if dst.exists():raise RuntimeError('Immutable ZIP exists '+str(dst))
 rows=[]
 with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(set(paths)):
   raw=p.read_bytes();rel=str(p.relative_to(R));z.writestr(prefix+'/'+rel,raw);rows.append(hashlib.sha256(raw).hexdigest()+'  '+rel)
  index=kind.upper()+'_FILES_V19.sha256';z.writestr(prefix+'/'+index,'\n'.join(rows)+'\n')
 with zipfile.ZipFile(dst) as z:assert z.testzip() is None
 return {'file':dst.name,'bytes':dst.stat().st_size,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'indexed_files':len(rows),'index':index}
runtime=[];sources=[]
for f in ['library-v19','inputs-v19/library-v18','experiments-v19']:
 for p in files(f):(sources if p.suffix=='.blend' else runtime).append(p)
for f in ['web-v19','web/vendor','web-v04/vendor','evidence-v19','scripts/v05','scripts/v06','scripts/v17','scripts/v18','scripts/v19']:runtime.extend(files(f))
runtime.extend(p for p in (R/'scripts').glob('*v19*') if p.is_file());runtime.extend([R/'START_STUDIO_V19.py',R/'START_WINDOWS_V19.cmd',R/'README_V19.md',R/'AGENTS.md']);runtime.extend((R/'docs').glob('*V19*'));runtime.extend(R.glob('THIRD_PARTY*.md'))
for key in ['vivi','vita']:
 sources.extend(p for p in files('library-v04/vroid-'+key+'/1.0.0') if p.suffix in ['.blend','.glb'] or 'textures' in p.parts);sources.append(R/'sources-v04/vroid'/(key.title()+'.vrm'));sources.append(R/'sources-v04/license-evidence'/('vroid2.html' if key=='vivi' else 'vroid3.html'))
receipt={'version':'0.19.0','deliveries':[make('Runtime',runtime),make('Sources',sources)],'usage':'Extract both into the same Character_Studio_0.19.0 folder. Runtime alone supports browser review. Both support offline reconstruction.','asset_versions_changed':False,'experiments_status':'REJECTED, diagnostics only','art_approved':False,'game_ready':False};(D/'receipt-v19.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
