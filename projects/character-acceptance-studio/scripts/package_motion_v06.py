"""Two immutable archives with independently verifiable per-file SHA-256 indexes."""
import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'deliveries';prefix='Character_Studio_0.6.0'
h=lambda b:hashlib.sha256(b).hexdigest()
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
 runtime=[];sources=[]
 for folder in ['library-v06','library-v05/vroid-vivi-motion-review/0.1.0']:
  runtime.extend(p for p in files(folder) if p.suffix!='.blend');sources.extend(p for p in files(folder) if p.suffix=='.blend')
 for folder in ['web-v06','web/vendor','web-v04/vendor','evidence-v06','scripts/v05','scripts/v06']:runtime.extend(files(folder))
 runtime.extend(p for p in (R/'scripts').glob('*v06*') if p.is_file())
 runtime.append(R/'library-v04/vroid-vivi/1.0.0/model.glb')
 sources.extend(p for p in files('library-v04/vroid-vivi/1.0.0') if p.suffix=='.blend' or 'textures' in p.parts)
 for name in ['sources-v04/vroid/Vivi.vrm','sources-v04/license-evidence/vroid2.html','assets/harbor-courier-review/0.3.0/harbor-courier-review.blend','assets/harbor-courier-review/0.3.0/asset_manifest.json']:sources.append(R/name)
 sources.extend(files('sources/harbor-v02/assets/licenses'));sources.extend(files('assets/harbor-courier-review/0.3.0/textures'))
 for name in ['START_STUDIO_V06.py','START_WINDOWS_V06.cmd','README_V06.md','THIRD_PARTY_V06.md','THIRD_PARTY_V05.md','THIRD_PARTY_V04.md','THIRD_PARTY_NOTICES.md','docs/CHECKPOINT_V06.md','AGENTS.md']:runtime.append(R/name)
 receipts=[make('Character_Studio_0.6.0_Runtime.zip',runtime,'RUNTIME_FILES_V06.sha256'),make('Character_Studio_0.6.0_Sources.zip',sources,'SOURCES_FILES_V06.sha256')];(D/'receipt-v06.json').write_text(json.dumps({'version':'0.6.0','deliveries':receipts,'usage':'Extract both into the same Character_Studio_0.6.0 folder. Runtime plays independently; Sources adds each version mother, original VRM/texture files and original motion reference.'},indent=2)+'\n');print(json.dumps(receipts,indent=2))
