#!/usr/bin/env python3
"""Acquire a CC0 bear BASE from an official publisher, fail closed on invalid GLB."""
import argparse,hashlib,json,re,struct,sys
from pathlib import Path
from urllib.parse import urljoin,urlsplit
import requests

PAGES={
 "innerscene":"https://www.innerscene.com/tools/library/3d-parts/brown-bear-7da82cb5",
 "pixor":"https://pixor.art/library/creatures/bear/"
}
def valid(data):
 return len(data)>100 and data[:4]==b"glTF" and struct.unpack_from("<II",data,4)==(2,len(data))
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--source",choices=PAGES,default="innerscene")
 p.add_argument("--out",required=True)
 p.add_argument("--report",required=True)
 args=p.parse_args()
 out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
 report=Path(args.report);report.parent.mkdir(parents=True,exist_ok=True)
 page=PAGES[args.source]
 log=[]
 s=requests.Session();s.headers["User-Agent"]="Mozilla/5.0 (educational asset quality research)"
 try:
  r=s.get(page,timeout=45);r.raise_for_status()
 except Exception as e:
  report.write_text(json.dumps({"source":page,"status":"blocked_page_request","error":str(e)[:400]},indent=2))
  print("SOURCE_PROBE blocked_page_request",str(e)[:160])
  return 2
 html=r.text
 links=re.findall(r'(?:href|src|data-url|fileUrl)\s*[=:]\s*["\']([^"\']+)["\']',html,re.I)
 links+=re.findall(r'https?[^"\'<>\s]+?\.glb(?:\?[^"\'<>\s]*)?',html,re.I)
 links=[urljoin(r.url,x.replace("\\/","/").replace("&amp;","&")) for x in links if ".glb" in x.lower() or "download" in x.lower()]
 links=list(dict.fromkeys(links))
 log.append({"page":page,"html_bytes":len(r.content),"candidate_links":links[:30]})
 downloaded=False
 for link in links[:20]:
  parsed=urlsplit(link)
  if parsed.scheme!="https":continue
  if parsed.hostname not in ("www.innerscene.com","innerscene.com","pixor.art","www.pixor.art","cdn.innerscene.com"):continue
  try:
   f=s.get(link,timeout=60);f.raise_for_status()
   data=f.content
   if len(data)>45000000:continue
   log.append({"candidate":link[:160],"size":len(data),"glb":valid(data)})
   if valid(data):
    out.write_bytes(data);downloaded=True;break
  except Exception as e:log.append({"candidate":link[:160],"error":str(e)[:160]})
 if not downloaded:
  try:
   from playwright.sync_api import sync_playwright
   with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,args=["--no-sandbox","--disable-gpu"])
    tab=browser.new_page(accept_downloads=True)
    tab.goto(page,wait_until="domcontentloaded",timeout=60000)
    tab.wait_for_timeout(2500)
    button=tab.get_by_text("Download GLB",exact=False).first
    if button.count():
     with tab.expect_download(timeout=55000) as info:button.click(timeout=30000)
     dl=info.value
     dl.save_as(str(out))
     downloaded=valid(out.read_bytes())
     log.append({"browser_download":dl.suggested_filename,"glb":downloaded})
    else:log.append({"browser_download":"button-not-found"})
    browser.close()
  except Exception as e:log.append({"browser_error":str(e)[:300]})
 if not downloaded:out.unlink(missing_ok=True)
 status={"source":page,"license_notice":"Source webpage states CC0; visually verify provenance before derivative publication","status":"candidate_unreviewed" if downloaded else "blocked_no_valid_glb","attempts":log}
 if downloaded:
  status["sha256"]=hashlib.sha256(out.read_bytes()).hexdigest()
  status["size"]=out.stat().st_size
 report.write_text(json.dumps(status,indent=2,ensure_ascii=False))
 print("SOURCE_PROBE",status["status"],"candidates",len(links))
 return 0 if downloaded else 2
if __name__=="__main__":sys.exit(main())
