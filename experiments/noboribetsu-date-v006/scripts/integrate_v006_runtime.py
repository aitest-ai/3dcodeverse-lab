#!/usr/bin/env python3
"""Minimal versioned V006 patch from original V005 JS; fail closed, never mutate old ZIP."""
from pathlib import Path
import json,os,hashlib
ROOT=Path(os.environ.get('DATE_V006_ROOT',Path(__file__).resolve().parent.parent)).resolve()
DIST=ROOT/'dist'
s=(ROOT/'baseline/app_v005.js').read_text()
def replace(old,new,label):
 global s
 count=s.count(old)
 if count!=1:raise RuntimeError(f'{label}: found {count}, expected 1')
 s=s.replace(old,new)
replace("let v005Road=null,v005Facades=null,v005Signs=null;", "let v005Road=null,v005Facades=null,v005Signs=null,v006Road=null;",'new scene root')
replace("version:'V005-east-candidate-r1',boot_ms", "version:'V006-tail-candidate-r1',boot_ms",'version')
replace("['V004-merchant-candidate-r1','V005-east-candidate-r1'].includes(manifest.version)","['V004-merchant-candidate-r1','V005-east-candidate-r1','V006-tail-candidate-r1'].includes(manifest.version)",'V004 extension allowed versions')
replace("if(!c||manifest.version!=='V005-east-candidate-r1')", "if(!c||!['V005-east-candidate-r1','V006-tail-candidate-r1'].includes(manifest.version))",'V005 extension allowed versions')
replace("Math.abs(info.route_end_m-manifest.route.at(-1).s)>.01||", "!manifest.route.some(p=>Math.abs(p.s-info.route_end_m)<.01)||",'V005 junction preservation')

# Strict per-footprint removal; old candidate accepted a total >0 even when one building was missed.
first=s.index('function suppressGreyBuildingPlaceholders(root,buildingIds){')
last=s.index('async function loadV004Extension(){',first)
new_func='''// V006 surgical replacement: remove whole connected OSM mass components, not only triangle centroids.
// Exact 3-D vertices are keyed at 0.1 mm to connect flat-shaded faces with duplicated indices.
function suppressGreyBuildingPlaceholders(root,buildingIds){
  const ids=[...new Set(buildingIds)];
  if(ids.length!==buildingIds.length||!ids.length)throw new Error('OSM 替換建物清單重複或為空');
  const byId=new Map(manifest.buildings.map(b=>[b.id,b]));
  const polygons=ids.map(id=>{
    const b=byId.get(id);
    if(!b||!Array.isArray(b.polygon)||b.polygon.length<3)throw new Error('OSM 指定建物底面不存在：'+id);
    return {id,poly:b.polygon.map(([x,n])=>[x,-n])};
  });
  const removedById=Object.fromEntries(ids.map(id=>[id,0]));let affectedMeshes=0;
  root.updateMatrixWorld(true);
  root.traverse(o=>{
    if(!o.isMesh||!o.geometry)return;
    const mats=Array.isArray(o.material)?o.material:[o.material];
    if(!mats.some(m=>m?.name==='Unrefined_OSM_mass'))return;
    if(mats.length!==1)throw new Error('OSM 量體不再是單一材質，拒絕排除');
    const g=o.geometry,positions=g.getAttribute('position'),ix=g.getIndex();
    if(!positions)throw new Error('OSM 量體缺少位置緩衝');
    const count=ix?ix.count:positions.count;
    if(count%3!==0)throw new Error('OSM 三角面結構異常');
    const n=count/3,parents=Array.from({length:n},(_,i)=>i),keys=new Map(),cent=[];
    const find=i=>{let j=i;while(parents[j]!==j){parents[j]=parents[parents[j]];j=parents[j]}return j};
    const union=(a,b)=>{const ra=find(a),rb=find(b);if(ra!==rb)parents[ra]=rb};
    const p=new THREE.Vector3();
    for(let i=0;i<n;i++){
      let cx=0,cz=0;
      for(let k=0;k<3;k++){
        const idx=ix?ix.getX(i*3+k):i*3+k;
        p.fromBufferAttribute(positions,idx).applyMatrix4(o.matrixWorld);
        cx+=p.x/3;cz+=p.z/3;
        const key=[p.x,p.y,p.z].map(v=>Math.round(v*10000)).join(',');
        const previous=keys.get(key);
        if(previous===undefined)keys.set(key,i);else union(i,previous);
      }
      cent.push([cx,cz]);
    }
    const groups=new Map();
    for(let i=0;i<n;i++){
      const parent=find(i);
      if(!groups.has(parent))groups.set(parent,[]);
      groups.get(parent).push(i);
    }
    const keep=[];let localRemoved=0;
    for(const group of groups.values()){
      let x=0,z=0;for(const i of group){x+=cent[i][0];z+=cent[i][1]}
      x/=group.length;z/=group.length;
      const hits=polygons.filter(b=>pointInPolygonEUS(x,z,b.poly));
      if(hits.length>1)throw new Error('OSM 建物連通塊落入多個底面：'+hits.map(h=>h.id).join(','));
      if(hits.length){removedById[hits[0].id]+=group.length;localRemoved+=group.length;}
      else for(const i of group)for(let k=0;k<3;k++)keep.push(ix?ix.getX(i*3+k):i*3+k);
    }
    if(localRemoved){
      const safeCopy=g.clone();safeCopy.setIndex(keep);
      safeCopy.computeBoundingBox();safeCopy.computeBoundingSphere();
      o.geometry=safeCopy;affectedMeshes++;
    }
  });
  for(const id of ids)if(removedById[id]===0)throw new Error('OSM 舊量體未成功排除：'+id);
  metrics.placeholder_removal_by_building={...(metrics.placeholder_removal_by_building||{}),...removedById};
  (metrics.placeholder_removal_runs??=[]).push({building_ids:ids,triangles_removed:Object.values(removedById).reduce((a,b)=>a+b,0),affected_meshes:affectedMeshes,method:'connected original OSM mass component by world-space vertex',counts:removedById});
  refreshDiagnostics();
}
'''
s=s[:first]+new_func+s[last:]

v006_func='''async function loadV006Extension(){
  const c=manifest.extension_v006;
  if(!c||manifest.version!=='V006-tail-candidate-r1')throw new Error('V006 擴建契約不存在');
  const info=await getJSON(c.manifest);
  if(info.schema!=='noboribetsu-date-v006-tail/1'||info.base_version!=='V005-east-candidate-r1'||
      Math.abs(info.route_end_m-manifest.route.at(-1).s)>.01||
      !manifest.route.some(p=>Math.abs(p.s-info.previous_route_end_m)<.01))
    throw new Error('V006 凍結 OSM 路線連續性驗證失敗');
  const ext=await getJSON(c.collision);
  if(ext.schema!=='noboribetsu-date-v006-final-frozen-osm-path/1'||ext.walkable?.length!==1||ext.obstacles?.length!==0)
    throw new Error('V006 碰撞或禁用新建物契約不一致');
  collisionData={...collisionData,walkable:[...collisionData.walkable,...ext.walkable],obstacles:[...collisionData.obstacles,...ext.obstacles]};
  const model=info.model;
  if(!model||model.path!==c.model.path||model.sha256!==c.model.sha256||model.bytes!==c.model.bytes)
    throw new Error('V006 模型完整性描述不一致');
  loadText.textContent='正在驗證與解析 V006 凍結 OSM 道路模型…';
  v006Road=await loadStageModel({...model,stage:'V006_ROAD'});
  v006Road.name='V006_ROAD';v006Road.visible=true;
  world=new CollisionWorld(collisionForStage(collisionData,'B'),8);
  metrics.v006_extension={route_length_m:info.route_end_m,added_m:info.added_length_m,model_sha256:model.sha256,
    buildings_added:0,source:'frozen V002 OSM; DEM visual, estimated width'};
  refreshDiagnostics();
}
'''
replace('function place(atEnd=false){',v006_func+'function place(atEnd=false){','append V006 loader')
replace('    await loadV005Extension();\n    A=new THREE.Group();','    await loadV005Extension();\n    await loadV006Extension();\n    A=new THREE.Group();','load V006')
replace("'第一人稱 · '+stage+' 場景 · V005 商家街'","'第一人稱 · '+stage+' 場景 · V006 商家街'",'stage caption')
replace("version:'V005-east-candidate-r1'});","version:'V006-tail-candidate-r1'});",'dataset version')
replace("ctx.fillText('V005 街尾',px(100),py(96));", "ctx.fillText('V005',px(100),py(96));ctx.fillText('新轉彎',px(114),py(101));ctx.fillText('V006 街尾',px(120),py(81));",'minimap end')
replace("'完整 V003 B ＋ V004／V005 商家街模型已載入；A 骨架首次切換才下載'","'完整 V003 B ＋ V004／V005 街景、V006 道路已載入；A 骨架按需下載'",'load ready')
replace('Noboribetsu_Date_V005_browser_diagnostics.json','Noboribetsu_Date_V006_browser_diagnostics.json','diagnostics filename')
# Stage switch retains V004/V005 facades and V006 road in both stages; no new candidate buildings.
(DIST/'app.js').write_text(s,encoding='utf8')
html=(ROOT/'baseline/index_v005.html').read_text(encoding='utf8')
html=html.replace('V005 擴建候選｜商家街第二段','V006 擴建候選｜商家街後段')
html=html.replace('V005 擴建候選 R1','V006 擴建候選 R1')
html=html.replace('V004+V005 總路線約 197.7 公尺','V004～V006 總路線約 231.6 公尺')
html=html.replace('V005 候選｜197.7 m 步行路線','V006 候選｜231.6 m 步行路線')
html=html.replace('V004 導引約 197.7 公尺（較 V004 新增約 67.7 公尺）','V006 導引約 231.6 公尺（較 V005 新增約 33.8 公尺）')
html=html.replace('V005 新增 WebGL2、Android 真機、Blender-native、私人網站 CDN／登入尚未驗收。','V006 新增 WebGL2、Android 真機、Blender-native、私人網站 CDN／登入尚未驗收；新增道路依凍結 OSM 最後兩段，沒有新建築。')
html=html.replace('以凍結 OSM 道路與建築輪廓擴建的 V004 候選','以凍結 OSM 道路與建築輪廓擴建的 V006 候選')
(DIST/'index.html').write_text(html,encoding='utf8')
qa={'version':'V006-tail-candidate-r1','status':'candidate_static_and_navigation_only_webgl2_not_verified',
 'summary':'V006 自 V005 197.7 m 延伸 33.8 m 至 231.6 m；沿凍結 V002 OSM 最後兩段路線，新增 DEM 貼合道路、不新增建築。V004/V005 舊屋與 B 模型保留；灰量體改為每棟排除都必須有命中，否則停止載入。Chromium WebGL2、Android、Blender-native、私人 CDN 仍未通過。',
 'private_site':'unchanged','blender_native':'not executed','third_person':False}
(DIST/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'V006_PATCHED','old_js_bytes':(ROOT/'baseline/app_v005.js').stat().st_size,'new_js_bytes':len(s),'added_model':1,'masked_buildings_minimum':5},ensure_ascii=False))