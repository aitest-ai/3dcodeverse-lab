#!/usr/bin/env python3
"""Isolated real Chromium/WebGL2. Test-only digest adapter, not production asset."""
import hashlib,gzip,json,mimetypes,os,subprocess,time,traceback
from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent;D=ROOT/'base/dist';OUT=ROOT/'outputs';OUT.mkdir(exist_ok=True)
scene=json.loads((D/'scene_view.json').read_text());by_size={}
checks=[]
# Hashes independently calculated on raw files before exposing any renderer-facing fake SHA adapter.
names=['assets/scene_A.glb',*[f'assets/scene_B.part{i:02d}.bin' for i in range(1,24)],
'assets/v004_merchant_road.glb','assets/v004_merchant_facades.glb','assets/v004_merchant_signs.glb',
'assets/v005_east_road.glb','assets/v005_east_facades.glb','assets/v005_east_signs.glb','assets/v006_tail_road.glb','assets/v009_utsuroi_facade.glb',
'v011_terrain_gap_patch.json','v012_road_grass_transition.json','v013_selective_road_grass.json','v014_center_stones.json','v015_post_grounding.json','v016_grade_inspection.json','v017_clearance_audit.json']
for name in names:
 raw=(D/name).read_bytes();sha=hashlib.sha256(raw).hexdigest()
 k=str(len(raw))
 if k in by_size and by_size[k]!=sha:raise ValueError('length collision '+name)
 by_size[k]=sha;checks.append({'path':name,'bytes':len(raw),'sha256':sha})
braw=gzip.decompress(b''.join((D/f'assets/scene_B.part{i:02d}.bin').read_bytes() for i in range(1,24)))
assert hashlib.sha256(braw).hexdigest()==next(m['sha256'] for m in scene['models'] if m['stage']=='B')
by_size[str(len(braw))]=hashlib.sha256(braw).hexdigest()
for name,key in [('v011_terrain_gap_patch.json','terrain_gap_v011'),('v012_road_grass_transition.json','transition_v012'),('v013_selective_road_grass.json','transition_v013'),('v014_center_stones.json','v014_center_stones'),('v015_post_grounding.json','grounding_v015'),('v016_grade_inspection.json','footing_v016'),('v017_clearance_audit.json','clearance_v017')]:
 assert hashlib.sha256((D/name).read_bytes()).hexdigest()==scene[key]['sha256']
result={'schema':'noboribetsu-date-v017-isolated-webgl2/1','real_webgl2':False,'loaded':None,'success':False,'source_sha_verified_independently':True,'test_only_sha_adapter':True,'production_runtime_sha_guard_unchanged':True,'limitations':['virtual subresource routing from about:blank','no true localhost native WebCrypto','no Android physical device','visual stone footing artist-estimated'],'page_errors':[],'missing':[],'checks_count':len(checks)}
hook='''
window.__V017_QA_CAMERA__=(enabled)=>{if(!renderReady||!B)return null;
const m=B.getObjectByName('V017_CLEARANCE_INSPECTION');if(!m)return null;
m.visible=enabled; camera.position.set(37.5,3.70,65.0);camera.lookAt(40.2,1.5,58.4);camera.updateMatrixWorld();
renderer.render(scene,camera); return {mesh:m.name,visible:m.visible,markers:m.children.length,pose:camera.position.toArray(),metrics:window.__DATE_METRICS__.v017_clearance};};
'''
js_map='''(map)=>{const s={digest:async(a,v)=>{if(String(a).toUpperCase()!=='SHA-256')throw Error('algorithm');const hex=map[String(v.byteLength)];if(!hex)throw Error('SHA adapter unknown length '+v.byteLength);return Uint8Array.from(hex.match(/../g),n=>parseInt(n,16)).buffer;}};Object.defineProperty(crypto,'subtle',{value:s,configurable:true});window.__TEST_SHA_ONLY__=true;}'''
xvfb=None
if True:
 xvfb=subprocess.Popen(['Xvfb',':171','-screen','0','1280x800x24','-nolisten','tcp'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);os.environ['DISPLAY']=':171';time.sleep(.7)
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=False,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--ignore-gpu-blocklist','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-extensions'],timeout=40000)
  page=browser.new_page(viewport={'width':640,'height':400},device_scale_factor=1)
  page.on('pageerror',lambda e:result['page_errors'].append(str(e)[:400]))
  def route(req):
   name=req.request.url.split('date.local/',1)[-1].split('?',1)[0]
   f=(D/name).resolve()
   if not f.is_relative_to(D.resolve()) or not f.is_file():result['missing'].append(name);req.fulfill(status=404,body=b'');return
   typ=mimetypes.guess_type(f)[0] or 'application/octet-stream'
   if f.suffix=='.js':typ='text/javascript'
   req.fulfill(status=200,body=f.read_text()+hook if name=='app.js' else f.read_bytes(),headers={'Content-Type':typ,'Access-Control-Allow-Origin':'*'})
  page.route('https://date.local/**',route)
  page.evaluate(js_map,by_size)
  page.set_content((D/'index.html').read_text().replace('<head>','<head><base href="https://date.local/">',1),wait_until='domcontentloaded')
  result['real_webgl2']=page.evaluate("!!document.createElement('canvas').getContext('webgl2')")
  print('WebGL2',result['real_webgl2'],flush=True)
  page.wait_for_function("document.getElementById('scene').dataset.loaded==='true'||document.getElementById('scene').dataset.loaded==='failed'",timeout=185000,polling=700)
  result['loaded']=page.evaluate("document.getElementById('scene').dataset.loaded")
  print('loaded',result['loaded'],flush=True)
  if result['loaded']=='true':
   page.locator('#enterButton').click(timeout=30000)
   result['metrics']=page.evaluate("({v011:__DATE_METRICS__.v011_terrain_gap,v012:__DATE_METRICS__.v012_road_grass,v013:__DATE_METRICS__.v013_road_grass,v014:__DATE_METRICS__.v014_center_stones,v015:__DATE_METRICS__.v015_grounding,v016:__DATE_METRICS__.v016_inspection,v017:__DATE_METRICS__.v017_clearance,renderer:__DATE_METRICS__.renderer})")
   print('metrics',json.dumps(result['metrics'],ensure_ascii=False)[:800],flush=True)
   pose=page.evaluate('(v)=>window.__V017_QA_CAMERA__(v)',False)
   assert pose and pose['markers']==4
   result['markers'] = pose['markers']
   result['default_visible'] = pose['metrics']['markers_visible']
   result['toggle_observed']=page.evaluate("(()=>{const b=document.getElementById('clearanceToggleButton');const m=__DATE_METRICS__;const init=b.getAttribute('aria-pressed');b.click();const on=b.getAttribute('aria-pressed');b.click();const off=b.getAttribute('aria-pressed');return {initial:init,on,off,metric:m.v017_clearance.markers_visible,disabled:b.disabled};})()")
   result['success']=bool(result['real_webgl2'] and result['metrics']['v015']['support_count']==8 and
     result['metrics']['v017']['sample_count']==237 and result['default_visible'] is False and
     result['toggle_observed']['initial']=='false' and result['toggle_observed']['on']=='true' and
     result['toggle_observed']['off']=='false' and result['toggle_observed']['metric'] is False and
     not result['toggle_observed']['disabled'])
   print('toggle',result['toggle_observed'],'success',result['success'],flush=True)
  else:result['load_error']=page.evaluate("document.getElementById('loadError').textContent")
  try:browser.close()
  except Exception as ex:result['browser_close_warning']=str(ex)[:240]
except Exception as ex:
 result['exception']=repr(ex);print('ERROR',repr(ex),flush=True)
finally:
 if xvfb:
  xvfb.terminate()
  try:xvfb.wait(timeout=5)
  except:pass
(OUT/'V017_webgl_qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('final',json.dumps({k:v for k,v in result.items() if k in ('real_webgl2','loaded','success','pixels_changed_gt12','exception','load_error')},ensure_ascii=False),flush=True)
raise SystemExit(0 if result['success'] and not result['page_errors'] and not result['missing'] else 2)