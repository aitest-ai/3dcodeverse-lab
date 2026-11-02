#!/usr/bin/env python3
"""Chromium mobile emulation with actual SwiftShader WebGL2, simulated pointer events.
NOT an Android real-device test and uses TEST-ONLY digest adapter as documented.
"""
import hashlib,json,mimetypes,os,sys
from pathlib import Path
from playwright.sync_api import sync_playwright,TimeoutError
from verify_all_assets import verify
ROOT=Path(os.environ['DATE_DIST_ROOT']);OUT=Path(os.environ['DATE_QA_DIR']);OUT.mkdir(exist_ok=True,parents=True)
models=verify();hash_map={str(d['bytes']):d['sha256'] for d in models}
for filename in ['v011_terrain_gap_patch.json','v012_road_grass_transition.json']:
 patch=ROOT/filename;hash_map[str(patch.stat().st_size)]=hashlib.sha256(patch.read_bytes()).hexdigest()
adapter=r'''shaMap=>{Object.defineProperty(crypto,'subtle',{configurable:true,value:{digest:async(algorithm,buffer)=>{
 const hex=shaMap[String(buffer.byteLength)];if(!hex)throw Error('QA digest: unknown length');
 return Uint8Array.from(hex.match(/.{2}/g),x=>parseInt(x,16)).buffer;
}}});window.__QA_ONLY__=true;}'''
report={'schema':'v012-mobile-emulation/1','device':'Chromium portrait 430x932 touch emulation','android_real_device':False,
 'webgl2':False,'simulated_crypto':True,'model_sha_independently_verified':all(r['pass'] for r in models),
 'result':'FAIL'}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-webgl','--ignore-gpu-blocklist','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'],timeout=20000)
 page=browser.new_page(viewport={'width':430,'height':932},device_scale_factor=1,is_mobile=True,has_touch=True)
 errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
 def route(r):
  name=r.request.url.split('date.local/',1)[-1].split('?',1)[0];f=ROOT/name
  if not f.is_file() or not f.resolve().is_relative_to(ROOT):r.fulfill(status=404,body=b'');return
  mime=mimetypes.guess_type(str(f))[0] or 'application/octet-stream'
  if f.suffix=='.js':mime='text/javascript'
  r.fulfill(status=200,path=str(f),headers={'Access-Control-Allow-Origin':'*','Content-Type':mime})
 page.route('https://date.local/**',route)
 page.evaluate(adapter,hash_map)
 html=(ROOT/'index.html').read_text('utf8').replace('<head>','<head><base href="https://date.local/">',1)
 page.set_content(html,wait_until='domcontentloaded')
 report['webgl2']=page.evaluate("!!document.createElement('canvas').getContext('webgl2')")
 try:page.wait_for_function("['true','failed'].includes(document.getElementById('scene').dataset.loaded)",timeout=150000,polling=600)
 except TimeoutError:pass
 report['loaded']=page.evaluate("document.getElementById('scene').dataset.loaded")
 if report['loaded']=='true':
  page.evaluate("document.getElementById('enterButton').click()")
  before=page.evaluate("document.getElementById('scene').dataset.position")
  page.evaluate('''() => {
   const j=document.getElementById('joystick'),s=document.getElementById('scene');
   let rect=j.getBoundingClientRect(),x=rect.left+rect.width/2,y=rect.top+rect.height/2;
   function event(el,type,id,xx,yy){el.dispatchEvent(new PointerEvent(type,{bubbles:true,cancelable:true,
      pointerId:id,pointerType:'touch',isPrimary:id===71,buttons:type==='pointerup'?0:1,button:0,clientX:xx,clientY:yy}));}
   event(j,'pointerdown',71,x,y);event(s,'pointerdown',72,260,490);
   event(j,'pointermove',71,x,y-28);event(s,'pointermove',72,306,490);
   window.__qaTouch={j,s,x,y,event};
  }''')
  page.wait_for_timeout(1100)
  page.evaluate("""() => {const q=window.__qaTouch;q.event(q.j,'pointerup',71,q.x,q.y-28);q.event(q.s,'pointerup',72,306,490)}""")
  after=page.evaluate("document.getElementById('scene').dataset.position")
  heading=page.evaluate("document.getElementById('scene').dataset.heading")
  page.wait_for_timeout(550)
  stop=page.evaluate("document.getElementById('scene').dataset.position")
  dist=lambda a,b:sum((float(x)-float(y))**2 for x,y in zip(a.split(','),b.split(',')))**.5
  report.update({'position_before':before,'position_after':after,'position_stopped':stop,
    'movement_m':dist(before,after),'drift_m':dist(after,stop),'heading':float(heading),
    'terrain_metrics':page.evaluate("window.__DATE_METRICS__.v011_terrain_gap"),
    'road_grass_metrics':page.evaluate("window.__DATE_METRICS__.v012_road_grass")})
  page.screenshot(path=str(OUT/'V012_Mobile_Emulated_WebGL2.png'),animations='disabled',timeout=25000)
  report['result']='PASS' if report['movement_m']>.1 and report['drift_m']<.02 and abs(report['heading'])>.01 else 'FAIL'
 report['errors']=errs
 (OUT/'V012_mobile_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False),flush=True)
 browser.close()
sys.exit(0 if report['result']=='PASS' else 2)