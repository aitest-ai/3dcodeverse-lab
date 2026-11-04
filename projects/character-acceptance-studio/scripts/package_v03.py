"""Versioned full-quality v0.3 runtime/source + visual evidence ZIPs. No old archive overwrite."""
import argparse,hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,default=R/'deliveries');a=p.parse_args()
assert (R/'OPEN_STUDIO_V03.html').exists(),'Build standalone first'
assert len(list((R/'evidence-v03/frames').rglob('*.png')))==384
assert len(list((R/'evidence-v03/details').rglob('*.png')))==64
assert len(list((R/'videos-v03').glob('*.mp4')))==12
rootfiles={'AGENTS.md','README_V03.md','START_STUDIO_V03.py','START_WINDOWS_V03.cmd','THIRD_PARTY_NOTICES.md','THIRD_PARTY_V03.md','OPEN_STUDIO_V03.html'}
docs={'INVENTORY.md','GARMENT_STAGE_V03.md','CHECKPOINT_V03.md'};runtime=[];evidence=[]
for f in sorted(R.rglob('*')):
    if not f.is_file():continue
    rel=f.relative_to(R);parts=rel.parts
    if any(x in parts for x in ['work','deliveries','__pycache__','node_modules']) or f.suffix in ['.blend1','.blend2']:continue
    if parts[0] in ['evidence-v03','videos-v03']:
        evidence.append(f)
        if f.suffix not in ['.png','.jpg','.mp4','.webm']:runtime.append(f)
    elif str(rel) in rootfiles or parts[0] in ['sources','web-v03']:runtime.append(f)
    elif parts[0]=='web' and (parts[1]=='vendor' or parts[1]=='style.css'):runtime.append(f)
    elif parts[0]=='assets' and (parts[-1] in ['registry-v03.json','provenance-lock.json'] or '0.2.0' in parts or '0.3.0' in parts):runtime.append(f)
    elif parts[0]=='scripts' and ('v03' in parts[-1] or parts[-1]=='bootstrap_blender.py' or parts[1]=='vendor'):runtime.append(f)
    elif parts[0]=='docs' and parts[-1] in docs:runtime.append(f)
prefix='Character_Studio_0.3.0/';sha=lambda b:hashlib.sha256(b).hexdigest();receipts=[]
for label in ['Runtime_Source','Evidence']:
    if (a.output_dir/f'Character_Studio_0.3.0_{label}.zip').exists():raise SystemExit('Refusing to overwrite frozen delivery')
for label,files,index in [('Runtime_Source',runtime,'RUNTIME_FILES_V03.sha256'),('Evidence',evidence,'EVIDENCE_FILES_V03.sha256')]:
    rows=[(sha(f.read_bytes()),str(f.relative_to(R))) for f in files];listing='\n'.join(h+'  '+name for h,name in rows)+'\n';a.output_dir.mkdir(parents=True,exist_ok=True);dest=a.output_dir/f'Character_Studio_0.3.0_{label}.zip'
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for f in files:z.write(f,prefix+str(f.relative_to(R)))
        z.writestr(prefix+index,listing)
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        for h,name in rows:assert sha(z.read(prefix+name))==h,name
        assert len(z.namelist())==len(rows)+1
    receipt={'file':dest.name,'bytes':dest.stat().st_size,'sha256':sha(dest.read_bytes()),'index':index,'verified_data_entries':len(rows),'zip_crc':'PASS','art_approved':False,'game_ready':False};receipts.append(receipt);print(json.dumps(receipt),flush=True)
(a.output_dir/'receipt-v03.json').write_text(json.dumps({'version':'0.3.0','shared_root':prefix,'runtime_scope':'v0.2 baseline and v0.3 editable assets, original source subset, exact viewer and build dependencies; original older archives preserved separately','archives':receipts},ensure_ascii=False,indent=2)+'\n')
