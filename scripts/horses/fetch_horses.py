#!/usr/bin/env python3
"""Fetch only Quaternius's original Horse.gltf and Horse_White.gltf.

IDs were obtained by a metadata-only traversal of the official public folder:
https://drive.google.com/drive/folders/1uJ3N5HfB7jKTseJUNQr3N4YaN0UuEtHk
No login bypass, archive scraping or third-party mirrors. Never execute source code.
"""
import hashlib
import json
from pathlib import Path
import gdown

SOURCE = "https://quaternius.com/packs/ultimateanimatedanimals.html"
FOLDER = "https://drive.google.com/drive/folders/1uJ3N5HfB7jKTseJUNQr3N4YaN0UuEtHk?usp=sharing"
HORSES = {
    "Horse": "1hbtY8kxnXiPdwYGVY7rWRgU0jl_-Q-LG",
    "Horse_White": "1sb2XaaPjEV9Z3a1bG8ReISiGlRXrSA7W",
}
root=Path("inputs/horses")
root.mkdir(parents=True, exist_ok=True)
manifest=[]
for name,drive_id in HORSES.items():
    p=root/(name+".gltf")
    print("DOWNLOADING_AUTHOR_CC0_GLTF",name,drive_id,flush=True)
    result=gdown.download(id=drive_id,output=str(p),quiet=False,use_cookies=False)
    if not result or not p.is_file() or p.stat().st_size<1000:
        raise RuntimeError("Official horse asset download failed: "+name)
    sha=hashlib.sha256(p.read_bytes()).hexdigest()
    doc=json.loads(p.read_text(encoding="utf-8"))
    if doc.get("asset",{}).get("version")!="2.0":
        raise RuntimeError("Not glTF 2.0: "+name)
    # Only inline buffers are allowed in this stage; no external URI fetch,
    # path traversal, or unknown origin endpoints.
    buffer_uris=[b.get("uri","") for b in doc.get("buffers",[])]
    image_uris=[b.get("uri","") for b in doc.get("images",[])]
    external=[u for u in buffer_uris+image_uris if u and not u.startswith("data:")]
    if external:
        raise RuntimeError("External glTF buffers/images not included in licensed source; inspect manually: "+str(external[:5]))
    animations=[a.get("name","") for a in doc.get("animations",[])]
    row={
      "name":name,"file":str(p),
      "sha256":sha,"bytes":p.stat().st_size,
      "source":SOURCE,"official_folder":FOLDER,
      "drive_id":drive_id,"creator":"Quaternius",
      "license":"CC0-1.0",
      "mesh_count":len(doc.get("meshes",[])),
      "skins":len(doc.get("skins",[])),
      "animations":animations,"animation_count":len(animations),
      "external_resources":external,
      "warning":"Source license confirmed, import/rig/animation still require real Blender and visual QA."
    }
    manifest.append(row)
    print("HORSE_SOURCE_INSPECTED",json.dumps(row,ensure_ascii=False),flush=True)
out=Path("outputs/horse")
out.mkdir(parents=True,exist_ok=True)
(out/"source_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
if any(row["animation_count"]==0 for row in manifest):
    raise RuntimeError("A source horse has zero animations; refuse to call it ready-to-race.")
