#!/usr/bin/env python3
"""Copy the immutable V010 runtime and attach V011 terrain holes in B only.

Does not rewrite frozen V010 GLBs, terrain textures, roads, routing or collisions.
Only 4 existing dist text files differ, plus 1 compact geometry JSON asset.
"""
import argparse, hashlib, json, shutil
from pathlib import Path
EXPECTED={
 'app.js':'ede7f35910f1d2153392d20c874953eb96e62068a8a684f5c0d2ae1c042bbd87',
 'index.html':'1e7c260a14e57e33ec0d7239b21821d2f05fa724284c6a7373d29dbb6a47dfc0',
 'qa.json':'05a201afc2cf0c2cca8957fca08d281bb88aa358d5f96fc1cf7a24eb54faf6d0',
 'scene_view.json':'15ac864d6a1c4a8e19b4460378c47d63297da047e4280e07aa7399c3e7d8e1b1',
}
SCHEMA='noboribetsu-v011-terrain-gap-patch/1'
INSTALL='''
// V011 render-only reconstruction of holes in the frozen B terrain.
// This does not patch the original GLB or change walkable collision geometry.
async function installV011TerrainGap(){
  const c=manifest.terrain_gap_v011;
  if(!c||c.schema!=='noboribetsu-v011-terrain-gap-patch/1'||
     c.source_b_sha256!==manifest.models.find(m=>m.stage==='B')?.sha256||
     c.gap_cells!==148||c.triangles!==296||!c.visual_only)
    throw new Error('V011 地形補洞版本資訊無效，已停止載入。');
  // A real SHA-256 digest is required in production. The isolated QA adapter
  // never ships in the Runtime and only resolves independently hashed bytes.
  const bytes=await getBuffer(c.path,()=>{});
  if(bytes.byteLength!==c.bytes)throw new Error('V011 地形補洞檔案長度錯誤，已停止載入。');
  const rawDigest=await crypto.subtle.digest('SHA-256',bytes);
  const actualHash=Array.from(new Uint8Array(rawDigest),n=>n.toString(16).padStart(2,'0')).join('');
  if(actualHash!==c.sha256)throw new Error('V011 地形補洞 SHA-256 驗證失敗，已停止載入。');
  const patch=JSON.parse(new TextDecoder().decode(bytes));
  if(patch.schema!==c.schema||patch.source_b_sha256!==c.source_b_sha256||
     patch.gap_cells!==148||patch.triangles!==296||patch.collision_enabled!==false||
     patch.positions?.length!==296*9||patch.normals?.length!==296*9||patch.uv?.length!==296*6||
     [...patch.positions,...patch.normals,...patch.uv].some(v=>!Number.isFinite(v)))
    throw new Error('V011 地形補洞內容不完整，已停止載入。');
  const sources=[];
  B.traverse(obj=>{
    if(!obj.isMesh)return;
    const materials=Array.isArray(obj.material)?obj.material:[obj.material];
    for(const m of materials)if(m?.name==='Original_grass')sources.push(m);
  });
  if(sources.length!==1)throw new Error('V011 無法找到唯一的原始草地材質。');
  const geometry=new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(patch.positions,3));
  geometry.setAttribute('normal',new THREE.Float32BufferAttribute(patch.normals,3));
  geometry.setAttribute('uv',new THREE.Float32BufferAttribute(patch.uv,2));
  geometry.computeBoundingSphere();
  const mesh=new THREE.Mesh(geometry,sources[0]);
  mesh.name='V011_GSI_TERRAIN_GAP_VISUAL_ONLY';
  mesh.receiveShadow=true;mesh.castShadow=false;mesh.userData={version:'V011',
    source:'V002 GSI missing cells; harmonic estimated elevations; not measured',
    visualOnly:true,collision:false,cells:148,triangles:296};
  B.add(mesh);
  metrics.v011_terrain_gap={cells:148,triangles:296,source_b_sha256:c.source_b_sha256,
    original_material_reused:true,collision_unchanged:true,route_unchanged:true,
    original_B_model_unchanged:true};
  refreshDiagnostics();
}
'''

def replace_once(text,needle,replacement):
 if text.count(needle)!=1:
  raise RuntimeError(f'Expected one occurrence of {needle[:70]}, found {text.count(needle)}')
 return text.replace(needle,replacement,1)

def run(base:Path,target:Path,patch_path:Path):
 if target.exists():raise FileExistsError('Target must not exist; old revisions never overwritten')
 for name,sha in EXPECTED.items():
  h=hashlib.sha256((base/name).read_bytes()).hexdigest()
  if h!=sha:raise ValueError('Frozen V010 text changed: '+name)
 patch=json.loads(patch_path.read_text('utf8'))
 if patch['schema']!=SCHEMA or patch['gap_cells']!=148 or patch['triangles']!=296:
  raise ValueError('Wrong V011 patch data')
 shutil.copytree(base,target)
 (target/'v011_terrain_gap_patch.json').write_bytes(patch_path.read_bytes())
 app=(target/'app.js').read_text('utf8')
 app=replace_once(app,'async function loadV009UtsuroiCandidate(){',INSTALL+'\nasync function loadV009UtsuroiCandidate(){')
 app=replace_once(app,'B=await loadStageModel(bDescriptor,onBytes);', 'B=await loadStageModel(bDescriptor,onBytes);\n    await installV011TerrainGap();')
 if app.count("version:'V010-controls-candidate-r1'")!=2: raise ValueError("Unexpected V010 version markers")
 app=app.replace("version:'V010-controls-candidate-r1'", "version:'V011-terrain-gap-candidate-r1'")
 app=replace_once(app,"'第一人稱 · '+stage+' 場景 · V010 低幀率移動修正'", "'第一人稱 · '+stage+' 場景 · V011 地形補洞／保留低幀率操控'")
 app=replace_once(app,'完整 B 場景與 V009 外觀已載入；V010 低幀率移動修正已啟用，A 按需下載','完整 B 場景與 V011 296 面地形補洞已載入；原 V010 操作維持，A 按需下載')
 app=replace_once(app,'Noboribetsu_Date_V010_browser_diagnostics.json','Noboribetsu_Date_V011_browser_diagnostics.json')
 (target/'app.js').write_text(app,'utf8')
 j=json.loads((target/'scene_view.json').read_text())
 if 'terrain_gap_v011' in j:raise ValueError('V011 already installed')
 j['terrain_gap_v011']={'schema':SCHEMA,'path':'v011_terrain_gap_patch.json',
  'gap_cells':148,'triangles':296,'visual_only':True,
  'sha256':hashlib.sha256(patch_path.read_bytes()).hexdigest(),'bytes':patch_path.stat().st_size,
  'source_b_sha256':patch['source_b_sha256'],'model_unchanged':True,'collision_unchanged':True,
  'provenance':'V002 GSI terrain no-data visual infill, author-estimated not surveyed'}
 (target/'scene_view.json').write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf8')
 qa=json.loads((target/'qa.json').read_text());qa.update({
   'version':'V011-terrain-gap-candidate-r1',
   'status':'VISUAL_INPAINT_REQUIRES_REAL_WEBGL_RENDER_REVIEW',
   'change_scope':'Visual-only patch of 148 empty B grass terrain cells (296 triangles); V010 controls and collision unchanged',
   'terrain_gap':{'gap_cells':148,'triangles':296,'missing_height_grid_nodes':84,'method':'discrete harmonic interpolation','surveyed':False,
      'source_b_sha256':patch['source_b_sha256']},
   'android':'NOT TESTED','private_site':'UNMODIFIED AND NOT TESTED','blender_native':'NOT EXECUTED'})
 (target/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf8')
 html=(target/'index.html').read_text('utf8')
 if html.count('V010 低幀率移動修正')!=2: raise ValueError('Unexpected V010 HTML label count')
 html=html.replace('V010 低幀率移動修正','V011 地形補洞＋V010 操控修正')
 (target/'index.html').write_text(html,'utf8')
 delta=[]
 for f in sorted(base.rglob('*')):
  if f.is_file():
   rel=f.relative_to(base)
   h0=hashlib.sha256(f.read_bytes()).hexdigest();h1=hashlib.sha256((target/rel).read_bytes()).hexdigest()
   if h0!=h1:delta.append(str(rel))
 if set(delta)!={'app.js','scene_view.json','qa.json','index.html'}:
  raise ValueError('Unexpected edits: '+str(delta))
 return {'original_files':sum(p.is_file() for p in base.rglob('*')),'changed':delta,
         'added':['v011_terrain_gap_patch.json'],
         'unchanged_original_files':sum(p.is_file() for p in base.rglob('*'))-len(delta),
         'patch_file_sha256':hashlib.sha256((target/'v011_terrain_gap_patch.json').read_bytes()).hexdigest(),
         'all_old_models_unchanged':True}

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('base',type=Path);parser.add_argument('target',type=Path);parser.add_argument('patch',type=Path);parser.add_argument('qa',type=Path);args=parser.parse_args()
 report=run(args.base,args.target,args.patch)
 args.qa.parent.mkdir(parents=True,exist_ok=True);args.qa.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(report)