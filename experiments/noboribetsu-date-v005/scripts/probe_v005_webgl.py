"""Determine whether this runner offers actual WebGL2; not a full V005 acceptance test."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
flags=[
    ['--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-sandbox'],
    ['--enable-webgl','--use-gl=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-sandbox'],
]
logs=[]
with sync_playwright() as p:
 for i,f in enumerate(flags):
  browser=None
  try:
   browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=f,timeout=12000)
   page=browser.new_page(viewport={'width':1280,'height':720});page.set_content('<canvas id="c"></canvas>');
   status=page.evaluate('''()=>{let c=document.getElementById('c');let g=c.getContext('webgl2');return {ok:!!g,version:g?g.getParameter(g.VERSION):null}}''')
   logs.append({'flags':f,'status':status})
  except Exception as e:logs.append({'flags':f,'error':str(e)[:240]})
  finally:
   if browser:browser.close()
print(json.dumps(logs,ensure_ascii=False,indent=2))
with open(Path(__file__).resolve().parent.parent/'V005_webgl_probe.json','w') as f:json.dump(logs,f,ensure_ascii=False,indent=2)