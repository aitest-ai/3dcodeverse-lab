from playwright.sync_api import sync_playwright
from pathlib import Path
import json
p=Path('/mnt/data/Noboribetsu_Date_V008_R1_Review.html')
report={'schema':'noboribetsu-v008-standalone-review/1','status':'FAIL'}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width,height in ((1280,800),(430,932)):
  page=b.new_page(viewport={'width':width,'height':height})
  page.set_content(p.read_text(encoding='utf-8'),wait_until='load',timeout=18000)
  rows=page.evaluate('''() => ({ figures:document.querySelectorAll('.compare').length,images:[...document.querySelectorAll('.compare img')].filter(x=>x.complete && x.naturalWidth > 0).length,sliders:document.querySelectorAll('input[type=range]').length })''')
  page.locator('#s0').fill('75')
  rows['slider_css']=page.locator('#c0').evaluate("e=>e.style.getPropertyValue('--split')")
  assert rows=={'figures':3,'images':6,'sliders':3,'slider_css':'75%'}
  report[f'{width}x{height}']=rows
  page.close()
 b.close()
report['status']='PASS_STATIC_INTERACTIVE_REVIEW_NO_WEBGL'
Path('/mnt/data/noboribetsu_v008_work/evidence/V008_review_page.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))