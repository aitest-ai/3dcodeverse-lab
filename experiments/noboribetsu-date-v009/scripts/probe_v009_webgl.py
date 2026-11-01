#!/usr/bin/env python3
"""WebGL 2 context probe (not a scene playthrough). Different from VTK visuals."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).parent
options=[[],['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'],
 ['--use-gl=swiftshader','--enable-unsafe-swiftshader'],
 ['--use-gl=angle','--use-angle=gl','--enable-unsafe-swiftshader']]
result=[]
with sync_playwright() as p:
 for opts in options:
  try:
   browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,
     args=['--no-sandbox','--disable-gpu-sandbox','--disable-dev-shm-usage',*opts],timeout=8000)
   page=browser.new_page();page.set_content('<canvas id="c"></canvas>')
   state=page.evaluate("""() => ({webgl2:!!document.getElementById('c').getContext('webgl2'),webgl:!!document.getElementById('c').getContext('webgl')})""")
   browser.close()
   result.append({'flags':opts,'result':state})
  except Exception as ex:result.append({'flags':opts,'error':str(ex)[:140]})
verified=any(v.get('result',{}).get('webgl2') for v in result)
report={'schema':'date-v009-webgl2-context/1','status':'CONTEXT_AVAILABLE' if verified else 'UNAVAILABLE_IN_CURRENT_CONTAINER',
        'chromium_probes':result,'full_threejs_scene_verified':False,'android_verified':False,
        'note':'Source and DOM checks can pass without the real WebGL 2 GPU scene'}
(root/'evidence/webgl_context_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':report['status'],'attempts':len(result),'webgl2_available':verified}))