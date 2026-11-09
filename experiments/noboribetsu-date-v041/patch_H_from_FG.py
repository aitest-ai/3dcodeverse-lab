#!/usr/bin/env python3
"""V041 H: patch 16 top Y coordinates in the sealed F+G GLB into an independent file.
Usage: python patch_H_from_FG.py SEALED_FG.glb NEW_H.glb
No original file overwritten. The complete replay and browser QA are in SourceQA.zip.
"""
from pathlib import Path
import hashlib,json,struct,sys
SRC="5583d3d9c54eb19ac4396f4a9803e57fe337daeaf70e446c249a5337758d5985"
DST="9d6ec28e7844c3b522b6b1453426334f36da580808ad78bd4bc3e7c5969463f4"
IDS=(10,11,14,15,18,19,22,23,26,27,30,31,34,35,38,39)
def sha(b): return hashlib.sha256(b).hexdigest()
def patch(old,new):
    old,new=Path(old),Path(new)
    if new.exists(): raise FileExistsError("Refusing to overwrite existing file")
    original=old.read_bytes()
    assert sha(original)==SRC
    assert struct.unpack_from("<4sII",original,0)==(b"glTF",2,len(original))
    n,chunk=struct.unpack_from("<I4s",original,12)
    assert chunk==b"JSON"
    j=json.loads(original[20:20+n]);start=20+n
    length,chunk=struct.unpack_from("<I4s",original,start)
    assert chunk==bytes([66,73,78,0]) and start+8+length==len(original)
    mesh=j["meshes"][2]; assert mesh["name"]=="wood_dark"
    ac=j["accessors"][mesh["primitives"][0]["attributes"]["POSITION"]]
    view=j["bufferViews"][ac["bufferView"]]
    assert ac["count"]==812 and ac["componentType"]==5126 and ac["type"]=="VEC3"
    offset=start+8+view.get("byteOffset",0)+ac.get("byteOffset",0)
    data=bytearray(original)
    for i in IDS:
        x,y,z=struct.unpack_from("<3f",data,offset+i*12)
        assert abs(y-6.678520679473877)<2e-5
        struct.pack_into("<f",data,offset+i*12+4,y-.225)
    candidate=bytes(data)
    assert sha(candidate)==DST and len(candidate)==len(original)
    new.write_bytes(candidate)
    print("PASS",str(new),sha(candidate))
if __name__=="__main__":
    if len(sys.argv)!=3: raise SystemExit(__doc__)
    patch(sys.argv[1],sys.argv[2])
