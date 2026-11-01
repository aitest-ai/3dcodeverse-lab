#!/usr/bin/env python3
"""Apply V004 merchant extension to a copied, NEVER in-place V003 R3 runtime.
This script asserts original V003 source markers and fails closed on unexpected upstream changes.
"""
from pathlib import Path
import json, zipfile, hashlib, os
ROOT=Path(os.environ.get("NOBORIBETSU_V004_WORKDIR", Path(__file__).resolve().parent)).resolve()
DST=ROOT/'runtime/dist'
BASE=ROOT/'baseline'
source=BASE/'app_R3_original.js'
if not source.is_file():
    raise FileNotFoundError("Frozen V003 R3 original app not found. Run prepare_v004_sources.py first.")
s=source.read_text()

def patch(old,new):
    global s
    if s.count(old)!=1:
        raise RuntimeError(f'Unexpected R3 source edit: expected marker {old[:85]!r} exactly once, found {s.count(old)}')
    s=s.replace(old,new)
patch("import {CollisionWorld,nearestRoute} from './navigation.js';", "import {CollisionWorld,nearestRoute,collisionForStage} from './navigation.js';")
patch("let aDescriptor=null,aLoadPromise=null,aLoaded=false;", "let aDescriptor=null,aLoadPromise=null,aLoaded=false;\nlet extensionRoad=null,extensionFacades=null,extensionSigns=null,collisionData=null;")
patch("const metrics=window.__DATE_METRICS__={version:'V003-candidate-r3'", "const metrics=window.__DATE_METRICS__={version:'V004-merchant-candidate-r1'")
patch("function place(atEnd=false){", """function pointInPolygonEUS(x,z,poly){
  let inside=false;
  for(let i=0,j=poly.length-1;i<poly.length;j=i++){
    const [xi,zi]=poly[i],[xj,zj]=poly[j];
    if((zi>z)!==(zj>z)&&x<(xj-xi)*(z-zi)/(zj-zi)+xi)inside=!inside;
  }
  return inside;
}
// Remove only placeholder triangles associated with the three actual named OSM footprints.
// The immutable original B GLB bytes are untouched. Unknown mesh layouts fail explicitly.
function suppressGreyBuildingPlaceholders(root,buildingIds){
  const polygons=manifest.buildings.filter(b=>buildingIds.includes(b.id))
    .map(b=>b.polygon.map(([x,north])=>[x,-north]));
  if(polygons.length!==buildingIds.length)throw new Error('V004 具名建物的 OSM 底面缺漏');
  let affectedMeshes=0,removedTriangles=0;
  root.updateMatrixWorld(true);
  root.traverse(o=>{
    if(!o.isMesh||!o.geometry)return;
    const mats=Array.isArray(o.material)?o.material:[o.material];
    if(!mats.some(m=>m?.name==='Unrefined_OSM_mass'))return;
    if(mats.length!==1)throw new Error('OSM 量體材質結構不同，停止 V004 覆寫排除');
    const g=o.geometry,pos=g.getAttribute('position'),ix=g.getIndex();
    if(!pos)throw new Error('OSM 量體位置緩衝不存在');
    const count=ix?ix.count:pos.count;
    if(count%3!==0)throw new Error('OSM 量體三角面資料不完整');
    const keep=[];const v=new THREE.Vector3();
    for(let i=0;i<count;i+=3){
      let cx=0,cz=0;
      for(let j=0;j<3;j++){
        const k=ix?ix.getX(i+j):i+j;
        v.fromBufferAttribute(pos,k).applyMatrix4(o.matrixWorld);cx+=v.x/3;cz+=v.z/3;
      }
      if(polygons.some(poly=>pointInPolygonEUS(cx,cz,poly)))removedTriangles++;
      else{keep.push(ix?ix.getX(i):i,ix?ix.getX(i+1):i+1,ix?ix.getX(i+2):i+2);}
    }
    if(keep.length!==count){g.setIndex(keep);g.computeBoundingSphere();affectedMeshes++;}
  });
  if(!removedTriangles)throw new Error('V004 量體排除失敗：未找到任何可替換的 OSM 三角面');
  metrics.v004_placeholder_removal={affectedMeshes,removedTriangles,buildingIds};refreshDiagnostics();
}
async function loadV004Extension(){
  if(!manifest.extension||manifest.version!=='V004-merchant-candidate-r1')
    throw new Error('V004 場景描述與擴展資料未對應。');
  const info=await getJSON(manifest.extension.manifest);
  if(info.schema!=='noboribetsu-date-v004-merchant/1'||
      Math.abs(info.route_new_length_m-manifest.route.at(-1).s)>.01)
    throw new Error('V004 路線與擴建版本契約不一致。');
  const extCollision=await getJSON(manifest.extension.collision);
  if(extCollision.schema!=='noboribetsu-date-v004-merchant-extension/1'||
      extCollision.walkable?.length!==1)throw new Error('V004 碰撞擴展資料異常。');
  collisionData={...collisionData,
    walkable:[...collisionData.walkable,...extCollision.walkable],
    obstacles:[...collisionData.obstacles,...extCollision.obstacles]};
  for(const [name,stage] of [['v004_merchant_road.glb','V004_ROAD'],['v004_merchant_facades.glb','V004_FACADES'],['v004_merchant_signs.glb','V004_SIGNS']]){
    const m=info.models[name];if(!m||m.path!==manifest.extension.models[name]?.path||m.sha256!==manifest.extension.models[name]?.sha256)
      throw new Error('V004 模型描述不一致：'+name);
    loadText.textContent='正在驗證擴建場景 '+name+'（保留原 B 模型品質）…';
    const root=await loadStageModel({...m,stage});
    root.name=stage;root.visible=stage==='V004_ROAD';
    if(stage==='V004_ROAD')extensionRoad=root;
    else if(stage==='V004_FACADES')extensionFacades=root;
    else extensionSigns=root;
  }
  suppressGreyBuildingPlaceholders(B,manifest.extension.building_ids);
  world=new CollisionWorld(collisionForStage(collisionData,'B'),8);
  metrics.v004_extension={added_m:info.added_length_m,models:3,source:'frozen V002 OSM; facade is author-estimated'};
  refreshDiagnostics();
}
function place(atEnd=false){""")
patch("  if(!session)return;inputEvents.cancel();const before=session.cameraPose();const from=session.stage;session.setStage(value);const after=session.cameraPose();",
"  if(!session)return;inputEvents.cancel();const before=session.cameraPose();const from=session.stage;session.setStage(value);\n  if(collisionData){world=new CollisionWorld(collisionForStage(collisionData,value),8);session.world=world;}\n  if(extensionFacades)extensionFacades.visible=value==='B';if(extensionSigns)extensionSigns.visible=value==='B';\n  const after=session.cameraPose();")
patch("  Object.assign($('scene').dataset,{position:[position.x,position.y,position.z].map(v=>v.toFixed(3)).join(','),heading:heading.toFixed(6),pitch:pitch.toFixed(6),stage,fov:String(session.fov),version:'V003-candidate-r3'});",
"  Object.assign($('scene').dataset,{position:[position.x,position.y,position.z].map(v=>v.toFixed(3)).join(','),heading:heading.toFixed(6),pitch:pitch.toFixed(6),stage,fov:String(session.fov),version:'V004-merchant-candidate-r1'});")
patch("  $('modeLabel').textContent='第一人稱 · '+stage+' 場景'+(blocked?' · 接近障礙／樣區邊界':'');",
"  $('modeLabel').textContent='第一人稱 · '+stage+' 場景 · V004 商家街'+(blocked?' · 接近障礙／樣區邊界':'');")
patch("  const px=x=>W/2+(x+1)*3.3,py=z=>29+(z+25)*2.16;",
"  const px=x=>12+(x+18)/85*(W-24),py=z=>15+(z+31)/110*(H-30);")
patch("  ctx.font='12px sans-serif';ctx.fillStyle='#4e5e4f';ctx.fillText('北 ↑',W-43,19);ctx.font='11px sans-serif';ctx.fillText('大手門',px(7),py(0));ctx.fillText('遊戯館',px(10),py(23));ctx.fillText('首期終點',px(4),py(59));",
"  ctx.font='12px sans-serif';ctx.fillStyle='#4e5e4f';ctx.fillText('北 ↑',W-43,19);ctx.font='11px sans-serif';ctx.fillText('大手門',px(7),py(0));ctx.fillText('遊戯館',px(10),py(23));ctx.fillText('轉彎',px(-2),py(59));ctx.fillText('七萬石',px(28),py(74));ctx.fillText('北京亭',px(34),py(50));ctx.fillText('V004 街尾',px(40),py(65));")
patch("    const collision=await getJSON('collision.json');world=new CollisionWorld(collision,8);",
"    collisionData=await getJSON('collision.json');world=new CollisionWorld(collisionData,8);")
patch("    B=await loadStageModel(bDescriptor,onBytes);\n    A=new THREE.Group();",
"    B=await loadStageModel(bDescriptor,onBytes);\n    await loadV004Extension();\n    A=new THREE.Group();")
patch("    $('enterButton').hidden=false;$('load').setAttribute('aria-busy','false');",
"    $('enterButton').hidden=false;$('load').setAttribute('aria-busy','false');")
patch("    session=new WalkSession({world,route:manifest.route,variants:{A,B}});",
"    session=new WalkSession({world,route:manifest.route,variants:{A,B}});")
patch("    setStage('B');resize();progress.value=100;loadText.textContent='B 精修場景已載入；A 骨架會在首次切換時無損載入';",
"    setStage('B');resize();progress.value=100;loadText.textContent='完整 V003 B ＋ V004 商家街 3D 擴建已載入；A 骨架首次切換才下載';")
patch("a.download='Noboribetsu_Date_V003_browser_diagnostics.json';",
"a.download='Noboribetsu_Date_V004_browser_diagnostics.json';")
(DST/'app.js').write_text(s,encoding='utf-8')
print('wrote app.js',len(s),'bytes')

# UI: explicit candidate and provenance, never misrepresent Blender/Android/browser verification.
index_original=BASE/'index_R3_original.html'
if not index_original.exists():
    raise FileNotFoundError("Frozen V003 R3 index not found. Run prepare_v004_sources.py first.")
html=index_original.read_text()
assert html.count('V003')>=3
html=html.replace('登別伊達時代村 V003 候選｜大手門・遊戯館','登別伊達時代村 V004 擴建候選｜商家街第一段')
html=html.replace('以真實地理資料與照片查證重建的大手門、遊戯館外觀樣區。獨立私人預覽，附同鏡頭 A／B 比較。', '以凍結 OSM 道路與建築輪廓擴建的 V004 候選；商家街外觀為作者推估，非現地測量。')
html=html.replace('V003 候選 R3','V004 擴建候選 R1')
html=html.replace('大手門與遊戯館外觀 · 原創材質 · 實際地形','保留完整 V003 B 模型 · 新增約 47 公尺商家街 · 作者估值外觀')
html=html.replace('可步行段從大手門北側廣場，到商家街南側第一個轉折；本次步行導引約 82.9 公尺。V004 擴建候選 R1 延續 V002 與 R2 的場景內容，初始只載完整 B 精修場景；A 資料骨架在第一次切換時才無損載入，並保留三項可見美術精修。V002 原版保留。V002 集中精修大手門到遊戯館的既有核心範圍，未延長路線。',
                  '可步行段從大手門北側廣場繼續經過第一個轉彎、向東延伸到商家街，V004 導引約 130.0 公尺（較 V003 新增約 47.1 公尺）。V004 完整保留 V003 R3 高品質 B 模型，另載入原創商家街地面與三棟外觀候選。高等學問所、北京亭、七萬石的名稱與位置採 V002 凍結 OSM 資料，建物門面、屋頂高度、招牌位置屬作者推估，不代表現場實測；室內未製作，V002/V003 均不覆寫。')
html=html.replace('大手門、遊戯館及入口鋪面依可定位照片製作。木構、瓦、門窗等為獨立幾何；其他鄰棟保留為待精修量體。',
                  '大手門與遊戯館沿用 V003 R3；本次新增商家街路面、窄石邊、屋瓦、木格柵、柱廊和原創招牌候選。只靠 OSM 能確認平面輪廓，三棟外觀仍是待實景比對的假設，不宣稱精確還原。')
html=html.replace('2019 年航照、2025 年官方照片用於查證。尺寸與地形仍有誤差，這是視覺重建樣區。',
                  '本次路線沿 V002 OSM 快照，約 6 公尺道路寬度、接地、三棟外觀與燈具為作者推估；未新增排水或室內，不複製官方照片。V004 新增實體 Android、Blender-native、私人網站 CDN／登入仍未驗收。')
(DST/'index.html').write_text(html,encoding='utf-8')
qa={'version':'V004-merchant-candidate-r1','status':'new_candidate_not_full_acceptance',
    'summary':'V004 商家街擴建候選：保留 V003 R3 高品質 B 模型與 A 懶載入；接續既有步行路線往東新增約 47.1 公尺、新增道路及 3 棟具名 OSM 建物的程序化外觀與碰撞。外觀細節與路寬為作者估值，不是測繪。新版 Blender 母檔、Android 真機與私人 CDN／登入尚未驗收。',
    'inherited_evidence':'V003 R3 Chromium + mobile simulation; not retested as V004 until V004 browser test completes',
    'v004_browser':'attempted; current test host cannot create WebGL2, full V004 browser rendering unverified', 'android':'not tested', 'blender_native':'source_ready_only','private_cdn':'not tested',
    'base_assets_sha256':'no changes to original V003 model/transport files'}
(DST/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')