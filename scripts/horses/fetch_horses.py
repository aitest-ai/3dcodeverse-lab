#!/usr/bin/env python3
"""Fetch Quaternius's original CC0 horse pair from PixelTriks public download.

Provenance: Quaternius Ultimate Animated Animals, CC0:
https://quaternius.com/packs/ultimateanimatedanimals.html
Public hosting/catalog: https://pixeltriks.com/browse?pack=quaternius-ultimate-animated-animals
Only downloads the two publicly exposed horse glTF assets, no credentials.
Do not equate other third-party, 3-clip horse files with this 13-clip pack.
"""
import hashlib, json, re, urllib.request
from pathlib import Path
from urllib.parse import urlparse,unquote

BASE="https://pixeltriks.com/characters/animals/"
SOURCE="https://quaternius.com/packs/ultimateanimatedanimals.html"
HORSES=["Horse","Horse_White"]
root=Path("inputs/horses")
root.mkdir(parents=True,exist_ok=True)
manifest=[]
for horse in HORSES:
    url=BASE+"quaternius_"+horse+".gltf"
    req=urllib.request.Request(url,headers={"User-Agent":"3dcodeverse-lab CC0 educational horse importer/1.0","Accept":"model/gltf+json,application/json"})
    print("FETCH_ORIGINAL_CC0",url,flush=True)
    with urllib.request.urlopen(req,timeout=65) as stream:
        if urlparse(stream.geturl()).hostname not in ("pixeltriks.com","www.pixeltriks.com"):
            raise RuntimeError("Unexpected host redirect. Refusing source without review.")
        blob=stream.read(35_000_000)
    if len(blob)<50000 or len(blob)>=35_000_000:raise RuntimeError("Invalid/truncated original horse data size")
    doc=json.loads(blob)
    if doc.get("asset",{}).get("version")!="2.0":raise RuntimeError("Not glTF 2.0 source")
    for u in [part.get("uri","") for part in doc.get("buffers",[])+doc.get("images",[])]:
        if not u or u.startswith("data:"):continue
        # Download sidecar only if hosted at the exact same origin and no path traversal.
        decoded=unquote(u)
        if not re.fullmatch(r"[A-Za-z0-9_./%-]+",decoded) or ".." in decoded or decoded.startswith("/"):
            raise RuntimeError("Unexpected external sidecar URI: "+u[:120])
        sideurl=BASE+decoded
        with urllib.request.urlopen(urllib.request.Request(sideurl,headers={"User-Agent":"3dcodeverse-lab CC0 importer/1.0"}),timeout=45) as side:
            data=side.read(50_000_000)
        if not 10<len(data)<50_000_000:raise RuntimeError("Sidecar size invalid")
        dest=(root/decoded).resolve()
        if root.resolve() not in dest.parents:raise RuntimeError("Path traversal blocked")
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(data)
    clips=[a.get("name","") for a in doc.get("animations",[])]
    p=root/(horse+".gltf")
    p.write_bytes(blob)
    item={
        "name":horse,"file":str(p),"sha256":hashlib.sha256(blob).hexdigest(),
        "bytes":len(blob),"creator":"Quaternius","license":"CC0-1.0",
        "official_original":SOURCE,
        "public_host":url,
        "original_quaternius_asset":True,
        "skins":len(doc.get("skins",[])),
        "meshes":len(doc.get("meshes",[])),
        "animations":clips,"animation_count":len(clips),
        "notice":"Real Blender preview and game engine animation still require testing"
    }
    print("HORSE_SOURCE_OK",json.dumps(item,ensure_ascii=False),flush=True)
    if len(clips)<10:raise RuntimeError("Original pack expected 12+ horse animations; got "+str(clips))
    if item["skins"]<1:raise RuntimeError("Horse is missing rig skin")
    manifest.append(item)
out=Path("outputs/horse")
out.mkdir(parents=True,exist_ok=True)
(out/"source_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
