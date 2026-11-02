#!/usr/bin/env python3
"""V016 non-destructive footing-grade inspection overlay; no architecture change.
Requires a fresh V015 Runtime archive and successful build_v016_audit.py.
"""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;D=P/'base/dist';OUT=P/'outputs'
source=json.loads((OUT/'v016_grade_inspection.json').read_text())
assert source['sample_count']==4 and source['stage']=='B' and source['diagnostic_only']
assert not (D/'v016_grade_inspection.json').exists(), 'Refusing to overwrite V016'
scene_file=D/'scene_view.json';scene=json.loads(scene_file.read_text()); assert 'footing_v016' not in scene
raw=(OUT/'v016_grade_inspection.json').read_bytes();sha=hashlib.sha256(raw).hexdigest()
assert scene['grounding_v015']['sha256']==source['source_v015_patch_sha256']
assert scene['extension']['models']['v004_merchant_facades.glb']['sha256']==source['source_facades_sha256']
scene['footing_v016']={'schema':source['schema'],'path':'v016_grade_inspection.json','sha256':sha,'bytes':len(raw),
 'stage':'B','diagnostic_only':True,'sample_count':4,'default_visible':False,'collision_changed':False,
 'original_geometry_modified':False,'source_facades_sha256':source['source_facades_sha256'],
 'source_v015_patch_sha256':source['source_v015_patch_sha256'],
 'notes':'4 readings on 2 continuous stone plinths, visual exposure 44.2-48.8cm; use optional markers for human review. No new footing repair.'}
scene_file.write_text(json.dumps(scene,ensure_ascii=False,indent=2)+'\n')
(D/'v016_grade_inspection.json').write_bytes(raw)
code_file=D/'app.js';code=code_file.read_text()
func=r'''// V016: 4 sample readings are on two existing 55cm stone plinths, not four independent posts.
// Optional B-only QA markers; disabled by default and have no collision or architectural effect.
async function installV016FootingInspection(){
 const c=manifest.footing_v016;
 if(!c||c.schema!=='noboribetsu-date-v016-grade-inspection/1'||c.stage!=='B'||
    c.diagnostic_only!==true||c.default_visible!==false||c.sample_count!==4||
    c.original_geometry_modified!==false||c.collision_changed!==false||
    c.source_facades_sha256!==manifest.extension.models['v004_merchant_facades.glb'].sha256||
    c.source_v015_patch_sha256!==manifest.grounding_v015.sha256)
   throw new Error('V016 基座來源契約不符');
 const raw=await getBuffer(c.path,()=>{});
 if(raw.byteLength!==c.bytes)throw new Error('V016 診斷資料長度不符');
 const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',raw)),b=>b.toString(16).padStart(2,'0')).join('');
 if(digest!==c.sha256)throw new Error('V016 診斷資料雜湊不符');
 const d=JSON.parse(new TextDecoder().decode(raw));
 if(d.schema!==c.schema||d.stage!=='B'||d.sample_count!==4||d.diagnostic_only!==true||
    d.default_visible!==false||d.original_geometry_modified!==false||
    d.source_facades_sha256!==c.source_facades_sha256||
    d.source_v015_patch_sha256!==c.source_v015_patch_sha256||
    !Array.isArray(d.burial_samples)||d.burial_samples.length!==4||
    d.burial_samples.some(p=>!Number.isFinite(p.x)||!Number.isFinite(p.z)||!Number.isFinite(p.marker_y)||
      !(p.burial_depth_m>.04&&p.burial_depth_m<.12)||p.remaining_exposed_height_m<.4||
      (p.continuous_plinth_block!==0&&p.continuous_plinth_block!==1)))
   throw new Error('V016 基座診斷數值無效');
 const group=new THREE.Group();group.name='V016_GRADE_INSPECTION_MARKERS';
 const mat=new THREE.MeshBasicMaterial({color:0xe3ac40,transparent:true,opacity:.9,
   side:THREE.DoubleSide,depthWrite:false});
 for(const [i,p] of d.burial_samples.entries()){
   const ring=new THREE.Mesh(new THREE.RingGeometry(.27,.35,32),mat);
   ring.rotation.x=-Math.PI/2;ring.position.set(p.x,p.marker_y,p.z);
   ring.name='V016_grade_sample_'+i;ring.userData={inspectionOnly:true,burial_m:p.burial_depth_m};group.add(ring);
 }
 group.visible=false;group.userData={inspectionOnly:true,collision:false,surveyed:false};B.add(group);
 metrics.v016_inspection={sample_count:4,continuous_plinths:2,
   original_plinths_unchanged:true,unresolved_burial_samples:4,markers_visible:false,
   source_authenticated:true,no_new_repair_geometry:true};refreshDiagnostics();
}

'''
anchor='// V015: reversible visual-only underfoot stone sleeves'
assert code.count(anchor)==1 and 'installV016FootingInspection' not in code
code=code.replace(anchor,func+anchor)
anchor='    await installV015PostGrounding();';assert code.count(anchor)==1
code=code.replace(anchor,anchor+'\n    await installV016FootingInspection();')
anchor="$('stoneToggleButton').disabled=false;$('footingToggleButton').disabled=false;$('enterButton').hidden=false;"
assert code.count(anchor)==1
code=code.replace(anchor,"$('stoneToggleButton').disabled=false;$('footingToggleButton').disabled=false;$('gradeAuditToggleButton').disabled=false;$('enterButton').hidden=false;")
anchor="$('footingToggleButton').onclick=()=>{"
assert code.count(anchor)==1
code=code.replace(anchor,"""$('gradeAuditToggleButton').onclick=()=>{
 const m=B?.getObjectByName('V016_GRADE_INSPECTION_MARKERS');if(!m)return;
 inputEvents.cancel();m.visible=!m.visible;
 $('gradeAuditToggleButton').textContent='基座取樣診斷 '+(m.visible?'開':'關');
 $('gradeAuditToggleButton').setAttribute('aria-pressed',String(m.visible));
 metrics.v016_inspection.markers_visible=m.visible;refreshDiagnostics();
};
"""+anchor)
code=code.replace('V015-porch-foot-grounding-r1','V016-footing-grade-audit-r1')
code=code.replace('V015 V004 柱腳接地候選（8 處）／保留 V014 石板、V011 地形補洞與 V012～013 路緣','V016 石基座高程診斷／保留 V015 的 8 處補強與 V014 石板')
code=code.replace('V011～V015 視覺候選已載入','V011～V015 視覺候選已載入；V016 診斷標記預設關閉')
code_file.write_text(code)
html_file=D/'index.html';html=html_file.read_text()
anchor='<button disabled id="footingToggleButton"';assert html.count(anchor)==1 and 'gradeAuditToggleButton' not in html
html=html.replace(anchor,'<button disabled id="gradeAuditToggleButton" aria-pressed="false" title="只標示兩條連續石基座的四個高程取樣點；不是四個獨立柱腳，也不修復原始幾何">基座取樣診斷 關</button>'+anchor)
html=html.replace('<title>登別伊達時代村 V015','<title>登別伊達時代村 V016')
html=html.replace('V015 V004 柱腳接地候選（實測模型差，非現地測量） R1','V016 石基座高程診斷（四個取樣點，非四個柱腳） R1')
html=html.replace('V015 候選｜231.6 m','V016 候選｜231.6 m')
html_file.write_text(html)
qa_file=D/'qa.json';qa=json.loads(qa_file.read_text());qa['version']='V016-footing-grade-audit-r1';qa['v016']={
  'scope':'Grade-only diagnostics: four samples along two continuous 0.55m plinths',
  'status':'candidate_diagnostic_only','visible_when_entered':False,'buildings_transformed':False,
  'v015_eight_underfoot_supports_unchanged':True,'no_new_plinth_fixes':True,
  'original_collision_unchanged':True,'webgl_test':'pending'}
qa_file.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
print('V016 integrated, bytes',len(raw),'sha',sha)