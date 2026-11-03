from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'],headless=True);page=b.new_page(viewport={'width':960,'height':600})
 page.goto('http://127.0.0.1:8130/');page.wait_for_function('window.__harborGodot?.ready',timeout=120000)
 s=page.evaluate('window.__harborGodot');r=page.locator('#canvas').bounding_box();x,y=s['buttons']['start'];page.mouse.click(x/1280*r['width']+r['x'],y/800*r['height']+r['y']);page.keyboard.press('KeyQ')
 for k in ['ShiftLeft','KeyA','KeyW']:page.keyboard.down(k)
 for i in range(12):
  page.wait_for_timeout(1000);s=page.evaluate('window.__harborGodot');print(json.dumps({k:s.get(k) for k in ['position','input','velocity','motion','nearest','dialog','physics_frames','process_frames','collisions']},ensure_ascii=False),flush=True)
 b.close()
