"""Runtime includes both characters; two source archives retain full-resolution source inputs per character."""
import json,hashlib,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'deliveries';prefix='Character_Studio_0.7.0';h=lambda b:hashlib.sha256(b).hexdigest()
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
 runtime=[p for p in files('library-v07') if p.suffix!='.blend']
 for folder in ['web-v07','web/vendor','web-v04/vendor','evidence-v07','scripts/v05','scripts/v06','scripts/v07']:runtime.extend(files(folder))
 runtime.extend(p for p in (R/'scripts').glob('*v07*') if p.is_file());runtime.append(R/'scripts/gait_plan_v02.py')
 for name in ['model.glb','skeleton-profile.json','adaptation.json']:runtime.append(R/'library-v06/vroid-vivi-motion-review/0.2.0'/name)
 for name in ['START_STUDIO_V07.py','START_WINDOWS_V07.cmd','README_V07.md','THIRD_PARTY_V07.md','THIRD_PARTY_V06.md','THIRD_PARTY_V05.md','THIRD_PARTY_V04.md','THIRD_PARTY_NOTICES.md','docs/CHECKPOINT_V07.md','AGENTS.md']:runtime.append(R/name)
 receipts=[make('Character_Studio_0.7.0_Runtime.zip',runtime,'RUNTIME_FILES_V07.sha256')]
 for key,ver in [('vivi','0.3.0'),('vita','0.1.0')]:
  sources=[p for p in files('library-v07/vroid-'+key+'-motion-review/'+ver) if p.suffix=='.blend'];sources.extend(p for p in files('library-v04/vroid-'+key+'/1.0.0') if p.suffix in ['.blend','.glb'] or 'textures' in p.parts);sources.append(R/'sources-v04/vroid'/('Vivi.vrm' if key=='vivi' else 'Vita.vrm'));sources.append(R/'sources-v04/license-evidence'/('vroid2.html' if key=='vivi' else 'vroid3.html'))
  if key=='vivi':sources.extend([R/'library-v06/vroid-vivi-motion-review/0.2.0/model.blend',R/'library-v05/vroid-vivi-motion-review/0.1.0/adaptation.json'])
  else:
   sources.extend([R/'assets/harbor-courier-review/0.3.0/harbor-courier-review.blend',R/'assets/harbor-courier-review/0.3.0/asset_manifest.json']);sources.extend(files('assets/harbor-courier-review/0.3.0/textures'));sources.extend(files('sources/harbor-v02/assets/licenses'))
  receipts.append(make('Character_Studio_0.7.0_'+key.title()+'_Sources.zip',sources,key.upper()+'_SOURCES_FILES_V07.sha256'))
 (D/'receipt-v07.json').write_text(json.dumps({'version':'0.7.0','deliveries':receipts,'usage':'Runtime plays both characters. Extract the character source archive(s) into the same Character_Studio_0.7.0 folder for editing/rebuilding. No prior ZIP is required.'},indent=2)+'\n');print(json.dumps(receipts,indent=2))
