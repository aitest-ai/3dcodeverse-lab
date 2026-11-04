#!/usr/bin/env python3
"""V30 real Chromium/WebGL2 canvas and safe failure smoke; never private GLB verification."""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'apps/onomichi-v30-3d-audit/dist'
assert (DIST/'app.js').is_file()
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(DIST)))
Thread(target=server.serve_forever,daemon=True).start()
url='http://127.0.0.1:'+str(server.server_port)+'/'
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--enable-webgl','--disable-dev-shm-usage'])
  page=browser.new_page(viewport={'width':1365,'height':950},device_scale_factor=1)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(url,wait_until='networkidle',timeout=60000)
  page.wait_for_timeout(1500)
  state=page.locator('#webglState').inner_text()
  assert 'WebGL2 已啟動' in state,'3D renderer failed: '+state+' / '+str(errors)
  assert page.evaluate("document.getElementById('canvas').width")>0
  assert page.evaluate("document.getElementById('canvas').height")>0
  for id in ['front','side','rear','threeQuarter','fit']:page.locator('#'+id).click()
  assert page.locator('#record').is_disabled()
  assert page.locator('#export').is_disabled()
  assert '未載入原版 GLB' in page.locator('#overlay').inner_text()
  assert not errors,'Uncaught errors: '+str(errors)
  print('PASS real Chromium WebGL2 original-model-empty stage + camera, no fake rider')
  page.set_viewport_size({'width':390,'height':844})
  page.wait_for_timeout(450)
  assert page.evaluate("document.documentElement.scrollWidth<=window.innerWidth+2"),'Mobile horizontal overflow'
  assert page.locator('#canvas').is_visible()
  print('PASS Chromium mobile viewport layout (not Android hardware)')
  browser.close()
finally:
 server.shutdown()
