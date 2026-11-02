#!/usr/bin/env python3
"""Create V012 candidate without mutating V011. Usage: python integrate_v012.py V011_dir V012_dir edge_json"""
from __future__ import annotations
import hashlib,json,shutil,sys
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()

def install(src:Path,out:Path,overlay:Path):
    if out.exists():raise FileExistsError(f'refuse to overwrite {out}')
    if not src.joinpath('dist/app.js').is_file():raise FileNotFoundError('V011 dist missing')
    expected={
        'dist/assets/v006_tail_road.glb':'423a928696dadd4fcea9a516f0a854e504e8eae6209adc141706e5cbe0737642',
        'dist/v011_terrain_gap_patch.json':'71f541341123354025d81e740f3bc55bbbf70e02634236e33be7e61bed77cf64'
    }
    for rel,s in expected.items():
        if sha((src/rel).read_bytes())!=s:raise ValueError('Frozen V011 file unexpectedly changed: '+rel)
    patch=json.loads(overlay.read_bytes())
    assert patch['schema']=='noboribetsu-v012-road-grass-transition/1'
    assert patch['triangles']==972 and patch['samples']==82
    shutil.copytree(src,out)
    dist=out/'dist'
    overlaybytes=overlay.read_bytes()
    (dist/'v012_road_grass_transition.json').write_bytes(overlaybytes)
    mfile=dist/'scene_view.json';manifest=json.loads(mfile.read_text())
    if 'transition_v012' in manifest:raise RuntimeError('V012 already applied')
    manifest['transition_v012']={
      'schema':patch['schema'],'path':'v012_road_grass_transition.json','sha256':sha(overlaybytes),
      'bytes':len(overlaybytes),'triangles':972,'route_start_s_m':patch['route_start_s_m'],
      'route_end_s_m':patch['route_end_s_m'],'road_glb_sha256':patch['road_glb_sha256'],
      'stage':'B','visual_only':True,'collision_changed':False,'V011_terrain_patch_untouched':True,
      'provenance':'Author-estimated road/grass fade from frozen V002 GSI heights; not a curb, drainage or survey'}
    mfile.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    p=dist/'app.js';s=p.read_text()
    needle='async function installV011TerrainGap(){'
    if s.count(needle)!=1:raise RuntimeError('V011 hook missing/duplicated')
    code=r'''async function installV012RoadGrassFade(){
  const c=manifest.transition_v012;
  if(!c||c.schema!=='noboribetsu-v012-road-grass-transition/1'||
      c.stage!=='B'||c.triangles!==972||c.visual_only!==true||c.collision_changed!==false||
      c.road_glb_sha256!==manifest.extension_v006.model.sha256)
    throw new Error('V012 路緣版本契約不相符，已停止載入。');
  const raw=await getBuffer(c.path,()=>{});
  if(raw.byteLength!==c.bytes)throw new Error('V012 路緣檔案長度錯誤');
  const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',raw)),n=>n.toString(16).padStart(2,'0')).join('');
  if(digest!==c.sha256)throw new Error('V012 路緣 SHA-256 不符，已停止載入');
  const p=JSON.parse(new TextDecoder().decode(raw));
  if(p.schema!==c.schema||p.triangles!==972||p.road_glb_sha256!==c.road_glb_sha256||
      p.collision_enabled!==false||p.samples!==82||
      p.positions?.length!==656*3||p.colors?.length!==656*4||p.indices?.length!==972*3||
      [...p.positions,...p.colors,...p.indices].some(n=>!Number.isFinite(n)))
    throw new Error('V012 路緣模型內容驗證失敗');
  const geo=new THREE.BufferGeometry();
  geo.setAttribute('position',new THREE.Float32BufferAttribute(p.positions,3));
  geo.setAttribute('color',new THREE.Float32BufferAttribute(p.colors,4));
  geo.setIndex(p.indices);
  geo.computeVertexNormals();geo.computeBoundingSphere();
  const mat=new THREE.MeshStandardMaterial({vertexColors:true,transparent:true,
    side:THREE.DoubleSide,depthWrite:false,roughness:1,metalness:0,
    polygonOffset:true,polygonOffsetFactor:-1,polygonOffsetUnits:-1});
  const mesh=new THREE.Mesh(geo,mat);
  mesh.name='V012_V006_ROAD_GRASS_FADE_VISUAL_ONLY';
  mesh.frustumCulled=true;mesh.renderOrder=5;mesh.receiveShadow=true;mesh.castShadow=false;
  mesh.userData={version:'V012',visualOnly:true,collision:false,triangles:972,
    provenance:'author-estimated from frozen V002 GSI heights; not a surveyed shoulder/drain'};
  B.add(mesh);
  metrics.v012_road_grass={triangles:972,vertices:656,source_glb_sha256:c.road_glb_sha256,
    collision_unchanged:true,route_unchanged:true,V011_terrain_patch_untouched:true};
  refreshDiagnostics();
}

'''
    s=s.replace(needle,code+needle)
    call='await installV011TerrainGap();'
    if s.count(call)!=1:raise RuntimeError('V011 single insertion hook invalid')
    s=s.replace(call,call+'\n    await installV012RoadGrassFade();')
    s=s.replace("version:'V011-terrain-gap-candidate-r1'","version:'V012-road-grass-candidate-r1'")
    s=s.replace('Noboribetsu_Date_V011_browser_diagnostics.json','Noboribetsu_Date_V012_browser_diagnostics.json')
    s=s.replace('V011 地形補洞／保留低幀率操控','V012 路緣柔化／保留 V011 補洞與操控')
    p.write_text(s)
    html=dist/'index.html';h=html.read_text()
    h=h.replace('V011','V012').replace('V010 候選｜231.6 m','V012 候選｜231.6 m')
    h=h.replace('V012 地形補洞＋V010 操控修正候選','V012 街尾路緣柔化＋保留 V011 補洞與 V010 操控')
    h=h.replace('WebGL2、Android、Blender 與私人網站仍未驗收。','隔離的 Chromium WebGL2 已有渲染驗證；Android 實機、Blender 與私人網站仍未驗收。')
    html.write_text(h)
    q=dist/'qa.json';qa=json.loads(q.read_text());qa.update({
      'version':'V012-road-grass-candidate-r1','status':'SOURCE_VERIFIED_PENDING_WEBGL2_VISUAL_QA',
      'change_scope':'V006 final 33.84m edge-only 972 transparent visual faces; V011 gap untouched',
      'transition_v012':manifest['transition_v012'],'private_site':'UNCHANGED_NOT_TESTED','android':'NOT TESTED'})
    q.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
    delta=[]
    for rel in sorted(p.relative_to(src).as_posix() for p in src.rglob('*') if p.is_file()):
       before=(src/rel).read_bytes();after=(out/rel).read_bytes()
       if before!=after:delta.append(rel)
    assert delta==['dist/app.js','dist/index.html','dist/qa.json','dist/scene_view.json'],delta
    assert all((src/r).read_bytes()==(out/r).read_bytes() for r in expected)
    result={'schema':'noboribetsu-v012-delta/1','changed_original_files':delta,
      'unchanged_original_files':sum(p.is_file() for p in src.rglob('*'))-len(delta),
      'new_files':['dist/v012_road_grass_transition.json'],
      'original_V011_patch_sha256':expected['dist/v011_terrain_gap_patch.json'],
      'original_V006_road_sha256':expected['dist/assets/v006_tail_road.glb'],'collision_changed':False,
      'stage_A_model_changed':False,'stage_B_original_model_changed':False}
    # Local viewer launcher and user-facing note: new files only, no change to V011 source.
    (out/'start_v012_local.py').write_text("""#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os
os.chdir(Path(__file__).resolve().parent / 'dist')
server=ThreadingHTTPServer(('127.0.0.1',8772),SimpleHTTPRequestHandler)
print('V012 locally available at http://127.0.0.1:8772/index.html',flush=True)
server.serve_forever()
""",encoding='utf8')
    (out/'README_V012.md').write_text("""# 登別伊達時代村 V012 R1｜最後 33.84 公尺道路／草地過渡

1. 完整解壓 ZIP，保持 `dist/` 與 `assets/` 的原始位置。
2. 執行 `python start_v012_local.py`，在一般電腦的 Chrome/Edge 開啟 `http://127.0.0.1:8772/index.html`。
3. 點「開始步行」，WASD 移動；按「街尾返程」可在終點檢查道路／草地過渡；A/B 可切換比較。
4. 另開獨立 `Noboribetsu_Date_V012_R1_Review.html` 以同鏡位比較實測 Chromium WebGL2 畫面。

V012 只加上視覺土／苔色帶 972 triangles。V011 148 格地形補洞（296 triangles）、高品質模型、地理來源、碰撞、231.57 m 路線與低幀率操控保持不變；不代表實地測繪。

獨立測試使用 Xvfb Chromium SwiftShader + 虛擬子資源，WebCrypto 模型雜湊由 Python 預驗證後以測試專用 adapter 回應；正式 Runtime 沒有此 adapter。Android 真機、私人網站 CDN/HTTPS 及 Blender `.blend` 未驗證。
""",encoding='utf8')
    result['new_files'] += ['start_v012_local.py','README_V012.md']
    (out/'V012_delta_qa.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    return result

if __name__=='__main__':
    if len(sys.argv)!=4:raise SystemExit('Usage: integrate_v012.py V011_DIR V012_DIR EDGE_JSON')
    print(json.dumps(install(*map(Path,sys.argv[1:])),ensure_ascii=False,indent=2))