#!/usr/bin/env python3
"""Visual source audit ONLY. Does not download, decrypt or redistribute model files."""
import argparse,hashlib,json,re
from pathlib import Path
from playwright.sync_api import sync_playwright
CANDIDATES={
 "meshy_bear":{"url":"https://www.meshy.ai/ja/3d-models/%E6%9C%A8%E5%BD%AB%E3%82%8A%E3%81%AE%E7%86%8A%2C%20%E6%97%A5%E6%9C%AC%E3%81%AE%E5%B7%A5%E8%8A%B8%E5%93%81%2C%20%E9%AE%AD%E3%82%92%E5%92%A5%E3%81%88%E3%81%A6%E3%81%84%E3%82%8B-0193a5a5-027c-7d36-89f8-a5c35105a5a6","license":"CC0 stated on community listing","access":"Community model download can require paid account; do not circumvent."},
 "booth_bear":{"url":"https://booth.pm/ja/items/8884329","license":"Creator terms permit use but prohibit raw-asset redistribution","access":"Paid ¥200; do not download without purchase."},
 "sketchfab_scan":{"url":"https://sketchfab.com/3d-models/wood-carved-bear-d72978ac57d2494788dcdc7037496b14","license":"CC BY-NC","access":"Non-commercial reference only; honor attribution."}
}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--out",default="candidate-audit");a=ap.parse_args()
 root=Path(a.out);root.mkdir(parents=True,exist_ok=True);records=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
  for key,spec in CANDIDATES.items():
   d=root/key;d.mkdir(exist_ok=True)
   obj={"name":key,"page":spec["url"],"source_license":spec["license"],"access_policy":spec["access"],"source_model_acquired":False,"shape_verdict":"UNREVIEWED","release_approved":False}
   page=browser.new_page(viewport={"width":1200,"height":900})
   try:
    res=page.goto(spec["url"],wait_until="domcontentloaded",timeout=55000)
    page.wait_for_timeout(2500)
    obj["http_status"]=res.status if res else None
    obj["title"]=page.title()[:200]
    obj["visible_text_excerpt"]=re.sub(r"\s+"," ",page.locator("body").inner_text(timeout=9000))[:1600]
    page.screenshot(path=str(d/"public_page.png"),full_page=False)
    obj["screenshot_sha256"]=hashlib.sha256((d/"public_page.png").read_bytes()).hexdigest()
    obj["public_page_captured"]=True
   except Exception as exc:
    obj["error"]=str(exc)[:500];obj["public_page_captured"]=False
   page.close()
   (d/"review.json").write_text(json.dumps(obj,ensure_ascii=False,indent=2))
   records.append(obj)
  browser.close()
 (root/"manifest.json").write_text(json.dumps({"candidates":records,"approved_for_game":False,"note":"No GLB acquired; screenshot is not 3D geometry quality proof."},ensure_ascii=False,indent=2))
 print("AUDIT_COMPLETED",len(records),"APPROVED_FOR_GAME",False)
if __name__=="__main__":main()
