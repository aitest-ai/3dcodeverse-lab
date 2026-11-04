#!/usr/bin/env python3
"""Immutable two-part delivery. Duplicate source containers and embedded textures are rehydrated losslessly."""
import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'deliveries';prefix='Character_Library_0.4.0';D.mkdir(exist_ok=True)
def h(b):return hashlib.sha256(b).hexdigest()
def make(name,files,index):
 dest=D/name
 if dest.exists():raise RuntimeError('Immutable delivery already exists: '+str(dest))
 rows=[]
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(set(files)):
   b=p.read_bytes();rel=str(p.relative_to(R));z.writestr(prefix+'/'+rel,b);rows.append(f'{h(b)}  {rel}')
  z.writestr(prefix+'/'+index,'\n'.join(rows)+'\n')
 with zipfile.ZipFile(dest) as z:assert z.testzip() is None
 info={'file':name,'bytes':dest.stat().st_size,'sha256':h(dest.read_bytes()),'indexed_files':len(rows),'index':index};print(info,flush=True);return info
if __name__=='__main__':
 entries=json.loads((R/'library-v04/catalog.json').read_text())['entries'];runtime=[];sources=[]
 for p in (R/'library-v04').rglob('*'):
  if not p.is_file() or 'textures' in p.parts or p.suffix=='.blend':continue
  runtime.append(p)
 for e in entries:
  if not e['editable']['original_blend_available']:sources.append(R/e['editable']['path'])
 for p in (R/'sources-v04').rglob('*'):
  if not p.is_file():continue
  if p.suffix in ['.glb','.vrm']:continue # exact duplicate of a pinned runtime container
  sources.append(p)
 runtime.append(R/'sources-v04/SOURCE_FILES.sha256')
 for folder in ['web-v04','web/vendor','evidence-v04']:
  runtime.extend(p for p in (R/folder).rglob('*') if p.is_file())
 runtime.extend(p for p in (R/'scripts').glob('*v04*') if p.is_file());runtime.append(R/'scripts/vendor/inspect_glb.py')
 for n in ['START_STUDIO_V04.py','START_WINDOWS_V04.cmd','README_V04.md','THIRD_PARTY_V04.md','AGENTS.md','docs/CHECKPOINT_V04.md']:runtime.append(R/n)
 receipts=[make('Character_Library_0.4.0_Runtime.zip',runtime,'RUNTIME_FILES_V04.sha256'),make('Character_Library_0.4.0_Sources.zip',sources,'SOURCES_FILES_V04.sha256')]
 (D/'receipt-v04.json').write_text(json.dumps({'version':'0.4.0','deliveries':receipts,'restore':'scripts/restore_library_v04.py reconstructs exact duplicate original containers/textures; no image reencoding. Extract both into the same directory.'},indent=2)+'\n')
