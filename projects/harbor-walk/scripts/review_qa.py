from playwright.sync_api import sync_playwright
from pathlib import Path
import json,math,os
R=Path(__file__).resolve().parents[1];E=R/'evidence';checks=[];errors=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=b.new_page(viewport={'width':1100,'height':760});page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(os.environ.get('HARBOR_URL','http://127.0.0.1:5173/')+'viewer.html',wait_until='domcontentloaded');page.wait_for_function('!!window.__atelier',timeout=90000)
 for view in ['front','side','back','face']:
  page.locator('[data-view='+view+']').click();page.wait_for_timeout(350);page.screenshot(path=str(E/('web-character-'+view+'.png')))
 for clip in ['Idle','Walk','Run','Turn','Talk','Interact','Celebrate']:
  page.locator('#clip').select_option(clip);page.wait_for_timeout(300);a=page.evaluate('window.__atelier.snapshot()');page.wait_for_timeout(600);z=page.evaluate('window.__atelier.snapshot()')
  ok=a['bones']!=z['bones'];checks.append({'name':'real animated bones: '+clip,'pass':ok});assert ok,clip
  if clip in ['Walk','Run','Turn']:page.locator('[data-view=front]').click();page.screenshot(path=str(E/('web-animation-'+clip.lower()+'.png')))
 page.locator('#smile').focus();page.keyboard.press('End');checks.append({'name':'facial slider accepts value','pass':page.evaluate('window.__atelier.snapshot().smile')=='1'})
 page.close()
 # Exercise actual load error then retry via DOM, without altering production code.
 page=b.new_page(viewport={'width':960,'height':600});page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('**/models/harbor-courier.glb',lambda route:route.abort())
 page.goto(os.environ.get('HARBOR_URL','http://127.0.0.1:5173/'));page.locator('#retry').wait_for(state='visible',timeout=60000);checks.append({'name':'asset failure presents retry UI','pass':True});page.screenshot(path=str(E/'load-retry.png'))
 page.unroute('**/models/harbor-courier.glb');page.locator('#retry').click();page.wait_for_function('window.__harbor?.snapshot().ready',timeout=90000);checks.append({'name':'retry reload recovers real game','pass':True})
 page.screenshot(path=str(E/'title-screen.png'))
 page.locator('#start').click();page.wait_for_function('window.__harbor.snapshot().frames>3');page.screenshot(path=str(E/'first-gameplay.png'))
 page.close()
 page=b.new_page(viewport={'width':430,'height':932},device_scale_factor=1,is_mobile=True,has_touch=True);page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(os.environ.get('HARBOR_URL','http://127.0.0.1:5173/'));page.wait_for_function('window.__harbor?.snapshot().ready',timeout=90000);page.locator('#start').click();page.locator('#help').click();page.screenshot(path=str(E/'mobile-layout.png'))
 ok=page.evaluate('document.documentElement.scrollWidth<=innerWidth');checks.append({'name':'430px responsive layout has no horizontal overflow','pass':ok});assert ok
 page.close();b.close()
(E/'review-qa.json').write_text(json.dumps({'status':'PASS' if all(c['pass'] for c in checks) and not errors else 'FAIL','checks':checks,'javascript_errors':errors,'limitations':['Mobile layout is tested using Chromium emulation, not Android hardware or touch locomotion.','Facial slider UI plus binary morph structure is verified; subtle facial quality remains a manual art review.']},ensure_ascii=False,indent=2))
