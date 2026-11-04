#!/usr/bin/env python3
"""V31 Chromium smoke: proves actual browser telemetry works on a clearly SYNTHETIC game fixture."""
import json
import pathlib
import sys
import tempfile
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from test_onomichi_v31_runtime_gate import gate,make_fixture

def main():
 with tempfile.TemporaryDirectory() as temp:
  folder=pathlib.Path(temp)
  archive,_=make_fixture(folder)
  clone=folder/"synthetic_game_clone"
  audit=gate.prepare(archive,clone,fixture_mode=True)
  assert audit["status"]==gate.TEST_LABEL
  server=ThreadingHTTPServer(("127.0.0.1",0),
    partial(SimpleHTTPRequestHandler,directory=str(clone)))
  Thread(target=server.serve_forever,daemon=True).start()
  host="http://127.0.0.1:"+str(server.server_port)
  try:
   with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
      args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader',
            '--enable-webgl','--disable-dev-shm-usage'])
    ctx=browser.new_context(accept_downloads=True,
      viewport={"width":1320,"height":850},device_scale_factor=1)
    page=ctx.new_page()
    errors=[]
    page.on('pageerror',lambda exc:errors.append(str(exc)))
    page.goto(host+'/review/onomichi-v31/',wait_until='networkidle')
    assert '合成／未核准' in page.locator('#source').inner_text()
    page.goto(host+'/',wait_until='networkidle')
    page.wait_for_selector('#onomichi-v31-observer #start',timeout=30000)
    assert page.evaluate('window.__fixtureGameLoaded') is True
    assert '合成／未知來源' in page.locator('#onomichi-v31-observer #source').inner_text()
    # A real Chromium WebGL canvas for browser-level smoke, NOT V28 original game.
    context_exists=page.evaluate("""
      (()=>{const c=document.getElementById('fake-world');
      return !!c.getContext('webgl2')})()
    """)
    assert context_exists,"Swiftshader WebGL2 synthetic test unavailable"
    page.locator('#onomichi-v31-observer #start').click()
    page.locator('#fake-world').click()
    page.keyboard.press('w')
    page.keyboard.press('a')
    page.locator('#bike').click()
    page.locator('#onomichi-v31-observer input[data-manual="walk"]').check()
    page.locator('#onomichi-v31-observer #stop').click()
    with page.expect_download() as d:
     page.locator('#onomichi-v31-observer #save').click()
    download=d.value
    data=json.loads(pathlib.Path(download.path()).read_text())
    assert data['status']=='SYNTHETIC_OR_UNVERIFIED_SOURCE_NOT_GAMEPLAY_APPROVED'
    assert data['verified_by_automated_gameplay'] is False
    assert data['original_site_modified'] is False
    assert data['capture']['recorded_event_count']>=4
    assert data['human_checklist_self_reported_only']['walk'] is True
    assert any(e['type']=='key_down' and e['code']=='KeyW' for e in data['capture']['events'])
    assert any(e['type']=='game_button' and e['id']=='bike' for e in data['capture']['events'])
    assert not errors,errors
    page.screenshot(path=str(folder/'V31_Synthetic_Desktop_QA.png'),full_page=True)
    page.set_viewport_size({"width":390,"height":844})
    page.wait_for_timeout(350)
    assert page.locator('#onomichi-v31-observer #toggle').is_visible()
    assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+2')
    page.screenshot(path=str(folder/'V31_Synthetic_Mobile_QA.png'),full_page=True)
    print(json.dumps({
     "status":"PASS_SYNTHETIC_FIXTURE_ONLY",
     "browser_webgl2":True,
     "observer_key_events":True,
     "observer_game_button_event":True,
     "local_json_export":True,
     "source_closure":True,
     "mobile_layout":True,
     "actual_original_v28_playtest":False
    },ensure_ascii=False))
    browser.close()
  finally:server.shutdown()

if __name__=="__main__":main()
