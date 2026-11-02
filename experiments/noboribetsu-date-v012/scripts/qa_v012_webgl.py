#!/usr/bin/env python3
"""Isolated real Chromium WebGL2 visual proof. SHA adapter is TEST ONLY and is never distributed in Runtime."""
import hashlib,json,mimetypes,os,sys
from pathlib import Path
from playwright.sync_api import sync_playwright,TimeoutError
from verify_all_assets import verify
ROOT=Path(os.environ['DATE_DIST_ROOT']); OUT=Path(os.environ['DATE_QA_DIR']);OUT.mkdir(parents=True,exist_ok=True)
records=verify(); assert all(x['pass'] for x in records)
size_map={}
for r in records:
 key=str(r['bytes']);assert key not in size_map or size_map[key]==r['sha256'];size_map[key]=r['sha256']
for filename in ['v011_terrain_gap_patch.json','v012_road_grass_transition.json']:
 path=ROOT/filename; key=str(path.stat().st_size);v=hashlib.sha256(path.read_bytes()).hexdigest()
 assert key not in size_map or size_map[key]==v
 size_map[key]=v
polyfill='''(shaMap)=>{const subtle={digest:async(algorithm,b)=>{if(String(algorithm).toUpperCase()!=="SHA-256")throw Error("bad digest");const hex=shaMap[String(b.byteLength)];if(!hex)throw Error("Unrecognized independently verified bytes "+b.byteLength);return Uint8Array.from(hex.match(/.{2}/g),x=>parseInt(x,16)).buffer;}};Object.defineProperty(crypto,'subtle',{value:subtle,configurable:true});window.__TEST_ONLY_HASH_ADAPTER__=true;}'''
r={'schema':'noboribetsu-v012-isolated-real-webgl2/1','full_model_sha256_verified_python':True,
   'browser_test_sha_adapter':True,'adapter_in_runtime':False,'real_webgl2':False,
   'android_real_device':False,'private_site_HTTPS_tested':False,'success':False,
   'steps':[],'errors':[],'network_errors':[]}
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=[
  '--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--ignore-gpu-blocklist',
  '--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader',
  '--disable-extensions','--disable-background-timer-throttling'],timeout=30000)
 page=browser.new_page(viewport={'width':960,'height':600},device_scale_factor=1)
 errs=[];missing=[]
 page.on('pageerror',lambda e:errs.append(str(e)[:600]))
 def serve(route):
  name=route.request.url.split('date.local/',1)[-1].split('?',1)[0]
  f=ROOT/name
  if not f.is_file() or not f.resolve().is_relative_to(ROOT):
   missing.append(name);route.fulfill(status=404,body=b'',headers={'Access-Control-Allow-Origin':'*'});return
  media=mimetypes.guess_type(str(f))[0] or 'application/octet-stream'
  if f.suffix=='.js':media='text/javascript'
  route.fulfill(status=200,path=str(f),headers={'Access-Control-Allow-Origin':'*','Content-Type':media})
 page.route('https://date.local/**',serve)
 page.evaluate(polyfill,size_map)
 html=(ROOT/'index.html').read_text().replace('<head>','<head><base href="https://date.local/">',1)
 page.set_content(html,wait_until='domcontentloaded')
 r['real_webgl2']=page.evaluate("!!document.createElement('canvas').getContext('webgl2')")
 print('WebGL2',r['real_webgl2'],flush=True)
 try:page.wait_for_function("['true','failed'].includes(document.getElementById('scene').dataset.loaded)",timeout=175000,polling=500)
 except TimeoutError:pass
 r['loaded']=page.evaluate("document.getElementById('scene').dataset.loaded")
 r['load_error_text']=page.evaluate("document.getElementById('loadError').textContent")
 print('Loaded',r['loaded'],'error',r['load_error_text'][:250],flush=True)
 if r['loaded']=='true':
  try:page.wait_for_function('window.__DATE_METRICS__?.first_frame_ms !== null',timeout=30000,polling=600)
  except TimeoutError:pass
  page.evaluate("document.getElementById('enterButton').click()")
  page.evaluate("document.getElementById('returnButton').click()")
  page.wait_for_timeout(750)
  page.screenshot(path=str(OUT/'V012_street_end_WebGL2.png'),timeout=55000,animations='disabled')
  r['tail']=page.evaluate('''() => ({position:document.getElementById('scene').dataset.position,stage:document.getElementById('scene').dataset.stage,
   road_grass:window.__DATE_METRICS__.v012_road_grass,terrain_gap:window.__DATE_METRICS__.v011_terrain_gap,
   rendered:window.__DATE_METRICS__.renderer,first_frame:window.__DATE_METRICS__.first_frame_ms})''')
  print('Tail',json.dumps(r['tail'],ensure_ascii=False),flush=True)
  page.evaluate("document.getElementById('aButton').click()")
  try:page.wait_for_function("document.getElementById('scene').dataset.stage==='A'",timeout=50000,polling=600)
  except TimeoutError:pass
  r['a_stage']=page.evaluate("document.getElementById('scene').dataset.stage")
  if r['a_stage']=='A':page.evaluate("document.getElementById('bButton').click()")
  r['b_stage']=page.evaluate("document.getElementById('scene').dataset.stage")
  r['switches']=page.evaluate("window.__DATE_METRICS__.stage_switches")
  r['success']=bool(r['real_webgl2'] and r['loaded']=='true' and r['tail']['road_grass'] and
    r['tail']['road_grass']['triangles']==972 and r['tail']['terrain_gap'] and
    r['tail']['terrain_gap']['triangles']==296 and r['a_stage']=='A' and r['b_stage']=='B' and
    all(max(x['eye_delta_m'],x['target_delta_m'],x['up_delta'],x['fov_delta'])<1e-8 for x in r['switches']))
 r['errors']=errs;r['network_errors']=missing
 browser.close()
(OUT/'V012_webgl_qa.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print('FINAL:',r['success'],'ERRORS:',r['errors'][:3],flush=True)
sys.exit(0 if r['success'] else 2)