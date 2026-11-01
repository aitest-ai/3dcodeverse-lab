#!/usr/bin/env python3
"""Add V007 photo-agnostic PBR façade candidate as a non-destructive B-stage override.

Run on a COPY of the V006 Runtime tree. The V006 ZIP remains byte-identical.
The baseline V005 GLB remains packaged, unchanged, and its own manifest stays frozen.
"""
from pathlib import Path
import sys,json,hashlib,shutil
root=Path(sys.argv[1]).resolve()
work=Path(sys.argv[2]).resolve()
dist=root/'dist';asset=dist/'assets';v007=work/'v007_outputs/v007_east_facades.glb'
if not dist.is_dir() or not v007.exists():raise SystemExit('Need extracted V006 runtime and completed V007 GLB')
view_path=dist/'scene_view.json';manifest=json.loads(view_path.read_text());qa=json.loads((work/'v007_outputs/v007_facade_qa.json').read_text())
assert manifest['version']=='V006-tail-candidate-r1', 'Requires pristine V006 candidate'
assert qa['source']['sha256']==hashlib.sha256((asset/'v005_east_facades.glb').read_bytes()).hexdigest()
assert qa['model']['sha256']==hashlib.sha256(v007.read_bytes()).hexdigest()

for new in ['v007_facade_manifest.json','review_v007.html']:
 if (dist/new).exists():raise FileExistsError('Refusing to overwrite old output '+new)
shutil.copy2(v007,asset/v007.name)
assert hashlib.sha256((asset/v007.name).read_bytes()).hexdigest()==qa['model']['sha256']
# Append-only semantic contract: both the original V005 and new V007 URLs exist.
model={'path':'assets/v007_east_facades.glb','bytes':v007.stat().st_size,'sha256':qa['model']['sha256']}
manifest['version']='V007-facade-candidate-r1'
manifest['extension_v007']={'manifest':'v007_facade_manifest.json','model':model,'source_v005_model_sha256':qa['source']['sha256'],
  'status':'artist-estimated B-stage materials and noren only; no route or collision changes'}
view_path.write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':'))+'\n')
facade_contract={'schema':'noboribetsu-date-v007-facade/1','base_version':'V006-tail-candidate-r1','version':manifest['version'],
 'source':qa['source'],'model':model,'mesh_count':qa['mesh_count'],'triangles':qa['total_triangles'],
 'scope':{'edited_buildings':['way/283905573','way/283905580'],'road_changed':False,'collision_changed':False,
          'V003_B_changed':False,'V005_original_façade_changed':False,'new_buildings':0,'interiors':False},
 'noren_max_displacement_m':qa['noren_max_displacement_m'],
 'status':'real GLB reloaded; neither site accuracy nor WebGL2/Android/Blender-native passed'}
(dist/'v007_facade_manifest.json').write_text(json.dumps(facade_contract,ensure_ascii=False,indent=2)+'\n')

script=dist/'app.js';s=script.read_text()
def once(a,b,label):
 global s
 if s.count(a)!=1:raise RuntimeError(f'{label} expected once; got {s.count(a)}')
 s=s.replace(a,b)
once('let v005Road=null,v005Facades=null,v005Signs=null,v006Road=null;','let v005Road=null,v005Facades=null,v005Signs=null,v006Road=null,v007Facades=null;','add object')
once("version:'V006-tail-candidate-r1',boot_ms", "version:'V007-facade-candidate-r1',boot_ms",'metrics version')
once("['V004-merchant-candidate-r1','V005-east-candidate-r1','V006-tail-candidate-r1'].includes(manifest.version)","['V004-merchant-candidate-r1','V005-east-candidate-r1','V006-tail-candidate-r1','V007-facade-candidate-r1'].includes(manifest.version)",'v004 versions')
once("['V005-east-candidate-r1','V006-tail-candidate-r1'].includes(manifest.version)","['V005-east-candidate-r1','V006-tail-candidate-r1','V007-facade-candidate-r1'].includes(manifest.version)",'v005 versions')
once("manifest.version!=='V006-tail-candidate-r1'", "!['V006-tail-candidate-r1','V007-facade-candidate-r1'].includes(manifest.version)",'v006 versions')
load_func="""// Visual-only B-stage override. Original V005 facade stays in archive, unchanged.
async function loadV007FacadeCandidate(){
  const c=manifest.extension_v007;
  if(!c||manifest.version!=='V007-facade-candidate-r1')throw new Error('V007 模型版本描述未對應');
  const info=await getJSON(c.manifest);
  if(info.schema!=='noboribetsu-date-v007-facade/1'||info.base_version!=='V006-tail-candidate-r1'||
     info.source?.sha256!==c.source_v005_model_sha256||
     info.model?.path!==c.model?.path||info.model?.sha256!==c.model?.sha256||
     info.model?.bytes!==c.model?.bytes||info.scope?.collision_changed!==false||
     info.scope?.road_changed!==false||info.scope?.new_buildings!==0)
    throw new Error('V007 材質/暖簾回寫契約不符，拒絕使用未核實替代模型');
  loadText.textContent='正在驗證 V007 精修木紋與暖簾模型…';
  v007Facades=await loadStageModel({...c.model,stage:'V007_FACADES'});
  v007Facades.name='V007_FACADES';v007Facades.visible=false;
  if(v005Facades)v005Facades.visible=false;
  metrics.v007_facades={source_sha256:info.source.sha256,new_sha256:info.model.sha256,
    collisions_unchanged:true,route_unchanged:true,geometry_scope:'material + <=1.9cm noren displacement'};
  refreshDiagnostics();
}
"""
once('function place(atEnd=false){',load_func+'function place(atEnd=false){','v007 function')
once('    await loadV006Extension();\n    A=new THREE.Group();','    await loadV006Extension();\n    await loadV007FacadeCandidate();\n    A=new THREE.Group();','v007 init')
once("if(v005Facades)v005Facades.visible=value==='B';if(v005Signs)v005Signs.visible=value==='B';",
     "if(v005Facades)v005Facades.visible=false;if(v007Facades)v007Facades.visible=value==='B';if(v005Signs)v005Signs.visible=value==='B';",'v007 stage')
once("'第一人稱 · '+stage+' 場景 · V006 商家街'", "'第一人稱 · '+stage+' 場景 · V007 商家街精修'",'stage label')
once("version:'V006-tail-candidate-r1'});", "version:'V007-facade-candidate-r1'});",'dataset version')
once('Noboribetsu_Date_V006_browser_diagnostics.json','Noboribetsu_Date_V007_browser_diagnostics.json','diagnostics name')
once("'完整 V003 B ＋ V004／V005 街景、V006 道路已載入；A 骨架按需下載'", "'完整 V003 B、V004／V005 街景、V006 道路與 V007 外觀精修已載入；A 按需下載'",'ready status')
script.write_text(s)

html=(dist/'index.html').read_text()
html=html.replace('V006 擴建候選','V007 近景精修候選').replace('V006 擴建候選 R1','V007 近景精修候選 R1').replace('V006 候選｜231.6 m','V007 候選｜231.6 m')
old='<div id="loadError" role="alert" hidden></div>'
assert html.count(old)==1
html=html.replace(old,old+'<p class="fallback"><a href="review_v007.html" target="_blank" rel="noopener">無法使用 WebGL？查看 V006／V007 真實 GLB 同鏡位比較</a></p>')
html=html.replace('V006 新增 WebGL2、Android 真機、Blender-native、私人網站 CDN／登入尚未驗收；新增道路依凍結 OSM 最後兩段，沒有新建築。',
   'V007 僅修正草鞋屋及變裝攝影館的材質與暖簾，不更動道路與碰撞；WebGL2、Android 真機、Blender-native、私人網站 CDN／登入仍未驗收。')
(dist/'index.html').write_text(html)
qa_status={'version':'V007-facade-candidate-r1','status':'candidate_glb_and_node_qa_only_webgl2_not_verified',
 'summary':'在 V006 原路線 231.5664m 和全部碰撞不變下，草鞋屋與變裝攝影館新增 GLB 材質修正和暖簾 1.4cm 內的垂墜；17 meshes / 14888 triangles, original V005 GLB retained. WebGL2/Android/Blender-native/private CDN not verified.',
 'private_site':'unchanged','blender_native':'not executed','third_person':False,'webgl2':'not tested due no context'}
(dist/'qa.json').write_text(json.dumps(qa_status,ensure_ascii=False,indent=2)+'\n')
# Review HTML references evidence/ side by side diagnostic PNGs, no external assets.
review=Path(work/'v007_outputs')
images=['waraji','utsuroi','approach'];(dist/'evidence').mkdir(exist_ok=True)
for name in images:
 shutil.copy2(review/f'V007_{name}_same_camera.png',dist/'evidence'/f'V007_{name}_same_camera.png')
cards='\n'.join(f'<figure><img src="evidence/V007_{name}_same_camera.png" alt="V006、V007 {name} 同鏡位對照"><figcaption>{label}｜左 V006、右 V007，皆為實體 GLB 的 VTK 診斷，非遊玩畫面</figcaption></figure>' for name,label in [('waraji','草鞋屋'),('utsuroi','變裝攝影館'),('approach','商家街入口')])
page=f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>登別伊達時代村 V007｜GLB 診斷比較</title>
<style>body{{font-family:system-ui,"Noto Sans TC",sans-serif;background:#f5f3ec;color:#28352e;margin:0}}main{{max-width:1180px;margin:auto;padding:24px}}h1{{font-size:clamp(22px,4vw,34px)}}figure{{margin:24px 0;background:#fff;border:1px solid #ddd9cd;padding:10px;border-radius:10px}}img{{width:100%;height:auto}}figcaption{{padding:8px;font-size:14px;color:#536055}}a{{color:#2d6258}}.note{{line-height:1.75}}</style></head><body><main><p><a href="index.html">回 3D 場景</a></p><h1>V006 / V007 同鏡位模型檢查</h1><p class="note">本頁供 WebGL 無法啟動時檢視**實際 glTF/GLB 幾何**的 VTK 診斷圖。兩版使用同一相機位置與燈光，不是 Blender Cycles、不是瀏覽器 WebGL、也不是依實景驗收。屋高、立面、木構仍為作者估計；沒有使用官方照片貼圖。</p>{cards}<p>版本：V007 façade candidate R1｜原始 V006 道路與碰撞完全保留｜Android／私人網站未驗收</p></main></body></html>'''
(dist/'review_v007.html').write_text(page)
print(json.dumps({'status':'V007_PATCHED', 'model':model, 'new_files':['v007_facade_manifest.json','review_v007.html','assets/v007_east_facades.glb'],'fallback_images':images},ensure_ascii=False))