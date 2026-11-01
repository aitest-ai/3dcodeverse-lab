#!/usr/bin/env python3
"""V010 browser integration QA using existing *unchanged* V009 runtime.

RESTRICTIONS:
- Top-level localhost/HTTPS navigation is blocked in this managed container. The
  isolated browser loads local files through Playwright's subresource interception.
- about:blank is NOT a secure origin; a TEST-ONLY SubtleCrypto SHA-256 adapter
  returns independently prevalidated per-model hashes by exact decoded length.
  It does NOT cryptographically hash browser in-memory buffers. Never deploy it.
- asset_preflight.json must be independently recomputed from exact immutable
  GLBs and gzip parts before any browser test is marked valid.
- Xvfb+ANGLE SwiftShader provides actual WebGL2; this is not Android and
  doesn't validate the private site's CDN, CSP, HTTPS, caching or sign-in.
"""
import json,mimetypes,time,sys,os
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from verify_all_assets import verify,ROOT
ROOT=Path(os.environ.get('DATE_DIST_ROOT',str(Path(__file__).resolve().parents[2]/'runtime'/'dist')))

OUT=Path(os.environ.get('DATE_QA_DIR',str(Path.cwd()/'v010_results')));OUT.mkdir(exist_ok=True)
records=verify()
size_to_digest={}
for r in records:
 key=str(r['bytes'])
 if key in size_to_digest and size_to_digest[key]!=r['sha256']:
  raise ValueError('Ambiguous model length for test harness: '+key)
 size_to_digest[key]=r['sha256']

# Tiny browser-side test adapter; protected by independent Python SHA-256 checks.
# No test-only code is written to /dist or to GitHub application production files.
JS_SHA_ADAPTER=r'''(shaMap) => {
  const subtle={digest:async(algorithm,modelBuffer)=>{
    if(String(algorithm).toUpperCase()!=='SHA-256')throw Error('QA only supports SHA-256');
    const n=modelBuffer.byteLength;
    const hex=shaMap[String(n)];
    if(!hex)throw Error('QA received unknown model byte length '+n);
    return Uint8Array.from(hex.match(/.{2}/g), h=>parseInt(h,16)).buffer;
  }};
  Object.defineProperty(window.crypto,'subtle',{value:subtle,configurable:true});
  window.__QA_SECURE_ORIGIN_SIMULATED__=true;
  return {secure:window.isSecureContext, subtle:typeof window.crypto.subtle?.digest==='function'};
}'''

report={'schema':'noboribetsu-v010-webgl2-integration/1','underlying_runtime':'V009 R1 unchanged',
        'scene_source':'local files fulfilled as https://date.local subresources from about:blank',
        'real_webgl2_required':True,'simulated_secure_origin_crypto':True,
        'crypto_caveat':'Independent SHA-256 of each model checked with Python; browser digest adapter accepts prechecked sizes, not a true WebCrypto digest. Not for production.',
        'verified_input_sha256':records,'steps':[], 'console_errors':[],
        'android_real_device_verified':False,'private_host_navigation_verified':False,
        'blender_native_verified':False,'success':False}

with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,timeout=15000,args=[
  '--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--ignore-gpu-blocklist',
  '--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader',
  '--disable-extensions','--disable-background-timer-throttling'])
 page=b.new_page(viewport={'width':960,'height':600},device_scale_factor=1)
 errs=[];reqs=[]
 page.on('pageerror',lambda e:errs.append('JS: '+str(e)[:800]))
 page.on('console',lambda m:errs.append('console: '+m.text[:600]) if m.type=='error' else None)
 def route_req(route):
  url=route.request.url
  item=url.split('date.local/',1)[-1].split('?',1)[0]
  f=ROOT/item
  if not f.is_file() or not f.resolve().is_relative_to(ROOT):
   reqs.append({'name':item,'status':404});route.fulfill(status=404,body='not found',headers={'Access-Control-Allow-Origin':'*'});return
  typ=mimetypes.guess_type(str(f))[0] or 'application/octet-stream'
  if f.suffix=='.js':typ='text/javascript'
  if f.suffix=='.glb':typ='model/gltf-binary'
  reqs.append({'name':item,'status':200,'bytes':f.stat().st_size})
  route.fulfill(status=200,path=str(f),headers={'Access-Control-Allow-Origin':'*','Content-Type':typ,'Cache-Control':'no-store'})
 page.route('https://date.local/**',route_req)
 poly=page.evaluate(JS_SHA_ADAPTER,size_to_digest)
 if not poly['subtle']:raise AssertionError('Test-only SHA adapter failed')
 html=(ROOT/'index.html').read_text('utf8').replace('<head>','<head><base href="https://date.local/">',1)
 start=time.monotonic()
 page.set_content(html,wait_until='domcontentloaded')
 ctx=page.evaluate("""() => {let gl=document.createElement('canvas').getContext('webgl2');return {webgl2:!!gl, version:gl?.getParameter(gl.VERSION)||null}}""")
 report['webgl2_context']=ctx
 print('INIT',json.dumps(ctx),flush=True)
 if not ctx['webgl2']:raise AssertionError('Actual WebGL2 context unavailable')
 try:
  page.wait_for_function("document.querySelector('#scene').dataset.loaded === 'true' || document.querySelector('#scene').dataset.loaded === 'failed'",timeout=145000,polling=500)
 except PlaywrightTimeout:pass
 ready=page.locator('#scene').get_attribute('data-loaded')
 main={'stage':'boot','result':ready,'seconds':round(time.monotonic()-start,1),
       'text':page.locator('#loadText').inner_text(),
       'error':page.locator('#loadError').inner_text() if ready!='true' else None}
 report['steps'].append(main);print('BOOT',json.dumps(main,ensure_ascii=False),flush=True)
 if ready=='true':
  try:page.wait_for_function('window.__DATE_METRICS__?.first_frame_ms !== null',timeout=30000,polling=500)
  except PlaywrightTimeout:pass
  m=page.evaluate('''() => ({version:__DATE_METRICS__.version, first_frame_ms:__DATE_METRICS__.first_frame_ms,gl:__DATE_METRICS__.webgl, renderer:__DATE_METRICS__.renderer,placeholder:__DATE_METRICS__.placeholder_removal_by_building, stage_switches:__DATE_METRICS__.stage_switches,model_stages:Object.keys(__DATE_METRICS__.models),fetch_count:__DATE_METRICS__.fetch_events.length})''')
  report['initial_metrics']=m
  page.screenshot(path=str(OUT/'V010_Entrypoint_Test.png'),full_page=False,animations='disabled')
  # Real DOM interactions (no Playwright actionability waits under software GPU).
  def sample(label):
   data=page.evaluate("""() => ({loaded:document.getElementById('scene').dataset.loaded,stage:document.getElementById('scene').dataset.stage,position:document.getElementById('scene').dataset.position,status:document.getElementById('positionLabel').textContent,trace:__DATE_METRICS__.stage_switches,first_frame:__DATE_METRICS__.first_frame_ms,errors:__DATE_METRICS__.error||null})""")
   report['steps'].append({'label':label,**data});print('STEP',label,json.dumps(data,ensure_ascii=False)[:950],flush=True)
   OUT.joinpath('V010_interaction_progress.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
   return data
  page.evaluate("document.getElementById('enterButton').click()")
  sample('enter')
  before=page.locator('#scene').get_attribute('data-position')
  page.keyboard.down('w');page.wait_for_timeout(850);page.keyboard.up('w');page.wait_for_timeout(200)
  after=page.locator('#scene').get_attribute('data-position')
  delta=sum((float(a)-float(b))**2 for a,b in zip(after.split(','),before.split(',')))**.5
  page.wait_for_timeout(450)
  stopped=page.locator('#scene').get_attribute('data-position')
  drift=sum((float(a)-float(b))**2 for a,b in zip(stopped.split(','),after.split(',')))**.5
  report['steps'].append({'label':'real_keyboard_walk','before':before,'after':after,'moved_m':delta,'position_after_release':stopped,'drift_after_release_m':drift})
  print('KEYBOARD',json.dumps({'before':before,'after':after,'moved_m':delta,'drift_after_release_m':drift}),flush=True)
  page.wait_for_timeout(200)
  page.evaluate("document.getElementById('returnButton').click()")
  tail=sample('street_tail')
  page.screenshot(path=str(OUT/'V010_StreetEnd_Test.png'),timeout=16000,animations='disabled')
  page.evaluate("document.getElementById('homeButton').click()")
  home=sample('return_home')
  page.evaluate("document.getElementById('aButton').click()")
  try: page.wait_for_function("document.getElementById('scene').dataset.stage==='A' || document.getElementById('scene').dataset.loaded==='failed'",timeout=40000,polling=250)
  except PlaywrightTimeout: pass
  a=sample('stage_A')
  if a['stage']=='A':
   page.evaluate("document.getElementById('bButton').click()")
   sample('stage_B_return')
  report['success']=bool(delta>0.05 and drift<0.05 and tail['position']!=home['position'] and a['stage']=='A' and all(max(item['eye_delta_m'],item['target_delta_m'],item['up_delta'],item['fov_delta'])<1e-8 for item in a['trace']))
 report['console_errors']=errs[:40]
 report['requests']={'total':len(reqs),'failures':[x for x in reqs if x['status']!=200]}
 OUT.joinpath('V010_Browser_Keyboard_And_Stage_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('FINAL',json.dumps({'success':report['success'],'metrics':report.get('initial_metrics'),'errors':report['console_errors'][:5],'screenshot_error':report.get('screenshot_error')},ensure_ascii=False),flush=True)
 b.close()
sys.exit(0 if report['success'] else 2)