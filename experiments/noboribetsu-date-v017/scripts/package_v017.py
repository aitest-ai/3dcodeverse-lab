#!/usr/bin/env python3
"""Deterministic V017 Runtime/SourceQA packages, no modification of V016 ZIP."""
import json,zipfile,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;O=P/'outputs';DEST=P.parent

def pack(name,mapping):
 out=DEST/name
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for arc,path in sorted(mapping.items()):
   b=Path(path).read_bytes();info=zipfile.ZipInfo(arc,date_time=(2026,11,2,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,b,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
 with zipfile.ZipFile(out) as z: assert z.testzip() is None
 return {'name':name,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'files':len(mapping)}
runtime={p.relative_to(P/'base').as_posix():p for p in (P/'base').rglob('*') if p.is_file()}
source_files={}
for file in ['build_v017_clearance.py','integrate_v017.py','qa_v017_webgl.py','validate_v017.py','create_v017_review.py','package_v017.py','README_V017.md','Noboribetsu_Date_V017_R1_Delivery_Report.md']:
 source_files['source/'+file]=P/file
for p in O.glob('*'):
 if p.suffix in ('.json','.png','.glb','.html'):
  source_files['evidence/'+p.name]=p
out=[pack('Noboribetsu_Date_V017_R1_Runtime.zip',runtime),pack('Noboribetsu_Date_V017_R1_SourceQA.zip',source_files)]
for file in ['Noboribetsu_Date_V017_R1_Review.html','V017_Clearance_Diagnostic_Rings.glb']:
 dst=DEST/file;dst.write_bytes((O/file).read_bytes());out.append({'name':file,'bytes':dst.stat().st_size,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
manifest={'schema':'noboribetsu-date-v017-delivery-sha256/1','status':'CANDIDATE_ISOLATED_WEBGL2_PASS','original_v016_sha256':hashlib.sha256((P/'V016_Runtime.zip').read_bytes()).hexdigest(),'artifacts':out,'limitations':['private HTTPS and Android not tested','doorway threshold dimensions unknown','Blender native not run']}
(DEST/'Noboribetsu_Date_V017_R1_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(DEST/'Noboribetsu_Date_V017_R1_Delivery_Report.md').write_bytes((P/'Noboribetsu_Date_V017_R1_Delivery_Report.md').read_bytes())
(DEST/'Noboribetsu_Date_V017_R1_Validation.json').write_bytes((O/'V017_integrity_qa.json').read_bytes())
print(json.dumps(manifest,ensure_ascii=False,indent=2))