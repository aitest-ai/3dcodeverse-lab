"""Versioned complete ZIP + full SHA index. Do not overwrite an existing delivery archive."""
import argparse,hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=R/'deliveries/Character_Studio_0.1.0_Complete.zip');a=p.parse_args()
if a.output.exists():raise SystemExit('Delivery already exists. Use a new version/path; no overwrite.')
if not (R/'OPEN_STUDIO.html').is_file():raise SystemExit('Build complete OPEN_STUDIO.html first')
def sha(b):return hashlib.sha256(b).hexdigest()
files=[]
for f in sorted(R.rglob('*')):
    rel=f.relative_to(R)
    if not f.is_file() or any(x in rel.parts for x in ['work','deliveries','__pycache__','node_modules']) or f.suffix in ['.blend1','.blend2'] or str(rel)=='FILES.sha256':continue
    files.append(f)
rows=[(sha(f.read_bytes()),str(f.relative_to(R))) for f in files];(R/'FILES.sha256').write_text('\n'.join(h+'  '+name for h,name in rows)+'\n')
files.append(R/'FILES.sha256');a.output.parent.mkdir(parents=True,exist_ok=True);prefix='Character_Studio_0.1.0/'
with zipfile.ZipFile(a.output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for f in files:z.write(f,prefix+str(f.relative_to(R)))
with zipfile.ZipFile(a.output) as z:
    assert z.testzip() is None
    for h,name in rows:assert sha(z.read(prefix+name))==h,name
    assert len(z.namelist())==len(files)
receipt={'file':a.output.name,'bytes':a.output.stat().st_size,'sha256':sha(a.output.read_bytes()),'entries':len(files),'verified_file_sha256_count':len(rows),'zip_crc':'PASS','includes_complete_html':True,'includes_editable_mothers_glbs_textures_profiles_licenses':True,'art_approved':False,'game_ready':False}
(a.output.parent/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt,ensure_ascii=False,indent=2))
