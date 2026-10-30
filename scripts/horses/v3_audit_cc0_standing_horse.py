#!/usr/bin/env python3
"""Audit a claimed CC0 standing horse from its public source, with no access bypass.

Fetch HTML metadata and derive ONLY explicit asset links. Never accept remote
scripts as download targets. If a publicly linked original .glb is available,
save bytes and independently inspect glTF 2.0 structural metadata.

This model is STATIC. Do NOT falsely label it rigged or animated, or copy its
geometry directly over the proven Quaternius 13-clip horse.
"""
from pathlib import Path
import urllib.request,urllib.parse
from html.parser import HTMLParser
import json,re,hashlib,struct

URL="https://www.innerscene.com/tools/library/3d-parts/standing-horse-01d8563f"
BASE="https://www.innerscene.com"
OUT=Path("outputs/horse_v3_candidate")
OUT.mkdir(parents=True,exist_ok=True)
UA="3dcodeverse-lab-CC0-asset-auditor/1.0"
def request(url,max_size=9_000_000, method="GET"):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/html,application/json,model/gltf-binary,*/*"},method=method)
    with urllib.request.urlopen(req,timeout=30) as r:
        final=r.geturl()
        if urllib.parse.urlsplit(final).scheme!="https":raise ValueError("Non-HTTPS redirect")
        blob=b"" if method=="HEAD" else r.read(max_size+1)
        if len(blob)>max_size:raise ValueError("Asset exceeds read limit")
        return final,dict(r.headers),blob
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ("a","link","meta","script"):
            for key in ("href","src","content"):
                val=a.get(key,"")
                if val and (".glb" in val.lower() or "download" in val.lower() or "asset" in val.lower()):
                    self.links.append(val)

report={"source":URL,"claimed_license":"CC0 per source listing","license_validation":"Requires source metadata and content",
        "static_unrigged":True,"download_status":"NOT_VERIFIED","candidates":[]}
try:
    final,headers,body=request(URL,max_size=3_000_000)
    report["page"]={"url":final,"mime":headers.get("Content-Type"),"size":len(body)}
    html=body.decode("utf-8","replace")
    parser=Links();parser.feed(html)
    found=parser.links+[x.replace("\\/","/") for x in re.findall(
        r'[^"\'<>\\s]+\\.glb(?:\\?[^"\'<>\\s]*)?',html,re.I)]
    candidates=[]
    for val in found:
        u=urllib.parse.urljoin(final,val)
        sp=urllib.parse.urlsplit(u)
        if sp.scheme!="https" or sp.hostname not in ("www.innerscene.com","innerscene.com"):
            continue
        if u not in candidates and ".glb" in sp.path.lower():candidates.append(u)
    report["asset_links_found"]=candidates[:25]
    report["page_mentions_filename"]="horse-original.glb" in html
    report["filename_contexts"]=[html[max(0,m.start()-550):min(len(html),m.end()+550)] for m in list(re.finditer("horse-original\\.glb",html,re.I))[:4]]
    report["keyword_contexts"]=[html[max(0,m.start()-130):min(len(html),m.end()+200)] for m in list(re.finditer(r'(?:downloadUrl|modelUrl|modelPath|assetUrl|\\.glb)',html,re.I))[:12]]
    report["script_paths"]=re.findall(r'<script[^>]*src=["\\']([^"\\']+)',html,re.I)[:16]
    # Only try explicitly present links, no speculative path traversal.
    for url in candidates[:6]:
        try:
            resolved,headers,blob=request(url,max_size=20_000_000)
            rec={"url":resolved,"length":len(blob),"mime":headers.get("Content-Type"),"is_glb":blob[:4]==b"glTF"}
            if rec["is_glb"]:
                magic,version,byte_len=struct.unpack_from("<4sII",blob,0)
                n,kind=struct.unpack_from("<I4s",blob,12)
                if magic!=b"glTF" or version!=2 or byte_len!=len(blob) or kind!=b"JSON":raise ValueError("Invalid glTF")
                d=json.loads(blob[20:20+n])
                rec.update({"meshes":len(d.get("meshes",[])),"skins":len(d.get("skins",[])),
                            "animations":len(d.get("animations",[])),"materials":len(d.get("materials",[])),
                            "nodes":len(d.get("nodes",[])),"sha256":hashlib.sha256(blob).hexdigest()})
                (OUT/"standing_horse_source.glb").write_bytes(blob)
                report["download_status"]="VERIFIED_PUBLIC_CC0_SOURCE_BYTES"
                report["model"]=rec
                break
            report["candidates"].append(rec)
        except Exception as e:report["candidates"].append({"url":url,"error":str(e)[:240]})
except Exception as e:report["page_error"]=type(e).__name__+": "+str(e)

(OUT/"source_audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("HIGH_DETAIL_HORSE_SOURCE_AUDIT",json.dumps(report,ensure_ascii=False)[:10000],flush=True)
