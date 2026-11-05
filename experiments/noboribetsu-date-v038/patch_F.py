#!/usr/bin/env python3
"""Reproducible raw-GLB F candidate patch; no original model overwrite.
Usage: python patch_F.py original_v004_merchant_facades.glb NEW_OUTPUT.glb
Standalone asset patch; complete V037 Inspector integration in the user's V038 SourceQA.
"""
from pathlib import Path
import hashlib, struct, json, sys
SOURCE_SHA = "132ee6c0add22fbfe4a9872d82cb5e6bed0e2e4f282533b6c61de6c156a7a5e3"
EXPECTED_F_SHA = "d9232643103378644ea89b780126a8c516c1a41da70edfaa2542916da558e1a0"
VERTICES = (2,3,6,7)
DELTA_Y = -0.225 # Artist-model units, not surveyed dimensions
sha = lambda data: hashlib.sha256(data).hexdigest()
def patch(src, dest):
    src, dest = Path(src), Path(dest)
    if dest.exists(): raise FileExistsError(f"Refusing overwrite: {dest}")
    original = src.read_bytes()
    assert sha(original) == SOURCE_SHA, "Wrong sealed original GLB"
    assert struct.unpack_from("<4sII", original, 0)==(b"glTF", 2, len(original))
    json_len, kind = struct.unpack_from("<I4s", original, 12)
    assert kind == b"JSON"
    data = json.loads(original[20:20+json_len])
    bhead=20+json_len;bin_len,kind=struct.unpack_from("<I4s", original,bhead)
    assert kind == b"BIN\\0" and bhead+8+bin_len==len(original)
    assert len(data["meshes"])==17 and data["meshes"][0]["name"]=="plaster_offwhite"
    prim=data["meshes"][0]["primitives"][0]
    pos=data["accessors"][prim["attributes"]["POSITION"]]
    assert pos["count"]==32 and pos["componentType"]==5126 and pos["type"]=="VEC3"
    view=data["bufferViews"][pos["bufferView"]]
    assert view.get("byteStride",12)==12
    start=bhead+8+view.get("byteOffset",0)+pos.get("byteOffset",0)
    out=bytearray(original)
    for vi in VERTICES:
        x,y,z=struct.unpack_from("<3f",out,start+vi*12)
        assert abs(y-6.72852039)<1e-4 and 1.8<x<22.1 and 45<z<57
        struct.pack_into("<f",out,start+vi*12+4,y+DELTA_Y)
    result=bytes(out)
    assert sha(result)==EXPECTED_F_SHA, "Unexpected geometry output"
    dest.write_bytes(result)
    print("PASS",dest.name,"SHA256",sha(result))
if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit(__doc__)
    patch(sys.argv[1],sys.argv[2])
