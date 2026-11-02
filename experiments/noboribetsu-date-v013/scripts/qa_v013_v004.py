#!/usr/bin/env python3
"""True Chromium WebGL2 isolated browser proof. Injected SHA adapter + placement hook TEST-ONLY."""
import os,sys,json,hashlib,mimetypes
from pathlib import Path
from playwright.sync_api import sync_playwright,TimeoutError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source012'/'source'))
from verify_all_assets import verify
ROOT=Path(os.environ['DATE_DIST_ROOT']);OUT=Path(os.environ['DATE_QA_DIR']);OUT.mkdir(parents=True,exist_ok=True)
records=verify();assert all(x['pass'] for x in records)
size_map={}
for r in records:
 k=str(r['bytes']);assert k not in size_map or size_map[k]==r['sha256'];size_map[k]=r['sha256']
for filename in ['v011_terrain_gap_patch.json','v012_road_grass_transition.json','v013_selective_road_grass.json']:
 file=ROOT/filename;key=str(file.stat().st_size);v=hashlib.sha256(file.read_bytes()).hexdigest()
 assert key not in size_map or size_map[key]==v
 size_map[key]=v
polyfill='''(shaMap)=>{const subtle={digest:async(algorithm,b)=>{if(String(algorithm).toUpperCase()!=='SHA-256')throw Error('bad digest');const hex=shaMap[String(b.byteLength)];if(!hex)throw Error('Unverified SHA source length '+b.byteLength);return Uint8Array.from(hex.match(/.{2}/g),x=>parseInt(x,16)).buffer;}};Object.defineProperty(crypto,'subtle',{value:subtle,configurable:true});window.__TEST_ONLY_SHA_ADAPTER__=true;}'''
# Only injected into the in-memory module response to teleport for 2 photographic QA points.
# Never written into the official Runtime app.js.
hook='''\nwindow.__TEST_ONLY_V013_JUMP__=(s,show)=>{if(!session||!renderReady)return false;
 const p=manifest.route.reduce((a,b)=>Math.abs(a.s-s)<Math.abs(b.s-s)?a:b);
 session.position={x:p.x,y:p.y,z:p.z};session.heading=0;session.pitch=0;
 const m=B.getObjectByName('V013_V004_V005_MERCHANT_SELECTIVE_EDGE_VISUAL');if(m)m.visible=show;
 updateCamera();updateStatus();miniMap();renderer.render(scene,camera);return true;};\n'''
result={'schema':'V013-isolated-Chromium-WebGL2/1','source_sha_all_verified':True,'browser_SHA_adapter_TEST_ONLY':True,
 'production_adapter':False,'test_camera_teleport_only':True,'real_webgl2':False,'real_android':False,'private_site_tested':False,'success':False,'errors':[],'missing_requests':[],'screenshots':[]}
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--ignore-gpu-blocklist','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-extensions','--disable-background-timer-throttling'],timeout=30000)
 page=browser.new_page(viewport={'width':600,'height':360},device_scale_factor=1)
 errors=[];missing=[];page.on('pageerror',lambda e:errors.append(str(e)[:500]))
 def serve(route):
  name=route.request.url.split('date.local/',1)[-1].split('?',1)[0]
  f=ROOT/name
  if not f.is_file() or not f.resolve().is_relative_to(ROOT):
   missing.append(name);route.fulfill(status=404,body=b'',headers={'Access-Control-Allow-Origin':'*'});return
  media=mimetypes.guess_type(str(f))[0] or 'application/octet-stream'
  if f.suffix=='.js':media='text/javascript'
  if name=='app.js':route.fulfill(status=200,body=f.read_text()+hook,headers={'Access-Control-Allow-Origin':'*','Content-Type':media})
  else:route.fulfill(status=200,path=str(f),headers={'Access-Control-Allow-Origin':'*','Content-Type':media})
 page.route('https://date.local/**',serve)
 page.evaluate(polyfill,size_map)
 html=(ROOT/'index.html').read_text().replace('<head>','<head><base href="https://date.local/">',1)
 page.set_content(html,wait_until='domcontentloaded')
 result['real_webgl2']=page.evaluate("!!document.createElement('canvas').getContext('webgl2')")
 print('V013 real WebGL2?',result['real_webgl2'],flush=True)
 try:page.wait_for_function("['true','failed'].includes(document.getElementById('scene').dataset.loaded)",timeout=195000,polling=650)
 except TimeoutError:pass
 result['loaded']=page.evaluate("document.getElementById('scene').dataset.loaded")
 result['error_text']=page.evaluate("document.getElementById('loadError').textContent")
 print('Loaded:',result['loaded'],result['error_text'][:260],flush=True)
 if result['loaded']=='true':
  page.evaluate("document.getElementById('enterButton').click()")
  page.wait_for_timeout(500)
  result['metrics']=page.evaluate("""() => ({v011:window.__DATE_METRICS__.v011_terrain_gap,v012:window.__DATE_METRICS__.v012_road_grass,v013:window.__DATE_METRICS__.v013_road_grass,renderer:window.__DATE_METRICS__.renderer,webgl:window.__DATE_METRICS__.webgl})""")
  print('Metrics',json.dumps(result['metrics'],ensure_ascii=False)[:1300],flush=True)
  for station,label in [(110,'v004')]:
   for show,state in [(False,'before'),(True,'after')]:
    success=page.evaluate('(args)=>window.__TEST_ONLY_V013_JUMP__(args.s,args.show)',{'s':station,'show':show})
    if not success:raise RuntimeError('QA route positioning failed')
    page.wait_for_timeout(300)
    file=OUT/f'V013_{label}_{state}_WebGL2.png'
    page.screenshot(path=str(file),timeout=65000,animations='disabled')
    result['screenshots'].append({'name':file.name,'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
    print(file.name,'saved',file.stat().st_size,flush=True)
  result['success']=bool(result['loaded']=='true' and result['metrics']['v011'] and result['metrics']['v012'] and result['metrics']['v013'] and result['metrics']['v013']['triangles']==2436)
 result['errors']=errors;result['missing_requests']=missing
 browser.close()
(OUT/'V013_real_webgl2_qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('V013 browser QA',result['success'],'error count',len(result['errors']),'requests missed',len(result['missing_requests']),flush=True)
sys.exit(0 if result['success'] and not errors and not missing else 2)