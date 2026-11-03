"""Real exported Godot Web game, native canvas GUI + actual keyboard/mouse. Snapshot is observation only."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json,math,time,statistics,os
R=Path(__file__).resolve().parents[1];E=R/'evidence';checks=[];errors=[];engine_errors=[];navigation=[];fps=[];report={}
def check(name,condition,detail=None):
 checks.append({'name':name,'pass':bool(condition),'detail':detail});print(name,condition,flush=True)
 if not condition:raise AssertionError(name+': '+str(detail))
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 ctx=b.new_context(viewport={'width':960,'height':600},record_video_dir=str(E/'video-raw'),record_video_size={'width':960,'height':600})
 page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:engine_errors.append(m.text) if m.type=='error' else None)
 snap=lambda:page.evaluate('window.__harborGodot')
 def advance(n=12):
  f=snap()['physics_frames'];page.wait_for_function('(n)=>window.__harborGodot.physics_frames>=n',arg=f+n,timeout=90000);fps.append(snap()['fps'])
 def click(id):
  s=snap();x,y=s['buttons'][id];r=page.locator('#canvas').bounding_box();page.mouse.click(r['x']+x/s['viewport'][0]*r['width'],r['y']+y/s['viewport'][1]*r['height']);advance()
 def release():
  for k in ['KeyW','KeyA','KeyS','KeyD','ShiftLeft']:page.keyboard.up(k)
 def go(x,z,tol=.35,timeout=90,stop_near=None):
  held=set();t=time.monotonic()
  while time.monotonic()-t<timeout:
   s=snap();dx=x-s['position'][0];dz=z-s['position'][2]
   if math.hypot(dx,dz)<tol or (stop_near and s['nearest']==stop_near):break
   desired={'ShiftLeft'}
   if abs(dx)>.12:desired.add('KeyD' if dx>0 else 'KeyA')
   if abs(dz)>.12:desired.add('KeyS' if dz>0 else 'KeyW')
   for k in ['KeyW','KeyA','KeyS','KeyD','ShiftLeft']:
    if k not in desired:page.keyboard.up(k)
   for k in desired:page.keyboard.down(k)
   held=desired;advance(12)
  release();advance(15);s=snap();distance=math.hypot(x-s['position'][0],z-s['position'][2]);navigation.append({'target':[x,z],'position':s['position'],'error_m':distance})
  if distance>tol+.35 and not (stop_near and s['nearest']==stop_near):raise AssertionError('Blocked navigation '+str(navigation[-1]))
 try:
  page.goto(os.environ.get('HARBOR_URL','http://127.0.0.1:8130/'),wait_until='domcontentloaded');page.wait_for_function('window.__harborGodot?.ready',timeout=120000)
  page.screenshot(path=str(E/'godot-standard.png'));click('start');check('Actual mature engine Web build starts',snap()['started'] and 'Godot 4.6.3' in snap()['engine'])
  a=snap()['bones'];advance(20);check('Idle has real changing bone poses',a!=snap()['bones'])
  page.keyboard.press('KeyQ');advance();check('User low-quality setting switches shadows off',snap()['low_quality'])
  p0=snap()['position'];page.keyboard.down('KeyW');advance(20);walk=snap();page.keyboard.up('KeyW');advance(20)
  check('Native CharacterBody3D moves using W and AnimationTree selects Walk',walk['position'][2]<p0[2]-.1 and walk['motion']=='Walk',walk['position'])
  check('Deceleration returns to Idle',snap()['motion']=='Idle')
  yaw=snap()['camera_yaw'];page.mouse.move(520,330);page.mouse.down();page.mouse.move(620,330,steps=6);page.mouse.up();advance();check('Mouse drag rotates actual SpringArm rig',abs(snap()['camera_yaw']-yaw)>.25)
  page.mouse.move(620,330);page.mouse.down();page.mouse.move(520,330,steps=6);page.mouse.up();advance();check('Inverse drag restores navigation heading',abs(snap()['camera_yaw'])<.1,snap()['camera_yaw'])
  before=snap()['npcs'];advance(180);after=snap()['npcs'];check('Both NPCs patrol in engine physics',all(math.dist(a['position'],c['position'])>.05 for a,c in zip(before,after)),[before,after])
  n=next(n for n in snap()['npcs'] if n['id']=='guide');go(n['position'][0],n['position'][2]+1.5,stop_near='guide')
  page.keyboard.press('KeyE');advance();check('E opens native NPC dialogue and two route choices',snap()['dialog'] and 'accept_slow' in snap()['buttons'] and 'accept_express' in snap()['buttons'])
  page.screenshot(path=str(E/'godot-choice.png'));click('accept_express');check('Express choice changes task rules',snap()['quest']==1 and snap()['express'])
  for x,z in [(-5,-4),(-5,2.5),(-2,2.5),(-2,9),(6,9)]:go(x,z)
  check('Three native pickups collected exactly once',len(snap()['collected'])==3 and snap()['score']==75,snap()['collected'])
  for x,z in [(13,9),(13,-5)]:go(x,z)
  n=next(n for n in snap()['npcs'] if n['id']=='keeper');go(n['position'][0],n['position'][2]+1.6,stop_near='keeper')
  page.keyboard.press('KeyE');advance();check('Second NPC accepts completed handout','deliver' in snap()['buttons'])
  click('deliver');check('Complete route awards base reward and timely express bonus',snap()['quest']==3 and snap()['score']==200,snap()['score']);page.screenshot(path=str(E/'godot-complete.png'));click('continue')
  page.keyboard.press('KeyV');advance(15);page.screenshot(path=str(E/'godot-portrait.png'))
  page.keyboard.press('KeyV');advance(15);page.keyboard.press('KeyB');advance();check('Facial morph responds to actual B key',snap()['smile']>.9);page.screenshot(path=str(E/'godot-face.png'))
  for key,name in [('Digit1','Idle'),('Digit2','Walk'),('Digit3','Run')]:
   page.keyboard.press(key);advance(20);a=snap()['bones'];advance(20);check('Live atelier '+name+' animates skeleton',a!=snap()['bones']);page.screenshot(path=str(E/('godot-preview-'+name.lower()+'.png')))
  page.keyboard.press('KeyV');advance();go(0,-5)
  page.keyboard.down('KeyW');advance(160);page.keyboard.up('KeyW');advance(18);check('CharacterBody cannot pass through solid building',snap()['position'][2]>-7.15,snap()['position'])
  page.mouse.move(400,300);page.mouse.down();page.mouse.move(400+math.pi/.005,300,steps=12);page.mouse.up();advance(15)
  check('Native SpringArm retracts before building',snap()['arm_length']<snap()['desired_arm']-1,{'hit':snap()['arm_length'],'desired':snap()['desired_arm']})
  check('No JS or engine runtime errors',not errors and not engine_errors,errors+engine_errors)
  report={'status':'PASS','checks':checks,'navigation':navigation,'final':snap(),'performance':{'renderer':'Chromium ANGLE SwiftShader software','viewport_css':[960,600],'quality':'low/shadows off during gameplay checks','fps_median_observed':statistics.median(fps),'hardware_certification':False},'errors':errors,'engine_errors':engine_errors}
 except Exception as e:
  page.screenshot(path=str(E/'godot-qa-failure.png'));report={'status':'FAIL','error':str(e),'checks':checks,'navigation':navigation,'snapshot':snap(),'errors':errors,'engine_errors':engine_errors};raise
 finally:
  (E/'godot-browser-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));video=page.video;ctx.close();video.save_as(str(E/'godot-gameplay.webm'));b.close()
