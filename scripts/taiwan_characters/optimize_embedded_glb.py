"""Re-encode images already embedded in a GLB, leaving mesh/rig/animations bytes untouched.
Usage: python3 optimize_embedded_glb.py input.glb output.glb [max_dimension]
Requirements: Pillow. Will reject any export without skeletons or with no images.
"""
from pathlib import Path
from io import BytesIO
from PIL import Image
import json,struct,sys

def optimize(inp,out,max_dim=512):
    old=Path(inp).read_bytes()
    magic,ver,total=struct.unpack_from("<4sII",old,0)
    assert magic==b"glTF" and ver==2 and total==len(old)
    jlen,jtype=struct.unpack_from("<I4s",old,12)
    assert jtype==b"JSON"
    doc=json.loads(old[20:20+jlen])
    bin_header=20+jlen
    blen,btype=struct.unpack_from("<I4s",old,bin_header)
    assert btype==b"BIN\0"
    binary=old[bin_header+8:bin_header+8+blen]
    assert len(doc["buffers"])==1 and len(binary)==blen
    views=doc["bufferViews"]
    images={img["bufferView"]:img for img in doc.get("images",[]) if "bufferView" in img}
    outbin=bytearray()
    log=[]
    for idx,view in sorted(enumerate(views),key=lambda e:e[1].get("byteOffset",0)):
        assert view.get("buffer",0)==0
        st=view.get("byteOffset",0)
        blob=binary[st:st+view["byteLength"]]
        assert len(blob)==view["byteLength"]
        if idx in images:
            initial=len(blob)
            with Image.open(BytesIO(blob)) as pic:
                original=pic.size
                pic.load()
                if max(pic.size)>max_dim:
                    pic.thumbnail((max_dim,max_dim),Image.Resampling.LANCZOS)
                if pic.mode not in ("RGB","RGBA"):
                    pic=pic.convert("RGBA" if "A" in pic.getbands() else "RGB")
                imagebuf=BytesIO()
                pic.save(imagebuf,format="PNG",optimize=True,compress_level=9)
                blob=imagebuf.getvalue()
                final=pic.size
            for im in doc["images"]:
                if im.get("bufferView")==idx:im["mimeType"]="image/png"
            log.append(dict(name=images[idx].get("name",str(idx)),before=initial,
                            after=len(blob),old_size=original,new_size=final))
        while len(outbin)%4:outbin.append(0)
        view["byteOffset"]=len(outbin)
        view["byteLength"]=len(blob)
        outbin.extend(blob)
    while len(outbin)%4:outbin.append(0)
    doc["buffers"][0]["byteLength"]=len(outbin)
    encoded=json.dumps(doc,ensure_ascii=False,separators=(",",":")).encode("utf-8")
    encoded+=b" "*((-len(encoded))%4)
    b=bytes(outbin)
    new=struct.pack("<4sII",b"glTF",2,12+8+len(encoded)+8+len(b))
    new+=struct.pack("<I4s",len(encoded),b"JSON")+encoded
    new+=struct.pack("<I4s",len(b),b"BIN\0")+b
    assert len(log)>=7 and len(doc.get("skins",[]))>=1
    assert all(max(x["new_size"])<=max_dim for x in log)
    assert len(new)<=6000000,("Not small enough",len(new))
    Path(out).write_bytes(new)
    print("VERIFIED_EMBEDDED_IMAGE_REWRITE",inp,out,"before",len(old),"after",len(new))
    print(json.dumps(log,ensure_ascii=False))

if __name__=="__main__":
    if len(sys.argv)<3:raise SystemExit("usage: input.glb output.glb [max_px]")
    optimize(sys.argv[1],sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 512)
