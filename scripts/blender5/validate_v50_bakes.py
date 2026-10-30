#!/usr/bin/env python3
"""Independent v4.9 geometry/UV/normal-texture GLB gate (stdlib)."""
import json,struct,sys
from pathlib import Path

folder=Path(sys.argv[1] if len(sys.argv)>1 else "outputs")
manifest=json.loads((folder/"asset_manifest.json").read_text())
qa=json.loads((folder/"bake_qa.json").read_text())
glb=folder/manifest["model_file"]
with glb.open("rb") as f:
    magic,version,total=struct.unpack("<4sII",f.read(12))
    assert magic==b"glTF" and version==2 and total==glb.stat().st_size
    size,kind=struct.unpack("<I4s",f.read(8))
    assert kind==b"JSON"
    doc=json.loads(f.read(size))
assert qa["meshes_required"]>=8 and len(qa["targets"])>=4,qa
normal_mats=[m for m in doc.get("materials",[]) if "normalTexture" in m]
assert len(normal_mats)>=8, f"Expected >=8 baked normal-map materials, found {len(normal_mats)}"
assert len(doc.get("images",[]))>=24,"Expected eight normal, eight color and eight roughness images"
assert doc.get("skins") and len(doc.get("animations",[]))>=6,"Lost skin or six actions"
assert all(x.get("name")!="BAKE_ONLY_HIGH_"+t["mesh"] for x in doc.get("nodes",[]) for t in qa["targets"])
for b in qa["targets"]:
    for key in ("basecolor_png","roughness_png"):
        tex=folder/b[key]
        assert tex.is_file() and tex.stat().st_size>1024,f"Missing UV authored surface texture {tex}"
        assert tex.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    p=folder/b["png"]
    assert p.exists() and p.stat().st_size>1024,f"Missing baked texture: {p}"
    assert p.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"),"Not PNG"
    assert b["high_faces"]>b["low_faces"],"No actual high-detail source"
    assert b["pixels"]==[512,512] and len(b["sha256"])==64
print(json.dumps({"verdict":"V50_BAKE_STRUCTURE_PASS","baked_maps":len(qa["targets"]),"normal_materials":len(normal_mats),"embedded_images":len(doc["images"]),"animations":len(doc.get("animations",[]))},ensure_ascii=False))
