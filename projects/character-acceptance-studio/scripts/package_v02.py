"""Two exact versioned ZIPs: full-quality runtime/source and separately overlaid visual evidence.
Splitting preserves original textures, editable mothers and original PNG bytes. No overwrite.
"""
import argparse,hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,default=R/'deliveries');a=p.parse_args()
if not (R/'OPEN_STUDIO_V02.html').is_file():raise SystemExit('Build OPEN_STUDIO_V02.html first')
assert len(list((R/'evidence-v02/frames').rglob('*.png')))==384,'Incomplete four-view capture'
assert len(list((R/'videos-v02').glob('*.mp4')))==12,'Incomplete evidence videos'
def sha(b):return hashlib.sha256(b).hexdigest()
runtime=[];evidence=[]
for f in sorted(R.rglob('*')):
    if not f.is_file():continue
    rel=f.relative_to(R);parts=rel.parts
    if any(x in parts for x in ['work','deliveries','__pycache__','node_modules']) or f.suffix in ['.blend1','.blend2']:continue
    if parts[0] in ['evidence','videos'] or str(rel) in ['OPEN_STUDIO.html','FILES.sha256','RUNTIME_FILES_V02.sha256','EVIDENCE_FILES_V02.sha256']:continue
    if parts[0] in ['evidence-v02','videos-v02']:
        evidence.append(f)
        if f.suffix not in ['.png','.mp4','.webm','.jpg']:runtime.append(f)
    else:runtime.append(f)
prefix='Character_Studio_0.2.0/';receipts=[]
targets=[('Runtime_Source',runtime,'RUNTIME_FILES_V02.sha256'),('Evidence',evidence,'EVIDENCE_FILES_V02.sha256')]
for label,files,index in targets:
    dest=a.output_dir/f'Character_Studio_0.2.0_{label}.zip'
    if dest.exists():raise SystemExit('Refusing to overwrite delivery: '+str(dest))
for label,files,index in targets:
    rows=[(sha(f.read_bytes()),str(f.relative_to(R))) for f in files]
    listing='\n'.join(h+'  '+name for h,name in rows)+'\n';a.output_dir.mkdir(parents=True,exist_ok=True)
    dest=a.output_dir/f'Character_Studio_0.2.0_{label}.zip'
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for f in files:z.write(f,prefix+str(f.relative_to(R)))
        z.writestr(prefix+index,listing)
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        for h,name in rows:assert sha(z.read(prefix+name))==h,name
        assert len(z.namelist())==len(files)+1
    receipt={'file':dest.name,'bytes':dest.stat().st_size,'sha256':sha(dest.read_bytes()),'entries':len(files)+1,'verified_sha256_count':len(rows),'index':index,'zip_crc':'PASS','art_approved':False,'game_ready':False};receipts.append(receipt);print(json.dumps(receipt),flush=True)
(a.output_dir/'receipt-v02.json').write_text(json.dumps({'version':'0.2.0','shared_root':prefix,'runtime_includes_editable_mothers_glbs_textures_profiles_licenses_and_complete_html':True,'evidence_contains_real_framebuffer_sequences_and_sampled_videos':True,'archives':receipts},ensure_ascii=False,indent=2)+'\n')
