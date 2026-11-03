from playwright.sync_api import sync_playwright
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-watchdog'])
 page=b.new_page(viewport={'width':1280,'height':800});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8130/');page.wait_for_function('window.__harborGodot?.ready',timeout=120000)
 def snap():return page.evaluate('window.__harborGodot')
 def advance(n=12):
  f=snap()['physics_frames'];page.wait_for_function('(f)=>window.__harborGodot.physics_frames>=f',arg=f+n,timeout=90000)
 s=snap();x,y=s['buttons']['start'];page.mouse.click(x,y);advance();page.screenshot(path=str(R/'evidence/godot-standard-gameplay.png'))
 page.keyboard.press('v');advance();page.screenshot(path=str(R/'evidence/godot-standard-portrait.png'))
 page.keyboard.press('v');advance();page.screenshot(path=str(R/'evidence/godot-standard-face.png'))
 page.keyboard.press('b');advance();page.screenshot(path=str(R/'evidence/godot-standard-smile.png'))
 (R/'evidence/standard-review.json').write_text(json.dumps({'status':'PASS' if not errors else 'FAIL','quality':snap()['low_quality'],'viewport':[1280,800],'smile':snap()['smile'],'javascript_errors':errors},indent=2));b.close()
