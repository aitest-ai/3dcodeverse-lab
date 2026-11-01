#!/usr/bin/env python3
"""Deterministic runtime-equivalent V005 FinalPolish A patch.

This script is intentionally source-protected. It only accepts the pinned V005
baseline environment GLB and produces the browser-validated A SHA.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, random, struct
from pathlib import Path

BASELINE_SHA = "32ddd3721e75b95f54ade22304e4d383930e4411507b0858f7d957f7171462d4"
OUTPUT_SHA = "752887763308bf71342b0d9ac292fc0f30ffa2e30d0ec6639e7373bb03cd5a55"
DEPTH = [0.055, 0.050, 0.044, 1.0]
REVEAL = [0.070, 0.063, 0.052, 1.0]
SEED = 1505006


def sha256(path: Path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def read_glb(path: Path):
    data = path.read_bytes()
    magic, ver, total = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or ver != 2 or total != len(data):
        raise ValueError("Not a valid GLB 2.0 file")
    off, chunks = 12, []
    while off < len(data):
        ln, typ = struct.unpack_from("<II", data, off)
        off += 8
        chunks.append((typ, bytearray(data[off:off+ln])))
        off += ln
    js = json.loads(chunks[0][1].decode("utf-8").rstrip(" \t\r\n\x00"))
    return js, chunks


def pack_glb(js, chunks):
    jb = json.dumps(js, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    jb += b" " * ((4 - len(jb) % 4) % 4)
    out = bytearray(struct.pack("<4sII", b"glTF", 2, 0))
    for i, (typ, buf) in enumerate(chunks):
        payload = bytearray(jb) if i == 0 else buf
        out += struct.pack("<II", len(payload), typ) + payload
    struct.pack_into("<I", out, 8, len(out))
    return bytes(out)


def accessor_values(js, binbuf, ai):
    a = js["accessors"][ai]; bv = js["bufferViews"][a["bufferView"]]
    comp_fmt = {5121:"B",5123:"H",5125:"I",5126:"f"}[a["componentType"]]
    comps = {"SCALAR":1,"VEC2":2,"VEC3":3,"VEC4":4}[a["type"]]
    size = struct.calcsize("<" + comp_fmt) * comps
    stride = bv.get("byteStride", size)
    off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    vals=[]
    for i in range(a["count"]):
        vals.append(struct.unpack_from("<" + comp_fmt*comps, binbuf, off+i*stride))
    return vals


def index_info(js, binbuf, ai):
    a=js["accessors"][ai]; bv=js["bufferViews"][a["bufferView"]]
    fmt={5121:"B",5123:"H",5125:"I"}[a["componentType"]]; sz=struct.calcsize("<"+fmt)
    off=bv.get("byteOffset",0)+a.get("byteOffset",0)
    vals=[struct.unpack_from("<"+fmt,binbuf,off+i*sz)[0] for i in range(a["count"])]
    return vals,fmt,sz,off,a


def gap_field(x):
    return math.sin(x*0.73+0.85)+0.52*math.sin(x*1.91-0.37)+0.23*math.cos(x*3.17+1.1)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--source",type=Path,required=True); p.add_argument("--output",type=Path,required=True)
    a=p.parse_args(); src=a.source.resolve(); out=a.output.resolve()
    if src == out: raise SystemExit("Refuse to overwrite baseline GLB")
    if sha256(src) != BASELINE_SHA: raise SystemExit("Unexpected baseline GLB SHA-256")
    js,chunks=read_glb(src); binbuf=chunks[1][1]
    mats={m.get("name"):m for m in js.get("materials",[])}
    for name,new in [("V005 neutral unmodeled dark depth",DEPTH),("V005 neutral closed window reveal",REVEAL)]:
        if name not in mats: raise SystemExit(f"Missing material: {name}")
        mats[name]["pbrMetallicRoughness"]["baseColorFactor"]=new
    rng=random.Random(SEED); total_removed=0; objects=[]
    for node in sorted((n for n in js["nodes"] if n.get("name","").startswith("V005 clustered grass ")),key=lambda n:n["name"]):
        prim=js["meshes"][node["mesh"]]["primitives"][0]
        pos=accessor_values(js,binbuf,prim["attributes"]["POSITION"])
        inds,fmt,sz,ioff,ia=index_info(js,binbuf,prim["indices"]); kept=[]; removed=0
        for k in range(0,len(inds),3):
            tri=inds[k:k+3]; cx=sum(pos[i][0] for i in tri)/3; z=sum(pos[i][2] for i in tri)/3
            remove=3.02<=z<=3.32 and gap_field(cx)>0.73 and rng.random()<0.72
            if remove: removed+=1
            else: kept.extend(tri)
        for j,v in enumerate(kept): struct.pack_into("<"+fmt,binbuf,ioff+j*sz,v)
        suffix=(len(inds)-len(kept))*sz
        if suffix: binbuf[ioff+len(kept)*sz:ioff+len(inds)*sz]=b"\x00"*suffix
        ia["count"]=len(kept); total_removed+=removed
        objects.append({"object":node["name"],"removed":removed})
    if len(objects)!=5: raise SystemExit(f"Expected 5 clustered grass objects, found {len(objects)}")
    blob=pack_glb(js,chunks); out.parent.mkdir(parents=True,exist_ok=True); tmp=out.with_suffix(out.suffix+".tmp"); tmp.write_bytes(blob); os.replace(tmp,out)
    digest=sha256(out)
    if digest != OUTPUT_SHA: raise SystemExit(f"Deterministic output SHA mismatch: {digest}")
    print(json.dumps({"status":"ok","output":str(out),"sha256":digest,"bytes":out.stat().st_size,"grass_triangles_removed":total_removed,"objects":objects},ensure_ascii=False,indent=2))

if __name__ == "__main__": main()
