#!/usr/bin/env python3
"""Integrate frozen V008 runtime with new V009 exterior model. Never write into V008.

Expected: new empty output root, input contains dist folder and new verified model QA.
No change to model A/B, geometry other than new external GLB, collision, route or WebGL dependencies.
"""
import argparse,hashlib,json,shutil
from pathlib import Path
BASE_VERSION='V008-structure-candidate-r1'
VERSION='V009-utsuroi-candidate-r1'

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()

def exactly(source,old,new,label):
 if source.count(old)!=1:raise RuntimeError(f'{label}: expected 1 occurrence, got {source.count(old)}')
 return source.replace(old,new)

def integrate(base:Path,work:Path):
 if (work/'runtime').exists():raise FileExistsError('v009 runtime already exists')
 qa=json.loads((work/'outputs/v009_model_qa.json').read_text())
 source_model=work/'outputs/v009_utsuroi_facade.glb'
 assert sha(source_model)==qa['glb_v009_sha256']
 original=base/'dist';src=original/'assets/v008_waraji_architecture.glb'
 assert sha(src)==qa['base_v008_sha256']
 dest=work/'runtime';shutil.copytree(base,dest)
 dist=dest/'dist';assets=dist/'assets';new=assets/source_model.name
 assert not new.exists();shutil.copy2(source_model,new)
 viewpath=dist/'scene_view.json';v=json.loads(viewpath.read_text())
 assert v['version']==BASE_VERSION and abs(v['route'][-1]['s']-231.56641497226084)<.000001
 descriptor={'path':'assets/'+new.name,'bytes':new.stat().st_size,'sha256':sha(new)}
 v['version']=VERSION
 v['extension_v009']={'manifest':'v009_facade_manifest.json','model':descriptor,'source_v008_sha256':qa['base_v008_sha256'],
                     'status':'unsurveyed sidewall-grid correction; official use verified, exterior not verified',
                     'skip_archived_models':['V005_FACADES','V007_FACADES','V008_FACADES']}
 viewpath.write_text(json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n')
 manifest={'schema':'noboribetsu-v009-utsuroi-sidewall/1','version':VERSION,'base_version':BASE_VERSION,'model':descriptor,
           'source_v008_sha256':qa['base_v008_sha256'],
           'geometry':{'original_triangles':qa['original_triangles'],'removed_triangles':qa['removed_triangles'],
                       'removed_side_grid_boxes':qa['removed_side_grid_boxes'],
                       'added_triangles':sum(n['triangles'] for n in qa['new_geometry'].values()),
                       'total_triangles':qa['total_triangles']},
           'preservation':{'other_20_original_meshes_unchanged':True,'A_stage_unchanged':True,
                           'collision_unchanged':True,'route_unchanged':True,'waraji_v008_unchanged':True},
           'provenance':{'source':'V008 candidate GLB + author-estimated sidewall correction',
                         'official_use_url':'https://edo-trip.jp/facility/utsuroi-kan/',
                         'exterior':'NOT independently verified; no current front/side elevations',
                         'no_official_photos_bundled':True},
           'acceptance':{'GLB':'exported reimported and geometry checked','WebGL2':'not tested',
                         'Android':'not tested','Blender_native':'not tested','private_site':'unchanged'}}
 (dist/'v009_facade_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 js=dist/'app.js';s=js.read_text()
 s=exactly(s,'v006Road=null,v007Facades=null,v008Facades=null;',
             'v006Road=null,v007Facades=null,v008Facades=null,v009Facades=null;','var')
 s=exactly(s,"version:'V008-structure-candidate-r1',boot_ms",f"version:'{VERSION}',boot_ms",'metrics')
 suffix="'V007-facade-candidate-r1','V008-structure-candidate-r1'].includes(manifest.version)"
 if s.count(suffix)!=3:raise RuntimeError('Expected three extension version lists; got '+str(s.count(suffix)))
 s=s.replace(suffix,"'V007-facade-candidate-r1','V008-structure-candidate-r1','V009-utsuroi-candidate-r1'].includes(manifest.version)")
 s=exactly(s,"if(stage==='V005_FACADES'&&manifest.version==='V008-structure-candidate-r1'){",
             "if(stage==='V005_FACADES'&&['V008-structure-candidate-r1','V009-utsuroi-candidate-r1'].includes(manifest.version)){",'V005 hidden skip')
 intro="""// V009 uses a new verified GLB. V008/V007/V005 remain archived and are not downloaded on boot.
async function loadV009UtsuroiCandidate(){
  const c=manifest.extension_v009;
  if(!c||manifest.version!=='V009-utsuroi-candidate-r1')throw new Error('V009 模型版本不符');
  const contract=await getJSON(c.manifest);
  if(contract.schema!=='noboribetsu-v009-utsuroi-sidewall/1'||contract.base_version!=='V008-structure-candidate-r1'||
     contract.version!==manifest.version||contract.source_v008_sha256!==c.source_v008_sha256||
     contract.model?.path!==c.model?.path||contract.model?.bytes!==c.model?.bytes||
     contract.model?.sha256!==c.model?.sha256||
     contract.preservation?.collision_unchanged!==true||contract.preservation?.route_unchanged!==true||
     contract.preservation?.A_stage_unchanged!==true||contract.preservation?.waraji_v008_unchanged!==true||
     contract.geometry?.removed_side_grid_boxes!==20||contract.geometry?.total_triangles!==17104)
    throw new Error('V009 來源、模型或路線契約不一致，已停止載入');
  loadText.textContent='正在驗證 V009 變裝攝影館側牆模型…';
  v009Facades=await loadStageModel({...c.model,stage:'V009_FACADES'});
  v009Facades.name='V009_FACADES';v009Facades.visible=false;
  metrics.v009_facade={model_sha256:c.model.sha256,source_v008_sha256:c.source_v008_sha256,
    triangles:contract.geometry.total_triangles,route_unchanged:true,collision_unchanged:true,
    geometry_status:'author-estimated side-wall correction; not an as-built reconstruction',
    archived_facade_models_skipped:['V005_FACADES','V007_FACADES','V008_FACADES']};
  refreshDiagnostics();
}
"""
 s=exactly(s,'function place(atEnd=false){',intro+'function place(atEnd=false){','loader insert')
 s=exactly(s,'    await loadV008StructureCandidate();','    await loadV009UtsuroiCandidate();','boot')
 s=exactly(s,"if(v007Facades)v007Facades.visible=false;if(v008Facades)v008Facades.visible=value==='B';if(v005Signs)v005Signs.visible=value==='B';",
             "if(v007Facades)v007Facades.visible=false;if(v008Facades)v008Facades.visible=false;if(v009Facades)v009Facades.visible=value==='B';if(v005Signs)v005Signs.visible=value==='B';",'stage')
 s=exactly(s,"'第一人稱 · '+stage+' 場景 · V008 草鞋屋簷下與窗格精修'",
             "'第一人稱 · '+stage+' 場景 · V009 變裝攝影館側牆精修'",'label')
 s=exactly(s,"version:'V008-structure-candidate-r1'});",f"version:'{VERSION}'}});",'dataset')
 s=exactly(s,"Noboribetsu_Date_V008_browser_diagnostics.json","Noboribetsu_Date_V009_browser_diagnostics.json",'export name')
 s=exactly(s,'完整 B 場景與 V008 建築細節已驗證；舊外觀保留但未重複下載，A 按需下載',
             '完整 B 場景與 V009 側牆已驗證；舊外觀仍保存但不重複下載，A 按需下載','status')
 js.write_text(s)
 page=dist/'index.html';h=page.read_text();
 # Replace all end-user version badges but keep historical filenames elsewhere.
 h=h.replace('V008 草鞋屋建築精修候選','V009 變裝攝影館側牆精修候選')
 h=h.replace('V008 候選｜231.6 m','V009 候選｜231.6 m')
 h=h.replace('review_v008.html','review_v009.html')
 h=h.replace('查看 V007／V008 同鏡位診斷比較','查看 V008／V009 同鏡位診斷比較')
 h=h.replace('V008 只對草鞋屋加入建築推估細節，保留 V007 與路線碰撞。參考的 2018 官方舊照不等於 2026 現況；WebGL2、Android、Blender、私人站仍未驗收。',
             'V009 修正變裝攝影館過密木條，為作者估計外觀，未有建築實測或完整立面照片；路線不變。WebGL2、Android、Blender 與私人網站仍未驗收。')
 page.write_text(h)
 (dist/'qa.json').write_text(json.dumps({'version':VERSION,'status':'GLB_exported_and_geometry_tests_passed_not_gpu_verified',
    'scope':'Utsuroi-kan sidewall, no route/collision or A change','length_m':231.56641497226084,
    'webgl2':'unavailable in current Chromium; NOT VERIFIED','android':'NOT TESTED',
    'blender_native':'NOT EXECUTED','private_site':'UNMODIFIED','third_person':False},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'status':'V009_INTEGRATED','version':VERSION,'model':descriptor,'original_v008_sha256':sha(src)},ensure_ascii=False))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('v008_runtime_root',type=Path);ap.add_argument('v009_work',type=Path);a=ap.parse_args();integrate(a.v008_runtime_root,a.v009_work)