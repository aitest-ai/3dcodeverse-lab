"""Verify original MakeHuman Faceunits 01 CC0 targets and produce an audit manifest.

The archive contains ARKit-style .target files from Mika Suominen (CC0).
Never guess names or replace vertex deltas with fake spherical mouth animation.
"""
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.error import URLError
import hashlib,json,zipfile,os,math
PACK_URLS=[
  "https://files2.makehumancommunity.org/functional/faceunits01.zip",
  "https://files.makehumancommunity.org/functional/faceunits01.zip",
]
DEST=Path(os.getenv("FACEUNITS_ROOT",".deps/mh_faceunits")).resolve()
DEST.mkdir(parents=True,exist_ok=True)
archive=DEST/"faceunits01.zip"
errors=[]
if not archive.exists():
    for url in PACK_URLS:
        try:
            with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0 MPFB verified CC0 research"}),timeout=80) as response, archive.open("wb") as output:
                while True:
                    chunk=response.read(1<<18)
                    if not chunk:break
                    output.write(chunk)
            print("FACEUNIT_SOURCE",url,flush=True)
            break
        except Exception as exc:
            errors.append(f"{url}: {exc}")
            archive.unlink(missing_ok=True)
if not archive.exists():raise RuntimeError("No CC0 Faceunits archive: "+str(errors))
if not zipfile.is_zipfile(archive):raise RuntimeError("Faceunits not a valid zip")
EXPECTED_ARCHIVE_SHA256="d113107bd7eb59f3af4df6fc0ec29bfcc593f496d0b336aec14f086a80ce7146"
actual_archive_sha=hashlib.sha256(archive.read_bytes()).hexdigest()
if actual_archive_sha!=EXPECTED_ARCHIVE_SHA256:
    raise RuntimeError("Faceunits01 checksum drift: verify source and license before using: "+actual_archive_sha)
records=[]
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for item in z.infolist():
        p=Path(item.filename)
        if p.is_absolute() or ".." in p.parts:raise RuntimeError("Unsafe name "+item.filename)
        if item.file_size>25*1024*1024:raise RuntimeError("Unexpected large member")
        if item.is_dir():continue
        if not item.filename.lower().endswith((".target",".target.gz",".json",".md",".txt")):continue
        output=DEST/"original"/item.filename
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_bytes(z.read(item))
        rec={"path":str(output.relative_to(DEST)),"size":item.file_size}
        if item.filename.lower().endswith(".target"):
            payload=z.read(item).decode("utf-8","replace")
            ids=[]
            for l in payload.splitlines():
                cols=l.split()
                if not cols or cols[0].startswith("#"):continue
                try:
                    v=int(cols[0])
                    if len(cols)<4:continue
                    ids.append(v)
                except Exception:pass
            rec.update({"vertices":len(ids),"min_index":min(ids) if ids else None,"max_index":max(ids) if ids else None})
        records.append(rec)
if len([r for r in records if r["path"].endswith(".target")])<8:raise RuntimeError("Expected 8+ genuine targets, only "+str(records))
manifest={"license":"CC0 (official Faceunits01 pack)", "contributor":"Mika Suominen",
  "source_page":"https://static.makehumancommunity.org/assets/assetpacks/faceunits01.html",
  "source_url":next((u for u in PACK_URLS if not errors or u not in [e.split(": ")[0] for e in errors]),PACK_URLS[0]),
  "archive_sha256":hashlib.sha256(archive.read_bytes()).hexdigest(),
  "archive_bytes":archive.stat().st_size,
  "targets":records}
(DEST/"faceunits_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
print("FACEUNIT_MANIFEST",json.dumps(manifest,ensure_ascii=False),flush=True)
