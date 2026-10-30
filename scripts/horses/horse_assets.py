#!/usr/bin/env python3
"""Shared horse model discovery/download for ChatGPT, Claude, Copilot and Codex.

Requires authenticated GitHub CLI for private repos:
  gh auth login
  python3 scripts/horses/horse_assets.py list
  python3 scripts/horses/horse_assets.py pull horse-brown --dest ./public/models

Downloads an immutable versioned GitHub Release asset when available.
While the initial Release is not yet published, falls back to the already
validated but time-limited GitHub Actions artifact.
Always validates pinned SHA256, GLB header, real skin and animation clips.
No token logging; does not alter existing assets without --replace.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
REGISTRY=ROOT/"assets"/"horses"/"registry.json"

def load_registry():
    d=json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert d["schema_version"]==1
    return d

def locate(d,name):
    for item in d["horses"]:
        if item["id"]==name:return item
    raise ValueError("Unknown horse '%s'. Run 'list' to see available IDs" % name)

def inspect_glb(path):
    with path.open("rb") as f:
        header=f.read(20)
        if len(header)<20:raise ValueError("Truncated GLB")
        magic,version,total=struct.unpack_from("<4sII",header,0)
        if magic!=b"glTF" or version!=2 or total!=path.stat().st_size:
            raise ValueError("Invalid GLB 2.0 header / file size")
        chunk_len,kind=struct.unpack_from("<I4s",header,12)
        if kind!=b"JSON":raise ValueError("GLB JSON chunk missing")
        data=header[20:]+f.read(chunk_len)
        model=json.loads(data)
    count=len(model.get("animations",[]))
    bones=max([len(s.get("joints",[])) for s in model.get("skins",[])],default=0)
    prims=[p for m in model.get("meshes",[]) for p in m.get("primitives",[])]
    weighted=any("JOINTS_0" in p.get("attributes",{}) and
                 "WEIGHTS_0" in p.get("attributes",{}) for p in prims)
    return {"animations":count,"bones":bones,"skinned":weighted,
            "meshes":len(model.get("meshes",[])),
            "images":len(model.get("images",[]))}

def verify(path,item):
    sha=hashlib.sha256(path.read_bytes()).hexdigest()
    expected=item["model"]["sha256"]
    if sha!=expected:raise ValueError("SHA256 mismatch: expected %s got %s"%(expected,sha))
    if path.stat().st_size!=item["model"]["bytes"]:
        raise ValueError("Wrong GLB byte count")
    stats=inspect_glb(path)
    if stats["animations"]!=item["animation_count"] or stats["bones"]!=item["skeleton_bones"]:
        raise ValueError("GLB lost animations/bones: "+str(stats))
    if not stats["skinned"]:raise ValueError("GLB lost skin weights")
    return {"sha256":sha,**stats}

def gh(*arguments):
    if not shutil.which("gh"):
        raise RuntimeError("Install GitHub CLI first: https://cli.github.com")
    p=subprocess.run(["gh",*arguments],capture_output=True,text=True)
    if p.returncode!=0:
        raise RuntimeError("GitHub CLI download failed. Confirm repo access via 'gh auth status'. "
                           "CLI error: "+p.stderr.strip()[:800])
    return p.stdout

def from_release(d,item,target):
    # Never silently overwrite a binary or download arbitrary unsigned URLs.
    gh("release","download",item["release"]["tag"],
       "-R",d["repository"],"--pattern",item["model"]["release_file"],
       "--dir",str(target))
    path=target/item["model"]["release_file"]
    if not path.is_file():raise RuntimeError("Release asset not present: "+path.name)
    return path

def from_artifact(d,item,target):
    info=item["fallback"]
    gh("run","download",str(info["run_id"]),"-R",d["repository"],
       "--name",info["artifact_name"],"--dir",str(target))
    path=target/info["model_path"]
    if not path.is_file():
        raise RuntimeError("Actions artifact missing expected subpath: "+str(path))
    return path

def run():
    p=argparse.ArgumentParser(description=__doc__)
    commands=p.add_subparsers(dest="cmd",required=True)
    commands.add_parser("list",help="List authoritative model IDs, version and provenance")
    get=commands.add_parser("pull",help="Fetch a horse from GitHub Releases or CI artifact")
    get.add_argument("id")
    get.add_argument("--dest",type=Path,default=Path("public/models"))
    get.add_argument("--source",choices=("auto","release","artifact"),default="auto")
    get.add_argument("--replace",action="store_true",help="Explicitly replace existing model file")
    check=commands.add_parser("verify",help="Verify a local GLB against the pinned registry hash")
    check.add_argument("id")
    check.add_argument("file",type=Path)
    a=p.parse_args()
    data=load_registry()
    if a.cmd=="list":
        for m in data["horses"]:
            print("%-15s v%-7s %-38s %s"%(m["id"],m["version"],m["label"],m["stage"]))
        print("Repo: "+data["repository"]+" (authenticated access may be needed)")
        return
    item=locate(data,a.id)
    if a.cmd=="verify":
        print(json.dumps(verify(a.file,item),ensure_ascii=False,indent=2))
        return
    dest=a.dest.resolve()
    dest.mkdir(parents=True,exist_ok=True)
    output=dest/(item["id"]+"-v"+item["version"]+".glb")
    if output.exists() and not a.replace:
        print("Already exists. Verifying before re-use: "+str(output))
        print(json.dumps(verify(output,item),ensure_ascii=False))
        return
    with tempfile.TemporaryDirectory(prefix="horse_asset_") as tmp:
        temp=Path(tmp)
        errors=[]
        sources=("release","artifact") if a.source=="auto" else (a.source,)
        for source in sources:
            try:
                path=from_release(data,item,temp) if source=="release" else from_artifact(data,item,temp)
                result=verify(path,item)
                shutil.copy2(path,output)
                print("HORSE_ASSET_PULL_OK",json.dumps({
                    "id":item["id"],"version":item["version"],"path":str(output),
                    "download_source":source,"license":item["license"],"validation":result
                    },ensure_ascii=False))
                return
            except Exception as e:errors.append(source+": "+str(e))
        raise RuntimeError("Could not obtain pinned model. "+" | ".join(errors))

if __name__=="__main__":
    try:run()
    except (RuntimeError,ValueError,OSError) as exc:
        print("ERROR:",exc,file=sys.stderr)
        sys.exit(2)
