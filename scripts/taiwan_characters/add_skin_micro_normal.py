"""Add a subtle, original CC0-friendly tangent-space skin normal map to a
genuine existing MakeHuman GLB without changing geometry, skeleton or clothes.

Example:
  python add_skin_micro_normal.py source.glb output.glb mature

The output is a material-only visual candidate. Do not claim it is art-approved
until the GLB has been re-rendered in the target 3D engine.
Dependency: Pillow (pip install Pillow)
"""
from pathlib import Path
from PIL import Image, ImageFilter
from io import BytesIO
import json, struct, random, sys, hashlib

def micro_normal(mature):
    rng=random.Random(20261030 + int(mature))
    size=512
    pixels=bytes(rng.randrange(0,256) for _ in range(64*64))
    gray=Image.frombytes("L",(64,64),pixels).resize((size,size),Image.Resampling.BICUBIC)
    blurred=gray.filter(ImageFilter.GaussianBlur(.8))
    src=blurred.load()
    strength=.23 if mature else .14
    dst=bytearray(size*size*3)
    for y in range(size):
        for x in range(size):
            dx=(src[(x+1)%size,y]-src[(x-1)%size,y])/255
            dy=(src[x,(y+1)%size]-src[x,(y-1)%size])/255
            vx=-dx*strength; vy=-dy*strength
            norm=(1+vx*vx+vy*vy)**.5
            pos=(y*size+x)*3
            dst[pos]=int((vx/norm*.5+.5)*255)
            dst[pos+1]=int((vy/norm*.5+.5)*255)
            dst[pos+2]=int((1/norm*.5+.5)*255)
    image=Image.frombytes("RGB",(size,size),bytes(dst))
    memory=BytesIO()
    image.save(memory,format="PNG",optimize=True)
    return memory.getvalue()

def process(src,dst,age):
    mature=age=="mature"
    b=Path(src).read_bytes()
    magic,ver,total=struct.unpack_from("<4sII",b,0)
    assert magic==b"glTF" and ver==2 and total==len(b)
    n,typ=struct.unpack_from("<I4s",b,12)
    assert typ==b"JSON"
    doc=json.loads(b[20:20+n])
    start=20+n
    blen,btype=struct.unpack_from("<I4s",b,start)
    assert btype==b"BIN\0"
    oldbin=b[start+8:start+8+blen]
    old_accessors=doc["accessors"].copy()
    old_skins=doc["skins"].copy()
    old_nodes=doc["nodes"].copy()
    old_meshes=doc["meshes"].copy()
    sk=next(x for x in doc["materials"] if x.get("name","").endswith(".body"))
    assert "normalTexture" not in sk, "Already contains normal texture"
    normal=micro_normal(mature)
    binary=bytearray(oldbin)
    while len(binary)%4:binary.append(0)
    off=len(binary);binary.extend(normal)
    while len(binary)%4:binary.append(0)
    idx=len(doc["bufferViews"])
    doc["bufferViews"].append({"buffer":0,"byteOffset":off,"byteLength":len(normal)})
    imidx=len(doc["images"])
    doc["images"].append({"name":"TaiwanSubtleSkinNormals","bufferView":idx,"mimeType":"image/png"})
    texidx=len(doc["textures"])
    doc["textures"].append({"source":imidx})
    sk["normalTexture"]={"index":texidx,"texCoord":0,"scale":.23 if mature else .14}
    sk["pbrMetallicRoughness"]["roughnessFactor"]=.78 if mature else .65
    doc["buffers"][0]["byteLength"]=len(binary)
    txt=json.dumps(doc,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    txt+=b" "*((-len(txt))%4)
    final=(struct.pack("<4sII",b"glTF",2,12+8+len(txt)+8+len(binary))+
          struct.pack("<I4s",len(txt),b"JSON")+txt+
          struct.pack("<I4s",len(binary),b"BIN\0")+bytes(binary))
    assert len(final)<=6000000, "6MB pilot budget exceeded"
    assert doc["accessors"]==old_accessors and doc["skins"]==old_skins
    assert doc["nodes"]==old_nodes and doc["meshes"]==old_meshes
    assert bytes(binary[:len(oldbin)])==oldbin
    Path(dst).write_bytes(final)
    print(json.dumps({"src":src,"dst":dst,"size":len(final),
                      "sha256":hashlib.sha256(final).hexdigest(),
                      "morph_target_count":sum(len(p.get("targets",[]))
                        for m in doc["meshes"] for p in m.get("primitives",[])),
                      "art_approved":False},ensure_ascii=False))

if __name__=="__main__":
    if len(sys.argv)!=4 or sys.argv[3] not in ("young","mature"):
        raise SystemExit("usage: src.glb dst.glb young|mature")
    process(sys.argv[1],sys.argv[2],sys.argv[3])
