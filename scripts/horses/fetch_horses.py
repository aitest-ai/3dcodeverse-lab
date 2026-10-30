#!/usr/bin/env python3
"""Download verified CC0 horse from an independently published game project.

This is a *different* three-clip Quaternius source than the creator's blocked
13-clip original folder. Do not claim they're the same source file.
Provenance:
 Original creator: Quaternius; license: CC0;
 Poly Pizza: https://poly.pizza/m/qvTrSG9pZF
 Public project attribution: https://github.com/crisleyhguimaraes/space-ship/blob/main/docs/ASSETS.md
 Source bytes are pinned to an inspected SHA-256. No login, secrets, or bypass.
"""
import hashlib
import json
import urllib.request
from pathlib import Path

URL="https://raw.githubusercontent.com/crisleyhguimaraes/space-ship/main/public/models/adventurers/horse.glb"
EXPECTED="153a2d9ab63e3ea50c5e4966b9d8b07a666714f7a15758acc2b3374c41c9ab70"
root=Path("inputs/horses")
root.mkdir(parents=True,exist_ok=True)
p=root/"source_cc0_horse_compressed.glb"
req=urllib.request.Request(URL,headers={"User-Agent":"3dcodeverse-horse-evaluation/1.0"})
with urllib.request.urlopen(req,timeout=50) as response:
    if response.geturl().split("/")[2] != "raw.githubusercontent.com":
        raise RuntimeError("Unexpected download host; refused")
    content=response.read(15*1024*1024+1)
if not 10000<len(content)<15*1024*1024:
    raise RuntimeError("Unexpected public model bytes")
sha=hashlib.sha256(content).hexdigest()
if sha!=EXPECTED:raise RuntimeError("Public model changed. Review license/source/asset contents before accepting new checksum.")
p.write_bytes(content)
meta={
  "creator":"Quaternius","license":"CC0-1.0",
  "original_asset":"https://poly.pizza/m/qvTrSG9pZF",
  "mirror_project":"https://github.com/crisleyhguimaraes/space-ship/blob/main/docs/ASSETS.md",
  "download_url":URL,"download_sha256":sha,"download_bytes":len(content),
  "note":"Mirror model has 3 clips (Idle/Walk/Gallop) and meshopt compression; not the 13-clip Ultimate Animated Animals file in the quota-blocked Drive.",
  "derivatives":["Horse","Horse_White (programmatic palette recolor, NOT official Horse_White file)"],
  "license_evidence":"https://quaternius.com/packs/ultimateanimatedanimals.html and https://poly.pizza/m/qvTrSG9pZF; verify independent model-specific license before reuse."
}
out=Path("outputs/horse");out.mkdir(parents=True,exist_ok=True)
(out/"source_manifest.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print("PUBLIC_HORSE_CC0_SHA256_OK",json.dumps(meta,ensure_ascii=False),flush=True)
