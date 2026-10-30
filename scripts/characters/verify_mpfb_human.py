"""Strict, independent structural acceptance of actual MPFB 3D export."""
import json
import struct
import sys
from pathlib import Path

folder = Path(sys.argv[1] if len(sys.argv)>1 else "outputs/human_mpfb")
manifest=json.loads((folder/"asset_manifest.json").read_text())
report=json.loads((folder/"report.json").read_text())
p=folder/manifest["model_file"]
assert p.stat().st_size>10000
with p.open("rb") as handle:
    head=handle.read(12)
    magic,version,byte_length=struct.unpack("<4sII",head)
    assert magic==b"glTF" and version==2
    assert byte_length==p.stat().st_size
    chunk_size,chunk_type=struct.unpack("<I4s",handle.read(8))
    assert chunk_type==b"JSON"
    doc=json.loads(handle.read(chunk_size))
meshes=doc.get("meshes",[])
skins=doc.get("skins",[])
names=[x.get("name","") for x in doc.get("nodes",[])]
assert meshes and skins, "Expected rigged human, not geometry-only mannequin"
assert any("Human" in n for n in names)
assert report["rig_bones"]>=30
assert report["body_vertices"]>8000, "Expect real MPFB human topology, not simple blocks"
assert report["height_m"]>1 and report["height_m"]<2.4
assert doc.get("materials"), "Expected PBR material"
prim=[p for m in meshes for p in m.get("primitives",[])]
assert any("JOINTS_0" in p.get("attributes",{}) and "WEIGHTS_0" in p.get("attributes",{}) for p in prim), "No vertex skin weights"
assert manifest["quality_status"] in ("BASEMESH_AND_RIG_TEST_NOT_PHOTOREAL_READY", "LICENSED_ASSET_CHARACTER_NEEDS_VISUAL_REVIEW")
if report.get("asset_count", 0):
    assert report["asset_count"]>=7, "Expected full eyes/hair/outfit, not partial asset application"
    assert len(meshes)>=5, "Expected multiple distinct meshes for eyes, hair and garments"
    assert len(doc.get("images", []))>=1, "Expected at least one texture image in dressed GLB"
    assert len(doc.get("materials", []))>=3, "Expected skin/clothing/hair materials"
result={"verdict":"STRUCTURE_PASS_not_artistic_approval",
        "body_vertices":report["body_vertices"],"bone_count":report["rig_bones"],
        "height_m":report["height_m"],"glb_bytes":p.stat().st_size,
        "skin_count":len(skins),"mesh_count":len(meshes),
        "pbr_materials":len(doc["materials"]),"preview_status":"next_step"}
(folder/"validation.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps(result,indent=2))
