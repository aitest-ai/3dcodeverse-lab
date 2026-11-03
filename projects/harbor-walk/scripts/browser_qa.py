"""Real Chromium/WebGL + DOM/keyboard/mouse QA; read-only snapshot, no teleport or quest mutation."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json,time,math,statistics,os
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'evidence';results=[];observations=[];errors=[]
def check(name,condition,detail=None):
 results.append({'name':name,'pass':bool(condition),'detail':detail});print(name,condition,flush=True)
 if not condition:raise AssertionError(name+': '+str(detail))
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 context=browser.new_context(viewport={'width':960,'height':600},record_video_dir=str(E/'video-raw'),record_video_size={'width':960,'height':600})
 page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
 snap=lambda:page.evaluate('window.__harbor.snapshot()')
 def advance(frames=5):
  start=snap()['frames'];page.wait_for_function('(n)=>window.__harbor.snapshot().frames>=n',arg=start+frames,timeout=60000)
 def release():
  for k in ['KeyW','KeyA','KeyS','KeyD','ShiftLeft']:page.keyboard.up(k)
 def go(x,z,tolerance=.35,timeout=150):
  began=time.monotonic();held=set()
  while time.monotonic()-began<timeout:
   s=snap();dx=x-s['position'][0];dz=z-s['position'][2]
   if math.hypot(dx,dz)<tolerance:break
   desired={'ShiftLeft'}
   if abs(dx)>.16:desired.add('KeyD' if dx>0 else 'KeyA')
   if abs(dz)>.16:desired.add('KeyS' if dz>0 else 'KeyW')
   for k in held-desired:page.keyboard.up(k)
   for k in desired-held:page.keyboard.down(k)
   held=desired;advance(3)
  release();advance(6)
  s=snap();observations.append({'target':[x,z],'position':s['position'],'distance':math.hypot(x-s['position'][0],z-s['position'][2]),'frames':s['frames']})
  if math.hypot(x-s['position'][0],z-s['position'][2])>tolerance+.4:raise AssertionError('Navigation did not reach '+str([x,z])+' '+str(s['position']))
 try:
  page.goto('http://127.0.0.1:5173/',wait_until='domcontentloaded');page.wait_for_function('window.__harbor?.snapshot().ready',timeout=90000)
  page.locator('#quality').click();page.locator('#start').click();advance(8)
  check('WebGL game renders with a real skinned GLB',snap()['render']['triangles']>30000,snap()['render'])
  a=snap();advance(8);b=snap();check('Idle bone quaternions change over time',a['bones']!=b['bones'])
  # Real drag rotates camera; inverse drag restores yaw for physical keyboard navigation.
  before=snap()['camera']['yaw'];page.mouse.move(510,410);page.mouse.down();page.mouse.move(610,420,steps=5);page.mouse.up();advance(3)
  check('Mouse drag rotates third-person camera',abs(snap()['camera']['yaw']-before)>.3)
  page.mouse.move(610,420);page.mouse.down();page.mouse.move(510,410,steps=5);page.mouse.up();advance(3)
  check('Camera yaw restored by inverse mouse drag',abs(snap()['camera']['yaw'])<.02,snap()['camera'])
  before=snap()['position'];page.keyboard.down('KeyW');advance(7);walk=snap();page.keyboard.up('KeyW');advance(8)
  check('WASD translates player and selects Walk',walk['animation']=='Walk' and walk['position'][2]<before[2]-.1,walk['position'])
  check('Released input decelerates to idle',snap()['animation']=='Idle',snap()['animation'])
  # Two NPCs must patrol before approaching them.
  npcs0=snap()['npcs'];advance(40);npcs1=snap()['npcs'];check('Both NPCs actually patrol',all(math.dist(a['position'],b['position'])>.05 for a,b in zip(npcs0,npcs1)),[npcs0,npcs1])
  guide=next(n for n in snap()['npcs'] if n['id']=='guide')['position'];go(guide[0],guide[2]+1.5,tolerance=.4)
  page.keyboard.press('KeyE');advance(3);check('Proximity + E opens NPC dialogue',snap()['dialogue'])
  page.screenshot(path=str(E/'npc-dialogue.png'))
  page.get_by_role('button',name='好，交給我吧').click();advance(4);check('Accepting dialogue starts quest',snap()['quest']=='collecting')
  for x,z in [(-5.5,-4.8),(-6,3.6),(8,8)]:
   # Avoid the raised tree planter and market: use central square between stamps.
   if x==8:
    go(-3.5,3.6);go(-3.5,8);go(8,8)
   else:go(x,z)
  check('All three pickups collected once',len(snap()['collected'])==3 and snap()['score']==75,snap()['collected'])
  page.screenshot(path=str(E/'three-stamps.png'))
  # Move along east side to avoid bench (x=7.5,z=6.7) and market (x=4,z=2.5).
  go(15,8);go(15,-5.3);go(7,-5.3,tolerance=.4)
  page.keyboard.press('KeyE');advance(3);check('Second NPC offers delivery',page.get_by_role('button',name='交付散策手帖').is_visible())
  page.get_by_role('button',name='交付散策手帖').click();advance(3)
  check('Complete quest loop awards exactly 150',snap()['quest']=='complete' and snap()['score']==150,snap()['score']);page.screenshot(path=str(E/'quest-complete.png'))
  page.get_by_role('button',name='繼續散策').click();advance(4)
  # Kinematic character physically stops against the bookshop wall at z=-9.
  go(3,-5.3);page.keyboard.down('KeyW');advance(45);page.keyboard.up('KeyW');advance(7)
  check('Player cannot cross solid bookshop wall',snap()['position'][2]>-8.8,snap()['position'])
  # Turn camera toward the wall; boom should retract, not show through the building.
  page.mouse.move(450,390);page.mouse.down();page.mouse.move(450+math.pi/.006,390,steps=12);page.mouse.up();advance(8)
  check('Camera boom retracts against building',snap()['camera']['distance']<snap()['camera']['desiredDistance']-1,snap()['camera'])
  check('No JavaScript runtime errors',not errors,errors)
  final=snap();times=final['frameMs'];report={'status':'PASS','checks':results,'navigation':observations,'final':{k:v for k,v in final.items() if k!='frameMs'},'performance':{'renderer':'Chromium ANGLE SwiftShader (software)','viewport':[960,600],'quality':'low','samples':len(times),'mean_frame_ms':statistics.mean(times) if times else None,'mean_fps':1000/statistics.mean(times) if times else None,'p95_frame_ms':sorted(times)[int(.95*(len(times)-1))] if times else None,'not_hardware_benchmark':True},'javascript_errors':errors}
 except Exception as e:
  page.screenshot(path=str(E/'browser-failure.png'));report={'status':'FAIL','error':str(e),'checks':results,'navigation':observations,'javascript_errors':errors,'snapshot':snap() if page.evaluate('!!window.__harbor') else None};raise
 finally:
  (E/'browser-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));video=page.video;context.close();video.save_as(str(E/'gameplay.webm'));browser.close()
