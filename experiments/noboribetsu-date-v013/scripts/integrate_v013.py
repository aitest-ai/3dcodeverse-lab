#!/usr/bin/env python3
"""Integrate V013 outside V012's frozen runtime; never overwrite existing versions."""
import sys,hashlib,json,shutil
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def go(source:Path,out:Path,overlay:Path):
 if out.exists():raise FileExistsError('Refuse to overwrite: '+str(out))
 source=Path(source);out=Path(out);overlay=Path(overlay)
 dist=source/'dist';orig_manifest=json.loads((dist/'scene_view.json').read_text())
 frozen={'dist/assets/v004_merchant_road.glb':'d766bbf2b8a7df403b0b76f1c618f1f9ba2796eb4197d2df574fc4de5e58c81d',
 'dist/assets/v005_east_road.glb':'acd6307cc3970bc628e6925167aa6f911c8036f299dc0338a9f5e1d0ebff2982',
 'dist/v012_road_grass_transition.json':'fee891da9536ba155e8fd00d560629da7ed6c9e88de0e1b29f38faf598059704',
 'dist/v011_terrain_gap_patch.json':'71f541341123354025d81e740f3bc55bbbf70e02634236e33be7e61bed77cf64'}
 for filename,expected in frozen.items():
  if sha(source/filename)!=expected:raise RuntimeError('Frozen source changed: '+filename)
 if 'transition_v013' in orig_manifest:raise RuntimeError('V013 applied already')
 obj=json.loads(overlay.read_bytes());tri=obj['triangles'];vert=obj['vertices'];data=overlay.read_bytes();digest=hashlib.sha256(data).hexdigest()
 assert obj['schema']=='noboribetsu-date-v013-adaptive-merchant-shoulder/1' and tri==2436 and vert==1688
 assert obj['collision_enabled'] is False and len(obj['positions'])==vert*3 and len(obj['colors'])==vert*4 and len(obj['indices'])==tri*3
 shutil.copytree(source,out)
 newdist=out/'dist';(newdist/'v013_selective_road_grass.json').write_bytes(data)
 manifest=json.loads((newdist/'scene_view.json').read_text());manifest['transition_v013']={
  'schema':obj['schema'],'path':'v013_selective_road_grass.json','sha256':digest,'bytes':len(data),
  'triangles':tri,'vertices':vert,'stage':'B','visual_only':True,'collision_changed':False,
  'v011_terrain_patch_untouched':True,'v012_transition_untouched':True,
  'source_v004_road_sha256':frozen['dist/assets/v004_merchant_road.glb'],
  'source_v005_road_sha256':frozen['dist/assets/v005_east_road.glb'],
  'provenance':'Author-estimated V004/V005 edge tint only outside preserved curb/stone/architecture; not surveyed.'}
 (newdist/'scene_view.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 code=f'''async function installV013SelectiveMerchantShoulder(){{
  const c=manifest.transition_v013;
  if(!c||c.schema!=='noboribetsu-date-v013-adaptive-merchant-shoulder/1'||
     c.stage!=='B'||c.triangles!==2436||c.vertices!==1688||
     c.visual_only!==true||c.collision_changed!==false||
     c.source_v004_road_sha256!==manifest.extension.models['v004_merchant_road.glb'].sha256||
     c.source_v005_road_sha256!==manifest.extension_v005.models['v005_east_road.glb'].sha256)
    throw new Error('V013 路緣來源版本不符，已停止載入');
  const raw=await getBuffer(c.path,()=>{{}});
  if(raw.byteLength!==c.bytes)throw new Error('V013 資料長度錯誤');
  const actual=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',raw)),n=>n.toString(16).padStart(2,'0')).join('');
  if(actual!==c.sha256)throw new Error('V013 資料 SHA-256 不符');
  const p=JSON.parse(new TextDecoder().decode(raw));
  if(p.schema!==c.schema||p.stage!=='B'||p.collision_enabled!==false||
     p.triangles!==2436||p.vertices!==1688||
     p.positions?.length!==5064||p.colors?.length!==6752||p.indices?.length!==7308||
     [...p.positions,...p.colors,...p.indices].some(n=>!Number.isFinite(n))||
     p.indices.some(n=>n<0||n>=p.vertices||!Number.isInteger(n)))
    throw new Error('V013 補強模型內容無效');
  const geo=new THREE.BufferGeometry();
  geo.setAttribute('position',new THREE.Float32BufferAttribute(p.positions,3));
  geo.setAttribute('color',new THREE.Float32BufferAttribute(p.colors,4));
  geo.setIndex(p.indices);geo.computeVertexNormals();geo.computeBoundingSphere();
  const mat=new THREE.MeshStandardMaterial({{vertexColors:true,transparent:true,
    side:THREE.DoubleSide,depthWrite:false,roughness:1,metalness:0,
    polygonOffset:true,polygonOffsetFactor:-1,polygonOffsetUnits:-1}});
  const mesh=new THREE.Mesh(geo,mat);mesh.name='V013_V004_V005_MERCHANT_SELECTIVE_EDGE_VISUAL';
  mesh.frustumCulled=true;mesh.renderOrder=6;mesh.castShadow=false;mesh.receiveShadow=true;
  mesh.userData={{version:'V013',visualOnly:true,collision:false,triangles:p.triangles,
    provenance:'frozen V002 GSI + original V004/V005 roads; estimated non-surveyed visual fade'}};
  B.add(mesh);
  metrics.v013_road_grass={{triangles:p.triangles,vertices:p.vertices,sections:p.parts.map(v=>({{name:v.section,triangles:v.triangles}})),
    stage:'B',collision_unchanged:true,route_unchanged:true,v011_gap_untouched:true,v012_fade_untouched:true}};
  refreshDiagnostics();
}}

'''
 app=newdist/'app.js';s=app.read_text();needle='async function installV012RoadGrassFade(){'
 if s.count(needle)!=1:raise RuntimeError('V012 insertion point unexpected')
 s=s.replace(needle,code+needle)
 needle='await installV012RoadGrassFade();'
 if s.count(needle)!=1:raise RuntimeError('V012 call unexpected')
 s=s.replace(needle,needle+'\n    await installV013SelectiveMerchantShoulder();')
 s=s.replace("version:'V012-road-grass-candidate-r1'","version:'V013-merchant-edge-candidate-r1'")
 s=s.replace('Noboribetsu_Date_V012_browser_diagnostics.json','Noboribetsu_Date_V013_browser_diagnostics.json')
 s=s.replace('V012 路緣柔化／保留 V011 補洞與操控','V013 商家街路緣補強／保留 V011 補洞與 V012 路緣')
 s=s.replace('完整 B 場景與 V011 296 面地形補洞已載入','完整 B 場景與 V011、V012、V013 視覺修補已載入')
 app.write_text(s)
 html=newdist/'index.html';h=html.read_text().replace('V012 候選','V013 候選');html.write_text(h)
 q=newdist/'qa.json';v=json.loads(q.read_text());v.update({'version':'V013-merchant-edge-candidate-r1','change_scope':'Only V004/V005 merchant road-to-grass selective non-collision visual fade, V012+V011 preserved','transition_v013':manifest['transition_v013'],'private_site':'UNMODIFIED_NOT_TESTED','android_real_device':'NOT TESTED'});q.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 delta=[p.relative_to(source).as_posix() for p in sorted(source.rglob('*')) if p.is_file() and p.read_bytes()!=(out/p.relative_to(source)).read_bytes()]
 if delta!=['dist/app.js','dist/index.html','dist/qa.json','dist/scene_view.json']:raise RuntimeError('Unexpected changes: '+str(delta))
 (out/'README_V013.md').write_text('# 登別伊達時代村 V013 候選｜商家街道路外側透明路緣\n\nV013 只改 V004/V005 商家街路面視覺過渡，V011 148 格補洞與 V012 街尾路緣、231.6m 路線和碰撞全數保留。\n\n以 `python start_v012_local.py` 啟動（僅本機），以一般 Chrome/Edge 在瀏覽器開啟。使用「街尾返程」與 WASD 檢視；A/B 可切換。\n\n仍需 Android 真機、真正私人網站 HTTPS、Blender 母檔及現場實景驗收；測試專用 SHA adapter 不包含在 Runtime。\n',encoding='utf8')
 result={'schema':'V013-delta/1','changed_original_files':delta,'original_unchanged_files':sum(p.is_file() for p in source.rglob('*'))-len(delta),'new_files':['dist/v013_selective_road_grass.json','README_V013.md'],'patch_sha256':digest,'collision_unchanged':True,'terrain_gap_v011_unchanged':True,'v012_unchanged':True}
 (out/'V013_delta_qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result,ensure_ascii=False,indent=2));return result
if __name__=='__main__':
 if len(sys.argv)!=4:raise SystemExit('usage integrate_v013.py SOURCE_V012_DIR NEW_V013_DIR PATCH_JSON')
 go(*map(Path,sys.argv[1:]))