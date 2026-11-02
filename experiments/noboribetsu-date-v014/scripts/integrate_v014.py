#!/usr/bin/env python3
"""Create V014 from pristine V013 folder without modifying the source."""
import sys,json,hashlib,shutil
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def run(src,dest,patch):
 src,dest,patch=map(Path,(src,dest,patch)); assert src.is_dir() and not dest.exists()
 d=src/'dist';view=json.loads((d/'scene_view.json').read_text());obj=json.loads(patch.read_text())
 assert 'transition_v013' in view and 'transition_v012' in view and 'terrain_gap_v011' in view
 assert 'v014_center_stones' not in view
 assert obj['schema']=='noboribetsu-date-v014-v004-centre-stones/1' and obj['stone_count']>=35
 assert obj['asset_source']['v004_road_sha256']==sha(d/'assets/v004_merchant_road.glb')
 assert len(obj['positions'])==3*obj['vertices'] and len(obj['colors'])==3*obj['vertices'] and len(obj['indices'])==3*obj['triangles']
 shutil.copytree(src,dest)
 new=dest/'dist';data=patch.read_bytes();(new/'v014_center_stones.json').write_bytes(data)
 view['v014_center_stones']={'schema':obj['schema'],'path':'v014_center_stones.json','sha256':sha(patch),'bytes':len(data),
                             'triangles':obj['triangles'],'vertices':obj['vertices'],'stone_count':obj['stone_count'],
                             'stage':'B','visual_only':True,'collision_changed':False,'author_estimated':True,
                             'v004_road_sha256':obj['asset_source']['v004_road_sha256']}
 (new/'scene_view.json').write_text(json.dumps(view,ensure_ascii=False,indent=2)+'\n')
 function=r'''async function installV014CentreStoneStudy(){
  const c=manifest.v014_center_stones;
  if(!c||c.schema!=='noboribetsu-date-v014-v004-centre-stones/1'||c.stage!=='B'||
    c.visual_only!==true||c.collision_changed!==false||c.author_estimated!==true||
    c.v004_road_sha256!==manifest.extension.models['v004_merchant_road.glb'].sha256)
    throw new Error('V014 路面設計研究版本契約錯誤');
  const raw=await getBuffer(c.path,()=>{});
  if(raw.byteLength!==c.bytes)throw new Error('V014 資料長度不符');
  const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',raw)),x=>x.toString(16).padStart(2,'0')).join('');
  if(digest!==c.sha256)throw new Error('V014 SHA-256 不符');
  const p=JSON.parse(new TextDecoder().decode(raw));
  if(p.schema!==c.schema||p.stone_count!==c.stone_count||p.triangles!==c.triangles||p.vertices!==c.vertices||
    p.positions?.length!==p.vertices*3||p.colors?.length!==p.vertices*3||p.indices?.length!==p.triangles*3||
    [...p.positions,...p.colors,...p.indices].some(x=>!Number.isFinite(x))||
    p.indices.some(x=>!Number.isInteger(x)||x<0||x>=p.vertices))
    throw new Error('V014 中央石板幾何驗證失敗');
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.Float32BufferAttribute(p.positions,3));
  g.setAttribute('color',new THREE.Float32BufferAttribute(p.colors,3));
  g.setIndex(p.indices);g.computeVertexNormals();g.computeBoundingSphere();
  const mat=new THREE.MeshStandardMaterial({vertexColors:true,side:THREE.DoubleSide,roughness:.99,metalness:0,
    polygonOffset:true,polygonOffsetFactor:-1,polygonOffsetUnits:-1});
  const mesh=new THREE.Mesh(g,mat);mesh.name='V014_V004_OPTIONAL_CENTRAL_STONE_STUDY';
  mesh.frustumCulled=true;mesh.castShadow=false;mesh.receiveShadow=true;
  mesh.userData={visualOnly:true,collision:false,source:'photo-informed estimated design; not surveyed'};
  B.add(mesh);
  metrics.v014_center_stones={stones:p.stone_count,triangles:p.triangles,stage:'B',collision_unchanged:true,
     photo_informed_only:true,not_surveyed:true};refreshDiagnostics();
}

'''
 app=new/'app.js';code=app.read_text();anchor='async function installV013SelectiveMerchantShoulder(){'
 assert code.count(anchor)==1, 'V013 function not found';code=code.replace(anchor,function+anchor)
 anchor='await installV013SelectiveMerchantShoulder();';assert code.count(anchor)==1
 code=code.replace(anchor,anchor+'\n    await installV014CentreStoneStudy();')
 code=code.replace('V013 商家街路緣','V014 商家街中央石板設計研究')
 code=code.replace('Noboribetsu_Date_V013_browser_diagnostics.json','Noboribetsu_Date_V014_browser_diagnostics.json')
 toggle="""
$('stoneToggleButton').onclick=()=>{
 const m=B?.getObjectByName('V014_V004_OPTIONAL_CENTRAL_STONE_STUDY');
 if(!m)return;inputEvents.cancel();m.visible=!m.visible;
 $('stoneToggleButton').textContent='中央石板候選 '+(m.visible?'開':'關');
 $('stoneToggleButton').setAttribute('aria-pressed',String(m.visible));
 metrics.v014_center_stones.visible=m.visible;refreshDiagnostics();
};
"""
 anchor="$('reloadButton').onclick=()=>location.reload();"
 assert code.count(anchor)==1
 code=code.replace(anchor,anchor+toggle)
 anchor="$('enterButton').hidden=false;$('load').setAttribute('aria-busy','false');"
 assert code.count(anchor)==1
 code=code.replace(anchor,"$('stoneToggleButton').disabled=false;"+anchor)
 code=code.replace("version:'V013-merchant-edge-candidate-r1'","version:'V014-centre-stone-study-r1'")
 code=code.replace('完整 B 場景與 V011、V012、V013 視覺修補已載入','完整 B 場景與 V011～V014 視覺候選已載入')
 app.write_text(code)
 h=new/'index.html';html=h.read_text()
 html=html.replace('登別伊達時代村 V012 街尾路緣柔化＋保留 V011 補洞與 V010 操控（沿用 V009 外觀）','登別伊達時代村 V014 商家街中央石板候選')
 html=html.replace('V012 街尾路緣柔化＋保留 V011 補洞與 V010 操控（沿用 V009 外觀）','V014 中央石板設計候選（未驗證位置與尺寸）')
 needle='<button disabled id="comfortButton"';assert html.count(needle)==1
 html=html.replace(needle,'<button disabled id="stoneToggleButton" aria-pressed="true" title="設計候選，未驗證實景位置">中央石板候選 開</button>'+needle)
 html=html.replace('V013 候選','V014 候選')
 h.write_text(html)
 q=new/'qa.json';qa=json.loads(q.read_text());qa.update({'version':'V014-centre-stone-study-r1','v014_optional_design':view['v014_center_stones'],
  'v014_status':'candidate_photo_informed_not_verified_paving_location','webgl2_actual':'PENDING_TEST','android':'NOT TESTED','private_site':'NOT TESTED'});q.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
 (dest/'README_V014.md').write_text('# V014｜商家街中央石板候選\n\n照片顯示時代村部分商家街有中央淺色石板；本版為 V004 的可拆除視覺設計候選，未驗證其確切位置與尺寸。\nV011–V013、道路碰撞、正式場景與 A 骨架保持不變。\n不含測試用雜湊替身。\n',encoding='utf8')
 originals={p.relative_to(src).as_posix():sha(p) for p in src.rglob('*') if p.is_file()}
 changed=sorted(k for k,v in originals.items() if sha(dest/k)!=v)
 assert changed==['dist/app.js','dist/index.html','dist/qa.json','dist/scene_view.json'],changed
 report={'base_files':len(originals),'unchanged_files':len(originals)-len(changed),'changed_files':changed,'new_files':sorted(str(p.relative_to(dest)) for p in dest.rglob('*') if p.is_file() and str(p.relative_to(dest)) not in originals)}
 (dest/'V014_delta_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False));return report
if __name__=='__main__':run(*sys.argv[1:])