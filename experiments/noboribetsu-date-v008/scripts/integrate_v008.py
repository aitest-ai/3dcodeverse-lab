#!/usr/bin/env python3
"""Integrate V008 standalone into a COPY of frozen V007 Runtime, with lazy skip for hidden older facade models.
No V007 archive or originals are modified. Requires output from build_v008.py.
"""
import argparse,hashlib,json,shutil,html,base64
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def once(s,a,b,tag):
 count=s.count(a)
 if count!=1: raise RuntimeError(f'{tag}: expected one anchor, got {count}')
 return s.replace(a,b)

def integrate(runtime,work):
 dist=runtime/'dist';asset=dist/'assets';outputs=work/'outputs';model=outputs/'v008_waraji_architecture.glb'
 report=json.loads((outputs/'v008_model_qa.json').read_text(encoding='utf-8'))
 if not model.exists() or sha(model)!=report['v008_glb_sha256']:raise RuntimeError('V008 GLB SHA mismatch')
 viewpath=dist/'scene_view.json';v=json.loads(viewpath.read_text(encoding='utf-8'))
 assert v['version']=='V007-facade-candidate-r1','Need frozen V007 runtime'
 assert sha(asset/'v007_east_facades.glb')==report['source_v007_sha256'],'V007 source changed'
 for f in ['v008_architecture_manifest.json','review_v008.html']:
  if (dist/f).exists():raise FileExistsError(f)
 dst=asset/model.name
 if dst.exists():raise FileExistsError(dst)
 shutil.copy2(model,dst)
 descriptor={'path':'assets/'+model.name,'bytes':model.stat().st_size,'sha256':sha(model)}
 v['version']='V008-structure-candidate-r1';v['extension_v008']={
  'manifest':'v008_architecture_manifest.json','model':descriptor,
  'frozen_v007_model_sha256':report['source_v007_sha256'],
  'status':'historical official photo guided 2018 facade details; 2025 current not verified',
  'skip_hidden_archived_models_on_boot':['V005_FACADES','V007_FACADES']}
 viewpath.write_text(json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
 contract={'schema':'noboribetsu-date-v008-structure/1','version':v['version'],
  'base_version':'V007-facade-candidate-r1','model':descriptor,'frozen_v007_model_sha256':report['source_v007_sha256'],
  'source_photo':{'url':report['reference_url'],'age':report['reference_age'],'license':'link only, not bundled'},
  'geometry':{'original_mesh_count':report['original_mesh_count'],'original_triangles':report['original_triangles'],
              'added_mesh_count':report['new_mesh_count'],'added_triangles':report['new_triangles'],
              'total_triangles':report['total_triangles']},
  'scope':{'route_changed':False,'collision_changed':False,'A_stage_changed':False,'V007_geometry_changed':False,
           'other_buildings_changed':False,'new_buildings':0,'interior_access':False},
  'realism':'photo-guided older architectural cues; current 2026 facade appearance not verified',
  'status':'GLB exported and reloaded; WebGL2/Android/Blender-native not verified'}
 (dist/'v008_architecture_manifest.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 
 js=dist/'app.js';s=js.read_text(encoding='utf-8')
 s=once(s,'let v005Road=null,v005Facades=null,v005Signs=null,v006Road=null,v007Facades=null;',
        'let v005Road=null,v005Facades=null,v005Signs=null,v006Road=null,v007Facades=null,v008Facades=null;', 'variable')
 s=once(s,"version:'V007-facade-candidate-r1',boot_ms", "version:'V008-structure-candidate-r1',boot_ms",'metrics')
 # These lists are nested suffixes in three extension versions. Adding V008 to
 # the shared suffix propagates across V004/V005/V006 validation consistently.
 suffix="'V006-tail-candidate-r1','V007-facade-candidate-r1'].includes(manifest.version)"
 if s.count(suffix)!=3:raise RuntimeError('V004/V005/V006 version-list layout changed')
 s=s.replace(suffix,"'V006-tail-candidate-r1','V007-facade-candidate-r1','V008-structure-candidate-r1'].includes(manifest.version)")
 old="""    loadText.textContent='正在驗證 V005 擴建資產 '+name+'…';
    const root=await loadStageModel({...m,stage});root.name=stage;
    root.visible=stage==='V005_ROAD';"""
 new="""    // In V008, V005 façade is an archived original never shown. Its SHA contract is kept,
    // but do not fetch/parse an invisible 395,568-byte GLB during initial boot.
    if(stage==='V005_FACADES'&&manifest.version==='V008-structure-candidate-r1'){
      metrics.v008_skipped_hidden_models??=[];metrics.v008_skipped_hidden_models.push({stage,bytes:m.bytes,sha256:m.sha256});continue;
    }
    loadText.textContent='正在驗證 V005 擴建資產 '+name+'…';
    const root=await loadStageModel({...m,stage});root.name=stage;
    root.visible=stage==='V005_ROAD';"""
 s=once(s,old,new,'skip archived model')
 fn="""// V008 only downloads the new photo-guided candidate, not the archived V005/V007 façades.
async function loadV008StructureCandidate(){
  const c=manifest.extension_v008;
  if(!c||manifest.version!=='V008-structure-candidate-r1')throw new Error('V008 模型版本描述不符');
  const info=await getJSON(c.manifest);
  if(info.schema!=='noboribetsu-date-v008-structure/1'||info.base_version!=='V007-facade-candidate-r1'||
     info.frozen_v007_model_sha256!==c.frozen_v007_model_sha256||
     info.model?.path!==c.model?.path||info.model?.sha256!==c.model?.sha256||info.model?.bytes!==c.model?.bytes||
     info.scope?.route_changed!==false||info.scope?.collision_changed!==false||
     info.scope?.new_buildings!==0||info.scope?.other_buildings_changed!==false||
     info.scope?.A_stage_changed!==false)
    throw new Error('V008 幾何或版本契約不一致，已拒絕載入');
  loadText.textContent='驗證草鞋屋 V008 歷史照片導向建築細節…';
  v008Facades=await loadStageModel({...c.model,stage:'V008_FACADES'});
  v008Facades.name='V008_FACADES';v008Facades.visible=false;
  metrics.v008_structural={model_sha256:info.model.sha256,source_v007_sha256:info.frozen_v007_model_sha256,
    added_triangles:info.geometry.added_triangles,route_unchanged:true,collision_unchanged:true,
    appearance_status:'author-estimated; 2025 refit unresolved',skipped_models:metrics.v008_skipped_hidden_models||[]};
  refreshDiagnostics();
}
"""
 s=once(s,'function place(atEnd=false){',fn+'function place(atEnd=false){','new function')
 s=once(s,'    await loadV007FacadeCandidate();','    await loadV008StructureCandidate();','boot override')
 s=once(s,"if(v005Facades)v005Facades.visible=false;if(v007Facades)v007Facades.visible=value==='B';if(v005Signs)v005Signs.visible=value==='B';",
        "if(v005Facades)v005Facades.visible=false;if(v007Facades)v007Facades.visible=false;if(v008Facades)v008Facades.visible=value==='B';if(v005Signs)v005Signs.visible=value==='B';",'stage switch')
 s=once(s,"'第一人稱 · '+stage+' 場景 · V007 商家街精修'", "'第一人稱 · '+stage+' 場景 · V008 草鞋屋簷下與窗格精修'",'stage label')
 s=once(s,"version:'V007-facade-candidate-r1'});", "version:'V008-structure-candidate-r1'});",'dataset version')
 s=once(s,'Noboribetsu_Date_V007_browser_diagnostics.json','Noboribetsu_Date_V008_browser_diagnostics.json','diagnostic filename')
 s=once(s,"'完整 V003 B、V004／V005 街景、V006 道路與 V007 外觀精修已載入；A 按需下載'",
        "'完整 B 場景與 V008 建築細節已驗證；舊外觀保留但未重複下載，A 按需下載'",'load status')
 js.write_text(s,encoding='utf-8')
 
 original=dist/'index.html';h=original.read_text(encoding='utf-8')
 h=h.replace('V007 近景精修候選','V008 草鞋屋建築精修候選')
 h=h.replace('V007 近景精修候選 R1','V008 草鞋屋建築精修候選 R1')
 h=h.replace('V007 候選｜231.6 m','V008 候選｜231.6 m')
 h=h.replace('review_v007.html','review_v008.html')
 h=h.replace('查看 V006／V007 真實 GLB 同鏡位比較','查看 V007／V008 同鏡位診斷比較')
 h=h.replace('V007 僅修正草鞋屋及變裝攝影館的材質與暖簾，不更動道路與碰撞；WebGL2、Android 真機、Blender-native、私人網站 CDN／登入仍未驗收。',
   'V008 只對草鞋屋加入建築推估細節，保留 V007 與路線碰撞。參考的 2018 官方舊照不等於 2026 現況；WebGL2、Android、Blender、私人站仍未驗收。')
 original.write_text(h,encoding='utf-8')
 (dist/'qa.json').write_text(json.dumps({'version':'V008-structure-candidate-r1','status':'candidate_GLB_geometry_and_offline_tests_only',
  'summary':'V008 草鞋屋基於官方歷史照片做局部結構推估；舊 V007 與道路碰撞不變。省去初始 2 個隱藏外觀 GLB 傳輸；WebGL2 真實畫面、Android、Blender、私人網址仍未驗收。',
  'webgl2':'context unavailable in current Chromium','android':'not tested','blender_native':'not executed','private_site':'unchanged','third_person':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 # fallbacks: actual generated VTK stills, each pair uses same virtual camera; no photo pixels.
 (dist/'evidence').mkdir(exist_ok=True)
 imgs=['waraji_front','waraji_eave','utsuroi']
 for nm in imgs:shutil.copy2(outputs/f'V008_{nm}_same_camera.png',dist/'evidence'/f'V008_{nm}_same_camera.png')
 items='\n'.join(f'<figure><img src="evidence/V008_{key}_same_camera.png" alt="V007 與 V008 {html.escape(key)} 模型對照"><figcaption>{label}：左 V007／右 V008，使用實際 GLB 的 VTK 同鏡位診斷，非 WebGL 或 Blender 畫面</figcaption></figure>' for key,label in [('waraji_front','草鞋屋正面'),('waraji_eave','草鞋屋二樓屋簷'),('utsuroi','變裝攝影館未修改對照')])
 page=f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>登別伊達時代村 V008｜建築對照</title><style>body{{background:#f4f3ee;color:#25382e;font-family:system-ui,"Noto Sans TC",sans-serif;margin:0}}main{{max-width:1160px;margin:auto;padding:24px}}figure{{background:white;border:1px solid #d5d4c9;padding:12px;margin:20px 0;border-radius:12px}}img{{width:100%;height:auto}}figcaption{{font-size:14px;color:#53645a;padding:8px}}p{{line-height:1.7}}a{{color:#326756}}</style></head><body><main><p><a href="index.html">返回 3D 場景</a></p><h1>V008 草鞋屋建築細節比較</h1><p>本頁由真實 GLB 重新讀入並以 VTK 固定鏡頭渲染。新增的二樓紙窗襯板、簷下木構與石基座是依<a href="{html.escape(report['reference_url'])}" target="_blank" rel="noopener noreferrer">2018 年存放的官方草鞋屋照片</a>推估；2025 年店舖改裝後的現況尚未查證，請勿視為精確還原。圖片非遊戲畫面，也未將第三方照片納入模型。</p>{items}<p>V007 全部 17 組原始模型頂點與面保持不變。V008 路線維持 231.5664 m；Android、WebGL2、Blender 與私人站連線未通過實測。</p></main></body></html>'''
 (dist/'review_v008.html').write_text(page,encoding='utf-8')
 print(json.dumps({'status':'V008_INTEGRATED_OFFLINE','new_model':descriptor,'skips':['V005_FACADES','V007_FACADES'],'version':v['version']},ensure_ascii=False))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('runtime_root',type=Path);ap.add_argument('work',type=Path);args=ap.parse_args();integrate(args.runtime_root,args.work)