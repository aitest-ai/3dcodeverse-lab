#!/usr/bin/env node
// Halows V12: reproducible OSM-centerline geometry preflight. NOT cycling navigation.
// Source lock prevents accidental route regression and prohibits inferred ferry links.
import fs from "node:fs";
import path from "node:path";
import {createHash} from "node:crypto";
import {fileURLToPath} from "node:url";
function auditSite(s){
  function check(ok,msg){if(!ok)throw new Error("V12_AUDIT_ERROR: "+msg);}
  check(s.asset_id==="halows-mukaishima-v09-geosite","incorrect snapshot ID");
  check(s.building.osm_way_id==="661155704","Halows footprint changed");
  check(Array.isArray(s.roads)&&s.roads.length===4,"road snapshot coverage changed");
  const nodes=new Map(),adj=new Map(),edges=[],classes=new Set();
  for(const w of s.roads){
    check(["trunk","tertiary","service"].includes(w.tags.highway),"unreviewed road class");
    check(Array.isArray(w.points)&&w.points.length>=2,"road polyline missing");
    classes.add(w.tags.highway);
    for(const p of w.points){
      check(typeof p.node_id==="string"&&Number.isFinite(p.x)&&Number.isFinite(p.y)&&Number.isFinite(p.elev_m),"invalid node");
      const old=nodes.get(p.node_id);
      if(old)check(Math.hypot(old.x-p.x,old.y-p.y,old.elev_m-p.elev_m)<0.06,"conflicting duplicate node "+p.node_id);
      else{nodes.set(p.node_id,p);adj.set(p.node_id,[]);}
    }
  }
  for(const w of s.roads)for(let i=1;i<w.points.length;i++){
    const a=w.points[i-1],b=w.points[i],len=Math.hypot(a.x-b.x,a.y-b.y);
    check(len>0.01,"degenerate edge "+w.osm_way_id);
    const e={way_id:w.osm_way_id,road_class:w.tags.highway,from:a.node_id,to:b.node_id,length_m:len,dem_endpoint_grade_fraction:Math.abs(a.elev_m-b.elev_m)/len};
    edges.push(e);adj.get(a.node_id).push({id:b.node_id,e});adj.get(b.node_id).push({id:a.node_id,e});
  }
  const unseen=new Set(nodes.keys()),components=[];
  while(unseen.size){
    const start=unseen.values().next().value,stack=[start],group=[];
    unseen.delete(start);
    while(stack.length){const n=stack.pop();group.push(n);for(const a of adj.get(n))if(unseen.delete(a.id))stack.push(a.id);}
    components.push(group.length);
  }
  function shortest(start,goal){
    check(nodes.has(start)&&nodes.has(goal),"anchor not on snapped road graph");
    const costs=new Map([[start,0]]),prev=new Map(),fixed=new Set();
    while(true){
      let best=null,cost=Infinity;
      for(const [n,d] of costs)if(!fixed.has(n)&&d<cost){best=n;cost=d;}
      if(best===null||best===goal)break;
      fixed.add(best);
      for(const {id,e} of adj.get(best))if(cost+e.length_m<(costs.get(id)??Infinity)){
        costs.set(id,cost+e.length_m);prev.set(id,{from:best,road_class:e.road_class,way_id:e.way_id});
      }
    }
    if(!costs.has(goal))return null;
    const path=[goal],classes=[],ways=[];let at=goal;
    while(at!==start){const p=prev.get(at);check(!!p,"shortest path backtrack failed");classes.push(p.road_class);ways.push(p.way_id);at=p.from;path.push(at);}
    path.reverse();
    return {distance_m:+costs.get(goal).toFixed(1),node_ids:path,road_classes:[...new Set(classes)],way_ids:[...new Set(ways)],status:"OSM_CENTERLINE_ONLY_NOT_BICYCLE_ROUTE"};
  }
  function euclidToFootprint(p){
    const fp=s.building.footprint;let closest=Infinity;
    for(let i=0;i<fp.length;i++){
      const a=fp[i],b=fp[(i+1)%fp.length],vx=b.x-a.x,vy=b.y-a.y;
      const t=Math.max(0,Math.min(1,((p.x-a.x)*vx+(p.y-a.y)*vy)/(vx*vx+vy*vy)));
      closest=Math.min(closest,Math.hypot(p.x-(a.x+t*vx),p.y-(a.y+t*vy)));
    }
    return +closest.toFixed(1);
  }
  const anchors=s.access_points,center=anchors.tajiri_west.osm_node_id;
  const paths={};
  for(const [label,key] of [["south","south_service_access"],["east","east_service_access"]]){
    const p=anchors[key];check(nodes.has(p.osm_node_id),"missing "+key);
    paths[label]={label:key,from:"tajiri_west",...shortest(center,p.osm_node_id),straight_line_to_building_outline_m:euclidToFootprint(p)};
  }
  check(components.length===1,"local OSM way graph is split");
  check(paths.south&&paths.east,"local access segments not connected");
  return {
    schema_version:1,asset_id:"halows-mukaishima-v12-route-audit",
    snapshot_id:s.asset_id,osm_way_building:s.building.osm_way_id,
    origin_wgs84:s.origin_wgs84,
    source_v09_git_blob:"a4af2bae722236664297cab363099e4b4dce498b",
    status:"LOCAL_CENTERLINES_CONNECTED__CYCLING_NOT_APPROVED",
    counts:{road_ways:s.roads.length,unique_nodes:nodes.size,edges:edges.length,components:components.length,component_sizes:components,road_types:[...classes].sort(),centerline_length_m:+edges.reduce((z,e)=>z+e.length_m,0).toFixed(1),max_dem_endpoint_grade_fraction:+Math.max(...edges.map(e=>e.dem_endpoint_grade_fraction)).toFixed(4)},
    anchor_paths:paths,
    approval_gates:{
      local_osm_centerlines_connected:true,
      store_door_geolocated:false,
      curb_cuts_field_verified:false,
      legal_bicycle_access_verified:false,
      ferry_to_store_connected:false,
      person_bicycle_collision_tested:false,
      browser_android_tested:false,
      full_3d_runtime_integrated:false
    },
    cautions:[
      "Only 4 OSM road ways near Halows; NOT a ferry-to-store or island-wide navigation graph.",
      "A common OSM node is a centerline junction, not proof of curb cut, crossing, safety or legal bicycle access.",
      "Route 317 is tagged trunk in the locked snapshot; do not silently approve cycling on that segment.",
      "Distance to the building outline is a straight-line geometry gap, not a door or accessible walking route.",
      "DEM endpoints and 20m visualization subsampling do not certify rideable grades, lane width or pavement.",
      "Halows official parking flow depicts vehicle movements and must not be used as a cycling route.",
      "Site geometry reflects a 2026-10-31 OSM snapshot and historical storefront references; no live field inspection."
    ],
    official_guidance:"https://www.jb-honshi.co.jp/english/shimanamicycling/howto/index02.html",
    halows_official:"https://www.halows.com/stores/detail/77",
    report_kind:"reproducible_geometric_preflight_not_gameplay_or_navigation"
  };
}
function makeViewer(s,r){
 const esc=(v)=>String(v).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
 const colors={trunk:"#b45446",tertiary:"#dba04d",service:"#4b8990"};
 const coords=(p)=>p.x.toFixed(2)+","+(-p.y).toFixed(2);
 const roadShapes=s.roads.map(w=>'<polyline points="'+w.points.map(coords).join(" ")+'" fill="none" stroke="'+colors[w.tags.highway]+'" stroke-width="'+(w.tags.highway==="trunk"?5:3.5)+'" stroke-linecap="round" stroke-linejoin="round"><title>OSM way '+esc(w.osm_way_id)+' / '+esc(w.tags.highway)+'</title></polyline>').join("\n");
 const polygon='<polygon points="'+s.building.footprint.map(coords).join(" ")+'" fill="#d3a79d" fill-opacity=".83" stroke="#805149" stroke-width="2.5"><title>Halows A棟（OSM 661155704），非測量竣工圖</title></polygon>';
 const anchors=[["tajiri_west","田尻西", "#394e65"],["south_service_access","南側接點","#287b80"],["east_service_access","東側接點","#47796a"]].map(([key,label,color])=>{const p=s.access_points[key];const dx=key==="south_service_access"?-6:7;const dy=key==="south_service_access"?-16:key==="tajiri_west"?-15:-9;const align=key==="south_service_access"?"end":"start";return '<circle cx="'+p.x+'" cy="'+(-p.y)+'" r="5.7" fill="'+color+'" stroke="white" stroke-width="2"/><text x="'+(p.x+dx)+'" y="'+(-p.y+dy)+'" text-anchor="'+align+'" font-size="10.5" font-weight="700" fill="#203c4a">'+label+'</text>';}).join("");
 const points=new Map();for(const w of s.roads)for(const p of w.points)points.set(p.node_id,p);
 const overlays=Object.entries(r.anchor_paths).map(([key,route])=>'<polyline id="route-'+key+'" class="route" points="'+route.node_ids.map(id=>coords(points.get(id))).join(" ")+'" fill="none" stroke="'+(key==="south"?"#aa4641":"#207a9b")+'" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" opacity=".85"/>').join("");
 const reportJson=esc(JSON.stringify(r,null,2));
 return `<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Halows 向島店 V12 道路連通審查</title>
<style>body{margin:0;background:#f7f5f0;color:#2e3c42;font:16px/1.55 system-ui,"Noto Sans TC",sans-serif}.shell{max-width:1100px;margin:auto;padding:26px 18px}h1{font-size:clamp(23px,3vw,34px);line-height:1.3;margin:0 0 8px}p{margin:10px 0}.sub{color:#61737a}.notice{border-left:5px solid #ad6848;background:#f7ece5;padding:14px 18px;border-radius:8px;margin:20px 0}.panel{background:#fff;border:1px solid #e4e0d9;border-radius:16px;padding:20px;box-shadow:0 3px 22px #132e3210}.map{overflow:hidden;border-radius:12px;background:#edf1ec}.map svg{display:block;width:100%;max-height:560px}.controls{display:flex;flex-wrap:wrap;gap:10px;margin:15px 0}.controls button{background:#f1f5f4;border:1px solid #b8c9c7;border-radius:50px;padding:10px 15px;color:#234f52;font-weight:700;cursor:pointer}.controls button:focus,.controls button:hover{background:#dcece8}.route{display:none}body[data-route="south"] #route-south,body[data-route="east"] #route-east{display:block}.legend{display:flex;flex-wrap:wrap;gap:17px;font-size:14px}.dot{display:inline-block;width:17px;height:5px;vertical-align:middle;margin-right:5px;border-radius:4px}.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}.fact{border-radius:10px;background:#f1f4f1;padding:12px 15px}.fact b{display:block;font-size:24px}.foot{font-size:13px;color:#53636a;margin-top:16px}details{margin-top:20px}pre{max-height:360px;overflow:auto;font-size:12px;background:#f3f5f5;padding:15px;border-radius:10px}a{color:#285f77}</style></head>
<body data-route="none"><main class="shell"><h1>瀨戶內騎行世界｜Halows V12 道路連通審查</h1><p class="sub">2026/10/31 OSM 固定快照 · ENU 局部座標（公尺） · 不需網路即可開啟</p><div class="notice"><strong>尚未核准自行車導航。</strong> 下方標亮的是 OSM 道路中心線的幾何最短路徑，不代表可以合法、安全騎乘或由渡船碼頭連通。建築輪廓不是實測門位。</div>
<section class="panel"><div class="facts"><div class="fact">道路線群<b>${r.counts.road_ways}</b></div><div class="fact">節點<b>${r.counts.unique_nodes}</b></div><div class="fact">連通群數<b>${r.counts.components}</b></div><div class="fact">幾何總長<b>${r.counts.centerline_length_m} m</b></div></div>
<div class="controls"><button type="button" data-route="south">田尻西 → 南側 ${r.anchor_paths.south.distance_m}m</button><button type="button" data-route="east">田尻西 → 東側 ${r.anchor_paths.east.distance_m}m</button><button type="button" data-route="none">清除標亮</button></div>
<div class="map"><svg viewBox="-220 -185 440 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Halows 附近四條 OSM 道路與建築輪廓示意圖"><rect x="-220" y="-185" width="440" height="360" fill="#ecf0ec"/><g stroke="#d4ded7" stroke-width=".5">${Array.from({length:9},(_,i)=>'<path d="M '+(-200+i*50)+' -185 V 175 M -220 '+(-170+i*40)+' H 220"/>').join("")}</g>${roadShapes}${polygon}${overlays}${anchors}</svg></div>
<p class="legend"><span><i class="dot" style="background:${colors.trunk}"></i>國道 317（trunk）</span><span><i class="dot" style="background:${colors.tertiary}"></i>主要道路（tertiary）</span><span><i class="dot" style="background:${colors.service}"></i>店區道路（service）</span><span><i class="dot" style="background:#d3a79d"></i>OSM 建築輪廓</span></p>
<p class="foot">上方 Y 軸依 ENU 定義向北；道路幾何不等於騎行路權。南側路徑涉及國道 317，尤其必須核對現地安全與法規。東西橋與渡船接續未在本份資料內，不能自動外推。</p>
<details><summary>查看完整 QA 記錄與尚未通過的驗收門檻</summary><pre>${reportJson}</pre></details></section>
<p class="foot">資料來源：<a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">© OpenStreetMap contributors（ODbL）</a>、既有 V09 GSI DEM 快照；<a href="${r.halows_official}" target="_blank" rel="noopener">Halows 官方店面參考</a>；<a href="${r.official_guidance}" target="_blank" rel="noopener">島波海道官方騎行指引</a>。本圖為內部 QA，不是現地測量或導航服務。</p></main>
<script>document.querySelectorAll('button[data-route]').forEach(b=>b.addEventListener('click',()=>{document.body.dataset.route=b.dataset.route;}));</script></body></html>`;
}
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../..");
const SOURCE=path.join(ROOT,"scripts/blender5/halows_site_v09_data.py");
const raw=fs.readFileSync(SOURCE);
const blob=createHash("sha1").update("blob "+raw.length).update(Buffer.from([0])).update(raw).digest("hex");
if(blob!=="a4af2bae722236664297cab363099e4b4dce498b")throw Error("Locked V09 site source changed; stop for human review: "+blob);
const sourceText=raw.toString("utf8");
const marker="SITE_DATA=r'''";
const start=sourceText.indexOf(marker),end=start<0?-1:sourceText.indexOf("'''",start+marker.length);
if(start<0||end<=start)throw Error("Cannot extract V09 site snapshot");
const site=JSON.parse(sourceText.slice(start+marker.length,end));
const report=auditSite(site);
if(report.counts.unique_nodes!==39||report.counts.edges!==39||report.counts.components!==1)throw Error("Unexpected V09 graph topology");
if(report.anchor_paths.south.distance_m!==66.5||report.anchor_paths.east.distance_m!==61.5)throw Error("Known anchor distance changed");
if(Object.values(report.approval_gates).filter(Boolean).length!==1||report.approval_gates.ferry_to_store_connected)throw Error("Unsafe route approval regression");
const html=makeViewer(site,report);
if(!html.includes('尚未核准自行車導航')||!html.includes('data-route="south"'))throw Error("Preview disclaimer or route UI missing");
if(process.argv.includes("--write")){
  const dir=path.join(ROOT,"outputs/halows-v12-route-audit");fs.mkdirSync(dir,{recursive:true});
  fs.writeFileSync(path.join(dir,"report.json"),JSON.stringify(report,null,2)+String.fromCharCode(10));
  fs.writeFileSync(path.join(dir,"route-preview.html"),html);
}
console.log(JSON.stringify({status:"V12_PREFLIGHT_PASS_NOT_NAVIGATION",nodes:report.counts.unique_nodes,edges:report.counts.edges,connected_components:report.counts.components,south_m:report.anchor_paths.south.distance_m,east_m:report.anchor_paths.east.distance_m,write:process.argv.includes("--write")},null,2));
