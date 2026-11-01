#!/usr/bin/env python3
"""Chromium DOM and image checks; NOT WebGL2, and no real URL navigation claims."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
root=Path(__file__).parent
html=(root/'outputs/Noboribetsu_Date_V009_R1_Review.html').read_text()
checks=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-gpu-sandbox','--disable-dev-shm-usage'])
 for w,h in [(1280,800),(430,932)]:
  page=b.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
  page.set_content(html,wait_until='load',timeout=30000)
  before=page.evaluate('''() => [...document.images].map(x=>({ok:x.complete&&x.naturalWidth>0,width:x.naturalWidth}))''')
  assert len(before)==8 and all(x['ok'] for x in before),(w,h,before)
  assert page.locator('input[type=range]').count()==4
  page.locator('input[type=range]').first.evaluate('(e) => {e.value="78";e.dispatchEvent(new Event("input",{bubbles:true}));}')
  value=page.locator('section.compare .after').first.evaluate('(e)=>e.style.clipPath')
  assert '22%' in value and value.startswith('inset('),value
  checks.append({'viewport':f'{w}x{h}','images_loaded':8,'sliders_working':4,'clip_after_value_78':value,'kind':'Chromium DOM set_content, not GPU test'})
  page.close()
 b.close()
out={'schema':'date-v009-review-dom/1','status':'PASS_DOM_FALLBACK','checks':checks,'webgl2_tested':False,'actual_private_URL_tested':False}
(root/'evidence/review_dom_qa.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False,indent=2))