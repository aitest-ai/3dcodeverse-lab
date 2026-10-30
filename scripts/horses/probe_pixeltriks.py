#!/usr/bin/env python3
"""Diagnose public, explicitly downloadable CC0 horse assets at PixelTriks.

Only fetches public HTML/JS and HEAD/limited GET at likely asset paths. No
access control bypass or credentials. Stores findings for precise integration.
"""
import json, re, urllib.request, urllib.error, urllib.parse
from pathlib import Path

base="https://pixeltriks.com"
page=base+"/browse?asset=characters%2Fanimals%2Fquaternius_Horse.gltf&pack=quaternius-ultimate-animated-animals"
out=Path("outputs/pixeltriks_probe");out.mkdir(parents=True,exist_ok=True)
ua="3dcodeverse-CC0-public-asset-inspector/1.0"
def get(url,timeout=18,max_bytes=600000):
    request=urllib.request.Request(url,headers={"User-Agent":ua,"Accept":"*/*"})
    with urllib.request.urlopen(request,timeout=timeout) as response:
        data=response.read(max_bytes+1)
        return {"url":response.geturl(),"code":response.status,"type":response.headers.get("Content-Type"),"bytes":len(data),"truncated":len(data)>max_bytes},data[:max_bytes]
report={"page":page,"html":None,"scripts":[],"candidates":[],"hints":[]}
try:
    info,html=get(page)
    report["html"]=info
    txt=html.decode("utf-8","replace")
    (out/"page_snapshot.html").write_text(txt,encoding="utf-8")
    scripts=re.findall(r'<script[^>]+src=["\']([^"\']+)',txt,re.IGNORECASE)
    report["scripts"]=scripts[:30]
    for text in re.findall(r'[^\s\"\']{0,60}(?:quaternius_Horse|\.gltf|assets/characters)[^\s\"\']{0,80}',txt):
        report["hints"].append(text[:180])
    for src in scripts[:6]:
        u=urllib.parse.urljoin(page,src)
        try:
            sinfo,js=get(u,max_bytes=2400000)
            doc=js.decode("utf-8","replace")
            hints=[doc[max(0,m.start()-125):m.end()+145] for m in list(re.finditer(r'quaternius_Horse|assets/characters|assets_base|modelPath|assetUrl|\.gltf',doc))[:18]]
            report.setdefault("js_probe",[]).append({"info":sinfo,"hints":hints})
            if hints:(out/("js_"+str(len(report["js_probe"]))+".txt")).write_text("\n---\n".join(hints),encoding="utf-8")
        except Exception as e:
            report.setdefault("js_probe",[]).append({"url":u,"error":repr(e)})
except Exception as e:report["page_error"]=repr(e)

paths=[
    "/assets/characters/animals/quaternius_Horse.gltf",
    "/models/characters/animals/quaternius_Horse.gltf",
    "/characters/animals/quaternius_Horse.gltf",
    "/asset/characters/animals/quaternius_Horse.gltf",
    "/api/assets/characters/animals/quaternius_Horse.gltf",
    "/api/model?path=characters%2Fanimals%2Fquaternius_Horse.gltf",
    "/static/assets/characters/animals/quaternius_Horse.gltf",
]
for path in paths:
    u=base+path
    try:
        info,blob=get(u,max_bytes=1600000)
        row={"path":path,"info":info,"prefix":blob[:55].hex()}
        if info["code"]==200 and blob.lstrip().startswith(b"{"):
            try:
                doc=json.loads(blob)
                if isinstance(doc,dict):
                    row["keys"]=list(doc)[:14]
                    row["gltf_asset"]=doc.get("asset")
                    row["meshes"]=len(doc.get("meshes",[]))
                    row["animations"]=[x.get("name") for x in doc.get("animations",[])[:15]]
                    if doc.get("asset",{}).get("version")=="2.0":
                        (out/"horse_candidate.gltf").write_bytes(blob)
                        row["saved"]=True
            except Exception as e:row["json_error"]=str(e)
        report["candidates"].append(row)
    except Exception as e:
        report["candidates"].append({"path":path,"error":str(e)[:180]})
(out/"probe_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
print("PIXELTRIKS_PROBE",json.dumps(report,ensure_ascii=False)[:13000])
