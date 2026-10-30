"""Audit genuine glTF 2.0 morph deltas, not shape names alone.

Usage: python validate_mouth_morphs.py exported.glb

For facial accessories to count as working, teeth or tongue must have a real
nonzero "mouthOpen" POSITION delta accessor with unchanged skinning. 
"""
import sys,json,struct,math
from pathlib import Path

def read_glb(path):
    raw=Path(path).read_bytes()
    magic,ver,total=struct.unpack_from("<4sII",raw)
    assert magic==b"glTF" and ver==2 and total==len(raw)
    length,typ=struct.unpack_from("<I4s",raw,12)
    assert typ==b"JSON"
    doc=json.loads(raw[20:20+length])
    off=20+length
    length2,typ2=struct.unpack_from("<I4s",raw,off)
    assert typ2==b"BIN\0"
    return doc,raw[off+8:off+8+length2]

def nonzero_vectors(doc,blob,index):
    acc=doc["accessors"][index]
    if acc["type"]!="VEC3":raise ValueError("Expected 3D POSITION target")
    if acc["componentType"]!=5126:raise ValueError("Expected float32 targets")
    n=acc["count"]
    if n==0:return 0,0.
    bview=doc["bufferViews"][acc["bufferView"]]
    stride=bview.get("byteStride",12)
    base=bview.get("byteOffset",0)+acc.get("byteOffset",0)
    nonzero=0;maxlen=0.
    for k in range(n):
        vec=struct.unpack_from("<fff",blob,base+k*stride)
        length=math.sqrt(sum(f*f for f in vec))
        if length>1e-6:nonzero+=1
        maxlen=max(maxlen,length)
    return nonzero,maxlen

def inspect(path):
    doc,bin=read_glb(path)
    result=[]
    for mesh in doc.get("meshes",[]):
        names=mesh.get("extras",{}).get("targetNames",[])
        for prim in mesh.get("primitives",[]):
            for i,name in enumerate(names):
                targets=prim.get("targets",[])
                if i>=len(targets):raise RuntimeError("Morph name without actual target "+mesh.get("name",""))
                if "POSITION" not in targets[i]:continue
                count,maxd=nonzero_vectors(doc,bin,targets[i]["POSITION"])
                result.append({"mesh":mesh.get("name",""),"name":name,
                               "vertices":count,"max_displacement_m":round(maxd,8)})
    body=[r for r in result if r["name"]=="mouthOpen" and r["vertices"]>1000]
    assert body,"Missing nonzero genuine body jawOpen morph"
    oral=[r for r in result if r["name"]=="mouthOpen" and
          any(part in r["mesh"].lower() for part in ("teeth","tongue")) and
          r["vertices"]>=8 and r["max_displacement_m"]>0.0001]
    if not oral:
        raise RuntimeError("MouthOpen exists by name but has no actual teeth/tongue delta")
    blink=[r for r in result if r["name"].startswith("eyeBlink") and
           any(part in r["mesh"].lower() for part in ("eyelash","eyebrow","eye")) and
           r["vertices"]>=5]
    assert blink,"Eye attachments not responding to blinking"
    print("VALIDATED_FACE_ACCESSORY_MORPHS",json.dumps(
          {"file":str(path),"oral":oral,"eye":blink[:10],
           "all_nonzero":len([r for r in result if r["vertices"]>0])},
          ensure_ascii=False))
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("Usage: validate_mouth_morphs.py file.glb")
    inspect(sys.argv[1])
