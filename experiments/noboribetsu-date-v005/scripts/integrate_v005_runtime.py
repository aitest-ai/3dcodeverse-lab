#!/usr/bin/env python3
"""Append V005 to V004 R1 without rewriting V004 GLB, collision, shaders, loader or controls."""
from __future__ import annotations
from pathlib import Path
import os,json,hashlib
ROOT=Path(os.environ.get('DATE_V005_ROOT',str(Path(__file__).resolve().parent.parent/'runtime')))
DIST=ROOT/'dist'
original=(ROOT/'V004_source_app.js').read_text(encoding='utf8')
s=original

def patch(old,new,label):
 global s
 count=s.count(old)
 if count!=1:raise RuntimeError(f'{label}: expected exactly one marker, got {count}: {old[:80]}')
 s=s.replace(old,new)

patch('let extensionRoad=null,extensionFacades=null,extensionSigns=null,collisionData=null;',
'''let extensionRoad=null,extensionFacades=null,extensionSigns=null,collisionData=null;
let v005Road=null,v005Facades=null,v005Signs=null;''','new scene roots')
patch("version:'V004-merchant-candidate-r1',boot_ms", "version:'V005-east-candidate-r1',boot_ms",'metric version')
patch("if(!manifest.extension||manifest.version!=='V004-merchant-candidate-r1')",
"if(!manifest.extension||!['V004-merchant-candidate-r1','V005-east-candidate-r1'].includes(manifest.version))",'preserve old version option')
patch('Math.abs(info.route_new_length_m-manifest.route.at(-1).s)>.01)',
'!manifest.route.some(p=>Math.abs(p.s-info.route_new_length_m)<.01))','check V004 junction in V005 long route')
# Insert after complete V004 stage loads, before place(): V005 new separate layer.
marker='function place(atEnd=false){'
function='''async function loadV005Extension(){
  const c=manifest.extension_v005;
  if(!c||manifest.version!=='V005-east-candidate-r1')throw new Error('V005 描述或版本未對應');
  const info=await getJSON(c.manifest);
  if(info.schema!=='noboribetsu-date-v005-east/1'||info.base_version!=='V004-merchant-candidate-r1'||
     Math.abs(info.route_end_m-manifest.route.at(-1).s)>.01||
     !manifest.route.some(p=>Math.abs(p.s-info.route_start_m)<.01))
       throw new Error('V005 OSM 路線連續性檢查未通過');
  const collision=await getJSON(c.collision);
  if(collision.schema!=='noboribetsu-date-v005-east-extension/1'||collision.walkable?.length!==1||
     collision.untouched_v004_collision_sha256!==manifest.extension.collision_sha256_v004)
       throw new Error('V005 碰撞描述未通過版本驗證');
  collisionData={...collisionData,walkable:[...collisionData.walkable,...collision.walkable],obstacles:[...collisionData.obstacles,...collision.obstacles]};
  for(const [name,stage] of [['v005_east_road.glb','V005_ROAD'],['v005_east_facades.glb','V005_FACADES'],['v005_east_signs.glb','V005_SIGNS']]){
    const m=info.models[name];if(!m||m.path!==c.models[name]?.path||m.sha256!==c.models[name]?.sha256)
      throw new Error('V005 模型雜湊描述不一致：'+name);
    loadText.textContent='正在驗證 V005 擴建資產 '+name+'…';
    const root=await loadStageModel({...m,stage});root.name=stage;
    root.visible=stage==='V005_ROAD';
    if(stage==='V005_ROAD')v005Road=root;
    else if(stage==='V005_FACADES')v005Facades=root;
    else v005Signs=root;
  }
  suppressGreyBuildingPlaceholders(B,c.building_ids);
  world=new CollisionWorld(collisionForStage(collisionData,'B'),8);
  metrics.v005_extension={added_m:info.added_length_m,models:3,buildings:info.known_buildings.map(x=>x.name),source:'OSM footprints + authored facades'};
  refreshDiagnostics();
}
'''
patch(marker,function+marker,'insert V005 loader')
patch("  if(extensionFacades)extensionFacades.visible=value==='B';if(extensionSigns)extensionSigns.visible=value==='B';",
"  if(extensionFacades)extensionFacades.visible=value==='B';if(extensionSigns)extensionSigns.visible=value==='B';\n  if(v005Facades)v005Facades.visible=value==='B';if(v005Signs)v005Signs.visible=value==='B';",'stage overlays')
patch("'第一人稱 · '+stage+' 場景 · V004 商家街'","'第一人稱 · '+stage+' 場景 · V005 商家街'",'caption')
patch("version:'V004-merchant-candidate-r1'});","version:'V005-east-candidate-r1'});",'dataset version')
patch("const px=x=>12+(x+18)/85*(W-24),py=z=>15+(z+31)/110*(H-30);",
"const px=x=>12+(x+72)/204*(W-24),py=z=>15+(z+31)/156*(H-30);",'map extent')
patch("ctx.fillText('V004 街尾',px(40),py(65));",
"ctx.fillText('V004',px(40),py(65));ctx.fillText('草鞋屋',px(52),py(76));ctx.fillText('變裝館',px(57),py(59));ctx.fillText('V005 街尾',px(100),py(96));",'map names')
patch("    await loadV004Extension();\n    A=new THREE.Group();",
"    await loadV004Extension();\n    await loadV005Extension();\n    A=new THREE.Group();",'insert V005 loader call')
patch("'完整 V003 B ＋ V004 商家街 3D 擴建已載入；A 骨架首次切換才下載'",
"'完整 V003 B ＋ V004／V005 商家街模型已載入；A 骨架首次切換才下載'",'loading ready')
patch('Noboribetsu_Date_V004_browser_diagnostics.json','Noboribetsu_Date_V005_browser_diagnostics.json','diagnostics name')
# B scene grey placeholder safety: every new building must remove at least one original triangle, not just any building.
patch("  if(!removedTriangles)throw new Error('V004 量體排除失敗：未找到任何可替換的 OSM 三角面');",
"  if(!removedTriangles)throw new Error('OSM 量體排除失敗：未找到任何可替換三角面');",'remove guard')
# Save V005 JS only after completing every frozen-context patch.
# Embed independent v004 collision digest in V005 scene-view contract; original V004 JSON remains immutable.
view_path=DIST/'scene_view.json'
view=json.loads(view_path.read_text(encoding='utf8'))
base_collision=(DIST/'extension_collision.json').read_bytes()
view['extension']['collision_sha256_v004']=hashlib.sha256(base_collision).hexdigest()
view_path.write_text(json.dumps(view,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf8')
(DIST/'app.js').write_text(s,encoding='utf8')
# Copy of V004 index with rewritten scope/version, no claim of formal WebGL2 acceptance.
h=(ROOT/'V004_source_index.html').read_text(encoding='utf8')
h=h.replace('V004 擴建候選 R1','V005 擴建候選 R1').replace('V004 擴建候選','V005 擴建候選')
h=h.replace('商家街第一段','商家街第二段')
h=h.replace('V004 商家街','V005 商家街')
h=h.replace('約 130.0 公尺（較 V003 新增約 47.1 公尺）','約 197.7 公尺（較 V004 新增約 67.7 公尺）')
h=h.replace('新增約 47 公尺商家街','V004+V005 總路線約 197.7 公尺')
h=h.replace('V004 新增實體 Android、Blender-native、私人網站 CDN／登入仍未驗收。',
            'V005 新增 WebGL2、Android 真機、Blender-native、私人網站 CDN／登入尚未驗收。')
h=h.replace('三棟外觀仍是待實景比對的假設', 'V004 三棟和 V005 草鞋屋、變裝攝影館的外觀仍待實景比對')
# Ensure visible explicit description is correct, even if previous V004 wording differs.
h=h.replace('</body>',"<p style='position:absolute;bottom:1em;right:1em;z-index:5;pointer-events:none;font:12px sans-serif;background:#fff9;padding:.35em .6em;border-radius:.4em'>V005 候選｜197.7 m 步行路線｜估計外觀，非現地測繪</p></body>")
(DIST/'index.html').write_text(h,encoding='utf8')
old=json.loads((ROOT/'V004_source_qa.json').read_text())
qa={'version':'V005-east-candidate-r1','status':'candidate_navigation_static_checked_browser_not_accepted',
 'summary':'V005 商家街第二段候選：V004 保留；沿原凍結 OSM 再延伸約 67.7 m，總路線約 197.7 m。新增草鞋屋與うつろい館的原創估值外觀。無室內、無第三人稱。Android、真實 WebGL2 畫面與私人 CDN 尚未驗收。',
 'previous_v004_status':old['status'],'blender_native':'not executed','private_site':'unchanged'}
(DIST/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'V005_RUNTIME_PATCHED','source_V004_js_bytes':len(original),'v005_js_bytes':len(s),'manifest_model_entries':3},ensure_ascii=False,indent=2))