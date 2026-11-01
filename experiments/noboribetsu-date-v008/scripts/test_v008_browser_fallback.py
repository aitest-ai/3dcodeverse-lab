"""DOM/subresource fallback test without top-level navigation; WebGL remains untestable."""
import json,sys,mimetypes
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent
dist=root/'base/dist'
report={'schema':'date-v008-no-webgl-fallback-browser/1','status':'FAIL','real_3d_play_verified':False,'android_verified':False,'navigation_tested':False}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader'])
 page=browser.new_page(viewport={'width':1280,'height':760})
 def supply(route):
  path=route.request.url.split('https://date.local/')[-1].split('?')[0]
  target=(dist/path).resolve()
  if not target.is_relative_to(dist.resolve()) or not target.is_file():
   route.fulfill(status=404,body='not found',headers={'access-control-allow-origin':'*'});return
  mime=mimetypes.guess_type(str(target))[0] or 'application/octet-stream'
  route.fulfill(status=200,content_type=mime,body=target.read_bytes(),headers={'access-control-allow-origin':'*'})
 page.route('https://date.local/**',supply)
 errors=[];page.on('console',lambda m: errors.append(m.text) if m.type=='error' else None)
 html=(dist/'index.html').read_text().replace('<head>','<head><base href="https://date.local/">',1)
 try:
  page.set_content(html,wait_until='domcontentloaded',timeout=15000)
  page.locator('#loadError:not([hidden])').wait_for(timeout=18000)
  details=page.evaluate('''() => ({webgl2_available:!!document.createElement('canvas').getContext('webgl2'),load_error:document.getElementById('loadError').textContent,review_link:document.querySelector('.fallback a')?.getAttribute('href'),manifest_ready:!!window.__DATE_METRICS__?.manifest_ready_ms,model_events:window.__DATE_METRICS__?.models||{},ready:document.querySelector('#scene').dataset.loaded,scene_version:document.title})''')
  report.update(details)
  review_html=(dist/'review_v008.html').read_text().replace('<head>','<head><base href="https://date.local/">',1)
  page.set_content(review_html,wait_until='load',timeout=10000)
  report['fallback_page_title']=page.title()
  report['fallback_images_loaded']=page.evaluate('''() => [...document.querySelectorAll('figure img')].filter(i=>i.complete && i.naturalWidth>0).length''')
  report['status']='PASS_DOM_FALLBACK_ONLY' if (not details['webgl2_available'] and '無法建立 WebGL' in details['load_error'] and report['fallback_images_loaded']==3 and not details['model_events'] and details['review_link']=='review_v008.html') else 'FAIL'
 except Exception as e:report['exception']=repr(e)
 report['console_errors']=errors[:6]
 browser.close()
(root/'evidence/V008_browser_fallback_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(0 if report['status']=='PASS_DOM_FALLBACK_ONLY' else 1)