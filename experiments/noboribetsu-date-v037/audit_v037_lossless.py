#!/usr/bin/env python3
"""V037 read-only lossless candidate contract: original GLB -> two material-only variants.
Requires Python standard library only. Usage:
python audit_v037_lossless.py original_v004_merchant_facades.glb V037_soft.glb V037_blend.glb
"""
from pathlib import Path
import hashlib,struct,json,sys
SOURCE_SHA="132ee6c0add22fbfe4a9872d82cb5e6bed0e2e4f282533b6c61de6c156a7a5e3"
EXPECTED={"soft":"fae86ba7a240cd19c99340be61953144f32856d594ce6ab68b1f9b4fb6e31112","blend":"ef38cdc679c70c01db01e3c69e420cd97205d10ae6bca43e15b3a5672b19ff03"}
def sha(b):return hashlib.sha256(b).hexdigest()
def glb(path):
 b=Path(path).read_bytes()
 magic,version,length=struct.unpack_from("<4sII",b,0)
 assert magic==b"glTF" and version==2 and length==len(b)
 n,t=struct.unpack_from("<I4s",b,12);assert t==b"JSON"
 j=json.loads(b[20:20+n])
 off=20+n;blen,t=struct.unpack_from("<I4s",b,off)
 assert t==b"BIN\x00" and off+8+blen==len(b)
 return b,j,b[off+8:]
b,j0,bin0=glb(sys.argv[1])
assert sha(b)==SOURCE_SHA and len(j0["meshes"])==17
p0=j0["meshes"][0]["primitives"][0]
old=j0["accessors"][p0["indices"]];v0=j0["bufferViews"][old["bufferView"]]
indices=list(struct.unpack_from("<144I",bin0,v0.get("byteOffset",0)))
assert len(indices)==144 and indices[24:30]==[3,7,6,3,6,2]
for mode,path in zip(("soft","blend"),sys.argv[2:4]):
 blob,j,data=glb(path)
 assert sha(blob)==EXPECTED[mode]
 assert data.startswith(bin0),"Original model GLB BIN changed"
 assert j["meshes"][1:]==j0["meshes"][1:],"Another building mesh changed"
 assert j["nodes"]==j0["nodes"],"Original nodes or transforms changed"
 assert j["materials"][:len(j0["materials"])]==j0["materials"]
 ps=j["meshes"][0]["primitives"];assert len(ps)==2
 def face_indices(p):
  acc=j["accessors"][p["indices"]];view=j["bufferViews"][acc["bufferView"]]
  count=acc["count"]
  return list(struct.unpack_from(f"<{count}I",data,view.get("byteOffset",0)+acc.get("byteOffset",0)))
 rest,roof=map(face_indices,ps)
 assert len(rest)==138 and roof==[3,7,6,3,6,2]
 assert rest[:24]+roof+rest[24:]==indices,"48 faces changed or reordered"
 assert ps[0]["attributes"]==p0["attributes"]
 assert ps[1]["attributes"]["POSITION"]==p0["attributes"]["POSITION"]
 print(mode,sha(blob),"PASS: 46+2 triangles; all original binary and vertices preserved")
print("PASS: original 17 logical meshes, no geometry changes or potential V035-B perimeter displacement")
