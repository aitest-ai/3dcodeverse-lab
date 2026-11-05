#!/usr/bin/env python3
"""V28 original browser runtime: verified ZIP -> static assets, ONLY at Vercel build time.

NO source model bytes, private URLs, tokens, or user data are committed to GitHub.
The full archive is supplied as a time-limited HTTPS URL using a secret project
environment variable V28_ARCHIVE_URL. Build logs print only public SHA/bytes.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import zipfile

EXPECTED_ARCHIVE_SHA="2b83e637fca50f20eb4237b9ebc3ae52a4264079a686819b44d694c7978905d1"
EXPECTED_ARCHIVE_BYTES=235696298
ZIP_PREFIX="onomichi-cycling-v28/"
SOURCE={
 "data/world.json":"ec06865c6cb69f34c833b981e93df7a511c05e252afb2be278fc4f730e003fd5",
 "src/main.mjs":"7892f987cdf1b8119be7376f4e74f9e4e6abca255da7f54beffe6645844d0422",
 "src/avatar.mjs":"17916971e03247d21210e33e1272a79e8c09040f2493a4c40a061f426c353a5c",
 "src/asset-loader.mjs":"62a4afe9e5982a00b590ae67807260d40d34686a87cdb750d9f34a11871a975c",
 "assets/actor/jie-v110-arm-v02.glb":"4dab76c398f4c30c3aa62ef88e389b28974018c01fd271c08bf029d840d263d1",
 "assets/bicycle/bicycle.glb":"7cb53e92247cf081354c1551b91ae812aab56be7c07748ed00764f0d2c844ece",
 "assets/zones/harbour.glb":"6067d50d1c9701bc81c8540d69025e410d75002be4bf1d0192427288772bca02",
 "assets/zones/onomichi.glb":"c1e6388b9ab4004d9b57620d558d2d17ace7293c00ab6dd38b3a26f23c367c2d",
 "assets/zones/mukaishima.glb":"de0c393ffe271f3824ea5d283416ff8e12c19c6fe34b5955fa30ec7dd8ea63ea",
 "assets/zones/ferry.glb":"db9f54d8a5ade5563b6b5aa7abe7f129a65e76a44031661ccea9d7dd0ce1d89d",
 "review/halows-v16/halows-mukaishima-v15-surface.glb":"317106f7edaabd87df6d5ff8aef314c00a8a6905ba9b0b6478ee4a60afc765b0",
 "review/onomichi-v20/V20_SourceDEM_Corridor_Visual_Only.glb":"54f358eae488db5493dce3ca3a0a76ea99bb673baa8c3f3f63169d13bc3fa7ba",
}
for path,value in SOURCE.items():
 assert re.fullmatch(r"[0-9a-f]{64}",value),(path,"bad source")
DISTRIBUTE_PREFIXES=("assets/","data/","src/","vendor/","review/")
DISTRIBUTE_FILES=("index.html","styles.css","README-runtime.md","NOTICE.md")
IGNORE_SUFFIX=(".blend",".py",".zip",".sqlite",".sqlite3")
MAX_BYTES=300_000_000

def sha256(path):
 h=hashlib.sha256()
 with path.open("rb") as file:
  for chunk in iter(lambda:file.read(1024*1024),b""):h.update(chunk)
 return h.hexdigest()

def download(target):
 local=os.environ.get("V28_LOCAL_ZIP")
 if local:
  source=Path(local).resolve()
  if not source.is_file():raise RuntimeError("V28_LOCAL_ZIP is missing")
  shutil.copyfile(source,target)
 else:
  url=os.environ.get("V28_ARCHIVE_URL","")
  endpoint=urlsplit(url)
  if endpoint.scheme!="https" or not endpoint.hostname or not endpoint.hostname.endswith(".oaiusercontent.com"):
   raise RuntimeError("A private HTTPS V28_ARCHIVE_URL build secret is required")
  request=Request(url,headers={"User-Agent":"V28-provenance-build/1.0"})
  h=hashlib.sha256();size=0
  # The signed URL must never appear in build output, errors or generated files.
  try:
   with urlopen(request,timeout=90) as response,target.open("wb") as output:
    while True:
     chunk=response.read(1024*1024)
     if not chunk:break
     size+=len(chunk)
     if size>EXPECTED_ARCHIVE_BYTES:raise RuntimeError("Archive download exceeds expected size")
     output.write(chunk)
     h.update(chunk)
  except Exception as error:
   raise RuntimeError("The authorized V28 archive could not be transferred to build runner") from None
  if size!=EXPECTED_ARCHIVE_BYTES or h.hexdigest()!=EXPECTED_ARCHIVE_SHA:
   raise RuntimeError("Authenticated source archive size/SHA mismatch")
 if target.stat().st_size!=EXPECTED_ARCHIVE_BYTES or sha256(target)!=EXPECTED_ARCHIVE_SHA:
  raise RuntimeError("V28 original archive SHA256/size verification failed")

def safe_member(member):
 s=member.filename
 if not s.startswith(ZIP_PREFIX) or "\\" in s or s.startswith("/") or ".." in PurePosixPath(s).parts:
  raise RuntimeError("Archive member path failed source safety check")
 rest=s[len(ZIP_PREFIX):]
 if rest and (any(t in ("..",".","") for t in PurePosixPath(rest).parts) or ":" in rest):
  raise RuntimeError("Archive member path is unsafe")
 return rest

def include(path):
 if path.endswith(IGNORE_SUFFIX):return False
 return path in DISTRIBUTE_FILES or path.startswith(DISTRIBUTE_PREFIXES)

def build():
 root=Path(__file__).resolve().parent
 dest=root/"dist"
 with tempfile.TemporaryDirectory(prefix="setouchi-v28-verified-") as tmp:
  archive=Path(tmp)/"original-v28.zip"
  download(archive)
  print("V28 source archive size and SHA256 verified",flush=True)
  if dest.exists():shutil.rmtree(dest)
  dest.mkdir()
  extracted=0;bytes_written=0;names=set()
  with zipfile.ZipFile(archive) as file:
   for info in file.infolist():
    if info.is_dir():continue
    relative=safe_member(info)
    if not include(relative):continue
    if relative in names:raise RuntimeError("Duplicate included asset path")
    names.add(relative)
    if info.file_size>MAX_BYTES:raise RuntimeError("Individual asset too large")
    output=dest.joinpath(*PurePosixPath(relative).parts)
    output.parent.mkdir(parents=True,exist_ok=True)
    hash=hashlib.sha256()
    with file.open(info) as stream,output.open("wb") as handle:
     while True:
      block=stream.read(1024*1024)
      if not block:break
      handle.write(block);hash.update(block)
    bytes_written+=info.file_size;extracted+=1
    if relative in SOURCE and hash.hexdigest()!=SOURCE[relative]:
     raise RuntimeError("Original source invariant failed: "+relative)
  missing=set(SOURCE)-names
  if missing:raise RuntimeError("Protected original assets missing from deploy output: "+str(sorted(missing)))
  world=json.loads((dest/"data/world.json").read_text(encoding="utf8"))
  for asset_id,asset in world["assets"].items():
   rel=asset["url"];path=dest/rel
   if not path.is_file() or path.stat().st_size!=asset["bytes"] or sha256(path)!=asset["sha256"]:
    raise RuntimeError("World asset manifest mismatch: "+asset_id)
  html=(dest/"index.html").read_text(encoding="utf8")
  if '<script type="module" src="./src/main.mjs"></script>' not in html and 'src/main.mjs' not in html:
   raise RuntimeError("Original main entrypoint missing from HTML")
  report={
   "schema_version":1,"release":"V28-ORIGINAL-STATIC-PREVIEW",
   "source_archive_sha256":EXPECTED_ARCHIVE_SHA,
   "original_world_sha256":SOURCE["data/world.json"],
   "original_main_sha256":SOURCE["src/main.mjs"],
   "original_avatar_sha256":SOURCE["src/avatar.mjs"],
   "original_game_code_modified":False,
   "asset_ids":list(world["assets"]),
   "original_protected_files_verified":len(SOURCE),
   "static_files":extracted,
   "static_total_bytes":bytes_written,
   "road_to_halows_rideable_approved":False,
   "field_survey_verified":False,
   "android_playtest_verified":False,
   "build_secret_exposed":False,
   "note":"True original V28 assets, source locked. No gameplay or physical-road safety approvals."
  }
  (dest/"PREVIEW_PROVENANCE.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
  print("Static preview packaged: files=",extracted,"bytes=",bytes_written,
        "protectedSHAchecks=",len(SOURCE),"original-runtime-code-unchanged=yes",flush=True)
if __name__=="__main__":build()
