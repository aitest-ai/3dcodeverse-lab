#!/usr/bin/env python3
"""Isolated Chromium ANGLE SwiftShader/WebGL2 test. Hash adapter TEST ONLY: not in runtime."""
import json,os,hashlib,zipfile,time,mimetypes,sys,gzip
from pathlib import Path
from playwright.sync_api import sync_playwright,TimeoutError as PlaywrightTimeout
R=Path(__file__).resolve().parent;D=R/'runtime/dist';O=R/'qa';O.mkdir(exist_ok=True)
scene=json.loads((D/'scene_view.json').read_text());keymap={}
def record(data):
 digest=hashlib.sha256(data).hexdigest();size=str(len(data));
 if size in keymap and keymap[size]!=digest:
  raise AssertionError('Same-size assets with different SHA: '+size)
 keymap[size]=digest
for p in D.rglob('*'):
 if p.is_file() and p.suffix in ('.json','.glb') and p.name!='scene_view.json': record(p.read_bytes())
# Independently hash the original frozen B 188MB before returning its SHA to test-only browser digest.
bdesc=next(m for m in scene['models'] if m['stage']=='B')
compressed=b''.join((D/x).read_bytes() for x in bdesc['parts']);raw=gzip.decompress(compressed)
assert hashlib.sha256(raw).hexdigest()==bdesc['sha256'] and len(raw)==bdesc['bytes']
record(raw)
assert 'v019_porch_guide.json' in str(list(D.glob('v019*')))
adapter='''(m)=>{const subtle={digest:async(a,b)=>{if(String(a).toUpperCase()!=='SHA-256')throw Error('Bad alg');const h=m[String(b.byteLength)];if(!h)throw Error('No verified digest for size '+b.byteLength);return Uint8Array.from(h.match(/.{2}/g),x=>parseInt(x,16)).buffer;}};Object.defineProperty(crypto,'subtle',{value:subtle,configurable:true});window.__TEST_ONLY_ADAPTER__=true;}'''
res={'schema':'noboribetsu-date-v019-isolated-real-webgl2/1','status':'failed','test_only_hash_adapter':True,'test_adapter_shipped':False,'original_b_sha256_independently_verified':True,'browser_page_source':'about:blank + virtual date.local subresource routing','real_site_https_tested':False,'android_tested':False,'loaded':False,'real_webgl2':False,'checks':{},'errors':[],'request_missing':[]}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--ignore-gpu-blocklist','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-extensions'],timeout=25000)
 page=browser.new_page(viewport={'width':900,'height':630},device_scale_factor=1)
 page.on('pageerror',lambda e:res['errors'].append(str(e)[:400]))
 def serve(route):
  name=route.request.url.split('date.local/',1)[-1].split('?',1)[0]
  f=(D/name).resolve()
  if not f.is_file() or not f.is_relative_to(D):
   res['request_missing'].append(name);route.fulfill(status=404,body=b'');return
  m=mimetypes.guess_type(str(f))[0] or 'application/octet-stream';m='text/javascript' if f.suffix=='.js' else m
  if name=='app.js':
   qa_hook="""
// V019 TEST-ONLY camera pose hook. Never shipped in actual dist/app.js.
window.__V019_SET_TEST_CAMERA__=(s)=>{const p=manifest.route.find(q=>q.s>=s);if(!session||!p)throw Error('Not ready');const q=manifest.route.find(v=>v.s>=s+2)||p;const ground=world.ground(p.x,p.z,p.y,.45);session.position={x:p.x,y:ground?.y??p.y,z:p.z};session.heading=Math.atan2(q.x-p.x,-(q.z-p.z));session.pitch=-.08;updateCamera();updateStatus();return {...session.position,stage:session.stage};};
"""
   route.fulfill(status=200,body=f.read_bytes()+qa_hook.encode(),headers={'Content-Type':m,'Access-Control-Allow-Origin':'*'})
  else:route.fulfill(status=200,path=str(f),headers={'Content-Type':m,'Access-Control-Allow-Origin':'*'})
 page.route('https://date.local/**',serve)
 page.evaluate(adapter,keymap)
 html=(D/'index.html').read_text().replace('<head>','<head><base href="https://date.local/">',1)
 page.set_content(html,wait_until='domcontentloaded')
 res['real_webgl2']=page.evaluate("!!document.createElement('canvas').getContext('webgl2')")
 print('WebGL2',res['real_webgl2'],flush=True)
 try:page.wait_for_function("['true','failed'].includes(document.querySelector('#scene').dataset.loaded)",timeout=135000,polling=700)
 except PlaywrightTimeout:pass
 res['loaded']=page.evaluate("document.querySelector('#scene').dataset.loaded==='true'")
 res['load_error']=page.evaluate("document.querySelector('#loadError').textContent")
 print('loaded',res['loaded'],res['load_error'][:300],flush=True)
 if res['loaded']:
  page.evaluate("document.querySelector('#enterButton').click()")
  # This separate guide is present in B stage, has no collision and uses verified route coordinates.
  res['checks']['guide_count']=page.evaluate("window.__DATE_METRICS__.v019_guide?.markers")
  res['checks']['guide_verified']=page.evaluate("window.__DATE_METRICS__.v019_guide?.source_verified")
  res['checks']['initial_switch_on']=page.evaluate("document.querySelector('#porchGuideToggleButton').getAttribute('aria-pressed')")
  page.evaluate("document.querySelector('#porchGuideToggleButton').click()")
  res['checks']['off']=page.evaluate("document.querySelector('#porchGuideToggleButton').getAttribute('aria-pressed')")
  page.evaluate("document.querySelector('#porchGuideToggleButton').click()")
  res['checks']['back_on']=page.evaluate("document.querySelector('#porchGuideToggleButton').getAttribute('aria-pressed')")
  res['checks']['B_stage']=page.evaluate("document.querySelector('#scene').dataset.stage")
  # Isolated camera-position hook is added only in QA subresource response; never in Runtime.
  res['checks']['camera_test_hook_shipped']=False
  if page.evaluate("typeof window.__V019_SET_TEST_CAMERA__==='function'"):
   res['checks']['porch_pose']=page.evaluate('window.__V019_SET_TEST_CAMERA__(90)')
   try:
    page.screenshot(path=str(O/'V019_Porch_Guide_On_WebGL2.png'),timeout=35000,animations='disabled')
    page.evaluate("document.querySelector('#porchGuideToggleButton').click()")
    page.screenshot(path=str(O/'V019_Porch_Guide_Off_WebGL2.png'),timeout=35000,animations='disabled')
    page.evaluate("document.querySelector('#porchGuideToggleButton').click()")
    res['checks']['porch_side_by_side_captured']=True
   except Exception as ex:res['errors'].append('porch screenshot: '+str(ex)[:180]);res['checks']['porch_side_by_side_captured']=False
  try:
   page.screenshot(path=str(O/'V019_WebGL2_Entrance.png'),timeout=25000,animations='disabled')
   res['checks']['screenshot']=True
  except Exception as ex:res['checks']['screenshot']=False;res['errors'].append('screenshot: '+str(ex)[:140])
 res['status']='pass' if res['real_webgl2'] and res['loaded'] and res['checks'].get('guide_count')==13 and res['checks'].get('guide_verified') and res['checks'].get('initial_switch_on')=='true' and res['checks'].get('off')=='false' and res['checks'].get('back_on')=='true' and not res['request_missing'] else 'failed'
 (O/'V019_webgl2_qa.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
 print('CHECKS',res['checks'],'STATUS',res['status'],flush=True)
 browser.close()
raise SystemExit(0 if res['status']=='pass' else 2)