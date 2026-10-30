"""V30: provenance-first inspection of a candidate CC0 brown-bear GLB.
No model integration or re-publication without verifying magic bytes,
the source-page CC0 notice, mesh shape, render and creator attribution.
"""
import pathlib,re,json,hashlib,requests,bs4,urllib.parse,sys
from urllib.parse import urljoin
ROOT=pathlib.Path("candidate");ROOT.mkdir(exist_ok=True,parents=True)
PAGE="https://www.innerscene.com/tools/library/3d-parts/brown-bear-7da82cb5"
out={"source_page":PAGE,"claimed_license":"CC0, original Innerscene, as published on model page",
     "can_redistribute":False,"verified_glb":False,"candidates":[]}
s=requests.Session();s.headers["User-Agent"]="Mozilla/5.0 (compatible; 3DCodeVerse research/0.1)"
try:
    r=s.get(PAGE,timeout=25)
    out["page_status"]=r.status_code
    out["page_length"]=len(r.content)
    r.raise_for_status()
    soup=bs4.BeautifulSoup(r.text,"html.parser")
    txt=soup.get_text(" ",strip=True)
    out["contains_cc0"]=("CC0" in txt and "Public domain" in txt)
    out["contains_creator"]="Innerscene - original model" in txt
    out["description_excerpt"]=txt[txt.find("Brown bear"):txt.find("Brown bear")+300]
    candidates=[]
    for tag in soup.select("a[href]"):
        href=tag.get("href")
        label=tag.get_text(" ",strip=True)
        if "glb" in href.lower() or ("download" in href.lower() and ("glb" in label.lower() or "glb" in href.lower())):
            candidates.append({"url":urljoin(PAGE,href),"label":label[:120],"method":"anchor"})
    for key in ["brown-bear.glb","7da82cb5","downloadGlb","downloadUrl","/api/library","download_url"]:
        for match in list(re.finditer(re.escape(key),r.text,re.I))[:4]:
            candidates.append({"keyword":key,"context":r.text[max(0,match.start()-160):match.end()+190],
                               "method":"page-context"})
    out["candidates"]=candidates[:40]
    # Only direct paths in publicly linked source page are eligible for download
    # avoid fetching arbitrary iframe/media URLs or authenticated resources.
    for c in candidates:
        url=c.get("url")
        if not url or not url.lower().split("?")[0].endswith(".glb"):continue
        try:
            m=s.get(url,timeout=35)
            if m.status_code==200 and m.content[:4]==b"glTF" and len(m.content)>120000:
                dest=ROOT/"brown_bear_source_CC0_candidate.glb"
                dest.write_bytes(m.content)
                out.update(verified_glb=True,direct_url=url,bytes=len(m.content),
                           sha256=hashlib.sha256(m.content).hexdigest())
                break
        except requests.RequestException as e:
            out.setdefault("download_errors",[]).append(str(e)[:250])
except Exception as e:
    out["error"]=str(e)[:600]
(ROOT/"source_probe.json").write_text(json.dumps(out,indent=2,ensure_ascii=False))
print("V30_SOURCE_PROBE",json.dumps(out,ensure_ascii=False)[:8500],flush=True)
# This first stage is DISCOVERY only; no false claim of being downloaded.
