#!/usr/bin/env python3
"""Add optional porch guide; original V018 runtime only edited inside new V019 working tree."""
from pathlib import Path
import json
root=Path(__file__).resolve().parent/'runtime'/'dist'
p=root/'app.js';s=p.read_text()
def rep(a,b):
 global s
 if s.count(a)!=1:raise RuntimeError('Unique anchor not found: '+a[:60])
 s=s.replace(a,b,1)
rep("const $=id=>document.getElementById(id);","const $=id=>document.getElementById(id);\nlet porchGuideGroup=null,porchGuideData=null,porchGuideEnabled=true;")
s=s.replace("version:'V017-merchant-clearance-audit-r1'","version:'V019-porch-guidance-candidate-r1'")
rep("// V016: 4 sample readings are on two existing 55cm stone plinths, not four independent posts.",'''// V019: 13 non-colliding, source-verified centerline guidance markers near the V004 porch.
// Advisory only: never changes WalkSession, collision or A stage.
async function installV019PorchGuide(){
 const c=manifest.porch_guide_v019;
 if(!c||c.schema!=='noboribetsu-date-v019-porch-centerline-guide/1'||
    c.stage!=='B'||c.default_visible!==true||c.collision_changed!==false||
    c.route_changed!==false||c.warning_not_certification!==true||c.sample_count!==13)
   throw new Error('V019 柱廊導引契約不符');
 const raw=await getBuffer(c.path,()=>{});
 if(raw.byteLength!==c.bytes)throw new Error('V019 導引資料長度不符');
 const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',raw)),x=>x.toString(16).padStart(2,'0')).join('');
 if(hash!==c.sha256)throw new Error('V019 導引資料 SHA-256 不符');
 const d=JSON.parse(new TextDecoder().decode(raw));
 if(d.schema!==c.schema||d.stage!=='B'||d.default_visible!==true||d.B_only!==true||
    d.diagnostic_not_surveyed!==true||d.collision_changed!==false||d.route_changed!==false||
    d.geometry_changed!==false||d.player_radius_m!==.26||d.samples?.length!==13||
    d.source_scene_v018_sha256!==c.source_scene_v018_sha256||
    !d.samples.every((p,i)=>Number.isFinite(p.x)&&Number.isFinite(p.y)&&Number.isFinite(p.z)&&
      Math.abs(p.s_m-(85+1.5*i))<1e-6&&
      Math.sqrt(nearestRoute(manifest.route,p.x,p.z)?.d2??Infinity)<.015))
   throw new Error('V019 導引點與凍結路線不符');
 porchGuideData=d;
 const guide=new THREE.Group();guide.name='V019_PORCH_GUIDANCE_ONLY';
 const geo=new THREE.RingGeometry(.115,.17,14);
 const mat=new THREE.MeshBasicMaterial({color:0x63c4a2,side:THREE.DoubleSide,transparent:true,opacity:.8,depthWrite:false});
 for(const [i,p] of d.samples.entries()){
  const mark=new THREE.Mesh(geo,mat);mark.rotation.x=-Math.PI/2;
  mark.position.set(p.x,p.y+.095,p.z);mark.name='V019_route_center_'+i;
  mark.userData={guide_only:true,collision:false,not_surveyed:true,s_m:p.s_m};guide.add(mark);
 }
 guide.userData={guide_only:true,collision:false,not_a_certified_clearance:true};
 porchGuideGroup=guide;B.add(guide);
 metrics.v019_guide={source_verified:true,markers:13,enabled:true,collision_unchanged:true,route_unchanged:true,scope:'V004 85–103m centerline only; not doorway/accessibility certificate'};
 refreshDiagnostics();
}

// V016: 4 sample readings are on two existing 55cm stone plinths, not four independent posts.''')
rep("  if(v005Facades)v005Facades.visible=false;if(v007Facades)","  if(porchGuideGroup)porchGuideGroup.visible=value==='B'&&porchGuideEnabled;\n  if(v005Facades)v005Facades.visible=false;if(v007Facades)")
rep("  Object.assign($('scene').dataset,{position:",'''  const notice=$('porchGuideNotice');
  if(notice&&porchGuideData){
    const relevant=stage==='B'&&porchGuideEnabled&&near&&near.s>=84.5&&near.s<=105;
    notice.hidden=!relevant;
    if(relevant){
      // Signed horizontal offset from route tangent, not actual measured sidewalk clearance.
      const k=manifest.route.findIndex(p=>p.s>=near.s),a=manifest.route[Math.max(0,k-1)],b=manifest.route[Math.min(manifest.route.length-1,Math.max(1,k))];
      const dx=b.x-a.x,dz=b.z-a.z,len=Math.hypot(dx,dz)||1;
      const signed=(-(dz/len)*(position.x-near.x)+(dx/len)*(position.z-near.z));
      notice.textContent=signed<porchGuideData.lateral_warning_offset_m
        ?'注意：左側靠柱區在模型中可能受阻，請回到中央導引點。'
        :'前方柱廊左側較窄，請參考中央提示點；不是實際店門淨寬保證。';
      notice.dataset.lateralOffsetM=signed.toFixed(3);
    }
  }
  Object.assign($('scene').dataset,{position:''')

rep("    await installV017ClearanceAudit();","    await installV017ClearanceAudit();\n    await installV019PorchGuide();")
rep("$('clearanceToggleButton').disabled=false;$('enterButton').hidden=false;","$('clearanceToggleButton').disabled=false;$('porchGuideToggleButton').disabled=false;$('enterButton').hidden=false;")
rep("$('clearanceToggleButton').onclick=()=>{",'''$('porchGuideToggleButton').onclick=()=>{
 if(!porchGuideGroup||!session)return;
 inputEvents.cancel();porchGuideEnabled=!porchGuideEnabled;
 porchGuideGroup.visible=porchGuideEnabled&&session.stage==='B';
 $('porchGuideToggleButton').textContent='柱廊中央提示 '+(porchGuideEnabled?'開':'關');
 $('porchGuideToggleButton').setAttribute('aria-pressed',String(porchGuideEnabled));
 metrics.v019_guide.enabled=porchGuideEnabled;updateStatus();refreshDiagnostics();
};
$('clearanceToggleButton').onclick=()=>{''')
rep("  $('modeLabel').textContent='第一人稱 · '+stage+' 場景 · V016 石基座高程診斷／保留 V015 的 8 處補強與 V014 石板'","  $('modeLabel').textContent='第一人稱 · '+stage+' 場景 · V019 柱廊導引（僅虛擬路線）／保留 V018 碰撞'")
p.write_text(s)
h=root/'index.html';html=h.read_text();a='<button disabled id="clearanceToggleButton"';assert html.count(a)==1
html=html.replace(a,'<button disabled id="porchGuideToggleButton" aria-pressed="true" title="V004 柱廊中央路線參考；非實際門寬、無障礙或避難通行認證">柱廊中央提示 開</button>'+a)
a='<span id="positionLabel">準備載入</span>';assert html.count(a)==1;html=html.replace(a,a+'<span id="porchGuideNotice" role="status" aria-live="polite" hidden></span>')
html=html.replace('<title>登別伊達時代村 V017','<title>登別伊達時代村 V019')
html=html.replace('V017 路線淨空診斷（中心線與柱子距離，非門口通行認證） R1','V019 柱廊中央導引（模型提示、非現地通行認證） R1')
html=html.replace('V016 候選｜231.6 m 步行路線｜估計外觀，非現地測繪','V019 導引候選｜231.6 m 步行路線｜非現地測繪')
html=html.replace('V016 石基座接地診斷','V019 柱廊中央提示')
h.write_text(html)
css=root/'style.css';css.write_text(css.read_text()+'''\n/* V019: compact, low-contrast opt-in/out guidance; does not block touch controls. */\n#porchGuideNotice{display:block;max-width:340px;font-size:11px;line-height:1.55;color:#355945;border-left:3px solid #63a68f;padding:3px 8px;background:#f2f8eeb8}\n#porchGuideNotice[hidden]{display:none!important}\n@media(max-width:600px){#porchGuideNotice{max-width:210px;font-size:10px}}\n''')
qa=root/'qa.json';data=json.loads(qa.read_text());data.update({'version':'V019-porch-guidance-candidate-r1','v019_status':'B-only guide and warning; full WebGL visual verification pending','v019_scope':'non-colliding centerline markers s 85-103 m; all original geometry/collision preserved','v019_not_egress_or_door_certification':True});qa.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('V019 APP / HTML / CSS / QA integrated')