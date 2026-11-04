from playwright.sync_api import sync_playwright
from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=b.new_page(viewport={'width':1100,'height':760});errors=[];console=[]
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:console.append(m.text) if m.type=='error' else None)
 page.goto('http://127.0.0.1:8130/',wait_until='domcontentloaded');page.wait_for_function('window.__harborGodot?.ready',timeout=120000)
 page.wait_for_timeout(2000);page.screenshot(path=str(r/'evidence/godot-first.png'))
 print(json.dumps({'snapshot':page.evaluate('window.__harborGodot'),'errors':errors,'console_errors':console},ensure_ascii=False));b.close()
