#!/usr/bin/env python3
"""Inspect the public, author-published Quaternius Drive folder without downloading all asset packs.

A discovery tool, not a license bypass. Returns a JSON inventory for the user and
a machine-readable list for the next pipeline stage.
"""
import json
from pathlib import Path
import gdown

URL="https://drive.google.com/drive/folders/1uJ3N5HfB7jKTseJUNQr3N4YaN0UuEtHk?usp=sharing"
out=Path("outputs/horse_source_discovery")
out.mkdir(parents=True,exist_ok=True)
print("GDOWN_VERSION", getattr(gdown,"__version__","unknown"))
try:
    result=gdown.download_folder(url=URL,quiet=False,remaining_ok=True,skip_download=True)
    print("DISCOVERY_RESULT",repr(result))
    data={"source_url":URL,"method":"gdown.download_folder skip_download=True",
          "result":result,"status":"metadata_only_no_assets_downloaded",
          "notice":"Do not claim a usable model until a full horse file passes import and animation checks"}
except Exception as exc:
    data={"source_url":URL,"method":"gdown folder metadata",
          "status":"failed","error":type(exc).__name__+": "+str(exc),
          "fallback":"Use the official Quaternius download page to manually obtain the CC0 archive."}
(out/"discovery.json").write_text(json.dumps(data,indent=2,ensure_ascii=False,default=str),encoding="utf-8")
print("DISCOVERY_JSON",json.dumps(data,ensure_ascii=False,default=str))
# Keep the job successful so the inventory is always uploaded and available.
