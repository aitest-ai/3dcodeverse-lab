#!/usr/bin/env python3
"""V31 source-locked local V28 runtime playtest copy. No public deployment or gameplay patch."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import stat
import sys
import tempfile
import zipfile
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

# Exact hashes read from protected V26/V27/V28 authentic source inventory.
V28_ZIP_SHA="2b83e637fca50f20eb4237b9ebc3ae52a4264079a686819b44d694c7978905d1"
PROTECTED={
 "data/world.json":"ec06865c6cb69f34c833b981e93df7a511c05e252afb2be278fc4f730e003fd5",
 "src/main.mjs":"7892f987cdf1b8119be7376f4e74f9e4e6abca255da7f54beffe6645844d0422",
 "src/asset-loader.mjs":"62a4afe9e5982a00b590ae67807260d40d34686a87cdb750d9f34a11871a975c",
 "src/avatar.mjs":"17916971e03247d21210e33e1272a79e8c09040f2493a4c40a061f426c353a5c",
 "assets/actor/jie-v110-arm-v02.glb":"4dab76c398f4c30c3aa62ef88e389b28974018c01fd271c08bf029d840d263d1",
 "assets/bicycle/bicycle.glb":"7cb53e92247cf081354c1551b91ae812aab56be7c07748ed00764f0d2c844ece",
 "assets/zones/onomichi.glb":"c1e6388b9ab4004d9b57620d558d2d17ace7293c00ab6dd38b3a26f23c367c2d",
 "assets/zones/harbour.glb":"6067d50d1c9701bc81c8540d69025e410d75002be4bf1d0192427288772bca02",
 "assets/zones/mukaishima.glb":"de0c393ffe271f3824ea5d283416ff8e12c19c6fe34b5955fa30ec7dd8ea63ea",
 "assets/zones/ferry.glb":"db9f54d8a5ade5563b6b5aa7abe7f129a65e76a44031661ccea9d7dd0ce1d89d",
 "review/halows-v16/halows-mukaishima-v15-surface.glb":"317106f7edaabd87df6d5ff8aef314c00a8a6905ba9b0b6478ee4a60afc765b0",
 "review/onomichi-v20/V20_SourceDEM_Corridor_Visual_Only.glb":"54f358eae488db5493dce3ca3a0a76ea99bb673baa8c3f3f63169d13bc3fa7ba",
}
# Do not accept placeholders or non-SHA source locks: fail closed at import.
for _path,_digest in PROTECTED.items():
    if len(_digest)!=64 or not re.fullmatch(r"[0-9a-f]{64}",_digest):
        raise RuntimeError("Source SHA lock malformed: "+_path)
MAX_TOTAL_UNCOMPRESSED=1_500_000_000
MAX_FILE_UNCOMPRESSED=350_000_000
MAX_ENTRIES=2000
TEST_LABEL="SYNTHETIC_FIXTURE_NOT_REAL_GAME"
REAL_LABEL="V28_ORIGINAL_ARCHIVE_AND_CORE_SHA_VERIFIED"

def sha256_file(path:pathlib.Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def validate_member(info:zipfile.ZipInfo)->tuple[str,...]:
    raw=info.filename
    if not raw or "\x00" in raw or "\\" in raw or raw.startswith("/") or ":" in raw.split("/")[0]:
        raise ValueError("Unsafe archive member name")
    components=raw.rstrip("/").split("/")
    if any(not part or part in (".","..") for part in components):
        raise ValueError("Archive traversal / ambiguous name rejected")
    mode=(info.external_attr >> 16) & 0o170000
    if mode not in (0,stat.S_IFREG,stat.S_IFDIR):
        raise ValueError("Archive links and special files forbidden")
    if info.file_size>MAX_FILE_UNCOMPRESSED:
        raise ValueError("Oversized archive file")
    if info.file_size>10_000_000 and info.compress_size<=100 and info.file_size>10000*max(1,info.compress_size):
        raise ValueError("Suspicious compression expansion")
    return tuple(components)

def inspect_archive(z:zipfile.ZipFile):
    infos=z.infolist()
    if not infos or len(infos)>MAX_ENTRIES:raise ValueError("Invalid archive entry count")
    size=0;by_path={};folded=set()
    for info in infos:
        validate_member(info)
        size+=info.file_size
        if size>MAX_TOTAL_UNCOMPRESSED:raise ValueError("Archive expansion over size budget")
        key=info.filename.rstrip("/")
        if key.casefold() in folded:raise ValueError("Duplicate/case-colliding archive file")
        folded.add(key.casefold())
        if not info.is_dir():by_path[key]=info
    possible=[]
    for name in by_path:
        if name.endswith("src/main.mjs"):
            prefix=name[:-len("src/main.mjs")]
            if prefix+"data/world.json" in by_path and prefix+"index.html" in by_path:
                possible.append(prefix)
    if len(possible)!=1:raise ValueError("Cannot uniquely identify authentic game root")
    prefix=possible[0]
    rel={}
    for name,info in by_path.items():
        if name.startswith(prefix):
            tail=name[len(prefix):]
            if tail:rel[tail]=info
    missing=[name for name in [*PROTECTED,"index.html"] if name not in rel]
    if missing:raise ValueError("Required original runtime files missing: "+", ".join(missing[:5]))
    return rel,prefix,size

def inject_observer(original:bytes)->bytes:
    try:html=original.decode("utf-8")
    except UnicodeDecodeError as e:raise ValueError("Original index is not UTF-8") from e
    if "ONOMICHI_V31_OBSERVER_INJECTION" in html:raise ValueError("Already instrumented")
    marker='<!-- ONOMICHI_V31_OBSERVER_INJECTION: cloned index only -->\n<script type="module" src="./review/onomichi-v31/observer.mjs"></script>\n'
    targets=list(re.finditer(r"</body\s*>",html,flags=re.IGNORECASE))
    if len(targets)!=1:raise ValueError("Need exactly one </body> to instrument copy")
    i=targets[0].start()
    return (html[:i]+marker+html[i:]).encode("utf-8")

def inspector(source:str)->dict:
    # Exact source hashes establish provenance; these names are hints, not API acceptance.
    return {
      "source_read":True,"expected_exports_present":{
         "AvatarDriver":"AvatarDriver" in source,
         "BicycleDriver":"BicycleDriver" in source},
      "source_module_imports":len(re.findall(r"^\s*import\b",source,re.MULTILINE)),
      "method_names_reference_only":sorted(set(re.findall(
          r"(?m)^\s{2,8}(?:async\s+)?([a-zA-Z_$][\w$]*)\s*\(",source)))[:80],
      "actual_driver_instantiated_by_v31":False,
      "note":"String and static source discovery only; live engine internals not exposed or mutated."
    }

def prepare(archive:pathlib.Path,target:pathlib.Path,*,fixture_mode:bool=False)->dict:
    """Create a separate copy; only internal tests may set fixture_mode=True."""
    archive=archive.resolve()
    target=target.resolve()
    if not archive.is_file():raise ValueError("Input ZIP not found")
    if target.exists():raise ValueError("Output exists; never overwrite existing game/version")
    target.parent.mkdir(parents=True,exist_ok=True)
    archive_sha=sha256_file(archive)
    if not fixture_mode and archive_sha!=V28_ZIP_SHA:
        raise ValueError("Full V28 package SHA256 mismatch; refusing unverified runtime")
    assets_root=pathlib.Path(__file__).resolve().parents[2]/"apps"/"onomichi-v31-original-runtime"
    if not all((assets_root/n).is_file() for n in ("observer.mjs","observer_ui.html","launch.html")):
        raise ValueError("V31 observer sources missing")
    with zipfile.ZipFile(archive) as z:
        rel,prefix,total=inspect_archive(z)
        work=pathlib.Path(tempfile.mkdtemp(prefix=".v31-candidate-",dir=target.parent))
        try:
            # No ZipFile.extract: all paths are checked, sizes bounded and writes are streamed.
            for name,info in rel.items():
                dest=work.joinpath(*name.split("/"))
                dest.parent.mkdir(parents=True,exist_ok=True)
                with z.open(info) as read,dest.open("wb") as out:
                    shutil.copyfileobj(read,out,1024*1024)
            observed={name:sha256_file(work/name) for name in PROTECTED}
            if not fixture_mode:
                bad=[name for name,digest in observed.items() if digest!=PROTECTED[name]]
                if bad:raise ValueError("Protected original file hashes changed: "+", ".join(bad[:5]))
            original_index=(work/"index.html").read_bytes()
            original_index_sha=hashlib.sha256(original_index).hexdigest()
            instrumented=inject_observer(original_index)
            (work/"index.html").write_bytes(instrumented)
            review=work/"review"/"onomichi-v31"
            review.mkdir(parents=True,exist_ok=True)
            shutil.copy2(assets_root/"observer.mjs",review/"observer.mjs")
            shutil.copy2(assets_root/"observer_ui.html",review/"observer_ui.html")
            shutil.copy2(assets_root/"launch.html",review/"index.html")
            src=(work/"src/avatar.mjs").read_text(encoding="utf-8")
            status=TEST_LABEL if fixture_mode else REAL_LABEL
            audit={
              "schema":"setouchi.v31.runtime.audit.v1","candidate":"V31",
              "status":status,"original_v28_archive_sha256":archive_sha,
              "expected_v28_archive_sha256":V28_ZIP_SHA,
              "source_root_in_zip":prefix,
              "source_members_count":len(rel),"source_uncompressed_bytes":total,
              "original_index_sha256":original_index_sha,
              "observed_core_sha256":observed,
              "expected_protected_sha256":PROTECTED if not fixture_mode else None,
              "core_hashes_verified":not fixture_mode,
              "original_game_core_changed":False,
              "instrumented_copy_index_only":True,
              "added_files":["review/onomichi-v31/observer.mjs",
                             "review/onomichi-v31/index.html",
                             "review/onomichi-v31/observer_ui.html",
                             "review/onomichi-v31/audit.json"],
              "original_driver_source_inspection":inspector(src),
              "original_avatar_driver_live_integration_verified":False,
              "actual_rider_hands_pedals_verified":False,
              "real_gameplay_playtest_verified":False,
              "android_onsite_verified":False,
              "road_collision_or_rights_verified":False,
              "website_deployed":False,
              "private_runtime_committed_to_git":False,
              "observer_scope":"read-only human playtest evidence: inputs/canvas presence, no geometry/physics/game variable hooks"
            }
            (review/"audit.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            work.rename(target)
            return audit
        except BaseException:
            shutil.rmtree(work,ignore_errors=True)
            raise

def serve(target:pathlib.Path,port:int):
    if not target.is_dir():raise ValueError("Prepared test directory not found")
    handler=partial(SimpleHTTPRequestHandler,directory=str(target))
    server=ThreadingHTTPServer(("127.0.0.1",port),handler)
    print("V31 local-only game: http://127.0.0.1:"+str(server.server_port)+"/")
    print("V31 QA portal: http://127.0.0.1:"+str(server.server_port)+"/review/onomichi-v31/")
    print("Only this machine can connect; stop with Ctrl+C.")
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

def main(argv=None):
    parser=argparse.ArgumentParser(description="V31 authentic V28 ZIP verifier + separate local playtest overlay")
    parser.add_argument("--zip",type=pathlib.Path,required=True,help="Exact V28 full original runtime ZIP")
    parser.add_argument("--out",type=pathlib.Path,required=True,help="New empty output path; existing folders rejected")
    parser.add_argument("--serve",action="store_true",help="Serve cloned game on loopback only")
    parser.add_argument("--port",type=int,default=8767)
    args=parser.parse_args(argv)
    try:
        audit=prepare(args.zip,args.out)
        print(json.dumps({k:audit[k] for k in ("status","original_v28_archive_sha256",
             "source_members_count","core_hashes_verified","original_game_core_changed")},
             ensure_ascii=False,indent=2))
        print("Original ZIP untouched; game clone: "+str(args.out.resolve()))
        if args.serve:serve(args.out.resolve(),args.port)
        return 0
    except (ValueError,OSError,zipfile.BadZipFile) as error:
        print("V31 rejected: "+str(error),file=sys.stderr)
        return 2
if __name__=="__main__":
    sys.exit(main())
