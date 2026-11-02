#!/usr/bin/env python3
"""Apply V017 clearance diagnostics only to a fresh V016 extracted dist/."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
D=ROOT/'base/dist';O=ROOT/'outputs'
patch=O/'v017_clearance_audit.json';raw=patch.read_bytes();data=json.loads(raw)
assert len(data['markers'])>=3 and data['stage']=='B' and data['default_visible'] is False
scene_path=D/'scene_view.json';scene=json.loads(scene_path.read_text());assert 'clearance_v017' not in scene
for key,digest in data['sources_sha256'].items():
 assert hashlib.sha256((ROOT/'base'/key).read_bytes()).hexdigest()==digest,f'Frozen source changed: {key}'
sha=hashlib.sha256(raw).hexdigest();scene['clearance_v017']={'schema':data['schema'],'path':'v017_clearance_audit.json','sha256':sha,'bytes':len(raw),'stage':'B','default_visible':False,'marker_count':len(data['markers']),'source_scene_sha256':data['sources_sha256']['dist/scene_view.json'],'collision_changed':False,'geometry_changed':False,'doorway_clearance_certified':False,'note':'2D centerline horizontal corridor diagnostics only; source building dimensions are estimated, no interiors.'}
scene_path.write_text(json.dumps(scene,ensure_ascii=False,indent=2)+'\n');(D/'v017_clearance_audit.json').write_bytes(raw)
app_file=D/'app.js';app=app_file.read_text()
func=r'''// V017: measured route-to-OBSTACLE horizontal gap, NOT door or egress certification.
// B-only QA overlay, off by default. Immutable navigation/collision/world materials.
async function installV017ClearanceAudit(){
 const c=manifest.clearance_v017;
 if(!c||c.schema!=='noboribetsu-date-v017-clearance-audit/1'||c.stage!=='B'||
    c.default_visible!==false||c.collision_changed!==false||c.geometry_changed!==false||
    c.source_scene_sha256===undefined||!Number.isInteger(c.marker_count)||c.marker_count<3)
   throw new Error('V017 通行診斷契約不符');
 const raw=await getBuffer(c.path,()=>{});
 if(raw.byteLength!==c.bytes)throw new Error('V017 通行診斷資料長度不符');
 const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',raw)),x=>x.toString(16).padStart(2,'0')).join('');
 if(hash!==c.sha256)throw new Error('V017 通行診斷雜湊不符');
 const d=JSON.parse(new TextDecoder().decode(raw));
 if(d.schema!==c.schema||d.stage!=='B'||d.default_visible!==false||
    d.collision_changed!==false||d.route_changed!==false||d.original_architecture_modified!==false||
    d.markers?.length!==c.marker_count||d.player_radius_m!==0.26||
    !d.summary?.walkable_centerline_pass||d.summary?.minimum_capsule_margin_m<=0||
    !d.markers.every(p=>Number.isFinite(p.x)&&Number.isFinite(p.y)&&Number.isFinite(p.z)&&
      Number.isFinite(p.margin_m)&&p.margin_m>0&&p.margin_m<.55))
   throw new Error('V017 通行量測資料不符');
 const group=new THREE.Group();group.name='V017_CLEARANCE_INSPECTION';
 const mat=new THREE.MeshBasicMaterial({color:0xf2c14b,side:THREE.DoubleSide,transparent:true,opacity:.85,depthWrite:false});
 const geometry=new THREE.RingGeometry(.23,.31,24);
 for(const [i,p] of d.markers.entries()){
  const ring=new THREE.Mesh(geometry,mat);
  ring.rotation.x=-Math.PI/2;ring.position.set(p.x,p.y,p.z);
  ring.name='V017_clearance_'+i;
  ring.userData={diagnostic_only:true,free_horizontal_margin_m:p.margin_m,nearest_obstacle:p.obstacle_id};
  group.add(ring);
 }
 group.visible=false;group.userData={diagnostic_only:true,collision:false,not_egress_certification:true};
 B.add(group);
 metrics.v017_clearance={sample_count:d.summary.sample_count,minimum_capsule_margin_m:d.summary.minimum_capsule_margin_m,
  marker_count:group.children.length,centerline_pass:d.summary.walkable_centerline_pass,
  door_threshold_surveyed:false,collision_changed:false,markers_visible:false,sha_verified:true};
 refreshDiagnostics();
}

'''
anchor='// V016: 4 sample readings are on two existing 55cm stone plinths'
assert app.count(anchor)==1 and 'installV017ClearanceAudit' not in app
app=app.replace(anchor,func+anchor)
anchor='    await installV016FootingInspection();'
assert app.count(anchor)==1
app=app.replace(anchor,anchor+'\n    await installV017ClearanceAudit();')
anchor="$('gradeAuditToggleButton').disabled=false;$('enterButton').hidden=false;"
assert app.count(anchor)==1
app=app.replace(anchor,"$('gradeAuditToggleButton').disabled=false;$('clearanceToggleButton').disabled=false;$('enterButton').hidden=false;")
anchor="$('gradeAuditToggleButton').onclick=()=>{"
assert app.count(anchor)==1
callback='''$('clearanceToggleButton').onclick=()=>{
 const m=B?.getObjectByName('V017_CLEARANCE_INSPECTION');if(!m)return;
 inputEvents.cancel();m.visible=!m.visible;
 $('clearanceToggleButton').textContent='步行淨空診斷 '+(m.visible?'開':'關');
 $('clearanceToggleButton').setAttribute('aria-pressed',String(m.visible));
 metrics.v017_clearance.markers_visible=m.visible;refreshDiagnostics();
};
'''
app=app.replace(anchor,callback+anchor)
app=app.replace("version:'V016-footing-grade-audit-r1'","version:'V017-merchant-clearance-audit-r1'")
app=app.replace('V016 診斷標記預設關閉','V016/V017 診斷標記預設關閉')
app_file.write_text(app)
html_file=D/'index.html';html=html_file.read_text()
anchor='<button disabled id="gradeAuditToggleButton"'
assert html.count(anchor)==1 and 'clearanceToggleButton' not in html
html=html.replace(anchor,'<button disabled id="clearanceToggleButton" aria-pressed="false" title="V004 路線距柱子淨餘距的 2D 檢查點；不是店門淨寬、無障礙或室內通行認證">步行淨空診斷 關</button>'+anchor)
html=html.replace('<title>登別伊達時代村 V016','<title>登別伊達時代村 V017')
html=html.replace('V016 石基座高程診斷（四個取樣點，非四個柱腳） R1','V017 路線淨空診斷（中心線與柱子距離，非門口通行認證） R1')
html_file.write_text(html)
qa_file=D/'qa.json';qa=json.loads(qa_file.read_text());qa['version']='V017-merchant-clearance-audit-r1';qa['v017']={'status':'SOURCE_PASS_BROWSER_QA_PENDING','scope':'V004 merchant street horizontal centerline and porch obstacles; no actual door thresholds verified','sample_count':data['summary']['sample_count'],'closest_margin_m':data['summary']['minimum_capsule_margin_m'],'optional_markers':len(data['markers']),'runtime_assets_modified':False,'collision_changed':False,'no_interior_claim':True,'android':'NOT TESTED','private_site':'NOT TESTED'}
qa_file.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
(D/'README_V017.md').write_text('V017 V004 步行中心線淨空診斷：開關預設關閉。保留 V016 全部模型；不宣稱門檻或室內通行符合規範。\n')
print('V017 integrated:',sha,len(raw),len(data['markers']))