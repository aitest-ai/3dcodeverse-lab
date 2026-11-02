#!/usr/bin/env python3
"""Non-destructive V015 runtime patch against exact V014 dist. 4 edited paths; 1 new JSON."""
import hashlib,json,shutil
from pathlib import Path
P=Path(__file__).resolve().parent;D=P/'base/dist';OUT=P/'outputs'
assert not (D/'v015_post_grounding.json').exists(), 'Use a fresh V014 extraction for each replay'
raw=(OUT/'v015_post_grounding.json').read_bytes();obj=json.loads(raw)
assert obj['support_count']==8 and obj['triangles']==96 and obj['vertices']==64
sha=hashlib.sha256(raw).hexdigest()
scene_path=D/'scene_view.json';scene=json.loads(scene_path.read_text())
assert 'grounding_v015' not in scene
assert scene['v014_center_stones']['stone_count']==50
scene['grounding_v015']={'schema':obj['schema'],'path':'v015_post_grounding.json','sha256':sha,'bytes':len(raw),'stage':'B','support_count':8,'vertices':64,'triangles':96,'visual_only':True,'collision_changed':False,'route_changed':False,'author_estimated':True,'source_facades_sha256':obj['source_facades_sha256'],'source_road_sha256':obj['source_road_sha256'],'known_unfixed_buried_posts':4,'provenance':'V004 visible road+terrain vs existing post stone lower face; not measured; eight floating posts only'}
scene_path.write_text(json.dumps(scene,ensure_ascii=False,indent=2)+'\n')
(D/'v015_post_grounding.json').write_bytes(raw)
code_path=D/'app.js';s=code_path.read_text()
func='''// V015: reversible visual-only underfoot stone sleeves for eight audited V004 floating porch feet.
// Do not alter original V004 geometry, roads, collision, or A stage.
async function installV015PostGrounding(){
 const c=manifest.grounding_v015;
 if(!c||c.schema!=='noboribetsu-date-v015-v004-porch-foot-grounding/1'||c.stage!=='B'||
    c.visual_only!==true||c.collision_changed!==false||c.route_changed!==false||c.author_estimated!==true||
    c.support_count!==8||c.vertices!==64||c.triangles!==96||
    c.source_road_sha256!==manifest.extension.models['v004_merchant_road.glb'].sha256||
    c.source_facades_sha256!==manifest.extension.models['v004_merchant_facades.glb'].sha256)
   throw new Error('V015 柱腳來源與版本契約不符');
 const raw=await getBuffer(c.path,()=>{});
 if(raw.byteLength!==c.bytes)throw new Error('V015 資料長度不符');
 const actual=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',raw)),x=>x.toString(16).padStart(2,'0')).join('');
 if(actual!==c.sha256)throw new Error('V015 柱腳補強 SHA-256 不符');
 const p=JSON.parse(new TextDecoder().decode(raw));
 if(p.schema!==c.schema||p.stage!=='B'||p.visual_only!==true||p.collision_changed!==false||p.route_changed!==false||
    p.source_road_sha256!==c.source_road_sha256||p.source_facades_sha256!==c.source_facades_sha256||
    p.support_count!==8||p.supports?.length!==8||p.triangles!==96||p.vertices!==64||
    p.positions?.length!==192||p.colors?.length!==192||p.indices?.length!==288||
    [...p.positions,...p.colors,...p.indices].some(v=>!Number.isFinite(v))||
    p.indices.some(v=>!Number.isInteger(v)||v<0||v>=64))
   throw new Error('V015 柱腳補強內容無效');
 const geometry=new THREE.BufferGeometry();
 geometry.setAttribute('position',new THREE.Float32BufferAttribute(p.positions,3));
 geometry.setAttribute('color',new THREE.Float32BufferAttribute(p.colors,3));
 geometry.setIndex(p.indices);geometry.computeVertexNormals();geometry.computeBoundingSphere();
 const material=new THREE.MeshStandardMaterial({vertexColors:true,roughness:1,metalness:0,side:THREE.DoubleSide});
 const mesh=new THREE.Mesh(geometry,material);mesh.name='V015_V004_POST_GROUNDING_VISUAL_ONLY';
 mesh.castShadow=false;mesh.receiveShadow=true;mesh.userData={visualOnly:true,collision:false,notSurveyed:true};
 B.add(mesh);
 metrics.v015_grounding={support_count:8,triangles:96,stage:'B',collision_unchanged:true,unresolved_buried_posts:4,visible:true};
 refreshDiagnostics();
}

'''
anchor='async function installV014CentreStoneStudy(){'
assert s.count(anchor)==1 and 'async function installV015PostGrounding' not in s
s=s.replace(anchor,func+anchor)
anchor='    await loadV004Extension();'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'\n    await installV015PostGrounding();')
anchor="    $('stoneToggleButton').disabled=false;$('enterButton').hidden=false;"
assert s.count(anchor)==1
s=s.replace(anchor,"    $('stoneToggleButton').disabled=false;$('footingToggleButton').disabled=false;$('enterButton').hidden=false;")
anchor="$('aButton').onclick=async()=>"
assert s.count(anchor)==1
s=s.replace(anchor,"""$('footingToggleButton').onclick=()=>{
 const m=B?.getObjectByName('V015_V004_POST_GROUNDING_VISUAL_ONLY');
 if(!m)return;inputEvents.cancel();m.visible=!m.visible;
 $('footingToggleButton').textContent='柱腳接地候選 '+(m.visible?'開':'關');
 $('footingToggleButton').setAttribute('aria-pressed',String(m.visible));
 metrics.v015_grounding.visible=m.visible;refreshDiagnostics();
};
"""+anchor)
s=s.replace("V014-centre-stone-study-r1","V015-porch-foot-grounding-r1")
s=s.replace('V014 商家街中央石板設計研究補強／保留 V011 補洞與 V012 路緣','V015 V004 柱腳接地候選（8 處）／保留 V014 石板、V011 地形補洞與 V012～013 路緣')
s=s.replace('V011～V014 視覺候選已載入','V011～V015 視覺候選已載入')
code_path.write_text(s)
h=D/'index.html';html=h.read_text();assert 'footingToggleButton' not in html
html=html.replace('<title>登別伊達時代村 V014','<title>登別伊達時代村 V015')
html=html.replace('V014 中央石板設計候選（未驗證位置與尺寸） R1','V015 V004 柱腳接地候選（實測模型差，非現地測量） R1')
anchor='<button disabled id="stoneToggleButton"'
assert html.count(anchor)==1
html=html.replace(anchor,'<button disabled id="footingToggleButton" aria-pressed="true" title="僅修補 8 處懸空柱腳，仍有 4 處埋入待人工處理">柱腳接地候選 開</button>'+anchor)
html=html.replace('V014 候選｜231.6 m','V015 候選｜231.6 m')
h.write_text(html)
q=D/'qa.json';qa=json.loads(q.read_text());qa['version']='V015-porch-foot-grounding-r1'
qa['v015']={'scope':'8 floating V004 porch posts only','source':'V004 real road triangle heights, V002 frozen terrain','remaining_buried_posts':4,'models_untouched':True,'collision_untouched':True,'visual_not_surveyed':True,'browser_test':'pending'}
q.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
print('V015 integrated; patch',len(raw),'sha256',sha)