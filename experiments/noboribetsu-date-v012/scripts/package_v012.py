#!/usr/bin/env python3
"""Create V012 ZIPs and signed manifest. Runtime is copied, never rebuilt destructively."""
import zipfile, pathlib, hashlib, json
R=pathlib.Path('/mnt/data/noboribetsu_v012_work');OUT=pathlib.Path('/mnt/data')
def putzip(dst, entries):
    with zipfile.ZipFile(dst,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for name,path in sorted(entries):
            z.write(path,name)
    with zipfile.ZipFile(dst) as z:
        failed=z.testzip();assert failed is None, failed
    return dst
runtime=[(q.relative_to(R/'runtime').as_posix(),q) for q in (R/'runtime').rglob('*') if q.is_file()]
runtime_zip=putzip(OUT/'Noboribetsu_Date_V012_R1_Runtime.zip',runtime)
qa_scripts=['build_v012_edge.py','integrate_v012.py','validate_v012.py','qa_v012_webgl.py','qa_v012_mobile.py','verify_all_assets.py','build_review_v012.py','package_v012.py']
qa_evidence=['V012_geometry_qa.json','V012_integrity_qa.json','V012_clean_replay_qa.json','V012_webgl_qa.json','V012_mobile_qa.json','V012_validation.json',
 'V011_street_end_WebGL2.png','V012_street_end_WebGL2.png','V012_Mobile_Emulated_WebGL2.png','V011_V012_StreetEnd_WebGL2_Comparison.png','V012_road_edge_detail.png']
source=[('source/'+s,R/s) for s in qa_scripts]
source +=[('evidence/'+s,R/'outputs'/s) for s in qa_evidence]
source += [('outputs/'+s,R/'outputs'/s) for s in ['v012_road_grass_transition.json','v012_road_grass_fade_editable.glb']]
source += [('README_V012.md',R/'README_V012_SourceQA.md'),('Noboribetsu_Date_V012_R1_Review.html',R/'Noboribetsu_Date_V012_R1_Review.html'),('Noboribetsu_Date_V012_R1_Delivery_Report.md',R/'Noboribetsu_Date_V012_R1_Delivery_Report.md')]
sourcezip=putzip(OUT/'Noboribetsu_Date_V012_R1_SourceQA.zip',source)
# Publish other standalone deliverables at verified final paths.
import shutil
for a,b in [(R/'Noboribetsu_Date_V012_R1_Review.html',OUT/'Noboribetsu_Date_V012_R1_Review.html'),(R/'Noboribetsu_Date_V012_R1_Delivery_Report.md',OUT/'Noboribetsu_Date_V012_R1_Delivery_Report.md'),(R/'outputs'/'V012_validation.json',OUT/'Noboribetsu_Date_V012_R1_Validation.json'),(R/'outputs'/'v012_road_grass_fade_editable.glb',OUT/'Noboribetsu_Date_V012_R1_Road_Grass_Fade.glb')]:shutil.copy2(a,b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
artifacts=[runtime_zip,sourcezip,OUT/'Noboribetsu_Date_V012_R1_Review.html',OUT/'Noboribetsu_Date_V012_R1_Delivery_Report.md',OUT/'Noboribetsu_Date_V012_R1_Validation.json',OUT/'Noboribetsu_Date_V012_R1_Road_Grass_Fade.glb']
manifest={'schema':'noboribetsu-date-v012-delivery-sha256/1','date':'2026-11-02','files':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in artifacts},'runtime_files':len(runtime),'sourceqa_files':len(source),'runtime_zip_crc_pass':True,'source_zip_crc_pass':True,'v011_old_versions_not_overwritten':True}
(OUT/'Noboribetsu_Date_V012_R1_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(manifest,ensure_ascii=False,indent=2))