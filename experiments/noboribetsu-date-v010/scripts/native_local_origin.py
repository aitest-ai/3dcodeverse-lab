#!/usr/bin/env python3
"""True localhost acceptance. NO SHA adapter, NO intercepted requests.

Will be blocked by some managed browsers' top-level navigation policies.
On a personal computer it tests genuine localhost origin and WebCrypto SHA.
Chromium/Playwright and a real graphics context are required.
"""
import argparse,json,threading,http.server,functools,shutil,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser();ap.add_argument('runtime_root',type=Path);ap.add_argument('--out',type=Path,default=Path('native_origin_results'))
a=ap.parse_args();root=a.runtime_root.resolve();d=root/'dist';a.out.mkdir(parents=True,exist_ok=True)
assert (d/'index.html').is_file()
class QuietHandler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(d)))
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/index.html'
result={'schema':'v010-native-localhost-webgl-1','source':url,'secure_origin':False,'true_webcrypto':False,'test_only_digest_adapter':False,'loaded':False,'renderer':None,'walked_m':None,'stage_A':None,'stage_B':None,'errors':[],'pass':False,'android_real_device':False}
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=shutil.which('chromium') or None,headless=True,args=['--no-sandbox','--enable-webgl','--ignore-gpu-blocklist','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  page=b.new_page(viewport={'width':900,'height':600},device_scale_factor=1)
  page.on('pageerror',lambda e:result['errors'].append(str(e)))
  page.goto(url,timeout=15000,wait_until='domcontentloaded')
  origin=page.evaluate('''() => ({secure:isSecureContext,subtle:typeof crypto.subtle?.digest==='function',webgl2:!!document.createElement('canvas').getContext('webgl2')})''')
  result['secure_origin']=origin['secure'];result['true_webcrypto']=origin['subtle'];result['webgl2']=origin['webgl2']
  if not all(origin.values()):raise RuntimeError('Real localhost secure WebGL2 requirements failed: '+str(origin))
  page.wait_for_function("document.querySelector('#scene').dataset.loaded === 'true' || document.querySelector('#scene').dataset.loaded === 'failed'",timeout=120000,polling=350)
  if page.locator('#scene').get_attribute('data-loaded')!='true':raise RuntimeError(page.locator('#loadError').inner_text())
  result['loaded']=True
  page.evaluate("document.getElementById('enterButton').click()")
  before=page.locator('#scene').get_attribute('data-position')
  page.keyboard.down('w');page.wait_for_timeout(850);page.keyboard.up('w')
  after=page.locator('#scene').get_attribute('data-position')
  result['walked_m']=sum((float(x)-float(y))**2 for x,y in zip(before.split(','),after.split(',')))**.5
  page.screenshot(path=str(a.out/'v010_native_origin_scene.png'),timeout=20000)
  page.evaluate("document.getElementById('aButton').click()")
  page.wait_for_function("document.getElementById('scene').dataset.stage==='A' || document.getElementById('scene').dataset.loaded==='failed'",timeout=60000,polling=350)
  result['stage_A']=page.locator('#scene').get_attribute('data-stage')
  page.evaluate("document.getElementById('bButton').click()")
  result['stage_B']=page.locator('#scene').get_attribute('data-stage')
  result['renderer']=page.evaluate('''() => window.__DATE_METRICS__?.webgl || null''')
  result['pass']=result['walked_m']>.05 and result['stage_A']=='A' and result['stage_B']=='B'
  b.close()
except Exception as e:result['errors'].append(str(e)[:2000])
finally:server.shutdown()
(a.out/'v010_native_origin_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
sys.exit(0 if result['pass'] else 2)