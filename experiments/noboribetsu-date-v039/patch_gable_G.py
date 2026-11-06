#!/usr/bin/env python3
"""Apply a surgical right-gable winding correction to a SHA-verified V004 GLB.
Only changes face 13's last two indices; no original file overwrites.
Usage: python patch_gable_G.py ORIGINAL_V004_GLb NEW_G_GLb
"""
from pathlib import Path
import hashlib,struct,json,sys
SRC="132ee6c0add22fbfe4a9872d82cb5e6bed0e2e4f282533b6c61de6c156a7a5e3"
G="bced01973a6a4c1909427092175ee924e73a1daed01b0f66608c60c0a91ffc03"
def sha(b): return hashlib.sha256(b).hexdigest()
if len(sys.argv)!=3:raise SystemExit(__doc__)
source,out=map(Path,sys.argv[1:])
if out.exists():raise FileExistsError("output already exists")
blob=source.read_bytes()
assert sha(blob)==SRC
assert struct.unpack_from("<4sII",blob,0)==(b"glTF",2,len(blob))
n,t=struct.unpack_from("<I4s",blob,12);assert t==b"JSON"
gl=json.loads(blob[20:20+n])
m=gl["meshes"][1]
assert m["name"]=="plaster_lower"
p=m["primitives"][0];acc=gl["accessors"][p["indices"]];v=gl["bufferViews"][acc["bufferView"]]
assert acc["count"]==126 and acc["componentType"]==5125
start=20+n+8+v["byteOffset"]+acc.get("byteOffset",0)
before=list(struct.unpack_from("<6I",blob,start+12*4*3))
assert before==[8,9,10,11,12,13],before
patched=bytearray(blob)
# Triangle 13 = array positions 39,40,41: (11,12,13) -> (11,13,12).
struct.pack_into("<I",patched,start+40*4,13)
struct.pack_into("<I",patched,start+41*4,12)
outdata=bytes(patched)
assert sha(outdata)==G and len(outdata)==len(blob)
out.write_bytes(outdata)
print("PASS:",out.name,sha(outdata))