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
'v011_terrain_gap_patch.json','v012_road_grass_transition.json','v013_selective_road_grass.json','v014_center_stones.json','v015_post_grounding.json']
for name in names:
 raw=(D/name).read_bytes();sha=hashlib.sha256(raw).hexdigest()
 k=str(len(raw))
 if k in by_size and by_size[k]!=sha:raise ValueError('length collision '+name)
 by_size[k]=sha;checks.append({'path':name,'bytes':len(raw),'sha256':sha})
braw=gzip.decompress(b''.join((D/f'assets/scene_B.part{i:02d}.bin').read_bytes() for i in range(1,24)))
assert hashlib.sha256(braw).hexdigest()==next(m['sha256'] for m in scene['models'] if m['stage']=='B')
by_size[str(len(braw))]=hashlib.sha256(braw).hexdigest()
for name,key in [('v011_terrain_gap_patch.json','terrain_gap_v011'),('v012_road_grass_transition.json','transition_v012'),('v013_selective_road_grass.json','transition_v013'),('v014_center_stones.json','v014_center_stones'),('v015_post_grounding.json','grounding_v015')]:
 assert hashlib.sha256((D/name).read_bytes()).hexdigest()==scene[key]['sha256']
result={'schema':'noboribetsu-date-v015-isolated-webgl2/1','real_webgl2':False,'loaded':None,'success':False,'source_sha_verified_independently':True,'test_only_sha_adapter':True,'production_runtime_sha_guard_unchanged':True,'limitations':['virtual subresource routing from about:blank','no true localhost native WebCrypto','no Android physical device','visual stone footing artist-estimated'],'page_errors':[],'missing':[],'checks_count':len(checks)}
hook='''
window.__V015_QA_CAMERA__=(enabled)=>{if(!renderReady||!B)return null;
const m=B.getObjectByName('V015_V004_POST_GROUNDING_VISUAL_ONLY');if(!m)return null;
m.visible=enabled; camera.position.set(8.4,2.40,64.0);camera.lookAt(9.2,1.8,52.0);camera.updateMatrixWorld();
renderer.render(scene,camera); return {mesh:m.name,visible:m.visible,vertices:m.geometry.attributes.position.count,triangles:m.geometry.index.count/3,pose:camera.position.toArray(),metrics:window.__DATE_METRICS__.v015_grounding};};
'''
js_map='''(map)=>{const s={digest:async(a,v)=>{if(String(a).toUpperCase()!=='SHA-256')throw Error('algorithm');const hex=map[String(v.byteLength)];if(!hex)throw Error('SHA adapter unknown length '+v.byteLength);return Uint8Array.from(hex.match(/../g),n=>parseInt(n,16)).buffer;}};Object.defineProperty(crypto,'subtle',{value:s,configurable:true});window.__TEST_SHA_ONLY__=true;}'''
xvfb=None
if True:
 xvfb=subprocess.Popen(['Xvfb',':149','-screen','0','1280x800x24','-nolisten','tcp'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);os.environ['DISPLAY']=':149';time.sleep(.7)
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=False,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--ignore-gpu-blocklist','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-extensions'],timeout=40000)
  page=browser.new_page(viewport={'width':960,'height':600},device_scale_factor=1)
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
  page.wait_for_function("document.getElementById('scene').dataset.loaded==='true'||document.getElementById('scene').dataset.loaded==='failed'",timeout=205000,polling=700)
  result['loaded']=page.evaluate("document.getElementById('scene').dataset.loaded")
  print('loaded',result['loaded'],flush=True)
  if result['loaded']=='true':
   page.locator('#enterButton').click(timeout=30000)
   result['metrics']=page.evaluate("({v011:__DATE_METRICS__.v011_terrain_gap,v012:__DATE_METRICS__.v012_road_grass,v013:__DATE_METRICS__.v013_road_grass,v014:__DATE_METRICS__.v014_center_stones,v015:__DATE_METRICS__.v015_grounding,renderer:__DATE_METRICS__.renderer})")
   print('metrics',json.dumps(result['metrics'],ensure_ascii=False)[:800],flush=True)
   for enabled,label in [(False,'before'),(True,'after')]:
    pose=page.evaluate('(v)=>window.__V015_QA_CAMERA__(v)',enabled);assert pose and pose['triangles']==96
    result[label+'_pose']=pose
    page.wait_for_timeout(800)
    path=OUT/f'V015_V004_Footing_{label}_RealWebGL2.png';page.screenshot(path=str(path),timeout=80000,animations='disabled')
    print(label,path.stat().st_size,flush=True)
   a=np.asarray(Image.open(OUT/'V015_V004_Footing_before_RealWebGL2.png').convert('RGB'),dtype=np.int16)
   b=np.asarray(Image.open(OUT/'V015_V004_Footing_after_RealWebGL2.png').convert('RGB'),dtype=np.int16)
   result['pixels_changed_gt12']=int(np.any(abs(a-b)>12,axis=2).sum())
   result['toggle_observed']=page.evaluate("(()=>{const m=document.getElementById('footingToggleButton');m.click();let a=m.getAttribute('aria-pressed');m.click();return {first:a,second:m.getAttribute('aria-pressed'),metric:window.__DATE_METRICS__.v015_grounding.visible}})()")
   print('pixels',result['pixels_changed_gt12'],'toggle',result['toggle_observed'],flush=True)
   result['success']=bool(result['real_webgl2'] and result['metrics']['v015']['support_count']==8 and result['metrics']['v011'] and result['metrics']['v012'] and result['metrics']['v013'] and result['metrics']['v014'] and result['pixels_changed_gt12']>40)
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
(OUT/'V015_webgl_qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('final',json.dumps({k:v for k,v in result.items() if k in ('real_webgl2','loaded','success','pixels_changed_gt12','exception','load_error')},ensure_ascii=False),flush=True)
raise SystemExit(0 if result['success'] and not result['page_errors'] and not result['missing'] else 2)