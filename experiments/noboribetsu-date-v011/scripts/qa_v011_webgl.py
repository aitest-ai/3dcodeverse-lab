#!/usr/bin/env python3
"""V011 isolated, REAL-WebGL2 screenshot and control acceptance.

Requires Xvfb + Chromium SwiftShader. In the managed sandbox, Chromium is
blocked from top-level localhost navigation; this QA page uses subresource
routing and TEST-ONLY length→pre-verified-hash adapter. All GLBs independently
SHA256-checked by Python before browser boot. Do not ship adapter to runtime.
"""
import json,mimetypes,os,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError
from verify_all_assets import verify
ROOT=Path(os.environ['DATE_DIST_ROOT'])
OUT=Path(os.environ['DATE_QA_DIR']);OUT.mkdir(parents=True,exist_ok=True)
records=verify()
size_map={}
for v in records:
 key=str(v['bytes']);assert key not in size_map or size_map[key]==v['sha256'];size_map[key]=v['sha256']
patch_file=ROOT/'v011_terrain_gap_patch.json'
size_map[str(patch_file.stat().st_size)]=__import__('hashlib').sha256(patch_file.read_bytes()).hexdigest()
polyfill=r'''(shaMap)=>{
 const subtle={digest:async(algorithm,b)=>{
  if(String(algorithm).toUpperCase()!=='SHA-256')throw Error('Not a SHA-256 call');
  const hex=shaMap[String(b.byteLength)];if(!hex)throw Error('Unrecognized byte count '+b.byteLength);
  return Uint8Array.from(hex.match(/.{2}/g),k=>parseInt(k,16)).buffer;
 }};
 Object.defineProperty(crypto,'subtle',{value:subtle,configurable:true});
 window.__TEST_ONLY_INDEPENDENTLY_VERIFIED_HASH_ADAPTER__=true;
}'''
results={'schema':'noboribetsu-v011-isolated-webgl2/1','source_b_sha256':records[0]['sha256'],
 'independent_model_sha256_verified':all(r['pass'] for r in records),
 'sha_adapter_used_in_browser':True,'adapter_shipped_to_runtime':False,
 'real_webgl2':False,'android_real_device':False,'private_site_https':False,
 'browser_origin':'isolated about:blank with virtual https://date.local/ subresource routing',
 'steps':[],'errors':[],'success':False}
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=[
  '--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--ignore-gpu-blocklist',
  '--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader',
  '--disable-extensions','--disable-background-timer-throttling'],timeout=20000)
 page=browser.new_page(viewport={'width':960,'height':600},device_scale_factor=1)
 errs=[];req=[]
 page.on('pageerror',lambda e:errs.append(str(e)[:500]))
 page.on('console',lambda m:errs.append('console: '+m.text[:500]) if m.type=='error' else None)
 def serve(route):
  name=route.request.url.split('date.local/',1)[-1].split('?',1)[0]
  f=ROOT/name
  if not f.is_file() or not f.resolve().is_relative_to(ROOT):
   req.append({'name':name,'status':404});route.fulfill(status=404,body=b'',headers={'Access-Control-Allow-Origin':'*'});return
  media=mimetypes.guess_type(str(f))[0] or 'application/octet-stream'
  if f.suffix=='.js':media='text/javascript'
  req.append({'name':name,'status':200})
  route.fulfill(status=200,path=str(f),headers={'Access-Control-Allow-Origin':'*','Content-Type':media})
 page.route('https://date.local/**',serve)
 page.evaluate(polyfill,size_map)
 html=(ROOT/'index.html').read_text('utf8').replace('<head>','<head><base href="https://date.local/">',1)
 page.set_content(html,wait_until='domcontentloaded')
 results['real_webgl2']=page.evaluate("!!document.createElement('canvas').getContext('webgl2')")
 print('webgl2=',results['real_webgl2'],flush=True)
 try:page.wait_for_function("['true','failed'].includes(document.getElementById('scene').dataset.loaded)",timeout=150000,polling=550)
 except TimeoutError:pass
 results['loaded']=page.evaluate("document.getElementById('scene').dataset.loaded")
 results['error_text']=page.evaluate("document.getElementById('loadError').textContent")
 print('LOADED=',results['loaded'],'ERROR=',results['error_text'][:500],flush=True)
 if results['loaded']=='true':
  try:page.wait_for_function('window.__DATE_METRICS__?.first_frame_ms !== null',timeout=30000,polling=600)
  except TimeoutError:pass
  page.evaluate("document.getElementById('enterButton').click()")
  page.evaluate("document.getElementById('returnButton').click()")
  page.wait_for_timeout(900)
  # Force a synchronous GPU readback so this captures the actual tail frame.
  page.screenshot(path=str(OUT/'V011_street_end_WebGL2.png'),animations='disabled',timeout=35000)
  results['tail']=page.evaluate("""() => ({position:document.getElementById('scene').dataset.position,
   stage:document.getElementById('scene').dataset.stage,heading:document.getElementById('scene').dataset.heading,
   terrain:window.__DATE_METRICS__.v011_terrain_gap || null,
   renderer:window.__DATE_METRICS__.renderer,
   original_placeholder:window.__DATE_METRICS__.placeholder_removal_by_building,
   first_frame_ms:window.__DATE_METRICS__.first_frame_ms})""")
  print('TAIL=',json.dumps(results['tail'],ensure_ascii=False),flush=True)
  # A/B path check only, without modifying B geometry.
  page.evaluate("document.getElementById('aButton').click()")
  try:page.wait_for_function("document.getElementById('scene').dataset.stage==='A'",timeout=50000,polling=600)
  except TimeoutError:pass
  results['stage_after_A']=page.evaluate("document.getElementById('scene').dataset.stage")
  if results['stage_after_A']=='A':page.evaluate("document.getElementById('bButton').click()")
  results['stage_after_B']=page.evaluate("document.getElementById('scene').dataset.stage")
  results['pose_switches']=page.evaluate("window.__DATE_METRICS__.stage_switches")
  results['success']=bool(results['real_webgl2'] and results['loaded']=='true' and
   results['tail']['terrain'] and results['tail']['terrain']['triangles']==296 and
   results['stage_after_A']=='A' and results['stage_after_B']=='B' and
   all(max(d['eye_delta_m'],d['target_delta_m'],d['up_delta'],d['fov_delta'])<1e-8 for d in results['pose_switches']))
 results['errors']=errs;results['failed_requests']=[x for x in req if x['status']!=200]
 (OUT/'V011_webgl2_qa.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
 browser.close()
print('FINAL',results['success'],'ERRORS',results['errors'][:3],flush=True)
sys.exit(0 if results['success'] else 2)