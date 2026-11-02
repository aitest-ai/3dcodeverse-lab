#!/usr/bin/env python3
"""Isolated Chromium WebGL2 screenshot QA. TEST-ONLY fake SHA adapter NEVER ships."""
import os,json,hashlib,gzip,mimetypes,subprocess,time,signal,traceback
from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright,TimeoutError
ROOT=Path(__file__).resolve().parent;D=ROOT/'candidate'/'dist';OUT=ROOT/'evidence';OUT.mkdir(exist_ok=True)
scene=json.loads((D/'scene_view.json').read_text())
assert scene['v014_center_stones']['stage']=='B'
# Independent full file SHA checks; gzip decoded B gets a second hash check.
checks=[]; by_size={}
for name in ['assets/scene_A.glb',*[f'assets/scene_B.part{i:02d}.bin' for i in range(1,24)],
 'assets/v004_merchant_road.glb','assets/v004_merchant_facades.glb','assets/v004_merchant_signs.glb',
 'assets/v005_east_road.glb','assets/v005_east_facades.glb','assets/v005_east_signs.glb',
 'assets/v006_tail_road.glb','assets/v009_utsuroi_facade.glb',
 'v011_terrain_gap_patch.json','v012_road_grass_transition.json','v013_selective_road_grass.json','v014_center_stones.json']:
 f=D/name;raw=f.read_bytes();digest=hashlib.sha256(raw).hexdigest();checks.append({'path':name,'bytes':len(raw),'sha256':digest});key=str(len(raw))
 if key in by_size and by_size[key]!=digest: raise RuntimeError('TEST adapter unsafe length hash conflict '+name)
 by_size[key]=digest
# Internal app may hash decoded B, not individual pieces.
braw=gzip.decompress(b''.join((D/f'assets/scene_B.part{i:02d}.bin').read_bytes() for i in range(1,24)))
assert hashlib.sha256(braw).hexdigest()==scene['models'][0]['sha256']
by_size[str(len(braw))]=hashlib.sha256(braw).hexdigest()
for n in ['v011_terrain_gap_patch.json','v012_road_grass_transition.json','v013_selective_road_grass.json','v014_center_stones.json']:
 key={'v011_terrain_gap_patch.json':'terrain_gap_v011','v012_road_grass_transition.json':'transition_v012','v013_selective_road_grass.json':'transition_v013','v014_center_stones.json':'v014_center_stones'}[n]
 assert hashlib.sha256((D/n).read_bytes()).hexdigest()==scene[key]['sha256']
result={'schema':'noboribetsu-date-v014-isolated-webgl2/1','model_sha_python_verified':True,'production_hash_code_untouched':True,'test_only_sha_adapter':True,'real_webgl2':False,'success':False,'errors':[],'missing':[],'screenshots':[],'device':'Xvfb Chromium SwiftShader simulated GPU (not Android)', 'limitations':['about:blank virtual subresources','no private website/CDN/HTTPS test','no native WebCrypto test','photo-inspired location estimated']}
# Prevent accidental use of test adapter in actual Runtime.
js_map='''(map)=>{const s={digest:async(a,v)=>{if(String(a).toUpperCase()!=='SHA-256')throw Error('algorithm');const hex=map[String(v.byteLength)];if(!hex)throw Error('SHA adapter unknown length '+v.byteLength);return Uint8Array.from(hex.match(/../g),n=>parseInt(n,16)).buffer;}};Object.defineProperty(crypto,'subtle',{value:s,configurable:true});window.__TEST_SHA_ONLY__=true;}'''
hook='''\nwindow.__V014_QA_JUMP__=(s,enabled)=>{if(!session||!renderReady)return null;
 const p=manifest.route.reduce((a,b)=>Math.abs(a.s-s)<Math.abs(b.s-s)?a:b);const i=manifest.route.indexOf(p);
 const lo=manifest.route[Math.max(0,i-2)],hi=manifest.route[Math.min(manifest.route.length-1,i+2)];
 session.position={x:p.x,y:p.y,z:p.z};session.heading=Math.atan2(hi.x-lo.x,-(hi.z-lo.z));session.pitch=-0.14;
 const mesh=B.getObjectByName('V014_V004_OPTIONAL_CENTRAL_STONE_STUDY');if(mesh)mesh.visible=enabled;
 updateCamera();updateStatus();miniMap();renderer.render(scene,camera);
 return {loaded:!!mesh,visible:mesh?.visible,heading:session.heading,position:p,triangles:window.__DATE_METRICS__.v014_center_stones?.triangles};};
'''
errors=[];missing=[]
# Xvfb is isolated, not display manager mutation.
xvfb=None
if not os.environ.get('DISPLAY'):
 xvfb=subprocess.Popen(['Xvfb',':138','-screen','0','1280x800x24','-nolisten','tcp'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);os.environ['DISPLAY']=':138';time.sleep(.8)
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=False,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--ignore-gpu-blocklist','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-extensions','--disable-background-timer-throttling'],timeout=45000)
  page=browser.new_page(viewport={'width':850,'height':510},device_scale_factor=1)
  page.on('pageerror',lambda e:errors.append(str(e)[:500]))
  def serve(route):
   name=route.request.url.split('date.local/',1)[-1].split('?',1)[0]
   p=(D/name).resolve()
   if not p.is_relative_to(D.resolve()) or not p.is_file():
    missing.append(name);route.fulfill(status=404,body=b'');return
   typ=mimetypes.guess_type(str(p))[0] or 'application/octet-stream'
   if p.suffix=='.js':typ='text/javascript'
   route.fulfill(status=200,body=(p.read_text()+hook if name=='app.js' else p.read_bytes()),headers={'Content-Type':typ,'Access-Control-Allow-Origin':'*'})
  page.route('https://date.local/**',serve)
  page.evaluate(js_map,by_size)
  page.set_content((D/'index.html').read_text().replace('<head>','<head><base href="https://date.local/">',1),wait_until='domcontentloaded')
  result['real_webgl2']=page.evaluate("!!document.createElement('canvas').getContext('webgl2')")
  print('V014 webgl2',result['real_webgl2'],flush=True)
  page.wait_for_function("document.getElementById('scene').dataset.loaded==='true'||document.getElementById('scene').dataset.loaded==='failed'",timeout=220000,polling=650)
  result['loaded']=page.evaluate("document.getElementById('scene').dataset.loaded")
  print('V014 loaded',result['loaded'],flush=True)
  if result['loaded']=='true':
   page.locator('#enterButton').click(timeout=35000)
   result['metrics']=page.evaluate("({v011:window.__DATE_METRICS__.v011_terrain_gap,v012:window.__DATE_METRICS__.v012_road_grass,v013:window.__DATE_METRICS__.v013_road_grass,v014:window.__DATE_METRICS__.v014_center_stones,render:window.__DATE_METRICS__.renderer,webgl:window.__DATE_METRICS__.webgl})")
   print('metrics',json.dumps(result['metrics'],ensure_ascii=False)[:1100],flush=True)
   for on,label in [(False,'before'),(True,'after')]:
    pose=page.evaluate('(o)=>window.__V014_QA_JUMP__(102,o)',on)
    print(label,pose,flush=True)
    assert pose and pose['loaded'] and pose['triangles']==100
    page.wait_for_timeout(500)
    name=f'V014_V004_{label}_RealWebGL2.png';dst=OUT/name
    page.screenshot(path=str(dst),timeout=90000,animations='disabled')
    result['screenshots'].append({'file':name,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'bytes':dst.stat().st_size})
   a=np.array(Image.open(OUT/'V014_V004_before_RealWebGL2.png').convert('RGB'),dtype=np.int16)
   b=np.array(Image.open(OUT/'V014_V004_after_RealWebGL2.png').convert('RGB'),dtype=np.int16)
   diff=np.abs(a-b);changed=np.any(diff>14,axis=2)
   result['pixel_compare']={'changed_over_14_count':int(changed.sum()),'fraction':float(changed.mean()),'mean_abs':float(diff.mean())}
   print('pixels',result['pixel_compare'],flush=True)
   # Real DOM button path: user can toggle without touching any source geometry.
   page.locator('#stoneToggleButton').click(timeout=30000)
   toggled_off=page.evaluate("({on:document.getElementById('stoneToggleButton').getAttribute('aria-pressed'),visible:window.__DATE_METRICS__.v014_center_stones.visible})")
   page.locator('#stoneToggleButton').click(timeout=30000)
   toggled_on=page.evaluate("({on:document.getElementById('stoneToggleButton').getAttribute('aria-pressed'),visible:window.__DATE_METRICS__.v014_center_stones.visible})")
   result['user_toggle_pass']=(toggled_off=={'on':'false','visible':False} and toggled_on=={'on':'true','visible':True})
   print('user toggle',toggled_off,toggled_on,flush=True)
   # Lazy-load A once and restore B; camera world pose must not move.
   page.locator('#aButton').click(timeout=35000)
   page.wait_for_function("document.getElementById('scene').dataset.stage==='A'",timeout=70000)
   page.locator('#bButton').click(timeout=35000)
   page.wait_for_function("document.getElementById('scene').dataset.stage==='B'",timeout=45000)
   result['ab_switch']=page.evaluate("window.__DATE_METRICS__.stage_switches.slice(-2)")
   result['ab_pose_zero']=all(max(row['eye_delta_m'],row['target_delta_m'],row['up_delta'],row['fov_delta'])<1e-8 for row in result['ab_switch'])
   print('AB return',result['ab_pose_zero'],flush=True)
   result['success']=bool(result['real_webgl2'] and result['metrics']['v014']['stones']==50 and result['metrics']['v011'] and result['metrics']['v012'] and result['metrics']['v013'] and changed.sum()>90 and result['user_toggle_pass'] and result['ab_pose_zero'])
  else:result['load_error']=page.evaluate("document.getElementById('loadError').textContent")
  browser.close()
finally:
 if xvfb:xvfb.terminate();xvfb.wait(timeout=5)
result['errors']=errors;result['missing']=missing
(OUT/'V014_webgl_qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('final',result['success'],len(errors),len(missing),flush=True)
raise SystemExit(0 if result['success'] and not errors and not missing else 2)