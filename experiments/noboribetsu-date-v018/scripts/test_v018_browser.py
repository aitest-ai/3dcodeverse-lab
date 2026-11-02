#!/usr/bin/env python3
"""Actual Chromium DOM event regression using unchanged V017 input modules, no WebGL claim."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json, hashlib
ROOT=Path(__file__).resolve().parent; D=ROOT/'base'/'dist'; OUT=ROOT/'outputs';OUT.mkdir(exist_ok=True)
source_files=['input-events.js','walk-session.js','navigation.js','controls.js']
source_shas={n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in source_files}
coll=json.loads((D/'collision.json').read_text())
for f in ('extension_collision.json','v005_collision.json','v006_collision.json'):
 v=json.loads((D/f).read_text());coll['walkable'].extend(v['walkable']);coll['obstacles'].extend(v['obstacles'])
route=json.loads((D/'scene_view.json').read_text())['route']
result={'schema':'noboribetsu-date-v018-chromium-dom-input/1','browser_dom':True,'physical_touch':False,'webgl_scene_loaded':False,'source_sha256':source_shas,'checks':[],'page_errors':[],'limitations':['Chromium DOM/PointerEvent regression only, not full WebGL scene','synthetic touch PointerEvent, not Android physical hardware','collision geometry author-estimated']}
html='''<!doctype html><html><head><base href="https://date.local/"></head><body><div id="scene" tabindex="0" style="width:350px;height:180px"></div><div id="joystick" style="width:94px;height:94px;position:absolute;left:15px;top:200px"><div id="stick"></div></div><script type="module">
import {CollisionWorld,collisionForStage,routeAt} from 'https://date.local/navigation.js';
import {WalkSession} from 'https://date.local/walk-session.js';
import {installInputControls} from 'https://date.local/input-events.js';
import {headingFromVector} from 'https://date.local/controls.js';
window.boot=(collision,route)=>{
 const world=new CollisionWorld(collisionForStage(collision,'B'),8);
 const variants={A:{visible:false},B:{visible:true}},session=new WalkSession({world,route,variants});session.start();
 const p=route.find(x=>x.s>=89.5);const g=world.ground(p.x,p.z,p.y,.45);session.position={x:p.x,y:g.y,z:p.z};session.heading=headingFromVector(route.find(x=>x.s>=90).x-p.x,route.find(x=>x.s>=90).z-p.z);
 const events=installInputControls({windowTarget:window,documentTarget:document,scene:document.querySelector('#scene'),joystickElement:document.querySelector('#joystick'),stickVisual:document.querySelector('#stick'),getSession:()=>session});
 window.s=session;window.events=events;window.tick=n=>{for(let i=0;i<n;i++)s.advance(.1)};window.pose=()=>({...s.position,heading:s.heading,pitch:s.pitch,stick:{...s.input.stick},keys:[...s.input.keys],stickPointer:s.input.stickPointer,lookPointer:s.input.lookPointer});return true;
};window.ready=true;
</script></body></html>'''
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu','--disable-dev-shm-usage'],timeout=20000)
 page=browser.new_page(viewport={'width':640,'height':420});page.on('pageerror',lambda e:result['page_errors'].append(str(e)))
 def intercept(req):
  p=D/req.request.url.split('date.local/',1)[-1]
  if p.is_file() and p.parent==D: req.fulfill(status=200,body=p.read_bytes(),headers={'Content-Type':'text/javascript','Access-Control-Allow-Origin':'*'})
  else:req.fulfill(status=404,body=b'')
 page.route('https://date.local/**',intercept)
 page.set_content(html,wait_until='load');page.wait_for_function('window.ready===true',timeout=10000)
 page.evaluate('(d)=>boot(d.c,d.r)',{'c':coll,'r':route})
 def check(name,cond,details):result['checks'].append({'name':name,'pass':bool(cond),**details})
 start=page.evaluate('pose()');page.locator('#scene').focus();page.keyboard.down('w');page.evaluate('tick(10)');moving=page.evaluate('pose()');page.keyboard.up('w');page.evaluate('tick(10)');stop=page.evaluate('pose()')
 delta=lambda a,b:((a['x']-b['x'])**2+(a['z']-b['z'])**2)**.5
 check('Keyboard W advances in Chromium DOM',delta(start,moving)>.15,{'distance_m':round(delta(start,moving),4)})
 check('Keyboard release stops movement',delta(moving,stop)<1e-8,{'drift_m':round(delta(moving,stop),9)})
 # Synthetic two-finger native PointerEvent dispatch to actual input handler.
 js='''()=>{const s=document.querySelector('#scene'),j=document.querySelector('#joystick');const E=(id,type,x,y,target)=>target.dispatchEvent(new PointerEvent(type,{bubbles:true,cancelable:true,pointerId:id,pointerType:'touch',isPrimary:id===41,buttons:type==='pointerup'?0:1,clientX:x,clientY:y}));
 const r=j.getBoundingClientRect(); E(41,'pointerdown',r.left+r.width/2,r.top+r.height/2,j);E(41,'pointermove',r.left+r.width/2,r.top+r.height/2-35,j);E(42,'pointerdown',200,80,s);E(42,'pointermove',235,90,s);return {stick:s===null?null:window.s.input.stick,lookPointer:window.s.input.lookPointer};}'''
 pointer=page.evaluate(js);pre=page.evaluate('pose()');page.evaluate('tick(8)');after=page.evaluate('pose()');
 check('Two simultaneous touch pointer owners',pre['stickPointer']==41 and pre['lookPointer'].get('id')==42,{'owners':[pre['stickPointer'],pre['lookPointer']]})
 check('Touch joystick moves and concurrent look rotates',delta(pre,after)>.1 and abs(after['heading']-start['heading'])>.04,{'move_m':round(delta(pre,after),3),'heading_delta_rad':round(after['heading']-start['heading'],4)})
 page.evaluate('''()=>{const j=document.querySelector('#joystick'),s=document.querySelector('#scene');j.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,pointerId:41,pointerType:'touch',buttons:0}));s.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,pointerId:42,pointerType:'touch',buttons:0}));}''')
 off=page.evaluate('pose()');page.evaluate('tick(7)');off2=page.evaluate('pose()')
 check('Both touch pointers released; no drift',off['stickPointer'] is None and off['lookPointer'] is None and delta(off,off2)<1e-8,{'drift_m':round(delta(off,off2),9)})
 page.keyboard.down('w');page.evaluate('tick(3)');blurBefore=page.evaluate('pose()');page.evaluate('window.dispatchEvent(new Event("blur"))');page.evaluate('tick(5)');blurAfter=page.evaluate('pose()');page.keyboard.up('w')
 check('Blur cancels input and prevents movement',not blurAfter['keys'] and delta(blurBefore,blurAfter)<1e-8,{'drift_m':round(delta(blurBefore,blurAfter),9)})
 result['chromium_version']=browser.version;browser.close()
result['pass']=bool(result['checks']) and all(c['pass'] for c in result['checks']) and not result['page_errors'];(OUT/'V018_browser_input_qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'pass':result['pass'],'checks':result['checks'],'page_errors':result['page_errors']},ensure_ascii=False,indent=2))
raise SystemExit(0 if result['pass'] else 1)